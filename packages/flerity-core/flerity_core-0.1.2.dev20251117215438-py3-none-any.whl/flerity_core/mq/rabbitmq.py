"""
RabbitMQ message queue implementation.

Provides production-ready RabbitMQ backend with:
- Async operations using aio-pika
- Connection pooling and management
- Dead letter exchange support
- Message durability and persistence
- Exponential backoff retry
"""

import asyncio
import json
import logging
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

try:
    import aio_pika
    from aio_pika import DeliveryMode
    from aio_pika import Message as RabbitMessage
    from aio_pika.exceptions import AMQPException
except ImportError:
    aio_pika = None
    RabbitMessage = None
    DeliveryMode = None
    AMQPException = Exception

from .ports import (
    AckError,
    Admin,
    ConsumeError,
    ConsumeOptions,
    Consumer,
    DeliveredMessage,
    Message,
    Producer,
    PublishError,
    PublishOptions,
    build_headers,
    ensure_json,
    validate_size,
)

try:
    from ..utils.ids import new_uuid
    from ..utils.logging import get_logger
    from ..utils.retry import exponential_backoff
except ImportError:
    import uuid
    def new_uuid() -> str:
        return str(uuid.uuid4())

    def get_logger(name: str | None = None) -> logging.Logger:
        return logging.getLogger(name or __name__)

    def exponential_backoff(base_delay: float, multiplier: float = 2.0,
                          max_delay: float | None = None, jitter: bool = False) -> Callable[[int], float]:
        def backoff_func(attempt: int) -> float:
            delay = min(base_delay * (multiplier ** attempt), max_delay or 30.0)
            return delay
        return backoff_func


logger = get_logger(__name__)


