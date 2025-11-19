"""Cache warming utilities for thread deletion operations."""
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from ...db.uow import async_uow_factory
from ...utils.logging import get_logger
from ...utils.tracing import trace_async
from .cache import get_deletion_cache
from .repository import ThreadsRepository

logger = get_logger(__name__)


class ThreadDeletionCacheWarmer:
    """Utility for warming thread deletion caches."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory
        self.cache = get_deletion_cache()

    @trace_async
    async def warm_user_threads_deletion_cache(self, user_id: UUID, limit: int = 20) -> int:
        """Warm deletion preview cache for user's most recent threads."""
        try:
            async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                repository = ThreadsRepository(uow.session)

                # Get user's recent threads
                threads = await repository.get_by_user_id(user_id, limit=limit)

                warmed_count = 0
                for thread in threads:
                    try:
                        # Get deletion preview data and cache it
                        preview_data = await repository.get_deletion_preview(thread.id)
                        success = await self.cache.set_deletion_preview(thread.id, preview_data)

                        if success:
                            warmed_count += 1

                    except Exception as e:
                        logger.warning("Failed to warm cache for thread", extra={
                            "thread_id": str(thread.id),
                            "user_id": str(user_id),
                            "error": str(e)
                        })

                logger.info("Deletion cache warmed for user threads", extra={
                    "user_id": str(user_id),
                    "total_threads": len(threads),
                    "warmed_count": warmed_count
                })

                return warmed_count
        except Exception as e:
            logger.error("Failed to warm user threads deletion cache", extra={
                "user_id": str(user_id),
                "error": str(e)
            })
            return 0

    @trace_async
    async def warm_thread_deletion_cache(self, thread_id: UUID, user_id: UUID) -> bool:
        """Warm deletion preview cache for a specific thread."""
        try:
            async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                repository = ThreadsRepository(uow.session)

                # Verify thread exists and belongs to user
                try:
                    await repository.get_by_id(thread_id)
                except Exception:
                    logger.warning("Thread not found or access denied for cache warming", extra={
                        "thread_id": str(thread_id),
                        "user_id": str(user_id)
                    })
                    return False

                # Get and cache deletion preview data
                preview_data = await repository.get_deletion_preview(thread_id)
                success = await self.cache.set_deletion_preview(thread_id, preview_data)

                if success:
                    logger.debug("Thread deletion cache warmed", extra={
                        "thread_id": str(thread_id),
                        "user_id": str(user_id)
                    })

                return success
        except Exception as e:
            logger.error("Failed to warm thread deletion cache", extra={
                "thread_id": str(thread_id),
                "user_id": str(user_id),
                "error": str(e)
            })
            return False

    @trace_async
    async def batch_warm_deletion_cache(self, thread_ids: list[UUID], user_id: UUID) -> dict[str, int]:
        """Warm deletion preview cache for multiple threads in batch."""
        results = {"success": 0, "failed": 0, "total": len(thread_ids)}

        try:
            async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                repository = ThreadsRepository(uow.session)

                for thread_id in thread_ids:
                    try:
                        # Verify thread exists and belongs to user
                        await repository.get_by_id(thread_id)

                        # Get and cache deletion preview data
                        preview_data = await repository.get_deletion_preview(thread_id)
                        success = await self.cache.set_deletion_preview(thread_id, preview_data)

                        if success:
                            results["success"] += 1
                        else:
                            results["failed"] += 1

                    except Exception as e:
                        results["failed"] += 1
                        logger.warning("Failed to warm cache for thread in batch", extra={
                            "thread_id": str(thread_id),
                            "user_id": str(user_id),
                            "error": str(e)
                        })

                logger.info("Batch deletion cache warming completed", extra={
                    "user_id": str(user_id),
                    "results": results
                })

        except Exception as e:
            logger.error("Failed to batch warm deletion cache", extra={
                "user_id": str(user_id),
                "thread_count": len(thread_ids),
                "error": str(e)
            })

        return results


def create_cache_warmer(session_factory: async_sessionmaker[AsyncSession]) -> ThreadDeletionCacheWarmer:
    """Factory function for ThreadDeletionCacheWarmer."""
    return ThreadDeletionCacheWarmer(session_factory)
