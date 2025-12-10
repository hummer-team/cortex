import re
import uuid
from sentence_transformers import SentenceTransformer
from core.config import EMBEDDING_MODEL
from services.storage import storage_service
import time


class IngestionService:
    """
    负责记忆的完整摄入流程：清洗 -> 分块 -> 向量化 -> 存储。
    """

    def __init__(self):
        print("Loading embedding model...")
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        print("Embedding model loaded.")

    def clean_text(self, text: str) -> str:
        """
        执行基础的文本清洗。
        - 移除多余的空白字符
        - 可以在这里扩展更复杂的清洗逻辑，如去除HTML标签等
        """
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def chunk_text(self, text: str, chunk_size: int = 512, chunk_overlap: int = 50) -> list[str]:
        """
        一个简单的递归字符文本分块器。
        """
        if len(text) <= chunk_size:
            return [text]

        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunks.append(text[start:end])
            start += chunk_size - chunk_overlap
        return chunks

    def process(self, content: str, source: str):
        """
        处理一份完整的原始文本，并将其存入记忆库。
        """
        print(f"Starting ingestion for source: {source}")

        # 1. 清洗
        cleaned_content = self.clean_text(content)

        # 2. 分块
        chunks = self.chunk_text(cleaned_content)
        if not chunks:
            print("No chunks generated after cleaning and chunking.")
            return

        print(f"Generated {len(chunks)} chunks.")

        # 3. 向量化
        embeddings = self.embedding_model.encode(
            chunks, show_progress_bar=True)

        # 4. 准备存储
        metadatas = [{"source": source, "ingested_at": int(
            time.time())} for _ in chunks]
        ids = [str(uuid.uuid4()) for _ in chunks]

        # 5. 存储
        storage_service.add_memory_chunks(
            chunks=chunks,
            metadatas=metadatas,
            ids=ids
        )
        print(f"Ingestion completed for source: {source}")
