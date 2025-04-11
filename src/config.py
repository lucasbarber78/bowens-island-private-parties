"""Configuration settings for the Bowens Island Private Parties connector."""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


class Config:
    """Configuration manager for the application."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration from the given path or default location."""
        if config_path is None:
            # Use default location in user's home directory
            self.config_path = os.path.join(
                Path.home(), ".bowens_island", "config.yaml"
            )
        else:
            self.config_path = config_path

        # Create default config if it doesn't exist
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        if not os.path.exists(self.config_path):
            self._create_default_config()

        # Load configuration
        self.reload()

    def reload(self) -> None:
        """Reload configuration from disk."""
        with open(self.config_path, "r") as f:
            self.config = yaml.safe_load(f)

    def save(self) -> None:
        """Save current configuration to disk."""
        with open(self.config_path, "w") as f:
            yaml.dump(self.config, f, default_flow_style=False)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by key."""
        keys = key.split(".")
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value and save to disk."""
        keys = key.split(".")
        config = self.config
        for i, k in enumerate(keys[:-1]):
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        self.save()

    def _create_default_config(self) -> None:
        """Create default configuration file."""
        default_config = {
            "cognito": {
                "api_key": "",
                "form_id": "17",  # Default form ID for Bowens Island Private Party
                "base_url": "https://www.cognitoforms.com/api",
            },
            "excel": {
                "template_path": "",
                "main_sheet": "MainData",
                "read_only": True,
            },
            "sync": {
                "last_sync": None,
                "auto_sync_on_open": True,
                "auto_sync_on_save": False,
                "confirm_changes": True,
            },
        }

        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, "w") as f:
            yaml.dump(default_config, f, default_flow_style=False)
