"""
Message queue factory and configuration management.

Provides centralized configuration and factory for creating message queue
backends based on environment configuration.
"""

import os
from enum import Enum
from typing import Any

from .inmem import InMemoryAdmin, InMemoryConsumer, InMemoryProducer
from .ports import Admin, Consumer, Producer

try:
    from ..utils.logging import get_logger
except ImportError:
    import logging
    def get_logger(name: str | None = None) -> logging.Logger:
        return logging.getLogger(name or __name__)


logger = get_logger(__name__)


class MqBackend(str, Enum):
    """Supported message queue backends."""
    INMEMORY = "inmemory"
    SQS = "sqs"
    RABBITMQ = "rabbitmq"
    REDIS = "redis"


class MqConfig:
    """Message queue configuration."""

    def __init__(
        self,
        backend: MqBackend = MqBackend.INMEMORY,
        **kwargs: Any
    ):
        self.backend = backend
        self.config = kwargs

    @classmethod
    def from_env(cls) -> "MqConfig":
        """Create configuration from environment variables."""
        backend_str = os.getenv("MQ_BACKEND", "inmemory").lower()

        try:
            backend = MqBackend(backend_str)
        except ValueError:
            logger.warning(
                f"Unknown MQ backend '{backend_str}', falling back to inmemory",
                extra={"backend": backend_str}
            )
            backend = MqBackend.INMEMORY

        # Backend-specific configuration
        config = {}

        if backend == MqBackend.SQS:
            config.update({
                "region": os.getenv("AWS_REGION", "us-east-1"),
                "endpoint_url": os.getenv("SQS_ENDPOINT_URL"),  # For LocalStack
            })

        elif backend == MqBackend.RABBITMQ:
            config.update({
                "url": os.getenv("RABBITMQ_URL", "amqp://localhost:5672/"),
                "pool_size": os.getenv("RABBITMQ_POOL_SIZE", "10"),
                "max_retries": os.getenv("RABBITMQ_MAX_RETRIES", "3"),
            })

        elif backend == MqBackend.REDIS:
            config.update({
                "url": os.getenv("REDIS_URL", "redis://localhost:6379"),
                "max_connections": os.getenv("REDIS_MAX_CONNECTIONS", "10"),
                "max_retries": os.getenv("REDIS_MAX_RETRIES", "3"),
            })

        return cls(backend=backend, **config)

    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "backend": self.backend.value,
            **self.config
        }


