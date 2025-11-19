"""
MSP Toolkit - AI-Powered Automation for Managed Service Providers

This package provides a comprehensive framework for automating common MSP tasks,
including client management, health monitoring, reporting, and RMM integration.

Features:
    - Client lifecycle management
    - Multi-platform health monitoring
    - Automated report generation
    - RMM platform integration
    - AI-powered automation via MCP server
    - Secure credential management
    - Extensible plugin architecture

Example:
    Basic usage of the MSP Toolkit:

    >>> from msp_toolkit import MSPToolkit
    >>> toolkit = MSPToolkit.from_config("config/msp-toolkit.yaml")
    >>> client_mgr = toolkit.get_client_manager()
    >>> clients = client_mgr.list_clients()
"""

__version__ = "0.1.0"
__author__ = "AIQSO"
__license__ = "MIT"

from msp_toolkit.core.toolkit import MSPToolkit
from msp_toolkit.core.client_manager import ClientManager
from msp_toolkit.core.health_monitor import HealthMonitor
from msp_toolkit.core.report_generator import ReportGenerator

__all__ = [
    "MSPToolkit",
    "ClientManager",
    "HealthMonitor",
    "ReportGenerator",
    "__version__",
]
