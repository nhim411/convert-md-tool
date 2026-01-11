"""
File Preview Component
Displays a list of selected files with ability to remove individual files.
"""

import os
import customtkinter as ctk
from tkinter import filedialog
from typing import Callable, List, Optional

from locales import LABELS


class FilePreview(ctk.CTkFrame):
    """
    Component for previewing and managing selected files.
    Shows a scrollable list of files with checkboxes to include/exclude.
    """

    def __init__(
        self,
        master,
        on_change: Optional[Callable[[], None]] = None,
        **kwargs
    ):
        """
        Initialize FilePreview.

        Args:
            master: Parent widget
            on_change: Callback when file selection changes
        """
        super().__init__(master, **kwargs)

        self._on_change = on_change
        self._files: List[str] = []
        self._file_vars: dict = {}  # path -> BooleanVar
        self._file_widgets: dict = {}  # path -> widget frame

        self._create_widgets()

    def _create_widgets(self):
        """Create and layout widgets."""
        # Header with count
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=(10, 5))

        self._header_label = ctk.CTkLabel(
            header_frame,
            text="📋 Danh sách tệp (0)",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self._header_label.pack(side="left")

        # Select/Deselect all buttons
        self._deselect_btn = ctk.CTkButton(
            header_frame,
            text="Bỏ chọn tất cả",
            command=self._deselect_all,
            width=100,
            height=24,
            font=ctk.CTkFont(size=11),
            fg_color="transparent",
            border_width=1,
            text_color=("gray10", "gray90")
        )
        self._deselect_btn.pack(side="right", padx=(5, 0))

        self._select_btn = ctk.CTkButton(
            header_frame,
            text="Chọn tất cả",
            command=self._select_all,
            width=90,
            height=24,
            font=ctk.CTkFont(size=11),
            fg_color="transparent",
            border_width=1,
            text_color=("gray10", "gray90")
        )
        self._select_btn.pack(side="right")

        # Scrollable file list
        self._file_list = ctk.CTkScrollableFrame(
            self,
            height=120,
            fg_color=("gray95", "gray17")
        )
        self._file_list.pack(fill="both", expand=True, padx=10, pady=(5, 10))

        # Placeholder when empty
        self._placeholder = ctk.CTkLabel(
            self._file_list,
            text="Chưa có tệp nào được chọn",
            text_color="gray"
        )
        self._placeholder.pack(pady=20)

    def set_files(self, files: List[str]):
        """
        Set the list of files to display.

        Args:
            files: List of file paths
        """
        # Clear existing
        self._clear_list()

        self._files = files

        if not files:
            self._placeholder.pack(pady=20)
            self._update_header()
            return

        self._placeholder.pack_forget()

        # Create checkbox for each file
        for filepath in files:
            self._add_file_widget(filepath)

        self._update_header()

    def _add_file_widget(self, filepath: str):
        """Add a file widget to the list."""
        var = ctk.BooleanVar(value=True)
        self._file_vars[filepath] = var

        frame = ctk.CTkFrame(self._file_list, fg_color="transparent")
        frame.pack(fill="x", pady=1)

        # Checkbox
        cb = ctk.CTkCheckBox(
            frame,
            text="",
            variable=var,
            command=self._on_file_toggle,
            width=20
        )
        cb.pack(side="left")

        # Filename
        filename = os.path.basename(filepath)
        name_label = ctk.CTkLabel(
            frame,
            text=filename,
            font=ctk.CTkFont(size=11),
            anchor="w"
        )
        name_label.pack(side="left", fill="x", expand=True)

        # File size
        try:
            size = os.path.getsize(filepath)
            size_str = self._format_size(size)
            size_label = ctk.CTkLabel(
                frame,
                text=size_str,
                font=ctk.CTkFont(size=10),
                text_color="gray",
                width=60
            )
            size_label.pack(side="right")
        except:
            pass

        self._file_widgets[filepath] = frame

    def _format_size(self, size: int) -> str:
        """Format file size."""
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        else:
            return f"{size / (1024 * 1024):.1f} MB"

    def _clear_list(self):
        """Clear the file list."""
        for widget in self._file_widgets.values():
            widget.destroy()
        self._file_widgets.clear()
        self._file_vars.clear()
        self._files.clear()

    def _on_file_toggle(self):
        """Handle file checkbox toggle."""
        self._update_header()
        if self._on_change:
            self._on_change()

    def _update_header(self):
        """Update header with selected count."""
        selected = len(self.get_selected_files())
        total = len(self._files)
        self._header_label.configure(text=f"📋 Danh sách tệp ({selected}/{total})")

    def _select_all(self):
        """Select all files."""
        for var in self._file_vars.values():
            var.set(True)
        self._update_header()
        if self._on_change:
            self._on_change()

    def _deselect_all(self):
        """Deselect all files."""
        for var in self._file_vars.values():
            var.set(False)
        self._update_header()
        if self._on_change:
            self._on_change()

    def get_selected_files(self) -> List[str]:
        """Get list of selected files."""
        return [
            path for path, var in self._file_vars.items()
            if var.get()
        ]

    def has_files(self) -> bool:
        """Check if there are any files."""
        return len(self._files) > 0

    def has_selected(self) -> bool:
        """Check if any files are selected."""
        return len(self.get_selected_files()) > 0
