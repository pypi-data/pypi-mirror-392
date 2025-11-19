"""Fast, dependency-free input validation & normalization helpers.

Used by API, worker, and webhook services for consistent input handling.
All functions raise ValueError with clear messages on invalid input.
"""

from __future__ import annotations

import re
import uuid
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo


def is_uuid(val: str) -> bool:
    """Check if string is a valid UUID (v4/v7 canonical form)."""
    try:
        uuid.UUID(val)
        return True
    except (ValueError, TypeError):
        return False


def require_uuid(val: str, *, name: str = "id") -> str:
    """Validate and normalize UUID to lowercase canonical form."""
    try:
        u = uuid.UUID(val)
        return str(u).lower()
    except (ValueError, TypeError):
        raise ValueError(f"{name} must be a valid UUID, got: {safe_truncate(str(val), 50)}")


def normalize_enum(val: str, allowed: set[str], *, case_insensitive: bool = True, name: str = "value") -> str:
    """Normalize enum value, returning canonical casing from allowed set."""
    val = val.strip()
    if case_insensitive:
        val_lower = val.lower()
        for allowed_val in allowed:
            if allowed_val.lower() == val_lower:
                return allowed_val
    else:
        if val in allowed:
            return val

    raise ValueError(f"{name} must be one of {sorted(allowed)}, got: {safe_truncate(val, 50)}")


def require_one_of(val: str, choices: set[str], *, name: str = "value", case_insensitive: bool = True) -> str:
    """Alias of normalize_enum for readability at call sites."""
    return normalize_enum(val, choices, case_insensitive=case_insensitive, name=name)


def clamp_int(n: int | None, *, default: int, min_value: int, max_value: int) -> int:
    """Clamp integer to range, using default if None."""
    if n is None:
        n = default
    return max(min_value, min(max_value, n))


def require_range(n: int | float, *, min_value: float | int | None = None, max_value: float | int | None = None, name: str = "value") -> int | float:
    """Validate number is within specified range."""
    if min_value is not None and n < min_value:
        raise ValueError(f"{name} must be >= {min_value}, got: {n}")
    if max_value is not None and n > max_value:
        raise ValueError(f"{name} must be <= {max_value}, got: {n}")
    return n


def require_len(s: str, *, min_len: int = 0, max_len: int | None = None, name: str = "value") -> str:
    """Validate string length without trimming."""
    length = len(s)
    if length < min_len:
        raise ValueError(f"{name} must be at least {min_len} characters, got: {length}")
    if max_len is not None and length > max_len:
        raise ValueError(f"{name} must be at most {max_len} characters, got: {length}")
    return s


def require_non_empty(s: str, *, name: str = "value") -> str:
    """Validate string is not empty after stripping."""
    if not s.strip():
        raise ValueError(f"{name} cannot be empty")
    return s


def parse_bool(val: bool | int | str, *, name: str = "flag") -> bool:
    """Parse boolean from various formats (case-insensitive)."""
    if isinstance(val, bool):
        return val
    if isinstance(val, int):
        if val in (0, 1):
            return bool(val)
        raise ValueError(f"{name} must be 0 or 1, got: {val}")

    val_lower = str(val).lower().strip()
    if val_lower in ("true", "yes", "1"):
        return True
    if val_lower in ("false", "no", "0"):
        return False

    raise ValueError(f"{name} must be true/false/yes/no/1/0, got: {safe_truncate(str(val), 50)}")


def parse_int(val: int | str, *, name: str = "number") -> int:
    """Parse integer, rejecting floats and non-decimal formats."""
    if isinstance(val, int):
        return val

    try:
        # Reject floats, hex, scientific notation
        val_str = str(val).strip()
        if '.' in val_str or 'e' in val_str.lower() or 'x' in val_str.lower():
            raise ValueError()
        return int(val_str)
    except (ValueError, TypeError):
        raise ValueError(f"{name} must be a valid integer, got: {safe_truncate(str(val), 50)}")


def require_regex(s: str, pattern: str, *, flags: int = 0, name: str = "value") -> str:
    """Validate string matches regex pattern."""
    if not re.match(pattern, s, flags):
        raise ValueError(f"{name} format is invalid")
    return s


def is_slug(s: str) -> bool:
    """Check if string is a valid slug (lowercase alphanumeric with hyphens)."""
    return bool(re.match(r'^[a-z0-9]+(?:-[a-z0-9]+)*$', s))


def require_slug(s: str, *, name: str = "slug") -> str:
    """Validate string is a valid slug."""
    if not is_slug(s):
        raise ValueError(f"{name} must be lowercase alphanumeric with hyphens, got: {safe_truncate(s, 50)}")
    return s


