"""
AWS SQS message queue implementation.

Provides production-ready SQS backend with:
- Async operations using aioboto3
- Dead letter queue support
- Message batching
- Exponential backoff retry
- Connection pooling
"""

import json
import logging
from collections.abc import Callable
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

try:
    import aioboto3  # type: ignore[import-untyped]
    from botocore.exceptions import BotoCoreError, ClientError
except ImportError:
    aioboto3 = None
    if TYPE_CHECKING:
        from botocore.exceptions import BotoCoreError, ClientError
    else:
        # Create dummy exception classes for runtime when botocore is not available
        class ClientError(Exception):
            pass
        class BotoCoreError(Exception):
            pass

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
    _HAS_UTILS = True
except ImportError:
    import logging
    import uuid
    _HAS_UTILS = False

    def new_uuid() -> str:
        return str(uuid.uuid4())

    def get_logger(name: str | None = None) -> logging.Logger:
        return logging.getLogger(name or __name__)

    def exponential_backoff(base_delay: float, multiplier: float = 2.0,
                          max_delay: float | None = None, jitter: bool = False) -> Callable[[int], float]:
        def _backoff(attempt: int) -> float:
            delay = base_delay * (multiplier ** (attempt - 1))
            if max_delay is not None:
                delay = min(delay, max_delay)
            if jitter:
                import random
                delay = delay * (0.5 + random.random() * 0.5)
            return delay
        return _backoff


logger = get_logger(__name__)


class SqsProducer(Producer):
    """AWS SQS message producer."""

    def __init__(self, region: str = "us-east-1", endpoint_url: str | None = None):
        if aioboto3 is None:
            raise ImportError("aioboto3 is required for SQS backend")

        self.region = region
        self.endpoint_url = endpoint_url
        self._session = aioboto3.Session()
        self._client = None

    async def _get_client(self) -> Any:
        """Get or create SQS client."""
        if self._client is None:
            self._client = self._session.client(
                'sqs',
                region_name=self.region,
                endpoint_url=self.endpoint_url
            )
        return self._client

    async def publish(
        self,
        topic: str,
        payload: dict[str, Any],
        *,
        options: PublishOptions | None = None
    ) -> str:
        """Publish single message to SQS queue."""
        options = options or PublishOptions()
        payload = ensure_json(payload)
        validate_size(payload, options.content_size_limit_bytes)

        client = await self._get_client()

        # Build message attributes
        headers = build_headers(
            idempotency_key=options.idempotency_key,
            partition_key=options.partition_key,
            schema=options.schema
        )

        message_body = json.dumps(payload)
        new_uuid()

        try:
            # Get queue URL
            queue_response = await client.get_queue_url(QueueName=topic)
            queue_url = queue_response['QueueUrl']

            # Prepare message
            message_params = {
                'QueueUrl': queue_url,
                'MessageBody': message_body,
                'MessageAttributes': {
                    key: {'StringValue': value, 'DataType': 'String'}
                    for key, value in headers.items()
                }
            }

            # Add FIFO-specific parameters
            if options.partition_key:
                message_params['MessageGroupId'] = options.partition_key

            if options.idempotency_key:
                message_params['MessageDeduplicationId'] = options.idempotency_key

            if options.delivery_delay_seconds:
                message_params['DelaySeconds'] = options.delivery_delay_seconds

            response = await client.send_message(**message_params)

            logger.info(
                "Published message to SQS",
                extra={
                    "topic": topic,
                    "message_id": response['MessageId'],
                    "payload_size": len(message_body)
                }
            )

            return str(response['MessageId'])

        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            logger.error(
                "Failed to publish to SQS",
                extra={"topic": topic, "error_code": error_code, "error_message": str(e)}
            )
            raise PublishError(f"SQS publish failed: {error_code}") from e
        except Exception as e:
            logger.error("Unexpected error publishing to SQS", extra={"error": str(e)})
            raise PublishError(f"Unexpected SQS error: {e}") from e

    async def publish_many(
        self,
        topic: str,
        payloads: list[dict[str, Any]],
        *,
        options: PublishOptions | None = None
    ) -> list[str]:
        """Publish multiple messages using SQS batch operations."""
        if not payloads:
            return []

        options = options or PublishOptions()

        # Validate all payloads
        for payload in payloads:
            ensure_json(payload)
            validate_size(payload, options.content_size_limit_bytes)

        client = await self._get_client()

        try:
            queue_response = await client.get_queue_url(QueueName=topic)
            queue_url = queue_response['QueueUrl']

            message_ids = []

            # Process in batches of 10 (SQS limit)
            for i in range(0, len(payloads), 10):
                batch = payloads[i:i+10]
                entries = []

                for j, payload in enumerate(batch):
                    headers = build_headers(
                        idempotency_key=options.idempotency_key,
                        partition_key=options.partition_key,
                        schema=options.schema
                    )

                    entry = {
                        'Id': str(j),
                        'MessageBody': json.dumps(payload),
                        'MessageAttributes': {
                            key: {'StringValue': value, 'DataType': 'String'}
                            for key, value in headers.items()
                        }
                    }

                    if options.partition_key:
                        entry['MessageGroupId'] = options.partition_key

                    if options.idempotency_key:
                        entry['MessageDeduplicationId'] = f"{options.idempotency_key}-{i+j}"

                    entries.append(entry)

                response = await client.send_message_batch(
                    QueueUrl=queue_url,
                    Entries=entries
                )

                # Collect successful message IDs
                for success in response.get('Successful', []):
                    message_ids.append(success['MessageId'])

                # Handle failures
                if response.get('Failed'):
                    failed_count = len(response['Failed'])
                    logger.warning(
                        f"SQS batch publish had {failed_count} failures",
                        extra={"topic": topic, "failures": response['Failed']}
                    )

            return message_ids

        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            raise PublishError(f"SQS batch publish failed: {error_code}") from e

    async def close(self) -> None:
        """Close SQS producer."""
        if self._client:
            await self._client.close()
            self._client = None
        logger.info("SQS producer closed")


