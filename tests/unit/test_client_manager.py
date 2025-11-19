"""
Unit tests for ClientManager.

Tests client lifecycle operations including creation, retrieval,
updates, and deletion.
"""

import pytest

from msp_toolkit.core.client_manager import ClientManager
from msp_toolkit.core.models import ClientTier, ClientStatus
from msp_toolkit.core.exceptions import ClientNotFoundError, ClientAlreadyExistsError


class TestClientManager:
    """Test suite for ClientManager."""

    def test_create_client(self, test_config):
        """Test creating a new client."""
        manager = ClientManager(test_config)

        client = manager.create(
            client_id="acme-corp",
            name="Acme Corp",
            contact_email="admin@acmecorp.com",
            tier=ClientTier.PREMIUM,
        )

        assert client.id == "acme-corp"
        assert client.name == "Acme Corp"
        assert client.tier == ClientTier.PREMIUM
        assert client.status == ClientStatus.ACTIVE

    def test_create_duplicate_client_raises_error(self, test_config):
        """Test that creating a duplicate client raises error."""
        manager = ClientManager(test_config)

        manager.create("acme-corp", name="Acme Corp")

        with pytest.raises(ClientAlreadyExistsError) as exc_info:
            manager.create("acme-corp", name="Acme Corp")

        assert exc_info.value.code == "CLIENT_ALREADY_EXISTS"

    def test_get_client(self, test_config):
        """Test retrieving a client by ID."""
        manager = ClientManager(test_config)
        manager.create("acme-corp", name="Acme Corp")

        client = manager.get_client("acme-corp")

        assert client.id == "acme-corp"
        assert client.name == "Acme Corp"

    def test_get_nonexistent_client_raises_error(self, test_config):
        """Test that getting a nonexistent client raises error."""
        manager = ClientManager(test_config)

        with pytest.raises(ClientNotFoundError) as exc_info:
            manager.get_client("nonexistent")

        assert exc_info.value.code == "CLIENT_NOT_FOUND"

    def test_list_clients(self, test_config):
        """Test listing all clients."""
        manager = ClientManager(test_config)

        manager.create("client-1", name="Client 1", tier=ClientTier.BRONZE)
        manager.create("client-2", name="Client 2", tier=ClientTier.PREMIUM)
        manager.create("client-3", name="Client 3", tier=ClientTier.PREMIUM)

        all_clients = manager.list_clients()
        assert len(all_clients) == 3

        premium_clients = manager.list_clients(filters={"tier": "premium"})
        assert len(premium_clients) == 2

    def test_update_client(self, test_config):
        """Test updating client information."""
        manager = ClientManager(test_config)
        manager.create("acme-corp", name="Acme Corp")

        updated = manager.update("acme-corp", name="Acme Corporation")

        assert updated.name == "Acme Corporation"

    def test_delete_client(self, test_config):
        """Test deleting a client."""
        manager = ClientManager(test_config)
        manager.create("acme-corp", name="Acme Corp")

        result = manager.delete("acme-corp")
        assert result is True

        with pytest.raises(ClientNotFoundError):
            manager.get_client("acme-corp")

    def test_onboard_client(self, test_config):
        """Test client onboarding workflow."""
        manager = ClientManager(test_config)
        manager.create("acme-corp", name="Acme Corp")

        result = manager.onboard("acme-corp", template="standard-business")

        assert result["status"] == "completed"
        assert "steps_completed" in result
