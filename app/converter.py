"""
Markdown Converter - Core Conversion Module
Wraps markitdown library for file conversion with error handling and batch processing.
Supports image extraction and AI description.
"""

import os
import logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Set, Callable
from markitdown import MarkItDown
from datetime import datetime
import json
import text_processor
import ai_helper
import chunker
import excel_cleaner

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class AIOptions:
    """Options for AI handling (Image & Text)."""
    extract_images: bool = False
    describe_images: bool = False

    # RAG & Summarization
    chunk_enabled: bool = False
    excel_clean_enabled: bool = False
    summary_enabled: bool = False

    ai_provider: str = "openai"
    api_key: Optional[str] = None
    ai_model: Optional[str] = None
    images_subdir: str = "images"


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
    """
    Wrapper for markitdown library with batch processing support.
    """

    # Mapping of format categories to file extensions
    # Optimized for minimal build size
    SUPPORTED_FORMATS: Dict[str, List[str]] = {
        'PDF': ['.pdf'],
        'Word': ['.docx', '.doc'],
        'PowerPoint': ['.pptx', '.ppt'],
        'Excel': ['.xlsx', '.xls'],
        'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff'],
        'Text': ['.csv', '.json', '.xml', '.txt'],
    }

    # Formats that support image extraction
    IMAGE_EXTRACTABLE_FORMATS = {'.pdf', '.docx', '.doc', '.pptx', '.ppt'}

    def __init__(self):
        """Initialize the converter with markitdown instance."""
        self._md = MarkItDown(enable_plugins=False)
        self._stop_requested = False
        self._ai_options = AIOptions()

    def set_ai_options(self, options: AIOptions):
        """Set AI handling options."""
        self._ai_options = options

    @classmethod
    def get_all_extensions(cls) -> Set[str]:
        """Get all supported file extensions."""
        extensions = set()
        for ext_list in cls.SUPPORTED_FORMATS.values():
            extensions.update(ext_list)
        return extensions

    @classmethod
    def get_extensions_for_formats(cls, format_names: List[str]) -> Set[str]:
        """Get file extensions for specified format categories."""
        extensions = set()
        for name in format_names:
            if name in cls.SUPPORTED_FORMATS:
                extensions.update(cls.SUPPORTED_FORMATS[name])
        return extensions

    def request_stop(self):
        """Request to stop ongoing batch conversion."""
        self._stop_requested = True

    def reset_stop(self):
        """Reset stop flag for new conversion."""
        self._stop_requested = False

    def _process_images(
        self,
        source_path: str,
        output_dir: Path,
        base_name: str
    ) -> tuple:
        """
        Extract and optionally describe images from a document.

        Returns:
            Tuple of (markdown_text, images_extracted, images_described)
        """
        from image_handler import (
            ImageExtractor,
            AIImageDescriber,
            format_images_for_markdown
        )

        ext = Path(source_path).suffix.lower()
        if ext not in self.IMAGE_EXTRACTABLE_FORMATS:
            return "", 0, 0

        # Extract images
        images = ImageExtractor.extract_images(source_path)
        if not images:
            return "", 0, 0

        images_extracted = len(images)
        images_described = 0

        # Save images to per-file folder: {base_name}_images/
        images_dir = output_dir / f"{base_name}_images"
        ImageExtractor.save_images(images, str(images_dir), base_name)

        # Describe images with AI if enabled
        if self._ai_options.describe_images and self._ai_options.api_key:
            try:
                describer = ai_helper.AIService( # Use AIService for image description via helper if refactored?
                    # Wait, AIService currently text only in my impl?
                    # Let's import ImageDescriber from image_handler for now as before,
                    # but use the unified options.
                    # Or better: make AIService handle both.
                    # For now keep using image_handler.AIImageDescriber but pass new options.
                    provider=self._ai_options.ai_provider,
                    api_key=self._ai_options.api_key,
                    model=self._ai_options.ai_model
                )
                # Note: I need to update image_handler.AIImageDescriber init to accept model properly if changed
                # It accepts (provider, api_key, model) so it's fine.

                # Actually I should use the class directly
                from image_handler import AIImageDescriber
                describer = AIImageDescriber(
                    provider=self._ai_options.ai_provider,
                    api_key=self._ai_options.api_key,
                    model=self._ai_options.ai_model
                )
                images = describer.describe_images(images)
                images_described = sum(1 for img in images if img.description)
            except Exception as e:
                logger.error(f"Failed to describe images: {e}")

        # Generate markdown for images
        md_text = format_images_for_markdown(
            images,
            str(images_dir),
            base_name,
            relative_path=True
        )

        return md_text, images_extracted, images_described

    def convert_file(
        self,
        source_path: str,
        output_dir: Optional[str] = None,
        overwrite: bool = False
    ) -> ConversionResult:
        """
        Convert a single file to Markdown.

        Args:
            source_path: Path to the source file
            output_dir: Optional output directory. If None, outputs to same directory as source.
            overwrite: If True, overwrite existing .md files. If False, skip.

        Returns:
            ConversionResult with success status and output path
        """
        source = Path(source_path)

        # Validate source file
        if not source.exists():
            return ConversionResult(
                source_path=source_path,
                output_path=None,
                success=False,
                error_message="Không tìm thấy tệp"
            )

        if not source.is_file():
            return ConversionResult(
                source_path=source_path,
                output_path=None,
                success=False,
                error_message="Đường dẫn không phải là tệp"
            )

        # Determine output path
        if output_dir:
            output_base = Path(output_dir)
        else:
            output_base = source.parent

        output_path = output_base / f"{source.name}.md"

        # Check if file exists and skip if not overwriting
        if output_path.exists() and not overwrite:
            return ConversionResult(
                source_path=source_path,
                output_path=str(output_path),
                success=True,
                skipped=True,
                error_message="File đã tồn tại, bỏ qua"
            )

        try:
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Excel Cleaning (Option A)
            actual_source = source
            temp_cleaned_file = None
            if self._ai_options.excel_clean_enabled and source.suffix.lower() in ['.xlsx', '.xls']:
                try:
                    cleaned = excel_cleaner.clean_excel_file(str(source))
                    if cleaned:
                        temp_cleaned_file = cleaned
                        actual_source = Path(cleaned)
                except Exception as e:
                    logger.warning(f"Excel cleaning failed, using original: {e}")

            try:
                # Convert using markitdown
                result = self._md.convert(str(actual_source))
                markdown_content = result.text_content
            finally:
                # Cleanup temp file
                if temp_cleaned_file and os.path.exists(temp_cleaned_file):
                    try:
                        os.remove(temp_cleaned_file)
                    except OSError:
                        pass

            # Process images if enabled
            images_extracted = 0
            images_described = 0

            # Process images if enabled
            images_extracted = 0
            images_described = 0

            if self._ai_options.extract_images:
                try:
                    images_md, images_extracted, images_described = self._process_images(
                        str(source),
                        output_base,
                        source.name
                    )
                    if images_md:
                        markdown_content += images_md
                except Exception as e:
                    logger.warning(f"Image processing failed: {e}")

            # Optimize for Japanese RAG
            try:
                # Clean text (remove spaces between JP chars)
                markdown_content = text_processor.clean_japanese_text(markdown_content)
                markdown_content = text_processor.normalize_width(markdown_content)

                # AI Enrichment (Summary & Keywords)
                ai_frontmatter = ""
                if self._ai_options.summary_enabled and self._ai_options.api_key:
                    try:
                        ai_service = ai_helper.AIService(
                            provider=self._ai_options.ai_provider,
                            api_key=self._ai_options.api_key,
                            model=self._ai_options.ai_model
                        )
                        summary_yaml = ai_service.summarize_text(markdown_content)
                        if summary_yaml:
                            ai_frontmatter = summary_yaml + "\n"
                    except Exception as e:
                        logger.warning(f"AI Summary failed: {e}")

                # Add RAG Metadata (Frontmatter)
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                frontmatter = f"---\nsource_file: {source.name}\nconverted_at: {timestamp}\n{ai_frontmatter}---\n\n"
                markdown_content = frontmatter + markdown_content

                # RAG Chunking
                if self._ai_options.chunk_enabled:
                    try:
                        rag_chunker = chunker.MarkdownChunker()
                        chunks = rag_chunker.chunk_text(markdown_content, source.name)

                        # Save .jsonl
                        jsonl_path = output_path.with_suffix('.jsonl')
                        with open(jsonl_path, 'w', encoding='utf-8') as f:
                            for chunk in chunks:
                                f.write(json.dumps(chunk, ensure_ascii=False) + "\n")
                        logger.info(f"Created RAG chunks: {jsonl_path}")
                    except Exception as e:
                        logger.warning(f"Chunking failed: {e}")

            except Exception as e:
                logger.warning(f"Text optimization failed: {e}")

            # Write output
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)

            logger.info(f"Converted: {source_path} -> {output_path}")

            return ConversionResult(
                source_path=source_path,
                output_path=str(output_path),
                success=True,
                images_extracted=images_extracted,
                images_described=images_described
            )

        except PermissionError:
            return ConversionResult(
                source_path=source_path,
                output_path=None,
                success=False,
                error_message="Không có quyền truy cập"
            )
        except Exception as e:
            logger.error(f"Conversion failed for {source_path}: {e}")
            return ConversionResult(
                source_path=source_path,
                output_path=None,
                success=False,
                error_message=str(e)
            )

    def scan_folder(
        self,
        folder_path: str,
        recursive: bool = False,
        max_depth: Optional[int] = None,
        allowed_extensions: Optional[Set[str]] = None
    ) -> List[str]:
        """
        Scan folder for convertible files.

        Args:
            folder_path: Path to folder
            recursive: Whether to scan subfolders
            max_depth: Maximum depth for recursive scan (None = unlimited)
            allowed_extensions: Set of allowed extensions (None = all supported)

        Returns:
            List of file paths
        """
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
        progress_callback: Optional[Callable[[int, int, ConversionResult], None]] = None
    ) -> List[ConversionResult]:
        """
        Convert all matching files in a folder.

        Args:
            folder_path: Path to folder
            recursive: Whether to include subfolders
            max_depth: Maximum depth for recursive conversion
            allowed_formats: List of format category names to include
            output_dir: Optional output directory
            overwrite: If True, overwrite existing .md files. If False, skip.
            progress_callback: Optional callback(current, total, result) for progress updates

        Returns:
            List of ConversionResult for each file
        """
        self.reset_stop()

        # Get allowed extensions
        if allowed_formats:
            allowed_extensions = self.get_extensions_for_formats(allowed_formats)
        else:
            allowed_extensions = self.get_all_extensions()

        # Scan for files
        files = self.scan_folder(
            folder_path,
            recursive=recursive,
            max_depth=max_depth,
            allowed_extensions=allowed_extensions
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
