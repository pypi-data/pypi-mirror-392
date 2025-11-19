"""
In-memory message broker implementation.

Provides a lightweight, deterministic message broker for testing and local development.
Implements at-least-once delivery semantics with visibility timeouts, retries, and DLQ.

Features:
- Async-first implementation using asyncio primitives
- Per-partition-key ordering (best effort)
- Configurable visibility timeouts and retry backoff
- Dead letter queue support
- Deterministic behavior for testing (injectable time function)
- No external dependencies beyond stdlib
"""

import asyncio
import logging
import time
from collections import defaultdict, deque
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from .ports import (
    AckError,
    Admin,
    ConsumeError,
    ConsumeOptions,
    Consumer,
    DeliveredMessage,
    Message,
    OversizedMessageError,
    Producer,
    PublishError,
    PublishOptions,
    SerializationError,
    build_headers,
    compute_idempotency_key,
    ensure_json,
    validate_size,
)

# Graceful imports from flerity_core.utils
try:
    from ..utils.ids import new_uuid
except ImportError:
    import uuid
    def new_uuid() -> str:
        return str(uuid.uuid4())

try:
    from ..utils.clock import utcnow
except ImportError:
    from datetime import datetime
    def utcnow() -> datetime:
        return datetime.now(UTC)

try:
    from ..utils.logging import get_logger
except ImportError:
    def get_logger(name: str | None = None) -> logging.Logger:
        return logging.getLogger(name)


# Configuration constants
MAX_PAYLOAD_BYTES = 256 * 1024
MAX_BATCH_BYTES = 2 * 1024 * 1024
DEFAULT_VISIBILITY_TIMEOUT = 30.0


@dataclass
class InternalMessage:
    """Internal message representation with broker metadata."""
    message_id: str
    message: Message
    visibility_deadline: float | None = None
    attempt: int = 0
    delivery_tag: str = field(default_factory=new_uuid)
    scheduled_for: float | None = None
    partition_key: str | None = None


@dataclass
class TopicState:
    """State for a single topic."""
    # Per-group queues
    pending: dict[str, deque[InternalMessage]] = field(default_factory=lambda: defaultdict(deque))
    dlq: dict[str, deque[InternalMessage]] = field(default_factory=lambda: defaultdict(deque))
    in_flight: dict[str, InternalMessage] = field(default_factory=dict)

    # Per-partition-key ordering
    partition_queues: dict[str, dict[str, deque[InternalMessage]]] = field(
        default_factory=lambda: defaultdict(lambda: defaultdict(deque))
    )
    partition_in_flight: dict[str, dict[str, InternalMessage]] = field(
        default_factory=lambda: defaultdict(dict)
    )

    # Consumer groups
    groups: set[str] = field(default_factory=set)


class InMemoryBroker:
    """Shared in-memory broker state."""

    def __init__(self, time_fn: Callable[[], float] | None = None):
        self.topics: dict[str, TopicState] = defaultdict(TopicState)
        self.time_fn = time_fn or time.monotonic
        self.logger = get_logger(__name__)
        self._lock = asyncio.Lock()

    def _get_current_time(self) -> float:
        """Get current time using configured time function."""
        return self.time_fn()

    async def _cleanup_expired_messages(self, topic_state: TopicState, group: str) -> None:
        """Move expired in-flight messages back to pending queue."""
        current_time = self._get_current_time()
        expired_tags = []

        for tag, msg in topic_state.in_flight.items():
            if msg.visibility_deadline and current_time >= msg.visibility_deadline:
                expired_tags.append(tag)

        for tag in expired_tags:
            msg = topic_state.in_flight.pop(tag)

            # Remove from partition in-flight if applicable
            if msg.partition_key:
                partition_in_flight = topic_state.partition_in_flight[group]
                if partition_in_flight.get(msg.partition_key) == msg:
                    del partition_in_flight[msg.partition_key]

            # Requeue with incremented attempt
            msg.attempt += 1
            msg.visibility_deadline = None
            msg.delivery_tag = new_uuid()

            if msg.partition_key:
                topic_state.partition_queues[group][msg.partition_key].appendleft(msg)
            else:
                topic_state.pending[group].appendleft(msg)

    def _calculate_backoff_delay(self, attempt: int) -> float:
        """Calculate exponential backoff delay."""
        return min(float(2 ** attempt) * 0.5, 30.0)


# Global broker instance
_broker = InMemoryBroker()


