from pathlib import Path
from cortex.logger.logger import get_logger

log = get_logger(__name__)
# root dir
BASE_DIR = Path(__file__).resolve().parent.parent

log.info(f"cortex base dir is {BASE_DIR}")

# 记忆存储配置
DB_PATH = BASE_DIR / "data"
COLLECTION_NAME = "personal_memory"

# AI 模型配置
# 本地嵌入模型，all-MiniLM-L6-v2 是一个轻量级且性能优秀的选择，体积小、速度快，适合边缘 / 低资源场景
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
# 本地摘要生成模型
SYNTHESIS_MODEL = "qwen3:8b"

# 检索配置
RETRIEVAL_TOP_K = 5  # 每次检索最相关的5个记忆片段
