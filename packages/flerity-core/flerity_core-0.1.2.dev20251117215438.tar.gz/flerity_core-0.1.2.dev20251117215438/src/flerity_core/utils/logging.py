"""Structured JSON logging with request context, redaction, and framework integration.

Provides production-ready JSON logging with automatic context injection from tracing,
safe redaction of sensitive data, and optional uvicorn/gunicorn bridge.
"""

from __future__ import annotations

import io
import logging
import os
import sys
import traceback
from datetime import UTC, datetime
from typing import Any

# Default redaction keys (case-insensitive)
DEFAULT_REDACT_KEYS = {
    "password", "pass", "secret", "token", "access_token", "refresh_token",
    "authorization", "api_key", "session", "cookie", "set-cookie",
    "email", "phone", "cpf", "credit_card", "ssn", "private_key"
}

# Global redaction keys
_REDACT_KEYS = DEFAULT_REDACT_KEYS.copy()

# Formatter error guard
_formatter_error_logged = False


def set_redact_keys(keys: set[str]) -> None:
    """Override global redaction keys."""
    global _REDACT_KEYS
    _REDACT_KEYS = {k.lower() for k in keys}


def redact_pii(data: dict[str, Any]) -> dict[str, Any]:
    """Redact PII from log data recursively.
    
    Args:
        data: Dictionary containing potentially sensitive data
        
    Returns:
        Dictionary with sensitive keys redacted
    """
    sensitive_keys = {
        'email', 'password', 'token', 'secret', 'api_key',
        'phone', 'cpf', 'credit_card', 'ssn', 'access_token',
        'refresh_token', 'private_key', 'authorization'
    }
    
    def _redact_recursive(obj: Any) -> Any:
        if isinstance(obj, dict):
            return {
                k: '[REDACTED]' if k.lower() in sensitive_keys else _redact_recursive(v)
                for k, v in obj.items()
            }
        elif isinstance(obj, list):
            return [_redact_recursive(item) for item in obj]
        return obj
    
    return _redact_recursive(data)


def safe_log_error(
    logger: logging.Logger,
    message: str,
    error: Exception,
    **context: Any
) -> None:
    """Log errors without exposing sensitive data.
    
    Args:
        logger: Logger instance
        message: Error message
        error: Exception instance
        **context: Additional context (will be redacted)
    """
    safe_context = redact_pii({
        "error_type": type(error).__name__,
        "error_message": str(error)[:200],
        **context
    })
    logger.error(message, extra=safe_context, exc_info=error)


class SafeLogger:
    """Logger wrapper with automatic PII redaction."""
    
    def __init__(self, logger: logging.Logger, enable_redaction: bool = True):
        self._logger = logger
        self._enable_redaction = enable_redaction
    
    def _safe_extra(self, extra: dict[str, Any] | None) -> dict[str, Any]:
        if not extra or not self._enable_redaction:
            return extra or {}
        return redact_pii(extra)
    
    def debug(self, msg: str, extra: dict[str, Any] | None = None) -> None:
        self._logger.debug(msg, extra=self._safe_extra(extra))
    
    def info(self, msg: str, extra: dict[str, Any] | None = None) -> None:
        self._logger.info(msg, extra=self._safe_extra(extra))
    
    def warning(self, msg: str, extra: dict[str, Any] | None = None) -> None:
        self._logger.warning(msg, extra=self._safe_extra(extra))
    
    def error(self, msg: str, extra: dict[str, Any] | None = None, exc_info: Any = None) -> None:
        self._logger.error(msg, extra=self._safe_extra(extra), exc_info=exc_info)


def get_safe_logger(name: str) -> SafeLogger:
    """Get logger with automatic PII redaction based on environment."""
    try:
        from ..config import get_config
        config = get_config()
        enable_redaction = config.enable_pii_redaction
    except Exception:
        # Fallback to always enable in case config is not available
        enable_redaction = True
    
    logger = logging.getLogger(name)
    return SafeLogger(logger, enable_redaction=enable_redaction)


def _to_level(v: int | str) -> int:
    """Convert level string/int to logging level."""
    if isinstance(v, int):
        return v
    return getattr(logging, str(v).upper(), logging.INFO)


def _get_timestamp() -> str:
    """Get ISO8601 timestamp with Z suffix."""
    try:
        from .clock import to_iso8601, utcnow
        return to_iso8601(utcnow())
    except Exception:
        return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _get_context() -> dict[str, str]:
    """Get context from tracing module."""
    try:
        from .tracing import get_context
        return get_context()
    except Exception:
        return {}