class InMemoryProducer(Producer):
    """In-memory message producer."""

    def __init__(self, broker: InMemoryBroker | None = None):
        self.broker = broker or _broker
        self.logger = get_logger(f"{__name__}.Producer")

    async def publish(
        self,
        topic: str,
        payload: dict[str, Any],
        *,
        options: PublishOptions | None = None
    ) -> str:
        """Publish a single message."""
        options = options or PublishOptions()

        try:
            # Validate payload
            payload = ensure_json(payload)
            validate_size(payload, options.content_size_limit_bytes)

            # Build headers
            headers = build_headers(
                idempotency_key=options.idempotency_key or compute_idempotency_key(topic, payload),
                schema=options.schema,
                partition_key=options.partition_key
            )

            # Create message
            message = Message(
                topic=topic,
                key=options.partition_key,
                payload=payload,
                headers=headers
            )

            message_id = new_uuid()
            scheduled_for = None
            if options.delivery_delay_seconds:
                scheduled_for = self.broker._get_current_time() + options.delivery_delay_seconds

            internal_msg = InternalMessage(
                message_id=message_id,
                message=message,
                scheduled_for=scheduled_for,
                partition_key=options.partition_key
            )

            async with self.broker._lock:
                topic_state = self.broker.topics[topic]

                # Add to all registered groups
                for group in topic_state.groups:
                    if options.partition_key:
                        topic_state.partition_queues[group][options.partition_key].append(internal_msg)
                    else:
                        topic_state.pending[group].append(internal_msg)

            self.logger.debug(
                "Published message",
                extra={
                    "message_id": message_id,
                    "topic": topic,
                    "partition_key": options.partition_key,
                    "payload_size": len(str(payload))
                }
            )

            return message_id

        except (SerializationError, OversizedMessageError):
            raise
        except Exception as e:
            raise PublishError(f"Failed to publish message: {e}")

    async def publish_many(
        self,
        topic: str,
        payloads: list[dict[str, Any]],
        *,
        options: PublishOptions | None = None
    ) -> list[str]:
        """Publish multiple messages."""
        message_ids = []
        for payload in payloads:
            message_id = await self.publish(topic, payload, options=options)
            message_ids.append(message_id)
        return message_ids


