import unittest
from unittest.mock import patch, MagicMock

from .ingestion import IngestionService

# --- 模拟数据 ---
SUCCESS_RESPONSE_FROM_LLM = "[JSON_START]\n{\n  \"source\": \"gemini\",\n  \"source_type\": \"llm_chat\",\n  \"tags\": [\"java\", \"workflow_engine\"]\n}\n[JSON_END]"
INVALID_JSON_RESPONSE_FROM_LLM = "[JSON_START]\n{\n  \"source\": \"gemini\",\n  \"tags\": [\"java\"\n}\n[JSON_END]"
NO_DELIMITER_RESPONSE_FROM_LLM = "{\n  \"source\": \"gemini\",\n  \"tags\": []\n}"


class TestIngestionServiceMetadataExtraction(unittest.TestCase):

    def setUp(self):
        self.mock_storage_service = MagicMock()

        self.ingestion_service = IngestionService(
            storage_service=self.mock_storage_service)

    @patch('cortex.services.ingestion.generate_chat_completion')
    @patch('cortex.services.ingestion.get_formatted_prompt')
    def test_extract_metadata_happy_path(self, mock_get_formatted_prompt, mock_generate_chat):
        """测试：Happy Path。"""
        # 准备
        mock_get_formatted_prompt.return_value = "A clean prompt"
        mock_generate_chat.return_value = SUCCESS_RESPONSE_FROM_LLM

        # 执行
        result = self.ingestion_service._extract_metadata_with_llm(
            "gemini_chat.md", "A chat about java.")

        # 断言
        expected = {"source": "gemini", "source_type": "llm_chat",
                    "tags": ["java", "workflow_engine"]}
        self.assertDictEqual(result, expected)
        mock_generate_chat.assert_called_once()
        mock_get_formatted_prompt.assert_called_once()

    @patch('cortex.services.ingestion.generate_chat_completion')
    @patch('cortex.services.ingestion.get_formatted_prompt')
    def test_fallback_when_llm_fails(self, mock_get_formatted_prompt, mock_generate_chat):
        """测试：当LLM调用本身抛出异常时，应回退。"""
        # 准备
        mock_get_formatted_prompt.return_value = "A prompt"
        mock_generate_chat.side_effect = Exception("Ollama connection failed")

        # 执行
        result = self.ingestion_service._extract_metadata_with_llm(
            "my_notes.txt", "Some notes.")

        # 断言
        self.assertDictEqual(
            result, {"source": "my", "source_type": "document", "tags": []})

    @patch('cortex.services.ingestion.generate_chat_completion')
    @patch('cortex.services.ingestion.get_formatted_prompt')
    def test_fallback_with_invalid_json(self, mock_get_formatted_prompt, mock_generate_chat):
        """测试：当LLM返回的JSON格式错误时，应回退"""
        mock_get_formatted_prompt.return_value = "A prompt"
        mock_generate_chat.return_value = INVALID_JSON_RESPONSE_FROM_LLM
        result = self.ingestion_service._extract_metadata_with_llm(
            "chatgpt.json", "A chat.")
        self.assertDictEqual(
            result, {"source": "chatgpt.json", "source_type": "document", "tags": []})

    @patch('cortex.services.ingestion.generate_chat_completion')
    @patch('cortex.services.ingestion.get_formatted_prompt')
    def test_direct_parse_if_delimiters_missing(self, mock_get_formatted_prompt, mock_generate_chat):
        """测试：如果LLM忘记了分隔符但返回了纯净JSON，应尝试直接解析"""
        mock_get_formatted_prompt.return_value = "A prompt"
        mock_generate_chat.return_value = NO_DELIMITER_RESPONSE_FROM_LLM
        result = self.ingestion_service._extract_metadata_with_llm(
            "qwen_log.txt", "A log.")
        # expected = json.loads(NO_DELIMITER_RESPONSE_FROM_LLM)
        self.assertDictEqual(
            result, {"source": "qwen", "source_type": "document", "tags": []})


if __name__ == '__main__':
    unittest.main()
