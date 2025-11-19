"""Quota service for usage limit enforcement and tracking."""

from datetime import date, datetime, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from ...db.uow import async_uow_factory
from ...utils.clock import utcnow
from ...utils.errors import BadRequest, QuotaExceededError
from ...utils.logging import get_logger
from ...utils.redis_client import get_redis_client
from ...utils.tracing import trace_async
from ...utils.request_tracking import RequestTracker
from ...utils.domain_logger import get_domain_logger
from .config import SubscriptionConfig, get_subscription_config
from .repository import SubscriptionRepository
from .schemas import QuotaType, SubscriptionTier
from .service import SubscriptionService

logger = get_logger(__name__)
domain_logger = get_domain_logger(__name__)


class QuotaStatus:
    """Represents the current quota status for a user."""

    def __init__(
        self,
        quota_type: QuotaType,
        current_usage: int,
        limit: int,
        remaining: int,
        reset_time: datetime,
        is_exceeded: bool = False
    ):
        self.quota_type = quota_type
        self.current_usage = current_usage
        self.limit = limit
        self.remaining = remaining
        self.reset_time = reset_time
        self.is_exceeded = is_exceeded


class QuotaService:
    """Service for managing usage quotas and limits."""

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        subscription_service: SubscriptionService | None = None,
        config: SubscriptionConfig | None = None
    ):
        self.session_factory = session_factory
        self.subscription_service = subscription_service
        self.redis_client = get_redis_client()

        # Load configuration
        self.config = config or get_subscription_config()

        # Cache TTL for quota data from config
        self.quota_cache_ttl = self.config.quota_cache_ttl

        # Quota limits configuration from config
        self.quota_limits = {
            SubscriptionTier.TRIAL: {
                QuotaType.ICEBREAKER: self.config.trial_icebreaker_limit,
                QuotaType.SUGGESTION: self.config.trial_suggestion_limit,
                QuotaType.THREAD: self.config.trial_thread_limit
            },
            SubscriptionTier.PAID: {
                QuotaType.ICEBREAKER: self.config.paid_icebreaker_limit,
                QuotaType.SUGGESTION: self.config.paid_suggestion_limit,
                QuotaType.THREAD: self.config.paid_thread_limit
            }
        }

    @trace_async
    async def check_quota(
        self,
        user_id: UUID,
        quota_type: QuotaType,
        thread_id: UUID | None = None,
        uow: Any | None = None
    ) -> QuotaStatus:
        """Check current quota status for user with Redis-based counting.
        
        Args:
            user_id: User ID
            quota_type: Type of quota to check
            thread_id: Optional thread ID for thread-specific quotas
            uow: Optional Unit of Work to reuse existing DB connection
        """
        with RequestTracker(user_id=user_id, operation="check_quota") as tracker:
            try:
                tracking_context = domain_logger.operation_start(
                    operation="check_quota",
                    context={
                        "user_id": str(user_id),
                        "quota_type": quota_type.value,
                        "thread_id": str(thread_id) if thread_id else None
                    }
                )

                # Get user's subscription tier
                if self.subscription_service:
                    tier = await self.subscription_service.get_subscription_tier(user_id)
                elif uow:
                    # Use provided UoW to avoid creating new connection
                    repo = SubscriptionRepository(uow.session)
                    status = await repo.get_by_user_id(user_id)
                    tier = status.subscription_tier if status else SubscriptionTier.TRIAL
                else:
                    # Fallback to database lookup (creates new connection)
                    async with async_uow_factory(self.session_factory, user_id=str(user_id))() as temp_uow:
                        repo = SubscriptionRepository(temp_uow.session)
                        status = await repo.get_by_user_id(user_id)
                        tier = status.subscription_tier if status else SubscriptionTier.TRIAL

                # Get quota limits for this tier
                limits = await self.get_quota_limits(tier)
                limit = limits.get(quota_type, 0)

                # For unlimited quotas, return unlimited status
                if limit == -1:
                    quota_status = QuotaStatus(
                        quota_type=quota_type,
                        current_usage=0,
                        limit=-1,
                        remaining=-1,
                        reset_time=self._get_next_reset_time(),
                        is_exceeded=False
                    )
                    
                    tracker.log_success(result_id=str(user_id))
                    domain_logger.operation_success(
                        tracking_context,
                        result_id=str(user_id),
                        user_id=str(user_id),
                        quota_type=quota_type.value,
                        tier=tier.value,
                        unlimited=True
                    )
                    
                    return quota_status

                # Get current usage from Redis
                current_usage = await self._get_current_usage(user_id, quota_type, thread_id, tier)

                # Calculate remaining quota
                remaining = max(0, limit - current_usage)
                is_exceeded = current_usage >= limit

                quota_status = QuotaStatus(
                    quota_type=quota_type,
                    current_usage=current_usage,
                    limit=limit,
                    remaining=remaining,
                    reset_time=self._get_next_reset_time(),
                    is_exceeded=is_exceeded
                )

                logger.debug("Quota checked", extra={
                    "user_id": str(user_id),
                    "quota_type": quota_type.value,
                    "thread_id": str(thread_id) if thread_id else None,
                    "tier": tier.value,
                    "current_usage": current_usage,
                    "limit": limit,
                    "remaining": remaining,
                    "is_exceeded": is_exceeded
                })

                tracker.log_success(result_id=str(user_id))
                domain_logger.operation_success(
                    tracking_context,
                    result_id=str(user_id),
                    user_id=str(user_id),
                    quota_type=quota_type.value,
                    tier=tier.value,
                    current_usage=current_usage,
                    limit=limit,
                    is_exceeded=is_exceeded
                )
                domain_logger.business_event(
                    event="quota_checked",
                    context={
                        "user_id": str(user_id),
                        "quota_type": quota_type.value,
                        "tier": tier.value,
                        "usage_percentage": (current_usage / limit * 100) if limit > 0 else 0,
                        "is_exceeded": is_exceeded
                    }
                )

                return quota_status

            except Exception as e:
                error_id = tracker.log_error(e, context={
                    "user_id": str(user_id),
                    "quota_type": quota_type.value,
                    "thread_id": str(thread_id) if thread_id else None
                })
                domain_logger.operation_error(
                    tracking_context,
                    e,
                    user_id=str(user_id),
                    quota_type=quota_type.value,
                    error_id=error_id
                )
                logger.error(f"Failed to check quota (Error ID: {error_id})", extra={
                    "user_id": str(user_id),
                    "quota_type": quota_type.value,
                    "thread_id": str(thread_id) if thread_id else None,
                    "error": str(e),
                    "error_id": error_id
                })
                raise BadRequest(f"Failed to check quota status (Error ID: {error_id})")

    @trace_async
    async def increment_usage(
        self,
        user_id: UUID,
        quota_type: QuotaType,
        thread_id: UUID | None = None,
        amount: int = 1,
        uow: Any | None = None
    ) -> int:
        """Increment usage counter with atomic operations.
        
        Args:
            user_id: User ID
            quota_type: Type of quota to increment
            thread_id: Optional thread ID for thread-specific quotas
            amount: Amount to increment by (default: 1)
            uow: Optional Unit of Work to reuse existing DB connection
        """
        if amount <= 0:
            raise BadRequest("Increment amount must be positive")

        with RequestTracker(user_id=user_id, operation="increment_usage") as tracker:
            try:
                tracking_context = domain_logger.operation_start(
                    operation="increment_usage",
                    context={
                        "user_id": str(user_id),
                        "quota_type": quota_type.value,
                        "thread_id": str(thread_id) if thread_id else None,
                        "amount": amount
                    }
                )

                # Get user's subscription tier
                if self.subscription_service:
                    tier = await self.subscription_service.get_subscription_tier(user_id)
                elif uow:
                    # Use provided UoW to avoid creating new connection
                    repo = SubscriptionRepository(uow.session)
                    status = await repo.get_by_user_id(user_id)
                    tier = status.subscription_tier if status else SubscriptionTier.TRIAL
                else:
                    # Fallback to database lookup (creates new connection)
                    async with async_uow_factory(self.session_factory, user_id=str(user_id))() as temp_uow:
                        repo = SubscriptionRepository(temp_uow.session)
                        status = await repo.get_by_user_id(user_id)
                        tier = status.subscription_tier if status else SubscriptionTier.TRIAL

                # Get quota limits for this tier
                limits = await self.get_quota_limits(tier)
                limit = limits.get(quota_type, 0)

                # For unlimited quotas, just log and return
                if limit == -1:
                    logger.debug("Usage incremented for unlimited quota", extra={
                        "user_id": str(user_id),
                        "quota_type": quota_type.value,
                        "amount": amount
                    })
                    
                    tracker.log_success(result_id=str(user_id))
                    tracking_context = domain_logger.operation_start("increment_usage")

                    domain_logger.operation_success(tracking_context,
                        context={
                            "user_id": str(user_id),
                            "quota_type": quota_type.value,
                            "tier": tier.value,
                            "unlimited": True
                        }
                    )
                    
                    return 0

                # Generate Redis key for usage tracking
                redis_key = self._get_usage_key(user_id, quota_type, thread_id, tier)

                # Atomic increment operation
                new_usage = await self.redis_client.incr(redis_key, amount)

                # Set expiration if this is a new key
                if new_usage == amount:
                    # Set expiration to end of day
                    seconds_until_reset = self._get_seconds_until_reset()
                    await self.redis_client.expire(redis_key, seconds_until_reset)

                logger.info("Usage incremented", extra={
                    "user_id": str(user_id),
                    "quota_type": quota_type.value,
                    "thread_id": str(thread_id) if thread_id else None,
                    "tier": tier.value,
                    "amount": amount,
                    "new_usage": new_usage,
                    "limit": limit
                })

                tracker.log_success(result_id=str(user_id))
                domain_logger.operation_success(
                    tracking_context,
                    result_id=str(user_id),
                    user_id=str(user_id),
                    quota_type=quota_type.value,
                    tier=tier.value,
                    amount=amount,
                    new_usage=new_usage,
                    limit=limit
                )
                domain_logger.business_event(
                    event="quota_usage_incremented",
                    context={
                        "user_id": str(user_id),
                        "quota_type": quota_type.value,
                        "tier": tier.value,
                        "new_usage": new_usage,
                        "limit": limit,
                        "usage_percentage": (new_usage / limit * 100) if limit > 0 else 0
                    }
                )

                return new_usage

            except Exception as e:
                error_id = tracker.log_error(e, context={
                    "user_id": str(user_id),
                    "quota_type": quota_type.value,
                    "thread_id": str(thread_id) if thread_id else None,
                    "amount": amount
                })
                domain_logger.operation_error(
                    tracking_context,
                    e,
                    user_id=str(user_id),
                    quota_type=quota_type.value,
                    error_id=error_id
                )
                logger.error(f"Failed to increment usage (Error ID: {error_id})", extra={
                    "user_id": str(user_id),
                    "quota_type": quota_type.value,
                    "thread_id": str(thread_id) if thread_id else None,
                    "amount": amount,
                    "error": str(e),
                    "error_id": error_id
                })
                raise BadRequest(f"Failed to increment usage (Error ID: {error_id})")

    @trace_async
    async def get_remaining_quota(
        self,
        user_id: UUID,
        quota_type: QuotaType,
        thread_id: UUID | None = None
    ) -> int:
        """Get remaining quota for user feedback."""
        try:
            quota_status = await self.check_quota(user_id, quota_type, thread_id)
            return quota_status.remaining

        except Exception as e:
            logger.error("Failed to get remaining quota", extra={
                "user_id": str(user_id),
                "quota_type": quota_type.value,
                "thread_id": str(thread_id) if thread_id else None,
                "error": str(e)
            })
            # Return 0 for safety
            return 0

    @trace_async
    async def validate_quota_before_action(
        self,
        user_id: UUID,
        quota_type: QuotaType,
        thread_id: UUID | None = None,
        locale: str | None = None,
        uow: Any | None = None
    ) -> None:
        """Validate quota before performing an action, raise exception if exceeded.
        
        Args:
            user_id: User ID
            quota_type: Type of quota to validate
            thread_id: Optional thread ID
            locale: User locale for error messages
            uow: Optional Unit of Work to reuse existing DB connection
        """
        with RequestTracker(user_id=user_id, operation="validate_quota_before_action") as tracker:
            try:
                tracking_context = domain_logger.operation_start(
                    operation="validate_quota_before_action",
                    context={
                        "user_id": str(user_id),
                        "quota_type": quota_type.value,
                        "thread_id": str(thread_id) if thread_id else None
                    }
                )

                quota_status = await self.check_quota(user_id, quota_type, thread_id, uow)

                if quota_status.is_exceeded:
                    logger.warning("Quota exceeded", extra={
                        "user_id": str(user_id),
                        "quota_type": quota_type.value,
                        "thread_id": str(thread_id) if thread_id else None,
                        "current_usage": quota_status.current_usage,
                        "limit": quota_status.limit
                    })

                    error_id = tracker.log_error(
                        QuotaExceededError(
                            quota_type=quota_type.value,
                            current_usage=quota_status.current_usage,
                            limit=quota_status.limit,
                            reset_time=quota_status.reset_time,
                            thread_id=str(thread_id) if thread_id else None,
                            locale=locale or "pt-BR"
                        ),
                        context={
                            "user_id": str(user_id),
                            "quota_type": quota_type.value,
                            "current_usage": quota_status.current_usage,
                            "limit": quota_status.limit
                        }
                    )
                    domain_logger.operation_error(
                        tracking_context,
                        QuotaExceededError(
                            quota_type=quota_type.value,
                            current_usage=quota_status.current_usage,
                            limit=quota_status.limit,
                            reset_time=quota_status.reset_time,
                            thread_id=str(thread_id) if thread_id else None,
                            locale=locale or "pt-BR"
                        ),
                        user_id=str(user_id),
                        quota_type=quota_type.value,
                        error_id=error_id
                    )
                    domain_logger.business_event(
                        event="quota_exceeded",
                        context={
                            "user_id": str(user_id),
                            "quota_type": quota_type.value,
                            "current_usage": quota_status.current_usage,
                            "limit": quota_status.limit,
                            "thread_id": str(thread_id) if thread_id else None
                        }
                    )

                    raise QuotaExceededError(
                        quota_type=quota_type.value,
                        current_usage=quota_status.current_usage,
                        limit=quota_status.limit,
                        reset_time=quota_status.reset_time,
                        thread_id=str(thread_id) if thread_id else None,
                        locale=locale or "pt-BR"  # Default to Portuguese for Brazilian users
                    )

                tracker.log_success(result_id=str(user_id))
                domain_logger.operation_success(
                    tracking_context,
                    result_id=str(user_id),
                    user_id=str(user_id),
                    quota_type=quota_type.value,
                    current_usage=quota_status.current_usage,
                    limit=quota_status.limit,
                    remaining=quota_status.remaining
                )

            except QuotaExceededError:
                # Re-raise quota exceeded errors without wrapping
                raise
            except Exception as e:
                error_id = tracker.log_error(e, context={
                    "user_id": str(user_id),
                    "quota_type": quota_type.value,
                    "thread_id": str(thread_id) if thread_id else None
                })
                domain_logger.operation_error(
                    tracking_context,
                    e,
                    user_id=str(user_id),
                    quota_type=quota_type.value,
                    error_id=error_id
                )
                logger.error(f"Failed to validate quota (Error ID: {error_id})", extra={
                    "user_id": str(user_id),
                    "quota_type": quota_type.value,
                    "error": str(e),
                    "error_id": error_id
                })
                raise BadRequest(f"Failed to validate quota (Error ID: {error_id})")

    @trace_async
    async def get_quota_limits(self, subscription_tier: SubscriptionTier) -> dict[QuotaType, int]:
        """Get quota limits based on subscription tier."""
        limits = self.quota_limits.get(subscription_tier, {})

        logger.debug("Quota limits retrieved", extra={
            "subscription_tier": subscription_tier.value,
            "limits": {k.value: v for k, v in limits.items()}
        })

        return limits

    @trace_async
    async def get_quota_limit_for_type(
        self,
        subscription_tier: SubscriptionTier,
        quota_type: QuotaType
    ) -> int:
        """Get specific quota limit for a subscription tier and quota type."""
        limits = await self.get_quota_limits(subscription_tier)
        return limits.get(quota_type, 0)

    @trace_async
    async def is_quota_unlimited(
        self,
        subscription_tier: SubscriptionTier,
        quota_type: QuotaType
    ) -> bool:
        """Check if quota is unlimited for given tier and type."""
        limit = await self.get_quota_limit_for_type(subscription_tier, quota_type)
        return limit == -1

    @trace_async
    async def get_quota_configuration(self) -> dict[str, dict[str, int]]:
        """Get complete quota configuration for all tiers."""
        config = {}

        for tier in SubscriptionTier:
            limits = await self.get_quota_limits(tier)
            config[tier.value] = {quota_type.value: limit for quota_type, limit in limits.items()}

        logger.debug("Complete quota configuration retrieved", extra={
            "configuration": config
        })

        return config

    def validate_quota_configuration(self) -> bool:
        """Validate that quota configuration matches requirements."""
        try:
            # Validate trial user limits
            trial_limits = self.quota_limits.get(SubscriptionTier.TRIAL, {})

            # Trial users: 3 threads, 10 requests per thread per day
            if trial_limits.get(QuotaType.THREAD) != 3:
                logger.error("Invalid trial thread limit", extra={
                    "expected": 3,
                    "actual": trial_limits.get(QuotaType.THREAD)
                })
                return False

            if trial_limits.get(QuotaType.ICEBREAKER) != 10:
                logger.error("Invalid trial icebreaker limit", extra={
                    "expected": 10,
                    "actual": trial_limits.get(QuotaType.ICEBREAKER)
                })
                return False

            if trial_limits.get(QuotaType.SUGGESTION) != 10:
                logger.error("Invalid trial suggestion limit", extra={
                    "expected": 10,
                    "actual": trial_limits.get(QuotaType.SUGGESTION)
                })
                return False

            # Validate paid user limits
            paid_limits = self.quota_limits.get(SubscriptionTier.PAID, {})

            # Paid users: unlimited threads, 50 requests per day total
            if paid_limits.get(QuotaType.THREAD) != -1:
                logger.error("Invalid paid thread limit", extra={
                    "expected": -1,
                    "actual": paid_limits.get(QuotaType.THREAD)
                })
                return False

            if paid_limits.get(QuotaType.ICEBREAKER) != 50:
                logger.error("Invalid paid icebreaker limit", extra={
                    "expected": 50,
                    "actual": paid_limits.get(QuotaType.ICEBREAKER)
                })
                return False

            if paid_limits.get(QuotaType.SUGGESTION) != 50:
                logger.error("Invalid paid suggestion limit", extra={
                    "expected": 50,
                    "actual": paid_limits.get(QuotaType.SUGGESTION)
                })
                return False

            logger.info("Quota configuration validation passed")
            return True

        except Exception as e:
            logger.error("Quota configuration validation failed", extra={
                "error": str(e)
            })
            return False

    @trace_async
    async def reset_daily_quotas(self) -> int:
        """Reset daily quotas for all users (background task)."""
        with RequestTracker(operation="reset_daily_quotas") as tracker:
            try:
                tracking_context = domain_logger.operation_start(
                    operation="reset_daily_quotas",
                    context={}
                )

                reset_count = 0
                today = date.today().isoformat()
                yesterday = (date.today() - timedelta(days=1)).isoformat()

                # Pattern to match quota keys from yesterday
                pattern = f"quota:*:*:{yesterday}"

                logger.info("Starting daily quota reset", extra={
                    "date": today,
                    "cleanup_date": yesterday
                })

                # Use pipeline for batch operations
                client = await self.redis_client.get_client()
                pipe = client.pipeline()

                # Collect keys to delete
                keys_to_delete = []
                async for key in self.redis_client.scan_iter(match=pattern):
                    keys_to_delete.append(key)

                # Delete keys in batches
                batch_size = 100
                for i in range(0, len(keys_to_delete), batch_size):
                    batch = keys_to_delete[i:i + batch_size]
                    if batch:
                        pipe.delete(*batch)
                        await pipe.execute()
                        reset_count += len(batch)
                        pipe.reset()

                logger.info("Daily quota reset completed", extra={
                    "reset_count": reset_count,
                    "date": today
                })

                tracker.log_success(result_id=str(reset_count))
                domain_logger.operation_success(
                    tracking_context,
                    result_id=str(reset_count),
                    reset_count=reset_count,
                    date=today,
                    cleanup_date=yesterday
                )
                domain_logger.business_event(
                    event="daily_quotas_reset",
                    context={
                        "reset_count": reset_count,
                        "date": today
                    }
                )

                return reset_count

            except Exception as e:
                error_id = tracker.log_error(e, context={})
                domain_logger.operation_error(
                    tracking_context,
                    e,
                    error_id=error_id
                )
                logger.error(f"Failed to reset daily quotas (Error ID: {error_id})", extra={
                    "error": str(e),
                    "error_id": error_id
                })
                raise BadRequest(f"Failed to reset daily quotas (Error ID: {error_id})")

    @trace_async
    async def cleanup_expired_quota_data(self, days_to_keep: int = 7) -> int:
        """Clean up quota data older than specified days."""
        try:
            cleanup_count = 0
            cutoff_date = date.today() - timedelta(days=days_to_keep)

            logger.info("Starting quota data cleanup", extra={
                "cutoff_date": cutoff_date.isoformat(),
                "days_to_keep": days_to_keep
            })

            # Use pipeline for batch operations
            client = await self.redis_client.get_client()
            pipe = client.pipeline()

            # Collect all keys to delete
            keys_to_delete = []

            # Generate patterns for dates older than cutoff
            for i in range(days_to_keep + 1, days_to_keep + 30):  # Clean up to 30 days back
                old_date = (date.today() - timedelta(days=i)).isoformat()
                pattern = f"quota:*:*:{old_date}"

                async for key in self.redis_client.scan_iter(match=pattern):
                    keys_to_delete.append(key)

            # Delete keys in batches
            batch_size = 100
            for i in range(0, len(keys_to_delete), batch_size):
                batch = keys_to_delete[i:i + batch_size]
                if batch:
                    pipe.delete(*batch)
                    await pipe.execute()
                    cleanup_count += len(batch)
                    pipe.reset()

            logger.info("Quota data cleanup completed", extra={
                "cleanup_count": cleanup_count,
                "cutoff_date": cutoff_date.isoformat()
            })

            return cleanup_count

        except Exception as e:
            logger.error("Failed to cleanup expired quota data", extra={
                "error": str(e)
            })
            raise BadRequest("Failed to cleanup expired quota data")

    @trace_async
    async def reset_user_quota(
        self,
        user_id: UUID,
        quota_type: QuotaType,
        thread_id: UUID | None = None
    ) -> None:
        """Reset quota for a specific user and quota type."""
        with RequestTracker(user_id=user_id, operation="reset_user_quota") as tracker:
            try:
                tracking_context = domain_logger.operation_start(
                    operation="reset_user_quota",
                    context={
                        "user_id": str(user_id),
                        "quota_type": quota_type.value,
                        "thread_id": str(thread_id) if thread_id else None
                    }
                )

                # Get user's subscription tier
                if self.subscription_service:
                    tier = await self.subscription_service.get_subscription_tier(user_id)
                else:
                    # Fallback to database lookup
                    async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                        repo = SubscriptionRepository(uow.session)
                        status = await repo.get_by_user_id(user_id)
                        tier = status.subscription_tier if status else SubscriptionTier.TRIAL

                # Generate Redis key and delete it
                redis_key = self._get_usage_key(user_id, quota_type, thread_id, tier)
                await self.redis_client.delete(redis_key)

                logger.info("User quota reset", extra={
                    "user_id": str(user_id),
                    "quota_type": quota_type.value,
                    "thread_id": str(thread_id) if thread_id else None,
                    "tier": tier.value
                })

                tracker.log_success(result_id=str(user_id))
                domain_logger.operation_success(
                    tracking_context,
                    result_id=str(user_id),
                    user_id=str(user_id),
                    quota_type=quota_type.value,
                    tier=tier.value,
                    thread_id=str(thread_id) if thread_id else None
                )
                domain_logger.business_event(
                    event="user_quota_reset",
                    context={
                        "user_id": str(user_id),
                        "quota_type": quota_type.value,
                        "tier": tier.value
                    }
                )

            except Exception as e:
                error_id = tracker.log_error(e, context={
                    "user_id": str(user_id),
                    "quota_type": quota_type.value,
                    "thread_id": str(thread_id) if thread_id else None
                })
                domain_logger.operation_error(
                    tracking_context,
                    e,
                    user_id=str(user_id),
                    quota_type=quota_type.value,
                    error_id=error_id
                )
                logger.error(f"Failed to reset user quota (Error ID: {error_id})", extra={
                    "user_id": str(user_id),
                    "quota_type": quota_type.value,
                    "thread_id": str(thread_id) if thread_id else None,
                    "error": str(e),
                    "error_id": error_id
                })
                raise BadRequest(f"Failed to reset user quota (Error ID: {error_id})")

    @trace_async
    async def get_quota_usage_stats(self) -> dict[str, any]:
        """Get quota usage statistics across all users."""
        try:
            stats = {
                "total_quota_keys": 0,
                "usage_by_type": {},
                "usage_by_tier": {},
                "generated_at": utcnow().isoformat()
            }

            today = date.today().isoformat()
            pattern = f"quota:*:*:{today}"

            # Scan all quota keys for today
            async for key in self.redis_client.scan_iter(match=pattern):
                try:
                    stats["total_quota_keys"] += 1

                    # Parse key to extract quota type and tier info
                    # Key format: quota:{user_id}:{quota_type}:{thread_id_or_total}:{date}
                    key_parts = key.split(":")
                    if len(key_parts) >= 3:
                        quota_type = key_parts[2]

                        # Get usage value
                        usage_str = await self.redis_client.get(key)
                        usage = int(usage_str) if usage_str else 0

                        # Aggregate by quota type
                        if quota_type not in stats["usage_by_type"]:
                            stats["usage_by_type"][quota_type] = {
                                "total_usage": 0,
                                "key_count": 0
                            }

                        stats["usage_by_type"][quota_type]["total_usage"] += usage
                        stats["usage_by_type"][quota_type]["key_count"] += 1

                except Exception as e:
                    logger.warning("Failed to process quota key for stats", extra={
                        "key": key,
                        "error": str(e)
                    })

            logger.info("Quota usage stats generated", extra={
                "total_keys": stats["total_quota_keys"]
            })

            return stats

        except Exception as e:
            logger.error("Failed to get quota usage stats", extra={
                "error": str(e)
            })
            raise BadRequest("Failed to get quota usage statistics")

    @trace_async
    async def get_user_quota_summary(self, user_id: UUID) -> dict[str, any]:
        """Get comprehensive quota summary for user."""
        try:
            # Get user's subscription tier
            if self.subscription_service:
                tier = await self.subscription_service.get_subscription_tier(user_id)
            else:
                # Fallback to database lookup
                async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                    repo = SubscriptionRepository(uow.session)
                    status = await repo.get_by_user_id(user_id)
                    tier = status.subscription_tier if status else SubscriptionTier.TRIAL

            # Get quota status for each quota type
            quota_summary = {
                "user_id": str(user_id),
                "subscription_tier": tier.value,
                "quotas": {},
                "reset_time": self._get_next_reset_time().isoformat()
            }

            for quota_type in QuotaType:
                quota_status = await self.check_quota(user_id, quota_type)
                quota_summary["quotas"][quota_type.value] = {
                    "current_usage": quota_status.current_usage,
                    "limit": quota_status.limit,
                    "remaining": quota_status.remaining,
                    "is_exceeded": quota_status.is_exceeded
                }

            logger.debug("Quota summary generated", extra={
                "user_id": str(user_id),
                "tier": tier.value
            })

            return quota_summary

        except Exception as e:
            logger.error("Failed to get quota summary", extra={
                "user_id": str(user_id), "error": str(e)
            })
            raise BadRequest("Failed to get quota summary")

    @trace_async
    async def bulk_increment_usage(
        self,
        operations: list[dict[str, any]]
    ) -> list[int]:
        """Bulk increment usage for multiple users/quota types atomically."""
        try:
            results = []
            client = await self.redis_client.get_client()
            pipe = client.pipeline()

            # Prepare all operations
            operation_keys = []
            for op in operations:
                user_id = op["user_id"]
                quota_type = QuotaType(op["quota_type"])
                thread_id = op.get("thread_id")
                amount = op.get("amount", 1)

                # Get user's subscription tier
                if self.subscription_service:
                    tier = await self.subscription_service.get_subscription_tier(user_id)
                else:
                    tier = SubscriptionTier.TRIAL  # Default fallback

                # Generate Redis key
                redis_key = self._get_usage_key(user_id, quota_type, thread_id, tier)
                operation_keys.append((redis_key, amount))

                # Add increment operation to pipeline
                pipe.incr(redis_key, amount)

            # Execute all operations atomically
            pipe_results = await pipe.execute()

            # Set expiration for new keys and collect results
            for i, ((redis_key, amount), new_usage) in enumerate(zip(operation_keys, pipe_results)):
                if new_usage == amount:  # New key created
                    seconds_until_reset = self._get_seconds_until_reset()
                    await self.redis_client.expire(redis_key, seconds_until_reset)

                results.append(new_usage)

            logger.info("Bulk usage increment completed", extra={
                "operations_count": len(operations),
                "total_increments": sum(op.get("amount", 1) for op in operations)
            })

            return results

        except Exception as e:
            logger.error("Failed to bulk increment usage", extra={
                "operations_count": len(operations), "error": str(e)
            })
            raise BadRequest("Failed to bulk increment usage")

    @trace_async
    async def get_quota_cache_stats(self) -> dict[str, any]:
        """Get quota cache statistics and health metrics."""
        try:
            stats = {
                "total_quota_keys": 0,
                "keys_by_date": {},
                "keys_by_type": {},
                "memory_usage": 0,
                "cache_hit_estimation": 0,
                "generated_at": utcnow().isoformat()
            }

            # Scan all quota keys
            pattern = "quota:*"
            async for key in self.redis_client.scan_iter(match=pattern):
                stats["total_quota_keys"] += 1

                # Parse key to extract information
                # Key format: quota:{user_id}:{quota_type}:{thread_id_or_total}:{date}
                key_parts = key.split(":")
                if len(key_parts) >= 5:
                    quota_type = key_parts[2]
                    date_part = key_parts[4]

                    # Count by type
                    if quota_type not in stats["keys_by_type"]:
                        stats["keys_by_type"][quota_type] = 0
                    stats["keys_by_type"][quota_type] += 1

                    # Count by date
                    if date_part not in stats["keys_by_date"]:
                        stats["keys_by_date"][date_part] = 0
                    stats["keys_by_date"][date_part] += 1

            # Get Redis memory info if available
            try:
                client = await self.redis_client.get_client()
                info = await client.info("memory")
                stats["memory_usage"] = info.get("used_memory", 0)
            except Exception as e:
                logger.warning("Failed to get Redis memory info", extra={"error": str(e)})

            logger.debug("Quota cache stats generated", extra={
                "total_keys": stats["total_quota_keys"]
            })

            return stats

        except Exception as e:
            logger.error("Failed to get quota cache stats", extra={
                "error": str(e)
            })
            raise BadRequest("Failed to get quota cache statistics")

    @trace_async
    async def optimize_quota_cache(self) -> dict[str, int]:
        """Optimize quota cache by removing unnecessary keys and compacting data."""
        try:
            optimization_stats = {
                "expired_keys_removed": 0,
                "zero_usage_keys_removed": 0,
                "total_keys_processed": 0
            }

            client = await self.redis_client.get_client()
            pipe = client.pipeline()

            # Scan all quota keys
            pattern = "quota:*"
            keys_to_remove = []

            async for key in self.redis_client.scan_iter(match=pattern):
                optimization_stats["total_keys_processed"] += 1

                try:
                    # Check TTL
                    ttl = await self.redis_client.ttl(key)
                    if ttl == -1:  # No expiration set
                        # Set expiration based on key date
                        key_parts = key.split(":")
                        if len(key_parts) >= 5:
                            key_date = key_parts[4]
                            try:
                                key_date_obj = date.fromisoformat(key_date)
                                if key_date_obj < date.today():
                                    # Old key, mark for removal
                                    keys_to_remove.append(key)
                                    continue
                                else:
                                    # Set proper expiration
                                    seconds_until_reset = self._get_seconds_until_reset()
                                    await self.redis_client.expire(key, seconds_until_reset)
                            except ValueError:
                                # Invalid date format, mark for removal
                                keys_to_remove.append(key)
                                continue

                    # Check for zero usage keys (optional cleanup)
                    usage_str = await self.redis_client.get(key)
                    if usage_str == "0":
                        keys_to_remove.append(key)
                        optimization_stats["zero_usage_keys_removed"] += 1

                except Exception as e:
                    logger.warning("Failed to process quota key during optimization", extra={
                        "key": key, "error": str(e)
                    })

            # Remove identified keys in batches
            batch_size = 100
            for i in range(0, len(keys_to_remove), batch_size):
                batch = keys_to_remove[i:i + batch_size]
                if batch:
                    pipe.delete(*batch)
                    await pipe.execute()
                    pipe.reset()

            optimization_stats["expired_keys_removed"] = len(keys_to_remove) - optimization_stats["zero_usage_keys_removed"]

            logger.info("Quota cache optimization completed", extra=optimization_stats)

            return optimization_stats

        except Exception as e:
            logger.error("Failed to optimize quota cache", extra={
                "error": str(e)
            })
            raise BadRequest("Failed to optimize quota cache")

    # Private helper methods

    async def _get_current_usage(
        self,
        user_id: UUID,
        quota_type: QuotaType,
        thread_id: UUID | None,
        tier: SubscriptionTier
    ) -> int:
        """Get current usage from Redis."""
        redis_key = self._get_usage_key(user_id, quota_type, thread_id, tier)

        try:
            usage_str = await self.redis_client.get(redis_key)
            return int(usage_str) if usage_str else 0
        except (ValueError, TypeError):
            logger.warning("Invalid usage value in Redis", extra={
                "redis_key": redis_key,
                "value": usage_str
            })
            return 0

    def _get_usage_key(
        self,
        user_id: UUID,
        quota_type: QuotaType,
        thread_id: UUID | None,
        tier: SubscriptionTier
    ) -> str:
        """Generate Redis key for usage tracking."""
        today = date.today().isoformat()

        # For trial users, track per-thread usage for icebreaker/suggestion
        if tier == SubscriptionTier.TRIAL and quota_type in [QuotaType.ICEBREAKER, QuotaType.SUGGESTION]:
            if thread_id:
                return f"quota:{user_id}:{quota_type.value}:{thread_id}:{today}"
            else:
                # Fallback to user-level tracking if no thread_id provided
                return f"quota:{user_id}:{quota_type.value}:total:{today}"

        # For paid users or thread quotas, track at user level
        return f"quota:{user_id}:{quota_type.value}:total:{today}"

    def _get_next_reset_time(self) -> datetime:
        """Get the next quota reset time (midnight UTC)."""
        now = utcnow()
        tomorrow = now.date() + timedelta(days=1)
        return datetime.combine(tomorrow, datetime.min.time()).replace(tzinfo=now.tzinfo)

    def _get_seconds_until_reset(self) -> int:
        """Get seconds until next quota reset."""
        now = utcnow()
        reset_time = self._get_next_reset_time()
        return int((reset_time - now).total_seconds())


def create_quota_service(
    session_factory: async_sessionmaker[AsyncSession],
    subscription_service: SubscriptionService | None = None
) -> QuotaService:
    """Factory function for QuotaService."""
    return QuotaService(session_factory, subscription_service)
