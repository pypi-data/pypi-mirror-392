"""
Utility functions for message queue implementations.

Provides common functionality for:
- Message deduplication
- Retry logic with exponential backoff
- Connection management
- Tracing helpers
"""

import asyncio
import hashlib
import json
import time
import uuid
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar, cast

try:
    from opentelemetry import trace  # type: ignore[import-not-found]
    from opentelemetry.trace import Status, StatusCode  # type: ignore[import-not-found]
except ImportError:
    trace = None

from ..utils.clock import utcnow
from ..utils.logging import get_logger

logger = get_logger(__name__)
tracer = trace.get_tracer(__name__) if trace else None

T = TypeVar('T')


def new_uuid() -> str:
    """Generate a new UUID string."""
    return str(uuid.uuid4())


def exponential_backoff(attempt: int, base_delay: float = 1.0, max_delay: float = 60.0) -> float:
    """Calculate exponential backoff delay."""
    delay = base_delay * (2 ** attempt)
    return min(delay, max_delay)


def backoff_func(max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 60.0):
    """Decorator for automatic retry with exponential backoff."""
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception: Exception | None = None
            
            for attempt in range(max_retries + 1):
                try:
                    if asyncio.iscoroutinefunction(func):
                        return await func(*args, **kwargs)
                    else:
                        return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        break
                    
                    delay = exponential_backoff(attempt, base_delay, max_delay)
                    await asyncio.sleep(delay)
            
            if last_exception:
                raise last_exception
            else:
                raise RuntimeError("Max retries exceeded")
        
        return wrapper
    return decorator


class DeduplicationCache:
    """In-memory deduplication cache with TTL support."""

    def __init__(self, ttl_seconds: int = 3600, max_size: int = 10000):
        self.ttl_seconds = ttl_seconds
        self.max_size = max_size
        self._cache: dict[str, tuple[Any, float]] = {}
        self._access_times: dict[str, float] = {}

    def get(self, key: str) -> Any | None:
        """Get value from cache if not expired."""
        if key not in self._cache:
            return None

        value, timestamp = self._cache[key]
        current_time = time.time()

        # Check if expired
        if current_time - timestamp > self.ttl_seconds:
            self._remove(key)
            return None

        # Update access time for LRU
        self._access_times[key] = current_time
        return value

    def set(self, key: str, value: Any) -> None:
        """Set value in cache with current timestamp."""
        current_time = time.time()

        # Evict if at max size
        if len(self._cache) >= self.max_size and key not in self._cache:
            self._evict_lru()

        self._cache[key] = (value, current_time)
        self._access_times[key] = current_time

    def _remove(self, key: str) -> None:
        """Remove key from cache."""
        self._cache.pop(key, None)
        self._access_times.pop(key, None)

    def _evict_lru(self) -> None:
        """Evict least recently used item."""
        if not self._access_times:
            return

        lru_key = min(self._access_times.keys(), key=lambda k: self._access_times[k])
        self._remove(lru_key)

    def clear(self) -> None:
        """Clear all cached items."""
        self._cache.clear()
        self._access_times.clear()

    def cleanup_expired(self) -> None:
        """Remove expired items from cache."""
        current_time = time.time()
        expired_keys = []

        for key, (_, timestamp) in self._cache.items():
            if current_time - timestamp > self.ttl_seconds:
                expired_keys.append(key)

        for key in expired_keys:
            self._remove(key)