class InMemoryConsumer(Consumer):
    """In-memory message consumer."""

    def __init__(self, broker: InMemoryBroker | None = None):
        self.broker = broker or _broker
        self.logger = get_logger(f"{__name__}.Consumer")
        self.topic: str | None = None
        self.options: ConsumeOptions | None = None

    async def subscribe(self, topic: str, *, options: ConsumeOptions) -> None:
        """Subscribe to a topic."""
        self.topic = topic
        self.options = options

        async with self.broker._lock:
            topic_state = self.broker.topics[topic]
            topic_state.groups.add(options.group)

            # Initialize queues if needed
            if options.group not in topic_state.pending:
                topic_state.pending[options.group] = deque()
            if options.group not in topic_state.dlq:
                topic_state.dlq[options.group] = deque()

    async def poll(self, *, max_messages: int | None = None) -> list[DeliveredMessage]:
        """Poll for available messages."""
        if not self.topic or not self.options:
            raise ConsumeError("Consumer not subscribed to any topic")

        max_msgs = max_messages or self.options.prefetch
        delivered: list[DeliveredMessage] = []

        async with self.broker._lock:
            topic_state = self.broker.topics[self.topic]

            # Clean up expired messages first
            await self.broker._cleanup_expired_messages(topic_state, self.options.group)

            current_time = self.broker._get_current_time()

            # Poll from partition queues first (for ordering)
            for partition_key, queue in topic_state.partition_queues[self.options.group].items():
                if len(delivered) >= max_msgs:
                    break

                # Skip if partition has in-flight message (ordering)
                if partition_key in topic_state.partition_in_flight[self.options.group]:
                    continue

                while queue and len(delivered) < max_msgs:
                    msg = queue.popleft()

                    # Check if scheduled for future delivery
                    if msg.scheduled_for and current_time < msg.scheduled_for:
                        queue.appendleft(msg)  # Put back
                        break

                    # Set visibility timeout
                    visibility_timeout = self.options.visibility_timeout_seconds or DEFAULT_VISIBILITY_TIMEOUT
                    msg.visibility_deadline = current_time + visibility_timeout

                    # Move to in-flight
                    topic_state.in_flight[msg.delivery_tag] = msg
                    topic_state.partition_in_flight[self.options.group][partition_key] = msg

                    delivered_msg = DeliveredMessage(
                        message=msg.message,
                        received_at=utcnow(),
                        attempt=msg.attempt,
                        delivery_tag=msg.delivery_tag,
                        scheduled_for=datetime.fromtimestamp(msg.scheduled_for) if msg.scheduled_for else None
                    )
                    delivered.append(delivered_msg)
                    break  # Only one per partition for ordering

            # Poll from general pending queue
            pending_queue = topic_state.pending[self.options.group]
            while pending_queue and len(delivered) < max_msgs:
                msg = pending_queue.popleft()

                # Check if scheduled for future delivery
                if msg.scheduled_for and current_time < msg.scheduled_for:
                    pending_queue.appendleft(msg)  # Put back
                    break

                # Set visibility timeout
                visibility_timeout = self.options.visibility_timeout_seconds or DEFAULT_VISIBILITY_TIMEOUT
                msg.visibility_deadline = current_time + visibility_timeout

                # Move to in-flight
                topic_state.in_flight[msg.delivery_tag] = msg

                delivered_msg = DeliveredMessage(
                    message=msg.message,
                    received_at=utcnow(),
                    attempt=msg.attempt,
                    delivery_tag=msg.delivery_tag,
                    scheduled_for=datetime.fromtimestamp(msg.scheduled_for) if msg.scheduled_for else None
                )
                delivered.append(delivered_msg)

        if not delivered:
            # Sleep for poll interval if no messages
            await asyncio.sleep(self.options.poll_interval_seconds)

        return delivered

    async def ack(self, delivery_tag: str) -> None:
        """Acknowledge message processing."""
        async with self.broker._lock:
            if self.topic and delivery_tag in self.broker.topics[self.topic].in_flight:
                msg = self.broker.topics[self.topic].in_flight.pop(delivery_tag)

                # Remove from partition in-flight if applicable
                if msg.partition_key and self.options:
                    partition_in_flight = self.broker.topics[self.topic].partition_in_flight[self.options.group]
                    if partition_in_flight.get(msg.partition_key) == msg:
                        del partition_in_flight[msg.partition_key]
            else:
                raise AckError(f"Message with delivery tag {delivery_tag} not found")

    async def nack(
        self,
        delivery_tag: str,
        *,
        requeue: bool = True,
        delay_seconds: int | None = None
    ) -> None:
        """Negatively acknowledge message processing."""
        if not self.topic or not self.options:
            raise AckError("Consumer not subscribed")

        async with self.broker._lock:
            topic_state = self.broker.topics[self.topic]

            if delivery_tag not in topic_state.in_flight:
                raise AckError(f"Message with delivery tag {delivery_tag} not found")

            msg = topic_state.in_flight.pop(delivery_tag)

            # Remove from partition in-flight if applicable
            if msg.partition_key:
                partition_in_flight = topic_state.partition_in_flight[self.options.group]
                if partition_in_flight.get(msg.partition_key) == msg:
                    del partition_in_flight[msg.partition_key]

            if not requeue:
                return

            msg.attempt += 1

            # Check if max retries exceeded
            if msg.attempt > self.options.max_retries:
                if self.options.dead_letter_topic:
                    # Move to DLQ
                    topic_state.dlq[self.options.group].append(msg)
                    self.logger.warning(
                        "Message moved to DLQ after max retries",
                        extra={
                            "message_id": msg.message_id,
                            "attempt": msg.attempt,
                            "max_retries": self.options.max_retries
                        }
                    )
                else:
                    self.logger.warning(
                        "Message dropped after max retries (no DLQ configured)",
                        extra={
                            "message_id": msg.message_id,
                            "attempt": msg.attempt,
                            "max_retries": self.options.max_retries
                        }
                    )
                return

            # Calculate delay
            if delay_seconds is not None:
                delay = float(delay_seconds)
            else:
                delay = self.broker._calculate_backoff_delay(msg.attempt)

            msg.scheduled_for = self.broker._get_current_time() + delay
            msg.visibility_deadline = None
            msg.delivery_tag = new_uuid()

            # Requeue
            if msg.partition_key:
                topic_state.partition_queues[self.options.group][msg.partition_key].append(msg)
            else:
                topic_state.pending[self.options.group].append(msg)

    async def close(self) -> None:
        """Close the consumer."""
        self.topic = None
        self.options = None


class InMemoryAdmin(Admin):
    """In-memory broker admin operations."""

    def __init__(self, broker: InMemoryBroker | None = None):
        self.broker = broker or _broker

    async def ensure_topic(
        self,
        topic: str,
        *,
        fifo: bool = False,
        _partitions: int | None = None
    ) -> None:
        """Ensure topic exists."""
        async with self.broker._lock:
            # Topic is created automatically when accessed
            _ = self.broker.topics[topic]

    async def purge(self, topic: str, *, group: str | None = None) -> None:
        """Purge messages from topic or group."""
        async with self.broker._lock:
            if topic not in self.broker.topics:
                return

            topic_state = self.broker.topics[topic]

            if group:
                # Purge specific group
                topic_state.pending[group].clear()
                topic_state.dlq[group].clear()
                topic_state.partition_queues[group].clear()

                # Remove in-flight messages for this group
                to_remove = []
                for tag, msg in topic_state.in_flight.items():
                    if tag.startswith(f"{group}:"):  # Assuming delivery tags are prefixed
                        to_remove.append(tag)
                for tag in to_remove:
                    del topic_state.in_flight[tag]
            else:
                # Purge entire topic
                topic_state.pending.clear()
                topic_state.dlq.clear()
                topic_state.partition_queues.clear()
                topic_state.in_flight.clear()
                topic_state.partition_in_flight.clear()
