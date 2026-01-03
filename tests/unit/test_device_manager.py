"""
Unit tests for DeviceManager.
"""

import pytest

from msp_toolkit.core.client_manager import ClientManager
from msp_toolkit.core.device_manager import DeviceManager
from msp_toolkit.core.exceptions import ClientNotFoundError, MSPToolkitError


class TestDeviceManager:
    """Test suite for DeviceManager."""

    def test_add_and_list_devices(self, test_config):
        client_mgr = ClientManager(test_config)
        client_mgr.create("acme-corp", name="Acme Corp")
        device_mgr = DeviceManager(test_config)

        device = device_mgr.add_device("acme-corp", name="server-1", type="server")
        devices = device_mgr.list_devices(client_id="acme-corp")

        assert device.id is not None
        assert len(devices) == 1
        assert devices[0].name == "server-1"

    def test_add_device_missing_client(self, test_config):
        device_mgr = DeviceManager(test_config)

        with pytest.raises(ClientNotFoundError):
            device_mgr.add_device("missing", name="device")

    def test_delete_device(self, test_config):
        client_mgr = ClientManager(test_config)
        client_mgr.create("acme-corp", name="Acme Corp")
        device_mgr = DeviceManager(test_config)
        device = device_mgr.add_device("acme-corp", name="server-1")

        assert device_mgr.delete_device(device.id) is True

        with pytest.raises(MSPToolkitError):
            device_mgr.delete_device(device.id)
