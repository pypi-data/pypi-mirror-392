"""Thread tracking notification service for managing tracking change notifications."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from ....db.uow import async_uow_factory
from ....utils.logging import get_logger
from ....utils.tracing import trace_async
from ...notifications.service import NotificationService
from ..repository import ThreadsRepository
from .schemas import ThreadTrackingConfiguration

logger = get_logger(__name__)


class ThreadTrackingNotificationService:
    """Service for managing thread tracking change notifications."""

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        notification_service: NotificationService,
    ):
        self.session_factory = session_factory
        self.notification_service = notification_service

    @trace_async
    async def check_and_notify_tracking_deactivation(
        self, user_id: UUID, thread_id: UUID, config: ThreadTrackingConfiguration
    ) -> None:
        """Check if thread had recent activity and send notification if tracking was accidentally deactivated."""
        try:
            # Check if user has tracking notifications enabled
            notifications_enabled = await self._are_tracking_notifications_enabled(user_id)
            if not notifications_enabled:
                logger.debug("Tracking notifications disabled for user", extra={
                    "user_id": str(user_id)
                })
                return

            # Check if thread had recent activity (within last 24 hours)
            has_recent_activity = await self._has_recent_activity(thread_id, hours=24)

            if has_recent_activity:
                # Get thread details for notification
                thread_details = await self._get_thread_details(user_id, thread_id)
                if not thread_details:
                    logger.warning("Thread not found for notification", extra={
                        "thread_id": str(thread_id),
                        "user_id": str(user_id)
                    })
                    return

                # Create notification for accidental deactivation
                await self._create_tracking_deactivation_notification(
                    user_id=user_id,
                    thread_id=thread_id,
                    thread_name=thread_details.get("contact_name") or thread_details.get("contact_handle", "Unknown"),
                    channel=thread_details.get("channel", "unknown")
                )

                logger.info("Tracking deactivation notification sent", extra={
                    "user_id": str(user_id),
                    "thread_id": str(thread_id),
                    "config_id": str(config.id)
                })
        except Exception as e:
            logger.error("Failed to check and notify tracking deactivation", extra={
                "user_id": str(user_id),
                "thread_id": str(thread_id),
                "error": str(e)
            })
            # Don't raise exception as this is a secondary operation

    @trace_async
    async def notify_tracking_reactivation(
        self, user_id: UUID, thread_id: UUID, config: ThreadTrackingConfiguration
    ) -> None:
        """Send notification when tracking is reactivated for a thread."""
        try:
            # Get thread details for notification
            thread_details = await self._get_thread_details(user_id, thread_id)
            if not thread_details:
                logger.warning("Thread not found for reactivation notification", extra={
                    "thread_id": str(thread_id),
                    "user_id": str(user_id)
                })
                return

            # Create notification for reactivation
            await self._create_tracking_reactivation_notification(
                user_id=user_id,
                thread_id=thread_id,
                thread_name=thread_details.get("contact_name") or thread_details.get("contact_handle", "Unknown"),
                channel=thread_details.get("channel", "unknown")
            )

            logger.info("Tracking reactivation notification sent", extra={
                "user_id": str(user_id),
                "thread_id": str(thread_id),
                "config_id": str(config.id)
            })
        except Exception as e:
            logger.error("Failed to send tracking reactivation notification", extra={
                "user_id": str(user_id),
                "thread_id": str(thread_id),
                "error": str(e)
            })
            # Don't raise exception as this is a secondary operation

    @trace_async
    async def _has_recent_activity(self, thread_id: UUID, hours: int = 24) -> bool:
        """Check if thread has had activity within the specified hours."""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)

            async with async_uow_factory(self.session_factory, user_id=None, apply_rls=False, read_only=True)() as uow:
                threads_repo = ThreadsRepository(uow.session)
                thread = await threads_repo.get_by_id(thread_id)

                return thread.last_activity >= cutoff_time
        except Exception as e:
            logger.error("Failed to check recent activity", extra={
                "thread_id": str(thread_id),
                "error": str(e)
            })
            # Default to False if check fails
            return False

    @trace_async
    async def _get_thread_details(self, user_id: UUID, thread_id: UUID) -> dict[str, Any] | None:
        """Get thread details for notification purposes."""
        try:
            async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                threads_repo = ThreadsRepository(uow.session)
                thread = await threads_repo.get_by_id(thread_id)

                return {
                    "contact_name": thread.contact_name,
                    "contact_handle": thread.contact_handle,
                    "channel": thread.channel,
                    "last_activity": thread.last_activity
                }
        except Exception as e:
            logger.error("Failed to get thread details", extra={
                "thread_id": str(thread_id),
                "user_id": str(user_id),
                "error": str(e)
            })
            return None

    @trace_async
    async def _are_tracking_notifications_enabled(self, user_id: UUID) -> bool:
        """Check if user has tracking notifications enabled in their preferences."""
        try:
            from ...users.repository import UsersRepository

            async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                users_repo = UsersRepository(uow.session)
                user = await users_repo.get_by_id(user_id)

                # Check user preferences for tracking notifications
                # Default to True if not explicitly set
                preferences = user.preferences or {}
                return preferences.get("tracking_notifications_enabled", True)
        except Exception as e:
            logger.error("Failed to check tracking notification preferences", extra={
                "user_id": str(user_id),
                "error": str(e)
            })
            # Default to True if check fails
            return True

    @trace_async
    async def _create_tracking_deactivation_notification(
        self, user_id: UUID, thread_id: UUID, thread_name: str, channel: str
    ) -> None:
        """Create notification for tracking deactivation."""
        title = "Rastreamento desativado"
        body = f"O rastreamento foi desativado para a conversa com {thread_name} no {channel.title()}. Esta conversa teve atividade recente. Deseja reativar?"

        metadata = {
            "type": "tracking_deactivated",
            "thread_id": str(thread_id),
            "thread_name": thread_name,
            "channel": channel,
            "action_available": True,
            "action_type": "reactivate_tracking"
        }

        await self.notification_service.create_notification(
            user_id=user_id,
            title=title,
            body=body,
            notification_type="tracking_deactivated",
            metadata=metadata
        )

    @trace_async
    async def _create_tracking_reactivation_notification(
        self, user_id: UUID, thread_id: UUID, thread_name: str, channel: str
    ) -> None:
        """Create notification for tracking reactivation."""
        title = "Rastreamento reativado"
        body = f"O rastreamento foi reativado para a conversa com {thread_name} no {channel.title()}."

        metadata = {
            "type": "tracking_reactivated",
            "thread_id": str(thread_id),
            "thread_name": thread_name,
            "channel": channel,
            "action_available": False
        }

        await self.notification_service.create_notification(
            user_id=user_id,
            title=title,
            body=body,
            notification_type="tracking_reactivated",
            metadata=metadata
        )


def create_thread_tracking_notification_service(
    session_factory: async_sessionmaker[AsyncSession],
    notification_service: NotificationService,
) -> ThreadTrackingNotificationService:
    """Factory function for ThreadTrackingNotificationService."""
    return ThreadTrackingNotificationService(session_factory, notification_service)
