"""
System metrics collection utilities.

Provides lightweight wrappers around psutil for CPU, memory, and disk usage.
Falls back to standard library where possible.
"""

from __future__ import annotations

import shutil

try:
    import psutil
except ImportError:  # pragma: no cover - exercised in runtime environments
    psutil = None  # type: ignore[arg-type]


class SystemMetrics:
    """Collects basic system resource metrics."""

    def __init__(self, disk_path: str = "/") -> None:
        self.disk_path = disk_path

    def cpu_percent(self) -> float:
        """Return CPU utilization percentage."""
        if psutil:
            return float(psutil.cpu_percent(interval=0.1))
        return 0.0

    def memory_percent(self) -> float:
        """Return memory utilization percentage."""
        if psutil:
            return float(psutil.virtual_memory().percent)
        return 0.0

    def disk_percent(self) -> float:
        """Return disk utilization percentage for the configured path."""
        if psutil:
            return float(psutil.disk_usage(self.disk_path).percent)
        usage = shutil.disk_usage(self.disk_path)
        return (usage.used / usage.total) * 100 if usage.total else 0.0
