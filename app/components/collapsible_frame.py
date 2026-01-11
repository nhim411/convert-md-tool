"""
Collapsible Frame Component
A frame that can be expanded/collapsed with a header button.
"""

import customtkinter as ctk
from typing import Optional


class CollapsibleFrame(ctk.CTkFrame):
    """
    A frame with a clickable header that expands/collapses the content.
    """

    def __init__(
        self,
        master,
        title: str,
        icon: str = "📁",
        expanded: bool = True,
        **kwargs
    ):
        """
        Initialize CollapsibleFrame.

        Args:
            master: Parent widget
            title: Header title
            icon: Icon to display before title
            expanded: Initial expanded state
        """
        super().__init__(master, **kwargs)

        self._title = title
        self._icon = icon
        self._expanded = expanded

        self._create_widgets()

        # Set initial state
        if not expanded:
            self._content_frame.pack_forget()

    def _create_widgets(self):
        """Create header and content area."""
        # Header button
        self._header = ctk.CTkButton(
            self,
            text=self._get_header_text(),
            command=self.toggle,
            anchor="w",
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray80", "gray30"),
            height=32,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self._header.pack(fill="x", padx=5, pady=(5, 0))

        # Content frame
        self._content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._content_frame.pack(fill="both", expand=True, padx=5, pady=5)

    def _get_header_text(self) -> str:
        """Get header text with expand/collapse indicator."""
        arrow = "▼" if self._expanded else "▶"
        return f"{arrow} {self._icon} {self._title}"

    def toggle(self):
        """Toggle expanded/collapsed state."""
        self._expanded = not self._expanded
        self._header.configure(text=self._get_header_text())

        if self._expanded:
            self._content_frame.pack(fill="both", expand=True, padx=5, pady=5)
        else:
            self._content_frame.pack_forget()

    def expand(self):
        """Expand the content."""
        if not self._expanded:
            self.toggle()

    def collapse(self):
        """Collapse the content."""
        if self._expanded:
            self.toggle()

    @property
    def content(self) -> ctk.CTkFrame:
        """Get the content frame to add widgets to."""
        return self._content_frame

    @property
    def is_expanded(self) -> bool:
        """Check if currently expanded."""
        return self._expanded

    def set_title(self, title: str):
        """Update the title."""
        self._title = title
        self._header.configure(text=self._get_header_text())
