from cortex.services.storage import storage_service
from cortex.core.chunk import chunk_text
from cortex.logger.logger import get_logger
import uuid

log = get_logger(__name__)


class IngestionService:
    """
    负责将外部知识源摄入并存储到记忆库中。
    """

    def __init__(self):
        # 在新的架构下，IngestionService不再需要直接处理嵌入模型。
        # 它的职责是分块并将文本块传递给StorageService。
        pass

    def process(self, content: str, source: str):
        """
        处理一段文本内容，将其分块并存入数据库。
        """
        log.info(f"Starting ingestion process for source: {source}")

        # 1. 将文本分块
        chunks = chunk_text(content)
        log.info(f"Content chunked into {len(chunks)} pieces.")

        if not chunks:
            log.warning(f"No chunks were generated for source: {source}. Skipping.")
            return

        # 2. 准备元数据和ID
        metadatas = [{"source": source} for _ in chunks]
        ids = [str(uuid.uuid4()) for _ in chunks]

        # 3. 将文本块添加到存储
        # 注意：我们传递的是原始文本块(chunks)，而不是嵌入向量。
        # ChromaDB会使用在集合上配置的嵌入函数自动处理向量化。
        storage_service.add_memory_chunks(
            chunks=chunks,
            metadatas=metadatas,
            ids=ids
        )

        log.info(
            f"Successfully ingested {len(chunks)} chunks from source: {source}")
