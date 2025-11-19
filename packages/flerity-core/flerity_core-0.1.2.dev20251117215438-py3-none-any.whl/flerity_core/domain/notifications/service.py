"""Notification service for business logic orchestration and delivery management."""

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from ...db.uow import async_uow_factory
from ...utils.errors import BadRequest, NotFound
from ...utils.logging import get_safe_logger
from ...utils.tracing import trace_async
from .repository import NotificationOutboxRepository, NotificationRepository
from .schemas import NotificationCreate, NotificationOut, NotificationOutboxOut, OutboxStatus

logger = get_safe_logger(__name__)


class NotificationService:
    """Service for notification management and delivery orchestration."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory

    @trace_async
    async def get_user_notifications(
        self, user_id: UUID, limit: int = 50, unread_only: bool = False
    ) -> list[NotificationOut]:
        """Get notifications for user with RLS enforcement."""
        if limit <= 0 or limit > 100:
            raise BadRequest("Limit must be between 1 and 100")

        try:
            async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                repository = NotificationRepository(uow.session)
                result: list[NotificationOut] = await repository.list_by_user(user_id, limit, unread_only)
                return result
        except BadRequest:
            raise
        except Exception as e:
            logger.error("Failed to retrieve notifications", extra={
                "user_id": str(user_id), "error": str(e)
            })
            raise BadRequest("Failed to retrieve notifications")

    @trace_async
    async def get_notification(self, notification_id: UUID, user_id: UUID) -> NotificationOut | None:
        """Get single notification by ID (RLS enforced)."""
        try:
            async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                repository = NotificationRepository(uow.session)
                result: NotificationOut | None = await repository.get_by_id(notification_id)
                return result
        except Exception as e:
            logger.error("Failed to get notification", extra={
                "notification_id": str(notification_id), "user_id": str(user_id), "error": str(e)
            })
            raise BadRequest("Failed to retrieve notification")

    @trace_async
    async def get_unread_count(self, user_id: UUID) -> int:
        """Get count of unread notifications for user."""
        try:
            async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                repository = NotificationRepository(uow.session)
                result: int = await repository.count_unread(user_id)
                return result
        except Exception as e:
            logger.error("Failed to get unread count", extra={
                "user_id": str(user_id), "error": str(e)
            })
            raise BadRequest("Failed to get unread count")

    @trace_async
    async def create_notification(
        self, user_id: UUID, title: str, body: str, notification_type: str,
        metadata: dict[str, Any] | None = None
    ) -> NotificationOut:
        """Create new notification for user."""
        notification_data = NotificationCreate(
            user_id=user_id,
            title=title,
            body=body,
            type=notification_type,
            metadata=metadata or {}
        )

        try:
            async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                repository = NotificationRepository(uow.session)
                result: NotificationOut = await repository.create(notification_data)
                return result
        except Exception as e:
            logger.error("Failed to create notification", extra={
                "user_id": str(user_id), "type": notification_type, "error": str(e)
            })
            raise BadRequest("Failed to create notification")

    @trace_async
    async def mark_as_read(self, user_id: UUID, notification_id: UUID, locale: str = "en-US") -> NotificationOut | None:
        """Mark notification as read (RLS enforced)."""
        try:
            async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                repository = NotificationRepository(uow.session)
                result: NotificationOut | None = await repository.mark_as_read(notification_id)
                return result
        except Exception as e:
            logger.error("Failed to mark notification as read", extra={
                "notification_id": str(notification_id), "user_id": str(user_id), "error": str(e)
            })
            raise BadRequest("Failed to mark notification as read")

    @trace_async
    async def mark_all_as_read(self, user_id: UUID, locale: str = "en-US") -> int:
        """Mark all unread notifications as read for user."""
        try:
            async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                repository = NotificationRepository(uow.session)
                result: int = await repository.mark_all_as_read(user_id)
                return result
        except Exception as e:
            logger.error("Failed to mark all notifications as read", extra={
                "user_id": str(user_id), "error": str(e)
            })
            raise BadRequest("Failed to mark notifications as read")

    @trace_async
    async def list_notifications(
        self, user_id: UUID, limit: int = 20, cursor: str | None = None,
        status_filter: str | None = None
    ) -> tuple[list[NotificationOut], str | None]:
        """List notifications with pagination and filtering."""
        if limit <= 0 or limit > 100:
            raise BadRequest("Limit must be between 1 and 100")

        try:
            unread_only = status_filter == "unread"
            async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                repository = NotificationRepository(uow.session)
                notifications = await repository.list_by_user(user_id, limit, unread_only)

            # Simple cursor implementation - use last notification ID
            next_cursor = None
            if notifications and len(notifications) == limit:
                next_cursor = str(notifications[-1].id)

            return notifications, next_cursor
        except BadRequest:
            raise
        except Exception as e:
            logger.error("Failed to list notifications", extra={
                "user_id": str(user_id), "error": str(e)
            })
            raise BadRequest("Failed to retrieve notifications")

    @trace_async
    async def delete_notification(self, user_id: UUID, notification_id: UUID, locale: str = "en-US") -> None:
        """Delete notification with user validation."""
        try:
            async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                repository = NotificationRepository(uow.session)
                await repository.delete(notification_id, locale)
        except NotFound:
            raise
        except Exception as e:
            logger.error("Failed to delete notification", extra={
                "notification_id": str(notification_id), "user_id": str(user_id), "error": str(e)
            })
            raise BadRequest("Failed to delete notification")

    @trace_async
    async def send_push_notification(self, notification_id: UUID) -> bool:
        """Send push notification to user devices via AWS SNS.
        
        Called by worker when processing notifications.push events.
        
        Args:
            notification_id: Notification to send
            
        Returns:
            True if sent to at least one device, False otherwise
        """
        try:
            # 1. Get notification from database
            async with async_uow_factory(self.session_factory, user_id=None)() as uow:
                notification_repo = NotificationRepository(uow.session)
                notification = await notification_repo.get_by_id(notification_id)

                if not notification:
                    logger.warning("Notification not found", extra={
                        "notification_id": str(notification_id)
                    })
                    return False

                # 2. Get user devices with push tokens
                from ..devices.repository import DevicesRepository
                devices_repo = DevicesRepository(uow.session)
                devices = await devices_repo.list_user_devices(notification.user_id)

                # Filter devices with valid push tokens
                devices_with_tokens = [d for d in devices if d.push_token and d.push_token.strip()]

                if not devices_with_tokens:
                    logger.info("No devices with push tokens found for user", extra={
                        "user_id": str(notification.user_id),
                        "notification_id": str(notification_id)
                    })
                    return False

                # 3. Send to each device
                from .push_sender import create_push_sender
                sender = create_push_sender()

                sent_count = 0
                failed_count = 0

                for device in devices_with_tokens:
                    success, error = await sender.send_to_device(
                        push_token=device.push_token,
                        platform=device.platform,
                        title=notification.title,
                        body=notification.body,
                        data=notification.metadata,
                        is_sandbox=device.is_sandbox
                    )

                    if success:
                        sent_count += 1
                    else:
                        failed_count += 1
                        logger.warning("Failed to send push to device", extra={
                            "device_id": str(device.id),
                            "platform": device.platform,
                            "error": error
                        })

                logger.info("Push notification delivery completed", extra={
                    "notification_id": str(notification_id),
                    "sent_count": sent_count,
                    "failed_count": failed_count,
                    "total_devices": len(devices_with_tokens)
                })

                return sent_count > 0

        except Exception as e:
            logger.error("Failed to send push notification", extra={
                "notification_id": str(notification_id),
                "error": str(e)
            })
            return False

    @trace_async
    async def send_email_notification(self, notification_id: UUID) -> bool:
        """Send email notification (placeholder for future implementation)."""
        logger.info("Email notification requested (not implemented)", extra={
            "notification_id": str(notification_id)
        })
        return False


class NotificationOutboxService:
    """Service for notification outbox management."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory

    @trace_async
    async def enqueue(self, key: str, payload: dict[str, Any], user_id: str | None = None) -> NotificationOutboxOut:
        """Enqueue notification for delivery (idempotent)."""
        try:
            async with async_uow_factory(self.session_factory, user_id=user_id)() as uow:
                repository = NotificationOutboxRepository(uow.session)
                result: NotificationOutboxOut = await repository.enqueue(key, payload)
                return result
        except Exception as e:
            logger.error("Failed to enqueue notification", extra={
                "key": key, "error": str(e)
            })
            raise BadRequest("Failed to enqueue notification")

    @trace_async
    async def get_by_id(self, outbox_id: UUID, user_id: str | None = None) -> NotificationOutboxOut | None:
        """Get outbox item by ID."""
        try:
            async with async_uow_factory(self.session_factory, user_id=user_id)() as uow:
                repository = NotificationOutboxRepository(uow.session)
                result: NotificationOutboxOut | None = await repository.get_by_id(outbox_id)
                return result
        except Exception as e:
            logger.error("Failed to get outbox item", extra={
                "outbox_id": str(outbox_id), "error": str(e)
            })
            raise BadRequest("Failed to retrieve outbox item")

    @trace_async
    async def list_by_status(self, status: OutboxStatus, limit: int = 50, user_id: str | None = None) -> list[NotificationOutboxOut]:
        """List outbox items by status."""
        if limit <= 0 or limit > 100:
            raise BadRequest("Limit must be between 1 and 100")

        try:
            async with async_uow_factory(self.session_factory, user_id=user_id)() as uow:
                repository = NotificationOutboxRepository(uow.session)
                result: list[NotificationOutboxOut] = await repository.list_by_status(status, limit)
                return result
        except Exception as e:
            logger.error("Failed to list outbox items", extra={
                "status": status, "error": str(e)
            })
            raise BadRequest("Failed to retrieve outbox items")

    @trace_async
    async def mark_sent(self, outbox_id: UUID, user_id: str | None = None) -> NotificationOutboxOut:
        """Mark outbox item as successfully sent."""
        try:
            async with async_uow_factory(self.session_factory, user_id=user_id)() as uow:
                repository = NotificationOutboxRepository(uow.session)
                result: NotificationOutboxOut = await repository.mark_sent(outbox_id)
                return result
        except NotFound:
            raise
        except Exception as e:
            logger.error("Failed to mark outbox item as sent", extra={
                "outbox_id": str(outbox_id), "error": str(e)
            })
            raise BadRequest("Failed to mark item as sent")

    @trace_async
    async def mark_failed(self, outbox_id: UUID, error: str, user_id: str | None = None) -> NotificationOutboxOut:
        """Mark outbox item as failed."""
        try:
            async with async_uow_factory(self.session_factory, user_id=user_id)() as uow:
                repository = NotificationOutboxRepository(uow.session)
                result: NotificationOutboxOut = await repository.mark_failed(outbox_id, error)
                return result
        except NotFound:
            raise
        except Exception as e:
            logger.error("Failed to mark outbox item as failed", extra={
                "outbox_id": str(outbox_id), "error": str(e)
            })
            raise BadRequest("Failed to mark item as failed")

    @trace_async
    async def cleanup_old_items(self, days_old: int = 30, user_id: str | None = None) -> int:
        """Clean up old processed outbox items."""
        try:
            async with async_uow_factory(self.session_factory, user_id=user_id)() as uow:
                repository = NotificationOutboxRepository(uow.session)
                result: int = await repository.cleanup_old_items(days_old)
                return result
        except Exception as e:
            logger.error("Failed to cleanup old outbox items", extra={
                "days_old": days_old, "error": str(e)
            })
            raise BadRequest("Failed to cleanup old items")

    @trace_async
    async def retry_failed_items(self, max_retries: int = 3, user_id: str | None = None) -> list[NotificationOutboxOut]:
        """Get failed items that can be retried."""
        try:
            async with async_uow_factory(self.session_factory, user_id=user_id)() as uow:
                repository = NotificationOutboxRepository(uow.session)
                result: list[NotificationOutboxOut] = await repository.retry_failed_items(max_retries)
                return result
        except Exception as e:
            logger.error("Failed to get retry items", extra={
                "max_retries": max_retries, "error": str(e)
            })
            raise BadRequest("Failed to get retry items")


def create_notification_service(session_factory: async_sessionmaker[AsyncSession]) -> NotificationService:
    """Factory function for NotificationService."""
    return NotificationService(session_factory)


def create_notification_outbox_service(session_factory: async_sessionmaker[AsyncSession]) -> NotificationOutboxService:
    """Factory function for NotificationOutboxService."""
    return NotificationOutboxService(session_factory)
