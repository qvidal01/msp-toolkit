"""
Data models for MSP Toolkit.

This module defines Pydantic models for type-safe data structures used
throughout the toolkit. All models include validation and serialization.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ClientTier(str, Enum):
    """Client service tier levels."""

    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PREMIUM = "premium"


class ClientStatus(str, Enum):
    """Client account status."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"


class Client(BaseModel):
    """
    Represents an MSP client.

    Attributes:
        id: Unique client identifier (lowercase with hyphens)
        name: Client company name
        contact_email: Primary contact email
        tier: Service tier level
        status: Current account status
        created_at: Account creation timestamp
        updated_at: Last update timestamp
        metadata: Additional custom fields
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    id: str = Field(..., pattern=r"^[a-z0-9-]+$", min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=255)
    contact_email: str | None = Field(None, pattern=r"^[^@]+@[^@]+\.[^@]+$")
    tier: ClientTier = ClientTier.BRONZE
    status: ClientStatus = ClientStatus.ACTIVE
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate client name doesn't contain forbidden characters."""
        forbidden_chars = ["<", ">", "&", ";", "|", "`", "$"]
        if any(char in v for char in forbidden_chars):
            raise ValueError(f"Name contains forbidden characters: {forbidden_chars}")
        return v


class HealthCheckType(str, Enum):
    """Types of health checks."""

    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    SERVICES = "services"
    NETWORK = "network"
    CUSTOM = "custom"


class HealthCheckStatus(str, Enum):
    """Health check result status."""

    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class CheckResult(BaseModel):
    """
    Result of a health check.

    Attributes:
        check_type: Type of check performed
        status: Result status
        message: Human-readable message
        value: Measured value (e.g., CPU percentage)
        threshold: Threshold that was checked
        timestamp: When check was performed
        data: Additional check-specific data
    """

    check_type: HealthCheckType
    status: HealthCheckStatus
    message: str
    value: float | None = None
    threshold: float | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    data: dict[str, Any] = Field(default_factory=dict)


class Device(BaseModel):
    """
    Represents a device managed for a client.

    Attributes:
        id: Unique device identifier
        client_id: Associated client ID
        name: Device name/hostname
        type: Device type (server, workstation, etc.)
        rmm_device_id: ID in RMM system
        last_seen: Last communication timestamp
        metadata: Additional device information
    """

    id: int | None = None
    client_id: str
    name: str
    type: str = "workstation"
    rmm_device_id: str | None = None
    last_seen: datetime | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ReportTemplate(str, Enum):
    """Available report templates."""

    MONTHLY_SUMMARY = "monthly-summary"
    HEALTH_REPORT = "health-report"
    SLA_COMPLIANCE = "sla-compliance"
    INCIDENT_SUMMARY = "incident-summary"


class ReportFormat(str, Enum):
    """Report output formats."""

    PDF = "pdf"
    HTML = "html"
    MARKDOWN = "markdown"


class Report(BaseModel):
    """
    Generated report metadata.

    Attributes:
        id: Unique report identifier
        client_id: Associated client ID
        template: Template used
        format: Output format
        generated_at: Generation timestamp
        file_path: Path to generated file
        data: Report data/content
    """

    id: int | None = None
    client_id: str
    template: ReportTemplate
    format: ReportFormat
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    file_path: str | None = None
    data: dict[str, Any] = Field(default_factory=dict)


class AlertSeverity(str, Enum):
    """Alert severity levels."""

    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class Alert(BaseModel):
    """
    System alert/notification.

    Attributes:
        id: Unique alert identifier
        client_id: Associated client ID
        severity: Alert severity
        message: Alert message
        acknowledged: Whether alert has been acknowledged
        created_at: Alert creation timestamp
        acknowledged_at: When alert was acknowledged
        metadata: Additional alert data
    """

    id: int | None = None
    client_id: str
    severity: AlertSeverity
    message: str
    acknowledged: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    acknowledged_at: datetime | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class HealthSummary(BaseModel):
    """
    Summary of health check results.

    Attributes:
        total_checks: Total number of checks performed
        healthy: Number of healthy checks
        warnings: Number of warning checks
        critical: Number of critical checks
        unknown: Number of unknown/failed checks
        last_check_time: Timestamp of last check
    """

    total_checks: int = 0
    healthy: int = 0
    warnings: int = 0
    critical: int = 0
    unknown: int = 0
    last_check_time: datetime | None = None
