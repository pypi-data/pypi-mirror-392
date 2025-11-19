"""Idempotency key generation, normalization, and verification with safe persistence.

Provides opaque key generation, request fingerprinting, state management with
concurrency protection, and framework-agnostic middleware helpers.
"""

from __future__ import annotations

import base64
import hashlib
import json
import re
import secrets
import threading
import time
from collections.abc import Mapping
from typing import Any, Protocol, TypedDict

# Constants
HDR_IDEMPOTENCY_KEY = "Idempotency-Key"
DEFAULT_TTL_S = 3600
DEFAULT_LOCK_MS = 30_000

# Key validation regex
_KEY_PATTERN = re.compile(r"^[A-Za-z0-9_-]{16,128}$")


class IdempotencyRecord(TypedDict, total=False):
    """Idempotency record structure for persistence."""
    key: str
    fingerprint: str
    state: str
    created_at_ms: int
    updated_at_ms: int
    ttl_s: int | None
    response_status: int | None
    response_headers: dict[str, str] | None
    response_body: Any | None
    error_code: str | None
    error_message: str | None
    lock_owner: str | None
    lock_expires_ms: int | None


class IdempotencyStore(Protocol):
    """Abstract interface for idempotency record storage."""

    def get(self, key: str) -> IdempotencyRecord | None:
        """Get record by key, None if not found."""
        ...

    def put_if_absent(self, rec: IdempotencyRecord) -> bool:
        """Insert record if key doesn't exist. Returns True if inserted."""
        ...

    def update(self, key: str, updates: Mapping[str, Any]) -> None:
        """Update existing record with partial updates."""
        ...

    def delete(self, key: str) -> None:
        """Delete record by key."""
        ...


# Exceptions
class IdempotencyError(Exception):
    """Base exception for idempotency errors."""
    pass


class InvalidKey(IdempotencyError):
    """Invalid idempotency key format."""
    pass


class IdempotencyInProgress(IdempotencyError):
    """Request is currently being processed by another client."""

    def __init__(self, message: str, owner: str | None = None, remaining_ms: int | None = None):
        super().__init__(message)
        self.owner = owner
        self.remaining_ms = remaining_ms


class RecordMismatch(IdempotencyError):
    """Same key used with different request fingerprint."""
    pass


# Utility functions
def _now_ms() -> int:
    """Get current time in milliseconds."""
    try:
        from .clock import now_ms
        return now_ms()
    except ImportError:
        return int(time.time() * 1000)


def _get_request_id() -> str | None:
    """Get current request ID from tracing."""
    try:
        from .tracing import get_request_id
        return get_request_id()
    except ImportError:
        return None


def _new_request_id() -> str:
    """Generate new request ID."""
    try:
        from .ids import new_request_id
        return new_request_id()
    except ImportError:
        return new_key(16)


def _canonical_dumps(obj: Any) -> str:
    """Canonical JSON serialization."""
    try:
        from .jsonx import canonical_dumps
        return canonical_dumps(obj)
    except ImportError:
        return json.dumps(obj, sort_keys=True, separators=(',', ':'))


def _canonical_hash(data: str) -> str:
    """Canonical hash of string data."""
    try:
        from .jsonx import canonical_hash
        return canonical_hash(data)
    except ImportError:
        try:
            from .crypto import sha256_hex
            return sha256_hex(data)
        except ImportError:
            return hashlib.sha256(data.encode('utf-8')).hexdigest()


# Key generation and validation
def new_key(nbytes: int = 24) -> str:
    """Generate cryptographically strong base64url key (unpadded)."""
    return base64.urlsafe_b64encode(secrets.token_bytes(nbytes)).decode().rstrip('=')


def normalize_key(value: str | None, *, name: str = "Idempotency-Key") -> str:
    """Normalize and validate idempotency key."""
    if not value:
        raise InvalidKey(f"{name} cannot be empty")

    # Trim whitespace
    key = value.strip()

    # Validate format and length
    if not _KEY_PATTERN.match(key):
        raise InvalidKey(f"{name} must be 16-128 characters of [A-Za-z0-9_-]")

    return key


