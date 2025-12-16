# /src/cortex/core/model_chat.py
import ollama
import requests
from cortex.core.config import (
    SYNTHESIS_MODEL_PROVIDER,
    SYNTHESIS_MODEL,
    MODEL_API_KEY,
    MODEL_API_URL
)
from cortex.logger.logger import get_logger
from typing import Dict, Any

log = get_logger(__name__)


def generate_chat_completion(prompt: str) -> str:
    """
    根据配置，调用本地或远程的LLM生成聊天响应。

    Args:
        prompt: 发送给模型的完整Prompt。

    Returns:
        模型生成的文本响应。
    """
    log.info(
        f"Generating chat completion using provider: {SYNTHESIS_MODEL_PROVIDER}")

    try:
        if SYNTHESIS_MODEL_PROVIDER == "local":
            return _call_local_ollama(prompt)
        elif SYNTHESIS_MODEL_PROVIDER == "qwen":
            return _call_remote_qwen(prompt)
        else:
            log.error(
                f"Unsupported model provider: {SYNTHESIS_MODEL_PROVIDER}")
            raise ValueError(
                f"Unsupported model provider: {SYNTHESIS_MODEL_PROVIDER}")
    except Exception as e:
        log.error(
            f"Error calling LLM provider '{SYNTHESIS_MODEL_PROVIDER}': {e}")
        # 在调用失败时返回一个标准的错误信息，而不是原始的上下文
        return "无法连接到语言模型进行摘要合成。"


def _call_local_ollama(prompt: str) -> str:
    """调用本地Ollama模型。"""
    response = ollama.chat(
        model=SYNTHESIS_MODEL,
        messages=[{'role': 'user', 'content': prompt}]
    )
    return response['message']['content']


def _call_remote_qwen(prompt: str) -> str:
    """调用远程的通义千问（Qwen）API。"""
    if not MODEL_API_KEY or not MODEL_API_URL:
        raise ValueError("Qwen API key or URL is not configured.")

    headers = {
        "Authorization": f"Bearer {MODEL_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": SYNTHESIS_MODEL,
        "input": {
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
    }

    response = requests.post(MODEL_API_URL, headers=headers, json=payload)
    response.raise_for_status()  # 如果HTTP请求失败，则抛出异常

    # 解析Qwen API的响应结构
    response_data = response.json()
    return response_data['output']['choices'][0]['message']['content']
