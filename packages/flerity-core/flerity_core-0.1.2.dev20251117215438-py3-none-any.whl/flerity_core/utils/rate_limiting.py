"""
Redis-based rate limiting with sliding window algorithm.

Provides production-ready rate limiting for AI orchestrator and other services
using Redis sorted sets for accurate sliding window implementation.
"""

import asyncio
import logging
import time
from typing import Any
from uuid import UUID

try:
    import redis.asyncio as redis
    from redis.asyncio import Redis
    _HAS_REDIS = True
    RedisType = Redis
except ImportError:
    _HAS_REDIS = False
    redis = None  # type: ignore
    Redis = None  # type: ignore
    RedisType = type(None)  # type: ignore

from .errors import RateLimitError

try:
    from ..config import config
    _HAS_CONFIG = True
    ConfigType = type(config)
except ImportError:
    _HAS_CONFIG = False
    config = None  # type: ignore
    ConfigType = type(None)  # type: ignore

logger = logging.getLogger(__name__)

def get_rate_limits() -> dict[str, dict[str, int]]:
    """Get rate limits from config or use defaults."""
    if _HAS_CONFIG and config:
        return {
            "user_per_minute": {"limit": config.RATE_LIMIT_USER_PER_MINUTE, "window": 60},
            "user_per_hour": {"limit": config.RATE_LIMIT_USER_PER_HOUR, "window": 3600},
            "global_per_hour": {"limit": config.RATE_LIMIT_GLOBAL_PER_HOUR, "window": 3600},
            "premium_user_per_minute": {"limit": config.RATE_LIMIT_PREMIUM_USER_PER_MINUTE, "window": 60},
            "premium_user_per_hour": {"limit": config.RATE_LIMIT_PREMIUM_USER_PER_HOUR, "window": 3600},
        }

    # Default limits
    return {
        "user_per_minute": {"limit": 10, "window": 60},
        "user_per_hour": {"limit": 100, "window": 3600},
        "global_per_hour": {"limit": 1000, "window": 3600},
        "premium_user_per_minute": {"limit": 20, "window": 60},
        "premium_user_per_hour": {"limit": 200, "window": 3600},
    }

# Job type specific limits
JOB_TYPE_LIMITS: dict[str, dict[str, int]] = {
    "icebreaker": {"user_per_minute": 5, "user_per_hour": 50},
    "suggestion": {"user_per_minute": 8, "user_per_hour": 80},
    "analysis": {"user_per_minute": 3, "user_per_hour": 30},
    "deletion": {"user_per_minute": 2, "user_per_hour": 20},  # More restrictive for deletions
}