class MqFactory:
    """Factory for creating message queue components."""

    def __init__(self, config: MqConfig | None = None):
        self.config = config or MqConfig.from_env()

    def create_producer(self) -> Producer:
        """Create message producer based on configuration."""
        backend = self.config.backend

        if backend == MqBackend.INMEMORY:
            return InMemoryProducer()

        elif backend == MqBackend.SQS:
            try:
                from .sqs import SqsProducer
                return SqsProducer(
                    region=self.config.config.get("region", "us-east-1"),
                    endpoint_url=self.config.config.get("endpoint_url")
                )
            except ImportError as e:
                logger.error(
                    "SQS backend not available, falling back to inmemory",
                    extra={"error": str(e)}
                )
                return InMemoryProducer()

        elif backend == MqBackend.RABBITMQ:
            try:
                from .rabbitmq import RabbitMqProducer
                return RabbitMqProducer(
                    url=self.config.config.get("url", "amqp://localhost:5672/"),
                    pool_size=self.config.config.get("pool_size", 10),
                    max_retries=self.config.config.get("max_retries", 3)
                )
            except ImportError as e:
                logger.error(
                    "RabbitMQ backend not available, falling back to inmemory",
                    extra={"error": str(e)}
                )
                return InMemoryProducer()

        elif backend == MqBackend.REDIS:
            try:
                from .redis import RedisProducer
                return RedisProducer(
                    url=self.config.config.get("url", "redis://localhost:6379"),
                    max_connections=self.config.config.get("max_connections", 10),
                    max_retries=self.config.config.get("max_retries", 3)
                )
            except ImportError as e:
                logger.error(
                    "Redis backend not available, falling back to inmemory",
                    extra={"error": str(e)}
                )
                return InMemoryProducer()

        else:
            logger.warning(
                f"Unknown backend {backend}, using inmemory",
                extra={"backend": backend}
            )
            return InMemoryProducer()

    def create_consumer(self) -> Consumer:
        """Create message consumer based on configuration."""
        backend = self.config.backend

        if backend == MqBackend.INMEMORY:
            return InMemoryConsumer()

        elif backend == MqBackend.SQS:
            try:
                from .sqs import SqsConsumer
                return SqsConsumer(
                    region=self.config.config.get("region", "us-east-1"),
                    endpoint_url=self.config.config.get("endpoint_url")
                )
            except ImportError as e:
                logger.error(
                    "SQS backend not available, falling back to inmemory",
                    extra={"error": str(e)}
                )
                return InMemoryConsumer()

        elif backend == MqBackend.RABBITMQ:
            try:
                from .rabbitmq import RabbitMqConsumer
                return RabbitMqConsumer(
                    url=self.config.config.get("url", "amqp://localhost:5672/"),
                    max_retries=self.config.config.get("max_retries", 3)
                )
            except ImportError as e:
                logger.error(
                    "RabbitMQ backend not available, falling back to inmemory",
                    extra={"error": str(e)}
                )
                return InMemoryConsumer()

        elif backend == MqBackend.REDIS:
            try:
                from .redis import RedisConsumer
                return RedisConsumer(
                    url=self.config.config.get("url", "redis://localhost:6379"),
                    max_connections=self.config.config.get("max_connections", 10)
                )
            except ImportError as e:
                logger.error(
                    "Redis backend not available, falling back to inmemory",
                    extra={"error": str(e)}
                )
                return InMemoryConsumer()

        else:
            logger.warning(
                f"Unknown backend {backend}, using inmemory",
                extra={"backend": backend}
            )
            return InMemoryConsumer()

    def create_admin(self) -> Admin:
        """Create message queue admin based on configuration."""
        backend = self.config.backend

        if backend == MqBackend.INMEMORY:
            return InMemoryAdmin()

        elif backend == MqBackend.SQS:
            try:
                from .sqs import SqsAdmin
                return SqsAdmin(
                    region=self.config.config.get("region", "us-east-1"),
                    endpoint_url=self.config.config.get("endpoint_url")
                )
            except ImportError as e:
                logger.error(
                    "SQS backend not available, falling back to inmemory",
                    extra={"error": str(e)}
                )
                return InMemoryAdmin()

        elif backend == MqBackend.RABBITMQ:
            try:
                from .rabbitmq import RabbitMqAdmin
                return RabbitMqAdmin(
                    url=self.config.config.get("url", "amqp://localhost:5672/")
                )
            except ImportError as e:
                logger.error(
                    "RabbitMQ backend not available, falling back to inmemory",
                    extra={"error": str(e)}
                )
                return InMemoryAdmin()

        elif backend == MqBackend.REDIS:
            try:
                from .redis import RedisAdmin
                return RedisAdmin(
                    url=self.config.config.get("url", "redis://localhost:6379")
                )
            except ImportError as e:
                logger.error(
                    "Redis backend not available, falling back to inmemory",
                    extra={"error": str(e)}
                )
                return InMemoryAdmin()

        else:
            logger.warning(
                f"Unknown backend {backend}, using inmemory",
                extra={"backend": backend}
            )
            return InMemoryAdmin()


# Global factory instance
_factory: MqFactory | None = None


def get_factory() -> MqFactory:
    """Get global message queue factory."""
    global _factory
    if _factory is None:
        _factory = MqFactory()
    return _factory


def set_factory(factory: MqFactory) -> None:
    """Set global message queue factory."""
    global _factory
    _factory = factory


def create_producer() -> Producer:
    """Create message producer using global factory."""
    return get_factory().create_producer()


def create_consumer() -> Consumer:
    """Create message consumer using global factory."""
    return get_factory().create_consumer()


def create_admin() -> Admin:
    """Create message queue admin using global factory."""
    return get_factory().create_admin()


# Convenience functions for common patterns
async def publish_event(
    topic: str,
    event_type: str,
    payload: dict[str, Any],
    *,
    user_id: str | None = None,
    correlation_id: str | None = None
) -> str:
    """Publish an event message with standard headers."""
    from .ports import PublishOptions

    # Add event metadata to payload
    event_payload = {
        "event_type": event_type,
        "data": payload,
        "timestamp": os.environ.get("CURRENT_TIME") or "2025-10-24T10:14:12.903Z"
    }

    # Build options with headers
    options = PublishOptions(
        idempotency_key=f"{event_type}-{user_id}-{correlation_id}" if user_id and correlation_id else None,
        partition_key=user_id,
        schema=f"event.{event_type}.v1"
    )

    producer = create_producer()
    return await producer.publish(topic, event_payload, options=options)


async def setup_dead_letter_queues(topics: list[str]) -> None:
    """Setup dead letter queues for given topics."""
    admin = create_admin()

    for topic in topics:
        # Ensure main topic
        await admin.ensure_topic(topic)

        # Ensure dead letter topic
        dlq_topic = f"{topic}.dlq"
        await admin.ensure_topic(dlq_topic)

        logger.info(
            "Dead letter queue setup complete",
            extra={"topic": topic, "dlq_topic": dlq_topic}
        )