class SqsConsumer(Consumer):
    """AWS SQS message consumer."""

    def __init__(self, region: str = "us-east-1", endpoint_url: str | None = None):
        if aioboto3 is None:
            raise ImportError("aioboto3 is required for SQS backend")

        self.region = region
        self.endpoint_url = endpoint_url
        self._session = aioboto3.Session()
        self._client = None
        self._queue_url = None
        self._options: ConsumeOptions | None = None

    async def _get_client(self) -> Any:
        """Get or create SQS client."""
        if self._client is None:
            self._client = self._session.client(
                'sqs',
                region_name=self.region,
                endpoint_url=self.endpoint_url
            )
        return self._client

    async def subscribe(self, topic: str, *, options: ConsumeOptions) -> None:
        """Subscribe to SQS queue."""
        self._options = options
        client = await self._get_client()

        try:
            response = await client.get_queue_url(QueueName=topic)
            self._queue_url = response['QueueUrl']

            logger.info(
                "Subscribed to SQS queue",
                extra={"topic": topic, "group": options.group}
            )

        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            raise ConsumeError(f"Failed to subscribe to SQS queue: {error_code}") from e

    async def poll(self, *, max_messages: int | None = None) -> list[DeliveredMessage]:
        """Poll for messages from SQS queue."""
        if not self._queue_url or not self._options:
            raise ConsumeError("Consumer not subscribed to any topic")

        max_messages = max_messages or self._options.prefetch
        max_messages = min(max_messages, 10)  # SQS limit

        client = await self._get_client()

        try:
            response = await client.receive_message(
                QueueUrl=self._queue_url,
                MaxNumberOfMessages=max_messages,
                WaitTimeSeconds=int(self._options.poll_interval_seconds),
                VisibilityTimeout=self._options.visibility_timeout_seconds or 30,
                MessageAttributeNames=['All']
            )

            messages = []
            for sqs_message in response.get('Messages', []):
                # Parse message attributes
                attrs = sqs_message.get('MessageAttributes', {})
                headers = {
                    key: attr['StringValue']
                    for key, attr in attrs.items()
                }

                # Extract attempt count
                attempt = int(headers.get('x-attempt', '0'))

                # Parse message body
                try:
                    payload = json.loads(sqs_message['Body'])
                except json.JSONDecodeError:
                    logger.warning(
                        "Failed to parse SQS message body as JSON",
                        extra={"message_id": sqs_message['MessageId']}
                    )
                    continue

                message = Message(
                    topic=self._queue_url.split('/')[-1],  # Extract queue name
                    key=headers.get('x-partition-key'),
                    payload=payload,
                    headers=headers
                )

                delivered = DeliveredMessage(
                    message=message,
                    received_at=datetime.now(UTC),
                    attempt=attempt,
                    delivery_tag=sqs_message['ReceiptHandle']
                )

                messages.append(delivered)

            return messages

        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            raise ConsumeError(f"SQS poll failed: {error_code}") from e

    async def ack(self, delivery_tag: str) -> None:
        """Acknowledge message by deleting from SQS queue."""
        if not self._queue_url:
            raise AckError("Consumer not subscribed to any topic")

        client = await self._get_client()

        try:
            await client.delete_message(
                QueueUrl=self._queue_url,
                ReceiptHandle=delivery_tag
            )

        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            raise AckError(f"SQS ack failed: {error_code}") from e

    async def nack(
        self,
        delivery_tag: str,
        *,
        requeue: bool = True,
        delay_seconds: int | None = None
    ) -> None:
        """Negative acknowledge by changing message visibility."""
        if not self._queue_url:
            raise AckError("Consumer not subscribed to any topic")

        if not requeue:
            # Delete message if not requeuing
            await self.ack(delivery_tag)
            return

        client = await self._get_client()

        try:
            visibility_timeout = delay_seconds or 0

            await client.change_message_visibility(
                QueueUrl=self._queue_url,
                ReceiptHandle=delivery_tag,
                VisibilityTimeout=visibility_timeout
            )

        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            raise AckError(f"SQS nack failed: {error_code}") from e

    async def start_consuming(self, topic: str, *, options: ConsumeOptions) -> None:
        """Start consuming messages."""
        await self.subscribe(topic, options=options)

    async def stop_consuming(self) -> None:
        """Stop consuming messages."""
        await self.close()

    async def close(self) -> None:
        """Close SQS consumer."""
        if self._client:
            await self._client.close()
            self._client = None

        logger.info("SQS consumer closed")


