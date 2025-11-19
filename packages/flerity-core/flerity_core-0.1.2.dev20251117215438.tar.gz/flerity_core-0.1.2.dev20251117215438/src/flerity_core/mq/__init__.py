"""
Message queue implementations and factory.

Provides production-ready message queue backends:
- InMemory: For testing and development
- SQS: AWS Simple Queue Service
- RabbitMQ: AMQP message broker
- Redis: Redis Streams for lightweight messaging

Usage:
    from flerity_core.mq import create_producer, create_consumer, create_admin
    
    # Use factory (configured via environment)
    producer = create_producer()
    consumer = create_consumer()
    admin = create_admin()
    
    # Or create specific backends
    from flerity_core.mq.sqs import SqsProducer
    producer = SqsProducer(region="us-west-2")
"""

# Factory and configuration
from .factory import (
    MqBackend,
    MqConfig,
    MqFactory,
    create_admin,
    create_consumer,
    create_producer,
    get_factory,
    publish_event,
    set_factory,
    setup_dead_letter_queues,
)

# In-memory implementation (always available)
from .inmem import (
    InMemoryAdmin,
    InMemoryConsumer,
    InMemoryProducer,
)
from .ports import (
    AckError,
    Admin,
    ConsumeError,
    ConsumeOptions,
    Consumer,
    DeliveredMessage,
    # Data structures
    Message,
    MessageHeaders,
    # Exceptions
    MqError,
    OversizedMessageError,
    # Protocols
    Producer,
    PublishError,
    PublishOptions,
    SerializationError,
    # Utilities
    build_headers,
    compute_idempotency_key,
    ensure_json,
    validate_size,
)

# Import with proper type handling
try:
    from .sqs import SqsAdmin, SqsConsumer, SqsProducer
except ImportError:
    SqsProducer = None  # type: ignore[assignment,misc]
    SqsConsumer = None  # type: ignore[assignment,misc]
    SqsAdmin = None  # type: ignore[assignment,misc]

try:
    from .rabbitmq import RabbitMqAdmin, RabbitMqConsumer, RabbitMqProducer
except ImportError:
    RabbitMqProducer = None  # type: ignore[assignment,misc]
    RabbitMqConsumer = None  # type: ignore[assignment,misc]
    RabbitMqAdmin = None  # type: ignore[assignment,misc]

try:
    from .redis import RedisAdmin, RedisConsumer, RedisProducer
except ImportError:
    RedisProducer = None  # type: ignore[assignment,misc]
    RedisConsumer = None  # type: ignore[assignment,misc]
    RedisAdmin = None  # type: ignore[assignment,misc]


__all__ = [
    # Core interfaces
    "Producer",
    "Consumer",
    "Admin",
    "Message",
    "DeliveredMessage",
    "PublishOptions",
    "ConsumeOptions",
    "MessageHeaders",

    # Exceptions
    "MqError",
    "PublishError",
    "ConsumeError",
    "AckError",
    "SerializationError",
    "OversizedMessageError",

    # Utilities
    "build_headers",
    "ensure_json",
    "compute_idempotency_key",
    "validate_size",

    # Factory
    "MqBackend",
    "MqConfig",
    "MqFactory",
    "get_factory",
    "set_factory",
    "create_producer",
    "create_consumer",
    "create_admin",
    "publish_event",
    "setup_dead_letter_queues",

    # Implementations
    "InMemoryProducer",
    "InMemoryConsumer",
    "InMemoryAdmin",
    "SqsProducer",
    "SqsConsumer",
    "SqsAdmin",
    "RabbitMqProducer",
    "RabbitMqConsumer",
    "RabbitMqAdmin",
    "RedisProducer",
    "RedisConsumer",
    "RedisAdmin",
]
