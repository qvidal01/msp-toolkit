"""
Custom exceptions for MSP Toolkit.

This module defines the exception hierarchy used throughout the toolkit.
All exceptions inherit from MSPToolkitError for easy catching.
"""

from typing import Any, Dict, Optional


class MSPToolkitError(Exception):
    """Base exception for all MSP Toolkit errors."""

    def __init__(
        self,
        message: str,
        code: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialize MSPToolkitError.

        Args:
            message: Human-readable error message
            code: Machine-readable error code (e.g., "CLIENT_NOT_FOUND")
            details: Additional context about the error
        """
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for serialization."""
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details,
            }
        }


class ClientNotFoundError(MSPToolkitError):
    """Raised when a client cannot be found."""

    def __init__(self, client_id: str) -> None:
        super().__init__(
            message=f"Client '{client_id}' not found",
            code="CLIENT_NOT_FOUND",
            details={"client_id": client_id},
        )


class ClientAlreadyExistsError(MSPToolkitError):
    """Raised when attempting to create a client that already exists."""

    def __init__(self, client_id: str) -> None:
        super().__init__(
            message=f"Client '{client_id}' already exists",
            code="CLIENT_ALREADY_EXISTS",
            details={"client_id": client_id},
        )


class ConfigurationError(MSPToolkitError):
    """Raised when configuration is invalid or missing."""

    def __init__(self, message: str, config_key: Optional[str] = None) -> None:
        details = {"config_key": config_key} if config_key else {}
        super().__init__(
            message=message,
            code="CONFIGURATION_ERROR",
            details=details,
        )


class IntegrationError(MSPToolkitError):
    """Raised when an integration (RMM, backup, etc.) fails."""

    def __init__(
        self,
        integration: str,
        message: str,
        original_error: Optional[Exception] = None,
    ) -> None:
        details = {"integration": integration}
        if original_error:
            details["original_error"] = str(original_error)
        super().__init__(
            message=f"{integration} integration error: {message}",
            code="INTEGRATION_ERROR",
            details=details,
        )


class AuthenticationError(MSPToolkitError):
    """Raised when authentication fails."""

    def __init__(self, service: str, message: str = "Authentication failed") -> None:
        super().__init__(
            message=f"{service}: {message}",
            code="AUTHENTICATION_ERROR",
            details={"service": service},
        )


class ValidationError(MSPToolkitError):
    """Raised when input validation fails."""

    def __init__(self, field: str, message: str) -> None:
        super().__init__(
            message=f"Validation error for '{field}': {message}",
            code="VALIDATION_ERROR",
            details={"field": field},
        )


class RateLimitExceededError(MSPToolkitError):
    """Raised when rate limit is exceeded."""

    def __init__(self, service: str, retry_after: Optional[int] = None) -> None:
        details = {"service": service}
        if retry_after:
            details["retry_after_seconds"] = retry_after
        super().__init__(
            message=f"Rate limit exceeded for {service}",
            code="RATE_LIMIT_EXCEEDED",
            details=details,
        )
