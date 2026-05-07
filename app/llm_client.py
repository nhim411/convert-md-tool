"""
LLM Client
Unified OpenAI-compatible client for text and vision operations.
Supports any OpenAI-compatible endpoint: OpenAI, Azure, Ollama, LM Studio, vLLM, Groq, etc.
"""

import logging
import base64
from typing import Optional

logger = logging.getLogger(__name__)


class LLMClient:
    """Unified OpenAI-compatible LLM client for text + vision."""

    def __init__(self, base_url: str, api_key: str, model: str):
        from openai import OpenAI
        self._client = OpenAI(
            base_url=base_url.rstrip("/"),
            api_key=api_key,
            timeout=30.0,
        )
        self._model = model

    @property
    def client(self):
        return self._client

    @property
    def model(self) -> str:
        return self._model

    def summarize(self, text: str) -> dict[str, str | list[str]]:
        """
        Gọi LLM để tạo tóm tắt và keywords.

        Args:
            text: Text cần tóm tắt (có thể cắt trước 8000 ký tự)

        Returns:
            dict với keys: summary (str), keywords (list[str])
        """
        prompt = (
            "Bạn là một trợ lý AI chuyên tóm tắt tài liệu. "
            "Hãy đọc đoạn văn bản sau và trả lời theo format YAML:\n\n"
            "summary: |-\n  <tóm tắt 2-3 câu về nội dung chính của tài liệu>\n"
            "keywords:\n  - <keyword 1>\n  - <keyword 2>\n  - <keyword 3>\n  - <keyword 4>\n  - <keyword 5>\n\n"
            f"Văn bản:\n{text[:8000]}"
        )

        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": "Bạn là một trợ lý AI chuyên tóm tắt tài liệu. Trả lời CHỉ bằng YAML, không giải thích gì thêm."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3,
            )
            content = response.choices[0].message.content.strip()

            result: dict[str, str | list[str]] = {"summary": "", "keywords": []}
            for line in content.splitlines():
                if line.startswith("summary: |-"):
                    result["summary"] = line.replace("summary: |-", "").strip()
                elif line.startswith("summary: "):
                    result["summary"] = line.replace("summary: ", "").strip()
                elif line.strip().startswith("-"):
                    keyword = line.strip()[1:].strip()
                    if keyword:
                        result["keywords"].append(keyword)

            return result
        except Exception as e:
            logger.error(f"summarize error: {e}")
            return {"summary": "", "keywords": []}

    def describe_image(self, image_bytes: bytes, prompt: str) -> str:
        """
        Gọi Vision API để mô tả ảnh.

        Args:
            image_bytes: Bytes của ảnh
            prompt: Prompt cho vision model

        Returns:
            Mô tả text của ảnh
        """
        try:
            b64 = base64.b64encode(image_bytes).decode("utf-8")
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/png;base64,{b64}"},
                            },
                        ],
                    }
                ],
                max_tokens=300,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"describe_image error: {e}")
            return ""

    def chat(self, messages: list[dict]) -> str:
        """
        Generic chat completion.

        Args:
            messages: List of {"role": "...", "content": "..."} dicts

        Returns:
            Assistant response text
        """
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=messages,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"chat error: {e}")
            return ""

    @staticmethod
    def fetch_models(base_url: str, api_key: str) -> list[str]:
        """
        Gọi /models endpoint để lấy danh sách models.

        Args:
            base_url: Base URL của API (vd: https://api.openai.com/v1)
            api_key: API key

        Returns:
            List of model names
        """
        from openai import OpenAI

        url = base_url.rstrip("/")
        try:
            client = OpenAI(base_url=url, api_key=api_key)
            response = client.models.list()
            models = [m.id for m in response.data]
            logger.info(f"fetched {len(models)} models from {url}")
            return sorted(models)
        except Exception as e:
            logger.error(f"fetch_models error: {e}")
            return []

    def test_connection(self) -> tuple[bool, str]:
        """
        Test kết nối tới API.

        Returns:
            (success: bool, message: str)
        """
        try:
            self._client.chat.completions.create(
                model=self._model,
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=5,
            )
            return True, "✅ Kết nối thành công"
        except Exception as e:
            return False, f"❌ Lỗi: {e}"
