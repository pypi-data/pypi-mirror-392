"""Notification repository for managing user notifications and outbox."""

from typing import Any
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from ...utils.errors import BadRequest, Conflict, NotFound
from ...utils.logging import get_logger
from ...utils.tracing import trace_async
from .schemas import (
    NotificationCreate,
    NotificationOut,
    NotificationOutboxOut,
    NotificationOutboxUpdate,
    NotificationUpdate,
    OutboxStatus,
    notif_outbox_table,
    notifications_table,
)

logger = get_logger(__name__)


class NotificationRepository:
    """Repository for notification data access operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    @trace_async
    async def get_by_id(self, notification_id: UUID) -> NotificationOut | None:
        """Get notification by ID (RLS enforced)."""
        try:
            stmt = sa.select(notifications_table).where(
                notifications_table.c.id == notification_id
            )

            result = await self.session.execute(stmt)
            row = result.fetchone()
            return NotificationOut.model_validate(row._asdict()) if row else None
        except sa.exc.SQLAlchemyError as e:
            logger.error("Database error getting notification", extra={
                "notification_id": str(notification_id), "error": str(e)
            })
            raise BadRequest("Failed to retrieve notification")
        except Exception as e:
            logger.error("Unexpected error getting notification", extra={
                "notification_id": str(notification_id), "error": str(e)
            })
            raise BadRequest("Failed to retrieve notification")

    @trace_async
    async def list_by_user(
        self, user_id: UUID, limit: int = 50, unread_only: bool = False
    ) -> list[NotificationOut]:
        """List notifications for user (RLS enforced)."""
        if limit <= 0 or limit > 100:
            raise BadRequest("Limit must be between 1 and 100")

        try:
            stmt = sa.select(notifications_table).where(
                notifications_table.c.user_id == user_id
            )

            if unread_only:
                stmt = stmt.where(notifications_table.c.read_at.is_(None))

            stmt = stmt.order_by(notifications_table.c.created_at.desc()).limit(limit)

            result = await self.session.execute(stmt)
            return [NotificationOut.model_validate(row._asdict()) for row in result.fetchall()]
        except sa.exc.SQLAlchemyError as e:
            logger.error("Database error listing notifications", extra={
                "user_id": str(user_id), "error": str(e)
            })
            raise BadRequest("Failed to retrieve notifications")
        except Exception as e:
            logger.error("Unexpected error listing notifications", extra={
                "user_id": str(user_id), "error": str(e)
            })
            raise BadRequest("Failed to retrieve notifications")

    @trace_async
    async def count_unread(self, user_id: UUID) -> int:
        """Count unread notifications for user."""
        stmt = sa.select(sa.func.count()).select_from(notifications_table).where(
            sa.and_(
                notifications_table.c.user_id == user_id,
                notifications_table.c.read_at.is_(None)
            )
        )

        result = await self.session.execute(stmt)
        return result.scalar() or 0

    @trace_async
    async def create(self, data: NotificationCreate) -> NotificationOut:
        """Create new notification."""
        notification_data = data.model_dump()

        try:
            stmt = sa.insert(notifications_table).values(**notification_data).returning(notifications_table)
            result = await self.session.execute(stmt)
            row = result.fetchone()
            if row is None:
                raise BadRequest("Failed to create notification")
            return NotificationOut.model_validate(row._asdict())
        except sa.exc.IntegrityError as e:
            logger.error("Notification creation integrity error", extra={"error": str(e)})
            raise Conflict("Notification creation conflict")
        except sa.exc.SQLAlchemyError as e:
            logger.error("Database error creating notification", extra={"error": str(e)})
            raise BadRequest("Failed to create notification")
        except Exception as e:
            logger.error("Unexpected error creating notification", extra={"error": str(e)})
            raise BadRequest("Failed to create notification")

    @trace_async
    async def update(self, notification_id: UUID, data: NotificationUpdate) -> NotificationOut | None:
        """Update notification."""
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_by_id(notification_id)

        update_data['updated_at'] = sa.func.now()

        stmt = (
            sa.update(notifications_table)
            .where(notifications_table.c.id == notification_id)
            .values(**update_data)
            .returning(notifications_table)
        )

        result = await self.session.execute(stmt)
        row = result.fetchone()
        return NotificationOut.model_validate(row._asdict()) if row else None

    @trace_async
    async def mark_as_read(self, notification_id: UUID) -> NotificationOut | None:
        """Mark notification as read."""
        stmt = (
            sa.update(notifications_table)
            .where(notifications_table.c.id == notification_id)
            .values(read_at=sa.func.now())
            .returning(notifications_table)
        )

        result = await self.session.execute(stmt)
        row = result.fetchone()
        return NotificationOut.model_validate(row._asdict()) if row else None

    @trace_async
    async def mark_all_as_read(self, user_id: UUID) -> int:
        """Mark all unread notifications as read for user."""
        stmt = (
            sa.update(notifications_table)
            .where(
                sa.and_(
                    notifications_table.c.user_id == user_id,
                    notifications_table.c.read_at.is_(None)
                )
            )
            .values(read_at=sa.func.now())
        )

        result = await self.session.execute(stmt)
        return getattr(result, 'rowcount', 0)

    @trace_async
    async def delete(self, notification_id: UUID, locale: str = "en-US") -> None:
        """Delete notification."""
        from ...utils.i18n import t

        stmt = sa.delete(notifications_table).where(
            notifications_table.c.id == notification_id
        )

        result = await self.session.execute(stmt)
        if getattr(result, 'rowcount', 0) == 0:
            raise NotFound(t("notifications.error.delete_failed", locale=locale))


class NotificationOutboxRepository:
    """Repository for notification outbox management."""

    def __init__(self, session: AsyncSession):
        self.session = session

    @trace_async
    async def enqueue(self, key: str, payload: dict[str, Any]) -> NotificationOutboxOut:
        """Enqueue notification for delivery (idempotent)."""
        stmt = pg_insert(notif_outbox_table).values(
            key=key,
            payload=payload,
            status="queued"
        ).on_conflict_do_nothing(
            index_elements=['key']
        ).returning(notif_outbox_table)

        result = await self.session.execute(stmt)
        row = result.fetchone()

        if row:
            return NotificationOutboxOut.model_validate(row._asdict())

        # If no row returned, fetch existing
        select_stmt = sa.select(notif_outbox_table).where(notif_outbox_table.c.key == key)
        result = await self.session.execute(select_stmt)
        row = result.fetchone()

        if not row:
            raise BadRequest("Failed to enqueue outbox item")

        return NotificationOutboxOut.model_validate(row._asdict())

    @trace_async
    async def get_by_id(self, outbox_id: UUID) -> NotificationOutboxOut | None:
        """Get outbox item by ID."""
        stmt = sa.select(notif_outbox_table).where(notif_outbox_table.c.id == outbox_id)

        result = await self.session.execute(stmt)
        row = result.fetchone()
        return NotificationOutboxOut.model_validate(row._asdict()) if row else None

    @trace_async
    async def update(self, outbox_id: UUID, data: NotificationOutboxUpdate) -> NotificationOutboxOut | None:
        """Update outbox item."""
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_by_id(outbox_id)

        update_data['updated_at'] = sa.func.now()

        stmt = (
            sa.update(notif_outbox_table)
            .where(notif_outbox_table.c.id == outbox_id)
            .values(**update_data)
            .returning(notif_outbox_table)
        )

        result = await self.session.execute(stmt)
        row = result.fetchone()
        return NotificationOutboxOut.model_validate(row._asdict()) if row else None

    @trace_async
    async def list_by_status(self, status: OutboxStatus, limit: int = 50) -> list[NotificationOutboxOut]:
        """List outbox items by status."""
        stmt = (
            sa.select(notif_outbox_table)
            .where(notif_outbox_table.c.status == status)
            .order_by(notif_outbox_table.c.created_at.asc())
            .limit(limit)
        )

        result = await self.session.execute(stmt)
        return [NotificationOutboxOut.model_validate(row._asdict()) for row in result.fetchall()]

    @trace_async
    async def mark_sent(self, outbox_id: UUID) -> NotificationOutboxOut:
        """Mark outbox item as successfully sent."""
        stmt = (
            sa.update(notif_outbox_table)
            .where(notif_outbox_table.c.id == outbox_id)
            .values(status="sent", updated_at=sa.func.now())
            .returning(notif_outbox_table)
        )

        result = await self.session.execute(stmt)
        row = result.fetchone()

        if not row:
            raise NotFound("Outbox item not found")

        return NotificationOutboxOut.model_validate(row._asdict())

    @trace_async
    async def mark_failed(self, outbox_id: UUID, error: str) -> NotificationOutboxOut:
        """Mark outbox item as failed."""
        stmt = (
            sa.update(notif_outbox_table)
            .where(notif_outbox_table.c.id == outbox_id)
            .values(
                status="failed",
                last_error=error,
                updated_at=sa.func.now()
            )
            .returning(notif_outbox_table)
        )

        result = await self.session.execute(stmt)
        row = result.fetchone()

        if not row:
            raise NotFound("Outbox item not found")

        return NotificationOutboxOut.model_validate(row._asdict())

    @trace_async
    async def cleanup_old_items(self, days_old: int = 30) -> int:
        """Clean up old processed outbox items."""
        try:
            stmt = sa.delete(notif_outbox_table).where(
                sa.and_(
                    notif_outbox_table.c.status.in_(["sent", "failed"]),
                    notif_outbox_table.c.updated_at < sa.func.now() - sa.text(f"INTERVAL '{days_old} days'")
                )
            )

            result = await self.session.execute(stmt)
            deleted_count = getattr(result, 'rowcount', 0)

            logger.info("Cleaned up old outbox items", extra={
                "deleted_count": deleted_count, "days_old": days_old
            })

            return deleted_count
        except sa.exc.SQLAlchemyError as e:
            logger.error("Database error cleaning up outbox", extra={"error": str(e)})
            raise BadRequest("Failed to cleanup outbox")
        except Exception as e:
            logger.error("Unexpected error cleaning up outbox", extra={"error": str(e)})
            raise BadRequest("Failed to cleanup outbox")

    @trace_async
    async def retry_failed_items(self, max_retries: int = 3) -> list[NotificationOutboxOut]:
        """Get failed items that can be retried."""
        try:
            stmt = (
                sa.select(notif_outbox_table)
                .where(
                    sa.and_(
                        notif_outbox_table.c.status == "failed",
                        notif_outbox_table.c.retry_count < max_retries
                    )
                )
                .order_by(notif_outbox_table.c.updated_at.asc())
                .limit(50)
            )

            result = await self.session.execute(stmt)
            return [NotificationOutboxOut.model_validate(row._asdict()) for row in result.fetchall()]
        except sa.exc.SQLAlchemyError as e:
            logger.error("Database error getting retry items", extra={"error": str(e)})
            raise BadRequest("Failed to get retry items")
        except Exception as e:
            logger.error("Unexpected error getting retry items", extra={"error": str(e)})
            raise BadRequest("Failed to get retry items")
