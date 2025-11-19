"""Thread deletion caching service for performance optimization."""
from typing import Any
from uuid import UUID

from ...utils.logging import get_logger
from ...utils.redis_client import get_redis_client
from ...utils.tracing import trace_async

logger = get_logger(__name__)


class ThreadDeletionCache:
    """Cache service for thread deletion operations."""

    # Cache key patterns
    DELETION_PREVIEW_KEY = "thread_deletion_preview:{thread_id}"
    USER_THREADS_KEY = "user_threads:{user_id}"
    THREAD_DATA_KEY = "thread_data:{thread_id}"

    # Cache TTL values (in seconds)
    DELETION_PREVIEW_TTL = 300  # 5 minutes - short TTL for preview data
    USER_THREADS_TTL = 600      # 10 minutes - medium TTL for thread lists
    THREAD_DATA_TTL = 1800      # 30 minutes - longer TTL for thread data

    def __init__(self):
        self.redis = get_redis_client()

    @trace_async
    async def get_deletion_preview(self, thread_id: UUID) -> dict[str, Any] | None:
        """Get cached deletion preview data."""
        try:
            key = self.DELETION_PREVIEW_KEY.format(thread_id=str(thread_id))
            cached_data = await self.redis.get_json(key)

            if cached_data:
                logger.debug("Deletion preview cache hit", extra={
                    "thread_id": str(thread_id),
                    "cache_key": key
                })
                return cached_data

            logger.debug("Deletion preview cache miss", extra={
                "thread_id": str(thread_id),
                "cache_key": key
            })
            return None
        except Exception as e:
            logger.warning("Failed to get deletion preview from cache", extra={
                "thread_id": str(thread_id),
                "error": str(e)
            })
            return None

    @trace_async
    async def set_deletion_preview(self, thread_id: UUID, preview_data: dict[str, Any]) -> bool:
        """Cache deletion preview data."""
        try:
            key = self.DELETION_PREVIEW_KEY.format(thread_id=str(thread_id))

            # Ensure thread_id is serializable
            serializable_data = {
                **preview_data,
                "thread_id": str(preview_data.get("thread_id", thread_id))
            }

            success = await self.redis.set(key, serializable_data, ex=self.DELETION_PREVIEW_TTL)

            if success:
                logger.debug("Deletion preview cached successfully", extra={
                    "thread_id": str(thread_id),
                    "cache_key": key,
                    "ttl": self.DELETION_PREVIEW_TTL
                })

            return success
        except Exception as e:
            logger.warning("Failed to cache deletion preview", extra={
                "thread_id": str(thread_id),
                "error": str(e)
            })
            return False

    @trace_async
    async def invalidate_deletion_preview(self, thread_id: UUID) -> bool:
        """Invalidate cached deletion preview data."""
        try:
            key = self.DELETION_PREVIEW_KEY.format(thread_id=str(thread_id))
            deleted_count = await self.redis.delete(key)

            logger.debug("Deletion preview cache invalidated", extra={
                "thread_id": str(thread_id),
                "cache_key": key,
                "deleted": deleted_count > 0
            })

            return deleted_count > 0
        except Exception as e:
            logger.warning("Failed to invalidate deletion preview cache", extra={
                "thread_id": str(thread_id),
                "error": str(e)
            })
            return False

    @trace_async
    async def invalidate_user_threads(self, user_id: UUID) -> bool:
        """Invalidate cached user threads data."""
        try:
            key = self.USER_THREADS_KEY.format(user_id=str(user_id))
            deleted_count = await self.redis.delete(key)

            logger.debug("User threads cache invalidated", extra={
                "user_id": str(user_id),
                "cache_key": key,
                "deleted": deleted_count > 0
            })

            return deleted_count > 0
        except Exception as e:
            logger.warning("Failed to invalidate user threads cache", extra={
                "user_id": str(user_id),
                "error": str(e)
            })
            return False

    @trace_async
    async def invalidate_thread_data(self, thread_id: UUID) -> bool:
        """Invalidate cached thread data."""
        try:
            key = self.THREAD_DATA_KEY.format(thread_id=str(thread_id))
            deleted_count = await self.redis.delete(key)

            logger.debug("Thread data cache invalidated", extra={
                "thread_id": str(thread_id),
                "cache_key": key,
                "deleted": deleted_count > 0
            })

            return deleted_count > 0
        except Exception as e:
            logger.warning("Failed to invalidate thread data cache", extra={
                "thread_id": str(thread_id),
                "error": str(e)
            })
            return False

    @trace_async
    async def invalidate_all_thread_caches(self, thread_id: UUID, user_id: UUID) -> None:
        """Invalidate all caches related to a thread."""
        try:
            # Invalidate deletion preview cache
            await self.invalidate_deletion_preview(thread_id)

            # Invalidate thread data cache
            await self.invalidate_thread_data(thread_id)

            # Invalidate user threads cache
            await self.invalidate_user_threads(user_id)

            logger.info("All thread caches invalidated", extra={
                "thread_id": str(thread_id),
                "user_id": str(user_id)
            })
        except Exception as e:
            logger.warning("Failed to invalidate all thread caches", extra={
                "thread_id": str(thread_id),
                "user_id": str(user_id),
                "error": str(e)
            })

    @trace_async
    async def warm_deletion_preview_cache(self, thread_id: UUID, preview_data: dict[str, Any]) -> bool:
        """Warm the deletion preview cache with fresh data."""
        return await self.set_deletion_preview(thread_id, preview_data)

    @trace_async
    async def get_cache_stats(self) -> dict[str, Any]:
        """Get cache statistics for monitoring."""
        try:
            client = await self.redis.get_client()
            info = await client.info("memory")

            return {
                "used_memory": info.get("used_memory", 0),
                "used_memory_human": info.get("used_memory_human", "0B"),
                "connected_clients": info.get("connected_clients", 0),
                "cache_hit_rate": "N/A"  # Would need separate tracking
            }
        except Exception as e:
            logger.warning("Failed to get cache stats", extra={"error": str(e)})
            return {}


# Global cache instance
_deletion_cache: ThreadDeletionCache | None = None


def get_deletion_cache() -> ThreadDeletionCache:
    """Get global thread deletion cache instance."""
    global _deletion_cache
    if _deletion_cache is None:
        _deletion_cache = ThreadDeletionCache()
    return _deletion_cache
