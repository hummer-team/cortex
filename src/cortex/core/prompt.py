# /src/cortex/core/prompt.py
from cortex.core.config import PROMPT_DIR, PROMPT_TEMPLATE_NAME
from cortex.logger.logger import get_logger
from typing import Dict, Any

log = get_logger(__name__)

_prompt_template_cache: Dict[str, str] = {}


def _load_prompt_template(template_name: str) -> str:
    """从文件加载指定的Prompt模板，并使用缓存。"""
    if template_name in _prompt_template_cache:
        return _prompt_template_cache[template_name]

    template_path = PROMPT_DIR / template_name
    log.info(f"Loading prompt template from file: {template_path}")

    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        _prompt_template_cache[template_name] = template_content
        return template_content
    except FileNotFoundError:
        log.error(f"Prompt template file not found: {template_path}")
        raise
    except Exception as e:
        log.error(f"Error reading prompt template file {template_path}: {e}")
        raise


def get_formatted_prompt(template_name: str, substitutions: Dict[str, Any]) -> str:
    """
    加载指定的Prompt模板，并使用.replace()方法安全地替换所有占位符。

    Args:
        template_name: 要加载的模板文件名。
        substitutions: 一个包含占位符和其对应值的字典。

    Returns:
        一个准备好发送给LLM的完整Prompt字符串。
    """
    template = _load_prompt_template(template_name)

    # 循环替换，这种方式不会与JSON中的{}冲突
    for key, value in substitutions.items():
        placeholder = f"{{{key}}}"
        template = template.replace(placeholder, str(value))

    return template


def get_synthesis_prompt(context: str) -> str:
    """获取用于上下文合成的Prompt。"""
    return get_formatted_prompt(
        template_name=PROMPT_TEMPLATE_NAME,
        substitutions={"context": context}
    )
