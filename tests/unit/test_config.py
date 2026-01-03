"""
Unit tests for configuration handling.
"""

import pytest

from msp_toolkit.core.exceptions import ConfigurationError
from msp_toolkit.utils.config import Config


def test_config_validation_applies_defaults():
    """Config.validate should normalize and apply defaults."""
    config = Config({
        "general": {"log_level": "info"},
        "database": {"type": "sqlite", "path": ":memory:"},
        "reporting": {"output_dir": "tests/output"},
    })

    assert config.validate() is True
    # Defaults should be present after validation
    assert config.get("health_checks.thresholds.cpu_percent") == 85
    assert config.get("general.log_level") == "INFO"


def test_config_validation_rejects_empty_configs():
    """Empty configs should raise a ConfigurationError."""
    config = Config({})

    with pytest.raises(ConfigurationError):
        config.validate()


def test_config_validation_rejects_invalid_values():
    """Out-of-range thresholds should fail validation."""
    config = Config({
        "health_checks": {"thresholds": {"cpu_percent": 150}},
    })

    with pytest.raises(ConfigurationError):
        config.validate()
