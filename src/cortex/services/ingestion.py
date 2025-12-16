from cortex.core.chunk import chunk
from cortex.core.model_chat import generate_chat_completion
from cortex.core.prompt import get_formatted_prompt
from cortex.logger.logger import get_logger
import uuid
import hashlib
import time
import json
from typing import Optional, Dict, Any

log = get_logger(__name__)


class IngestionService:
    """
    负责将外部知识源摄入并存储到记忆库中。
    """

    def __init__(self, storage_service):
        """
        通过依赖注入接收一个存储服务实例。
        """
        self.storage_service = storage_service

    def _calculate_hash(self, content: str) -> str:
        """计算给定字符串内容的SHA-256哈希值。"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def _extract_metadata_with_llm(self, filename: str, description: Optional[str]) -> Dict[str, Any]:
        if not description:
            description = "No description provided."
        try:
            prompt = get_formatted_prompt(
                template_name="cortex_sys_metadata_v1.md",
                substitutions={"filename": filename,
                               "description": description}
            )
            log.info(f"Extracting metadata for '{filename}' with LLM...")
            response_str = generate_chat_completion(prompt)
            start_tag = "[JSON_START]"
            end_tag = "[JSON_END]"
            start_index = response_str.find(start_tag)
            end_index = response_str.find(end_tag)
            if start_index != -1 and end_index != -1:
                json_str = response_str[start_index +
                                        len(start_tag):end_index].strip()
                return json.loads(json_str)
            else:
                log.warning(
                    "JSON delimiters not found, attempting direct parse.")
                return json.loads(response_str)
        except Exception as e:
            log.error(
                f"Failed to extract metadata with LLM: {e}. Falling back to basic metadata.")
            source = filename.split('_')[0].lower()
            return {"source": source, "source_type": "document", "tags": []}

    def process(self, content: str, source_filename: str, description: Optional[str] = None):
        log.info(f"Starting ingestion process for source: {source_filename}")
        file_hash = self._calculate_hash(content)

        # 现在通过注入的实例调用
        if self.storage_service.check_if_hash_exists(file_hash):
            log.info(
                f"Content from source '{source_filename}' already exists. Skipping.")
            return

        extracted_metadata = self._extract_metadata_with_llm(
            source_filename, description)
        chunks = chunk.chunk_text(content)
        if not chunks:
            log.warning(
                f"No chunks generated for {source_filename}. Skipping.")
            return

        current_timestamp = int(time.time())
        final_metadatas = []
        for i, _ in enumerate(chunks):
            tags_list = extracted_metadata.get("tags", [])
            tags_str = ",".join(tags_list) if isinstance(
                tags_list, list) else ""
            meta = {
                "source": extracted_metadata.get("source", source_filename),
                "source_type": extracted_metadata.get("source_type", "document"),
                "tags": tags_str,
                "creation_ts": current_timestamp,
                "file_hash": file_hash,
                "chunk_index": i,
                "original_filename": source_filename
            }
            final_metadatas.append(meta)

        ids = [str(uuid.uuid4()) for _ in chunks]

        # 现在通过注入的实例调用
        self.storage_service.add_memory_chunks(
            chunks=chunks,
            metadatas=final_metadatas,
            ids=ids
        )
        log.info(
            f"Successfully ingested {len(chunks)} chunks from {source_filename}")
