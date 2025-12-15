# core/models.py
from pydantic import BaseModel, Field
from typing import List


class IngestRequest(BaseModel):
    """记忆摄入请求体"""
    content: str = Field(..., description="需要摄入的原始文本内容")
    source: str = Field(...,
                        description="记忆来源，例如 'chatgpt_export.json' 或 'ide_plugin'")


class QueryRequest(BaseModel):
    """记忆查询请求体"""
    query: str = Field(..., description="用户查询的主题")


class ContextResponse(BaseModel):
    """
    记忆查询的上下文响应体。
    这是返回给前端的、用于生成“记忆包”的核心数据。
    """
    context: str = Field(..., description="由LLM提炼和总结后的上下文摘要")
    retrieved_sources: List[str] = Field(..., description="生成该摘要所参考的原始记忆来源列表")