def _safe_redact_and_dumps(data: dict[str, Any]) -> str:
    """Safely redact and serialize data to JSON."""
    try:
        from . import jsonx
        redacted = jsonx.redact(data, redact_keys=_REDACT_KEYS)
        return jsonx.dumps(redacted)
    except Exception:
        # Fallback to basic JSON without redaction
        import json
        try:
            return json.dumps(data, default=str, separators=(',', ':'))
        except Exception:
            return str(data)


def _strip_control_chars(s: str) -> str:
    """Strip control characters from string."""
    try:
        from . import jsonx
        return jsonx.strip_control_chars(s)
    except Exception:
        import re
        return re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', s)


def _truncate_large_field(value: str, max_chars: int = 100000) -> str:
    """Truncate large fields to prevent log explosion."""
    if len(value) > max_chars:
        return value[:max_chars] + "...(truncated)"
    return value


class JsonFormatter(logging.Formatter):
    """JSON formatter with context injection and redaction."""

    def __init__(self, app_name: str = "flerity", service: str | None = None, env: str | None = None):
        super().__init__()
        self.app_name = app_name
        self.service = service or app_name
        
        # Robust environment detection for production JSON logging
        if env:
            self.env = env
        else:
            # Check multiple environment variables
            env_var = (os.getenv("ENV") or 
                      os.getenv("ENVIRONMENT") or 
                      os.getenv("STAGE") or 
                      "development")
            self.env = env_var
            
        self.pid = os.getpid()
        self.version = os.getenv("APP_VERSION")

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        global _formatter_error_logged

        try:
            # Always use JSON format for all environments
            # Full JSON format
            payload = {
                    "ts": _get_timestamp(),
                    "lvl": record.levelname,
                    "msg": _strip_control_chars(record.getMessage()),
                    "logger": record.name,
                    "module": record.module,
                    "func": record.funcName,
                    "line": record.lineno,
                    "app": self.app_name,
                    "service": self.service,
                    "env": self.env,
                    "pid": self.pid,
                }

            # Add version if available
            if self.version:
                payload["version"] = self.version

            # Add context from tracing
            context = _get_context()
            payload.update(context)

            # Add exception info if present
            if record.exc_info:
                exc_type, exc_value, exc_tb = record.exc_info
                payload["exc"] = {
                    "type": exc_type.__name__ if exc_type else "Unknown",
                    "msg": str(exc_value) if exc_value else "",
                    "stack": _strip_control_chars(traceback.format_exception(exc_type, exc_value, exc_tb)[-1] if exc_tb else "")
                }

            # Add extra fields from record, avoiding reserved keys
            reserved_keys = {
                "ts", "lvl", "msg", "logger", "module", "func", "line",
                "app", "service", "env", "pid", "version", "exc",
                "request_id", "correlation_id", "user_id", "locale", "timezone",
                "message", "asctime"
            }

            extra = {}
            for key, value in record.__dict__.items():
                if (not key.startswith('_') and
                    key not in reserved_keys and
                    key not in {'name', 'levelno', 'levelname', 'pathname', 'filename',
                               'lineno', 'funcName', 'created', 'msecs', 'relativeCreated',
                               'thread', 'threadName', 'processName', 'process', 'module',
                               'exc_info', 'exc_text', 'stack_info', 'getMessage', 'args'}):
                    extra[key] = value

            if extra:
                payload["extra"] = extra

            # Serialize and truncate if needed
            result = _safe_redact_and_dumps(payload)
            return _truncate_large_field(result)

        except Exception as e:
            # Fallback to plain text on serialization failure
            if not _formatter_error_logged:
                _formatter_error_logged = True
                print(f"JsonFormatter error: {e}", file=sys.stderr)

            return f"{_get_timestamp()} ERROR {record.name} JsonFormatter failed: {record.getMessage()}"


class ContextFilter(logging.Filter):
    """Filter that injects context as record attributes."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Inject context into record attributes."""
        context = _get_context()
        for key, value in context.items():
            setattr(record, key, value)
        return True


def record_with_context(data: dict[str, Any] | None = None) -> dict[str, Any]:
    """Merge tracing context into data dict (non-destructive)."""
    result = data.copy() if data else {}
    context = _get_context()
    result.update(context)
    return result


def bind_extra(logger: logging.Logger, **kwargs: Any) -> logging.LoggerAdapter[logging.Logger]:
    """Return LoggerAdapter that always includes extra kwargs."""
    return logging.LoggerAdapter(logger, kwargs)


