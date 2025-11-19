"""
Security utilities for credential management and encryption.

This module provides secure credential storage and retrieval using
OS keyring and environment variables.
"""

import os
from typing import Optional

import keyring
import structlog

from msp_toolkit.core.exceptions import ConfigurationError


logger = structlog.get_logger(__name__)


class CredentialManager:
    """
    Secure credential storage and retrieval.

    Uses OS keyring for local development and environment variables
    for production deployments.

    Example:
        >>> cred_mgr = CredentialManager()
        >>> api_key = cred_mgr.get_credential("rmm", "api_key")
        >>> cred_mgr.set_credential("rmm", "api_key", "secret123")
    """

    def __init__(self, use_keyring: bool = True) -> None:
        """
        Initialize CredentialManager.

        Args:
            use_keyring: Whether to use OS keyring (disable for CI/production)
        """
        self.use_keyring = use_keyring

    def get_credential(self, service: str, key: str) -> Optional[str]:
        """
        Retrieve credential from keyring or environment variable.

        Environment variables take precedence over keyring.
        Variable name format: {SERVICE}_{KEY} (uppercase).

        Args:
            service: Service name (e.g., "rmm", "backup")
            key: Credential key (e.g., "api_key", "password")

        Returns:
            Credential value or None if not found

        Example:
            >>> # Checks RMM_API_KEY env var, then OS keyring
            >>> api_key = cred_mgr.get_credential("rmm", "api_key")
        """
        # Try environment variable first (production)
        env_var = f"{service.upper()}_{key.upper()}"
        value = os.getenv(env_var)

        if value:
            logger.debug("Retrieved credential from environment", service=service, key=key)
            return value

        # Fall back to keyring (local development)
        if self.use_keyring:
            try:
                value = keyring.get_password(service, key)
                if value:
                    logger.debug("Retrieved credential from keyring", service=service, key=key)
                    return value
            except Exception as e:
                logger.warning(
                    "Failed to retrieve from keyring",
                    service=service,
                    key=key,
                    error=str(e),
                )

        logger.warning("Credential not found", service=service, key=key)
        return None

    def set_credential(self, service: str, key: str, value: str) -> None:
        """
        Store credential in OS keyring.

        Note: This only stores in keyring, not environment variables.
        For production, set environment variables directly.

        Args:
            service: Service name
            key: Credential key
            value: Credential value

        Raises:
            ConfigurationError: If keyring storage fails
        """
        if not self.use_keyring:
            raise ConfigurationError(
                "Keyring disabled. Set credentials via environment variables."
            )

        try:
            keyring.set_password(service, key, value)
            logger.info("Credential stored in keyring", service=service, key=key)
        except Exception as e:
            raise ConfigurationError(
                f"Failed to store credential: {e}",
                config_key=f"{service}.{key}",
            )

    def delete_credential(self, service: str, key: str) -> None:
        """
        Delete credential from OS keyring.

        Args:
            service: Service name
            key: Credential key
        """
        if not self.use_keyring:
            logger.warning("Keyring disabled, cannot delete credential")
            return

        try:
            keyring.delete_password(service, key)
            logger.info("Credential deleted from keyring", service=service, key=key)
        except keyring.errors.PasswordDeleteError:
            logger.warning("Credential not found in keyring", service=service, key=key)
        except Exception as e:
            logger.error("Failed to delete credential", service=service, key=key, error=str(e))
