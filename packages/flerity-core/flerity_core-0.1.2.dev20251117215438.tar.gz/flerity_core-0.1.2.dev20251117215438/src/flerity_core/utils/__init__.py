"""Shared utilities for the Flerity backend.

This package provides common utilities used across API, webhook, and worker services
including validation, tracing, logging, retry logic, and idempotency handling.
"""

from .logging import (
    SafeLogger,
    configure_json_logger,
    get_logger,
    get_safe_logger,
    log_event,
    log_exception,
    redact_pii,
    safe_log_error,
)

__all__ = [
    "SafeLogger",
    "configure_json_logger",
    "get_logger",
    "get_safe_logger",
    "log_event",
    "log_exception",
    "redact_pii",
    "safe_log_error",
]
