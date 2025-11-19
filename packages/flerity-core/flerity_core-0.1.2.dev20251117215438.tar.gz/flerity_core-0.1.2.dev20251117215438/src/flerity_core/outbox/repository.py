"""Outbox repository for database operations."""

from __future__ import annotations

from datetime import timedelta
from typing import Any
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from ..utils.clock import utcnow
from ..utils.errors import BadRequest, NotFound
from ..utils.ids import new_uuid
from ..utils.jsonx import canonical_dumps
from ..utils.tracing import trace_async
from .schemas import OutboxItemCreate, OutboxItemOut, OutboxItemUpdate, OutboxStatus, outbox_table


class OutboxRepository:
    """Repository for outbox operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    @trace_async
    async def create(self, data: OutboxItemCreate) -> OutboxItemOut:
        """Create new outbox item."""
        outbox_data = data.model_dump(exclude_none=True)
        outbox_data["id"] = new_uuid()
        outbox_data["payload"] = canonical_dumps(data.payload)

        stmt = sa.insert(outbox_table).values(**outbox_data).returning(outbox_table)
        result = await self.session.execute(stmt)
        row = result.fetchone()

        if not row:
            raise BadRequest("Failed to create outbox item")

        # Convert row to dict and parse payload back to dict
        row_dict = dict(row._mapping)
        if isinstance(row_dict["payload"], str):
            import json
            row_dict["payload"] = json.loads(row_dict["payload"])

        return OutboxItemOut.model_validate(row_dict)

    @trace_async
    async def claim_batch(
        self,
        *,
        limit: int = 50,
        max_attempts: int = 5
    ) -> list[OutboxItemOut]:
        """Claim a batch of outbox items for processing."""
        if limit > 100:
            raise BadRequest("Limit cannot exceed 100")

        # First, select items to claim
        select_stmt = (
            sa.select(outbox_table.c.id)
            .where(
                sa.and_(
                    outbox_table.c.status == "queued",
                    outbox_table.c.scheduled_at <= utcnow(),
                    outbox_table.c.attempts < max_attempts
                )
            )
            .order_by(outbox_table.c.priority.desc(), outbox_table.c.created_at.asc())
            .limit(limit)
        )

        select_result = await self.session.execute(select_stmt)
        item_ids = [row.id for row in select_result.fetchall()]

        if not item_ids:
            return []

        # Update claimed items
        update_stmt = (
            sa.update(outbox_table)
            .where(outbox_table.c.id.in_(item_ids))
            .values(
                status="processing",
                attempts=outbox_table.c.attempts + 1,
                updated_at=utcnow()
            )
            .returning(outbox_table)
        )

        result = await self.session.execute(update_stmt)
        return [OutboxItemOut.model_validate(dict(row._mapping)) for row in result.fetchall()]

    @trace_async
    async def update(self, item_id: UUID, data: OutboxItemUpdate) -> OutboxItemOut:
        """Update outbox item."""
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            existing_item: OutboxItemOut = await self.get(item_id)
            return existing_item

        update_data["updated_at"] = utcnow()

        # Handle JSON fields
        if "result" in update_data and update_data["result"] is not None:
            update_data["result"] = canonical_dumps(update_data["result"])
        if "error" in update_data and update_data["error"] is not None:
            update_data["error"] = canonical_dumps(update_data["error"])

        stmt = (
            sa.update(outbox_table)
            .where(outbox_table.c.id == item_id)
            .values(**update_data)
            .returning(outbox_table)
        )

        result = await self.session.execute(stmt)
        row = result.fetchone()

        if not row:
            raise NotFound(f"Outbox item {item_id} not found")

        # Convert row to dict and validate
        row_dict = dict(row._mapping)
        return OutboxItemOut.model_validate(row_dict)

    @trace_async
    async def get(self, item_id: UUID) -> OutboxItemOut:
        """Get outbox item by ID."""
        stmt = sa.select(outbox_table).where(outbox_table.c.id == item_id)
        result = await self.session.execute(stmt)
        row = result.fetchone()

        if not row:
            raise NotFound(f"Outbox item {item_id} not found")

        # Convert row to dict and validate
        row_dict = dict(row._mapping)
        return OutboxItemOut.model_validate(row_dict)

    @trace_async
    async def mark_succeeded(self, item_id: UUID, result: dict[str, Any]) -> OutboxItemOut:
        """Mark outbox item as succeeded."""
        updated_item: OutboxItemOut = await self.update(item_id, OutboxItemUpdate(
            status="succeeded",
            result=result
        ))
        return updated_item

    @trace_async
    async def mark_failed(
        self,
        item_id: UUID,
        error_msg: str,
        attempts: int,
        backoff_base_seconds: float = 15.0,
        backoff_cap_seconds: float = 900.0,
        max_attempts: int = 5
    ) -> OutboxItemOut:
        """Mark outbox item as failed or dead."""
        status: OutboxStatus = "dead" if attempts >= max_attempts else "failed"

        # Calculate next retry time with exponential backoff
        next_retry = None
        if status == "failed":
            backoff_seconds = min(
                backoff_base_seconds * (2 ** (attempts - 1)),
                backoff_cap_seconds
            )
            next_retry = utcnow() + timedelta(seconds=backoff_seconds)

        updated_item: OutboxItemOut = await self.update(item_id, OutboxItemUpdate(
            status=status,
            error={"message": error_msg, "attempts": attempts},
            scheduled_at=next_retry
        ))
        return updated_item
