"""
Configuration management.

This module handles loading and validation of configuration from
YAML files, environment variables, and dictionaries.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from dotenv import load_dotenv

from msp_toolkit.core.exceptions import ConfigurationError


class Config:
    """
    Configuration manager for MSP Toolkit.

    Loads configuration from YAML files and environment variables,
    with support for nested key access and defaults.

    Example:
        >>> config = Config.from_file("config/msp-toolkit.yaml")
        >>> log_level = config.get("general.log_level", "INFO")
        >>> db_host = config.get("database.host", "localhost")
    """

    def __init__(self, config_dict: Dict[str, Any]) -> None:
        """
        Initialize Config with dictionary.

        Args:
            config_dict: Configuration dictionary
        """
        self._config = config_dict
        load_dotenv()  # Load .env file if present

    @classmethod
    def from_file(cls, config_path: str) -> "Config":
        """
        Load configuration from YAML file.

        Args:
            config_path: Path to YAML configuration file

        Returns:
            Config instance

        Raises:
            ConfigurationError: If file cannot be loaded
        """
        config_file = Path(config_path)

        if not config_file.exists():
            raise ConfigurationError(
                f"Configuration file not found: {config_path}",
                config_key="config_path",
            )

        try:
            with open(config_file, "r") as f:
                config_dict = yaml.safe_load(f) or {}
        except Exception as e:
            raise ConfigurationError(
                f"Failed to parse configuration file: {e}",
                config_key="config_path",
            )

        return cls(config_dict)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key.

        Supports nested keys using dot notation (e.g., "database.host").
        Environment variables take precedence over config file values.

        Args:
            key: Configuration key (supports dot notation)
            default: Default value if key not found

        Returns:
            Configuration value or default

        Example:
            >>> config.get("database.host", "localhost")
            'localhost'
            >>> config.get("general.log_level", "INFO")
            'DEBUG'  # If LOG_LEVEL env var is set to DEBUG
        """
        # Check for environment variable override
        env_key = key.upper().replace(".", "_")
        env_value = os.getenv(env_key)
        if env_value is not None:
            return env_value

        # Navigate nested dictionary
        keys = key.split(".")
        value = self._config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value.

        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        keys = key.split(".")
        config = self._config

        # Navigate to the parent key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        # Set the value
        config[keys[-1]] = value

    def validate(self) -> bool:
        """
        Validate configuration.

        Returns:
            True if configuration is valid

        Raises:
            ConfigurationError: If configuration is invalid
        """
        # TODO: Implement comprehensive validation
        # For now, just check that config exists
        if not self._config:
            raise ConfigurationError("Configuration is empty")

        return True

    def to_dict(self) -> Dict[str, Any]:
        """
        Get configuration as dictionary.

        Returns:
            Configuration dictionary
        """
        return self._config.copy()
