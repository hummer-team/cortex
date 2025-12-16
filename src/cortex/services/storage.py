import chromadb
from chromadb.utils import embedding_functions
from cortex.core.config import DB_PATH, COLLECTION_NAME, EMBEDDING_MODEL
from typing import List, Dict, Any, Optional
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
        if not hasattr(self, 'client'):
            log.info("Initializing ChromaDB client...")
            self.client = chromadb.PersistentClient(path=str(DB_PATH))
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
        """向数据库中批量添加记忆片段。"""
        if not chunks:
            return
        self.collection.add(
            documents=chunks,
            metadatas=metadatas,
            ids=ids
        )
        log.info(f"Added {len(chunks)} memory chunks to the database.")

    def check_if_hash_exists(self, file_hash: str) -> bool:
        """高效地检查具有特定文件哈希的文档是否已存在。"""
        results = self.collection.get(
            where={"file_hash": file_hash},
            limit=1
        )
        return bool(results['ids'])

    def query_memories(self, query_text: str, top_k: int, where_filter: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """根据查询文本和可选的元数据过滤器，检索最相关的记忆片段。"""
        results = self.collection.query(
            query_texts=[query_text],
            n_results=top_k,
            where=where_filter  # 应用元数据过滤器
        )

        retrieved = []
        if results and results['documents']:
            for i, doc in enumerate(results['documents'][0]):
                retrieved.append({
                    "text": doc,
                    "metadata": results['metadatas'][0][i],
                    "distance": results['distances'][0][i]
                })
        return retrieved


storage_service = StorageService()