def is_email(s: str) -> bool:
    """Check if string is a valid email (simple RFC-lite validation)."""
    return bool(re.match(r'^[^@\s]{1,64}@[^@\s]+\.[A-Za-z]{2,}$', s))


def require_email(s: str, *, name: str = "email") -> str:
    """Validate and normalize email (lowercase domain, preserve localpart)."""
    if not is_email(s):
        raise ValueError(f"{name} must be a valid email address")

    local, domain = s.rsplit('@', 1)
    return f"{local}@{domain.lower()}"


def normalize_locale(s: str, *, name: str = "locale") -> str:
    """Normalize locale to ll-CC format (e.g., pt-br -> pt-BR, en -> en)."""
    s = s.strip()
    if not re.match(r'^[a-zA-Z]{2}(?:[-_][a-zA-Z]{2})?$', s):
        raise ValueError(f"{name} must be in format 'll' or 'll-CC', got: {safe_truncate(s, 50)}")

    parts = re.split(r'[-_]', s)
    lang = parts[0].lower()

    if len(parts) == 1:
        return lang

    country = parts[1].upper()
    return f"{lang}-{country}"


def is_iana_tz(tz: str) -> bool:
    """Check if string is a valid IANA timezone."""
    try:
        ZoneInfo(tz)
        return True
    except Exception:
        return False


def require_iana_tz(tz: str, *, name: str = "timezone") -> str:
    """Validate IANA timezone string."""
    if not is_iana_tz(tz):
        raise ValueError(f"{name} must be a valid IANA timezone, got: {safe_truncate(tz, 50)}")
    return tz


def require_iso8601_datetime(s: str, *, name: str = "timestamp") -> str:
    """Validate and normalize ISO8601 datetime string."""
    try:
        # Try to import from project clock module
        from .clock import parse_iso8601, to_iso8601
        dt = parse_iso8601(s)
        return to_iso8601(dt)
    except ImportError:
        # Fallback to stdlib
        try:
            # Handle Z suffix
            normalized = s.replace('Z', '+00:00')
            dt = datetime.fromisoformat(normalized)
            return dt.isoformat()
        except ValueError:
            raise ValueError(f"{name} must be a valid ISO8601 datetime, got: {safe_truncate(s, 50)}")


def require_direction(s: str, *, name: str = "direction") -> str:
    """Validate and normalize sort direction to 'asc' or 'desc'."""
    direction = s.strip().lower()
    if direction in ("asc", "ascending"):
        return "asc"
    if direction in ("desc", "descending"):
        return "desc"

    raise ValueError(f"{name} must be 'asc' or 'desc', got: {safe_truncate(s, 50)}")


def require_limit(n: int | None, *, default: int = 20, min_value: int = 1, max_value: int = 100) -> int:
    """Validate and clamp pagination limit."""
    return clamp_int(n, default=default, min_value=min_value, max_value=max_value)


def require_uuid_list(values: list[str] | tuple[str, ...], *, name: str = "ids", unique: bool = True) -> list[str]:
    """Validate list of UUIDs, optionally deduplicating while preserving order."""
    if not isinstance(values, (list, tuple)):
        raise ValueError(f"{name} must be a list or tuple")

    result = []
    seen = set()

    for i, val in enumerate(values):
        try:
            normalized = require_uuid(val, name=f"{name}[{i}]")
            if unique:
                if normalized not in seen:
                    result.append(normalized)
                    seen.add(normalized)
            else:
                result.append(normalized)
        except ValueError as e:
            raise ValueError(str(e))

    return result


def require_list(values: object, *, name: str = "items", min_len: int = 0, max_len: int | None = None) -> list[Any]:
    """Validate object is a list/tuple and convert to list with length bounds."""
    if isinstance(values, tuple):
        values = list(values)
    elif not isinstance(values, list):
        raise ValueError(f"{name} must be a list or tuple")

    length = len(values)
    if length < min_len:
        raise ValueError(f"{name} must have at least {min_len} items, got: {length}")
    if max_len is not None and length > max_len:
        raise ValueError(f"{name} must have at most {max_len} items, got: {length}")

    return values


def strip_control_chars(s: str) -> str:
    """Remove ASCII control characters except tab, CR, LF."""
    return re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', s)


def safe_truncate(s: str, max_len: int) -> str:
    """Safely truncate string without breaking UTF-8 sequences."""
    if len(s) <= max_len:
        return s
    return s[:max_len] + "..."


def validate_uuid(value: str) -> bool:
    """Validate UUID format."""
    try:
        import uuid
        uuid.UUID(value)
        return True
    except (ValueError, TypeError):
        return False


def validate_enum(value: str, allowed_values: list[str]) -> bool:
    """Validate enum value."""
    return value in allowed_values
