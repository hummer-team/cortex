from cortex.core.config import RETRIEVAL_TOP_K
from cortex.core.models import ContextResponse
from cortex.core.prompt import get_synthesis_prompt, get_formatted_prompt
from cortex.core.model_chat import generate_chat_completion
from cortex.logger.logger import get_logger
from typing import Optional, Tuple, List, Dict, Any
import json
import time

log = get_logger(__name__)


class RetrievalService:
    """
    负责记忆的检索与合成流程。
    """

    def __init__(self, storage_service):
        """通过依赖注入接收存储服务实例。"""
        self.storage_service = storage_service

    def _understand_query_with_llm(self, query: str) -> Dict[str, Any]:
        try:
            prompt = get_formatted_prompt(
                template_name="cortex_sys_v1.md",
                substitutions={"user_query": query,
                               "current_timestamp": int(time.time())}
            )
            log.info("Decomposing user query with LLM...")
            response_str = generate_chat_completion(prompt)
            if response_str.startswith("```json"):
                response_str = response_str[7:-4].strip()
            structured_query = json.loads(response_str)
            log.info(f"Decomposed query: {structured_query}")
            return structured_query
        except Exception as e:
            log.error(
                f"Failed to understand query with LLM: {e}. Falling back to simple semantic search.")
            return {"core_query": query, "filters": []}

    def retrieve_and_prepare_context(self, query: str) -> Optional[Tuple[str, List[str]]]:
        structured_query = self._understand_query_with_llm(query)
        core_query = structured_query.get("core_query", query)
        where_clause = {}
        if "filters" in structured_query and structured_query["filters"]:
            filters_list = []
            for f in structured_query["filters"]:
                field, op, value = f['field'], f['operator'], f['value']
                if op == 'eq':
                    filters_list.append({field: value})
                else:
                    filters_list.append({field: {f"${op}": value}})
            if filters_list:
                where_clause["$and"] = filters_list
        log.info(
            f"Executing hybrid search with core_query='{core_query}' and where_clause={where_clause}")

        # 通过注入的实例调用
        retrieved_memories = self.storage_service.query_memories(
            query_text=core_query,
            top_k=RETRIEVAL_TOP_K,
            where_filter=where_clause if where_clause else None
        )
        if not retrieved_memories:
            log.info("No relevant memories found after hybrid search.")
            return None
        log.info(f"Retrieved {len(retrieved_memories)} memory chunks.")
        context_for_synthesis = "相关历史记忆片段:\n\n"
        sources = set()
        for i, memory in enumerate(retrieved_memories):
            source_name = memory['metadata'].get('source', '未知来源')
            context_for_synthesis += f"--- 记忆片段 {i+1} (来源: {source_name}) ---\n"
            context_for_synthesis += memory['text'] + "\n\n"
            sources.add(source_name)
        return context_for_synthesis, list(sources)

    def synthesize_context(self, context: str) -> str:
        log.info("Step 2: Synthesizing context with configured LLM...")
        meta_prompt = get_synthesis_prompt(context)
        synthesized_context = generate_chat_completion(meta_prompt)
        log.info("Synthesis complete.")
        return synthesized_context

    def query_and_synthesize(self, query: str) -> ContextResponse:
        retrieval_result = self.retrieve_and_prepare_context(query)
        if not retrieval_result:
            return ContextResponse(context="未找到与您查询相关的记忆。", retrieved_sources=[])
        context_for_synthesis, sources = retrieval_result
        synthesized_context = self.synthesize_context(context_for_synthesis)
        return ContextResponse(context=synthesized_context, retrieved_sources=sources)
