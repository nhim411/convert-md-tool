"""
AI Helper Module
Provides AI services for text summarization and enrichment.
Supports OpenAI and Google Gemini.
"""

import logging
from typing import Optional, List
import textwrap

logger = logging.getLogger(__name__)

class AIService:
    """
    Unified AI Service for Text operations.
    """

    def __init__(
        self,
        provider: str = "openai",
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ):
        """
        Initialize AI Service.

        Args:
            provider: 'openai' or 'gemini'
            api_key: API key
            model: Model name
        """
        self.provider = provider.lower()
        self.api_key = api_key

        if self.provider == "openai":
            self.model = model or "gpt-4o-mini"
        elif self.provider == "gemini":
            self.model = model or "gemini-1.5-flash"
        else:
            self.model = model # custom provider?

    def summarize_text(self, text: str, max_length: int = 150) -> Optional[str]:
        """
        Summarize the given text.
        """
        if not self.api_key:
            return None

        # Truncate text if too long to save tokens (start + end)
        if len(text) > 10000:
            text = text[:8000] + "\n...\n" + text[-2000:]

        prompt = f"""
        Analyze the following text and provide:
        1. A concise summary (max 3 sentences).
        2. 5 key tags/keywords.

        Format output as YAML Block:
        ```yaml
        summary: "..."
        tags: [tag1, tag2]
        ```

        Text:
        {text}
        """

        try:
            if self.provider == "openai":
                return self._call_openai(prompt)
            elif self.provider == "gemini":
                return self._call_gemini(prompt)
        except Exception as e:
            logger.error(f"AI Summarization failed: {e}")
            return None

    def _call_openai(self, prompt: str) -> Optional[str]:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200
            )
            return response.choices[0].message.content
        except ImportError:
            logger.error("openai module not found")
            return None

    def _call_gemini(self, prompt: str) -> Optional[str]:
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(self.model)
            response = model.generate_content(prompt)
            return response.text
        except ImportError:
            logger.error("google-generativeai module not found")
            return None

    @staticmethod
    def fetch_available_models(provider: str, api_key: str) -> List[str]:
        """
        Fetch available models from the provider.
        """
        if not api_key:
            return []

        try:
            if provider == "openai":
                from openai import OpenAI
                client = OpenAI(api_key=api_key)
                models = client.models.list()
                # Filter useful chat models
                return sorted([
                    m.id for m in models
                    if m.id.startswith(("gpt-4", "gpt-3.5", "o1"))
                    and "audio" not in m.id and "realtime" not in m.id
                ], reverse=True)

            elif provider == "gemini":
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                models = genai.list_models()
                # Filter generation models
                return sorted([
                    m.name.replace("models/", "")
                    for m in models
                    if "generateContent" in m.supported_generation_methods
                ], reverse=True)

        except Exception as e:
            logger.error(f"Failed to fetch models for {provider}: {e}")
            return []

        return []