def from_headers(headers: Mapping[str, str]) -> str | None:
    """Extract idempotency key from headers (case-insensitive)."""
    # Create case-insensitive lookup
    header_map = {k.lower(): v for k, v in headers.items()}

    # Try primary header first, then fallback
    key = header_map.get("idempotency-key") or header_map.get("x-idempotency-key")

    return normalize_key(key) if key else None


# Request fingerprinting
def request_fingerprint(
    method: str,
    path: str,
    body: Any = None,
    *,
    user_id: str | None = None,
    extra: Mapping[str, Any] | None = None
) -> str:
    """Compute canonical fingerprint of request."""
    fingerprint_data = {
        "m": method.upper(),
        "p": path,
        "u": user_id,
        "b": body,
        "x": extra or {}
    }

    canonical_json = _canonical_dumps(fingerprint_data)
    return _canonical_hash(canonical_json).lower()


# Core execution flow
def begin_execution(
    store: IdempotencyStore,
    key: str,
    fingerprint: str,
    *,
    ttl_s: int = DEFAULT_TTL_S,
    lock_ms: int = DEFAULT_LOCK_MS,
    owner: str | None = None
) -> tuple[str, IdempotencyRecord]:
    """Begin idempotent execution, handling concurrency and state."""
    if owner is None:
        owner = _get_request_id() or _new_request_id()

    now = _now_ms()
    existing = store.get(key)

    if existing is None:
        # Create new in-progress record
        record: IdempotencyRecord = {
            "key": key,
            "fingerprint": fingerprint,
            "state": "in_progress",
            "created_at_ms": now,
            "updated_at_ms": now,
            "ttl_s": ttl_s,
            "lock_owner": owner,
            "lock_expires_ms": now + lock_ms
        }

        if store.put_if_absent(record):
            return owner, record
        else:
            # Race condition - retry with existing record
            existing = store.get(key)
            if existing is None:
                raise IdempotencyError("Failed to create or retrieve record")

    # Handle existing record
    if existing["fingerprint"] != fingerprint:
        raise RecordMismatch(f"Key {key} used with different request fingerprint")

    if existing["state"] == "completed":
        return owner, existing

    if existing["state"] == "error":
        return owner, existing

    if existing["state"] == "in_progress":
        # Check lock expiry
        lock_expires = existing.get("lock_expires_ms")
        if lock_expires is None or now > lock_expires:
            # Steal expired lock
            steal_updates: IdempotencyRecord = {
                "lock_owner": owner,
                "lock_expires_ms": now + lock_ms,
                "updated_at_ms": now
            }
            store.update(key, steal_updates)
            existing.update(steal_updates)
            return owner, existing
        else:
            # Lock still active
            if existing.get("lock_owner") == owner:
                # Same owner - extend lock
                extend_updates: IdempotencyRecord = {
                    "lock_expires_ms": now + lock_ms,
                    "updated_at_ms": now
                }
                store.update(key, extend_updates)
                existing.update(extend_updates)
                return owner, existing
            else:
                # Different owner - wait
                remaining = (lock_expires or 0) - now
                raise IdempotencyInProgress(
                    f"Request in progress by {existing.get('lock_owner')}",
                    owner=existing.get("lock_owner"),
                    remaining_ms=remaining
                )

    return owner, existing


def complete_execution(
    store: IdempotencyStore,
    key: str,
    *,
    status: int,
    headers: Mapping[str, str] | None,
    body: Any,
    fingerprint: str
) -> IdempotencyRecord:
    """Mark execution as completed and store response."""
    now = _now_ms()

    updates = {
        "state": "completed",
        "updated_at_ms": now,
        "response_status": status,
        "response_headers": dict(headers) if headers else None,
        "response_body": body,
        "lock_owner": None,
        "lock_expires_ms": None
    }

    store.update(key, updates)

    # Return updated record
    record = store.get(key)
    if record is None:
        raise IdempotencyError(f"Record {key} disappeared after completion")

    return record


