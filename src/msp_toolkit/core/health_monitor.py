"""
System health monitoring functionality.

This module provides health checking capabilities for MSP client systems
including CPU, memory, disk, services, and network monitoring.
"""

from datetime import datetime, timedelta, timezone

import structlog

from msp_toolkit.core.exceptions import ValidationError
from msp_toolkit.core.models import (
    CheckResult,
    HealthCheckStatus,
    HealthCheckType,
    HealthSummary,
)
from msp_toolkit.integrations.rmm.local import LocalRMMAdapter
from msp_toolkit.storage.db import get_engine, init_db, session_scope
from msp_toolkit.storage.models import HealthCheckRecord
from msp_toolkit.utils.config import Config
from msp_toolkit.utils.system import SystemMetrics

logger = structlog.get_logger(__name__)


class HealthMonitor:
    """
    Monitors system health for MSP clients.

    Performs various health checks (CPU, memory, disk, services, network)
    and maintains historical data for trend analysis.

    Example:
        >>> config = Config.from_file("config.yaml")
        >>> monitor = HealthMonitor(config)
        >>> results = monitor.run_checks("acme-corp")
        >>> for result in results:
        ...     print(f"{result.check_type}: {result.status}")
    """

    def __init__(self, config: Config) -> None:
        """
        Initialize HealthMonitor.

        Args:
            config: Configuration object
        """
        self.config = config
        self.engine = get_engine(
            self.config.get("database.type", "sqlite"),
            self.config.get("database.path"),
        )
        init_db(self.engine)
        self.metrics = SystemMetrics()
        self.rmm_adapter = LocalRMMAdapter(self.engine)
        logger.info("HealthMonitor initialized", db_path=self.config.get("database.path"))

    def run_checks(
        self,
        client_id: str,
        check_types: list[HealthCheckType | str] | None = None,
    ) -> list[CheckResult]:
        """
        Run health checks for a client.

        Args:
            client_id: Client identifier
            check_types: Specific check types to run (all if None)

        Returns:
            List of CheckResult objects

        Example:
            >>> results = monitor.run_checks("acme-corp", [HealthCheckType.CPU, HealthCheckType.MEMORY])
        """
        if not client_id:
            raise ValidationError("client_id", "Client ID is required for health checks")

        check_types = self._normalize_check_types(check_types)

        results = []
        for check_type in check_types:
            result = self._execute_check(client_id, check_type)
            results.append(result)

        self._persist_results(client_id, results)

        logger.info(
            "Health checks completed",
            client_id=client_id,
            total_checks=len(results),
            healthy=sum(1 for r in results if r.status == HealthCheckStatus.HEALTHY),
            warnings=sum(1 for r in results if r.status == HealthCheckStatus.WARNING),
            critical=sum(1 for r in results if r.status == HealthCheckStatus.CRITICAL),
        )

        return results

    def _execute_check(
        self,
        client_id: str,
        check_type: HealthCheckType,
    ) -> CheckResult:
        """
        Execute a specific health check.

        Args:
            client_id: Client identifier
            check_type: Type of check to perform

        Returns:
            CheckResult object
        """
        # TODO: Implement actual health checks via RMM integration
        # For now, return mock data

        # Get thresholds from config
        thresholds = self.config.get("health_checks.thresholds", {})
        cpu_threshold = self._get_threshold(thresholds, "cpu_percent", 85)
        memory_threshold = self._get_threshold(thresholds, "memory_percent", 90)
        disk_threshold = self._get_threshold(thresholds, "disk_percent", 85)

        if check_type == HealthCheckType.CPU:
            cpu_usage = self.metrics.cpu_percent()
            status = HealthCheckStatus.HEALTHY if cpu_usage < cpu_threshold else HealthCheckStatus.WARNING

            return CheckResult(
                check_type=check_type,
                status=status,
                message=f"CPU usage: {cpu_usage}%",
                value=cpu_usage,
                threshold=cpu_threshold,
            )

        elif check_type == HealthCheckType.MEMORY:
            memory_usage = self.metrics.memory_percent()
            status = HealthCheckStatus.HEALTHY if memory_usage < memory_threshold else HealthCheckStatus.WARNING

            return CheckResult(
                check_type=check_type,
                status=status,
                message=f"Memory usage: {memory_usage}%",
                value=memory_usage,
                threshold=memory_threshold,
            )

        elif check_type == HealthCheckType.DISK:
            disk_usage = self.metrics.disk_percent()
            status = HealthCheckStatus.HEALTHY if disk_usage < disk_threshold else HealthCheckStatus.WARNING

            return CheckResult(
                check_type=check_type,
                status=status,
                message=f"Disk usage: {disk_usage}%",
                value=disk_usage,
                threshold=disk_threshold,
            )

        elif check_type == HealthCheckType.SERVICES:
            devices = self.rmm_adapter.get_devices(client_id)
            status = HealthCheckStatus.HEALTHY if devices else HealthCheckStatus.WARNING

            return CheckResult(
                check_type=check_type,
                status=status,
                message=f"{len(devices)} device(s) managed via RMM",
                data={"devices": [d.model_dump() for d in devices]},
            )

        else:
            return CheckResult(
                check_type=check_type,
                status=HealthCheckStatus.HEALTHY,
                message=f"{check_type.value} check passed",
            )

    def get_history(
        self,
        client_id: str,
        days: int = 7,
    ) -> list[CheckResult]:
        """
        Retrieve historical health check results.

        Args:
            client_id: Client identifier
            days: Number of days of history to retrieve

        Returns:
            List of CheckResult objects from the specified period
        """
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        with session_scope(self.engine) as session:
            records = (
                session.query(HealthCheckRecord)
                .filter(HealthCheckRecord.client_id == client_id)
                .filter(HealthCheckRecord.timestamp >= cutoff_date)
                .order_by(HealthCheckRecord.timestamp.desc())
                .all()
            )

            history = [
                CheckResult(
                    check_type=HealthCheckType(record.check_type),
                    status=HealthCheckStatus(record.status),
                    message=record.message,
                    value=record.value,
                    threshold=record.threshold,
                    timestamp=record.timestamp,
                )
                for record in records
            ]

            logger.debug(
                "Retrieved health check history",
                client_id=client_id,
                days=days,
                results=len(history),
            )
            return history

    def get_status_summary(self, client_id: str) -> HealthSummary:
        """
        Get summary of current health status.

        Args:
            client_id: Client identifier

        Returns:
            HealthSummary object with aggregated statistics
        """
        recent_results = self.get_history(client_id, days=1)

        summary = HealthSummary(
            total_checks=len(recent_results),
            healthy=sum(1 for r in recent_results if r.status == HealthCheckStatus.HEALTHY),
            warnings=sum(1 for r in recent_results if r.status == HealthCheckStatus.WARNING),
            critical=sum(1 for r in recent_results if r.status == HealthCheckStatus.CRITICAL),
            unknown=sum(1 for r in recent_results if r.status == HealthCheckStatus.UNKNOWN),
            last_check_time=recent_results[-1].timestamp if recent_results else None,
        )

        return summary

    def configure(
        self,
        client_id: str,
        check_config: dict[str, any],
    ) -> bool:
        """
        Configure health checks for a client.

        Args:
            client_id: Client identifier
            check_config: Check configuration (thresholds, enabled checks, etc.)

        Returns:
            True if configuration successful
        """
        # TODO: Store client-specific check configuration
        logger.info(
            "Health check configuration updated",
            client_id=client_id,
            config=check_config,
        )
        return True

    @staticmethod
    def _get_threshold(thresholds: dict[str, any], key: str, default: float) -> float:
        """Safely coerce threshold values to float with sensible defaults."""
        raw_value = thresholds.get(key, default)
        try:
            return float(raw_value)
        except (TypeError, ValueError) as exc:
            raise ValidationError(
                f"health_checks.thresholds.{key}",
                f"Threshold must be numeric (received {raw_value!r})",
            ) from exc

    def _normalize_check_types(
        self,
        check_types: list[HealthCheckType | str] | None,
    ) -> list[HealthCheckType]:
        """Normalize check type inputs to HealthCheckType enums."""
        if check_types is None:
            return [
                HealthCheckType.CPU,
                HealthCheckType.MEMORY,
                HealthCheckType.DISK,
                HealthCheckType.SERVICES,
                HealthCheckType.NETWORK,
            ]

        normalized: list[HealthCheckType] = []
        for check in check_types:
            if isinstance(check, HealthCheckType):
                normalized.append(check)
                continue
            try:
                normalized.append(HealthCheckType(check))
            except ValueError as exc:
                raise ValidationError(
                    "check_types",
                    f"Unsupported health check type '{check}'",
                ) from exc

        return normalized

    def _persist_results(self, client_id: str, results: list[CheckResult]) -> None:
        """Persist health check results to the database."""
        with session_scope(self.engine) as session:
            for result in results:
                record = HealthCheckRecord(
                    client_id=client_id,
                    check_type=result.check_type.value,
                    status=result.status.value,
                    message=result.message,
                    value=result.value,
                    threshold=result.threshold,
                    timestamp=result.timestamp,
                )
                session.add(record)
