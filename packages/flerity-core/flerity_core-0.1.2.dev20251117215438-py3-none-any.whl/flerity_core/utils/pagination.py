"""Secure cursor-based pagination utilities for Flerity backend services.

Provides opaque, tamper-resistant pagination cursors using HMAC signatures
and deterministic JSON encoding. Supports keyset pagination to avoid offset
enumeration vulnerabilities.

Security Features:
- HMAC-signed cursors prevent tampering
- TTL support prevents cursor reuse
- Base64url encoding without padding
- No raw sort values exposed in URLs
- Deterministic JSON serialization
"""

from __future__ import annotations

import base64
from collections.abc import Mapping, Sequence
from typing import Any, cast

from .clock import now_ms
from .crypto import hmac_sha256_b64url, verify_signature
from .jsonx import canonical_dumps, loads


def _b64url_encode(data: bytes) -> str:
    """Encode bytes as URL-safe base64 without padding."""
    return base64.urlsafe_b64encode(data).decode('ascii').rstrip('=')


def _b64url_decode(s: str) -> bytes:
    """Decode URL-safe base64 string, tolerant of missing padding."""
    padding = (-len(s)) % 4
    s_padded = s + ('=' * padding)
    return base64.urlsafe_b64decode(s_padded)


def encode_cursor(
    payload: Mapping[str, Any],
    *,
    secret: str | bytes | None = None,
    ttl_s: int | None = None
) -> str:
    """Encode pagination cursor as opaque, signed base64url token.
    
    Args:
        payload: JSON-serializable cursor data
        secret: Optional HMAC signing key
        ttl_s: Optional TTL in seconds
        
    Returns:
        Opaque base64url cursor token (no padding)
    """
    iat = now_ms()
    envelope = {"v": 1, "iat": iat, "data": payload}

    if ttl_s is not None:
        envelope["exp"] = iat + (ttl_s * 1000)

    if secret is not None:
        # Sign envelope without signature field
        sig = hmac_sha256_b64url(secret, canonical_dumps(envelope))
        envelope["sig"] = sig

    cursor_json = canonical_dumps(envelope)
    return _b64url_encode(cursor_json.encode('utf-8'))


def decode_cursor(
    cursor: str | None,
    *,
    secret: str | bytes | None = None,
    max_age_s: int | None = None
) -> dict[str, Any] | None:
    """Decode and validate pagination cursor.
    
    Args:
        cursor: Base64url cursor token or None
        secret: HMAC signing key (must match encode)
        max_age_s: Maximum age in seconds relative to iat
        
    Returns:
        Cursor payload data or None if cursor is None
        
    Raises:
        ValueError: If cursor is malformed, expired, or signature invalid
    """
    if cursor is None:
        return None

    try:
        cursor_bytes = _b64url_decode(cursor)
        envelope = loads(cursor_bytes.decode('utf-8'))

        if not isinstance(envelope, dict) or envelope.get("v") != 1:
            raise ValueError("Invalid cursor format")

        iat = envelope.get("iat")
        exp = envelope.get("exp")
        data = envelope.get("data")
        sig = envelope.get("sig")

        if not isinstance(iat, int) or data is None:
            raise ValueError("Missing required cursor fields")

        # Verify signature if secret provided
        if secret is not None:
            if sig is None:
                raise ValueError("Cursor missing signature")

            # Reconstruct envelope without signature for verification
            verify_envelope = {"v": 1, "iat": iat, "data": data}
            if exp is not None:
                verify_envelope["exp"] = exp

            if not verify_signature(secret, canonical_dumps(verify_envelope), sig):
                raise ValueError("Invalid cursor signature")

        current_time = now_ms()

        # Check expiration
        if exp is not None and current_time > exp:
            raise ValueError("Cursor expired")

        # Check max age
        if max_age_s is not None:
            max_age_ms = max_age_s * 1000
            if current_time > (iat + max_age_ms):
                raise ValueError("Cursor too old")

        return cast(dict[str, Any], data) if isinstance(data, dict) else None

    except (ValueError, KeyError, TypeError) as e:
        if isinstance(e, ValueError) and str(e).startswith(("Invalid cursor", "Cursor expired", "Cursor too old")):
            raise
        raise ValueError("Malformed cursor") from e


