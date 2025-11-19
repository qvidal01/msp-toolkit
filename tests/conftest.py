"""
Pytest configuration and fixtures.

This module provides reusable test fixtures for all tests.
"""

import pytest
from pathlib import Path

from msp_toolkit import MSPToolkit
from msp_toolkit.utils.config import Config
from msp_toolkit.core.models import Client, ClientTier, ClientStatus


@pytest.fixture
def test_config():
    """Provide test configuration."""
    return Config({
        "general": {
            "log_level": "DEBUG",
            "company_name": "Test MSP",
        },
        "database": {
            "type": "sqlite",
            "path": ":memory:",
        },
        "health_checks": {
            "thresholds": {
                "cpu_percent": 85,
                "memory_percent": 90,
                "disk_percent": 85,
            }
        },
        "reporting": {
            "template_dir": "templates/reports",
            "output_dir": "tests/output",
        },
    })


@pytest.fixture
def toolkit(test_config):
    """Provide MSPToolkit instance."""
    return MSPToolkit(test_config)


@pytest.fixture
def sample_client():
    """Provide sample client for testing."""
    return Client(
        id="test-client",
        name="Test Client Inc",
        contact_email="admin@testclient.com",
        tier=ClientTier.PREMIUM,
        status=ClientStatus.ACTIVE,
    )


@pytest.fixture
def temp_output_dir(tmp_path):
    """Provide temporary output directory."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir
