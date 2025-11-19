"""
Configuration management for notify-me.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


class Config:
    """Manages configuration for the notify-me application."""

    def __init__(self):
        self.config_dir = Path.home() / ".notify-me"
        self.config_file = self.config_dir / "config.json"
        self.config_dir.mkdir(exist_ok=True)
        self._config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or return defaults."""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def save_config(self) -> None:
        """Save current configuration to file."""
        with open(self.config_file, "w") as f:
            json.dump(self._config, f, indent=2)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value and save."""
        self._config[key] = value
        self.save_config()

    def is_configured(self) -> bool:
        """Check if the bot is properly configured."""
        return bool(self.get("bot_token") and self.get("chat_id"))

    @property
    def bot_token(self) -> Optional[str]:
        """Get the bot token."""
        return self.get("bot_token")

    @property
    def chat_id(self) -> Optional[str]:
        """Get the chat ID."""
        return self.get("chat_id")
