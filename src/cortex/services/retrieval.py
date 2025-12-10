import ollama
from sentence_transformers import SentenceTransformer
from cortex.core.config import EMBEDDING_MODEL, SYNTHESIS_MODEL, RETRIEVAL_TOP_K
from cortex.services.storage import storage_service
from cortex.core.models import ContextResponse  # 确认导入了我们定义的模型


class RetrievalService:
    """
    负责记忆的检索与合成流程。
    """

    def __init__(self):
        print("Loading embedding model for retrieval...")
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        print("Embedding model loaded.")

    def query_and_synthesize(self, query: str) -> ContextResponse:  # 返回类型现在是明确的
        """
        根据用户查询，检索相关记忆并生成上下文摘要。
        """
        # ... (内部逻辑保持不变) ...

        print(f"Received query: '{query}'")

        # 1. 向量化查询
        query_embedding = self.embedding_model.encode(query).tolist()

        # 2. 检索相关记忆
        retrieved_memories = storage_service.query_memories(
            query_embedding=query_embedding,
            top_k=RETRIEVAL_TOP_K
        )

        if not retrieved_memories:
            return ContextResponse(context="未找到相关记忆。", retrieved_sources=[])

        print(f"Retrieved {len(retrieved_memories)} memory chunks.")

        # 3. 构建用于合成的上下文
        context_for_synthesis = "相关历史记忆片段:\n\n"
        sources = set()
        for i, memory in enumerate(retrieved_memories):
            context_for_synthesis += f"--- 记忆片段 {i+1} (来源: {memory['metadata']['source']}) ---\n"
            context_for_synthesis += memory['text'] + "\n\n"
            sources.add(memory['metadata']['source'])

        # 4. 构建元指令 (Meta-Prompt)
        meta_prompt = f"""
        你是一个信息整理专家。你的任务是阅读以下多个可能重复或零散的“历史记忆片段”，然后将它们提炼和总结成一段通顺、连贯、高度浓缩的“背景上下文摘要”。
        这份摘要将用于帮助用户与另一个AI进行对话。
        请确保摘要内容忠于原文，但要去除冗余，并将相关的点组织在一起。
        请直接输出摘要内容，不要添加任何额外的解释或开场白。

        {context_for_synthesis}
        """

        # 5. 调用本地LLM进行合成
        print("Synthesizing context with local LLM...")
        try:
            response = ollama.chat(
                model=SYNTHESIS_MODEL,
                messages=[{'role': 'user', 'content': meta_prompt}]
            )
            synthesized_context = response['message']['content']
            print("Synthesis complete.")
        except Exception as e:
            print(f"Error calling local LLM: {e}")
            synthesized_context = "无法连接到本地LLM进行摘要合成。以下是原始记忆片段：\n\n" + context_for_synthesis

        return ContextResponse(
            context=synthesized_context,
            retrieved_sources=list(sources)
        )
