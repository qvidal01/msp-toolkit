"""
Device lifecycle management.

Provides CRUD operations for devices backed by SQLite via SQLAlchemy.
"""

from __future__ import annotations

from datetime import datetime, timezone

import structlog

from msp_toolkit.core.exceptions import ClientNotFoundError, MSPToolkitError
from msp_toolkit.core.models import Device
from msp_toolkit.storage.db import get_engine, init_db, session_scope
from msp_toolkit.storage.models import ClientRecord, DeviceRecord
from msp_toolkit.utils.config import Config

logger = structlog.get_logger(__name__)


class DeviceManager:
    """Manages devices for clients."""

    def __init__(self, config: Config) -> None:
        self.config = config
        self.engine = get_engine(
            self.config.get("database.type", "sqlite"),
            self.config.get("database.path"),
        )
        init_db(self.engine)
        logger.info("DeviceManager initialized", db_path=self.config.get("database.path"))

    def list_devices(self, client_id: str | None = None) -> list[Device]:
        """List devices optionally filtered by client."""
        with session_scope(self.engine) as session:
            query = session.query(DeviceRecord)
            if client_id:
                query = query.filter(DeviceRecord.client_id == client_id)
            records = query.order_by(DeviceRecord.id.asc()).all()
            return [self._to_model(r) for r in records]

    def add_device(
        self,
        client_id: str,
        name: str,
        type: str = "workstation",
        rmm_device_id: str | None = None,
        metadata: dict | None = None,
    ) -> Device:
        """Add/register a device for a client."""
        with session_scope(self.engine) as session:
            client = session.get(ClientRecord, client_id)
            if client is None:
                raise ClientNotFoundError(client_id)

            record = DeviceRecord(
                client_id=client_id,
                name=name,
                type=type,
                rmm_device_id=rmm_device_id,
                last_seen=datetime.now(timezone.utc),
                metadata_json=metadata or {},
            )
            session.add(record)
            session.flush()

            logger.info("Device added", client_id=client_id, device_id=record.id, name=name)
            return self._to_model(record)

    def delete_device(self, device_id: int) -> bool:
        """Delete a device by ID."""
        with session_scope(self.engine) as session:
            record = session.get(DeviceRecord, device_id)
            if record is None:
                raise MSPToolkitError(
                    message=f"Device '{device_id}' not found",
                    code="DEVICE_NOT_FOUND",
                    details={"device_id": device_id},
                )
            session.delete(record)
            logger.info("Device deleted", device_id=device_id, client_id=record.client_id)
            return True

    @staticmethod
    def _to_model(record: DeviceRecord) -> Device:
        """Convert ORM record to Pydantic model."""
        return Device(
            id=record.id,
            client_id=record.client_id,
            name=record.name,
            type=record.type,
            rmm_device_id=record.rmm_device_id,
            last_seen=record.last_seen,
            metadata=record.metadata_json or {},
        )
