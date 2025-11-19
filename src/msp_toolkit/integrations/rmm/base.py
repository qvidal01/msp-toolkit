"""
Base RMM adapter interface.

This module defines the abstract base class that all RMM adapters
must implement to provide a unified interface.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Any

from msp_toolkit.core.models import Device


class RMMAdapter(ABC):
    """
    Abstract base class for RMM platform adapters.

    All RMM integrations (ConnectWise, Datto, NinjaRMM, etc.) must
    inherit from this class and implement its abstract methods.

    Example:
        >>> class ConnectWiseRMM(RMMAdapter):
        ...     def get_devices(self, client_id):
        ...         # Implementation here
        ...         pass
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize RMM adapter.

        Args:
            config: Configuration dictionary for this adapter
        """
        self.config = config

    @abstractmethod
    def get_devices(self, client_id: str) -> List[Device]:
        """
        Get all devices for a client.

        Args:
            client_id: Client identifier

        Returns:
            List of Device objects
        """
        pass

    @abstractmethod
    def deploy_agent(self, device_id: str) -> Dict[str, Any]:
        """
        Deploy RMM agent to a device.

        Args:
            device_id: Device identifier

        Returns:
            Deployment result dictionary
        """
        pass

    @abstractmethod
    def execute_command(self, device_id: str, command: str) -> Dict[str, Any]:
        """
        Execute command on a device.

        Args:
            device_id: Device identifier
            command: Command to execute

        Returns:
            Command execution result
        """
        pass

    @abstractmethod
    def get_alerts(self, client_id: str, since: datetime) -> List[Dict[str, Any]]:
        """
        Get alerts for a client.

        Args:
            client_id: Client identifier
            since: Get alerts since this timestamp

        Returns:
            List of alert dictionaries
        """
        pass
