"""
Output Options Component
Configuration for output location.
"""

import customtkinter as ctk
from tkinter import filedialog
from typing import Callable, Optional

from locales import LABELS


class OutputOptions(ctk.CTkFrame):
    """
    Component for output configuration.
    Allows selecting a custom output directory.
    """

    def __init__(
        self,
        master,
        on_change: Optional[Callable[[], None]] = None,
        **kwargs
    ):
        """
        Initialize OutputOptions.

        Args:
            master: Parent widget
            on_change: Callback when options change
        """
        super().__init__(master, **kwargs)

        self._on_change = on_change
        self._output_path = ""
        self._create_widgets()

    def _create_widgets(self):
        """Create and layout widgets."""
        # Header
        header = ctk.CTkLabel(
            self,
            text=f"📤 {LABELS['output_settings']}",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        header.pack(anchor="w", padx=10, pady=(10, 5))

        # Note about default location
        note = ctk.CTkLabel(
            self,
            text="ℹ️ Mặc định file .md sẽ được lưu cùng vị trí với file gốc",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        note.pack(anchor="w", padx=10, pady=(0, 5))

        # Custom output checkbox
        self._custom_output_var = ctk.BooleanVar(value=False)
        self._custom_cb = ctk.CTkCheckBox(
            self,
            text=LABELS['export_different'],
            variable=self._custom_output_var,
            command=self._on_custom_toggle
        )
        self._custom_cb.pack(anchor="w", padx=10, pady=5)

        # Path selection frame
        path_frame = ctk.CTkFrame(self, fg_color="transparent")
        path_frame.pack(fill="x", padx=10, pady=(5, 10))

        # Path entry
        self._path_entry = ctk.CTkEntry(
            path_frame,
            placeholder_text=LABELS['output_placeholder'],
            state="disabled",
            height=36
        )
        self._path_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # Browse button
        self._browse_btn = ctk.CTkButton(
            path_frame,
            text=f"📂 {LABELS['browse']}",
            command=self._browse,
            width=100,
            height=36,
            state="disabled"
        )
        self._browse_btn.pack(side="right")

    def _on_custom_toggle(self):
        """Handle custom output checkbox toggle."""
        is_custom = self._custom_output_var.get()
        state = "normal" if is_custom else "disabled"

        self._path_entry.configure(state=state)
        self._browse_btn.configure(state=state)

        if not is_custom:
            self._output_path = ""
            self._path_entry.configure(state="normal")
            self._path_entry.delete(0, "end")
            self._path_entry.configure(state="disabled")

        self._notify_change()

    def _browse(self):
        """Open folder selection dialog."""
        path = filedialog.askdirectory(
            title=LABELS['output_settings']
        )

        if path:
            self._output_path = path
            self._path_entry.configure(state="normal")
            self._path_entry.delete(0, "end")
            self._path_entry.insert(0, path)
            # Keep state as normal since custom is enabled
            self._notify_change()

    def _notify_change(self):
        """Notify callback of change."""
        if self._on_change:
            self._on_change()

    @property
    def use_custom_output(self) -> bool:
        """Check if custom output is enabled."""
        return self._custom_output_var.get()

    @property
    def output_path(self) -> Optional[str]:
        """
        Get output path.
        Returns None if using source location.
        """
        if self._custom_output_var.get() and self._output_path:
            return self._output_path
        return None