class MessageDeduplicator:
    """Message deduplication using content hashing and idempotency keys."""

    def __init__(self, cache_ttl_seconds: int = 3600):
        self._cache = DeduplicationCache(ttl_seconds=cache_ttl_seconds)
        self._processed_keys: set[str] = set()

    def generate_content_hash(self, payload: dict[str, Any]) -> str:
        """Generate deterministic hash from message content."""
        # Create canonical JSON representation
        canonical = json.dumps(payload, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(canonical.encode()).hexdigest()[:16]

    def is_duplicate(self, idempotency_key: str | None, payload: dict[str, Any]) -> bool:
        """Check if message is a duplicate."""
        # Check idempotency key first
        if idempotency_key:
            if self._cache.get(f"idem:{idempotency_key}"):
                return True

        # Check content hash
        content_hash = self.generate_content_hash(payload)
        if self._cache.get(f"hash:{content_hash}"):
            return True

        return False

    def mark_processed(self, idempotency_key: str | None, payload: dict[str, Any], message_id: str) -> None:
        """Mark message as processed."""
        if idempotency_key:
            self._cache.set(f"idem:{idempotency_key}", message_id)

        content_hash = self.generate_content_hash(payload)
        self._cache.set(f"hash:{content_hash}", message_id)

    def get_cached_result(self, idempotency_key: str | None, payload: dict[str, Any]) -> str | None:
        """Get cached result for duplicate message."""
        if idempotency_key:
            result = self._cache.get(f"idem:{idempotency_key}")
            if result:
                return str(result)

        content_hash = self.generate_content_hash(payload)
        cached_result = self._cache.get(f"hash:{content_hash}")
        return str(cached_result) if cached_result else None


async def retry_with_backoff(
    func: Callable[..., T],
    *args: Any,
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    jitter: bool = True,
    **kwargs: Any
) -> T:
    """
    Retry function with exponential backoff.
    
    Args:
        func: Async function to retry
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        backoff_factor: Multiplier for delay on each retry
        jitter: Add random jitter to delay
    """
    import random

    last_exception: Exception | None = None

    for attempt in range(max_retries + 1):
        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            return cast(T, result)
        except Exception as e:
            last_exception = e

            if attempt == max_retries:
                break

            # Calculate delay with exponential backoff
            delay = min(base_delay * (backoff_factor ** attempt), max_delay)

            # Add jitter to prevent thundering herd
            if jitter:
                delay *= (0.5 + random.random() * 0.5)

            logger.warning(
                f"Attempt {attempt + 1} failed, retrying in {delay:.2f}s",
                extra={
                    "attempt": attempt + 1,
                    "max_retries": max_retries,
                    "delay": delay,
                    "error": str(e)
                }
            )

            await asyncio.sleep(delay)

    # All retries exhausted
    if last_exception is not None:
        raise last_exception
    else:
        raise RuntimeError("All retries exhausted with no exception recorded")


def trace_mq_operation(operation_name: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator to add tracing to MQ operations."""
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            if not tracer:
                return await func(*args, **kwargs)

            span = tracer.start_span(f"mq.{operation_name}")

            try:
                # Extract common attributes from args
                if args and hasattr(args[0], '__class__'):
                    span.set_attributes({
                        "mq.provider": args[0].__class__.__module__.split('.')[-1],
                        "mq.operation": operation_name
                    })

                # Extract topic/queue name if available
                if len(args) > 1 and isinstance(args[1], str):
                    span.set_attributes({"mq.destination": args[1]})

                result = await func(*args, **kwargs)
                span.set_status(Status(StatusCode.OK))
                return result

            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.set_attributes({
                    "error.type": type(e).__name__,
                    "error.message": str(e)
                })
                raise
            finally:
                span.end()

        return wrapper
    return decorator


class ConnectionManager:
    """Manages connections with health checking and reconnection."""

    def __init__(self, connection_factory: Callable[[], Any] = None, health_check_interval: float = 30.0, max_connections: int = 10) -> None:
        self.connection_factory = connection_factory or (lambda: None)
        self.health_check_interval = health_check_interval
        self.max_connections = max_connections
        self._connection: Any = None
        self._last_health_check: float = 0.0
        self._connection_lock = asyncio.Lock()

    async def get_connection(self) -> Any:
        """Get healthy connection, creating or reconnecting as needed."""
        async with self._connection_lock:
            current_time = time.time()

            # Check if we need to health check
            if (self._connection and
                current_time - self._last_health_check > self.health_check_interval):

                if not await self._health_check():
                    logger.info("Connection health check failed, reconnecting")
                    await self._close_connection()
                    self._connection = None

            # Create connection if needed
            if not self._connection:
                self._connection = await self.connection_factory()
                self._last_health_check = current_time
                logger.info("Created new connection")

            return self._connection

    async def _health_check(self) -> bool:
        """Check if connection is healthy."""
        try:
            # This would be provider-specific health check
            # For now, assume connection is healthy if it exists
            return self._connection is not None
        except Exception:
            return False

    async def _close_connection(self) -> None:
        """Close current connection."""
        if self._connection:
            try:
                if hasattr(self._connection, 'close'):
                    await self._connection.close()
                elif hasattr(self._connection, 'disconnect'):
                    await self._connection.disconnect()
            except Exception as e:
                logger.warning(f"Error closing connection: {e}")

    async def close(self) -> None:
        """Close connection manager."""
        async with self._connection_lock:
            await self._close_connection()
            self._connection = None


class MessageMetrics:
    """Collect metrics for message queue operations."""

    def __init__(self) -> None:
        self.published_count = 0
        self.consumed_count = 0
        self.ack_count = 0
        self.nack_count = 0
        self.error_count = 0
        self.duplicate_count = 0
        self._start_time = utcnow()

    def record_publish(self, count: int = 1) -> None:
        """Record published messages."""
        self.published_count += count

    def record_consume(self, count: int = 1) -> None:
        """Record consumed messages."""
        self.consumed_count += count

    def record_ack(self, count: int = 1) -> None:
        """Record acknowledged messages."""
        self.ack_count += count

    def record_nack(self, count: int = 1) -> None:
        """Record negative acknowledged messages."""
        self.nack_count += count

    def record_error(self, count: int = 1) -> None:
        """Record errors."""
        self.error_count += count

    def record_duplicate(self, count: int = 1) -> None:
        """Record duplicate messages."""
        self.duplicate_count += count

    def get_summary(self) -> dict[str, Any]:
        """Get metrics summary."""
        uptime = (utcnow() - self._start_time).total_seconds()

        return {
            "uptime_seconds": uptime,
            "published_count": self.published_count,
            "consumed_count": self.consumed_count,
            "ack_count": self.ack_count,
            "nack_count": self.nack_count,
            "error_count": self.error_count,
            "duplicate_count": self.duplicate_count,
            "publish_rate": self.published_count / uptime if uptime > 0 else 0,
            "consume_rate": self.consumed_count / uptime if uptime > 0 else 0,
            "error_rate": self.error_count / max(self.published_count + self.consumed_count, 1)
        }


def validate_message_size(payload: dict[str, Any], max_size_bytes: int = 256 * 1024) -> None:
    """Validate message size doesn't exceed limits."""
    message_size = len(json.dumps(payload).encode('utf-8'))
    if message_size > max_size_bytes:
        raise ValueError(f"Message size {message_size} exceeds limit {max_size_bytes}")


def sanitize_topic_name(topic: str, provider: str = "generic") -> str:
    """Sanitize topic name for specific provider requirements."""
    # Remove invalid characters
    sanitized = ''.join(c for c in topic if c.isalnum() or c in '-_.')

    # Provider-specific rules
    if provider == "sqs":
        # SQS queue names: 1-80 chars, alphanumeric, hyphens, underscores
        sanitized = sanitized[:80]
    elif provider == "rabbitmq":
        # RabbitMQ: 255 chars max
        sanitized = sanitized[:255]
    elif provider == "redis":
        # Redis: no specific limits, but keep reasonable
        sanitized = sanitized[:200]

    return sanitized or "default-topic"
