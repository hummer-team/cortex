import chromadb
from chromadb.types import Collection
from chromadb.utils import embedding_functions
from cortex.core.config import DB_PATH, COLLECTION_NAME, EMBEDDING_MODEL
from typing import List, Dict, Any
from cortex.logger.logger import get_logger

log = get_logger(__name__)


class StorageService:
    """
    封装对本地向量数据库的所有操作。
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(StorageService, cls).__new__(
                cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        # 使用单例模式确保只有一个客户端实例
        if not hasattr(self, 'client'):
            log.info("Initializing ChromaDB client...")
            self.client = chromadb.PersistentClient(path=str(DB_PATH))

            # 明确指定嵌入函数，让ChromaDB负责嵌入
            # 这将使用 sentence-transformers，与我们之前的查询逻辑保持一致
            embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=EMBEDDING_MODEL
            )

            self.collection = self.client.get_or_create_collection(
                name=COLLECTION_NAME,
                embedding_function=embedding_function
            )
            log.info(
                f"ChromaDB collection '{COLLECTION_NAME}' loaded/created with SentenceTransformerEmbeddingFunction.")

    def add_memory_chunks(self, chunks: List[str], metadatas: List[Dict[str, Any]], ids: List[str]):
        """
        向数据库中批量添加记忆片段。
        ChromaDB将使用在集合上配置的嵌入函数自动处理文档的向量化。
        """
        if not chunks:
            return
        self.collection.add(
            documents=chunks,
            metadatas=metadatas,
            ids=ids
        )
        log.info(f"Added {len(chunks)} memory chunks to the database.")

    def query_memories(self, query_text: str, top_k: int) -> List[Dict[str, Any]]:
        """
        根据查询文本，检索最相关的记忆片段。
        ChromaDB将使用在集合上配置的嵌入函数自动处理查询的向量化。
        """
        results = self.collection.query(
            # <--- 注意：这里从 query_embeddings 改为 query_texts
            query_texts=[query_text],
            n_results=top_k
        )

        # 将结果格式化为更易用的结构
        retrieved = []
        if results and results['documents']:
            for i, doc in enumerate(results['documents'][0]):
                retrieved.append({
                    "text": doc,
                    "metadata": results['metadatas'][0][i],
                    "distance": results['distances'][0][i]
                })
        return retrieved


# 创建一个全局实例，方便其他服务调用
storage_service = StorageService()
