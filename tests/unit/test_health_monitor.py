"""
Unit tests for HealthMonitor.

Tests health checking functionality including CPU, memory,
disk checks and result storage.
"""

import pytest

from msp_toolkit.core.health_monitor import HealthMonitor
from msp_toolkit.core.models import HealthCheckType, HealthCheckStatus


class TestHealthMonitor:
    """Test suite for HealthMonitor."""

    def test_run_checks(self, test_config):
        """Test running health checks for a client."""
        monitor = HealthMonitor(test_config)

        results = monitor.run_checks("test-client")

        assert len(results) > 0
        assert all(isinstance(r.check_type, HealthCheckType) for r in results)
        assert all(isinstance(r.status, HealthCheckStatus) for r in results)

    def test_run_specific_check_types(self, test_config):
        """Test running specific health check types."""
        monitor = HealthMonitor(test_config)

        results = monitor.run_checks(
            "test-client",
            check_types=[HealthCheckType.CPU, HealthCheckType.MEMORY],
        )

        assert len(results) == 2
        assert results[0].check_type in [HealthCheckType.CPU, HealthCheckType.MEMORY]

    def test_get_history(self, test_config):
        """Test retrieving health check history."""
        monitor = HealthMonitor(test_config)

        # Run checks to generate history
        monitor.run_checks("test-client")

        history = monitor.get_history("test-client", days=7)

        assert len(history) > 0

    def test_get_status_summary(self, test_config):
        """Test getting health status summary."""
        monitor = HealthMonitor(test_config)

        # Run checks first
        monitor.run_checks("test-client")

        summary = monitor.get_status_summary("test-client")

        assert summary.total_checks > 0
        assert summary.healthy >= 0
        assert summary.warnings >= 0
        assert summary.critical >= 0

    def test_configure_health_checks(self, test_config):
        """Test configuring health checks for a client."""
        monitor = HealthMonitor(test_config)

        config = {
            "thresholds": {
                "cpu_percent": 75,
                "memory_percent": 80,
            }
        }

        result = monitor.configure("test-client", config)

        assert result is True
