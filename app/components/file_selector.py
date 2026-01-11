"""
File Selector Component
Allows user to select a file or folder for conversion.
"""

import customtkinter as ctk
from tkinter import filedialog
from typing import Callable, Optional

from locales import LABELS


class FileSelector(ctk.CTkFrame):
    """
    Component for selecting source file or folder.
    Includes radio buttons for mode selection and browse button.
    """

    def __init__(
        self,
        master,
        on_selection_change: Optional[Callable[[str, str], None]] = None,
        **kwargs
    ):
        """
        Initialize FileSelector.

        Args:
            master: Parent widget
            on_selection_change: Callback(path, mode) when selection changes
        """
        super().__init__(master, **kwargs)

        self._on_selection_change = on_selection_change
        self._selected_path = ""
        self._mode = "folder"  # "file" or "folder"

        self._create_widgets()

    def _create_widgets(self):
        """Create and layout widgets."""
        # Header
        header = ctk.CTkLabel(
            self,
            text=f"📁 {LABELS['select_source']}",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        header.pack(anchor="w", padx=10, pady=(10, 5))

        # Path display frame
        path_frame = ctk.CTkFrame(self, fg_color="transparent")
        path_frame.pack(fill="x", padx=10, pady=5)

        # Path entry
        self._path_entry = ctk.CTkEntry(
            path_frame,
            placeholder_text=LABELS['no_selection'],
            state="readonly",
            height=36
        )
        self._path_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # Browse button
        self._browse_btn = ctk.CTkButton(
            path_frame,
            text=f"📂 {LABELS['browse']}",
            command=self._browse,
            width=100,
            height=36
        )
        self._browse_btn.pack(side="right")

        # Mode selection frame
        mode_frame = ctk.CTkFrame(self, fg_color="transparent")
        mode_frame.pack(anchor="w", padx=10, pady=(5, 10))

        self._mode_var = ctk.StringVar(value="folder")

        self._file_radio = ctk.CTkRadioButton(
            mode_frame,
            text=LABELS['file_mode'],
            variable=self._mode_var,
            value="file",
            command=self._on_mode_change
        )
        self._file_radio.pack(side="left", padx=(0, 20))

        self._folder_radio = ctk.CTkRadioButton(
            mode_frame,
            text=LABELS['folder_mode'],
            variable=self._mode_var,
            value="folder",
            command=self._on_mode_change
        )
        self._folder_radio.pack(side="left")

    def _browse(self):
        """Open file/folder dialog."""
        if self._mode_var.get() == "file":
            path = filedialog.askopenfilename(
                title=LABELS['select_source'],
                filetypes=[
                    ("Tất cả tệp hỗ trợ", "*.pdf *.docx *.doc *.pptx *.ppt *.xlsx *.xls *.jpg *.jpeg *.png *.gif *.bmp *.webp *.mp3 *.wav *.m4a *.html *.htm *.csv *.json *.xml *.txt *.zip *.epub"),
                    ("PDF", "*.pdf"),
                    ("Word", "*.docx *.doc"),
                    ("PowerPoint", "*.pptx *.ppt"),
                    ("Excel", "*.xlsx *.xls"),
                    ("Hình ảnh", "*.jpg *.jpeg *.png *.gif *.bmp *.webp"),
                    ("Tất cả", "*.*"),
                ]
            )
        else:
            path = filedialog.askdirectory(
                title=LABELS['select_source']
            )

        if path:
            self._selected_path = path
            self._update_path_display()
            self._notify_change()

    def _update_path_display(self):
        """Update the path entry display."""
        self._path_entry.configure(state="normal")
        self._path_entry.delete(0, "end")
        if self._selected_path:
            self._path_entry.insert(0, self._selected_path)
        self._path_entry.configure(state="readonly")

    def _on_mode_change(self):
        """Handle mode change between file and folder."""
        new_mode = self._mode_var.get()
        if new_mode != self._mode:
            self._mode = new_mode
            # Clear selection when mode changes
            self._selected_path = ""
            self._update_path_display()
            self._notify_change()

    def _notify_change(self):
        """Notify callback of selection change."""
        if self._on_selection_change:
            self._on_selection_change(self._selected_path, self._mode)

    @property
    def selected_path(self) -> str:
        """Get currently selected path."""
        return self._selected_path

    @property
    def mode(self) -> str:
        """Get current mode ('file' or 'folder')."""
        return self._mode_var.get()

    def is_folder_mode(self) -> bool:
        """Check if folder mode is selected."""
        return self._mode_var.get() == "folder"