class RabbitMqProducer(Producer):
    """RabbitMQ message producer with connection pooling."""

    def __init__(
        self,
        url: str = "amqp://localhost:5672/",
        pool_size: int = 10,
        max_retries: int = 3
    ):
        if aio_pika is None:
            raise ImportError("aio-pika is required for RabbitMQ backend")

        self.url = url
        self.pool_size = pool_size
        self.max_retries = max_retries
        self._connection_pool = None
        self._channel_pool = None

    async def _get_connection(self) -> Any:
        """Get or create connection for test compatibility."""
        if self._connection_pool is None:
            if aio_pika:
                self._connection_pool = await aio_pika.connect_robust(self.url)
        return self._connection_pool

    async def _get_connection_pool(self) -> Any:
        """Get or create connection pool."""
        if self._connection_pool is None:
            self._connection_pool = aio_pika.pool.Pool(
                aio_pika.connect_robust,
                max_size=self.pool_size,
                url=self.url
            )
        return self._connection_pool

    async def _get_channel_pool(self) -> Any:
        """Get or create channel pool."""
        if self._channel_pool is None:
            connection_pool = await self._get_connection_pool()
            self._channel_pool = aio_pika.pool.Pool(
                self._get_channel,
                max_size=self.pool_size * 2,
                connection_pool=connection_pool
            )
        return self._channel_pool

    async def _get_channel(self, connection_pool: Any) -> Any:
        """Get channel from connection pool."""
        async with connection_pool.acquire() as connection:
            return await connection.channel()

    async def publish(
        self,
        topic: str,
        payload: dict[str, Any],
        *,
        options: PublishOptions | None = None
    ) -> str:
        """Publish single message to RabbitMQ exchange."""
        options = options or PublishOptions()
        payload = ensure_json(payload)
        validate_size(payload, options.content_size_limit_bytes)

        headers = build_headers(
            idempotency_key=options.idempotency_key,
            partition_key=options.partition_key,
            schema=options.schema
        )

        message_body = json.dumps(payload).encode('utf-8')
        message_id = new_uuid()

        for attempt in range(self.max_retries + 1):
            try:
                connection = await self._get_connection()
                channel = await connection.channel()

                # Declare exchange
                exchange = await channel.declare_exchange(
                    topic,
                    aio_pika.ExchangeType.TOPIC,
                    durable=True
                )

                # Create message
                rabbit_message = RabbitMessage(
                    message_body,
                    headers=headers,
                    message_id=message_id,
                    delivery_mode=DeliveryMode.PERSISTENT,
                    timestamp=datetime.now(UTC)
                )

                # Set routing key
                routing_key = options.partition_key or "default"

                # Publish message
                await exchange.publish(
                    rabbit_message,
                    routing_key=routing_key,
                    timeout=options.timeout_seconds
                )

                logger.info(
                    "Published message to RabbitMQ",
                    extra={
                        "topic": topic,
                        "message_id": message_id,
                        "routing_key": routing_key,
                        "payload_size": len(message_body)
                    }
                )

                return message_id

            except AMQPException as e:
                if attempt < self.max_retries:
                    backoff_func = exponential_backoff(0.1, 2.0, 5.0, True)
                    delay = backoff_func(attempt)
                    await asyncio.sleep(delay)
                    continue

                logger.error(
                    "Failed to publish to RabbitMQ",
                    extra={"topic": topic, "error": str(e), "attempt": attempt}
                )
                raise PublishError(f"RabbitMQ publish failed: {e}") from e
            except Exception as e:
                logger.error("Unexpected error publishing to RabbitMQ", extra={"error": str(e)})
                raise PublishError(f"Unexpected RabbitMQ error: {e}") from e

        raise PublishError("Max retries exceeded")

    async def publish_many(
        self,
        topic: str,
        payloads: list[dict[str, Any]],
        *,
        options: PublishOptions | None = None
    ) -> list[str]:
        """Publish multiple messages to RabbitMQ."""
        if not payloads:
            return []

        options = options or PublishOptions()

        # Validate all payloads
        for payload in payloads:
            ensure_json(payload)
            validate_size(payload, options.content_size_limit_bytes)

        message_ids = []

        try:
            connection = await self._get_connection()
            channel = await connection.channel()

            # Declare exchange
            exchange = await channel.declare_exchange(
                topic,
                aio_pika.ExchangeType.TOPIC,
                durable=True
            )

            # Publish all messages
            for payload in payloads:
                headers = build_headers(
                    idempotency_key=options.idempotency_key,
                    partition_key=options.partition_key,
                    schema=options.schema
                )

                message_body = json.dumps(payload).encode('utf-8')
                message_id = new_uuid()

                rabbit_message = RabbitMessage(
                    message_body,
                    headers=headers,
                    message_id=message_id,
                    delivery_mode=DeliveryMode.PERSISTENT,
                    timestamp=datetime.now(UTC)
                )

                routing_key = options.partition_key or "default"

                await exchange.publish(
                    rabbit_message,
                    routing_key=routing_key,
                    timeout=options.timeout_seconds
                )

                message_ids.append(message_id)

            logger.info(
                f"Published {len(message_ids)} messages to RabbitMQ",
                extra={"topic": topic, "count": len(message_ids)}
            )

            return message_ids

        except AMQPException as e:
            raise PublishError(f"RabbitMQ batch publish failed: {e}") from e

    async def close(self) -> None:
        """Close RabbitMQ producer."""
        if self._channel_pool:
            await self._channel_pool.close()
        if self._connection_pool:
            if hasattr(self._connection_pool, 'close'):
                await self._connection_pool.close()
            self._connection_pool = None
        logger.info("RabbitMQ producer closed")

    @property
    def _connection(self) -> Any:
        """For test compatibility."""
        return self._connection_pool

    @_connection.setter
    def _connection(self, value: Any) -> None:
        """For test compatibility."""
        self._connection_pool = value


