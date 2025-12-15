# app.py
from cortex.services.retrieval import RetrievalService
from cortex.services.ingestion import IngestionService
from cortex.core.models import ContextResponse
import chainlit as cl
from chainlit.element import Element
import os
import sys
from typing import List
from cortex.logger.logger import get_logger

log = get_logger(__name__)

# 【关键】将src目录添加到Python的模块搜索路径中
# 这使得我们可以直接从根目录运行app.py，并导入cortex包
sys.path.insert(0, os.path.abspath("./src"))


# --- 在应用启动时，一次性加载所有需要的服务和模型 ---
# 这可以确保模型只被加载一次，而不是在每个会话中都重新加载
try:
    ingestion_service = IngestionService()
    retrieval_service = RetrievalService()
except Exception as e:
    log.info(f"Fatal error during service initialization: {e}")
    # 在实际应用中，这里应该有更健壮的错误处理
    sys.exit(1)

# --- Chainlit 应用逻辑 ---


@cl.on_chat_start
async def start_chat():
    """
    当一个新的聊天会话开始时，这个函数会被调用。
    """
    await cl.Message(
        content="欢迎使用 **Cortex** 记忆助手！\n\n"
                "您可以直接向我提问，我会根据您的记忆库生成上下文。\n\n"
                "或者，您可以上传一份文本文件（`.txt`, `.md`）来扩充您的记忆库。",
        author="Cortex"
    ).send()


@cl.on_message
async def main(message: cl.Message):
    """
    当用户发送一条消息时，这个函数会被调用。
    """
    # 检查是否有文件被上传
    files = message.elements
    if files:
        await process_uploaded_files(files)
        return

    # 如果没有文件，则处理用户的文本查询
    query = message.content

    # 发送一个“思考中”的占位符，提升用户体验
    thinking_message = cl.Message(content="", author="Cortex")
    await thinking_message.send()

    # 调用我们的核心检索服务
    response: ContextResponse = retrieval_service.query_and_synthesize(query)

    # 将最终的“记忆包”格式化并发送给用户
    memory_packet_element = cl.Text(
        name="memory_packet.md",
        content=response.context,
        display="inline"
    )

    thinking_message.content = (
        f"好的，我已经根据您的主题 **'{query}'** 生成了一份上下文“记忆包”。\n\n"
        f"这份摘要参考了 **{len(response.retrieved_sources)}** 个原始记忆来源：`{', '.join(response.retrieved_sources)}`\n\n"
        "您可以直接复制下方的文本，并将其用于您接下来的LLM对话中。"
    )
    thinking_message.elements = [memory_packet_element]
    await thinking_message.update()


async def process_uploaded_files(files: List[Element]):
    """
    处理用户上传的文件。
    """
    for file in files:
        # 检查文件路径是否存在，并且MIME类型是可接受的
        if file.path and ("text" in file.mime or "octet-stream" in file.mime or file.name.endswith('.md')):
            try:
                # 从文件路径读取内容
                with open(file.path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 确保读取后的内容不为空（或仅有空白符）
                if not content.strip():
                    await cl.Message(content=f"文件 `{file.name}` 已跳过 (文件内容为空)。", author="Cortex").send()
                    continue

                # 发送一个“处理中”的消息
                processing_msg = cl.Message(
                    content=f"正在摄入记忆文件: `{file.name}` ...", author="Cortex")
                await processing_msg.send()

                # 调用我们的核心摄入服务
                ingestion_service.process(content=content, source=file.name)
                processing_msg.content = f"✅ 记忆文件 `{file.name}` 已成功摄入！"
                await processing_msg.update()

            except Exception as e:
                await cl.Message(content=f"❌ 处理文件 `{file.name}` 时发生错误: {e}", author="Cortex").send()

        else:
            reason = "不是支持的文本格式"
            if not file.path:
                reason = "无法访问文件路径"
            elif "text" not in file.mime:
                reason = f"文件类型 '{file.mime}' 不受支持"

            await cl.Message(
                content=f"文件 `{file.name}` 已跳过 ({reason})。",
                author="Cortex"
            ).send()
