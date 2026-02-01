"""
Progress Panel Component (Enhanced)
Displays conversion progress with status log and action buttons.
"""

import os
import platform
import subprocess
import customtkinter as ctk
from typing import Optional, Dict, List
from datetime import datetime

from locales import LABELS


class ProgressPanel(ctk.CTkFrame):
    """
    Component for displaying conversion progress.
    Includes progress bar, status label, scrollable log with action buttons.
    """

    def __init__(self, master, **kwargs):
        """
        Initialize ProgressPanel.

        Args:
            master: Parent widget
        """
        super().__init__(master, **kwargs)

        # Store output paths for quick access
        self._output_files: Dict[str, str] = {}  # source -> output

        self._create_widgets()
        self.reset()

    def _create_widgets(self):
        """Create and layout widgets."""
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=(10, 5))

        header = ctk.CTkLabel(
            header_frame,
            text=f"📊 {LABELS['progress']}",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        header.pack(side="left")

        # Clear log button
        self._clear_btn = ctk.CTkButton(
            header_frame,
            text=f"🗑️ {LABELS['clear_log']}",
            command=self.clear_log,
            width=100,
            height=28,
            fg_color="transparent",
            border_width=1,
            text_color=("gray10", "gray90")
        )
        self._clear_btn.pack(side="right")

        # Progress bar frame
        progress_frame = ctk.CTkFrame(self, fg_color="transparent")
        progress_frame.pack(fill="x", padx=10, pady=5)

        # Progress bar
        self._progress_bar = ctk.CTkProgressBar(progress_frame, height=20)
        self._progress_bar.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self._progress_bar.set(0)

        # Progress label
        self._progress_label = ctk.CTkLabel(
            progress_frame,
            text="0%",
            width=80
        )
        self._progress_label.pack(side="right")

        # Status label
        self._status_label = ctk.CTkLabel(
            self,
            text=LABELS['ready'],
            font=ctk.CTkFont(size=12)
        )
        self._status_label.pack(anchor="w", padx=10, pady=5)

        # Results frame with scrollable list
        self._results_frame = ctk.CTkScrollableFrame(
            self,
            height=150,
            fg_color=("gray95", "gray17")
        )
        self._results_frame.pack(fill="both", expand=True, padx=10, pady=(5, 10))

    def reset(self):
        """Reset progress to initial state."""
        self._progress_bar.set(0)
        self._progress_label.configure(text="0%")
        self._status_label.configure(text=LABELS['ready'])
        self._output_files.clear()

    def set_progress(self, current: int, total: int):
        """Update progress bar and label."""
        if total > 0:
            progress = current / total
            self._progress_bar.set(progress)
            percentage = int(progress * 100)
            self._progress_label.configure(text=f"{percentage}% ({current}/{total})")

    def set_status(self, status: str):
        """Update status label."""
        self._status_label.configure(text=status)

    def log_conversion_result(
        self,
        source: str,
        output: Optional[str],
        success: bool,
        error: Optional[str] = None,
        skipped: bool = False,
        images_extracted: int = 0,
        images_described: int = 0
    ):
        """
        Log a conversion result with action buttons.

        Args:
            source: Source file path
            output: Output file path (if successful)
            success: Whether conversion succeeded
            error: Error message if failed
            skipped: Whether the file was skipped (already exists)
            images_extracted: Number of images extracted
            images_described: Number of images described by AI
        """
        # Create result row
        row = ctk.CTkFrame(self._results_frame, fg_color="transparent")
        row.pack(fill="x", pady=2)

        source_name = os.path.basename(source)
        timestamp = datetime.now().strftime("%H:%M:%S")

        if skipped and output:
            # Skipped file - yellow/orange styling
            output_name = os.path.basename(output)

            # Status icon - skip symbol
            icon_label = ctk.CTkLabel(row, text="⏭️", width=20)
            icon_label.pack(side="left")

            # Time
            time_label = ctk.CTkLabel(
                row, text=f"[{timestamp}]",
                font=ctk.CTkFont(size=10),
                text_color="gray",
                width=70
            )
            time_label.pack(side="left")

            # Filename with skip message
            text = f"{source_name} → {LABELS.get('file_skipped', 'Bỏ qua (đã tồn tại)')}"
            name_label = ctk.CTkLabel(
                row,
                text=text,
                font=ctk.CTkFont(size=11),
                text_color="orange",
                anchor="w"
            )
            name_label.pack(side="left", fill="x", expand=True)

            # Open existing file button
            file_btn = ctk.CTkButton(
                row,
                text="📄",
                width=28,
                height=24,
                command=lambda p=output: self._open_file(p),
                fg_color="transparent",
                border_width=1,
                text_color=("gray10", "gray90")
            )
            file_btn.pack(side="right", padx=2)

        elif success and output:
            output_name = os.path.basename(output)
            self._output_files[source] = output

            # Status icon
            icon_label = ctk.CTkLabel(row, text="✓", text_color="green", width=20)
            icon_label.pack(side="left")

            # Time
            time_label = ctk.CTkLabel(
                row, text=f"[{timestamp}]",
                font=ctk.CTkFont(size=10),
                text_color="gray",
                width=70
            )
            time_label.pack(side="left")

            # Filename
            text = f"{source_name} → {output_name}"
            if images_extracted > 0:
                text += f" (+{images_extracted} ảnh"
                if images_described > 0:
                    text += f", {images_described} mô tả"
                text += ")"

            name_label = ctk.CTkLabel(
                row,
                text=text,
                font=ctk.CTkFont(size=11),
                anchor="w"
            )
            name_label.pack(side="left", fill="x", expand=True)

            # Open folder button
            folder_btn = ctk.CTkButton(
                row,
                text="📂",
                width=28,
                height=24,
                command=lambda p=output: self._open_folder(p),
                fg_color="transparent",
                border_width=1,
                text_color=("gray10", "gray90")
            )
            folder_btn.pack(side="right", padx=2)

            # Open file button
            file_btn = ctk.CTkButton(
                row,
                text="📄",
                width=28,
                height=24,
                command=lambda p=output: self._open_file(p),
                fg_color="transparent",
                border_width=1,
                text_color=("gray10", "gray90")
            )
            file_btn.pack(side="right", padx=2)

        else:
            # Error icon
            icon_label = ctk.CTkLabel(row, text="✗", text_color="red", width=20)
            icon_label.pack(side="left")

            # Time
            time_label = ctk.CTkLabel(
                row, text=f"[{timestamp}]",
                font=ctk.CTkFont(size=10),
                text_color="gray",
                width=70
            )
            time_label.pack(side="left")

            # Error message
            error_msg = error or LABELS['error_conversion']
            name_label = ctk.CTkLabel(
                row,
                text=f"{source_name} - {error_msg}",
                font=ctk.CTkFont(size=11),
                text_color="red",
                anchor="w"
            )
            name_label.pack(side="left", fill="x", expand=True)

    def _open_file(self, filepath: str):
        """Open file with default application."""
        try:
            if platform.system() == "Darwin":  # macOS
                subprocess.run(["open", filepath], check=True)
            elif platform.system() == "Windows":
                os.startfile(filepath)
            else:  # Linux
                subprocess.run(["xdg-open", filepath], check=True)
        except Exception as e:
            self.log_message(f"Không thể mở file: {e}", "error")

    def _open_folder(self, filepath: str):
        """Open folder containing the file."""
        folder = os.path.dirname(filepath)
        try:
            if platform.system() == "Darwin":  # macOS
                subprocess.run(["open", "-R", filepath], check=True)
            elif platform.system() == "Windows":
                subprocess.run(["explorer", "/select,", filepath], check=True)
            else:  # Linux
                subprocess.run(["xdg-open", folder], check=True)
        except Exception as e:
            self.log_message(f"Không thể mở thư mục: {e}", "error")

    def log_message(self, message: str, status: str = "info"):
        """Add a simple message to the log."""
        row = ctk.CTkFrame(self._results_frame, fg_color="transparent")
        row.pack(fill="x", pady=2)

        icons = {
            'success': ('✓', 'green'),
            'error': ('✗', 'red'),
            'info': ('ℹ', 'gray'),
            'processing': ('⏳', 'orange'),
        }

        icon, color = icons.get(status, ('•', 'gray'))
        timestamp = datetime.now().strftime("%H:%M:%S")

        icon_label = ctk.CTkLabel(row, text=icon, text_color=color, width=20)
        icon_label.pack(side="left")

        time_label = ctk.CTkLabel(
            row, text=f"[{timestamp}]",
            font=ctk.CTkFont(size=10),
            text_color="gray",
            width=70
        )
        time_label.pack(side="left")

        msg_label = ctk.CTkLabel(
            row,
            text=message,
            font=ctk.CTkFont(size=11),
            text_color=color if status == 'error' else None,
            anchor="w"
        )
        msg_label.pack(side="left", fill="x", expand=True)

    def clear_log(self):
        """Clear the results list."""
        for widget in self._results_frame.winfo_children():
            widget.destroy()
        self._output_files.clear()

    def show_done(self, success_count: int, total_count: int):
        """Show completion message."""
        message = LABELS['done'].format(success=success_count, total=total_count)
        self.set_status(message)

    def get_output_files(self) -> List[str]:
        """Get list of successfully converted output files."""
        return list(self._output_files.values())