class RabbitMqConsumer(Consumer):
    """RabbitMQ message consumer with dead letter queue support."""

    def __init__(
        self,
        url: str = "amqp://localhost:5672/",
        max_retries: int = 3
    ):
        if aio_pika is None:
            raise ImportError("aio-pika is required for RabbitMQ backend")

        self.url = url
        self.max_retries = max_retries
        self._connection: Any = None
        self._channel: Any = None
        self._queue: Any = None
        self._options: ConsumeOptions | None = None
        self._consuming = False

    async def _get_connection(self) -> Any:
        """Get or create connection."""
        if self._connection is None or self._connection.is_closed:
            self._connection = await aio_pika.connect_robust(self.url)
        return self._connection

    async def _get_channel(self) -> Any:
        """Get or create channel."""
        if self._channel is None or self._channel.is_closed:
            connection = await self._get_connection()
            self._channel = await connection.channel()
            prefetch_count = self._options.prefetch if self._options is not None else 10
            await self._channel.set_qos(prefetch_count=prefetch_count)
        return self._channel

    async def subscribe(self, topic: str, *, options: ConsumeOptions) -> None:
        """Subscribe to RabbitMQ queue."""
        self._options = options

        try:
            channel = await self._get_channel()

            # Declare exchange
            exchange = await channel.declare_exchange(
                topic,
                aio_pika.ExchangeType.TOPIC,
                durable=True
            )

            # Declare dead letter exchange if specified
            dlx_name = None
            if options.dead_letter_topic:
                await channel.declare_exchange(
                    options.dead_letter_topic,
                    aio_pika.ExchangeType.TOPIC,
                    durable=True
                )
                dlx_name = options.dead_letter_topic

            # Declare queue with dead letter configuration
            queue_args = {}
            if dlx_name:
                queue_args.update({
                    "x-dead-letter-exchange": dlx_name,
                    "x-max-retries": options.max_retries
                })

            queue_name = f"{topic}.{options.group}"
            self._queue = await channel.declare_queue(
                queue_name,
                durable=True,
                arguments=queue_args
            )

            # Bind queue to exchange
            assert self._queue is not None  # Help mypy understand this is not None
            await self._queue.bind(exchange, routing_key="#")

            logger.info(
                "Subscribed to RabbitMQ queue",
                extra={
                    "topic": topic,
                    "queue": queue_name,
                    "group": options.group,
                    "dead_letter_topic": options.dead_letter_topic
                }
            )

        except AMQPException as e:
            raise ConsumeError(f"Failed to subscribe to RabbitMQ: {e}") from e

    async def poll(self, *, max_messages: int | None = None) -> list[DeliveredMessage]:
        """Poll for messages from RabbitMQ queue."""
        if not self._queue or not self._options:
            raise ConsumeError("Consumer not subscribed to any topic")

        max_messages = max_messages or self._options.prefetch
        messages = []

        try:
            # Get messages up to max_messages
            for _ in range(max_messages):
                try:
                    rabbit_message = await asyncio.wait_for(
                        self._queue.get(timeout=self._options.poll_interval_seconds),
                        timeout=self._options.poll_interval_seconds
                    )

                    if rabbit_message is None:
                        break

                    # Parse message
                    try:
                        payload = json.loads(rabbit_message.body.decode('utf-8'))
                    except json.JSONDecodeError:
                        logger.warning(
                            "Failed to parse RabbitMQ message body as JSON",
                            extra={"message_id": rabbit_message.message_id}
                        )
                        await rabbit_message.nack(requeue=False)
                        continue

                    # Extract headers
                    headers = rabbit_message.headers or {}
                    headers = {k: str(v) for k, v in headers.items()}

                    # Extract attempt count
                    attempt = int(headers.get('x-attempt', '0'))

                    message = Message(
                        topic=rabbit_message.exchange,
                        key=headers.get('x-partition-key'),
                        payload=payload,
                        headers=headers
                    )

                    delivered = DeliveredMessage(
                        message=message,
                        received_at=datetime.now(UTC),
                        attempt=attempt,
                        delivery_tag=str(rabbit_message.delivery_tag)
                    )

                    messages.append(delivered)

                except TimeoutError:
                    break

            return messages

        except AMQPException as e:
            raise ConsumeError(f"RabbitMQ poll failed: {e}") from e

    async def ack(self, delivery_tag: str) -> None:
        """Acknowledge message."""
        if not self._channel:
            raise AckError("Consumer not subscribed to any topic")

        try:
            delivery_tag_int = int(delivery_tag)
            await self._channel.basic_ack(delivery_tag=delivery_tag_int)

        except AMQPException as e:
            raise AckError(f"RabbitMQ ack failed: {e}") from e

    async def nack(
        self,
        delivery_tag: str,
        *,
        requeue: bool = True,
        delay_seconds: int | None = None
    ) -> None:
        """Negative acknowledge message."""
        if not self._channel:
            raise AckError("Consumer not subscribed to any topic")

        try:
            delivery_tag_int = int(delivery_tag)
            await self._channel.basic_nack(delivery_tag=delivery_tag_int, requeue=requeue)

        except AMQPException as e:
            raise AckError(f"RabbitMQ nack failed: {e}") from e

    async def start_consuming(self, topic: str, *, options: ConsumeOptions) -> None:
        """Start consuming messages."""
        await self.subscribe(topic, options=options)

    async def stop_consuming(self) -> None:
        """Stop consuming messages."""
        self._consuming = False
        await self.close()

    async def close(self) -> None:
        """Close RabbitMQ consumer."""
        if self._channel and not self._channel.is_closed:
            await self._channel.close()

        if self._connection and not self._connection.is_closed:
            await self._connection.close()

        logger.info("RabbitMQ consumer closed")


