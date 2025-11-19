"""Analytics caching layer for performance optimization."""

import json
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel
from redis.asyncio import Redis

from flerity_core.utils.clock import utcnow
from flerity_core.utils.logging import get_logger

logger = get_logger(__name__)


class CachedAnalytics(BaseModel):
    """Cached analytics data with metadata."""
    data: dict[str, Any]
    cached_at: datetime
    tier: str  # "tier1" or "tier2"


class AnalyticsCache:
    """Redis-based cache for analytics metrics."""

    # Cache TTLs
    TIER1_TTL = 300  # 5 minutes (frequent updates)
    TIER2_TTL = 900  # 15 minutes (AI analysis is expensive)
    OVERVIEW_TTL = 1800  # 30 minutes (aggregated data)

    def __init__(self, redis_client: Redis):
        self.redis = redis_client

    def _make_key(self, prefix: str, user_id: UUID, thread_id: UUID | None = None) -> str:
        """Generate cache key."""
        if thread_id:
            return f"analytics:{prefix}:{user_id}:{thread_id}"
        return f"analytics:{prefix}:{user_id}"

    async def get_tier1(self, user_id: UUID, thread_id: UUID) -> dict[str, Any] | None:
        """Get cached TIER 1 analytics."""
        key = self._make_key("tier1", user_id, thread_id)
        cached = await self.redis.get(key)
        
        if cached:
            logger.debug("Analytics TIER 1 cache hit", extra={
                "user_id": str(user_id),
                "thread_id": str(thread_id)
            })
            data = json.loads(cached)
            return data["data"]
        
        logger.debug("Analytics TIER 1 cache miss", extra={
            "user_id": str(user_id),
            "thread_id": str(thread_id)
        })
        return None

    async def set_tier1(self, user_id: UUID, thread_id: UUID, data: dict[str, Any], last_activity_hours: int | None = None) -> None:
        """Cache TIER 1 analytics with dynamic TTL."""
        key = self._make_key("tier1", user_id, thread_id)
        cached = CachedAnalytics(
            data=data,
            cached_at=utcnow(),
            tier="tier1"
        )
        
        # Dynamic TTL: inactive threads (>72h) get 1h cache, active get 5min
        ttl = 3600 if last_activity_hours and last_activity_hours > 72 else self.TIER1_TTL
        
        await self.redis.setex(
            key,
            ttl,
            json.dumps(cached.model_dump(), default=str)
        )
        
        logger.debug("Analytics TIER 1 cached", extra={
            "user_id": str(user_id),
            "thread_id": str(thread_id),
            "ttl": ttl
        })

    async def get_tier2(self, user_id: UUID, thread_id: UUID) -> dict[str, Any] | None:
        """Get cached TIER 2 analytics (includes AI analysis)."""
        key = self._make_key("tier2", user_id, thread_id)
        cached = await self.redis.get(key)
        
        if cached:
            logger.debug("Analytics TIER 2 cache hit", extra={
                "user_id": str(user_id),
                "thread_id": str(thread_id)
            })
            data = json.loads(cached)
            return data["data"]
        
        logger.debug("Analytics TIER 2 cache miss", extra={
            "user_id": str(user_id),
            "thread_id": str(thread_id)
        })
        return None

    async def set_tier2(self, user_id: UUID, thread_id: UUID, data: dict[str, Any]) -> None:
        """Cache TIER 2 analytics (AI analysis)."""
        key = self._make_key("tier2", user_id, thread_id)
        cached = CachedAnalytics(
            data=data,
            cached_at=utcnow(),
            tier="tier2"
        )
        
        await self.redis.setex(
            key,
            self.TIER2_TTL,
            json.dumps(cached.model_dump(), default=str)
        )
        
        logger.debug("Analytics TIER 2 cached", extra={
            "user_id": str(user_id),
            "thread_id": str(thread_id),
            "ttl": self.TIER2_TTL
        })

    async def get_overview(self, user_id: UUID) -> dict[str, Any] | None:
        """Get cached overview analytics."""
        key = self._make_key("overview", user_id)
        cached = await self.redis.get(key)
        
        if cached:
            logger.debug("Analytics overview cache hit", extra={"user_id": str(user_id)})
            data = json.loads(cached)
            return data["data"]
        
        logger.debug("Analytics overview cache miss", extra={"user_id": str(user_id)})
        return None

    async def set_overview(self, user_id: UUID, data: dict[str, Any]) -> None:
        """Cache overview analytics."""
        key = self._make_key("overview", user_id)
        cached = CachedAnalytics(
            data=data,
            cached_at=utcnow(),
            tier="overview"
        )
        
        await self.redis.setex(
            key,
            self.OVERVIEW_TTL,
            json.dumps(cached.model_dump(), default=str)
        )
        
        logger.debug("Analytics overview cached", extra={
            "user_id": str(user_id),
            "ttl": self.OVERVIEW_TTL
        })

    async def invalidate_thread(self, user_id: UUID, thread_id: UUID) -> None:
        """Invalidate all cache for a specific thread."""
        keys = [
            self._make_key("tier1", user_id, thread_id),
            self._make_key("tier2", user_id, thread_id),
            self._make_key("overview", user_id)
        ]
        
        deleted = await self.redis.delete(*keys)
        logger.info("Analytics cache invalidated", extra={
            "user_id": str(user_id),
            "thread_id": str(thread_id),
            "keys_deleted": deleted
        })

    async def invalidate_user(self, user_id: UUID) -> None:
        """Invalidate all cache for a user."""
        pattern = f"analytics:*:{user_id}:*"
        cursor = 0
        deleted = 0
        
        while True:
            cursor, keys = await self.redis.scan(cursor, match=pattern, count=100)
            if keys:
                deleted += await self.redis.delete(*keys)
            if cursor == 0:
                break
        
        logger.info("User analytics cache invalidated", extra={
            "user_id": str(user_id),
            "keys_deleted": deleted
        })
    
    async def invalidate_batch(self, invalidations: list[tuple[UUID, UUID]]) -> None:
        """Invalidate multiple threads efficiently (batch operation)."""
        if not invalidations:
            return
        
        keys = []
        for user_id, thread_id in invalidations:
            keys.extend([
                self._make_key("tier1", user_id, thread_id),
                self._make_key("tier2", user_id, thread_id),
            ])
        
        if keys:
            deleted = await self.redis.delete(*keys)
            logger.info("Batch cache invalidation", extra={
                "threads_count": len(invalidations),
                "keys_deleted": deleted
            })
