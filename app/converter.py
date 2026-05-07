"""
Markdown Converter - Core Conversion Module
Wraps markitdown library for file conversion with error handling and batch processing.
Supports image extraction via markitdown-ocr and AI enrichment via LLMClient.
"""

import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


@dataclass
class AIOptions:
    """Options for AI handling (Image & Text)."""
    extract_images: bool = False
    ocr_enabled: bool = False
    chunk_enabled: bool = False
    excel_clean_enabled: bool = False
    summary_enabled: bool = False

    # OpenAI-Compatible Configuration
    base_url: str = "https://api.openai.com/v1"
    api_key: str = ""
    model: str = "gpt-4o-mini"


@dataclass
class ConversionResult:
    """Result of a single file conversion."""
    source_path: str
    output_path: Optional[str]
    success: bool
    error_message: Optional[str] = None
    skipped: bool = False
    images_extracted: int = 0
    images_described: int = 0


class MarkdownConverter:
    """Wrapper for markitdown + markitdown-ocr with batch processing."""

    SUPPORTED_FORMATS: Dict[str, List[str]] = {
        "PDF": [".pdf"],
        "Word": [".docx", ".doc"],
        "PowerPoint": [".pptx", ".ppt"],
        "Excel": [".xlsx", ".xls"],
        "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff"],
        "Text": [".csv", ".json", ".xml", ".txt"],
    }

    IMAGE_EXTRACTABLE_FORMATS = {".pdf", ".docx", ".doc", ".pptx", ".ppt"}

    def __init__(self):
        self._stop_requested = False
        self._ai_options = AIOptions()
        self._llm_client = None
        self._ocr_service = None
        self._rag_pipeline = None

    def set_ai_options(self, options: AIOptions):
        self._ai_options = options

    @classmethod
    def get_all_extensions(cls) -> Set[str]:
        extensions = set()
        for ext_list in cls.SUPPORTED_FORMATS.values():
            extensions.update(ext_list)
        return extensions

    @classmethod
    def get_extensions_for_formats(cls, format_names: List[str]) -> Set[str]:
        extensions = set()
        for name in format_names:
            if name in cls.SUPPORTED_FORMATS:
                extensions.update(cls.SUPPORTED_FORMATS[name])
        return extensions

    def request_stop(self):
        self._stop_requested = True

    def reset_stop(self):
        self._stop_requested = False

    def _get_llm_client(self):
        """Lazy-init LLM client."""
        if not self._ai_options.api_key:
            return None
        if self._llm_client is None:
            from llm_client import LLMClient
            self._llm_client = LLMClient(
                base_url=self._ai_options.base_url,
                api_key=self._ai_options.api_key,
                model=self._ai_options.model,
            )
        return self._llm_client

    def _get_ocr_service(self):
        """Lazy-init OCR service via markitdown-ocr."""
        if not self._ai_options.api_key:
            return None
        if self._ocr_service is None:
            client = self._get_llm_client()
            if client:
                from ocr_service import OCRService
                self._ocr_service = OCRService(client)
        return self._ocr_service

    def _get_rag_pipeline(self):
        """Lazy-init RAG pipeline."""
        if self._rag_pipeline is None:
            from rag_pipeline import RAGPipeline
            self._rag_pipeline = RAGPipeline()
        return self._rag_pipeline

    def convert_file(
        self,
        source_path: str,
        output_dir: Optional[str] = None,
        overwrite: bool = False,
    ) -> ConversionResult:
        """Convert a single file to Markdown."""
        source = Path(source_path)

        if not source.exists():
            return ConversionResult(source_path, None, False, "Không tìm thấy tệp")

        if not source.is_file():
            return ConversionResult(source_path, None, False, "Đường dẫn không phải là tệp")

        output_base = Path(output_dir) if output_dir else source.parent
        output_path = output_base / f"{source.name}.md"

        if output_path.exists() and not overwrite:
            return ConversionResult(source_path, str(output_path), True, skipped=True, error_message="File đã tồn tại, bỏ qua")

        try:
            output_base.mkdir(parents=True, exist_ok=True)

            # Step 1: Excel cleaning
            actual_source = source
            temp_cleaned_file = None
            if self._ai_options.excel_clean_enabled and source.suffix.lower() in (".xlsx", ".xls"):
                try:
                    from excel_cleaner import clean_excel_file
                    cleaned = clean_excel_file(str(source))
                    if cleaned:
                        temp_cleaned_file = cleaned
                        actual_source = Path(cleaned)
                except Exception as e:
                    logger.warning(f"Excel cleaning failed: {e}")

            try:
                # Step 2: Convert with markitdown-ocr if API key available AND OCR enabled
                if self._ai_options.api_key and self._ai_options.ocr_enabled:
                    ocr = self._get_ocr_service()
                    if ocr:
                        markdown_content = ocr.convert_with_ocr(str(actual_source))
                    else:
                        from markitdown import MarkItDown
                        md = MarkItDown(enable_plugins=False)
                        markdown_content = md.convert(str(actual_source), keep_data_uris=True).text_content
                else:
                    from markitdown import MarkItDown
                    md = MarkItDown(enable_plugins=False)
                    markdown_content = md.convert(str(actual_source), keep_data_uris=True).text_content
            finally:
                if temp_cleaned_file and os.path.exists(temp_cleaned_file):
                    try:
                        os.remove(temp_cleaned_file)
                    except OSError:
                        pass

            # Step 2.5: Image extraction (if enabled)
            images_extracted = 0
            images_dir = None
            if self._ai_options.extract_images:
                try:
                    images_dir = output_base / f"{source.name}_images"
                    
                    import re
                    import base64
                    import binascii
                    
                    # 1. Process inline base64 images generated by markitdown
                    pattern = r'!\[([^\]]*)\]\(data:image/([a-zA-Z0-9.+]+);base64,([a-zA-Z0-9+/=]+)\)'
                    if re.search(pattern, markdown_content):
                        images_dir.mkdir(parents=True, exist_ok=True)
                        
                        def replacer(match):
                            nonlocal images_extracted
                            alt_text = match.group(1)
                            ext = match.group(2)
                            if ext.lower() == 'jpeg': ext = 'jpg'
                            b64_data = match.group(3)
                            
                            images_extracted += 1
                            filename = f"image_{images_extracted}.{ext}"
                            out_path = images_dir / filename
                            
                            try:
                                image_bytes = base64.b64decode(b64_data)
                                out_path.write_bytes(image_bytes)
                            except binascii.Error:
                                pass # Invalid base64
                                
                            rel_path = f"{source.name}_images/{filename}"
                            return f"![{alt_text}]({rel_path})"
                            
                        markdown_content = re.sub(pattern, replacer, markdown_content)
                    
                    # 2. Process PDF images (pdfminer does not extract images, so we use PyMuPDF and append)
                    if source.suffix.lower() == ".pdf":
                        images_dir.mkdir(parents=True, exist_ok=True)
                        extracted_pdf = self._extract_images(actual_source, images_dir, start_count=images_extracted)
                        if extracted_pdf > 0:
                            images_extracted += extracted_pdf
                            img_refs = "\n\n## Hình ảnh đính kèm (PDF)\n\n"
                            # Append only the newly extracted PDF images
                            for img_file in sorted(images_dir.iterdir()):
                                if getattr(img_file, "is_newly_extracted", True): # We just append all for simplicity
                                    pass
                            
                            # Safely just iterate what's in the folder and append anything not already linked
                            # Wait, simple approach: just append all from PyMuPDF
                            # But since PDF doesn't have inline images, all images in images_dir are from PyMuPDF!
                            img_refs = "\n\n## Hình ảnh đính kèm\n\n"
                            for img_file in sorted(images_dir.iterdir()):
                                rel_path = f"{source.name}_images/{img_file.name}"
                                img_refs += f"![{img_file.stem}]({rel_path})\n\n"
                            markdown_content += img_refs
                            
                except Exception as e:
                    logger.warning(f"Image extraction failed: {e}")

            # Step 3: Text optimization
            try:
                from text_processor import clean_japanese_text, normalize_width
                markdown_content = clean_japanese_text(markdown_content)
                markdown_content = normalize_width(markdown_content)
            except Exception as e:
                logger.warning(f"Text optimization failed: {e}")

            # Step 4: AI enrichment
            if self._ai_options.summary_enabled and self._ai_options.api_key:
                try:
                    client = self._get_llm_client()
                    if client:
                        result = client.summarize(markdown_content[:8000])
                        summary = result.get("summary", "")
                        keywords = result.get("keywords", [])
                        if summary:
                            frontmatter = f"---\nsource_file: {source.name}\nconverted_at: {datetime.now(timezone.utc).isoformat()}\nai_summary: |-\n  {summary}\nai_keywords:\n"
                            for kw in keywords:
                                frontmatter += f"  - {kw}\n"
                            frontmatter += "---\n\n"
                            markdown_content = frontmatter + markdown_content
                except Exception as e:
                    logger.warning(f"AI summary failed: {e}")

            # Step 5: RAG Chunking
            if self._ai_options.chunk_enabled:
                try:
                    pipeline = self._get_rag_pipeline()
                    chunks = pipeline.chunk(markdown_content, source.name)
                    jsonl_path = output_path.with_suffix(".jsonl")
                    pipeline.save_jsonl(chunks, str(jsonl_path))
                    logger.info(f"Created RAG chunks: {jsonl_path}")
                except Exception as e:
                    logger.warning(f"RAG chunking failed: {e}")

            # Step 6: Add standard frontmatter if not added by AI
            if not self._ai_options.summary_enabled and not markdown_content.startswith("---"):
                frontmatter = f"---\nsource_file: {source.name}\nconverted_at: {datetime.now(timezone.utc).isoformat()}\n---\n\n"
                markdown_content = frontmatter + markdown_content

            # Step 7: Write output
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(markdown_content)

            logger.info(f"Converted: {source_path} -> {output_path}")

            return ConversionResult(
                source_path=source_path,
                output_path=str(output_path),
                success=True,
                images_extracted=images_extracted,
            )

        except PermissionError:
            return ConversionResult(source_path, None, False, "Không có quyền truy cập")
        except Exception as e:
            logger.error(f"Conversion failed for {source_path}: {e}")
            return ConversionResult(source_path, None, False, str(e))

    def _extract_images(self, source: "Path", images_dir: "Path", start_count: int = 0) -> int:
        """
        Extract images from PDF using PyMuPDF. 
        DOCX and PPTX are handled inline via markitdown base64 extraction.
        Returns number of extracted images.
        """
        count = 0
        suffix = source.suffix.lower()

        if suffix == ".pdf":
            try:
                import fitz  # PyMuPDF
                doc = fitz.open(str(source))
                for page_num in range(len(doc)):
                    images = doc.get_page_images(page_num)
                    for img_idx, img in enumerate(images):
                        xref = img[0]
                        image_data = doc.extract_image(xref)
                        img_bytes = image_data["image"]
                        ext = image_data.get("ext", "png")
                        out_path = images_dir / f"page{page_num + 1}_img{start_count + count + 1}.{ext}"
                        out_path.write_bytes(img_bytes)
                        count += 1
                doc.close()
            except Exception as e:
                logger.warning(f"PyMuPDF failed or not installed, skipping PDF image extraction: {e}")

        return count

    def scan_folder(
        self,
        folder_path: str,
        recursive: bool = False,
        max_depth: Optional[int] = None,
        allowed_extensions: Optional[Set[str]] = None,
    ) -> List[str]:
        """Scan folder for convertible files."""
        folder = Path(folder_path)
        if not folder.exists() or not folder.is_dir():
            return []

        if allowed_extensions is None:
            allowed_extensions = self.get_all_extensions()

        files = []

        def scan_dir(dir_path: Path, current_depth: int = 0):
            if self._stop_requested:
                return
            try:
                for item in dir_path.iterdir():
                    if self._stop_requested:
                        return
                    if item.is_file():
                        if item.suffix.lower() in allowed_extensions:
                            files.append(str(item))
                    elif item.is_dir() and recursive:
                        if max_depth is None or current_depth < max_depth:
                            scan_dir(item, current_depth + 1)
            except PermissionError:
                logger.warning(f"Permission denied: {dir_path}")

        scan_dir(folder)
        return sorted(files)

    def convert_folder(
        self,
        folder_path: str,
        recursive: bool = False,
        max_depth: Optional[int] = None,
        allowed_formats: Optional[List[str]] = None,
        output_dir: Optional[str] = None,
        overwrite: bool = False,
        progress_callback: Optional[Callable[[int, int, ConversionResult], None]] = None,
    ) -> List[ConversionResult]:
        """Convert all matching files in a folder."""
        self.reset_stop()

        if allowed_formats:
            allowed_extensions = self.get_extensions_for_formats(allowed_formats)
        else:
            allowed_extensions = self.get_all_extensions()

        files = self.scan_folder(
            folder_path,
            recursive=recursive,
            max_depth=max_depth,
            allowed_extensions=allowed_extensions,
        )

        if not files:
            return []

        results = []
        total = len(files)

        for i, file_path in enumerate(files):
            if self._stop_requested:
                break
            result = self.convert_file(file_path, output_dir, overwrite=overwrite)
            results.append(result)
            if progress_callback:
                progress_callback(i + 1, total, result)

        return results