class RateLimiter:
    """Redis-based sliding window rate limiter."""

    def __init__(self, redis_client: RedisType):
        self.redis = redis_client

    async def check_rate_limit(
        self,
        user_id: UUID,
        job_type: str,
        is_premium: bool = False,
        thread_id: UUID | None = None,
    ) -> dict[str, int]:
        """Check rate limits and return remaining counts.
        
        Args:
            user_id: User identifier
            job_type: Type of AI job
            is_premium: Whether user has premium subscription
            thread_id: Optional thread identifier for per-thread limits
            
        Returns:
            Dict with remaining counts for each limit type
            
        Raises:
            RateLimitError: If any rate limit is exceeded
        """
        if not _HAS_REDIS:
            logger.warning("Redis not available, skipping rate limiting")
            return {"user_per_minute": 999, "user_per_hour": 999}

        current_time = time.time()
        user_str = str(user_id)

        # Get current rate limits
        rate_limits = get_rate_limits()

        # Determine limits based on premium status

        # Check user-level limits
        user_minute_key = f"ai:ratelimit:user:{user_str}:minute"
        user_hour_key = f"ai:ratelimit:user:{user_str}:hour"
        global_hour_key = "ai:ratelimit:global:hour"

        # Get job-specific limits
        job_limits = JOB_TYPE_LIMITS.get(job_type, {})

        # For premium users, use premium limits or job limits (whichever is higher)
        if is_premium:
            job_minute_limit = job_limits.get("user_per_minute", 0)
            premium_minute_limit = rate_limits["premium_user_per_minute"]["limit"]
            user_minute_limit = max(job_minute_limit, premium_minute_limit)

            job_hour_limit = job_limits.get("user_per_hour", 0)
            premium_hour_limit = rate_limits["premium_user_per_hour"]["limit"]
            user_hour_limit = max(job_hour_limit, premium_hour_limit)
        else:
            user_minute_limit = job_limits.get("user_per_minute", rate_limits["user_per_minute"]["limit"])
            user_hour_limit = job_limits.get("user_per_hour", rate_limits["user_per_hour"]["limit"])

        # Use Redis pipeline for atomic operations
        pipe = self.redis.pipeline()

        # Check and increment user per-minute limit
        self._check_and_increment(
            pipe, user_minute_key, current_time, 60, user_minute_limit
        )

        # Check and increment user per-hour limit
        self._check_and_increment(
            pipe, user_hour_key, current_time, 3600, user_hour_limit
        )

        # Check and increment global per-hour limit
        self._check_and_increment(
            pipe, global_hour_key, current_time, 3600, rate_limits["global_per_hour"]["limit"]
        )

        try:
            results = await pipe.execute()

            # Parse results (each check returns [count, remaining])
            user_minute_count, _user_minute_remaining = results[0], results[1]
            user_hour_count, _user_hour_remaining = results[2], results[3]
            global_hour_count, _global_hour_remaining = results[4], results[5]

            # Check if any limits exceeded
            if user_minute_count > user_minute_limit:
                raise RateLimitError(
                    f"User rate limit exceeded: {user_minute_count}/{user_minute_limit} per minute",
                    details={
                        "limit_type": "user_per_minute",
                        "current": user_minute_count,
                        "limit": user_minute_limit,
                        "reset_in": 60,
                    }
                )

            if user_hour_count > user_hour_limit:
                raise RateLimitError(
                    f"User rate limit exceeded: {user_hour_count}/{user_hour_limit} per hour",
                    details={
                        "limit_type": "user_per_hour",
                        "current": user_hour_count,
                        "limit": user_hour_limit,
                        "reset_in": 3600,
                    }
                )

            if global_hour_count > rate_limits["global_per_hour"]["limit"]:
                raise RateLimitError(
                    f"Global rate limit exceeded: {global_hour_count}/{rate_limits['global_per_hour']['limit']} per hour",
                    details={
                        "limit_type": "global_per_hour",
                        "current": global_hour_count,
                        "limit": rate_limits["global_per_hour"]["limit"],
                        "reset_in": 3600,
                    }
                )

            return {
                "user_per_minute": max(0, user_minute_limit - user_minute_count),
                "user_per_hour": max(0, user_hour_limit - user_hour_count),
                "global_per_hour": max(0, rate_limits["global_per_hour"]["limit"] - global_hour_count),
            }

        except RateLimitError:
            # Re-raise rate limit errors - these are intentional
            raise
        except Exception as e:
            logger.error(f"Error during rate limiting: {e}")
            # Fail open - allow request if Redis is down or any other error occurs
            return {"user_per_minute": 999, "user_per_hour": 999}

    def _check_and_increment(
        self,
        pipe: Any,
        key: str,
        current_time: float,
        window_seconds: int,
        limit: int
    ) -> None:
        """Add sliding window check and increment to pipeline."""
        window_start = current_time - window_seconds

        # Remove expired entries
        pipe.zremrangebyscore(key, 0, window_start)

        # Count current entries
        pipe.zcard(key)

        # Add current request
        pipe.zadd(key, {str(current_time): current_time})

        # Set expiration
        pipe.expire(key, window_seconds + 10)  # Extra buffer for cleanup

    async def get_rate_limit_headers(
        self,
        user_id: UUID,
        job_type: str,
        is_premium: bool = False,
    ) -> dict[str, str]:
        """Get rate limit headers for HTTP responses."""
        try:
            remaining = await self.check_rate_limit(user_id, job_type, is_premium)
            rate_limits = get_rate_limits()

            # Use the most restrictive limit for headers
            min_remaining = min(remaining.values())

            return {
                "X-RateLimit-Limit": str(rate_limits["user_per_minute"]["limit"]),
                "X-RateLimit-Remaining": str(min_remaining),
                "X-RateLimit-Reset": str(int(time.time() + 60)),  # Next minute
            }
        except RateLimitError as e:
            reset_time = int(time.time() + e.details.get("reset_in", 60))
            return {
                "X-RateLimit-Limit": str(e.details.get("limit", 0)),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(reset_time),
            }
        except Exception as e:
            logger.error(f"Error getting rate limit headers: {e}")
            return {}


async def create_rate_limiter(redis_url: str) -> RateLimiter | None:
    """Create rate limiter instance with Redis connection."""
    if not _HAS_REDIS:
        logger.warning("Redis not available, rate limiting disabled")
        return None

    try:
        redis_client = redis.from_url(redis_url, decode_responses=True)
        # Test connection
        await redis_client.ping()
        logger.info("Redis rate limiter initialized")
        return RateLimiter(redis_client)
    except Exception as e:
        logger.error(f"Failed to initialize Redis rate limiter: {e}")
        return None


# Sync version for backward compatibility
class SyncRateLimiter:
    """Synchronous wrapper for rate limiter."""

    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self._limiter: RateLimiter | None = None

    def check_rate_limit(
        self,
        user_id: UUID,
        job_type: str,
        is_premium: bool = False,
        thread_id: UUID | None = None,
    ) -> dict[str, int]:
        """Sync wrapper for rate limit check."""
        if not _HAS_REDIS:
            logger.warning("Redis not available, skipping rate limiting")
            return {"user_per_minute": 999, "user_per_hour": 999}

        # Create new event loop for sync context
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        if not self._limiter:
            self._limiter = loop.run_until_complete(
                create_rate_limiter(self.redis_url)
            )

        if not self._limiter:
            return {"user_per_minute": 999, "user_per_hour": 999}

        return loop.run_until_complete(
            self._limiter.check_rate_limit(user_id, job_type, is_premium, thread_id)
        )
