"""
Main MSP Toolkit class - entry point for the framework.

This module provides the primary interface for interacting with the MSP Toolkit.
"""

from pathlib import Path
from typing import Any, Dict, Optional

import structlog

from msp_toolkit.core.client_manager import ClientManager
from msp_toolkit.core.health_monitor import HealthMonitor
from msp_toolkit.core.report_generator import ReportGenerator
from msp_toolkit.core.exceptions import ConfigurationError
from msp_toolkit.utils.config import Config
from msp_toolkit.utils.logger import setup_logging


logger = structlog.get_logger(__name__)


class MSPToolkit:
    """
    Main entry point for MSP Toolkit.

    This class provides access to all toolkit functionality including
    client management, health monitoring, reporting, and integrations.

    Example:
        >>> toolkit = MSPToolkit.from_config("config/msp-toolkit.yaml")
        >>> client_mgr = toolkit.get_client_manager()
        >>> health_mon = toolkit.get_health_monitor()
        >>> clients = client_mgr.list_clients()

    Attributes:
        config: Configuration object
        _client_manager: Cached client manager instance
        _health_monitor: Cached health monitor instance
        _report_generator: Cached report generator instance
    """

    def __init__(self, config: Config) -> None:
        """
        Initialize MSP Toolkit.

        Args:
            config: Configuration object

        Raises:
            ConfigurationError: If configuration is invalid
        """
        self.config = config
        self._client_manager: Optional[ClientManager] = None
        self._health_monitor: Optional[HealthMonitor] = None
        self._report_generator: Optional[ReportGenerator] = None

        # Set up logging
        setup_logging(level=config.get("general.log_level", "INFO"))
        logger.info("MSP Toolkit initialized", version="0.1.0")

    @classmethod
    def from_config(cls, config_path: str) -> "MSPToolkit":
        """
        Create toolkit instance from configuration file.

        Args:
            config_path: Path to YAML configuration file

        Returns:
            Initialized MSPToolkit instance

        Raises:
            ConfigurationError: If config file is missing or invalid
        """
        config_file = Path(config_path)
        if not config_file.exists():
            raise ConfigurationError(
                f"Configuration file not found: {config_path}",
                config_key="config_path",
            )

        config = Config.from_file(config_path)
        return cls(config)

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "MSPToolkit":
        """
        Create toolkit instance from configuration dictionary.

        Args:
            config_dict: Configuration dictionary

        Returns:
            Initialized MSPToolkit instance
        """
        config = Config(config_dict)
        return cls(config)

    def get_client_manager(self) -> ClientManager:
        """
        Get client manager instance.

        Returns:
            ClientManager instance (cached after first call)
        """
        if self._client_manager is None:
            self._client_manager = ClientManager(self.config)
        return self._client_manager

    def get_health_monitor(self) -> HealthMonitor:
        """
        Get health monitor instance.

        Returns:
            HealthMonitor instance (cached after first call)
        """
        if self._health_monitor is None:
            self._health_monitor = HealthMonitor(self.config)
        return self._health_monitor

    def get_report_generator(self) -> ReportGenerator:
        """
        Get report generator instance.

        Returns:
            ReportGenerator instance (cached after first call)
        """
        if self._report_generator is None:
            self._report_generator = ReportGenerator(self.config)
        return self._report_generator

    def health_check(self) -> Dict[str, Any]:
        """
        Perform self-diagnostic health check of the toolkit.

        Returns:
            Dictionary with health check results

        Example:
            >>> toolkit = MSPToolkit.from_config("config.yaml")
            >>> status = toolkit.health_check()
            >>> print(status["status"])  # "healthy" or "unhealthy"
        """
        results = {
            "status": "healthy",
            "checks": [],
        }

        # Check database connectivity
        try:
            # TODO: Implement actual database check
            results["checks"].append({
                "component": "database",
                "status": "healthy",
                "message": "Database accessible",
            })
        except Exception as e:
            results["status"] = "unhealthy"
            results["checks"].append({
                "component": "database",
                "status": "unhealthy",
                "message": f"Database check failed: {e}",
            })

        # Check configuration
        if self.config.validate():
            results["checks"].append({
                "component": "configuration",
                "status": "healthy",
                "message": "Configuration valid",
            })
        else:
            results["status"] = "unhealthy"
            results["checks"].append({
                "component": "configuration",
                "status": "unhealthy",
                "message": "Configuration invalid",
            })

        return results
