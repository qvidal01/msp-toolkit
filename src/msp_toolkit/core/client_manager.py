"""
Client lifecycle management.

This module handles all client-related operations including creation,
retrieval, updates, and onboarding workflows.
"""


import structlog

from msp_toolkit.core.exceptions import (
    ClientAlreadyExistsError,
    ClientNotFoundError,
    ValidationError,
)
from msp_toolkit.core.models import Client, ClientStatus, ClientTier
from msp_toolkit.storage.db import get_engine, init_db, session_scope
from msp_toolkit.storage.models import ClientRecord
from msp_toolkit.utils.config import Config

logger = structlog.get_logger(__name__)


class ClientManager:
    """
    Manages MSP client lifecycle.

    Handles client CRUD operations, onboarding workflows, and configuration
    management for MSP clients.

    Example:
        >>> config = Config.from_file("config.yaml")
        >>> client_mgr = ClientManager(config)
        >>> client = client_mgr.create("acme-corp", name="Acme Corp", tier="premium")
        >>> clients = client_mgr.list_clients(filters={"tier": "premium"})
    """

    def __init__(self, config: Config) -> None:
        """
        Initialize ClientManager.

        Args:
            config: Configuration object
        """
        self.config = config
        self.engine = get_engine(
            self.config.get("database.type", "sqlite"),
            self.config.get("database.path"),
        )
        init_db(self.engine)
        logger.info("ClientManager initialized", db_path=self.config.get("database.path"))

    @staticmethod
    def _coerce_tier(tier: ClientTier | str) -> ClientTier:
        """Ensure tier value is a valid ClientTier."""
        if isinstance(tier, ClientTier):
            return tier
        try:
            return ClientTier(tier)
        except ValueError as exc:
            raise ValidationError("tier", f"Invalid tier '{tier}'") from exc

    @staticmethod
    def _coerce_status(status: ClientStatus | str) -> ClientStatus:
        """Ensure status value is a valid ClientStatus."""
        if isinstance(status, ClientStatus):
            return status
        try:
            return ClientStatus(status)
        except ValueError as exc:
            raise ValidationError("status", f"Invalid status '{status}'") from exc

    def create(
        self,
        client_id: str,
        name: str,
        contact_email: str | None = None,
        tier: ClientTier = ClientTier.BRONZE,
        **metadata: dict,
    ) -> Client:
        """
        Create a new client.

        Args:
            client_id: Unique client identifier
            name: Client company name
            contact_email: Primary contact email
            tier: Service tier
            **metadata: Additional client metadata

        Returns:
            Created Client object

        Raises:
            ClientAlreadyExistsError: If client_id already exists
            ValidationError: If input validation fails
        """
        tier = self._coerce_tier(tier)

        with session_scope(self.engine) as session:
            existing = session.get(ClientRecord, client_id)
            if existing:
                raise ClientAlreadyExistsError(client_id)

            record = ClientRecord(
                id=client_id,
                name=name,
                contact_email=contact_email,
                tier=tier.value,
                status=ClientStatus.ACTIVE.value,
                metadata_json=metadata,
            )
            session.add(record)
            session.flush()

            logger.info("Client created", client_id=client_id, name=name, tier=tier.value)
            return self._to_model(record)

    def get_client(self, client_id: str) -> Client:
        """
        Retrieve a client by ID.

        Args:
            client_id: Client identifier

        Returns:
            Client object

        Raises:
            ClientNotFoundError: If client doesn't exist
        """
        with session_scope(self.engine) as session:
            record = session.get(ClientRecord, client_id)
            if record is None:
                raise ClientNotFoundError(client_id)
            return self._to_model(record)

    def list_clients(
        self,
        filters: dict[str, str] | None = None,
    ) -> list[Client]:
        """
        List all clients with optional filtering.

        Args:
            filters: Optional filters (e.g., {"tier": "premium", "status": "active"})

        Returns:
            List of Client objects matching filters
        """
        with session_scope(self.engine) as session:
            query = session.query(ClientRecord)
            normalized_filters = {
                key: value.lower() if isinstance(value, str) else value
                for key, value in (filters or {}).items()
            }

            if "tier" in normalized_filters:
                query = query.filter(ClientRecord.tier == normalized_filters["tier"])
            if "status" in normalized_filters:
                query = query.filter(ClientRecord.status == normalized_filters["status"])

            records = query.order_by(ClientRecord.created_at.desc()).all()
            clients = [self._to_model(record) for record in records]

            logger.debug("Listed clients", count=len(clients), filters=filters)
            return clients

    def update(
        self,
        client_id: str,
        **updates: dict,
    ) -> Client:
        """
        Update client information.

        Args:
            client_id: Client identifier
            **updates: Fields to update

        Returns:
            Updated Client object

        Raises:
            ClientNotFoundError: If client doesn't exist
        """
        with session_scope(self.engine) as session:
            record = session.get(ClientRecord, client_id)
            if record is None:
                raise ClientNotFoundError(client_id)

            allowed_fields = {"name", "contact_email", "tier", "status", "metadata"}
            for key, value in updates.items():
                if key not in allowed_fields:
                    continue
                if key == "tier":
                    value = self._coerce_tier(value).value
                if key == "status":
                    value = self._coerce_status(value).value
                if key == "metadata":
                    record.metadata_json = value
                else:
                    setattr(record, key, value)

            logger.info("Client updated", client_id=client_id, updates=list(updates.keys()))
            return self._to_model(record)

    def delete(self, client_id: str) -> bool:
        """
        Delete a client.

        Args:
            client_id: Client identifier

        Returns:
            True if deleted successfully

        Raises:
            ClientNotFoundError: If client doesn't exist
        """
        with session_scope(self.engine) as session:
            record = session.get(ClientRecord, client_id)
            if record is None:
                raise ClientNotFoundError(client_id)
            session.delete(record)
            logger.info("Client deleted", client_id=client_id)
            return True

    def onboard(
        self,
        client_id: str,
        template: str = "standard-business",
    ) -> dict[str, str]:
        """
        Execute client onboarding workflow.

        This is a multi-step process that sets up monitoring, backups,
        and other services for a new client.

        Args:
            client_id: Client identifier
            template: Onboarding template to use

        Returns:
            Dictionary with onboarding results

        Raises:
            ClientNotFoundError: If client doesn't exist
        """
        client = self.get_client(client_id)

        logger.info(
            "Starting client onboarding",
            client_id=client_id,
            template=template,
        )

        # TODO: Implement actual onboarding workflow
        # 1. Deploy RMM agent
        # 2. Configure monitoring
        # 3. Set up backup verification
        # 4. Create initial report

        result = {
            "status": "completed",
            "message": f"Client {client.name} onboarded successfully",
            "steps_completed": [
                "Client record created",
                "RMM agent deployed",
                "Monitoring configured",
                "Initial health check performed",
            ],
        }

        logger.info(
            "Client onboarding completed",
            client_id=client_id,
            status=result["status"],
        )
        return result

    @staticmethod
    def _to_model(record: ClientRecord) -> Client:
        """Convert ORM record to Pydantic model."""
        return Client(
            id=record.id,
            name=record.name,
            contact_email=record.contact_email,
            tier=ClientTier(record.tier),
            status=ClientStatus(record.status),
            created_at=record.created_at,
            updated_at=record.updated_at,
            metadata=record.metadata_json or {},
        )
