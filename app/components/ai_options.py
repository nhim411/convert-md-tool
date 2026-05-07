"""
AI Options Component
Consolidates Image handling, RAG Chunking, and AI Enrichment options.
"""

import customtkinter as ctk
from typing import Callable, Optional
import threading

from locales import LABELS


class AIOptions(ctk.CTkFrame):
    """
    Component for AI and Advanced options.
    Includes:
    - RAG Smart Chunking
    - Image Extraction
    - AI Summarization & Description
    - OpenAI-Compatible API Configuration
    """

    DEFAULT_MODELS = ["gpt-4o", "gpt-4o-mini", "o1-preview", "o1-mini", "gpt-4-turbo"]

    def __init__(
        self,
        master,
        on_change: Optional[Callable[[], None]] = None,
        **kwargs
    ):
        super().__init__(master, **kwargs)
        self._on_change = on_change
        self._api_key = ""
        self._models_cache: list[str] = []
        self._create_widgets()

    def _create_widgets(self):
        # 1. RAG Section
        rag_header = ctk.CTkLabel(
            self, text="📚 RAG & Chunking", font=ctk.CTkFont(size=13, weight="bold")
        )
        rag_header.pack(anchor="w", padx=10, pady=(10, 5))

        self._chunk_var = ctk.BooleanVar(value=False)
        self._chunk_cb = ctk.CTkCheckBox(
            self,
            text="Smart Chunking (Tách nhỏ theo Header)",
            variable=self._chunk_var,
            command=self._notify_change,
        )
        self._chunk_cb.pack(anchor="w", padx=10, pady=2)

        self._excel_clean_var = ctk.BooleanVar(value=False)
        self._excel_clean_cb = ctk.CTkCheckBox(
            self,
            text="Clean Excel Data (Forward Fill)",
            variable=self._excel_clean_var,
            command=self._notify_change,
        )
        self._excel_clean_cb.pack(anchor="w", padx=10, pady=2)

        chunk_note = ctk.CTkLabel(
            self,
            text="   → Xuất ra thêm file .jsonl cho RAG",
            text_color="gray",
            font=ctk.CTkFont(size=10),
        )
        chunk_note.pack(anchor="w", padx=10)

        # 2. Image Section
        img_header = ctk.CTkLabel(
            self, text="🖼️ Hình ảnh", font=ctk.CTkFont(size=13, weight="bold")
        )
        img_header.pack(anchor="w", padx=10, pady=(15, 5))

        self._extract_var = ctk.BooleanVar(value=False)
        self._extract_cb = ctk.CTkCheckBox(
            self,
            text="Trích xuất hình ảnh (PDF/Docx/PPTX)",
            variable=self._extract_var,
            command=self._notify_change,
        )
        self._extract_cb.pack(anchor="w", padx=10, pady=2)

        self._ocr_var = ctk.BooleanVar(value=False)
        self._ocr_cb = ctk.CTkCheckBox(
            self,
            text="Dùng AI mô tả ảnh (OCR - cần API)",
            variable=self._ocr_var,
            command=self._on_ai_feature_change,
        )
        self._ocr_cb.pack(anchor="w", padx=10, pady=2)

        # 3. AI Enrichment Section
        ai_header = ctk.CTkLabel(
            self, text="✨ AI Enrichment", font=ctk.CTkFont(size=13, weight="bold")
        )
        ai_header.pack(anchor="w", padx=10, pady=(15, 5))

        self._summary_var = ctk.BooleanVar(value=False)
        self._summary_cb = ctk.CTkCheckBox(
            self,
            text="Tóm tắt & Tạo Keywords (cần API)",
            variable=self._summary_var,
            command=self._on_ai_feature_change,
        )
        self._summary_cb.pack(anchor="w", padx=10, pady=2)

        # 4. API Configuration Frame
        self._api_config_frame = ctk.CTkFrame(self, fg_color=("gray90", "gray20"))
        self._api_config_frame.pack(fill="x", padx=10, pady=10)

        config_title = ctk.CTkLabel(
            self._api_config_frame,
            text="🔗 OpenAI-Compatible Configuration",
            font=ctk.CTkFont(size=12, weight="bold"),
        )
        config_title.pack(anchor="w", padx=10, pady=(8, 5))

        # Base URL row
        url_row = ctk.CTkFrame(self._api_config_frame, fg_color="transparent")
        url_row.pack(fill="x", padx=10, pady=3)

        ctk.CTkLabel(url_row, text="Base URL:", width=70, anchor="w").pack(side="left")
        self._base_url_entry = ctk.CTkEntry(url_row, width=300)
        self._base_url_entry.insert(0, "https://api.openai.com/v1")
        self._base_url_entry.pack(side="left", fill="x", expand=True)

        # Model row
        model_row = ctk.CTkFrame(self._api_config_frame, fg_color="transparent")
        model_row.pack(fill="x", padx=10, pady=3)

        ctk.CTkLabel(model_row, text="Model:", width=70, anchor="w").pack(side="left")
        self._model_var = ctk.StringVar(value="gpt-4o-mini")
        self._model_menu = ctk.CTkOptionMenu(
            model_row,
            values=self.DEFAULT_MODELS,
            variable=self._model_var,
            width=200,
        )
        self._model_menu.pack(side="left")

        self._refresh_btn = ctk.CTkButton(
            model_row,
            text="🔄",
            width=32,
            command=self._refresh_models,
            fg_color="transparent",
            border_width=1,
            text_color=("gray10", "gray90"),
        )
        self._refresh_btn.pack(side="left", padx=5)

        # API Key row
        key_row = ctk.CTkFrame(self._api_config_frame, fg_color="transparent")
        key_row.pack(fill="x", padx=10, pady=(0, 5))

        ctk.CTkLabel(key_row, text="API Key:", width=70, anchor="w").pack(side="left")
        self._api_entry = ctk.CTkEntry(
            key_row,
            placeholder_text="Nhập API Key...",
            show="•",
            width=200,
        )
        self._api_entry.pack(side="left", fill="x", expand=True)

        self._test_btn = ctk.CTkButton(
            key_row,
            text="Test",
            width=60,
            command=self._test_connection,
        )
        self._test_btn.pack(side="right", padx=(5, 0))

        self._status_label = ctk.CTkLabel(
            self._api_config_frame,
            text="",
            font=ctk.CTkFont(size=10),
        )
        self._status_label.pack(anchor="w", padx=10, pady=(0, 5))

        self._on_ai_feature_change()

    def _on_ai_feature_change(self) -> None:
        """Enable/disable API config based on whether AI features are needed."""
        needed = self._summary_var.get() or getattr(self, "_ocr_var", ctk.BooleanVar(value=False)).get()
        if needed:
            self._api_config_frame.configure(border_width=1, border_color="green")
        else:
            self._api_config_frame.configure(border_width=0)
        self._notify_change()

    def _refresh_models(self) -> None:
        """Fetch models from the configured base_url."""
        base_url = self._base_url_entry.get().strip()
        api_key = self._api_entry.get().strip()

        if not api_key:
            self._status_label.configure(
                text="⚠️ Cần nhập API Key trước", text_color="orange"
            )
            return
        if not base_url:
            self._status_label.configure(
                text="⚠️ Cần nhập Base URL trước", text_color="orange"
            )
            return

        self._status_label.configure(text="⏳ Đang tải danh sách...", text_color="blue")
        self.update_idletasks()

        def fetch():
            from llm_client import LLMClient
            models = LLMClient.fetch_models(base_url, api_key)
            self.after(0, lambda: self._update_model_list(models))

        threading.Thread(target=fetch, daemon=True).start()

    def _update_model_list(self, models: list[str]) -> None:
        """Update model dropdown after refresh."""
        if models:
            self._models_cache = models
            self._model_menu.configure(values=models)
            if self._model_var.get() not in models:
                self._model_var.set(models[0])
            self._status_label.configure(
                text=f"✅ Tìm thấy {len(models)} models", text_color="green"
            )
        else:
            self._model_menu.configure(values=self.DEFAULT_MODELS)
            self._status_label.configure(
                text="❌ Không lấy được danh sách (Check Key/URL/Net)",
                text_color="red",
            )

    def _test_connection(self) -> None:
        """Test API connection."""
        base_url = self._base_url_entry.get().strip()
        api_key = self._api_entry.get().strip()
        model = self._model_var.get()

        if not api_key:
            self._status_label.configure(
                text="⚠️ Cần nhập API Key", text_color="orange"
            )
            return

        self._api_key = api_key
        self._status_label.configure(text="⏳ Đang kiểm tra...", text_color="blue")
        self.update_idletasks()

        def test():
            from llm_client import LLMClient
            client = LLMClient(base_url, api_key, model)
            success, msg = client.test_connection()
            color = "green" if success else "red"
            self.after(0, lambda: self._status_label.configure(text=msg, text_color=color))

        threading.Thread(target=test, daemon=True).start()
        self._notify_change()

    def _notify_change(self) -> None:
        if self._on_change:
            self._on_change()

    # Properties
    @property
    def chunking_enabled(self) -> bool:
        return self._chunk_var.get()

    @property
    def excel_clean_enabled(self) -> bool:
        return self._excel_clean_var.get()

    @property
    def extract_images(self) -> bool:
        return self._extract_var.get()

    @property
    def summarize_enabled(self) -> bool:
        return self._summary_var.get()

    @property
    def llm_config(self) -> dict:
        return {
            "base_url": self._base_url_entry.get().strip(),
            "api_key": self._api_entry.get().strip(),
            "model": self._model_var.get(),
        }

    def get_config(self) -> dict:
        return {
            "chunk_enabled": self._chunk_var.get(),
            "excel_clean_enabled": self._excel_clean_var.get(),
            "extract_images": self._extract_var.get(),
            "ocr_enabled": getattr(self, "_ocr_var", ctk.BooleanVar(value=False)).get(),
            "summary_enabled": self._summary_var.get(),
            "base_url": self._base_url_entry.get().strip(),
            "api_key": self._api_entry.get().strip(),
            "model": self._model_var.get(),
        }

    def load_config(self, cfg: dict) -> None:
        self._chunk_var.set(cfg.get("chunk_enabled", False))
        self._excel_clean_var.set(cfg.get("excel_clean_enabled", False))
        self._extract_var.set(cfg.get("extract_images", False))
        self._ocr_var.set(cfg.get("ocr_enabled", False))
        self._summary_var.set(cfg.get("summary_enabled", False))

        self._base_url_entry.delete(0, "end")
        self._base_url_entry.insert(0, cfg.get("base_url", "https://api.openai.com/v1"))

        self._api_entry.delete(0, "end")
        self._api_entry.insert(0, cfg.get("api_key", ""))

        self._model_var.set(cfg.get("model", "gpt-4o-mini"))

        self._on_ai_feature_change()
