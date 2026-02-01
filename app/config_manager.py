"""
Configuration Manager
Handles saving and loading application settings.
"""

import os
import json
import logging
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import Optional, Dict, Any

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
    describe_images: bool = False
    summary_enabled: bool = False

    ai_provider: str = "openai"
    ai_model: str = "gpt-4o-mini"
    openai_key: str = ""
    gemini_key: str = ""

    # Selected formats
    selected_formats: list = field(default_factory=lambda: [
        'PDF', 'Word', 'PowerPoint', 'Excel', 'Images', 'Text'
    ])

    # Image options
    extract_images: bool = False
    describe_images: bool = False
    ai_provider: str = "openai"

    # API Keys (stored securely)
    openai_api_key: str = ""
    gemini_api_key: str = ""

    # Selected models
    openai_model: str = "gpt-4o-mini"
    gemini_model: str = "gemini-1.5-flash"


class ConfigManager:
    """
    Manages application configuration persistence.
    """

    CONFIG_FILENAME = "config.json"

    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize ConfigManager.

        Args:
            config_dir: Directory to store config. Defaults to app directory.
        """
        if config_dir:
            self._config_dir = Path(config_dir)
        else:
            # Use user's home directory for config
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
            with open(self._config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Update config with loaded values
            for key, value in data.items():
                if hasattr(self._config, key):
                    setattr(self._config, key, value)

            logger.info(f"Config loaded from {self._config_path}")
        except Exception as e:
            logger.error(f"Failed to load config: {e}")

        return self._config

    def save(self, config: Optional[AppConfig] = None) -> bool:
        """
        Save configuration to file.

        Args:
            config: Config to save. Uses current config if None.

        Returns:
            True if saved successfully
        """
        if config:
            self._config = config

        try:
            with open(self._config_path, 'w', encoding='utf-8') as f:
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

    def clear_api_key(self, provider: str) -> None:
        """Clear API key for a provider."""
        if provider == "openai":
            self._config.openai_api_key = ""
        elif provider == "gemini":
            self._config.gemini_api_key = ""
        self.save()

    @property
    def config(self) -> AppConfig:
        """Get current config."""
        return self._config
