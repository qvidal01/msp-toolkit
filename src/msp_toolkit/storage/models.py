"""SQLAlchemy models for persistence."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import JSON, Column, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from msp_toolkit.storage.db import Base


class ClientRecord(Base):
    __tablename__ = "clients"

    id = Column(String(100), primary_key=True)
    name = Column(String(255), nullable=False)
    contact_email = Column(String(255), nullable=True)
    tier = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False)
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    devices = relationship("DeviceRecord", back_populates="client", cascade="all, delete-orphan")
    health_checks = relationship(
        "HealthCheckRecord",
        back_populates="client",
        cascade="all, delete-orphan",
    )


class DeviceRecord(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    client_id = Column(String(100), ForeignKey("clients.id"), nullable=False)
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False, default="workstation")
    rmm_device_id = Column(String(255), nullable=True)
    last_seen = Column(DateTime(timezone=True), nullable=True)
    metadata_json = Column(JSON, default=dict)

    client = relationship("ClientRecord", back_populates="devices")


class HealthCheckRecord(Base):
    __tablename__ = "health_checks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    client_id = Column(String(100), ForeignKey("clients.id"), nullable=False, index=True)
    check_type = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False)
    message = Column(Text, nullable=False)
    value = Column(Float, nullable=True)
    threshold = Column(Float, nullable=True)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)

    client = relationship("ClientRecord", back_populates="health_checks")
