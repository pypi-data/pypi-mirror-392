"""
Production-ready JSON utilities for Flerity backend services.

Provides deterministic serialization, safe logging with PII redaction,
and canonical hashing for idempotency keys.
"""

from __future__ import annotations

import base64
import hashlib
import json
import re
from collections.abc import Callable
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any
from uuid import UUID

# Default keys to redact in logs (case-insensitive)
_DEFAULT_REDACT_KEYS = {
    "password", "pass", "secret", "token", "access_token", "refresh_token",
    "authorization", "api_key", "session", "cookie", "set-cookie"
}

# Control chars to strip (except \t\r\n)
_CONTROL_CHARS_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def default_encoder(o: Any) -> Any:
    """Default JSON encoder for common Python types."""
    if isinstance(o, datetime):
        # Aware datetime -> ISO with Z for UTC, naive treated as UTC
        iso = o.isoformat()
        if o.tzinfo is not None:
            if iso.endswith("+00:00"):
                iso = iso[:-6] + "Z"
        else:
            iso += "Z"
        return iso
    elif isinstance(o, date):
        return o.isoformat()
    elif isinstance(o, UUID):
        return str(o)
    elif isinstance(o, Enum):
        try:
            json.dumps(o.value)  # Test if value is JSON-serializable
            return o.value
        except (TypeError, ValueError):
            return str(o)
    elif isinstance(o, Decimal):
        return str(o)
    elif isinstance(o, (bytes, bytearray)):
        return base64.urlsafe_b64encode(o).decode().rstrip("=")
    elif isinstance(o, (set, frozenset)):
        return sorted(list(o), key=lambda x: (type(x).__name__, x))
    else:
        raise TypeError(f"Object of type {type(o).__name__} is not JSON serializable")


def dumps(
    obj: Any,
    *,
    sort_keys: bool = True,
    separators: tuple[str, str] = (",", ":"),
    ensure_ascii: bool = False,
    default: Callable[[Any], Any] | None = None
) -> str:
    """Deterministic JSON serialization with stable ordering."""
    return json.dumps(
        obj,
        sort_keys=sort_keys,
        separators=separators,
        ensure_ascii=ensure_ascii,
        default=default or default_encoder
    )


def pretty_dumps(
    obj: Any,
    *,
    indent: int = 2,
    sort_keys: bool = True,
    ensure_ascii: bool = False
) -> str:
    """Human-readable deterministic JSON with indentation."""
    return json.dumps(
        obj,
        indent=indent,
        sort_keys=sort_keys,
        ensure_ascii=ensure_ascii,
        default=default_encoder
    )


def canonical_dumps(obj: Any) -> str:
    """Strict canonical form for hashing - byte-for-byte stable."""
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=default_encoder
    )


def loads(s: str | bytes, *, max_bytes: int | None = None) -> Any:
    """Parse JSON safely with optional size limit."""
    if isinstance(s, bytes):
        s = s.decode("utf-8", errors="strict")

    if max_bytes is not None and len(s.encode("utf-8")) > max_bytes:
        raise ValueError(f"Input exceeds max_bytes limit of {max_bytes}")

    return json.loads(s)


def canonical_hash(obj: Any, *, algo: str = "sha256") -> str:
    """Hash of canonical JSON representation."""
    try:
        hasher = hashlib.new(algo)
    except ValueError:
        raise ValueError(f"Unsupported hash algorithm: {algo}")

    canonical_json = canonical_dumps(obj)
    hasher.update(canonical_json.encode("utf-8"))
    return hasher.hexdigest()


def redact(
    obj: Any,
    *,
    redact_keys: set[str] | None = None,
    mask: str = "*****"
) -> Any:
    """Recursively redact sensitive values by key name (case-insensitive)."""
    if redact_keys is None:
        redact_keys = _DEFAULT_REDACT_KEYS

    # Convert to lowercase for case-insensitive matching
    redact_keys_lower = {k.lower() for k in redact_keys}

    def _redact_recursive(obj: Any) -> Any:
        if isinstance(obj, dict):
            return {
                k: mask if k.lower() in redact_keys_lower else _redact_recursive(v)
                for k, v in obj.items()
            }
        elif isinstance(obj, list):
            return [_redact_recursive(item) for item in obj]
        elif isinstance(obj, tuple):
            return tuple(_redact_recursive(item) for item in obj)
        else:
            return obj

    return _redact_recursive(obj)


def strip_control_chars(s: str) -> str:
    """Remove ASCII control characters except \\t\\r\\n."""
    return _CONTROL_CHARS_RE.sub("", s)


def log_dumps(
    obj: Any,
    *,
    redact_keys: set[str] | None = None,
    max_len: int = 10000
) -> str:
    """Safe JSON for logs with redaction and truncation."""
    redacted_obj = redact(obj, redact_keys=redact_keys)
    json_str = dumps(redacted_obj)
    clean_str = strip_control_chars(json_str)

    if len(clean_str) > max_len:
        return clean_str[:max_len] + "...(truncated)"

    return clean_str


def is_probably_base64url(s: str) -> bool:
    """Check if string looks like base64url encoding."""
    if not s:
        return False

    # Base64url uses A-Z, a-z, 0-9, -, _
    if not re.match(r"^[A-Za-z0-9_-]+$", s):
        return False

    # Should be reasonable length for base64
    return len(s) >= 4
