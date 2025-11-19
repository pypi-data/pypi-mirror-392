"""Redis client utility for flerity_core."""

import json
import logging
from typing import Any

import redis.asyncio as redis
from redis.asyncio import Redis

from ..config import config

logger = logging.getLogger(__name__)


class RedisClient:
    """Async Redis client wrapper."""

    def __init__(self, redis_url: str | None = None):
        self.redis_url = redis_url or config.REDIS_URL
        self._client: Redis | None = None

    async def get_client(self) -> Redis:
        """Get or create Redis client."""
        if self._client is None:
            self._client = redis.from_url(self.redis_url, decode_responses=True)
        return self._client

    async def set(self, key: str, value: str | dict[str, Any], ex: int | None = None) -> bool:
        """Set key-value with optional expiration."""
        client = await self.get_client()
        if isinstance(value, dict):
            value = json.dumps(value)
        return await client.set(key, value, ex=ex)

    async def get(self, key: str) -> str | None:
        """Get value by key."""
        client = await self.get_client()
        return await client.get(key)

    async def get_json(self, key: str) -> dict[str, Any] | None:
        """Get JSON value by key."""
        value = await self.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                logger.warning(f"Failed to decode JSON for key: {key}")
        return None

    async def delete(self, key: str) -> int:
        """Delete key."""
        client = await self.get_client()
        return await client.delete(key)

    async def ping(self) -> bool:
        """Test Redis connection."""
        try:
            client = await self.get_client()
            await client.ping()
            return True
        except Exception as e:
            logger.error(f"Redis ping failed: {e}")
            return False

    async def incr(self, key: str, amount: int = 1) -> int:
        """Increment key by amount."""
        client = await self.get_client()
        return await client.incr(key, amount)

    async def expire(self, key: str, time: int) -> bool:
        """Set expiration time for key."""
        client = await self.get_client()
        return await client.expire(key, time)

    async def ttl(self, key: str) -> int:
        """Get time to live for key."""
        client = await self.get_client()
        return await client.ttl(key)

    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        client = await self.get_client()
        return bool(await client.exists(key))

    async def scan_iter(self, match: str | None = None, count: int | None = None):
        """Iterate over keys matching pattern."""
        client = await self.get_client()
        async for key in client.scan_iter(match=match, count=count):
            yield key

    async def close(self) -> None:
        """Close Redis connection."""
        if self._client:
            await self._client.aclose()
            self._client = None


# Global Redis client instance
_redis_client: RedisClient | None = None


def get_redis_client() -> RedisClient:
    """Get global Redis client instance."""
    global _redis_client
    if _redis_client is None:
        _redis_client = RedisClient()
    return _redis_client