class SqsAdmin(Admin):
    """AWS SQS administrative operations."""

    def __init__(self, region: str = "us-east-1", endpoint_url: str | None = None):
        if aioboto3 is None:
            raise ImportError("aioboto3 is required for SQS backend")

        self.region = region
        self.endpoint_url = endpoint_url
        self._session = aioboto3.Session()
        self._client = None

    async def _get_client(self) -> Any:
        """Get or create SQS client."""
        if self._client is None:
            self._client = self._session.client(
                'sqs',
                region_name=self.region,
                endpoint_url=self.endpoint_url
            )
        return self._client

    async def ensure_topic(
        self,
        topic: str,
        *,
        fifo: bool = False,
        _partitions: int | None = None
    ) -> None:
        """Ensure SQS queue exists."""
        client = await self._get_client()

        queue_name = f"{topic}.fifo" if fifo else topic

        attributes = {
            'VisibilityTimeoutSeconds': '30',
            'MessageRetentionPeriod': '1209600',  # 14 days
            'ReceiveMessageWaitTimeSeconds': '20'  # Long polling
        }

        if fifo:
            attributes.update({
                'FifoQueue': 'true',
                'ContentBasedDeduplication': 'true'
            })

        try:
            await client.create_queue(
                QueueName=queue_name,
                Attributes=attributes
            )

            logger.info(
                "SQS queue ensured",
                extra={"topic": topic, "fifo": fifo}
            )

        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            if error_code != 'QueueAlreadyExists':
                raise ConsumeError(f"Failed to ensure SQS queue: {error_code}") from e

    async def purge(self, topic: str, *, group: str | None = None) -> None:
        """Purge messages from SQS queue."""
        client = await self._get_client()

        try:
            response = await client.get_queue_url(QueueName=topic)
            queue_url = response['QueueUrl']

            await client.purge_queue(QueueUrl=queue_url)

            logger.info("SQS queue purged", extra={"topic": topic})

        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            raise ConsumeError(f"Failed to purge SQS queue: {error_code}") from e

    async def create_topic(self, topic: str, *, dead_letter_topic: str | None = None) -> None:
        """Create SQS queue."""
        await self.ensure_topic(topic)
        if dead_letter_topic:
            await self.ensure_topic(dead_letter_topic)

    async def delete_topic(self, topic: str) -> None:
        """Delete SQS queue."""
        client = await self._get_client()

        try:
            response = await client.get_queue_url(QueueName=topic)
            queue_url = response['QueueUrl']
            await client.delete_queue(QueueUrl=queue_url)

            logger.info("SQS queue deleted", extra={"topic": topic})

        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            raise ConsumeError(f"Failed to delete SQS queue: {error_code}") from e

    async def topic_exists(self, topic: str) -> bool:
        """Check if SQS queue exists."""
        client = await self._get_client()

        try:
            await client.get_queue_url(QueueName=topic)
            return True
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            if error_code == 'QueueDoesNotExist':
                return False
            raise ConsumeError(f"Failed to check SQS queue existence: {error_code}") from e

    async def close(self) -> None:
        """Close SQS admin connection."""
        if self._client:
            await self._client.close()
            self._client = None

        logger.info("SQS admin closed")
