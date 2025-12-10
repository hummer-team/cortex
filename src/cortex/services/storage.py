import chromadb
from chromadb.types import Collection
from cortex.core.config import DB_PATH, COLLECTION_NAME
from typing import List, Dict, Any


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
            print("Initializing ChromaDB client...")
            self.client = chromadb.PersistentClient(path=str(DB_PATH))
            self.collection = self.client.get_or_create_collection(
                name=COLLECTION_NAME)
            print(f"ChromaDB collection '{COLLECTION_NAME}' loaded/created.")

    def add_memory_chunks(self, chunks: List[str], metadatas: List[Dict[str, Any]], ids: List[str]):
        """
        向数据库中批量添加记忆片段。
        """
        if not chunks:
            return
        self.collection.add(
            documents=chunks,
            metadatas=metadatas,
            ids=ids
        )
        print(f"Added {len(chunks)} memory chunks to the database.")

    def query_memories(self, query_embedding: List[float], top_k: int) -> List[Dict[str, Any]]:
        """
        根据查询向量，检索最相关的记忆片段。
        """
        results = self.collection.query(
            query_embeddings=[query_embedding],
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
