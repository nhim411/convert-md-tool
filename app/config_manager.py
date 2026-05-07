"""
Configuration Manager
Handles saving and loading application settings.
"""

import json
import logging
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class AppConfig:
    """Application configuration settings."""
    # Theme
    theme: str = "dark"

    # Conversion options
    include_subfolders: bool = False
    depth_all: bool = True
    use_custom_output: bool = False
    custom_output_path: str = ""
    overwrite_existing: bool = False

    # RAG & AI Options
    chunk_enabled: bool = False
    excel_clean_enabled: bool = False
    extract_images: bool = False
    summary_enabled: bool = False

    # OpenAI-Compatible Configuration (unified)
    base_url: str = "https://api.openai.com/v1"
    api_key: str = ""
    model: str = "gpt-4o-mini"

    # Selected formats
    selected_formats: list = field(default_factory=lambda: [
        "PDF", "Word", "PowerPoint", "Excel", "Images", "Text"
    ])


class ConfigManager:
    """Manages application configuration persistence."""

    CONFIG_FILENAME = "config.json"

    def __init__(self, config_dir: str | None = None):
        if config_dir:
            self._config_dir = Path(config_dir)
        else:
            self._config_dir = Path.home() / ".markdown-converter"
        self._config_dir.mkdir(parents=True, exist_ok=True)
        self._config_path = self._config_dir / self.CONFIG_FILENAME
        self._config = AppConfig()

    def load(self) -> AppConfig:
        """Load configuration from file."""
        if not self._config_path.exists():
            logger.info("No config file found, using defaults")
            return self._config

        try:
            with open(self._config_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            for key, value in data.items():
                if hasattr(self._config, key):
                    setattr(self._config, key, value)

            self._migrate_legacy_fields(data)
            logger.info(f"Config loaded from {self._config_path}")
        except Exception as e:
            logger.error(f"Failed to load config: {e}")

        return self._config

    def _migrate_legacy_fields(self, data: dict) -> None:
        """Migrate legacy openai/gemini config to new unified format."""
        if not self._config.api_key:
            for old_key in ("openai_api_key", "openai_key"):
                if data.get(old_key):
                    self._config.api_key = data[old_key]
                    break

        if self._config.model == "gpt-4o-mini":
            for old_key in ("openai_model", "ai_model"):
                if data.get(old_key):
                    self._config.model = data[old_key]
                    break

    def save(self, config: AppConfig | None = None) -> bool:
        """Save configuration to file."""
        if config:
            self._config = config

        try:
            with open(self._config_path, "w", encoding="utf-8") as f:
                json.dump(asdict(self._config), f, indent=2, ensure_ascii=False)
            logger.info(f"Config saved to {self._config_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """Get a config value."""
        return getattr(self._config, key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a config value."""
        if hasattr(self._config, key):
            setattr(self._config, key, value)

    def clear_api_key(self) -> None:
        """Clear the stored API key."""
        self._config.api_key = ""
        self.save()

    @property
    def config(self) -> AppConfig:
        """Get current config."""
        return self._config
