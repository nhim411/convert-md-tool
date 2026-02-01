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
    - API Key & Model Management
    """

    OPENAI_MODELS = ["gpt-4o", "gpt-4o-mini", "o1-preview", "o1-mini", "gpt-4-turbo"]
    GEMINI_MODELS = ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-2.0-flash-exp"]

    def __init__(
        self,
        master,
        on_change: Optional[Callable[[], None]] = None,
        **kwargs
    ):
        super().__init__(master, **kwargs)
        self._on_change = on_change
        self._api_keys = {"openai": "", "gemini": ""}
        self._create_widgets()

    def _create_widgets(self):
        # 1. RAG Section
        rag_header = ctk.CTkLabel(self, text="📚 RAG & Chunking", font=ctk.CTkFont(size=13, weight="bold"))
        rag_header.pack(anchor="w", padx=10, pady=(10, 5))

        self._chunk_var = ctk.BooleanVar(value=False)
        self._chunk_cb = ctk.CTkCheckBox(
            self,
            text="Smart Chunking (Tách nhỏ theo Header)",
            variable=self._chunk_var,
            command=self._notify_change
        )
        self._chunk_cb.pack(anchor="w", padx=10, pady=2)

        self._excel_clean_var = ctk.BooleanVar(value=False)
        self._excel_clean_cb = ctk.CTkCheckBox(
            self,
            text="Clean Excel Data (Forward Fill)",
            variable=self._excel_clean_var,
            command=self._notify_change
        )
        self._excel_clean_cb.pack(anchor="w", padx=10, pady=2)

        chunk_note = ctk.CTkLabel(self, text="   → Xuất ra thêm file .jsonl cho RAG", text_color="gray", font=ctk.CTkFont(size=10))
        chunk_note.pack(anchor="w", padx=10)

        # 2. Image Section
        img_header = ctk.CTkLabel(self, text="🖼️ Hình ảnh", font=ctk.CTkFont(size=13, weight="bold"))
        img_header.pack(anchor="w", padx=10, pady=(15, 5))

        self._extract_var = ctk.BooleanVar(value=False)
        self._extract_cb = ctk.CTkCheckBox(
            self,
            text="Trích xuất hình ảnh (PDF/Docx/PPTX)",
            variable=self._extract_var,
            command=self._notify_change
        )
        self._extract_cb.pack(anchor="w", padx=10, pady=2)

        # 3. AI Enrichment Section
        ai_header = ctk.CTkLabel(self, text="✨ AI Enrichment", font=ctk.CTkFont(size=13, weight="bold"))
        ai_header.pack(anchor="w", padx=10, pady=(15, 5))

        self._summary_var = ctk.BooleanVar(value=False)
        self._summary_cb = ctk.CTkCheckBox(
            self,
            text="Tóm tắt & Tạo Keywords (cần API)",
            variable=self._summary_var,
            command=self._on_ai_feature_change
        )
        self._summary_cb.pack(anchor="w", padx=10, pady=2)

        self._describe_var = ctk.BooleanVar(value=False)
        self._describe_cb = ctk.CTkCheckBox(
            self,
            text="Mô tả nội dung ảnh (Vision API)",
            variable=self._describe_var,
            command=self._on_ai_feature_change
        )
        self._describe_cb.pack(anchor="w", padx=10, pady=2)

        # 4. API Configuration (Hidden/Disabled unless AI needed)
        self._ai_config_frame = ctk.CTkFrame(self, fg_color=("gray90", "gray20"))
        self._ai_config_frame.pack(fill="x", padx=10, pady=10)

        # Provider
        row1 = ctk.CTkFrame(self._ai_config_frame, fg_color="transparent")
        row1.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(row1, text="Provider:").pack(side="left")
        self._provider_var = ctk.StringVar(value="openai")
        self._provider_menu = ctk.CTkOptionMenu(
            row1,
            values=["openai", "gemini"],
            variable=self._provider_var,
            command=self._on_provider_change,
            width=100
        )
        self._provider_menu.pack(side="left", padx=10)

        ctk.CTkLabel(row1, text="Model:").pack(side="left", padx=(10, 0))
        self._model_var = ctk.StringVar(value="gpt-4o-mini")
        self._model_menu = ctk.CTkOptionMenu(
            row1,
            values=self.OPENAI_MODELS,
            variable=self._model_var,
            width=140
        )
        self._model_menu.pack(side="left", padx=5)

        # Refresh Button (New)
        self._refresh_btn = ctk.CTkButton(
            row1,
            text="🔄",
            width=30,
            command=self._refresh_models,
            fg_color="transparent",
            border_width=1,
            text_color=("gray10", "gray90")
        )
        self._refresh_btn.pack(side="left", padx=5)

        # API Key
        row2 = ctk.CTkFrame(self._ai_config_frame, fg_color="transparent")
        row2.pack(fill="x", padx=10, pady=(0, 5))

        self._api_entry = ctk.CTkEntry(
            row2,
            placeholder_text="Nhập API Key...",
            show="•",
            width=200
        )
        self._api_entry.pack(side="left", fill="x", expand=True)

        self._test_btn = ctk.CTkButton(
            row2, text="Test", width=60, command=self._test_api_key
        )
        self._test_btn.pack(side="right", padx=(5, 0))

        self._status_label = ctk.CTkLabel(self._ai_config_frame, text="", font=ctk.CTkFont(size=10))
        self._status_label.pack(anchor="w", padx=10, pady=(0, 5))

        # Initial state
        self._on_ai_feature_change()

    def _on_ai_feature_change(self):
        # Enable AI config if Summary OR Describe is checked
        needed = self._summary_var.get() or self._describe_var.get()
        state = "normal" if needed else "disabled"

        # We don't disable the frame itself to keep text readable
        # self._provider_menu.configure(state=state)
        # self._model_menu.configure(state=state)
        # self._api_entry.configure(state=state)
        # self._test_btn.configure(state=state)

        # Color hint
        if needed:
            self._ai_config_frame.configure(border_width=1, border_color="green")
        else:
            self._ai_config_frame.configure(border_width=0)

        self._notify_change()

    def _on_provider_change(self, provider):
        # Save current key
        # (Simplified logic from image_options.py)
        if provider == "openai":
            self._model_menu.configure(values=self.OPENAI_MODELS)
            self._model_var.set("gpt-4o-mini")
        else:
            self._model_menu.configure(values=self.GEMINI_MODELS)
            self._model_var.set("gemini-1.5-flash")

        # Restore key logic... (same as before)
        saved = self._api_keys.get(provider, "")
        self._api_entry.delete(0, "end")
        self._api_entry.insert(0, saved)
        self._notify_change()

    def _test_api_key(self):
        key = self._api_entry.get().strip()
        provider = self._provider_var.get()
        if not key:
            self._status_label.configure(text="⚠️ Theo API Key", text_color="orange")
            return

        # Save key
        self._api_keys[provider] = key

        # Mock test or real test
        self._status_label.configure(text="✅ Đã lưu API Key", text_color="green")
        self._notify_change()

    def _refresh_models(self):
        """Fetch models from API."""
        key = self._api_entry.get().strip()
        provider = self._provider_var.get()

        if not key:
            self._status_label.configure(text="⚠️ Cần nhập API Key trước", text_color="orange")
            return

        self._status_label.configure(text="⏳ Đang tải danh sách...", text_color="blue")
        self.update_idletasks()

        def fetch():
            # Import inside to avoid circular deps if any, or just for cleanliness
            from ai_helper import AIService
            models = AIService.fetch_available_models(provider, key)

            # Scheduling UI update on main thread
            self.after(0, lambda: self._update_model_list(models))

        threading.Thread(target=fetch, daemon=True).start()

    def _update_model_list(self, models):
        if models:
            self._model_menu.configure(values=models)
            # Default to first if current not in list
            if self._model_var.get() not in models:
                self._model_var.set(models[0])

            count = len(models)
            self._status_label.configure(text=f"✅ Tìm thấy {count} models", text_color="green")
        else:
            self._status_label.configure(text="❌ Không lấy được danh sách (Check Key/Net)", text_color="red")


    def _notify_change(self):
        if self._on_change:
            self._on_change()

    # Properties
    @property
    def chunking_enabled(self): return self._chunk_var.get()
    @property
    def excel_clean_enabled(self): return self._excel_clean_var.get()

    @property
    def extract_images(self): return self._extract_var.get()
    @property
    def summarize_enabled(self): return self._summary_var.get()
    @property
    def describe_images(self): return self._describe_var.get()
    @property
    def ai_config(self):
        return {
            "provider": self._provider_var.get(),
            "model": self._model_var.get(),
            "api_key": self._api_entry.get().strip()
        }

    # Load/Save Config methods...
    def get_config(self):
        return {
            "chunk_enabled": self._chunk_var.get(),
            "excel_clean_enabled": self._excel_clean_var.get(),
            "extract_images": self._extract_var.get(),
            "summary_enabled": self._summary_var.get(),
            "describe_images": self._describe_var.get(),
            "ai_provider": self._provider_var.get(),
            "ai_model": self._model_var.get(),
            "openai_key": self._api_keys.get("openai", self._api_entry.get() if self._provider_var.get()=="openai" else ""),
            "gemini_key": self._api_keys.get("gemini", self._api_entry.get() if self._provider_var.get()=="gemini" else "")
        }

    def load_config(self, cfg):
        self._chunk_var.set(cfg.get("chunk_enabled", False))
        self._excel_clean_var.set(cfg.get("excel_clean_enabled", False))
        self._extract_var.set(cfg.get("extract_images", False))
        self._summary_var.set(cfg.get("summary_enabled", False))
        self._describe_var.set(cfg.get("describe_images", False))

        self._provider_var.set(cfg.get("ai_provider", "openai"))
        self._on_provider_change(self._provider_var.get())

        self._model_var.set(cfg.get("ai_model", "gpt-4o-mini"))

        self._api_keys["openai"] = cfg.get("openai_key", "")
        self._api_keys["gemini"] = cfg.get("gemini_key", "")

        # Set entry
        curr_prov = self._provider_var.get()
        self._api_entry.delete(0, "end")
        self._api_entry.insert(0, self._api_keys.get(curr_prov, ""))

        self._on_ai_feature_change()