def fail_execution(
    store: IdempotencyStore,
    key: str,
    *,
    error_code: str,
    error_message: str | None = None
) -> None:
    """Mark execution as failed."""
    now = _now_ms()

    updates = {
        "state": "error",
        "updated_at_ms": now,
        "error_code": error_code,
        "error_message": error_message,
        "lock_owner": None,
        "lock_expires_ms": None
    }

    store.update(key, updates)


def get_replay(
    store: IdempotencyStore,
    key: str,
    *,
    expect_fingerprint: str | None = None
) -> IdempotencyRecord | None:
    """Get completed record for replay."""
    record = store.get(key)

    if record is None or record["state"] != "completed":
        return None

    if expect_fingerprint and record["fingerprint"] != expect_fingerprint:
        return None

    return record


# Middleware helpers
def pre_handle(
    store: IdempotencyStore,
    key: str | None,
    *,
    method: str,
    path: str,
    user_id: str | None,
    body: Any,
    ttl_s: int = DEFAULT_TTL_S,
    lock_ms: int = DEFAULT_LOCK_MS
) -> tuple[str, str, IdempotencyRecord | None]:
    """Pre-handle idempotency check."""
    # Generate key if not provided
    if key is None:
        key = new_key()
    else:
        key = normalize_key(key)

    # Compute fingerprint
    fingerprint = request_fingerprint(method, path, body, user_id=user_id)

    # Begin execution
    owner, record = begin_execution(
        store, key, fingerprint,
        ttl_s=ttl_s, lock_ms=lock_ms
    )

    # Return record for replay if completed
    if record["state"] == "completed":
        return key, fingerprint, record

    # Continue with execution
    return key, fingerprint, None


def post_handle(
    store: IdempotencyStore,
    key: str,
    fingerprint: str,
    *,
    status: int,
    headers: Mapping[str, str] | None,
    body: Any
) -> IdempotencyRecord:
    """Post-handle idempotency completion."""
    return complete_execution(
        store, key,
        status=status, headers=headers, body=body,
        fingerprint=fingerprint
    )


# In-memory store implementation
class InMemoryIdempotencyStore:
    """Thread-safe in-memory idempotency store for testing."""

    def __init__(self) -> None:
        self._records: dict[str, IdempotencyRecord] = {}
        self._lock = threading.RLock()

    def _is_expired(self, record: IdempotencyRecord) -> bool:
        """Check if record is expired based on TTL."""
        ttl_s = record.get("ttl_s")
        if ttl_s is None:
            return False

        created_at = record.get("created_at_ms", 0)
        ttl_ms = ttl_s * 1000
        return _now_ms() > (created_at + ttl_ms)

    def get(self, key: str) -> IdempotencyRecord | None:
        """Get record by key, respecting TTL."""
        with self._lock:
            record = self._records.get(key)
            if record and self._is_expired(record):
                del self._records[key]
                return None
            return record.copy() if record else None

    def put_if_absent(self, rec: IdempotencyRecord) -> bool:
        """Insert record if key doesn't exist."""
        with self._lock:
            if rec["key"] in self._records:
                return False
            self._records[rec["key"]] = rec.copy()
            return True

    def update(self, key: str, updates: Mapping[str, Any]) -> None:
        """Update existing record."""
        with self._lock:
            if key not in self._records:
                raise IdempotencyError(f"Record {key} not found for update")
            # Update only valid fields that exist in IdempotencyRecord
            record = self._records[key]
            for k, v in updates.items():
                if k in IdempotencyRecord.__annotations__:
                    record[k] = v  # type: ignore[literal-required]

    def delete(self, key: str) -> None:
        """Delete record by key."""
        with self._lock:
            self._records.pop(key, None)
