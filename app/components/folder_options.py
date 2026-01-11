"""
Folder Options Component
Options for recursive folder processing.
"""

import customtkinter as ctk
from typing import Callable, Optional

from locales import LABELS


class FolderOptions(ctk.CTkFrame):
    """
    Component for folder conversion options.
    Includes recursive checkbox and depth selection.
    """

    def __init__(
        self,
        master,
        on_change: Optional[Callable[[], None]] = None,
        **kwargs
    ):
        """
        Initialize FolderOptions.

        Args:
            master: Parent widget
            on_change: Callback when options change
        """
        super().__init__(master, **kwargs)

        self._on_change = on_change
        self._create_widgets()

    def _create_widgets(self):
        """Create and layout widgets."""
        # Header
        header = ctk.CTkLabel(
            self,
            text=f"⚙️ {LABELS['folder_options']}",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        header.pack(anchor="w", padx=10, pady=(10, 5))

        # Options frame
        options_frame = ctk.CTkFrame(self, fg_color="transparent")
        options_frame.pack(fill="x", padx=10, pady=(5, 10))

        # Recursive checkbox
        self._recursive_var = ctk.BooleanVar(value=False)
        self._recursive_cb = ctk.CTkCheckBox(
            options_frame,
            text=LABELS['include_subfolders'],
            variable=self._recursive_var,
            command=self._on_recursive_change
        )
        self._recursive_cb.pack(side="left", padx=(0, 20))

        # Depth label
        self._depth_label = ctk.CTkLabel(
            options_frame,
            text=f"{LABELS['depth']}:"
        )
        self._depth_label.pack(side="left", padx=(0, 5))

        # Depth dropdown
        self._depth_var = ctk.StringVar(value=LABELS['depth_all'])
        self._depth_menu = ctk.CTkOptionMenu(
            options_frame,
            values=[LABELS['depth_one'], LABELS['depth_all']],
            variable=self._depth_var,
            command=self._on_depth_change,
            width=120,
            state="disabled"
        )
        self._depth_menu.pack(side="left")

    def _on_recursive_change(self):
        """Handle recursive checkbox change."""
        is_recursive = self._recursive_var.get()
        # Enable/disable depth dropdown based on recursive state
        self._depth_menu.configure(state="normal" if is_recursive else "disabled")
        self._notify_change()

    def _on_depth_change(self, _):
        """Handle depth selection change."""
        self._notify_change()

    def _notify_change(self):
        """Notify callback of change."""
        if self._on_change:
            self._on_change()

    @property
    def is_recursive(self) -> bool:
        """Get whether recursive mode is enabled."""
        return self._recursive_var.get()

    @property
    def max_depth(self) -> Optional[int]:
        """
        Get maximum depth for recursive processing.
        Returns None for unlimited, 1 for single level.
        """
        if not self._recursive_var.get():
            return None

        if self._depth_var.get() == LABELS['depth_one']:
            return 1
        return None  # All levels

    def set_enabled(self, enabled: bool):
        """Enable or disable the component."""
        state = "normal" if enabled else "disabled"
        self._recursive_cb.configure(state=state)
        if enabled and self._recursive_var.get():
            self._depth_menu.configure(state="normal")
        else:
            self._depth_menu.configure(state="disabled")
