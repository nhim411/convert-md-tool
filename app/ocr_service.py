"""
OCR Service
markitdown-ocr plugin wrapper for LLM Vision OCR on embedded images.
Supports any OpenAI-compatible LLM client.
"""

from __future__ import annotations

import logging

from llm_client import LLMClient

logger = logging.getLogger(__name__)


class OCRService:
    """markitdown-ocr plugin wrapper for image OCR via LLM Vision."""

    def __init__(self, llm_client: LLMClient):
        self._llm_client = llm_client

    def convert_with_ocr(self, file_path: str) -> str:
        """
        Convert document using markitdown-ocr plugin for embedded image OCR.

        Args:
            file_path: Path to the document (PDF, DOCX, PPTX, XLSX)

        Returns:
            Markdown text with OCR content embedded for images
        """
        try:
            from markitdown import MarkItDown

            md = MarkItDown(
                enable_plugins=True,
                llm_client=self._llm_client.client,
                llm_model=self._llm_client.model,
            )
            result = md.convert(file_path)
            return result.text_content
        except Exception as e:
            logger.error(f"markitdown-ocr conversion error for {file_path}: {e}")
            # Fallback: try standard markitdown without plugin
            try:
                from markitdown import MarkItDown

                md = MarkItDown(enable_plugins=False)
                result = md.convert(file_path)
                logger.warning(f"Fallback to standard markitdown for {file_path}")
                return result.text_content
            except Exception as e2:
                logger.error(f"markitdown fallback also failed for {file_path}: {e2}")
                raise
