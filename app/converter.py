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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ImageOptions:
    """Options for image handling during conversion."""
    extract_images: bool = False
    describe_images: bool = False
    ai_provider: str = "openai"  # 'openai' or 'gemini'
    api_key: Optional[str] = None
    images_subdir: str = "images"


@dataclass
class ConversionResult:
    """Result of a single file conversion."""
    source_path: str
    output_path: Optional[str]
    success: bool
    error_message: Optional[str] = None
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
        self._image_options = ImageOptions()

    def set_image_options(self, options: ImageOptions):
        """Set image handling options."""
        self._image_options = options

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
        if self._image_options.describe_images and self._image_options.api_key:
            try:
                describer = AIImageDescriber(
                    provider=self._image_options.ai_provider,
                    api_key=self._image_options.api_key
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
        output_dir: Optional[str] = None
    ) -> ConversionResult:
        """
        Convert a single file to Markdown.

        Args:
            source_path: Path to the source file
            output_dir: Optional output directory. If None, outputs to same directory as source.

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

        output_path = output_base / f"{source.stem}.md"

        try:
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Convert using markitdown
            result = self._md.convert(str(source))
            markdown_content = result.text_content

            # Process images if enabled
            images_extracted = 0
            images_described = 0

            if self._image_options.extract_images:
                try:
                    images_md, images_extracted, images_described = self._process_images(
                        str(source),
                        output_base,
                        source.stem
                    )
                    if images_md:
                        markdown_content += images_md
                except Exception as e:
                    logger.warning(f"Image processing failed: {e}")

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

            result = self.convert_file(file_path, output_dir)
            results.append(result)

            if progress_callback:
                progress_callback(i + 1, total, result)

        return results
