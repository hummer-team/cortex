from pathlib import Path
import os
from cortex.logger.logger import get_logger

log = get_logger(__name__)

# --- 路径配置 ---
# 项目根目录
CORTEX_HOME = Path(__file__).resolve().parent.parent.parent.parent
# 'src/cortex' 目录
BASE_DIR = Path(__file__).resolve().parent.parent
# 'prompt' 模板目录
PROMPT_DIR = CORTEX_HOME / "prompt"

log.info(f"Cortex home directory: {CORTEX_HOME}")
log.info(f"Cortex base directory: {BASE_DIR}")
log.info(f"Prompt directory: {PROMPT_DIR}")


# --- 记忆存储配置 ---
DB_PATH = BASE_DIR / "data"
COLLECTION_NAME = "personal_memory"

# 1. 嵌入模型 (Embedding Model)
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# 2. 上下文合成模型 (Synthesis Model)
SYNTHESIS_MODEL_PROVIDER = os.getenv("SYNTHESIS_MODEL_PROVIDER", "local")
SYNTHESIS_MODEL = os.getenv("SYNTHESIS_MODEL", "SYNTHESIS_MODEL")

# 远程API的配置
MODEL_API_KEY = os.getenv("MODEL_API_KEY", "")
MODEL_API_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"

# 3. Prompt模板配置
# 从环境变量读取模板文件名，默认为 'qwen3_v1.md'
PROMPT_TEMPLATE_NAME = os.getenv("PROMPT_TEMPLATE_NAME", "qwen3_v1.md")


# --- 检索配置 ---
RETRIEVAL_TOP_K = int(os.getenv("RETRIEVAL_TOP_K", 5))
CORTEX_SYS_PROMPT_TEMPLATE = os.getenv("CORTEX_SYS_PROMPT_TEMPLATE", "")
