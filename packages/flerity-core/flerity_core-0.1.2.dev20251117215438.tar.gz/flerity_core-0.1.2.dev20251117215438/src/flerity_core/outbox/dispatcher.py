"""
Transactional Outbox Dispatcher.

Generic dispatcher for processing outbox items using proper service/repository pattern.
Supports async operations with proper error handling, retries, and observability.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Protocol
from uuid import UUID

from ..db.uow import AsyncUnitOfWork
from ..utils.errors import FailedDependency
from ..utils.logging import get_logger
from .repository import OutboxRepository
from .schemas import OutboxItemOut
from .service import OutboxService

logger = get_logger(__name__)


# Type aliases
TransformFn = Callable[[dict[str, Any]], tuple[str, dict[str, Any], dict[str, Any] | None]]


class Producer(Protocol):
    """Protocol for message producer."""
    async def publish(self, topic: str, payload: dict[str, Any], *, options: Any = None) -> str: ...


class UoWFactory(Protocol):
    """Protocol for Unit of Work factory."""
    async def __call__(self) -> AsyncUnitOfWork: ...


@dataclass
class DispatcherSettings:
    """Settings for dispatcher behavior."""
    max_batch_claim: int = 50
    max_attempts: int = 5
    backoff_base_seconds: float = 15.0
    backoff_cap_seconds: float = 900.0


class AsyncOutboxDispatcher:
    """Async dispatcher for Transactional Outbox pattern."""

    def __init__(
        self,
        *,
        producer: Producer,
        uow_factory: UoWFactory,
        transform: TransformFn | None = None,
        settings: DispatcherSettings | None = None,
    ) -> None:
        self.producer = producer
        self.uow_factory = uow_factory
        self.transform = transform
        self.settings = settings or DispatcherSettings()
        self.logger = get_logger(f"{__name__}.AsyncOutboxDispatcher")

    async def process_batch(self) -> int:
        """Process one batch of outbox items."""
        try:
            async with await self.uow_factory() as uow:
                service = OutboxService(OutboxRepository(uow.session))

                claimed_items = await service.claim_batch(
                    limit=self.settings.max_batch_claim,
                    max_attempts=self.settings.max_attempts
                )

                if not claimed_items:
                    return 0

                processed = 0
                for item in claimed_items:
                    try:
                        await self._process_item(item, service)
                        processed += 1
                    except Exception as e:
                        self.logger.error(
                            "Failed to process outbox item",
                            extra={
                                "outbox_id": str(item.id),
                                "error": str(e)
                            }
                        )
                        await service.mark_failed(
                            item_id=item.id,
                            error_msg=str(e),
                            attempts=item.attempts,
                            max_attempts=self.settings.max_attempts
                        )

                await uow.commit()
                return processed

        except Exception as e:
            self.logger.error("Batch processing failed", extra={"error": str(e)})
            raise FailedDependency(f"Outbox processing failed: {e}")

    async def _process_item(self, item: OutboxItemOut, service: OutboxService) -> None:
        """Process a single outbox item."""
        try:
            # Transform payload if needed
            if self.transform:
                topic, message_payload, publish_opts = self.transform(item.payload)
            else:
                topic = item.topic
                message_payload = item.payload
                publish_opts = None

            # Publish message
            message_id = await self.producer.publish(
                topic=topic,
                payload=message_payload,
                options=publish_opts
            )

            # Mark as succeeded
            await service.mark_succeeded(item.id, {"message_id": message_id})

            self.logger.info(
                "Outbox item processed successfully",
                extra={
                    "outbox_id": str(item.id),
                    "topic": topic,
                    "message_id": message_id
                }
            )

        except Exception as e:
            self.logger.error(
                "Failed to process outbox item",
                extra={
                    "outbox_id": str(item.id),
                    "error": str(e),
                    "attempts": item.attempts
                }
            )
            raise


async def enqueue_outbox(
    session: Any,
    *,
    topic: str,
    payload: dict[str, Any],
    user_id: UUID | None = None,
    priority: int = 100,
    scheduled_at: Any = None
) -> str:
    """Enqueue item to outbox using service layer."""
    service = OutboxService(OutboxRepository(session))

    item = await service.enqueue(
        topic=topic,
        payload=payload,
        user_id=user_id,
        priority=priority,
        scheduled_at=scheduled_at
    )

    return str(item.id)
