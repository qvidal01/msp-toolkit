"""
Local RMM adapter backed by the toolkit database.

This adapter is intended for development and demo environments where
devices are tracked locally via SQLite rather than a remote RMM.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select

from msp_toolkit.core.models import Device
from msp_toolkit.integrations.rmm.base import RMMAdapter
from msp_toolkit.storage.db import session_scope
from msp_toolkit.storage.models import DeviceRecord


class LocalRMMAdapter(RMMAdapter):
    """Implements the RMM adapter interface using local persistence."""

    def get_devices(self, client_id: str) -> list[Device]:
        with session_scope(self.engine) as session:
            records = session.execute(
                select(DeviceRecord).where(DeviceRecord.client_id == client_id)
            ).scalars().all()
            return [
                Device(
                    id=record.id,
                    client_id=record.client_id,
                    name=record.name,
                    type=record.type,
                    rmm_device_id=record.rmm_device_id,
                    last_seen=record.last_seen,
                    metadata=record.metadata_json or {},
                )
                for record in records
            ]

    def deploy_agent(self, device_id: str, **device_attrs: Any) -> dict[str, Any]:
        """
        Register a device for a client.

        device_id should be formatted as "{client_id}:{device_name}".
        """
        try:
            client_id, device_name = device_id.split(":", 1)
        except ValueError:
            raise ValueError("device_id must be formatted as 'client_id:device_name'")

        with session_scope(self.engine) as session:
            record = DeviceRecord(
                client_id=client_id,
                name=device_name,
                type=device_attrs.get("type", "workstation"),
                rmm_device_id=device_attrs.get("rmm_device_id"),
                last_seen=device_attrs.get("last_seen", datetime.now(timezone.utc)),
                metadata_json=device_attrs.get("metadata", {}),
            )
            session.add(record)
            session.flush()

            return {
                "status": "registered",
                "device_id": record.id,
                "client_id": client_id,
                "name": device_name,
            }

    def execute_command(self, device_id: str, command: str) -> dict[str, Any]:
        # For local adapter we don't execute arbitrary commands for safety.
        return {
            "status": "unsupported",
            "message": "Command execution is disabled for LocalRMMAdapter",
        }

    def get_alerts(self, client_id: str, since: datetime) -> list[dict[str, Any]]:
        # Local adapter does not surface alerts; return empty list for now.
        return []

    def __init__(self, engine) -> None:
        super().__init__({"type": "local"})
        self.engine = engine
