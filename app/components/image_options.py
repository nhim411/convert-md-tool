"""
Image Options Component (Enhanced)
Options for image extraction and AI description with API testing and model selection.
"""

import customtkinter as ctk
from typing import Callable, Optional
import threading

from locales import LABELS


class ImageOptions(ctk.CTkFrame):
    """
    Component for image extraction and AI description options.
    Enhanced with API testing, model selection, and explanatory notes.
    """

    # Available models (updated 2026)
    OPENAI_MODELS = [
        "gpt-4o-mini",
        "gpt-4o",
        "gpt-4-turbo",
        "gpt-4.5-preview",
        "o1-mini",
        "o1-preview",
    ]
    GEMINI_MODELS = [
        "gemini-1.5-flash",
        "gemini-1.5-pro",
        "gemini-2.0-flash",
        "gemini-2.5-flash",
        "gemini-3-flash",
    ]

    def __init__(
        self,
        master,
        on_change: Optional[Callable[[], None]] = None,
        **kwargs
    ):
        """
        Initialize ImageOptions.

        Args:
            master: Parent widget
            on_change: Callback when options change
        """
        super().__init__(master, **kwargs)

        self._on_change = on_change
        self._api_keys = {"openai": "", "gemini": ""}
        self._create_widgets()

    def _create_widgets(self):
        """Create and layout widgets."""
        # Header
        header = ctk.CTkLabel(
            self,
            text=f"🖼️ {LABELS.get('image_options', 'Tùy chọn Hình ảnh')}",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        header.pack(anchor="w", padx=10, pady=(10, 5))

        # Explanatory note
        note_text = "ℹ️ markitdown không convert được ảnh trong tài liệu. Bật tùy chọn dưới đây để trích xuất và mô tả ảnh."
        note_label = ctk.CTkLabel(
            self,
            text=note_text,
            font=ctk.CTkFont(size=11),
            text_color="gray",
            wraplength=600,
            justify="left"
        )
        note_label.pack(anchor="w", padx=10, pady=(0, 5))

        # Extract images checkbox
        self._extract_var = ctk.BooleanVar(value=False)
        self._extract_cb = ctk.CTkCheckBox(
            self,
            text="Trích xuất hình ảnh từ tài liệu (chỉ PDF)",
            variable=self._extract_var,
            command=self._on_extract_change
        )
        self._extract_cb.pack(anchor="w", padx=10, pady=5)

        # Extract note - per-file folder structure
        extract_note = ctk.CTkLabel(
            self,
            text="   → Ảnh lưu vào: [tên_file]_images/ cạnh file .md",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        extract_note.pack(anchor="w", padx=10)

        # AI description frame
        self._ai_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._ai_frame.pack(fill="x", padx=20, pady=5)

        # Describe with AI checkbox
        self._describe_var = ctk.BooleanVar(value=False)
        self._describe_cb = ctk.CTkCheckBox(
            self._ai_frame,
            text=LABELS.get('describe_images', 'Mô tả hình ảnh bằng AI (cần API key)'),
            variable=self._describe_var,
            command=self._on_describe_change,
            state="disabled"
        )
        self._describe_cb.pack(anchor="w", pady=2)

        # Describe note
        describe_note = ctk.CTkLabel(
            self._ai_frame,
            text="→ AI sẽ mô tả nội dung ảnh để AI agent có thể đọc được",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        describe_note.pack(anchor="w", padx=20)

        # AI Provider selection
        provider_frame = ctk.CTkFrame(self._ai_frame, fg_color="transparent")
        provider_frame.pack(fill="x", pady=(10, 5))

        self._provider_label = ctk.CTkLabel(
            provider_frame,
            text=LABELS.get('ai_provider', 'AI Provider:'),
            state="disabled"
        )
        self._provider_label.pack(side="left", padx=(0, 10))

        self._provider_var = ctk.StringVar(value="openai")
        self._provider_menu = ctk.CTkOptionMenu(
            provider_frame,
            values=["openai", "gemini"],
            variable=self._provider_var,
            command=self._on_provider_change,
            width=100,
            state="disabled"
        )
        self._provider_menu.pack(side="left")

        # Model selection
        self._model_label = ctk.CTkLabel(
            provider_frame,
            text="Model:",
            state="disabled"
        )
        self._model_label.pack(side="left", padx=(20, 10))

        self._model_var = ctk.StringVar(value="gpt-4o-mini")
        self._model_menu = ctk.CTkOptionMenu(
            provider_frame,
            values=self.OPENAI_MODELS,
            variable=self._model_var,
            width=130,
            state="disabled"
        )
        self._model_menu.pack(side="left")

        # API Key input frame
        api_frame = ctk.CTkFrame(self._ai_frame, fg_color="transparent")
        api_frame.pack(fill="x", pady=5)

        self._api_label = ctk.CTkLabel(
            api_frame,
            text="API Key:",
            state="disabled"
        )
        self._api_label.pack(side="left", padx=(0, 10))

        self._api_entry = ctk.CTkEntry(
            api_frame,
            placeholder_text=LABELS.get('api_key_placeholder', 'Nhập API key...'),
            show="•",
            state="disabled",
            width=220
        )
        self._api_entry.pack(side="left")

        # Toggle show/hide API key
        self._show_key_var = ctk.BooleanVar(value=False)
        self._show_key_btn = ctk.CTkButton(
            api_frame,
            text="👁",
            width=30,
            command=self._toggle_show_key,
            state="disabled",
            fg_color="transparent",
            border_width=1
        )
        self._show_key_btn.pack(side="left", padx=5)

        # Test API button
        self._test_btn = ctk.CTkButton(
            api_frame,
            text="🔍 Test",
            width=60,
            command=self._test_api_key,
            state="disabled",
            fg_color="transparent",
            border_width=1
        )
        self._test_btn.pack(side="left", padx=5)

        # Clear API button
        self._clear_btn = ctk.CTkButton(
            api_frame,
            text="🗑️",
            width=30,
            command=self._clear_api_key,
            state="disabled",
            fg_color="transparent",
            border_width=1,
            text_color="gray"
        )
        self._clear_btn.pack(side="left")

        # Status label
        self._status_label = ctk.CTkLabel(
            self._ai_frame,
            text="",
            font=ctk.CTkFont(size=11)
        )
        self._status_label.pack(anchor="w", pady=2)

    def _on_extract_change(self):
        """Handle extract checkbox change."""
        is_extract = self._extract_var.get()
        state = "normal" if is_extract else "disabled"

        self._describe_cb.configure(state=state)

        if not is_extract:
            self._describe_var.set(False)
            self._on_describe_change()

        self._notify_change()

    def _on_describe_change(self):
        """Handle describe checkbox change."""
        is_describe = self._describe_var.get()
        state = "normal" if is_describe else "disabled"

        self._provider_label.configure(state=state)
        self._provider_menu.configure(state=state)
        self._model_label.configure(state=state)
        self._model_menu.configure(state=state)
        self._api_label.configure(state=state)
        self._api_entry.configure(state=state)
        self._show_key_btn.configure(state=state)
        self._test_btn.configure(state=state)
        self._clear_btn.configure(state=state)

        if not is_describe:
            self._status_label.configure(text="")

        self._notify_change()

    def _on_provider_change(self, provider: str):
        """Handle provider change."""
        # Update model options
        if provider == "openai":
            self._model_menu.configure(values=self.OPENAI_MODELS)
            self._model_var.set("gpt-4o-mini")
        else:
            self._model_menu.configure(values=self.GEMINI_MODELS)
            self._model_var.set("gemini-1.5-flash")

        # Restore saved API key for this provider
        saved_key = self._api_keys.get(provider, "")
        self._api_entry.configure(state="normal")
        self._api_entry.delete(0, "end")
        if saved_key:
            self._api_entry.insert(0, saved_key)

        self._status_label.configure(text="")
        self._notify_change()

    def _toggle_show_key(self):
        """Toggle API key visibility."""
        if self._show_key_var.get():
            self._api_entry.configure(show="•")
            self._show_key_var.set(False)
        else:
            self._api_entry.configure(show="")
            self._show_key_var.set(True)

    def _test_api_key(self):
        """Test the API key."""
        api_key = self._api_entry.get().strip()
        if not api_key:
            self._status_label.configure(text="⚠️ Vui lòng nhập API key", text_color="orange")
            return

        provider = self._provider_var.get()
        model = self._model_var.get()

        self._status_label.configure(text="⏳ Đang kiểm tra...", text_color="gray")
        self._test_btn.configure(state="disabled")

        # Test in background thread
        def test_thread():
            success, message = self._do_test_api(provider, api_key, model)
            self.after(0, lambda: self._show_test_result(success, message))

        threading.Thread(target=test_thread, daemon=True).start()

    def _do_test_api(self, provider: str, api_key: str, model: str) -> tuple:
        """Perform API test."""
        try:
            if provider == "openai":
                from openai import OpenAI
                client = OpenAI(api_key=api_key)
                # Simple test - list models
                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": "Hi"}],
                    max_tokens=5
                )
                return True, f"✅ Kết nối thành công với {model}"
            else:
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                model_obj = genai.GenerativeModel(model)
                response = model_obj.generate_content("Hi")
                return True, f"✅ Kết nối thành công với {model}"
        except Exception as e:
            error_msg = str(e)
            if "invalid_api_key" in error_msg.lower() or "api key" in error_msg.lower():
                return False, "❌ API key không hợp lệ"
            elif "model" in error_msg.lower():
                return False, f"❌ Model không khả dụng: {model}"
            else:
                return False, f"❌ Lỗi: {error_msg[:50]}"

    def _show_test_result(self, success: bool, message: str):
        """Show API test result."""
        color = "green" if success else "red"
        self._status_label.configure(text=message, text_color=color)
        self._test_btn.configure(state="normal")

        # Save API key if successful
        if success:
            provider = self._provider_var.get()
            self._api_keys[provider] = self._api_entry.get().strip()

    def _clear_api_key(self):
        """Clear the API key."""
        provider = self._provider_var.get()
        self._api_keys[provider] = ""
        self._api_entry.configure(state="normal")
        self._api_entry.delete(0, "end")
        self._status_label.configure(text="🗑️ Đã xóa API key", text_color="gray")
        self._notify_change()

    def _notify_change(self):
        """Notify callback of change."""
        if self._on_change:
            self._on_change()

    # Public properties
    @property
    def extract_images(self) -> bool:
        return self._extract_var.get()

    @property
    def describe_images(self) -> bool:
        return self._describe_var.get()

    @property
    def ai_provider(self) -> str:
        return self._provider_var.get()

    @property
    def ai_model(self) -> str:
        return self._model_var.get()

    @property
    def api_key(self) -> Optional[str]:
        key = self._api_entry.get().strip()
        return key if key else None

    # Config methods for save/load
    def get_config(self) -> dict:
        """Get current config as dict."""
        return {
            "extract_images": self._extract_var.get(),
            "describe_images": self._describe_var.get(),
            "ai_provider": self._provider_var.get(),
            "ai_model": self._model_var.get(),
            "openai_api_key": self._api_keys.get("openai", ""),
            "gemini_api_key": self._api_keys.get("gemini", ""),
        }

    def load_config(self, config: dict):
        """Load config from dict."""
        if config.get("extract_images"):
            self._extract_var.set(True)
            self._on_extract_change()

        if config.get("describe_images"):
            self._describe_var.set(True)
            self._on_describe_change()

        if config.get("ai_provider"):
            self._provider_var.set(config["ai_provider"])
            self._on_provider_change(config["ai_provider"])

        if config.get("ai_model"):
            self._model_var.set(config["ai_model"])

        # Load saved API keys
        self._api_keys["openai"] = config.get("openai_api_key", "")
        self._api_keys["gemini"] = config.get("gemini_api_key", "")

        # Show current provider's key
        provider = self._provider_var.get()
        if self._api_keys.get(provider):
            self._api_entry.configure(state="normal")
            self._api_entry.delete(0, "end")
            self._api_entry.insert(0, self._api_keys[provider])
            if not self._describe_var.get():
                self._api_entry.configure(state="disabled")
