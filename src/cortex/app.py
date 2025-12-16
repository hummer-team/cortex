# app.py
from cortex.services.retrieval import RetrievalService
from cortex.services.ingestion import IngestionService
from cortex.services.storage import storage_service
import chainlit as cl
from chainlit.element import Element
import os
import sys
from typing import List, Optional
from cortex.logger.logger import get_logger
import asyncio

log = get_logger(__name__)

sys.path.insert(0, os.path.abspath("./src"))

# --- 在应用启动时，一次性加载所有需要的服务和模型 ---
try:
    ingestion_service = IngestionService(storage_service=storage_service)
    retrieval_service = RetrievalService(storage_service=storage_service)
except Exception as e:
    log.error(f"Fatal error during service initialization: {e}")
    sys.exit(1)


@cl.on_chat_start
async def start_chat():
    await cl.Message(
        content="欢迎使用 **Cortex** 记忆助手！\n\n"
                "您可以直接向我提问，我会根据您的记忆库生成上下文。\n\n"
                "或者，您可以上传一份文本文件（`.txt`, `.md`），并附上一句描述。",
        author="Cortex"
    ).send()


@cl.on_message
async def main(message: cl.Message):
    if message.elements:
        description = message.content if message.content.strip() else None
        await process_uploaded_files(message.elements, description)
        return

    query = message.content
    thinking_msg = cl.Message(content="", author="Cortex")
    await thinking_msg.send()
    await thinking_msg.stream_token("🧠 正在检索您的记忆库...")
    await asyncio.sleep(0.5)
    retrieval_result = retrieval_service.retrieve_and_prepare_context(query)
    if not retrieval_result:
        await thinking_msg.stream_token("\n\n未找到与您查询相关的记忆。")
        await thinking_msg.update()
        return
    context_for_synthesis, sources = retrieval_result
    await thinking_msg.stream_token(f"\n\n📚 找到了 {len(sources)} 条相关记忆。")
    await asyncio.sleep(0.5)
    await thinking_msg.stream_token("\n\n✍️ 正在为您生成上下文摘要...")
    await asyncio.sleep(0.5)
    synthesized_context = retrieval_service.synthesize_context(
        context_for_synthesis)
    memory_packet_element = cl.Text(
        name="memory_packet.md", content=synthesized_context, display="inline")
    final_content = (
        f"好的，我已经根据您的主题 **'{query}'** 生成了一份上下文“记忆包”。\n\n"
        f"这份摘要参考了 **{len(sources)}** 个原始记忆来源：`{', '.join(sources)}`\n\n"
        "您可以直接复制下方的文本，并将其用于您接下来的LLM对话中。"
    )
    thinking_msg.content = final_content
    thinking_msg.elements = [memory_packet_element]
    await thinking_msg.update()


async def process_uploaded_files(files: List[Element], description: Optional[str]):
    for file in files:
        try:
            with open(file.path, 'r', encoding='utf-8') as f:
                content = f.read()
            if not content.strip():
                await cl.Message(content=f"文件 `{file.name}` 已跳过 (文件内容为空)。", author="Cortex").send()
                continue
            final_description = description
            if not final_description:
                res = await cl.AskUserMessage(
                    content=f"✅ 文件 `{file.name}` 已收到。\n\n请用一句话描述这份记忆的内容（例如：‘这是关于用Java实现工作流的Gemini对话’），或者直接回复‘跳过’。",
                    timeout=120,
                    author="Cortex"
                ).send()
                if res and res['content'].lower().strip() not in ["跳过", "skip"]:
                    final_description = res['content']
            processing_msg = cl.Message(
                content=f"正在处理 `{file.name}`...", author="Cortex")
            await processing_msg.send()
            ingestion_service.process(
                content=content,
                source_filename=file.name,
                description=final_description
            )
            processing_msg.content = f"✅ 记忆文件 `{file.name}` 已成功摄入！"
            await processing_msg.update()
        except Exception as e:
            log.error(f"Error processing file {file.name}: {e}")
            await cl.Message(content=f"❌ 处理文件 `{file.name}` 时发生错误。", author="Cortex").send()
