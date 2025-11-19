"""
Production-ready time handling utilities for Flerity backend services.

Provides timezone-aware datetime operations, monotonic timers, and testable clock abstractions.
Single source of truth for time across the codebase.
"""

from __future__ import annotations

import abc
import asyncio
import re
import time
from datetime import UTC, datetime, tzinfo
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

# ISO 8601 parsing regex for common formats
_ISO_PATTERN = re.compile(
    r"^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.(\d+))?(Z|[+-]\d{2}:\d{2})$"
)


def utcnow() -> datetime:
    """Return timezone-aware UTC datetime."""
    return datetime.now(UTC)


def ensure_tzaware(dt: datetime, default_tz: tzinfo = UTC) -> datetime:
    """Attach default timezone if naive, return as-is if already aware."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=default_tz)
    return dt


def to_iso8601(dt: datetime) -> str:
    """Convert datetime to ISO 8601 string with Z suffix for UTC."""
    if dt.tzinfo is None:
        raise ValueError("datetime must be timezone-aware")

    # Convert to UTC and format with Z suffix
    utc_dt = dt.astimezone(UTC)
    return utc_dt.strftime("%Y-%m-%dT%H:%M:%S") + "Z"


def parse_iso8601(s: str) -> datetime:
    """Parse ISO 8601/RFC 3339 string to timezone-aware datetime."""
    if not s:
        raise ValueError("Empty string")

    # Handle Z suffix by replacing with +00:00
    normalized = s.replace("Z", "+00:00")

    try:
        # Use fromisoformat for standard parsing
        dt = datetime.fromisoformat(normalized)
        return ensure_tzaware(dt)
    except ValueError as e:
        raise ValueError(f"Invalid ISO 8601 format: {s}") from e


def from_timestamp(ts: float, tz: tzinfo | None = UTC) -> datetime:
    """Convert Unix timestamp to timezone-aware datetime."""
    return datetime.fromtimestamp(ts, tz=tz)


def now_ms() -> int:
    """Return current UTC epoch time in milliseconds."""
    return int(time.time() * 1000)


def to_tz(dt: datetime, tz_name: str) -> datetime:
    """Convert aware datetime to given IANA timezone."""
    if dt.tzinfo is None:
        raise ValueError("datetime must be timezone-aware")

    try:
        target_tz = ZoneInfo(tz_name)
        return dt.astimezone(target_tz)
    except ZoneInfoNotFoundError:
        raise ZoneInfoNotFoundError(f"Unknown timezone: {tz_name}")


def start_of_day(dt: datetime, tz_name: str) -> datetime:
    """Return start of day (00:00:00) in given timezone."""
    tz_dt = to_tz(dt, tz_name)
    return tz_dt.replace(hour=0, minute=0, second=0, microsecond=0)


def end_of_day(dt: datetime, tz_name: str) -> datetime:
    """Return end of day (23:59:59.999999) in given timezone."""
    tz_dt = to_tz(dt, tz_name)
    return tz_dt.replace(hour=23, minute=59, second=59, microsecond=999999)


def truncate(dt: datetime, *, unit: str) -> datetime:
    """Truncate datetime to specified unit (second|minute|hour|day)."""
    if unit == "second":
        return dt.replace(microsecond=0)
    elif unit == "minute":
        return dt.replace(second=0, microsecond=0)
    elif unit == "hour":
        return dt.replace(minute=0, second=0, microsecond=0)
    elif unit == "day":
        return dt.replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        raise ValueError(f"Unsupported unit: {unit}. Use second|minute|hour|day")


def monotonic_ms() -> int:
    """Return monotonic time in milliseconds."""
    return int(time.perf_counter() * 1000)


def elapsed_ms(since_ms: int) -> int:
    """Return elapsed milliseconds since given monotonic time."""
    return monotonic_ms() - since_ms


class Timer:
    """Context manager for measuring elapsed time using monotonic clock."""

    def __init__(self) -> None:
        self.ms: float = 0.0
        self._start: float = 0.0

    def __enter__(self) -> Timer:
        self._start = time.perf_counter()
        return self

    def __exit__(self, exc_type: Any, exc: Any, _tb: Any) -> None:
        self.ms = (time.perf_counter() - self._start) * 1000

    async def __aenter__(self) -> Timer:
        self._start = time.perf_counter()
        return self

    async def __aexit__(self, exc_type: Any, exc: Any, _tb: Any) -> None:
        self.ms = (time.perf_counter() - self._start) * 1000


def deadline_after_ms(ms: int) -> int:
    """Return monotonic deadline (ms) relative to now."""
    return monotonic_ms() + ms


def remaining_ms(deadline_ms: int) -> int:
    """Return remaining milliseconds until deadline, clamped to ≥0."""
    return max(0, deadline_ms - monotonic_ms())


async def sleep_until(deadline_ms: int) -> None:
    """Sleep until monotonic deadline, no-op if already passed."""
    remaining = remaining_ms(deadline_ms)
    if remaining > 0:
        await asyncio.sleep(remaining / 1000.0)


class Clock(abc.ABC):
    """Abstract clock interface for dependency injection and testing."""

    @abc.abstractmethod
    def now(self) -> datetime:
        """Return current UTC datetime."""
        pass

    @abc.abstractmethod
    def monotonic(self) -> float:
        """Return monotonic time in seconds."""
        pass

    @abc.abstractmethod
    async def sleep(self, seconds: float) -> None:
        """Sleep for given seconds."""
        pass


class SystemClock(Clock):
    """Real system clock implementation."""

    def now(self) -> datetime:
        """Return current system UTC time."""
        return utcnow()

    def monotonic(self) -> float:
        """Return system monotonic time in seconds."""
        return time.perf_counter()

    async def sleep(self, seconds: float) -> None:
        """Sleep using asyncio."""
        if seconds > 0:
            await asyncio.sleep(seconds)


class FrozenClock(Clock):
    """Deterministic clock for testing that can be manually advanced."""

    def __init__(self, start_dt: datetime | None = None, start_monotonic: float | None = None):
        """Initialize with optional start time and monotonic base."""
        self._dt = start_dt or utcnow()
        self._monotonic = start_monotonic or 0.0

        # Ensure datetime is timezone-aware
        self._dt = ensure_tzaware(self._dt)

    def now(self) -> datetime:
        """Return current frozen time."""
        return self._dt

    def monotonic(self) -> float:
        """Return current frozen monotonic time."""
        return self._monotonic

    def tick(self, seconds: float) -> None:
        """Advance both datetime and monotonic time by given seconds."""
        from datetime import timedelta
        self._dt += timedelta(seconds=seconds)
        self._monotonic += seconds

    async def sleep(self, seconds: float) -> None:
        """Advance time without real delay."""
        if seconds > 0:
            self.tick(seconds)