class RabbitMqAdmin(Admin):
    """RabbitMQ administrative operations."""

    def __init__(self, url: str = "amqp://localhost:5672/"):
        if aio_pika is None:
            raise ImportError("aio-pika is required for RabbitMQ backend")

        self.url = url
        self._connection = None
        self._channel = None

    async def _get_connection(self) -> Any:
        """Get or create connection."""
        if self._connection is None or self._connection.is_closed:
            self._connection = await aio_pika.connect_robust(self.url)
        return self._connection

    async def _get_channel(self) -> Any:
        """Get or create channel."""
        if self._channel is None or self._channel.is_closed:
            connection = await self._get_connection()
            self._channel = await connection.channel()
        return self._channel

    async def ensure_topic(
        self,
        topic: str,
        *,
        fifo: bool = False,
        _partitions: int | None = None
    ) -> None:
        """Ensure RabbitMQ exchange exists."""
        try:
            channel = await self._get_channel()

            # Declare exchange
            await channel.declare_exchange(
                topic,
                type="topic",
                durable=True
            )

            logger.info(
                "RabbitMQ exchange ensured",
                extra={"topic": topic, "fifo": fifo}
            )

        except AMQPException as e:
            raise ConsumeError(f"Failed to ensure RabbitMQ exchange: {e}") from e

    async def purge(self, topic: str, *, group: str | None = None) -> None:
        """Purge messages from RabbitMQ queue."""
        try:
            channel = await self._get_channel()

            if group:
                queue_name = f"{topic}.{group}"
                queue = await channel.declare_queue(queue_name, passive=True)
                await queue.purge()

                logger.info(
                    "RabbitMQ queue purged",
                    extra={"topic": topic, "group": group}
                )
            else:
                # Cannot purge entire exchange, would need to purge all queues
                logger.warning(
                    "Cannot purge entire RabbitMQ exchange, specify group",
                    extra={"topic": topic}
                )

        except AMQPException as e:
            raise ConsumeError(f"Failed to purge RabbitMQ queue: {e}") from e

    async def create_topic(self, topic: str, *, dead_letter_topic: str | None = None) -> None:
        """Create RabbitMQ exchange."""
        await self.ensure_topic(topic)
        if dead_letter_topic:
            await self.ensure_topic(dead_letter_topic)

    async def delete_topic(self, topic: str) -> None:
        """Delete RabbitMQ exchange."""
        try:
            channel = await self._get_channel()
            exchange = await channel.get_exchange(topic)
            await exchange.delete()

            logger.info("RabbitMQ exchange deleted", extra={"topic": topic})

        except AMQPException as e:
            raise ConsumeError(f"Failed to delete RabbitMQ exchange: {e}") from e

    async def topic_exists(self, topic: str) -> bool:
        """Check if RabbitMQ exchange exists."""
        try:
            channel = await self._get_channel()
            await channel.get_exchange(topic, ensure=False)
            return True
        except AMQPException:
            return False

    async def create_queue(self, queue_name: str, *, durable: bool = True) -> None:
        """Create RabbitMQ queue."""
        try:
            channel = await self._get_channel()
            await channel.declare_queue(queue_name, durable=durable)

            logger.info("RabbitMQ queue created", extra={"queue": queue_name})

        except AMQPException as e:
            raise ConsumeError(f"Failed to create RabbitMQ queue: {e}") from e

    async def bind_queue(self, queue_name: str, exchange_name: str, routing_key: str) -> None:
        """Bind RabbitMQ queue to exchange."""
        try:
            channel = await self._get_channel()
            queue = await channel.declare_queue(queue_name, passive=True)
            exchange = await channel.get_exchange(exchange_name)
            await queue.bind(exchange, routing_key=routing_key)

            logger.info(
                "RabbitMQ queue bound to exchange",
                extra={
                    "queue": queue_name,
                    "exchange": exchange_name,
                    "routing_key": routing_key
                }
            )

        except AMQPException as e:
            raise ConsumeError(f"Failed to bind RabbitMQ queue: {e}") from e

    async def close(self) -> None:
        """Close RabbitMQ admin connection."""
        if self._channel and not self._channel.is_closed:
            await self._channel.close()

        if self._connection and not self._connection.is_closed:
            await self._connection.close()
            self._connection = None

        logger.info("RabbitMQ admin closed")