def clamp_limit(requested: int | None, *, default: int = 20, max_limit: int = 100) -> int:
    """Clamp pagination limit to safe bounds.
    
    Args:
        requested: Requested limit or None
        default: Default limit for None/invalid values
        max_limit: Maximum allowed limit
        
    Returns:
        Clamped limit value
    """
    if requested is None or requested <= 0:
        return default
    return min(requested, max_limit)


def validate_direction(direction: str) -> str:
    """Validate and normalize sort direction.
    
    Args:
        direction: Sort direction string
        
    Returns:
        Normalized direction ("asc" or "desc")
        
    Raises:
        ValueError: If direction is invalid
    """
    normalized = direction.lower().strip()
    if normalized in ("asc", "ascending"):
        return "asc"
    elif normalized in ("desc", "descending"):
        return "desc"
    else:
        raise ValueError(f"Invalid direction: {direction}")


def extract_next_cursor_from_items(
    items: Sequence[Mapping[str, Any]],
    *,
    limit: int,
    sort_keys: Sequence[str],
    direction: str = "desc",
    secret: str | bytes | None = None,
    ttl_s: int | None = None
) -> str | None:
    """Extract next cursor from paginated items.
    
    Args:
        items: Sequence of result items
        limit: Page limit used for query
        sort_keys: Sort column names in order
        direction: Sort direction
        secret: Optional HMAC signing key
        ttl_s: Optional cursor TTL
        
    Returns:
        Next cursor token or None if no more pages
    """
    if len(items) < limit:
        return None

    last_item = items[-1]
    values = [last_item[key] for key in sort_keys]

    payload = {
        "sort": list(sort_keys),
        "dir": validate_direction(direction),
        "vals": values
    }

    return encode_cursor(payload, secret=secret, ttl_s=ttl_s)


def build_keyset_predicate(
    values: Sequence[Any],
    *,
    sort_cols: Sequence[str],
    direction: str = "desc"
) -> tuple[str, dict[str, Any]]:
    """Build lexicographic keyset WHERE predicate for cursor pagination.
    
    Args:
        values: Sort values from cursor (aligned with sort_cols)
        sort_cols: Column names for sorting
        direction: Sort direction
        
    Returns:
        Tuple of (SQL predicate string, parameter binds)
    """
    if len(values) != len(sort_cols):
        raise ValueError("Values and sort_cols must have same length")

    if not values:
        return "1=1", {}

    direction = validate_direction(direction)
    op = "<" if direction == "desc" else ">"

    conditions = []
    binds = {}

    for i in range(len(sort_cols)):
        # Build condition for this level of the lexicographic comparison
        level_conditions = []

        # All previous columns must be equal
        for j in range(i):
            param_name = f"k{j}"
            level_conditions.append(f"{sort_cols[j]} = :{param_name}")
            binds[param_name] = values[j]

        # Current column uses the comparison operator
        param_name = f"k{i}"
        level_conditions.append(f"{sort_cols[i]} {op} :{param_name}")
        binds[param_name] = values[i]

        # Combine conditions for this level with AND
        condition = " AND ".join(level_conditions)
        conditions.append(f"({condition})")

    # Combine all levels with OR
    predicate = " OR ".join(conditions)
    return predicate, binds


def page_response(
    items: Sequence[Any],
    *,
    limit: int,
    next_cursor_payload: Mapping[str, Any] | None = None,
    secret: str | bytes | None = None,
    ttl_s: int | None = None
) -> dict[str, Any]:
    """Build standard paginated response envelope.
    
    Args:
        items: Page items
        limit: Page limit
        next_cursor_payload: Optional cursor payload for next page
        secret: Optional HMAC signing key
        ttl_s: Optional cursor TTL
        
    Returns:
        Standard pagination response envelope
    """
    next_cursor = None
    if next_cursor_payload is not None:
        next_cursor = encode_cursor(next_cursor_payload, secret=secret, ttl_s=ttl_s)

    return {
        "items": list(items),
        "pagination": {
            "limit": limit,
            "nextCursor": next_cursor
        }
    }
