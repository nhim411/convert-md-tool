"""
Markdown Converter - Main Application
Cross-platform desktop application for converting files to Markdown.
"""

import os
import sys
import threading

# Add app directory to path for imports BEFORE importing local modules
app_dir = os.path.dirname(os.path.abspath(__file__))
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

import customtkinter as ctk
from typing import Optional, List

from locales import LABELS
from converter import MarkdownConverter, ConversionResult, ImageOptions as ImageOptionsData
from config_manager import ConfigManager, AppConfig
from components import (
    FileSelector,
    FolderOptions,
    OutputOptions,
    FormatFilter,
    ProgressPanel,
    ImageOptions,
    FilePreview,
    CollapsibleFrame,
)


class MarkdownConverterApp(ctk.CTk):
    """Main application window."""

    def __init__(self):
        super().__init__()

        # Initialize config manager and load settings
        self._config_manager = ConfigManager()
        self._config = self._config_manager.load()

        # Configure window
        self.title(LABELS['app_title'])
        self.geometry("750x900")
        self.minsize(650, 800)

        # Set appearance from config
        ctk.set_appearance_mode(self._config.theme)
        ctk.set_default_color_theme("blue")

        # Initialize converter
        self._converter = MarkdownConverter()
        self._is_converting = False
        self._conversion_thread: Optional[threading.Thread] = None

        # Files for file mode
        self._selected_files: List[str] = []

        # Create UI
        self._create_widgets()
        self._bind_events()
        self._load_config_to_ui()

    def _create_widgets(self):
        """Create and layout all widgets."""
        # Main container with padding
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # Header
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))

        title_label = ctk.CTkLabel(
            header_frame,
            text=f"🔄 {LABELS['app_title']}",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(side="left")

        # Theme toggle
        theme_icon = "☀️" if self._config.theme == "dark" else "🌙"
        self._theme_btn = ctk.CTkButton(
            header_frame,
            text=theme_icon,
            width=40,
            height=40,
            command=self._toggle_theme,
            fg_color="transparent",
            border_width=1
        )
        self._theme_btn.pack(side="right")

        # Scrollable content frame
        content_frame = ctk.CTkScrollableFrame(main_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True)

        # File Selector
        self._file_selector = FileSelector(
            content_frame,
            on_selection_change=self._on_source_change
        )
        self._file_selector.pack(fill="x", pady=(0, 5))

        # Format Filter (expanded, with note about processed formats)
        self._format_collapse = CollapsibleFrame(
            content_frame,
            title="Định dạng tệp",
            icon="📑",
            expanded=True
        )
        self._format_collapse.pack(fill="x", pady=(0, 5))

        # Note about formats
        format_note = ctk.CTkLabel(
            self._format_collapse.content,
            text="ℹ️ Chọn các định dạng tệp sẽ được chuyển đổi sang Markdown",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        format_note.pack(anchor="w", padx=10, pady=(5, 0))

        self._format_filter = FormatFilter(self._format_collapse.content)
        self._format_filter.pack(fill="x")

        # File Preview (for file mode) - shown after format filter
        self._file_preview = FilePreview(
            content_frame,
            on_change=self._on_file_preview_change
        )
        # Hidden by default, shown when files selected

        # Folder Options (hidden by default, shown in folder mode)
        self._folder_options = FolderOptions(content_frame)
        # Will be shown only in folder mode

        # Output Options with note
        self._output_options = OutputOptions(content_frame)
        self._output_options.pack(fill="x", pady=(0, 5))

        # Image Options (collapsed by default)
        self._image_collapse = CollapsibleFrame(
            content_frame,
            title="Tùy chọn hình ảnh",
            icon="🖼️",
            expanded=False
        )
        self._image_collapse.pack(fill="x", pady=(0, 5))
        self._image_options = ImageOptions(self._image_collapse.content)
        self._image_options.pack(fill="x")

        # Convert Button
        self._convert_btn = ctk.CTkButton(
            content_frame,
            text=f"🚀 {LABELS['start_convert']}",
            command=self._start_conversion,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self._convert_btn.pack(fill="x", pady=(5, 5))

        # Progress Panel in collapsible frame
        self._progress_collapse = CollapsibleFrame(
            content_frame,
            title="Kết quả",
            icon="📊",
            expanded=True
        )
        self._progress_collapse.pack(fill="both", expand=True, pady=(0, 5))
        self._progress_panel = ProgressPanel(self._progress_collapse.content)
        self._progress_panel.pack(fill="both", expand=True)

    def _bind_events(self):
        """Bind event handlers."""
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _load_config_to_ui(self):
        """Load saved config to UI components."""
        # Folder options
        if self._config.include_subfolders:
            self._folder_options._recursive_var.set(True)

        # Image options
        self._image_options.load_config({
            "extract_images": self._config.extract_images,
            "describe_images": self._config.describe_images,
            "ai_provider": self._config.ai_provider,
            "openai_api_key": self._config.openai_api_key,
            "gemini_api_key": self._config.gemini_api_key,
            "ai_model": self._config.openai_model if self._config.ai_provider == "openai" else self._config.gemini_model,
        })

    def _save_config(self):
        """Save current UI state to config."""
        # Theme
        self._config.theme = ctk.get_appearance_mode().lower()

        # Folder options
        self._config.include_subfolders = self._folder_options.is_recursive

        # Image options
        img_config = self._image_options.get_config()
        self._config.extract_images = img_config.get("extract_images", False)
        self._config.describe_images = img_config.get("describe_images", False)
        self._config.ai_provider = img_config.get("ai_provider", "openai")
        self._config.openai_api_key = img_config.get("openai_api_key", "")
        self._config.gemini_api_key = img_config.get("gemini_api_key", "")

        if self._config.ai_provider == "openai":
            self._config.openai_model = img_config.get("ai_model", "gpt-4o-mini")
        else:
            self._config.gemini_model = img_config.get("ai_model", "gemini-1.5-flash")

        self._config_manager.save(self._config)

    def _on_source_change(self, path: str, mode: str):
        """Handle source selection change."""
        # Enable/disable folder options based on mode
        self._folder_options.set_enabled(mode == "folder")

        # Handle file preview for file mode
        if mode == "file" and path:
            if os.path.isfile(path):
                # Single file - show preview
                self._selected_files = [path]
                self._file_preview.set_files(self._selected_files)
                self._file_preview.pack(fill="x", pady=(0, 5), after=self._file_selector)
        else:
            # Folder mode or no selection - hide preview
            self._file_preview.pack_forget()
            self._selected_files = []

    def _on_file_preview_change(self):
        """Handle file preview selection change."""
        self._selected_files = self._file_preview.get_selected_files()

    def _toggle_theme(self):
        """Toggle between light and dark theme."""
        current = ctk.get_appearance_mode()
        if current == "Dark":
            ctk.set_appearance_mode("light")
            self._theme_btn.configure(text="🌙")
        else:
            ctk.set_appearance_mode("dark")
            self._theme_btn.configure(text="☀️")

    def _validate_inputs(self) -> bool:
        """Validate user inputs before conversion."""
        # Check source path
        if not self._file_selector.selected_path:
            self._show_error(LABELS['error_no_source'])
            return False

        # Check path exists
        if not os.path.exists(self._file_selector.selected_path):
            self._show_error(LABELS['error_invalid_path'])
            return False

        # Check file preview selection
        if self._file_selector.is_folder_mode():
            if not self._format_filter.has_selection():
                self._show_error(LABELS['error_no_formats'])
                return False
        else:
            if self._file_preview.has_files() and not self._file_preview.has_selected():
                self._show_error("Vui lòng chọn ít nhất một tệp để chuyển đổi")
                return False

        return True

    def _show_error(self, message: str):
        """Show error in progress panel."""
        self._progress_panel.log_message(message, "error")

    def _start_conversion(self):
        """Start the conversion process."""
        if self._is_converting:
            # Stop conversion
            self._converter.request_stop()
            self._convert_btn.configure(
                text=f"🚀 {LABELS['start_convert']}",
                state="disabled"
            )
            return

        if not self._validate_inputs():
            return

        # Update UI state
        self._is_converting = True
        self._convert_btn.configure(text=f"⏹ {LABELS['stop_convert']}")
        self._progress_panel.reset()
        self._progress_panel.set_status(LABELS['processing'])

        # Apply image options to converter
        image_opts = ImageOptionsData(
            extract_images=self._image_options.extract_images,
            describe_images=self._image_options.describe_images,
            ai_provider=self._image_options.ai_provider,
            api_key=self._image_options.api_key
        )
        self._converter.set_image_options(image_opts)

        # Start conversion in background thread
        self._conversion_thread = threading.Thread(
            target=self._run_conversion,
            daemon=True
        )
        self._conversion_thread.start()

    def _run_conversion(self):
        """Run conversion in background thread."""
        try:
            source_path = self._file_selector.selected_path
            output_dir = self._output_options.output_path

            if self._file_selector.is_folder_mode():
                # Folder conversion
                selected_formats = self._format_filter.get_selected_formats()
                recursive = self._folder_options.is_recursive
                max_depth = self._folder_options.max_depth

                results = self._converter.convert_folder(
                    folder_path=source_path,
                    recursive=recursive,
                    max_depth=max_depth,
                    allowed_formats=selected_formats,
                    output_dir=output_dir,
                    progress_callback=self._on_progress
                )

                if not results:
                    self.after(0, lambda: self._progress_panel.log_message(
                        LABELS['error_empty_folder'], "info"
                    ))

                # Show completion
                success_count = sum(1 for r in results if r.success)
                self.after(0, lambda: self._progress_panel.show_done(
                    success_count, len(results)
                ))
            else:
                # File mode - convert selected files
                files_to_convert = self._file_preview.get_selected_files() if self._file_preview.has_files() else [source_path]
                total = len(files_to_convert)

                self.after(0, lambda: self._progress_panel.set_progress(0, total))

                success_count = 0
                for i, file_path in enumerate(files_to_convert):
                    if self._converter._stop_requested:
                        break

                    result = self._converter.convert_file(file_path, output_dir)
                    if result.success:
                        success_count += 1

                    self.after(0, lambda r=result, c=i+1, t=total: self._on_progress(c, t, r))

                self.after(0, lambda: self._progress_panel.show_done(success_count, total))

        except Exception as e:
            self.after(0, lambda: self._progress_panel.log_message(
                str(e), "error"
            ))

        finally:
            # Reset UI state
            self.after(0, self._conversion_complete)

    def _on_progress(self, current: int, total: int, result: ConversionResult):
        """Callback for progress updates from converter."""
        def update():
            self._progress_panel.set_progress(current, total)
            self._progress_panel.set_status(
                LABELS['converting'].format(current=current, total=total)
            )
            self._progress_panel.log_conversion_result(
                source=result.source_path,
                output=result.output_path,
                success=result.success,
                error=result.error_message,
                images_extracted=result.images_extracted,
                images_described=result.images_described
            )

        self.after(0, update)

    def _conversion_complete(self):
        """Reset UI after conversion completes."""
        self._is_converting = False
        self._convert_btn.configure(
            text=f"🚀 {LABELS['start_convert']}",
            state="normal"
        )
        self._converter.reset_stop()

    def _on_close(self):
        """Handle window close."""
        # Save config before closing
        self._save_config()

        if self._is_converting:
            self._converter.request_stop()
        self.destroy()


def main():
    """Application entry point."""
    app = MarkdownConverterApp()
    app.mainloop()


if __name__ == "__main__":
    main()
