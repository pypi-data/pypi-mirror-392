"""Outbox service for business logic."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from ..utils.logging import get_logger
from ..utils.tracing import trace_async
from .repository import OutboxRepository
from .schemas import OutboxItemCreate, OutboxItemOut

logger = get_logger(__name__)


class OutboxService:
    """Business logic for outbox operations."""

    def __init__(self, repository: OutboxRepository) -> None:
        self.repository = repository

    @trace_async
    async def enqueue(
        self,
        *,
        topic: str,
        payload: dict[str, Any],
        user_id: UUID | None = None,
        priority: int = 100,
        scheduled_at: datetime | None = None
    ) -> OutboxItemOut:
        """Enqueue item to outbox."""
        data = OutboxItemCreate(
            user_id=user_id,
            topic=topic,
            payload=payload,
            priority=priority,
            scheduled_at=scheduled_at
        )

        created_item: OutboxItemOut = await self.repository.create(data)
        return created_item

    @trace_async
    async def claim_batch(
        self,
        *,
        limit: int = 50,
        max_attempts: int = 5
    ) -> list[OutboxItemOut]:
        """Claim a batch of outbox items for processing."""
        claimed_items: list[OutboxItemOut] = await self.repository.claim_batch(
            limit=limit,
            max_attempts=max_attempts
        )
        return claimed_items

    @trace_async
    async def mark_succeeded(self, item_id: UUID, result: dict[str, Any]) -> OutboxItemOut | None:
        """Mark outbox item as succeeded."""
        succeeded_item: OutboxItemOut = await self.repository.mark_succeeded(item_id, result)
        return succeeded_item

    @trace_async
    async def mark_failed(
        self,
        item_id: UUID,
        error_msg: str,
        attempts: int,
        max_attempts: int = 5
    ) -> OutboxItemOut | None:
        """Mark outbox item as failed or dead."""
        failed_item: OutboxItemOut = await self.repository.mark_failed(
            item_id=item_id,
            error_msg=error_msg,
            attempts=attempts,
            max_attempts=max_attempts
        )
        return failed_item
