import ollama
from cortex.core.config import SYNTHESIS_MODEL, RETRIEVAL_TOP_K
from cortex.services.storage import storage_service
from cortex.core.models import ContextResponse
from cortex.logger.logger import get_logger

log = get_logger(__name__)


class RetrievalService:
    """
    负责记忆的检索与合成流程。
    """

    def __init__(self):
        # 不再需要自己加载嵌入模型
        pass

    def query_and_synthesize(self, query: str) -> ContextResponse:
        """
        根据用户查询，检索相关记忆并生成上下文摘要。
        """
        log.info(f"Received query: '{query}'")

        # 1. 检索相关记忆 (不再需要手动编码)
        # 直接将查询文本传递给 storage_service
        retrieved_memories = storage_service.query_memories(
            query_text=query,
            top_k=RETRIEVAL_TOP_K
        )

        if not retrieved_memories:
            return ContextResponse(context="未找到相关记忆。", retrieved_sources=[])

        log.info(f"Retrieved {len(retrieved_memories)} memory chunks.")

        # 2. 构建用于合成的上下文
        context_for_synthesis = "相关历史记忆片段:\n\n"
        sources = set()
        for i, memory in enumerate(retrieved_memories):
            context_for_synthesis += f"--- 记忆片段 {i+1} (来源: {memory['metadata']['source']}) ---\n"
            context_for_synthesis += memory['text'] + "\n\n"
            sources.add(memory['metadata']['source'])

        # 3. 构建元指令 (Meta-Prompt)
        meta_prompt = f"""
        你是一个信息整理专家。你的任务是阅读以下多个可能重复或零散的“历史记忆片段”，然后将它们提炼和总结成一段通顺、连贯、高度浓缩的“背景上下文摘要”。
        这份摘要将用于帮助用户与另一个AI进行对话。
        请确保摘要内容忠于原文，但要去除冗余，并将相关的点组织在一起。
        请直接输出摘要内容，不要添加任何额外的解释或开场白。

        {context_for_synthesis}
        """

        # 4. 调用本地LLM进行合成
        log.info("Synthesizing context with local LLM...")
        try:
            response = ollama.chat(
                model=SYNTHESIS_MODEL,
                messages=[{'role': 'user', 'content': meta_prompt}]
            )
            synthesized_context = response['message']['content']
            log.info("Synthesis complete.")
        except Exception as e:
            log.error(f"Error calling local LLM: {e}")
            synthesized_context = "无法连接到本地LLM进行摘要合成。以下是原始记忆片段：\n\n" + context_for_synthesis

        return ContextResponse(
            context=synthesized_context,
            retrieved_sources=list(sources)
        )
