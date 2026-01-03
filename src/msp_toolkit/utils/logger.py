"""
Logging configuration and utilities.

This module sets up structured logging using structlog with proper
formatting and sanitization of sensitive data.
"""

import logging
import sys

import structlog


def setup_logging(level: str = "INFO") -> None:
    """
    Configure structured logging for the application.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level.upper(), logging.INFO),
    )

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            _sanitize_processor,
            structlog.dev.ConsoleRenderer() if sys.stdout.isatty()
            else structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, level.upper(), logging.INFO)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=False,
    )


def _sanitize_processor(logger, method_name, event_dict):
    """
    Sanitize sensitive data from logs.

    Masks values for keys containing 'password', 'key', 'secret', 'token'.
    """
    sensitive_keys = {'password', 'key', 'secret', 'token', 'credential'}

    def mask_value(key, value):
        if any(sensitive in key.lower() for sensitive in sensitive_keys):
            if isinstance(value, str) and value:
                return "*" * min(len(value), 8)
        return value

    # Recursively sanitize nested dictionaries
    def sanitize_dict(d):
        if not isinstance(d, dict):
            return d

        sanitized = {}
        for k, v in d.items():
            if isinstance(v, dict):
                sanitized[k] = sanitize_dict(v)
            elif isinstance(v, list):
                sanitized[k] = [sanitize_dict(item) if isinstance(item, dict) else mask_value(k, item) for item in v]
            else:
                sanitized[k] = mask_value(k, v)
        return sanitized

    return sanitize_dict(event_dict)
