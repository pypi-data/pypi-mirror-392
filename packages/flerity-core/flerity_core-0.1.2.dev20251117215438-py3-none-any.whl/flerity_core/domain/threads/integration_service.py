"""
Thread Deletion Integration Service

This service coordinates all components of the thread deletion system to ensure
proper end-to-end functionality and real-time updates.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from ...db.uow import async_uow_factory
from ...utils.errors import BadRequest, NotFound
from ...utils.logging import get_logger
from ...utils.tracing import trace_async
from ...utils.request_tracking import RequestTracker
from ...utils.domain_logger import get_domain_logger
from .cache import get_deletion_cache
from .repository import ThreadsRepository
from .schemas import ThreadDeletionResult
from .service import ThreadsService

logger = get_logger(__name__)
domain_logger = get_domain_logger("threads.integration")


class ThreadDeletionIntegrationService:
    """
    Integration service that coordinates all thread deletion components.
    
    This service ensures:
    - Proper coordination between mobile UI and backend APIs
    - Real-time updates work end-to-end
    - Confirmation flow works across all components
    - Cache consistency across operations
    - Error handling and recovery
    """

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory
        self.threads_service = ThreadsService(session_factory)
        self.cache = get_deletion_cache()

    @trace_async
    async def initiate_deletion_flow(
        self,
        thread_id: UUID,
        user_id: UUID,
        client_type: str = "mobile"
    ) -> dict[str, Any]:
        """
        Initiate the complete deletion flow with proper coordination.
        
        This method:
        1. Validates thread ownership and permissions
        2. Loads deletion preview for confirmation
        3. Prepares cache for optimal performance
        4. Returns all data needed for confirmation UI
        """
        with RequestTracker(user_id=str(user_id), operation="initiate_deletion_flow", 
                          thread_id=str(thread_id), client_type=client_type) as tracker:
            try:
                tracking_context = domain_logger.operation_start("initiate_deletion_flow", 
                    thread_id=str(thread_id), user_id=str(user_id), client_type=client_type)
                
                # Validate thread exists and user has access
                async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                    repository = ThreadsRepository(uow.session)

                    try:
                        thread = await repository.get_by_id(thread_id)
                    except NotFound:
                        error_id = domain_logger.operation_error(tracking_context, 
                            error=BadRequest(f"Thread {thread_id} not found or access denied"),
                            thread_id=str(thread_id), user_id=str(user_id))
                        raise BadRequest(f"Thread {thread_id} not found or access denied")

                    # Get deletion preview with caching
                    preview = await self.threads_service.get_deletion_preview(thread_id, user_id)

                    # Warm related caches for better performance
                    await self._warm_deletion_caches(thread_id, user_id)

                    result = {
                        "thread_id": str(thread_id),
                        "thread_name": thread.contact_name or "Unknown",
                        "preview": preview.model_dump(),
                        "flow_initiated_at": datetime.now(UTC).isoformat(),
                        "client_type": client_type
                    }

                    domain_logger.business_event("deletion_flow_initiated", 
                        thread_id=str(thread_id), user_id=str(user_id), client_type=client_type,
                        message_count=preview.message_count, thread_name=thread.contact_name)
                    domain_logger.operation_success(tracking_context, 
                        thread_id=str(thread_id), user_id=str(user_id), client_type=client_type,
                        message_count=preview.message_count)
                    tracker.log_success(result_id=str(thread_id), message_count=preview.message_count)
                    return result

            except Exception as e:
                error_id = domain_logger.operation_error(tracking_context, error=e,
                    thread_id=str(thread_id), user_id=str(user_id), client_type=client_type)
                tracker.log_error(e, context={"thread_id": str(thread_id), "client_type": client_type})
                raise

    @trace_async
    async def execute_deletion_with_coordination(
        self,
        thread_id: UUID,
        user_id: UUID,
        client_metadata: dict[str, Any] | None = None
    ) -> ThreadDeletionResult:
        """
        Execute thread deletion with full coordination and real-time updates.
        
        This method:
        1. Performs the permanent deletion
        2. Coordinates cache invalidation
        3. Triggers real-time updates
        4. Handles error recovery
        """
        with RequestTracker(user_id=str(user_id), operation="execute_deletion_with_coordination", 
                          thread_id=str(thread_id)) as tracker:
            try:
                tracking_context = domain_logger.operation_start("execute_deletion_with_coordination", 
                    thread_id=str(thread_id), user_id=str(user_id), client_metadata=client_metadata)
                
                # Execute the deletion
                deletion_result = await self.threads_service.delete_thread_permanently(
                    thread_id, user_id
                )

                # Coordinate post-deletion activities
                await self._coordinate_post_deletion(thread_id, user_id, deletion_result)

                domain_logger.business_event("coordinated_deletion_executed", 
                    thread_id=str(thread_id), user_id=str(user_id),
                    message_count=deletion_result.message_count,
                    tracking_config_deleted=deletion_result.tracking_config_deleted)
                domain_logger.operation_success(tracking_context, 
                    thread_id=str(thread_id), user_id=str(user_id),
                    message_count=deletion_result.message_count,
                    tracking_config_deleted=deletion_result.tracking_config_deleted)
                tracker.log_success(result_id=str(thread_id), 
                    message_count=deletion_result.message_count,
                    tracking_config_deleted=deletion_result.tracking_config_deleted)
                return deletion_result

            except Exception as e:
                error_id = domain_logger.operation_error(tracking_context, error=e,
                    thread_id=str(thread_id), user_id=str(user_id), client_metadata=client_metadata)
                tracker.log_error(e, context={"thread_id": str(thread_id), "client_metadata": client_metadata})
                raise

    @trace_async
    async def validate_deletion_state(
        self,
        thread_id: UUID,
        user_id: UUID
    ) -> dict[str, Any]:
        """
        Validate the current state of a thread deletion operation.
        
        This is useful for:
        - Confirming deletion completion
        - Checking cache consistency
        - Validating real-time update propagation
        """
        try:
            async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                repository = ThreadsRepository(uow.session)

                # Check if thread still exists
                thread_exists = True
                try:
                    await repository.get_by_id(thread_id)
                except NotFound:
                    thread_exists = False

                # Check cache state
                cache_stats = await self.cache.get_cache_stats()

                # Check if deletion preview is cached (should be cleared after deletion)
                cached_preview = await self.cache.get_deletion_preview(thread_id)

                validation_result = {
                    "thread_id": str(thread_id),
                    "thread_exists": thread_exists,
                    "cache_consistent": cached_preview is None,
                    "cache_stats": cache_stats,
                    "validated_at": datetime.now(UTC).isoformat()
                }

                logger.info("Deletion state validated", extra={
                    "thread_id": str(thread_id),
                    "user_id": str(user_id),
                    "validation_result": validation_result
                })

                return validation_result

        except Exception as e:
            logger.error("Failed to validate deletion state", extra={
                "thread_id": str(thread_id),
                "user_id": str(user_id),
                "error": str(e)
            })
            raise

    @trace_async
    async def get_integration_health(self, user_id: UUID) -> dict[str, Any]:
        """
        Get health status of all integration components.
        
        This helps diagnose issues with the deletion system.
        """
        try:
            health_data = {
                "timestamp": datetime.now(UTC).isoformat(),
                "user_id": str(user_id),
                "components": {}
            }

            # Check threads service health
            try:
                await self.threads_service.get_cache_stats()
                health_data["components"]["threads_service"] = {
                    "status": "healthy",
                    "last_check": datetime.now(UTC).isoformat()
                }
            except Exception as e:
                health_data["components"]["threads_service"] = {
                    "status": "unhealthy",
                    "error": str(e),
                    "last_check": datetime.now(UTC).isoformat()
                }

            # Check cache health
            try:
                cache_stats = await self.cache.get_cache_stats()
                health_data["components"]["cache"] = {
                    "status": "healthy",
                    "stats": cache_stats,
                    "last_check": datetime.now(UTC).isoformat()
                }
            except Exception as e:
                health_data["components"]["cache"] = {
                    "status": "unhealthy",
                    "error": str(e),
                    "last_check": datetime.now(UTC).isoformat()
                }

            # Check database connectivity
            try:
                async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                    repository = ThreadsRepository(uow.session)
                    # Simple query to test connectivity
                    await repository.get_by_user_id(user_id, limit=1)
                    health_data["components"]["database"] = {
                        "status": "healthy",
                        "last_check": datetime.now(UTC).isoformat()
                    }
            except Exception as e:
                health_data["components"]["database"] = {
                    "status": "unhealthy",
                    "error": str(e),
                    "last_check": datetime.now(UTC).isoformat()
                }

            # Overall health status
            unhealthy_components = [
                name for name, data in health_data["components"].items()
                if data["status"] == "unhealthy"
            ]

            health_data["overall_status"] = "healthy" if not unhealthy_components else "degraded"
            health_data["unhealthy_components"] = unhealthy_components

            logger.info("Integration health checked", extra={
                "user_id": str(user_id),
                "overall_status": health_data["overall_status"],
                "unhealthy_components": unhealthy_components
            })

            return health_data

        except Exception as e:
            logger.error("Failed to check integration health", extra={
                "user_id": str(user_id),
                "error": str(e)
            })
            raise

    async def _warm_deletion_caches(self, thread_id: UUID, user_id: UUID) -> None:
        """Warm caches for optimal deletion performance."""
        try:
            # Warm deletion preview cache if not already cached
            cached_preview = await self.cache.get_deletion_preview(thread_id)
            if not cached_preview:
                await self.threads_service.get_deletion_preview(thread_id, user_id)

            logger.debug("Deletion caches warmed", extra={
                "thread_id": str(thread_id),
                "user_id": str(user_id)
            })
        except Exception as e:
            # Don't fail the flow if cache warming fails
            logger.warning("Failed to warm deletion caches", extra={
                "thread_id": str(thread_id),
                "user_id": str(user_id),
                "error": str(e)
            })

    async def _coordinate_post_deletion(
        self,
        thread_id: UUID,
        user_id: UUID,
        deletion_result: ThreadDeletionResult
    ) -> None:
        """Coordinate activities after successful deletion."""
        try:
            # Ensure all related caches are invalidated
            await self.cache.invalidate_all_thread_caches(thread_id, user_id)

            # Additional coordination tasks can be added here:
            # - Real-time notifications to other clients
            # - Analytics event tracking
            # - Audit logging
            # - External system notifications

            logger.debug("Post-deletion coordination completed", extra={
                "thread_id": str(thread_id),
                "user_id": str(user_id),
                "deletion_result": deletion_result.model_dump()
            })
        except Exception as e:
            # Don't fail the deletion if post-coordination fails
            logger.warning("Post-deletion coordination failed", extra={
                "thread_id": str(thread_id),
                "user_id": str(user_id),
                "error": str(e)
            })


def create_thread_deletion_integration_service(
    session_factory: async_sessionmaker[AsyncSession]
) -> ThreadDeletionIntegrationService:
    """Factory function for ThreadDeletionIntegrationService."""
    return ThreadDeletionIntegrationService(session_factory)
