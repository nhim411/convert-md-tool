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
from converter import MarkdownConverter, ConversionResult, AIOptions as ConverterAIOptions
from config_manager import ConfigManager, AppConfig
from components import (
    FileSelector,
    FolderOptions,
    OutputOptions,
    FormatFilter,
    ProgressPanel,
    FormatFilter,
    ProgressPanel,
    AIOptions,
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
        self.geometry("1100x700")
        self.minsize(900, 600)

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
        # Main container
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 1. Header Area (Full Width)
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
            width=32,
            height=32,
            command=self._toggle_theme,
            fg_color="transparent",
            border_width=1,
            hover_color=("gray85", "gray25")
        )
        self._theme_btn.pack(side="right")

        # 2. Content Area (Split Columns)
        content_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True)

        # --- LEFT COLUMN (Inputs & Config) ---
        # 65% width normally, but with pack side=left expand=True it shares space.
        # We can use grid or pack. Pack is easier if we want flexible split.
        left_col = ctk.CTkFrame(content_frame, fg_color="transparent")
        left_col.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Scrollable container for Left Column if height is small
        self._scroll_frame = ctk.CTkScrollableFrame(left_col, fg_color="transparent")
        self._scroll_frame.pack(fill="both", expand=True, pady=(0, 10))

        # Hero Section (File Selector)
        hero_frame = ctk.CTkFrame(self._scroll_frame, fg_color=("gray95", "gray15"), corner_radius=10)
        hero_frame.pack(fill="x", pady=(0, 10), ipady=5)

        self._file_selector = FileSelector(
            hero_frame,
            on_selection_change=self._on_source_change
        )
        self._file_selector.pack(fill="x", padx=10, pady=5)

        # File Preview (Inside Hero)
        self._file_preview = FilePreview(
            hero_frame,
            on_change=self._on_file_preview_change
        )
        # Initially hidden

        # Settings Tabs
        self._tab_view = ctk.CTkTabview(self._scroll_frame, height=350)
        self._tab_view.pack(fill="x", expand=True)

        # Create Tabs
        tab_general = self._tab_view.add(LABELS.get('tab_general', "Cấu hình"))
        tab_formats = self._tab_view.add(LABELS.get('tab_formats', "Định dạng"))
        tab_advanced = self._tab_view.add(LABELS.get('tab_advanced', "Nâng cao & AI"))

        # --- Tab 1: General ---
        self._output_options = OutputOptions(tab_general, fg_color="transparent")
        self._output_options.pack(fill="x", pady=5)

        self._folder_options = FolderOptions(
            tab_general,
            fg_color="transparent",
            on_change=self._on_folder_options_change
        )
        self._folder_options.pack(fill="x", pady=5)

        # --- Tab 2: Formats ---
        format_note = ctk.CTkLabel(
            tab_formats,
            text="ℹ️ Chọn các định dạng tệp sẽ được chuyển đổi sang Markdown",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        format_note.pack(anchor="w", padx=10, pady=(10, 5))

        self._format_filter = FormatFilter(
            tab_formats,
            on_change=self._on_format_change
        )
        self._format_filter.pack(fill="x", padx=5)

        # --- Tab 3: Advanced ---
        self._ai_options = AIOptions(tab_advanced, fg_color="transparent")
        self._ai_options.pack(fill="both", expand=True, padx=5, pady=5)

        # Action Button (Bottom of Left Column)
        self._convert_btn = ctk.CTkButton(
            left_col,
            text=f"🚀 {LABELS['start_convert']}",
            command=self._start_conversion,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=("blue", "#1f538d"),
        )
        self._convert_btn.pack(fill="x", side="bottom", pady=(10, 0))


        # --- RIGHT COLUMN (Progress & Logs) ---
        right_col = ctk.CTkFrame(content_frame, fg_color=("gray90", "gray13"), corner_radius=10)
        right_col.pack(side="right", fill="both", expand=True, ipadx=5, ipady=5)

        # We pass height=0 or something to imply full fill, but ProgressPanel logic needs update
        # to expand its internal scroll frame.
        self._progress_panel = ProgressPanel(right_col)
        self._progress_panel.pack(fill="both", expand=True, padx=5, pady=5)

    def _bind_events(self):
        """Bind event handlers."""
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _load_config_to_ui(self):
        """Load saved config to UI components."""
        # Folder options
        if self._config.include_subfolders:
            self._folder_options._recursive_var.set(True)

        # Output options
        self._output_options.set_overwrite_existing(self._config.overwrite_existing)

        # AI options
        self._ai_options.load_config({
            "extract_images": self._config.extract_images,
            "describe_images": self._config.describe_images,
            "chunk_enabled": self._config.chunk_enabled,
            "excel_clean_enabled": self._config.excel_clean_enabled,
            "summary_enabled": self._config.summary_enabled,
            "ai_provider": self._config.ai_provider,
            "openai_key": self._config.openai_api_key,
            "gemini_key": self._config.gemini_api_key,
            "ai_model": self._config.openai_model if self._config.ai_provider == "openai" else self._config.gemini_model,
        })

    def _save_config(self):
        """Save current UI state to config."""
        # Theme
        self._config.theme = ctk.get_appearance_mode().lower()

        # Folder options
        self._config.include_subfolders = self._folder_options.is_recursive

        # Output options
        self._config.overwrite_existing = self._output_options.overwrite_existing

        # AI options
        ai_config = self._ai_options.get_config()
        self._config.extract_images = ai_config.get("extract_images", False)
        self._config.describe_images = ai_config.get("describe_images", False)
        self._config.chunk_enabled = ai_config.get("chunk_enabled", False)
        self._config.excel_clean_enabled = ai_config.get("excel_clean_enabled", False)
        self._config.summary_enabled = ai_config.get("summary_enabled", False)

        self._config.ai_provider = ai_config.get("ai_provider", "openai")
        self._config.openai_api_key = ai_config.get("openai_key", "")
        self._config.gemini_api_key = ai_config.get("gemini_key", "")

        if self._config.ai_provider == "openai":
            self._config.openai_model = ai_config.get("ai_model", "gpt-4o-mini")
        else:
            self._config.gemini_model = ai_config.get("ai_model", "gemini-1.5-flash")

        self._config_manager.save(self._config)

    def _on_source_change(self, path: str, mode: str):
        """Handle source selection change."""
        # Enable/disable folder options based on mode
        self._folder_options.set_enabled(mode == "folder")

        if path:
            if mode == "file":
                if os.path.isfile(path):
                    # Single file - show preview
                    self._selected_files = [path]
                    self._file_preview.set_files(self._selected_files)
                    self._file_preview.pack(fill="x", padx=15, pady=(0, 10), after=self._file_selector)
            else:
                # Folder mode - scan and show preview
                self.after(100, self._scan_folder)  # Small delay to ensure UI ready
                self._file_preview.pack(fill="x", padx=15, pady=(0, 10), after=self._file_selector)
        else:
            # No selection - hide preview
            self._file_preview.pack_forget()
            self._selected_files = []

    def _on_format_change(self):
        """Handle format selection change."""
        if self._file_selector.is_folder_mode() and self._file_selector.selected_path:
            self._scan_folder()

    def _on_folder_options_change(self):
        """Handle folder options change."""
        if self._file_selector.is_folder_mode() and self._file_selector.selected_path:
            self._scan_folder()

    def _scan_folder(self):
        """Scan folder for files and update preview."""
        path = self._file_selector.selected_path
        if not path or not os.path.isdir(path):
            return

        # Show loading state (optional, can be improved)
        self._progress_panel.set_status("Đang quét thư mục...")

        # Get settings
        selected_formats = self._format_filter.get_selected_formats()
        recursive = self._folder_options.is_recursive
        max_depth = self._folder_options.max_depth

        # Run scan in background to avoid freezing UI
        def scan_task():
            files = self._converter.scan_folder(
                folder_path=path,
                recursive=recursive,
                max_depth=max_depth,
                allowed_extensions=self._converter.get_extensions_for_formats(selected_formats)
            )
            # Update UI on main thread
            self.after(0, lambda: self._update_preview_after_scan(files))

        threading.Thread(target=scan_task, daemon=True).start()

    def _update_preview_after_scan(self, files: List[str]):
        """Update preview with scanned files."""
        self._selected_files = files
        self._file_preview.set_files(files)
        self._progress_panel.set_status(LABELS['ready'])

        if not files:
            self._progress_panel.log_message(LABELS['error_empty_folder'], "info")

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

        # Apply AI options to converter
        ai_cfg = self._ai_options.get_config()
        ai_opts = ConverterAIOptions(
            extract_images=ai_cfg.get("extract_images", False),
            describe_images=ai_cfg.get("describe_images", False),
            chunk_enabled=ai_cfg.get("chunk_enabled", False),
            excel_clean_enabled=ai_cfg.get("excel_clean_enabled", False),
            summary_enabled=ai_cfg.get("summary_enabled", False),
            ai_provider=ai_cfg.get("ai_provider", "openai"),
            api_key=ai_cfg.get("openai_key") if ai_cfg.get("ai_provider")=="openai" else ai_cfg.get("gemini_key"),
            ai_model=ai_cfg.get("ai_model")
        )
        self._converter.set_ai_options(ai_opts)

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
                # Folder conversion - Use files from preview!
                # We already scanned, so we trust the preview list.
                files_to_convert = self._file_preview.get_selected_files()

                # Check directly, if list empty logic below handles it
            else:
                # File mode - convert selected files
                files_to_convert = self._file_preview.get_selected_files() if self._file_preview.has_files() else [source_path]

            if not files_to_convert:
                 self.after(0, lambda: self._progress_panel.log_message(
                    LABELS['error_empty_folder'], "info"
                ))
                 return

            total = len(files_to_convert)
            overwrite = self._output_options.overwrite_existing

            self.after(0, lambda: self._progress_panel.set_progress(0, total))

            success_count = 0
            for i, file_path in enumerate(files_to_convert):
                if self._converter._stop_requested:
                    break

                result = self._converter.convert_file(file_path, output_dir, overwrite=overwrite)
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
                skipped=result.skipped,
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
