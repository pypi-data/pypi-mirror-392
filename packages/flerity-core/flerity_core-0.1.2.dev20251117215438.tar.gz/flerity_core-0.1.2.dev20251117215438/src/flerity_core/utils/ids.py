"""
Production-ready identifier generation utilities for Flerity backend services.

Provides safe, URL-friendly identifiers for requests, correlations, entities, and nonces.
Zero external dependencies, deterministic behavior.
"""

import base64
import os
import re
import secrets
import uuid
from collections.abc import Mapping

# Initialize APP_NAMESPACE from environment or generate new one
_app_namespace_str = os.environ.get("APP_NAMESPACE_UUID")
if _app_namespace_str:
    try:
        APP_NAMESPACE = uuid.UUID(_app_namespace_str)
    except ValueError:
        APP_NAMESPACE = uuid.uuid4()
else:
    APP_NAMESPACE = uuid.uuid4()

# Header constants
HDR_REQUEST_ID = "X-Request-Id"
HDR_CORRELATION_ID = "X-Correlation-Id"

# Standard UUID namespaces
_STANDARD_NAMESPACES = {
    "dns": uuid.NAMESPACE_DNS,
    "url": uuid.NAMESPACE_URL,
    "oid": uuid.NAMESPACE_OID,
    "x500": uuid.NAMESPACE_X500,
    "app": APP_NAMESPACE,
}

# Regex for validating base64url strings
_B64URL_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")


def _b64url_encode(raw: bytes) -> str:
    """Encode bytes as base64url without padding."""
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def _b64url_decode(s: str) -> bytes:
    """Decode base64url string, tolerant of missing padding."""
    padding = 4 - (len(s) % 4)
    if padding != 4:
        s += "=" * padding
    return base64.urlsafe_b64decode(s)


def ensure_urlsafe(s: str) -> str:
    """Ensure string is URL-safe by replacing problematic characters."""
    return s.replace("+", "-").replace("/", "_").rstrip("=")


def new_uuid() -> str:
    """Generate a random UUIDv4 string."""
    return str(uuid.uuid4())


def new_uuid7_or_4() -> str:
    """Generate UUIDv7 if available (Python 3.12+), otherwise UUIDv4."""
    if hasattr(uuid, "uuid7"):
        return str(uuid.uuid7())
    return str(uuid.uuid4())


def is_uuid(value: str) -> bool:
    """Validate if string is a valid UUID (v4 or v7)."""
    try:
        # Check format first - must have hyphens in correct positions
        if len(value) != 36 or value.count('-') != 4:
            return False

        # Check hyphen positions
        if (value[8] != '-' or value[13] != '-' or
            value[18] != '-' or value[23] != '-'):
            return False

        parsed = uuid.UUID(value)
        return parsed.version in (4, 7)
    except (ValueError, AttributeError):
        return False


def uuid5_ns(namespace: str, name: str) -> str:
    """Generate deterministic UUIDv5 using namespace and name."""
    if namespace not in _STANDARD_NAMESPACES:
        raise ValueError(f"Unknown namespace: {namespace}. Supported: {list(_STANDARD_NAMESPACES.keys())}")

    ns_uuid = _STANDARD_NAMESPACES[namespace]
    return str(uuid.uuid5(ns_uuid, name))


def uuid5_app(name: str) -> str:
    """Generate deterministic UUIDv5 using APP_NAMESPACE."""
    return str(uuid.uuid5(APP_NAMESPACE, name))


def new_request_id(nbytes: int = 9) -> str:
    """Generate URL-safe, short base64url request ID."""
    if nbytes < 1 or nbytes > 64:
        raise ValueError("nbytes must be between 1 and 64")
    return _b64url_encode(secrets.token_bytes(nbytes))


def new_correlation_id() -> str:
    """Generate time-sortable correlation ID (UUIDv7 if available, else UUIDv4)."""
    return new_uuid7_or_4()


def normalize_request_id(value: str | None, *, min_len: int = 8, max_len: int = 64) -> str:
    """Validate and normalize request ID, generate new one if invalid."""
    if not value:
        return new_request_id()

    if len(value) < min_len or len(value) > max_len:
        return new_request_id()

    if not _B64URL_PATTERN.match(value):
        return new_request_id()

    return value


def new_nonce(nbytes: int = 16) -> str:
    """Generate cryptographically strong base64url nonce."""
    if nbytes < 1:
        raise ValueError("nbytes must be positive")
    return _b64url_encode(secrets.token_bytes(nbytes))


def short_id(nbytes: int = 9) -> str:
    """Generate short URL-safe ID (alias for new_request_id)."""
    return new_request_id(nbytes)


def pick_request_id(headers: Mapping[str, str] | None) -> str:
    """Extract and validate request ID from headers, generate new if invalid."""
    if not headers:
        return new_request_id()

    request_id = headers.get(HDR_REQUEST_ID)
    return normalize_request_id(request_id)


def pick_correlation_id(headers: Mapping[str, str] | None) -> str:
    """Extract and validate correlation ID from headers, generate new if invalid."""
    if not headers:
        return new_correlation_id()

    correlation_id = headers.get(HDR_CORRELATION_ID)
    if not correlation_id:
        return new_correlation_id()

    # Accept UUIDs (v4/v7) or base64url strings (8-64 chars)
    if is_uuid(correlation_id):
        return correlation_id

    if (isinstance(correlation_id, str) and
        8 <= len(correlation_id) <= 64 and
        _B64URL_PATTERN.match(correlation_id)):
        return correlation_id

    return new_correlation_id()
