from cortex.logger.logger import get_logger
import re
log = get_logger(__name__)


class Chunck:
    def clean_text(self, text: str) -> str:
        """
        执行基础的文本清洗。
        - 移除多余的空白字符
        - 可以在这里扩展更复杂的清洗逻辑，如去除HTML标签等
        """
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def chunk_text(self, text: str, chunk_size: int = 512, chunk_overlap: int = 50) -> list[str]:
        """
        一个简单的递归字符文本分块器。
        """
        if len(text) <= chunk_size:
            return [text]

        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunks.append(text[start:end])
            start += chunk_size - chunk_overlap
        return chunks
