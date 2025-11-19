"""
Messaging abstraction ports and interfaces.

This module defines cloud-agnostic messaging interfaces that map to various
cloud providers:

AWS Mappings:
- partition_key → SQS FIFO MessageGroupId / SNS FIFO MessageGroupId / Kinesis partition key
- idempotency_key → SQS MessageDeduplicationId / SNS MessageDeduplicationId / custom header
- visibility_timeout_seconds → SQS VisibilityTimeout / consumer-side management for others
- group → SQS queue name / SNS subscription / Kinesis consumer group
- dead_letter_topic → SQS DLQ / SNS DLQ / custom error handling

Kafka Mappings:
- partition_key → Kafka partition key
- idempotency_key → custom header for deduplication
- group → Kafka consumer group
- visibility_timeout_seconds → consumer-side session timeout management
"""

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Protocol

# Graceful imports from flerity_core.utils
try:
    from ..utils.ids import new_uuid
except ImportError:
    import uuid
    def new_uuid() -> str:
        return str(uuid.uuid4())

try:
    from ..utils.jsonx import canonical_dumps
except ImportError:
    def canonical_dumps(obj: Any) -> str:
        return json.dumps(obj, sort_keys=True, separators=(',', ':'))

try:
    from ..utils.clock import utcnow
except ImportError:
    from datetime import datetime
    def utcnow() -> datetime:
        return datetime.now(UTC)


# Type aliases
MessageHeaders = dict[str, str]


# Data structures
@dataclass(frozen=True)
class Message:
    """A message with topic, key, payload, and headers."""
    topic: str
    key: str | None
    payload: dict[str, Any]
    headers: MessageHeaders


@dataclass(frozen=True)
class PublishOptions:
    """Options for publishing messages."""
    idempotency_key: str | None = None
    partition_key: str | None = None
    schema: str | None = None
    delivery_delay_seconds: int | None = None
    timeout_seconds: int | None = None
    batch: bool = False
    content_size_limit_bytes: int | None = 256 * 1024  # 256 KiB


@dataclass(frozen=True)
class ConsumeOptions:
    """Options for consuming messages."""
    group: str
    prefetch: int = 10
    visibility_timeout_seconds: int | None = None
    max_retries: int = 5
    dead_letter_topic: str | None = None
    batch: bool = False
    poll_interval_seconds: float = 0.2


@dataclass(frozen=True)
class DeliveredMessage:
    """A message delivered to a consumer with metadata."""
    message: Message
    received_at: datetime
    attempt: int
    delivery_tag: str
    scheduled_for: datetime | None = None


@dataclass(frozen=True)
class Batch:
    """A batch of delivered messages."""
    messages: list[DeliveredMessage]


# Exceptions
class MqError(Exception):
    """Base exception for messaging errors."""
    pass


class PublishError(MqError):
    """Error during message publishing."""
    pass


class SerializationError(MqError):
    """Error serializing message payload."""
    pass


class OversizedMessageError(MqError):
    """Message exceeds size limits."""
    pass


class ConsumeError(MqError):
    """Error during message consumption."""
    pass


class AckError(MqError):
    """Error acknowledging message."""
    pass


# Protocols
class Producer(Protocol):
    """Message producer interface."""

    async def publish(
        self,
        topic: str,
        payload: dict[str, Any],
        *,
        options: PublishOptions | None = None
    ) -> str:
        """
        Publish a single message to a topic.
        
        Args:
            topic: Target topic name
            payload: Message payload (must be JSON-serializable)
            options: Publishing options
            
        Returns:
            Opaque message ID
            
        Raises:
            PublishError: If publishing fails
            SerializationError: If payload is not JSON-serializable
            OversizedMessageError: If message exceeds size limits
        """
        ...

    async def publish_many(
        self,
        topic: str,
        payloads: list[dict[str, Any]],
        *,
        options: PublishOptions | None = None
    ) -> list[str]:
        """
        Publish multiple messages to a topic.
        
        Args:
            topic: Target topic name
            payloads: List of message payloads
            options: Publishing options
            
        Returns:
            List of opaque message IDs
            
        Raises:
            PublishError: If publishing fails
            SerializationError: If any payload is not JSON-serializable
            OversizedMessageError: If any message exceeds size limits
        """
        ...


