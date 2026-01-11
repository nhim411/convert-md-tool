"""
Format Filter Component
Checkboxes for selecting file formats to convert.
"""

import customtkinter as ctk
from typing import Callable, List, Optional, Dict

from locales import LABELS


class FormatFilter(ctk.CTkFrame):
    """
    Component for filtering file formats.
    Displays checkboxes for each supported format with check all/uncheck all buttons.
    """

    # Format definitions with their display names
    # Optimized for minimal build size
    FORMATS = [
        ('PDF', 'format_pdf'),
        ('Word', 'format_word'),
        ('PowerPoint', 'format_powerpoint'),
        ('Excel', 'format_excel'),
        ('Images', 'format_images'),
        ('Text', 'format_text'),
    ]

    def __init__(
        self,
        master,
        on_change: Optional[Callable[[], None]] = None,
        **kwargs
    ):
        """
        Initialize FormatFilter.

        Args:
            master: Parent widget
            on_change: Callback when selection changes
        """
        super().__init__(master, **kwargs)

        self._on_change = on_change
        self._format_vars: Dict[str, ctk.BooleanVar] = {}
        self._create_widgets()

    def _create_widgets(self):
        """Create and layout widgets."""
        # Header frame with title and buttons
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=(10, 5))

        # Header label
        header = ctk.CTkLabel(
            header_frame,
            text=f"📑 {LABELS['file_formats']}",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        header.pack(side="left")

        # Uncheck all button
        self._uncheck_btn = ctk.CTkButton(
            header_frame,
            text=f"✗ {LABELS['uncheck_all']}",
            command=self._uncheck_all,
            width=100,
            height=28,
            fg_color="transparent",
            border_width=1,
            text_color=("gray10", "gray90")
        )
        self._uncheck_btn.pack(side="right", padx=(5, 0))

        # Check all button
        self._check_btn = ctk.CTkButton(
            header_frame,
            text=f"✓ {LABELS['check_all']}",
            command=self._check_all,
            width=110,
            height=28,
            fg_color="transparent",
            border_width=1,
            text_color=("gray10", "gray90")
        )
        self._check_btn.pack(side="right")

        # Checkboxes frame
        checkbox_frame = ctk.CTkFrame(self, fg_color="transparent")
        checkbox_frame.pack(fill="x", padx=10, pady=(5, 10))

        # Create checkboxes in a grid (2 rows x 3 columns)
        # Default: only Word, PowerPoint, Excel checked
        default_checked = {'Word', 'PowerPoint', 'Excel'}

        for i, (format_key, label_key) in enumerate(self.FORMATS):
            row = i // 3
            col = i % 3

            var = ctk.BooleanVar(value=format_key in default_checked)
            self._format_vars[format_key] = var

            cb = ctk.CTkCheckBox(
                checkbox_frame,
                text=LABELS[label_key],
                variable=var,
                command=self._notify_change,
                width=120
            )
            cb.grid(row=row, column=col, padx=5, pady=5, sticky="w")

        # Configure grid columns to be equal
        for col in range(5):
            checkbox_frame.columnconfigure(col, weight=1)

    def _check_all(self):
        """Check all format checkboxes."""
        for var in self._format_vars.values():
            var.set(True)
        self._notify_change()

    def _uncheck_all(self):
        """Uncheck all format checkboxes."""
        for var in self._format_vars.values():
            var.set(False)
        self._notify_change()

    def _notify_change(self):
        """Notify callback of change."""
        if self._on_change:
            self._on_change()

    def get_selected_formats(self) -> List[str]:
        """Get list of selected format keys."""
        return [
            format_key
            for format_key, var in self._format_vars.items()
            if var.get()
        ]

    def has_selection(self) -> bool:
        """Check if at least one format is selected."""
        return any(var.get() for var in self._format_vars.values())
