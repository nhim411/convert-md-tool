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
        # Main layout frame (transparent)
        # 1. Mode Selection (Top)
        mode_frame = ctk.CTkFrame(self, fg_color="transparent")
        mode_frame.pack(fill="x", padx=0, pady=(0, 10))

        self._mode_var = ctk.StringVar(value="folder")

        # Custom styled radio buttons (segmented control style)
        self._folder_radio = ctk.CTkRadioButton(
            mode_frame,
            text=LABELS['folder_mode'],
            variable=self._mode_var,
            value="folder",
            command=self._on_mode_change,
            # font=ctk.CTkFont(size=13, weight="bold")
        )
        self._folder_radio.pack(side="left", padx=(0, 20))

        self._file_radio = ctk.CTkRadioButton(
            mode_frame,
            text=LABELS['file_mode'],
            variable=self._mode_var,
            value="file",
            command=self._on_mode_change,
            # font=ctk.CTkFont(size=13, weight="bold")
        )
        self._file_radio.pack(side="left")

        # 2. Hero Input Area (Big Browse Button + Entry)
        input_frame = ctk.CTkFrame(self, fg_color="transparent")
        input_frame.pack(fill="x")

        # Path Input (Center) - Taller and bigger font
        self._path_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text=LABELS['placeholder_select'],
            state="readonly",
            height=50,
            font=ctk.CTkFont(size=14)
        )
        self._path_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # Browse Button (Right) - Large
        self._browse_btn = ctk.CTkButton(
            input_frame,
            text=f"📂 {LABELS['browse']}",
            command=self._browse_action,
            width=120,
            height=50,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("green", "#2fa572"), # Different color to convert button
            hover_color=("darkgreen", "#106a43")
        )
        self._browse_btn.pack(side="right")

    def _browse_action(self):
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