class Consumer(Protocol):
    """Message consumer interface."""

    async def subscribe(self, topic: str, *, options: ConsumeOptions) -> None:
        """
        Subscribe to a topic with the given options.
        
        Args:
            topic: Topic to subscribe to
            options: Consumption options including group and retry settings
            
        Raises:
            ConsumeError: If subscription fails
        """
        ...

    async def poll(self, *, max_messages: int | None = None) -> list[DeliveredMessage]:
        """
        Poll for available messages.
        
        Args:
            max_messages: Maximum number of messages to return (defaults to prefetch)
            
        Returns:
            List of delivered messages (may be empty)
            
        Raises:
            ConsumeError: If polling fails
        """
        ...

    async def ack(self, delivery_tag: str) -> None:
        """
        Acknowledge successful processing of a message.
        
        Args:
            delivery_tag: Opaque delivery tag from DeliveredMessage
            
        Raises:
            AckError: If acknowledgment fails
        """
        ...

    async def nack(
        self,
        delivery_tag: str,
        *,
        requeue: bool = True,
        delay_seconds: int | None = None
    ) -> None:
        """
        Negatively acknowledge a message (processing failed).
        
        Args:
            delivery_tag: Opaque delivery tag from DeliveredMessage
            requeue: Whether to requeue the message for retry
            delay_seconds: Delay before requeuing (overrides exponential backoff)
            
        Raises:
            AckError: If negative acknowledgment fails
        """
        ...

    async def close(self) -> None:
        """Close the consumer and clean up resources."""
        ...


class Admin(Protocol):
    """Administrative operations interface."""

    async def ensure_topic(
        self,
        topic: str,
        *,
        fifo: bool = False,
        _partitions: int | None = None
    ) -> None:
        """
        Ensure a topic exists with the given configuration.
        
        Args:
            topic: Topic name
            fifo: Whether to enable FIFO ordering
            _partitions: Number of _partitions (for Kafka-like systems)
        """
        ...

    async def purge(self, topic: str, *, group: str | None = None) -> None:
        """
        Purge messages from a topic or consumer group.
        
        Args:
            topic: Topic to purge
            group: Consumer group to purge (if None, purges entire topic)
        """
        ...


# Helper functions
def build_headers(
    request_id: str | None = None,
    correlation_id: str | None = None,
    idempotency_key: str | None = None,
    schema: str | None = None,
    partition_key: str | None = None,
    attempt: int = 0
) -> MessageHeaders:
    """
    Build message headers with reserved keys.
    
    Args:
        request_id: Request ID for tracing
        correlation_id: Correlation ID for tracing
        idempotency_key: Idempotency key for deduplication
        schema: Message schema identifier
        partition_key: Partition key for ordering
        attempt: Retry attempt number
        
    Returns:
        Message headers dictionary
    """
    headers: MessageHeaders = {
        "x-sent-at": utcnow().isoformat(),
        "x-attempt": str(attempt),
    }

    if request_id:
        headers["x-request-id"] = request_id
    if correlation_id:
        headers["x-correlation-id"] = correlation_id
    if idempotency_key:
        headers["x-idempotency-key"] = idempotency_key
    if schema:
        headers["x-schema"] = schema
    if partition_key:
        headers["x-partition-key"] = partition_key

    return headers


def ensure_json(payload: Any) -> dict[str, Any]:
    """
    Ensure payload is JSON-serializable and return as dict.
    
    Args:
        payload: Payload to validate
        
    Returns:
        Validated payload as dict
        
    Raises:
        SerializationError: If payload is not JSON-serializable dict
    """
    if not isinstance(payload, dict):
        raise SerializationError(f"Payload must be a dict, got {type(payload)}")

    try:
        json.dumps(payload)
        return payload
    except (TypeError, ValueError) as e:
        raise SerializationError(f"Payload is not JSON-serializable: {e}")


def compute_idempotency_key(topic: str, payload: dict[str, Any]) -> str:
    """
    Compute deterministic idempotency key from topic and payload.
    
    Args:
        topic: Message topic
        payload: Message payload
        
    Returns:
        SHA256 hash of canonical JSON representation
    """
    canonical = canonical_dumps({"topic": topic, "payload": payload})
    return hashlib.sha256(canonical.encode()).hexdigest()


def validate_size(payload: dict[str, Any], limit_bytes: int | None) -> None:
    """
    Validate payload size against limit.
    
    Args:
        payload: Payload to validate
        limit_bytes: Size limit in bytes (None to skip validation)
        
    Raises:
        OversizedMessageError: If payload exceeds limit
    """
    if limit_bytes is None:
        return

    size = len(json.dumps(payload).encode('utf-8'))
    if size > limit_bytes:
        raise OversizedMessageError(
            f"Message size {size} bytes exceeds limit {limit_bytes} bytes"
        )