def configure_json_logger(
    *,
    level: int | str = "INFO",
    stream: io.TextIOBase | None = None,
    app_name: str = "flerity",
    service: str | None = None,
    env: str | None = None,
    include_uvicorn_bridge: bool = True
) -> None:
    """Configure root logger with JSON formatter and optional uvicorn bridge."""
    # Clear existing handlers to avoid duplicates
    root_logger = logging.getLogger()
    root_logger.handlers.clear()

    # Set level
    root_logger.setLevel(_to_level(level))

    # Create handler
    handler = logging.StreamHandler(stream or sys.stdout)
    handler.setLevel(_to_level(level))

    # Set JSON formatter
    formatter = JsonFormatter(app_name=app_name, service=service, env=env)
    handler.setFormatter(formatter)

    # Add context filter
    context_filter = ContextFilter()
    handler.addFilter(context_filter)

    # Add handler to root logger
    root_logger.addHandler(handler)

    # Configure uvicorn/gunicorn bridge
    if include_uvicorn_bridge:
        _configure_uvicorn_bridge(handler, formatter)


def _configure_uvicorn_bridge(handler: logging.Handler, formatter: JsonFormatter) -> None:
    """Configure uvicorn/gunicorn loggers to use our handler."""
    bridge_loggers = [
        "uvicorn",
        "uvicorn.access",
        "uvicorn.error",
        "gunicorn.error",
        "gunicorn.access"
    ]

    for logger_name in bridge_loggers:
        logger = logging.getLogger(logger_name)
        logger.handlers.clear()
        logger.propagate = True
        logger.setLevel(logging.INFO)

        # Special handling for access logs
        if "access" in logger_name:
            access_handler = logging.StreamHandler(sys.stdout)
            access_handler.setFormatter(UvicornAccessFormatter(formatter))
            logger.addHandler(access_handler)
            logger.propagate = False


class UvicornAccessFormatter(logging.Formatter):
    """Formatter for uvicorn access logs with structured fields."""

    def __init__(self, base_formatter: JsonFormatter):
        super().__init__()
        self.base_formatter = base_formatter

    def format(self, record: logging.LogRecord) -> str:
        """Format uvicorn access log as structured JSON."""
        try:
            # Extract access log fields from record
            access_fields = {}

            # Try to parse common uvicorn access log fields
            if hasattr(record, 'args') and record.args:
                try:
                    # Cast to tuple for indexing (record.args can be tuple or list)
                    args = tuple(record.args) if not isinstance(record.args, tuple) else record.args
                    # Uvicorn access logs typically have: client, method, path, http_version, status_code
                    if len(args) >= 5:
                        # Convert status_code safely
                        status_code = None
                        if args[4] is not None:
                            try:
                                # Convert object to int safely
                                status_code = int(str(args[4]))
                            except (ValueError, TypeError):
                                status_code = None

                        access_fields.update({
                            "event": "http_access",
                            "remote_addr": str(args[0]) if args[0] else None,
                            "method": str(args[1]) if args[1] else None,
                            "path": str(args[2]) if args[2] else None,
                            "http_version": str(args[3]) if args[3] else None,
                            "status_code": status_code,
                        })
                except (IndexError, ValueError, TypeError):
                    pass

            # Check for process_time in record dict
            if hasattr(record, 'process_time'):
                try:
                    access_fields["process_time_ms"] = int(float(record.process_time) * 1000)
                except (ValueError, TypeError):
                    pass

            # Add access fields to record
            for key, value in access_fields.items():
                if value is not None:
                    setattr(record, key, value)

            return self.base_formatter.format(record)

        except Exception:
            # Fallback to base formatter
            return self.base_formatter.format(record)


def get_logger(name: str | None = None) -> logging.Logger:
    """Get logger with JSON formatter already configured."""
    return logging.getLogger(name)


def log_exception(
    logger: logging.Logger,
    msg: str,
    *,
    extra: dict[str, Any] | None = None,
    exc: BaseException | None = None
) -> None:
    """Log exception at ERROR level with exc_info."""
    logger.error(msg, extra=extra, exc_info=exc or True)


def log_duration(
    logger: logging.Logger,
    msg: str,
    *,
    ms: float,
    extra: dict[str, Any] | None = None,
    level: int = logging.INFO
) -> None:
    """Log duration with timing information."""
    log_extra = {"duration_ms": ms}
    if extra:
        log_extra.update(extra)
    logger.log(level, msg, extra=log_extra)


def log_event(logger: logging.Logger, event: str, **fields: Any) -> None:
    """Log structured event with fields."""
    extra = {"event": event}
    extra.update(fields)
    logger.info(event, extra=extra)
