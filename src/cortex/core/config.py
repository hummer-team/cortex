from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent

# 记忆存储配置
DB_PATH = BASE_DIR / "data"
COLLECTION_NAME = "personal_memory"

# AI 模型配置
# 本地嵌入模型，all-MiniLM-L6-v2 是一个轻量级且性能优秀的选择
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
# 本地摘要生成模型
SYNTHESIS_MODEL = "llama3:8b"

# 检索配置
RETRIEVAL_TOP_K = 5  # 每次检索最相关的5个记忆片段
