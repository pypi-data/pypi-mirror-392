"""Thread tracking service for business logic and tracking management."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from ....db.uow import async_uow_factory
from ....utils.errors import BadRequest, NotFound
from ....utils.logging import get_safe_logger
from ....utils.tracing import trace_async
from ....utils.request_tracking import RequestTracker
from ....utils.domain_logger import get_domain_logger
from ...telemetry.schemas import TelemetryEventCreate
from ...telemetry.service import TelemetryService
from ..repository import ThreadsRepository
from .notification_service import ThreadTrackingNotificationService
from .repository import ThreadTrackingRepository
from .schemas import (
    ThreadTrackingConfiguration,
    ThreadTrackingConfigurationCreate,
    ThreadTrackingConfigurationUpdate,
)

logger = get_safe_logger(__name__)
domain_logger = get_domain_logger("threads.tracking")


class ThreadTrackingService:
    """Business logic for thread tracking configuration management."""

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        notification_service: ThreadTrackingNotificationService | None = None,
        telemetry_service: TelemetryService | None = None,
    ):
        self.session_factory = session_factory
        self.notification_service = notification_service
        self.telemetry_service = telemetry_service

        # Metrics tracking
        self._metrics = {
            "tracking_enabled_count": 0,
            "tracking_disabled_count": 0,
            "tracking_checks_count": 0,
            "tracking_errors_count": 0,
        }

    @trace_async
    async def enable_tracking(self, user_id: UUID, thread_id: UUID) -> ThreadTrackingConfiguration:
        """Enable tracking for a thread."""
        with RequestTracker(user_id=str(user_id), operation="enable_tracking", thread_id=str(thread_id)) as tracker:
            try:
                tracking_context = tracking_context = domain_logger.operation_start("enable_tracking", thread_id=str(thread_id), user_id=str(user_id))
                
                async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                    # First verify the thread exists and belongs to the user
                    threads_repo = ThreadsRepository(uow.session)
                    try:
                        await threads_repo.get_by_id(thread_id)
                    except NotFound:
                        error_id = domain_logger.operation_error(tracking_context, 
                            error=BadRequest(f"Thread {thread_id} not found or access denied"),
                            thread_id=str(thread_id), user_id=str(user_id))
                        raise BadRequest(f"Thread {thread_id} not found or access denied")

                    tracking_repo = ThreadTrackingRepository(uow.session)

                    # Check if tracking configuration already exists
                    existing_config = await tracking_repo.get_by_thread_id(thread_id)
                    if existing_config:
                        if existing_config.is_active:
                            # Already enabled, return existing configuration
                            domain_logger.business_event("tracking_already_enabled", 
                                thread_id=str(thread_id), user_id=str(user_id), config_id=str(existing_config.id))
                            tracker.log_success(result_id=str(existing_config.id), status="already_enabled")
                            return existing_config
                        else:
                            # Update existing configuration to active
                            update_data = ThreadTrackingConfigurationUpdate(is_active=True)
                            config = await tracking_repo.update(thread_id, update_data, user_id)
                            await uow.commit()

                            # Send reactivation notification if notification service is available
                            if self.notification_service:
                                await self.notification_service.notify_tracking_reactivation(
                                    user_id, thread_id, config
                                )

                            # Send telemetry event
                            await self._send_telemetry_event(
                                "tracking_reactivated",
                                user_id,
                                {
                                    "thread_id": str(thread_id),
                                    "config_id": str(config.id),
                                    "action": "reactivate"
                                }
                            )

                            # Record metrics
                            self._metrics["tracking_enabled_count"] += 1

                            domain_logger.business_event("tracking_reactivated", 
                                thread_id=str(thread_id), user_id=str(user_id), config_id=str(config.id))
                            domain_logger.operation_success(tracking_context, 
                                thread_id=str(thread_id), user_id=str(user_id), config_id=str(config.id), action="reactivate")
                            tracker.log_success(result_id=str(config.id), status="reactivated")
                            return config
                    else:
                        # Create new tracking configuration
                        create_data = ThreadTrackingConfigurationCreate(
                            thread_id=thread_id,
                            is_active=True
                        )
                        config = await tracking_repo.create(create_data, user_id)
                        await uow.commit()

                        # Send telemetry event
                        await self._send_telemetry_event(
                            "tracking_enabled",
                            user_id,
                            {
                                "thread_id": str(thread_id),
                                "config_id": str(config.id),
                                "action": "enable"
                            }
                        )

                        # Record metrics
                        self._metrics["tracking_enabled_count"] += 1

                        domain_logger.business_event("tracking_enabled", 
                            thread_id=str(thread_id), user_id=str(user_id), config_id=str(config.id))
                        domain_logger.operation_success(tracking_context, 
                            thread_id=str(thread_id), user_id=str(user_id), config_id=str(config.id), action="enable")
                        tracker.log_success(result_id=str(config.id), status="enabled")
                        return config
            except BadRequest:
                raise
            except Exception as e:
                # Send error telemetry event
                await self._send_telemetry_event(
                    "tracking_error",
                    user_id,
                    {
                        "thread_id": str(thread_id),
                        "action": "enable",
                        "error": str(e),
                        "error_type": type(e).__name__
                    }
                )

                # Record error metrics
                self._metrics["tracking_errors_count"] += 1

                error_id = domain_logger.operation_error(tracking_context, error=e,
                    thread_id=str(thread_id), user_id=str(user_id), action="enable")
                tracker.log_error(e, context={"thread_id": str(thread_id), "action": "enable"})
                raise BadRequest(f"Failed to enable tracking (Error ID: {error_id})")

    @trace_async
    async def disable_tracking(self, user_id: UUID, thread_id: UUID) -> None:
        """Disable tracking for a thread."""
        with RequestTracker(user_id=str(user_id), operation="disable_tracking", thread_id=str(thread_id)) as tracker:
            try:
                tracking_context = tracking_context = domain_logger.operation_start("disable_tracking", thread_id=str(thread_id), user_id=str(user_id))
                
                async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                    # First verify the thread exists and belongs to the user
                    threads_repo = ThreadsRepository(uow.session)
                    try:
                        await threads_repo.get_by_id(thread_id)
                    except NotFound:
                        error_id = domain_logger.operation_error(tracking_context, 
                            error=BadRequest(f"Thread {thread_id} not found or access denied"),
                            thread_id=str(thread_id), user_id=str(user_id))
                        raise BadRequest(f"Thread {thread_id} not found or access denied")

                    tracking_repo = ThreadTrackingRepository(uow.session)

                    # Check if tracking configuration exists
                    existing_config = await tracking_repo.get_by_thread_id(thread_id)
                    if not existing_config:
                        # No configuration exists, nothing to disable
                        domain_logger.business_event("tracking_no_config_to_disable", 
                            thread_id=str(thread_id), user_id=str(user_id))
                        tracker.log_success(status="no_config")
                        return

                    if not existing_config.is_active:
                        # Already disabled, nothing to do
                        domain_logger.business_event("tracking_already_disabled", 
                            thread_id=str(thread_id), user_id=str(user_id), config_id=str(existing_config.id))
                        tracker.log_success(status="already_disabled")
                        return

                    # Update configuration to inactive
                    update_data = ThreadTrackingConfigurationUpdate(is_active=False)
                    updated_config = await tracking_repo.update(thread_id, update_data, user_id)
                    await uow.commit()

                    # Check for recent activity and send notification if needed
                    if self.notification_service and updated_config:
                        await self.notification_service.check_and_notify_tracking_deactivation(
                            user_id, thread_id, updated_config
                        )

                    # Send telemetry event
                    await self._send_telemetry_event(
                        "tracking_disabled",
                        user_id,
                        {
                            "thread_id": str(thread_id),
                            "config_id": str(existing_config.id),
                            "action": "disable"
                        }
                    )

                    # Record metrics
                    self._metrics["tracking_disabled_count"] += 1

                    domain_logger.business_event("tracking_disabled", 
                        thread_id=str(thread_id), user_id=str(user_id), config_id=str(existing_config.id))
                    domain_logger.operation_success(tracking_context, 
                        thread_id=str(thread_id), user_id=str(user_id), config_id=str(existing_config.id), action="disable")
                    tracker.log_success(result_id=str(existing_config.id), status="disabled")
            except BadRequest:
                raise
            except Exception as e:
                # Send error telemetry event
                await self._send_telemetry_event(
                    "tracking_error",
                    user_id,
                    {
                        "thread_id": str(thread_id),
                        "action": "disable",
                        "error": str(e),
                        "error_type": type(e).__name__
                    }
                )

                # Record error metrics
                self._metrics["tracking_errors_count"] += 1

                error_id = domain_logger.operation_error(tracking_context, error=e,
                    thread_id=str(thread_id), user_id=str(user_id), action="disable")
                tracker.log_error(e, context={"thread_id": str(thread_id), "action": "disable"})
                raise BadRequest(f"Failed to disable tracking (Error ID: {error_id})")

    @trace_async
    async def is_tracking_enabled(self, thread_id: UUID) -> bool:
        """Check if tracking is enabled for a thread (cached lookup)."""
        try:
            # Use a read-only session without RLS for fast lookups
            async with async_uow_factory(self.session_factory, user_id=None, apply_rls=False, read_only=True)() as uow:
                tracking_repo = ThreadTrackingRepository(uow.session)
                result = await tracking_repo.is_tracking_enabled(thread_id)

                # Send telemetry event for status checks (only occasionally to avoid spam)
                import random
                if random.random() < 0.1:  # 10% sampling rate
                    await self._send_telemetry_event(
                        "tracking_status_checked",
                        None,  # No user context for status checks
                        {
                            "thread_id": str(thread_id),
                            "is_enabled": result,
                            "action": "check_status"
                        }
                    )

                # Record metrics
                self._metrics["tracking_checks_count"] += 1

                logger.debug("Thread tracking status checked", extra={
                    "thread_id": str(thread_id),
                    "is_enabled": result,
                    "action": "check_status",
                    "metrics": self._get_metrics_summary()
                })

                return result
        except Exception as e:
            # Send error telemetry event
            await self._send_telemetry_event(
                "tracking_error",
                None,
                {
                    "thread_id": str(thread_id),
                    "action": "check_status",
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            )

            # Record error metrics
            self._metrics["tracking_errors_count"] += 1

            logger.error("Failed to check tracking status", extra={
                "thread_id": str(thread_id),
                "error": str(e),
                "action": "check_status",
                "metrics": self._get_metrics_summary()
            })
            # Default to False if check fails
            return False

    @trace_async
    async def get_tracking_status(self, user_id: UUID, thread_id: UUID) -> ThreadTrackingConfiguration | None:
        """Get tracking configuration for a specific thread."""
        try:
            async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                # First verify the thread exists and belongs to the user
                threads_repo = ThreadsRepository(uow.session)
                try:
                    await threads_repo.get_by_id(thread_id)
                except NotFound:
                    raise BadRequest(f"Thread {thread_id} not found or access denied")

                tracking_repo = ThreadTrackingRepository(uow.session)
                return await tracking_repo.get_by_thread_id(thread_id)
        except BadRequest:
            raise
        except Exception as e:
            logger.error("Failed to get tracking status", extra={
                "thread_id": str(thread_id),
                "user_id": str(user_id),
                "error": str(e)
            })
            raise BadRequest(f"Failed to get tracking status: {str(e)}")

    @trace_async
    async def get_user_tracking_configs(self, user_id: UUID) -> list[ThreadTrackingConfiguration]:
        """Get all tracking configurations for a user."""
        try:
            async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                tracking_repo = ThreadTrackingRepository(uow.session)
                return await tracking_repo.get_by_user_id(user_id)
        except Exception as e:
            logger.error("Failed to get user tracking configurations", extra={
                "user_id": str(user_id),
                "error": str(e)
            })
            raise BadRequest(f"Failed to get tracking configurations: {str(e)}")

    @trace_async
    async def warm_user_cache(self, user_id: UUID) -> None:
        """Warm cache for user's tracking configurations."""
        try:
            async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                tracking_repo = ThreadTrackingRepository(uow.session)
                # This will populate the cache as a side effect
                await tracking_repo.get_by_user_id(user_id)

                logger.debug("Cache warmed for user tracking configurations", extra={
                    "user_id": str(user_id)
                })
        except Exception as e:
            logger.warning("Failed to warm user cache", extra={
                "user_id": str(user_id),
                "error": str(e)
            })
            # Don't raise exception as cache warming is optional

    @trace_async
    async def warm_thread_cache(self, thread_id: UUID) -> None:
        """Warm cache for thread tracking status."""
        try:
            async with async_uow_factory(self.session_factory, user_id=None, apply_rls=False, read_only=True)() as uow:
                tracking_repo = ThreadTrackingRepository(uow.session)
                # This will populate the cache as a side effect
                await tracking_repo.is_tracking_enabled(thread_id)

                logger.debug("Cache warmed for thread tracking status", extra={
                    "thread_id": str(thread_id)
                })
        except Exception as e:
            logger.warning("Failed to warm thread cache", extra={
                "thread_id": str(thread_id),
                "error": str(e)
            })
            # Don't raise exception as cache warming is optional

    @trace_async
    async def bulk_warm_caches(self, user_id: UUID, thread_ids: list[UUID]) -> None:
        """Warm caches for multiple threads and user configurations."""
        try:
            # Warm user cache
            await self.warm_user_cache(user_id)

            # Warm thread caches in parallel
            import asyncio
            await asyncio.gather(
                *[self.warm_thread_cache(thread_id) for thread_id in thread_ids],
                return_exceptions=True
            )

            logger.info("Bulk cache warming completed", extra={
                "user_id": str(user_id),
                "thread_count": len(thread_ids)
            })
        except Exception as e:
            logger.warning("Failed to bulk warm caches", extra={
                "user_id": str(user_id),
                "thread_count": len(thread_ids),
                "error": str(e)
            })
            # Don't raise exception as cache warming is optional

    @trace_async
    async def validate_thread_ownership(self, user_id: UUID, thread_id: UUID) -> bool:
        """Validate that a thread belongs to the specified user."""
        try:
            async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                threads_repo = ThreadsRepository(uow.session)
                try:
                    thread = await threads_repo.get_by_id(thread_id)
                    return thread.user_id == user_id
                except NotFound:
                    return False
        except Exception as e:
            logger.error("Failed to validate thread ownership", extra={
                "thread_id": str(thread_id),
                "user_id": str(user_id),
                "error": str(e)
            })
            return False

    @trace_async
    async def bulk_enable_tracking(self, user_id: UUID, thread_ids: list[UUID]) -> list[ThreadTrackingConfiguration]:
        """Enable tracking for multiple threads efficiently."""
        if not thread_ids:
            return []

        try:
            async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                # Verify all threads exist and belong to the user
                threads_repo = ThreadsRepository(uow.session)
                tracking_repo = ThreadTrackingRepository(uow.session)

                # Check existing configurations
                existing_configs = await tracking_repo.get_by_user_id(user_id)
                existing_thread_ids = {config.thread_id for config in existing_configs}

                # Separate threads that need new configs vs updates
                threads_to_create = []
                threads_to_update = []

                for thread_id in thread_ids:
                    # Verify thread exists and belongs to user
                    try:
                        await threads_repo.get_by_id(thread_id)
                    except NotFound:
                        logger.warning("Thread not found during bulk enable", extra={
                            "thread_id": str(thread_id), "user_id": str(user_id)
                        })
                        continue

                    if thread_id in existing_thread_ids:
                        threads_to_update.append(thread_id)
                    else:
                        threads_to_create.append(ThreadTrackingConfigurationCreate(
                            thread_id=thread_id, is_active=True
                        ))

                # Bulk create new configurations
                created_configs = []
                if threads_to_create:
                    created_configs = await tracking_repo.bulk_create_tracking_configs(
                        threads_to_create, user_id
                    )

                # Bulk update existing configurations
                updated_count = 0
                if threads_to_update:
                    updated_count = await tracking_repo.bulk_update_tracking_status(
                        threads_to_update, True, user_id
                    )

                await uow.commit()

                logger.info("Bulk tracking enabled", extra={
                    "user_id": str(user_id),
                    "created_count": len(created_configs),
                    "updated_count": updated_count
                })

                return created_configs
        except Exception as e:
            logger.error("Failed to bulk enable tracking", extra={
                "user_id": str(user_id),
                "thread_count": len(thread_ids),
                "error": str(e)
            })
            raise BadRequest(f"Failed to enable tracking: {str(e)}")

    @trace_async
    async def bulk_disable_tracking(self, user_id: UUID, thread_ids: list[UUID]) -> int:
        """Disable tracking for multiple threads efficiently."""
        if not thread_ids:
            return 0

        try:
            async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                tracking_repo = ThreadTrackingRepository(uow.session)

                # Bulk update to inactive
                updated_count = await tracking_repo.bulk_update_tracking_status(
                    thread_ids, False, user_id
                )

                await uow.commit()

                logger.info("Bulk tracking disabled", extra={
                    "user_id": str(user_id),
                    "updated_count": updated_count
                })

                return updated_count
        except Exception as e:
            logger.error("Failed to bulk disable tracking", extra={
                "user_id": str(user_id),
                "thread_count": len(thread_ids),
                "error": str(e)
            })
            raise BadRequest(f"Failed to disable tracking: {str(e)}")

    @trace_async
    async def get_tracking_statistics(self, user_id: UUID) -> dict[str, int]:
        """Get tracking statistics for user."""
        try:
            async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                tracking_repo = ThreadTrackingRepository(uow.session)
                return await tracking_repo.get_tracking_stats(user_id)
        except Exception as e:
            logger.error("Failed to get tracking statistics", extra={
                "user_id": str(user_id),
                "error": str(e)
            })
            raise BadRequest(f"Failed to get tracking statistics: {str(e)}")

    async def _send_telemetry_event(
        self,
        event_type: str,
        user_id: UUID | None,
        data: dict[str, any]
    ) -> None:
        """Send telemetry event for tracking operations."""
        if not self.telemetry_service:
            return

        try:
            from datetime import UTC, datetime

            event = TelemetryEventCreate(
                event_type="ui_action",  # Use existing telemetry event type
                timestamp=datetime.now(UTC),
                user_id=str(user_id) if user_id else "system",
                device_id="server",
                session_id="tracking_service",
                platform="server",
                data={
                    "action_id": event_type,
                    "component": "thread_tracking",
                    **data
                }
            )

            # Use system context for telemetry (no RLS)
            async with async_uow_factory(self.session_factory, user_id=None, apply_rls=False)() as uow:
                from ...telemetry.repository import TelemetryRepository
                telemetry_repo = TelemetryRepository(uow.session)
                await telemetry_repo.create(event)
                await uow.commit()

        except Exception as e:
            # Don't fail the main operation if telemetry fails
            logger.warning("Failed to send telemetry event", extra={
                "event_type": event_type,
                "error": str(e)
            })

    def _get_metrics_summary(self) -> dict[str, int]:
        """Get current metrics summary."""
        return self._metrics.copy()

    @trace_async
    async def get_service_metrics(self) -> dict[str, int]:
        """Get service metrics for monitoring."""
        return self._get_metrics_summary()

    @trace_async
    async def reset_metrics(self) -> None:
        """Reset service metrics (for testing or periodic resets)."""
        self._metrics = {
            "tracking_enabled_count": 0,
            "tracking_disabled_count": 0,
            "tracking_checks_count": 0,
            "tracking_errors_count": 0,
        }
        logger.info("Thread tracking service metrics reset")


def create_thread_tracking_service(
    session_factory: async_sessionmaker[AsyncSession],
    notification_service: ThreadTrackingNotificationService | None = None,
    telemetry_service: TelemetryService | None = None,
) -> ThreadTrackingService:
    """Factory function for ThreadTrackingService."""
    return ThreadTrackingService(session_factory, notification_service, telemetry_service)
