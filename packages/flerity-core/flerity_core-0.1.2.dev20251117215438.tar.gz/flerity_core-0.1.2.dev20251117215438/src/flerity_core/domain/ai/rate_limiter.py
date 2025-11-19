"""
AI Rate Limiter for cost control.

Implements token bucket algorithm to limit AI API calls.
"""
from uuid import UUID

from ...utils.logging import get_logger
from ...utils.redis_client import RedisClient

logger = get_logger(__name__)


class AIRateLimiter:
    """Rate limiter for AI API calls using token bucket algorithm."""

    def __init__(
        self,
        redis_client: RedisClient,
        max_calls_per_hour: int = 100,
        max_calls_per_day: int = 1000
    ):
        """
        Initialize rate limiter.

        Args:
            redis_client: Redis client for distributed rate limiting
            max_calls_per_hour: Maximum AI calls per hour per user
            max_calls_per_day: Maximum AI calls per day per user
        """
        self.redis = redis_client
        self.max_calls_per_hour = max_calls_per_hour
        self.max_calls_per_day = max_calls_per_day

    async def check_rate_limit(
        self,
        user_id: UUID,
        operation: str = "ai_analysis"
    ) -> tuple[bool, str | None]:
        """
        Check if user can make an AI call.

        Args:
            user_id: User ID
            operation: Operation type (for separate limits)

        Returns:
            (allowed, reason) - True if allowed, False with reason if not
        """
        try:
            # Check hourly limit
            hourly_key = f"ai_rate_limit:hourly:{user_id}:{operation}"
            hourly_count = await self._get_count(hourly_key)

            if hourly_count >= self.max_calls_per_hour:
                return False, f"Hourly limit exceeded ({self.max_calls_per_hour} calls/hour)"

            # Check daily limit
            daily_key = f"ai_rate_limit:daily:{user_id}:{operation}"
            daily_count = await self._get_count(daily_key)

            if daily_count >= self.max_calls_per_day:
                return False, f"Daily limit exceeded ({self.max_calls_per_day} calls/day)"

            return True, None

        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            # Fail open - allow request if Redis is down
            return True, None

    async def increment(
        self,
        user_id: UUID,
        operation: str = "ai_analysis"
    ) -> None:
        """
        Increment rate limit counters after successful AI call.

        Args:
            user_id: User ID
            operation: Operation type
        """
        try:
            # Increment hourly counter (1 hour TTL)
            hourly_key = f"ai_rate_limit:hourly:{user_id}:{operation}"
            await self._increment_counter(hourly_key, ttl=3600)

            # Increment daily counter (24 hours TTL)
            daily_key = f"ai_rate_limit:daily:{user_id}:{operation}"
            await self._increment_counter(daily_key, ttl=86400)

        except Exception as e:
            logger.error(f"Rate limit increment failed: {e}")

    async def get_remaining(
        self,
        user_id: UUID,
        operation: str = "ai_analysis"
    ) -> dict[str, int]:
        """
        Get remaining AI calls for user.

        Args:
            user_id: User ID
            operation: Operation type

        Returns:
            {
                "hourly_remaining": int,
                "daily_remaining": int
            }
        """
        try:
            hourly_key = f"ai_rate_limit:hourly:{user_id}:{operation}"
            daily_key = f"ai_rate_limit:daily:{user_id}:{operation}"

            hourly_count = await self._get_count(hourly_key)
            daily_count = await self._get_count(daily_key)

            return {
                "hourly_remaining": max(0, self.max_calls_per_hour - hourly_count),
                "daily_remaining": max(0, self.max_calls_per_day - daily_count)
            }

        except Exception as e:
            logger.error(f"Get remaining failed: {e}")
            return {
                "hourly_remaining": self.max_calls_per_hour,
                "daily_remaining": self.max_calls_per_day
            }

    async def _get_count(self, key: str) -> int:
        """Get current count from Redis."""
        value = await self.redis.get(key)
        return int(value) if value else 0

    async def _increment_counter(self, key: str, ttl: int) -> None:
        """Increment counter with TTL."""
        current = await self.redis.get(key)

        if current is None:
            # First increment - set with TTL
            await self.redis.set(key, "1", ex=ttl)
        else:
            # Increment existing counter
            await self.redis.incr(key)
