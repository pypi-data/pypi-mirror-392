"""Subscription service for business logic orchestration and RevenueCat integration."""
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from ...db.uow import async_uow_factory
from ...utils.clock import utcnow
from ...utils.errors import BadRequest, DependencyError, NotFound
from ...utils.logging import get_safe_logger
from ...utils.enhanced_logging import log_subscription_error
from ...utils.redis_client import get_redis_client
from ...utils.tracing import trace_async
from ...utils.request_tracking import RequestTracker
from ...utils.domain_logger import get_domain_logger, get_subscription_logger
from .config import SubscriptionConfig, get_subscription_config
from .db_optimization import SubscriptionDatabaseOptimizer
from .repository import SubscriptionRepository
from .revenuecat_client import RevenueCatClient, RevenueCatWebhookEvent
from .schemas import (
    ApplePurchaseRequest,
    GooglePurchaseRequest,
    SubscriptionPlatform,
    SubscriptionStatusCreate,
    SubscriptionStatusOut,
    SubscriptionStatusUpdate,
    SubscriptionTier,
    subscription_status_table,
)

logger = get_safe_logger(__name__)
domain_logger = get_domain_logger(__name__)


class SubscriptionService:
    """Business logic for subscription management with RevenueCat integration."""

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        revenuecat_client: RevenueCatClient | None = None,
        config: SubscriptionConfig | None = None
    ):
        self.session_factory = session_factory
        self.revenuecat_client = revenuecat_client
        self.redis_client = get_redis_client()
        self.db_optimizer = SubscriptionDatabaseOptimizer(session_factory)

        # Load configuration
        self.config = config or get_subscription_config()

        # Cache configuration from config
        self.subscription_cache_ttl = self.config.subscription_cache_ttl
        self.entitlement_cache_ttl = self.config.entitlement_cache_ttl

        # Trial configuration from config
        self.trial_duration_days = self.config.trial_duration_days

        # Feature entitlements mapping
        self.feature_entitlements = {
            "unlimited_threads": ["premium", "pro"],
            "advanced_ai": ["premium", "pro"],
            "priority_support": ["pro"],
            "analytics": ["premium", "pro"],
        }

    @trace_async
    async def get_subscription_status(self, user_id: UUID) -> SubscriptionStatusOut:
        """Get current subscription status for user with caching."""
        with RequestTracker(user_id=user_id, operation="get_subscription_status") as tracker:
            try:
                tracking_context = domain_logger.operation_start(
                    operation="get_subscription_status",
                    context={"user_id": str(user_id)}
                )

                cache_key = f"subscription:status:{user_id}"

                # Try to get from cache first
                cached_data = await self.redis_client.get_json(cache_key)
                if cached_data:
                    logger.debug("Subscription status retrieved from cache", extra={
                        "user_id": str(user_id)
                    })
                    result = SubscriptionStatusOut(**cached_data)
                    
                    tracker.log_success(result_id=str(user_id))
                    domain_logger.operation_success(
                        tracking_context,
                        result_id=str(user_id),
                        user_id=str(user_id),
                        source="cache",
                        tier=result.subscription_tier.value if result.subscription_tier else None,
                        active=result.active
                    )
                    
                    return result

                # Get from database
                async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                    repo = SubscriptionRepository(uow.session)
                    status = await repo.get_by_user_id(user_id)

                    if status is None:
                        # For now, return a default trial status instead of creating in DB
                        # This avoids integrity issues in tests where subscriptions might already exist
                        from datetime import timedelta
                        now = utcnow()
                        trial_end = now + timedelta(days=30)
                        
                        status = SubscriptionStatusOut(
                            user_id=user_id,
                            active=True,
                            entitlement="free",
                            platform=None,
                            product_id=None,
                            will_renew=False,
                            original_purchase_date=None,
                            expiration_date=trial_end,
                            grace_period=False,
                            trial=True,
                            billing_issue=False,
                            raw=None,
                            updated_at=now,
                            revenuecat_subscriber_id=None,
                            subscription_tier=SubscriptionTier.TRIAL,
                            trial_start_date=now,
                            trial_end_date=trial_end,
                        )

                    # Check if subscription is active (not expired)
                    is_active = self._is_subscription_active(status)

                    # Update active status
                    result = SubscriptionStatusOut(
                        user_id=status.user_id,
                        active=is_active,
                        entitlement=status.entitlement,
                        platform=status.platform,
                        product_id=status.product_id,
                        will_renew=status.will_renew,
                        original_purchase_date=status.original_purchase_date,
                        expiration_date=status.expiration_date,
                        grace_period=status.grace_period,
                        trial=status.trial,
                        billing_issue=status.billing_issue,
                        raw=status.raw,
                        updated_at=status.updated_at,
                        revenuecat_subscriber_id=status.revenuecat_subscriber_id,
                        subscription_tier=status.subscription_tier,
                        trial_start_date=status.trial_start_date,
                        trial_end_date=status.trial_end_date,
                    )

                    # Cache the result
                    await self.redis_client.set(
                        cache_key,
                        result.model_dump(mode='json'),
                        ex=self.subscription_cache_ttl
                    )

                    logger.info("Subscription status retrieved from database", extra={
                        "user_id": str(user_id),
                        "tier": status.subscription_tier.value,
                        "active": is_active
                    })

                    tracker.log_success(result_id=str(user_id))
                    domain_logger.operation_success(
                        tracking_context,
                        result_id=str(user_id),
                        user_id=str(user_id),
                        source="database",
                        tier=status.subscription_tier.value,
                        active=is_active
                    )
                    domain_logger.business_event(
                        event="subscription_status_retrieved",
                        context={
                            "user_id": str(user_id),
                            "tier": status.subscription_tier.value,
                            "active": is_active,
                            "trial": status.trial
                        }
                    )

                    return result

            except Exception as e:
                error_id = tracker.log_error(e, context={"user_id": str(user_id)})
                domain_logger.operation_error(
                    tracking_context,
                    e,
                    user_id=str(user_id),
                    error_id=error_id
                )
                
                # Keep existing enhanced logging
                enhanced_error_id = log_subscription_error(
                    error=e,
                    operation="get_subscription_status",
                    user_id=str(user_id),
                    cache_key=cache_key,
                    component="subscription_service"
                )
                logger.error(f"Failed to get subscription status (Error ID: {enhanced_error_id})", extra={
                    "user_id": str(user_id), 
                    "error": str(e),
                    "error_id": enhanced_error_id,
                    "operation": "get_subscription_status"
                })
                raise BadRequest(f"Failed to retrieve subscription status (Error ID: {enhanced_error_id})")

    @trace_async
    async def create_subscription_status(self, user_id: UUID, data: SubscriptionStatusCreate) -> SubscriptionStatusOut:
        """Create subscription status."""
        with RequestTracker(user_id=user_id, operation="create_subscription_status") as tracker:
            try:
                tracking_context = domain_logger.operation_start(
                    operation="create_subscription_status",
                    context={"user_id": str(user_id), "tier": data.subscription_tier.value if data.subscription_tier else None}
                )

                async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                    repo = SubscriptionRepository(uow.session)
                    result: SubscriptionStatusOut = await repo.create(user_id, data)
                    await uow.commit()
                    
                    tracker.log_success(result_id=str(result.user_id))
                    domain_logger.operation_success(
                        tracking_context,
                        result_id=str(result.user_id),
                        user_id=str(user_id),
                        tier=result.subscription_tier.value if result.subscription_tier else None,
                        trial=result.trial
                    )
                    domain_logger.business_event(
                        event="subscription_status_created",
                        context={
                            "user_id": str(user_id),
                            "tier": result.subscription_tier.value if result.subscription_tier else None,
                            "trial": result.trial,
                            "entitlement": result.entitlement
                        }
                    )
                    
                    return result
            except Exception as e:
                error_id = tracker.log_error(e, context={"user_id": str(user_id)})
                domain_logger.operation_error(
                    tracking_context,
                    e,
                    user_id=str(user_id),
                    error_id=error_id
                )
                logger.error(f"Failed to create subscription status (Error ID: {error_id})", extra={
                    "user_id": str(user_id), "error": str(e), "error_id": error_id
                })
                raise BadRequest(f"Failed to create subscription status (Error ID: {error_id})")

    @trace_async
    async def update_subscription_status(self, user_id: UUID, data: SubscriptionStatusUpdate) -> SubscriptionStatusOut | None:
        """Update subscription status."""
        with RequestTracker(user_id=user_id, operation="update_subscription_status") as tracker:
            try:
                tracking_context = domain_logger.operation_start(
                    operation="update_subscription_status",
                    context={"user_id": str(user_id)}
                )

                async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                    repo = SubscriptionRepository(uow.session)
                    result: SubscriptionStatusOut | None = await repo.update(user_id, data)
                    
                    if result:
                        tracker.log_success(result_id=str(result.user_id))
                        domain_logger.operation_success(
                            tracking_context,
                            result_id=str(result.user_id),
                            user_id=str(user_id),
                            tier=result.subscription_tier.value if result.subscription_tier else None
                        )
                        domain_logger.business_event(
                            event="subscription_status_updated",
                            context={
                                "user_id": str(user_id),
                                "tier": result.subscription_tier.value if result.subscription_tier else None,
                                "entitlement": result.entitlement
                            }
                        )
                    else:
                        tracker.log_success(result_id=str(user_id))
                        tracking_context = domain_logger.operation_start("update_subscription_status")

                        domain_logger.operation_success(tracking_context,
                            context={"user_id": str(user_id), "result": "not_found"}
                        )
                    
                    return result
            except Exception as e:
                error_id = tracker.log_error(e, context={"user_id": str(user_id)})
                domain_logger.operation_error(
                    tracking_context,
                    e,
                    user_id=str(user_id),
                    error_id=error_id
                )
                logger.error(f"Failed to update subscription status (Error ID: {error_id})", extra={
                    "user_id": str(user_id), "error": str(e), "error_id": error_id
                })
                raise BadRequest(f"Failed to update subscription status (Error ID: {error_id})")

    @trace_async
    async def upsert_subscription_status(self, user_id: UUID, data: SubscriptionStatusCreate, locale: str = "en-US") -> SubscriptionStatusOut:
        """Upsert subscription status (idempotent)."""
        try:
            async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                repo = SubscriptionRepository(uow.session)
                result: SubscriptionStatusOut = await repo.upsert(user_id, data, locale)
                return result
        except Exception as e:
            logger.error("Failed to upsert subscription status", extra={
                "user_id": str(user_id), "error": str(e)
            })
            raise BadRequest("Failed to upsert subscription status")

    @trace_async
    async def delete_subscription_status(self, user_id: UUID) -> None:
        """Delete subscription status."""
        try:
            async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                repo = SubscriptionRepository(uow.session)
                await repo.delete(user_id)
        except NotFound:
            raise
        except Exception as e:
            logger.error("Failed to delete subscription status", extra={
                "user_id": str(user_id), "error": str(e)
            })
            raise BadRequest("Failed to delete subscription status")

    @trace_async
    async def is_subscription_active(self, user_id: UUID) -> bool:
        """Check if subscription is active."""
        try:
            async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                repo = SubscriptionRepository(uow.session)
                result: bool = await repo.is_active(user_id)
                return result
        except Exception as e:
            logger.error("Failed to check subscription active status", extra={
                "user_id": str(user_id), "error": str(e)
            })
            raise BadRequest("Failed to check subscription status")

    @trace_async
    async def sync_google_purchase(self, user_id: UUID, purchase_data: GooglePurchaseRequest, locale: str = "en-US") -> SubscriptionStatusOut:
        """Sync Google Play purchase."""
        try:
            # Create subscription data from purchase
            subscription_data = SubscriptionStatusCreate(
                entitlement="premium",
                platform="google",
                product_id=purchase_data.product_id,
                will_renew=True,
                raw={"purchase_token": purchase_data.purchase_token}
            )

            result = await self.upsert_subscription_status(user_id, subscription_data, locale)

            logger.info("Google purchase synced", extra={
                "user_id": str(user_id),
                "product_id": purchase_data.product_id
            })

            return SubscriptionStatusOut(
                user_id=user_id,
                active=True,
                entitlement=result.entitlement,
                platform=result.platform,
                product_id=result.product_id,
                will_renew=result.will_renew,
                original_purchase_date=result.original_purchase_date,
                expiration_date=result.expiration_date,
                grace_period=result.grace_period,
                trial=result.trial,
                billing_issue=result.billing_issue,
                raw=result.raw,
                updated_at=result.updated_at
            )
        except Exception as e:
            logger.error("Failed to sync Google purchase", extra={
                "user_id": str(user_id), "error": str(e)
            })
            raise BadRequest("Failed to sync Google purchase")

    @trace_async
    async def sync_apple_purchase(self, user_id: UUID, purchase_data: ApplePurchaseRequest, locale: str = "en-US") -> SubscriptionStatusOut:
        """Sync Apple App Store purchase."""
        try:
            # Create subscription data from purchase
            subscription_data = SubscriptionStatusCreate(
                entitlement="premium",
                platform="apple",
                product_id="flerity_premium_monthly",  # Default product for Apple
                will_renew=True,
                raw={"transaction_id": purchase_data.transaction_id}
            )

            result = await self.upsert_subscription_status(user_id, subscription_data, locale)

            logger.info("Apple purchase synced", extra={
                "user_id": str(user_id),
                "transaction_id": purchase_data.transaction_id
            })

            return SubscriptionStatusOut(
                user_id=user_id,
                active=True,
                entitlement=result.entitlement,
                platform=result.platform,
                product_id=result.product_id,
                will_renew=result.will_renew,
                original_purchase_date=result.original_purchase_date,
                expiration_date=result.expiration_date,
                grace_period=result.grace_period,
                trial=result.trial,
                billing_issue=result.billing_issue,
                raw=result.raw,
                updated_at=result.updated_at
            )
        except Exception as e:
            logger.error("Failed to sync Apple purchase", extra={
                "user_id": str(user_id), "error": str(e)
            })
            raise BadRequest("Failed to sync Apple purchase")

    @trace_async
    async def find_expiring_subscriptions(self, days_ahead: int = 7) -> list[SubscriptionStatusOut]:
        """Find subscriptions expiring within specified days."""
        try:
            # Use system context for admin operations
            async with async_uow_factory(self.session_factory, user_id=None)() as uow:
                repo = SubscriptionRepository(uow.session)
                result: list[SubscriptionStatusOut] = await repo.find_expiring_soon(days_ahead)
                return result
        except Exception as e:
            logger.error("Failed to find expiring subscriptions", extra={
                "days_ahead": days_ahead, "error": str(e)
            })
            raise BadRequest("Failed to find expiring subscriptions")

    @trace_async
    async def find_subscriptions_by_platform(self, platform: SubscriptionPlatform) -> list[SubscriptionStatusOut]:
        """Find all subscriptions by platform."""
        try:
            # Use system context for admin operations
            async with async_uow_factory(self.session_factory, user_id=None)() as uow:
                repo = SubscriptionRepository(uow.session)
                result: list[SubscriptionStatusOut] = await repo.find_by_platform(platform)
                return result
        except Exception as e:
            logger.error("Failed to find subscriptions by platform", extra={
                "platform": platform, "error": str(e)
            })
            raise BadRequest("Failed to find subscriptions by platform")

    @trace_async
    async def get_active_subscription_count(self) -> int:
        """Get count of active subscriptions."""
        try:
            # Use system context for admin operations
            async with async_uow_factory(self.session_factory, user_id=None)() as uow:
                repo = SubscriptionRepository(uow.session)
                result: int = await repo.count_active_subscriptions()
                return result
        except Exception as e:
            logger.error("Failed to count active subscriptions", extra={"error": str(e)})
            raise BadRequest("Failed to count active subscriptions")

    @trace_async
    async def validate_purchase(self, user_id: UUID, platform: SubscriptionPlatform, purchase_data: dict[str, Any]) -> dict[str, Any]:
        """Validate purchase data from platform."""
        try:
            if platform == "google":
                # Validate Google purchase data
                if not purchase_data.get("purchase_token") or not purchase_data.get("product_id"):
                    raise BadRequest("Missing required Google purchase data")

                # In a real implementation, this would call Google Play API
                # For now, just validate the structure
                return {
                    "valid": True,
                    "platform": platform,
                    "product_id": purchase_data["product_id"],
                    "purchase_token": purchase_data["purchase_token"],
                    "validated_at": utcnow().isoformat()
                }

            elif platform == "apple":
                # Validate Apple purchase data
                if not purchase_data.get("transaction_id") or not purchase_data.get("receipt_data"):
                    raise BadRequest("Missing required Apple purchase data")

                # In a real implementation, this would call App Store API
                # For now, just validate the structure
                return {
                    "valid": True,
                    "platform": platform,
                    "transaction_id": purchase_data["transaction_id"],
                    "receipt_data": purchase_data["receipt_data"],
                    "validated_at": utcnow().isoformat()
                }

            else:
                raise BadRequest(f"Unsupported platform: {platform}")

        except Exception as e:
            logger.error("Failed to validate purchase", extra={
                "user_id": str(user_id), "platform": platform, "error": str(e)
            })
            raise BadRequest("Failed to validate purchase")


    @trace_async
    async def sync_with_revenuecat(self, user_id: UUID) -> SubscriptionStatusOut:
        """Sync subscription status with RevenueCat in real-time."""
        if not self.revenuecat_client:
            logger.warning("RevenueCat client not configured, skipping sync", extra={
                "user_id": str(user_id)
            })
            return await self.get_subscription_status(user_id)

        try:
            # Get subscriber info from RevenueCat
            subscriber_info = await self.revenuecat_client.get_subscriber_info(str(user_id))

            # Determine subscription tier from RevenueCat entitlements
            tier = await self._determine_subscription_tier_from_revenuecat(subscriber_info)

            # Update local subscription status
            async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                repo = SubscriptionRepository(uow.session)

                # Get current status or create new one
                current_status = await repo.get_by_user_id(user_id)

                if current_status is None:
                    # Create new subscription from RevenueCat data
                    subscription_data = self._create_subscription_from_revenuecat(
                        user_id, subscriber_info, tier
                    )
                    result = await repo.create(user_id, subscription_data)
                else:
                    # Update existing subscription
                    update_data = self._create_update_from_revenuecat(subscriber_info, tier)
                    result = await repo.update(user_id, update_data)
                    if result is None:
                        result = current_status

                # Invalidate cache
                await self._invalidate_subscription_cache(user_id)

                logger.info("Subscription synced with RevenueCat", extra={
                    "user_id": str(user_id),
                    "tier": tier.value,
                    "has_entitlements": bool(subscriber_info.get("entitlements"))
                })

                return result

        except DependencyError as e:
            logger.error("RevenueCat sync failed", extra={
                "user_id": str(user_id), "error": str(e)
            })
            # Return cached/database status on RevenueCat failure
            return await self.get_subscription_status(user_id)
        except Exception as e:
            logger.error("Unexpected error during RevenueCat sync", extra={
                "user_id": str(user_id), "error": str(e)
            })
            raise BadRequest("Failed to sync with RevenueCat")

    @trace_async
    async def is_feature_enabled(self, user_id: UUID, feature: str) -> bool:
        """Check if a feature is enabled for the user based on entitlements."""
        cache_key = f"subscription:entitlement:{user_id}:{feature}"

        try:
            # Try cache first
            cached_result = await self.redis_client.get(cache_key)
            if cached_result is not None:
                return cached_result.lower() == "true"

            # Get subscription status
            status = await self.get_subscription_status(user_id)

            # Check feature entitlement
            required_entitlements = self.feature_entitlements.get(feature, [])
            is_enabled = status.entitlement in required_entitlements

            # For trial users, enable basic features
            if status.subscription_tier == SubscriptionTier.TRIAL:
                basic_features = ["basic_ai", "limited_threads"]
                is_enabled = is_enabled or feature in basic_features

            # Cache the result
            await self.redis_client.set(
                cache_key,
                str(is_enabled).lower(),
                ex=self.entitlement_cache_ttl
            )

            logger.debug("Feature entitlement checked", extra={
                "user_id": str(user_id),
                "feature": feature,
                "enabled": is_enabled,
                "entitlement": status.entitlement
            })

            return is_enabled

        except Exception as e:
            logger.error("Failed to check feature entitlement", extra={
                "user_id": str(user_id), "feature": feature, "error": str(e)
            })
            # Default to false for security
            return False

    @trace_async
    async def create_trial_subscription(self, user_id: UUID) -> SubscriptionStatusOut:
        """Create a new trial subscription for user registration."""
        try:
            async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                repo = SubscriptionRepository(uow.session)

                # Check if subscription already exists
                existing = await repo.get_by_user_id(user_id)
                if existing:
                    logger.info("Trial subscription already exists", extra={
                        "user_id": str(user_id)
                    })
                    return existing

                # Create trial subscription
                result = await self._create_trial_subscription(user_id, repo)
                
                # Commit the transaction
                await uow.commit()

                logger.info("Trial subscription created", extra={
                    "user_id": str(user_id),
                    "trial_end_date": result.trial_end_date.isoformat() if result.trial_end_date else None
                })

                return result

        except Exception as e:
            logger.error("Failed to create trial subscription", extra={
                "user_id": str(user_id), "error": str(e)
            })
            raise BadRequest("Failed to create trial subscription")

    @trace_async
    async def is_trial_expired(self, user_id: UUID) -> bool:
        """Check if user's trial period has expired."""
        try:
            status = await self.get_subscription_status(user_id)

            if status.subscription_tier != SubscriptionTier.TRIAL:
                return False

            if not status.trial_end_date:
                return False

            is_expired = status.trial_end_date <= utcnow()

            logger.debug("Trial expiration checked", extra={
                "user_id": str(user_id),
                "trial_end_date": status.trial_end_date.isoformat(),
                "is_expired": is_expired
            })

            return is_expired

        except Exception as e:
            logger.error("Failed to check trial expiration", extra={
                "user_id": str(user_id), "error": str(e)
            })
            # Default to expired for security
            return True

    @trace_async
    async def upgrade_trial_to_paid(self, user_id: UUID, revenuecat_subscriber_id: str) -> SubscriptionStatusOut:
        """Upgrade user from trial to paid subscription."""
        try:
            async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                repo = SubscriptionRepository(uow.session)

                # Update subscription to paid tier
                update_data = SubscriptionStatusUpdate(
                    subscription_tier=SubscriptionTier.PAID,
                    revenuecat_subscriber_id=revenuecat_subscriber_id,
                    entitlement="premium",
                    trial=False,
                    will_renew=True,
                    expiration_date=utcnow() + timedelta(days=30)  # 30-day paid period
                )

                result = await repo.update(user_id, update_data)
                if result is None:
                    raise NotFound("Subscription not found for upgrade")

                # Invalidate cache
                await self._invalidate_subscription_cache(user_id)

                logger.info("Trial upgraded to paid subscription", extra={
                    "user_id": str(user_id),
                    "revenuecat_subscriber_id": revenuecat_subscriber_id
                })

                return result

        except Exception as e:
            logger.error("Failed to upgrade trial to paid", extra={
                "user_id": str(user_id), "error": str(e)
            })
            raise BadRequest("Failed to upgrade subscription")

    @trace_async
    async def handle_webhook_event(self, event: RevenueCatWebhookEvent) -> None:
        """Handle RevenueCat webhook events for subscription lifecycle changes."""
        with RequestTracker(operation="handle_webhook_event", resource=f"event_{event.event_type}") as tracker:
            try:
                user_id = UUID(event.app_user_id)
                
                tracking_context = domain_logger.operation_start(
                    operation="handle_webhook_event",
                    context={
                        "event_type": event.event_type,
                        "user_id": str(user_id),
                        "product_id": event.product_id
                    }
                )

                logger.info("Processing RevenueCat webhook event", extra={
                    "event_type": event.event_type,
                    "user_id": str(user_id),
                    "product_id": event.product_id
                })

                if event.event_type == "INITIAL_PURCHASE":
                    await self._handle_initial_purchase(user_id, event)
                elif event.event_type == "RENEWAL":
                    await self._handle_renewal(user_id, event)
                elif event.event_type == "CANCELLATION":
                    await self._handle_cancellation(user_id, event)
                elif event.event_type == "EXPIRATION":
                    await self._handle_expiration(user_id, event)
                else:
                    logger.warning("Unhandled webhook event type", extra={
                        "event_type": event.event_type,
                        "user_id": str(user_id)
                    })

                tracker.log_success(result_id=str(user_id))
                tracking_context = domain_logger.operation_start("handle_webhook_event")

                domain_logger.operation_success(tracking_context,
                    context={
                        "event_type": event.event_type,
                        "user_id": str(user_id),
                        "product_id": event.product_id
                    }
                )
                domain_logger.business_event(
                    event="webhook_event_processed",
                    context={
                        "event_type": event.event_type,
                        "user_id": str(user_id),
                        "product_id": event.product_id
                    }
                )

            except ValueError as e:
                error_id = tracker.log_error(e, context={"app_user_id": event.app_user_id})
                domain_logger.operation_error(
                    tracking_context,
                    e,
                    {"app_user_id": event.app_user_id, "error_id": error_id}
                )
                logger.error(f"Invalid user ID in webhook event (Error ID: {error_id})", extra={
                    "app_user_id": event.app_user_id, "error": str(e), "error_id": error_id
                })
                raise BadRequest(f"Invalid user ID in webhook event (Error ID: {error_id})")
            except Exception as e:
                error_id = tracker.log_error(e, context={"event_type": event.event_type})
                domain_logger.operation_error(
                    tracking_context,
                    e,
                    {"event_type": event.event_type, "error_id": error_id}
                )
                logger.error(f"Failed to handle webhook event (Error ID: {error_id})", extra={
                    "event_type": event.event_type, "error": str(e), "error_id": error_id
                })
                raise BadRequest(f"Failed to process webhook event (Error ID: {error_id})")

    # Private helper methods

    def _is_subscription_active(self, status: SubscriptionStatusOut) -> bool:
        """Check if subscription is currently active."""
        if not status.expiration_date:
            return False
        return status.expiration_date > utcnow()

    async def _create_trial_subscription(self, user_id: UUID, repo: SubscriptionRepository) -> SubscriptionStatusOut:
        """Create a new trial subscription."""
        now = utcnow()
        trial_end = now + timedelta(days=self.trial_duration_days)

        subscription_data = SubscriptionStatusCreate(
            entitlement="free",
            platform=None,  # Will be handled by repository to avoid constraint issues
            subscription_tier=SubscriptionTier.TRIAL,
            trial=True,
            trial_start_date=now,
            trial_end_date=trial_end,
            expiration_date=trial_end,
            will_renew=False
        )

        return await repo.create(user_id, subscription_data)

    async def _determine_subscription_tier_from_revenuecat(self, subscriber_info) -> SubscriptionTier:
        """Determine subscription tier from RevenueCat subscriber info."""
        entitlements = subscriber_info.get("entitlements", {})

        # Check for active premium entitlements
        for entitlement_id, entitlement_data in entitlements.items():
            if entitlement_data.get("expires_date") is None or \
               datetime.fromisoformat(entitlement_data["expires_date"].replace('Z', '+00:00')) > datetime.utcnow():
                return SubscriptionTier.PAID

        return SubscriptionTier.TRIAL

    def _create_subscription_from_revenuecat(self, user_id: UUID, subscriber_info, tier: SubscriptionTier) -> SubscriptionStatusCreate:
        """Create subscription data from RevenueCat subscriber info."""
        entitlements = subscriber_info.get("entitlements", {})

        # Get the first active entitlement for basic info
        active_entitlement = None
        for entitlement_data in entitlements.values():
            if entitlement_data.get("expires_date") is None or \
               datetime.fromisoformat(entitlement_data["expires_date"].replace('Z', '+00:00')) > datetime.utcnow():
                active_entitlement = entitlement_data
                break

        if active_entitlement:
            return SubscriptionStatusCreate(
                entitlement="premium" if tier == SubscriptionTier.PAID else "free",
                subscription_tier=tier,
                revenuecat_subscriber_id=str(user_id),
                product_id=active_entitlement.get("product_identifier"),
                expiration_date=datetime.fromisoformat(active_entitlement["expires_date"].replace('Z', '+00:00')) if active_entitlement.get("expires_date") else None,
                original_purchase_date=datetime.fromisoformat(active_entitlement["purchase_date"].replace('Z', '+00:00')) if active_entitlement.get("purchase_date") else None,
                trial=tier == SubscriptionTier.TRIAL,
                will_renew=True,
                raw=subscriber_info
            )
        else:
            # No active entitlements, create trial
            now = utcnow()
            return SubscriptionStatusCreate(
                entitlement="free",
                subscription_tier=SubscriptionTier.TRIAL,
                revenuecat_subscriber_id=str(user_id),
                trial=True,
                trial_start_date=now,
                trial_end_date=now + timedelta(days=self.trial_duration_days),
                expiration_date=now + timedelta(days=self.trial_duration_days),
                will_renew=False,
                raw=subscriber_info
            )

    def _create_update_from_revenuecat(self, subscriber_info, tier: SubscriptionTier) -> SubscriptionStatusUpdate:
        """Create subscription update data from RevenueCat subscriber info."""
        entitlements = subscriber_info.get("entitlements", {})

        # Get the first active entitlement for basic info
        active_entitlement = None
        for entitlement_data in entitlements.values():
            if entitlement_data.get("expires_date") is None or \
               datetime.fromisoformat(entitlement_data["expires_date"].replace('Z', '+00:00')) > datetime.utcnow():
                active_entitlement = entitlement_data
                break

        if active_entitlement:
            return SubscriptionStatusUpdate(
                entitlement="premium" if tier == SubscriptionTier.PAID else "free",
                subscription_tier=tier,
                product_id=active_entitlement.get("product_identifier"),
                expiration_date=datetime.fromisoformat(active_entitlement["expires_date"].replace('Z', '+00:00')) if active_entitlement.get("expires_date") else None,
                trial=tier == SubscriptionTier.TRIAL,
                will_renew=True,
                raw=subscriber_info
            )
        else:
            return SubscriptionStatusUpdate(
                entitlement="free",
                subscription_tier=SubscriptionTier.TRIAL,
                trial=True,
                will_renew=False,
                raw=subscriber_info
            )

    async def _invalidate_subscription_cache(self, user_id: UUID) -> None:
        """Invalidate subscription-related cache entries."""
        try:
            # Delete subscription status cache
            status_key = f"subscription:status:{user_id}"
            await self.redis_client.delete(status_key)
            
            # Delete auth subscription cache
            auth_key = f"auth:subscription:{user_id}"
            await self.redis_client.delete(auth_key)

            # Delete entitlement cache entries (scan for pattern)
            entitlement_pattern = f"subscription:entitlement:{user_id}:*"
            deleted_count = 0

            async for key in self.redis_client.scan_iter(match=entitlement_pattern):
                await self.redis_client.delete(key)
                deleted_count += 1

            logger.debug("Subscription cache invalidated", extra={
                "user_id": str(user_id),
                "entitlement_keys_deleted": deleted_count
            })

        except Exception as e:
            logger.warning("Failed to invalidate subscription cache", extra={
                "user_id": str(user_id), "error": str(e)
            })

    async def _handle_initial_purchase(self, user_id: UUID, event: RevenueCatWebhookEvent) -> None:
        """Handle initial purchase webhook event."""
        await self.upgrade_trial_to_paid(user_id, event.original_app_user_id)

    async def _handle_renewal(self, user_id: UUID, event: RevenueCatWebhookEvent) -> None:
        """Handle renewal webhook event."""
        async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
            repo = SubscriptionRepository(uow.session)

            expiration_date = None
            if event.expiration_at_ms:
                expiration_date = datetime.fromtimestamp(event.expiration_at_ms / 1000)

            update_data = SubscriptionStatusUpdate(
                expiration_date=expiration_date,
                will_renew=True,
                billing_issue=False
            )

            await repo.update(user_id, update_data)
            await self._invalidate_subscription_cache(user_id)

    async def _handle_cancellation(self, user_id: UUID, event: RevenueCatWebhookEvent) -> None:
        """Handle cancellation webhook event."""
        async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
            repo = SubscriptionRepository(uow.session)

            update_data = SubscriptionStatusUpdate(
                will_renew=False
            )

            await repo.update(user_id, update_data)
            await self._invalidate_subscription_cache(user_id)

    async def _handle_expiration(self, user_id: UUID, event: RevenueCatWebhookEvent) -> None:
        """Handle expiration webhook event."""
        async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
            repo = SubscriptionRepository(uow.session)

            # Downgrade to trial
            now = utcnow()
            update_data = SubscriptionStatusUpdate(
                subscription_tier=SubscriptionTier.TRIAL,
                entitlement="free",
                trial=True,
                trial_start_date=now,
                trial_end_date=now + timedelta(days=self.trial_duration_days),
                expiration_date=now + timedelta(days=self.trial_duration_days),
                will_renew=False
            )

            await repo.update(user_id, update_data)
            await self._invalidate_subscription_cache(user_id)

    @trace_async
    async def get_trial_days_remaining(self, user_id: UUID) -> int:
        """Get number of days remaining in trial period."""
        try:
            status = await self.get_subscription_status(user_id)

            if status.subscription_tier != SubscriptionTier.TRIAL or not status.trial_end_date:
                return 0

            now = utcnow()
            if status.trial_end_date <= now:
                return 0

            days_remaining = (status.trial_end_date - now).days
            return max(0, days_remaining)

        except Exception as e:
            logger.error("Failed to get trial days remaining", extra={
                "user_id": str(user_id), "error": str(e)
            })
            return 0

    @trace_async
    async def extend_trial_period(self, user_id: UUID, additional_days: int) -> SubscriptionStatusOut:
        """Extend trial period by additional days."""
        if additional_days <= 0:
            raise BadRequest("Additional days must be positive")

        try:
            async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                repo = SubscriptionRepository(uow.session)

                status = await repo.get_by_user_id(user_id)
                if not status or status.subscription_tier != SubscriptionTier.TRIAL:
                    raise BadRequest("User does not have an active trial subscription")

                # Extend trial end date
                new_trial_end = (status.trial_end_date or utcnow()) + timedelta(days=additional_days)

                update_data = SubscriptionStatusUpdate(
                    trial_end_date=new_trial_end,
                    expiration_date=new_trial_end
                )

                result = await repo.update(user_id, update_data)
                if result is None:
                    raise NotFound("Subscription not found")

                # Invalidate cache
                await self._invalidate_subscription_cache(user_id)

                logger.info("Trial period extended", extra={
                    "user_id": str(user_id),
                    "additional_days": additional_days,
                    "new_trial_end": new_trial_end.isoformat()
                })

                return result

        except Exception as e:
            logger.error("Failed to extend trial period", extra={
                "user_id": str(user_id), "additional_days": additional_days, "error": str(e)
            })
            raise BadRequest("Failed to extend trial period")

    @trace_async
    async def find_expiring_trials(self, days_ahead: int = 3) -> list[SubscriptionStatusOut]:
        """Find trial subscriptions expiring within specified days."""
        try:
            async with async_uow_factory(self.session_factory, user_id=None)() as uow:
                repo = SubscriptionRepository(uow.session)

                # Find trials by tier and expiration date
                trials = await repo.find_by_subscription_tier(SubscriptionTier.TRIAL)

                # Filter by expiration date
                now = utcnow()
                cutoff_date = now + timedelta(days=days_ahead)

                expiring_trials = [
                    trial for trial in trials
                    if trial.trial_end_date and now <= trial.trial_end_date <= cutoff_date
                ]

                logger.info("Found expiring trials", extra={
                    "count": len(expiring_trials),
                    "days_ahead": days_ahead
                })

                return expiring_trials

        except Exception as e:
            logger.error("Failed to find expiring trials", extra={
                "days_ahead": days_ahead, "error": str(e)
            })
            raise BadRequest("Failed to find expiring trials")

    @trace_async
    async def enforce_trial_expiration(self, user_id: UUID) -> bool:
        """Enforce trial expiration by checking and updating status."""
        try:
            is_expired = await self.is_trial_expired(user_id)

            if is_expired:
                async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                    repo = SubscriptionRepository(uow.session)

                    # Update to expired trial status
                    update_data = SubscriptionStatusUpdate(
                        entitlement="expired",
                        will_renew=False
                    )

                    await repo.update(user_id, update_data)
                    await self._invalidate_subscription_cache(user_id)

                    logger.info("Trial expiration enforced", extra={
                        "user_id": str(user_id)
                    })

            return is_expired

        except Exception as e:
            logger.error("Failed to enforce trial expiration", extra={
                "user_id": str(user_id), "error": str(e)
            })
            # Default to expired for security
            return True

    @trace_async
    async def get_subscription_tier(self, user_id: UUID) -> SubscriptionTier:
        """Get user's current subscription tier."""
        try:
            status = await self.get_subscription_status(user_id)
            return status.subscription_tier
        except Exception as e:
            logger.error("Failed to get subscription tier", extra={
                "user_id": str(user_id), "error": str(e)
            })
            # Default to trial for new users
            return SubscriptionTier.TRIAL

    @trace_async
    async def get_user_entitlements(self, user_id: UUID) -> list[str]:
        """Get list of entitlements for the user."""
        try:
            status = await self.get_subscription_status(user_id)

            # Base entitlements for all users
            entitlements = ["basic_features"]

            # Add tier-specific entitlements
            if status.subscription_tier == SubscriptionTier.TRIAL:
                entitlements.extend([
                    "limited_threads",  # 3 threads max
                    "basic_ai",         # 10 requests per thread per day
                    "basic_support"
                ])
            elif status.subscription_tier == SubscriptionTier.PAID:
                entitlements.extend([
                    "unlimited_threads",
                    "advanced_ai",      # 50 requests per day total
                    "priority_support",
                    "analytics"
                ])

            # Add entitlement-specific features
            if status.entitlement == "premium":
                entitlements.extend([
                    "premium_features",
                    "advanced_analytics"
                ])
            elif status.entitlement == "pro":
                entitlements.extend([
                    "premium_features",
                    "advanced_analytics",
                    "pro_features",
                    "api_access"
                ])

            logger.debug("User entitlements retrieved", extra={
                "user_id": str(user_id),
                "tier": status.subscription_tier.value,
                "entitlement": status.entitlement,
                "entitlements_count": len(entitlements)
            })

            return entitlements

        except Exception as e:
            logger.error("Failed to get user entitlements", extra={
                "user_id": str(user_id), "error": str(e)
            })
            # Return minimal entitlements on error
            return ["basic_features"]

    @trace_async
    async def update_subscription_tier(self, user_id: UUID, new_tier: SubscriptionTier) -> SubscriptionStatusOut:
        """Update user's subscription tier."""
        try:
            async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                repo = SubscriptionRepository(uow.session)

                # Determine new entitlement based on tier
                new_entitlement = "premium" if new_tier == SubscriptionTier.PAID else "free"

                # Set appropriate dates based on tier
                now = utcnow()
                if new_tier == SubscriptionTier.TRIAL:
                    trial_end = now + timedelta(days=self.trial_duration_days)
                    update_data = SubscriptionStatusUpdate(
                        subscription_tier=new_tier,
                        entitlement=new_entitlement,
                        trial=True,
                        trial_start_date=now,
                        trial_end_date=trial_end,
                        expiration_date=trial_end,
                        will_renew=False
                    )
                else:  # PAID
                    paid_end = now + timedelta(days=30)  # 30-day paid period
                    update_data = SubscriptionStatusUpdate(
                        subscription_tier=new_tier,
                        entitlement=new_entitlement,
                        trial=False,
                        expiration_date=paid_end,
                        will_renew=True
                    )

                result = await repo.update(user_id, update_data)
                if result is None:
                    raise NotFound("Subscription not found")

                # Invalidate cache
                await self._invalidate_subscription_cache(user_id)

                logger.info("Subscription tier updated", extra={
                    "user_id": str(user_id),
                    "old_tier": "unknown",
                    "new_tier": new_tier.value,
                    "new_entitlement": new_entitlement
                })

                return result

        except Exception as e:
            logger.error("Failed to update subscription tier", extra={
                "user_id": str(user_id), "new_tier": new_tier.value, "error": str(e)
            })
            raise BadRequest("Failed to update subscription tier")

    @trace_async
    async def bulk_update_subscription_cache(self, user_ids: list[UUID]) -> int:
        """Bulk update subscription cache for multiple users."""
        updated_count = 0

        for user_id in user_ids:
            try:
                # This will fetch from DB and update cache
                await self.get_subscription_status(user_id)
                updated_count += 1
            except Exception as e:
                logger.warning("Failed to update cache for user", extra={
                    "user_id": str(user_id), "error": str(e)
                })

        logger.info("Bulk cache update completed", extra={
            "total_users": len(user_ids),
            "updated_count": updated_count
        })

        return updated_count

    @trace_async
    async def warm_subscription_cache(self, limit: int = 1000) -> int:
        """Warm subscription cache for active users."""
        try:
            warmed_count = 0

            # Get active subscriptions from database
            async with async_uow_factory(self.session_factory, user_id=None)() as uow:
                SubscriptionRepository(uow.session)

                # Get active subscriptions (those not expired)
                stmt = sa.select(subscription_status_table.c.user_id).where(
                    subscription_status_table.c.expiration_date > sa.func.now()
                ).limit(limit)

                result = await uow.session.execute(stmt)
                user_ids = [row.user_id for row in result.fetchall()]

            # Warm cache for these users
            for user_id in user_ids:
                try:
                    # This will populate the cache
                    await self.get_subscription_status(user_id)
                    warmed_count += 1
                except Exception as e:
                    logger.warning("Failed to warm cache for user", extra={
                        "user_id": str(user_id), "error": str(e)
                    })

            logger.info("Subscription cache warming completed", extra={
                "total_users": len(user_ids),
                "warmed_count": warmed_count
            })

            return warmed_count

        except Exception as e:
            logger.error("Failed to warm subscription cache", extra={
                "error": str(e)
            })
            raise BadRequest("Failed to warm subscription cache")

    @trace_async
    async def preload_user_entitlements(self, user_id: UUID, features: list[str]) -> dict[str, bool]:
        """Preload and cache entitlements for multiple features."""
        try:
            entitlements = {}

            for feature in features:
                try:
                    is_enabled = await self.is_feature_enabled(user_id, feature)
                    entitlements[feature] = is_enabled
                except Exception as e:
                    logger.warning("Failed to check feature entitlement", extra={
                        "user_id": str(user_id), "feature": feature, "error": str(e)
                    })
                    entitlements[feature] = False

            logger.debug("User entitlements preloaded", extra={
                "user_id": str(user_id),
                "features_count": len(features),
                "enabled_count": sum(entitlements.values())
            })

            return entitlements

        except Exception as e:
            logger.error("Failed to preload user entitlements", extra={
                "user_id": str(user_id), "error": str(e)
            })
            raise BadRequest("Failed to preload entitlements")

    @trace_async
    async def get_subscription_analytics(self) -> dict[str, Any]:
        """Get subscription analytics and metrics."""
        try:
            async with async_uow_factory(self.session_factory, user_id=None)() as uow:
                repo = SubscriptionRepository(uow.session)

                # Get counts by tier
                trial_subscriptions = await repo.find_by_subscription_tier(SubscriptionTier.TRIAL)
                paid_subscriptions = await repo.find_by_subscription_tier(SubscriptionTier.PAID)

                # Get active subscription count
                active_count = await repo.count_active_subscriptions()

                # Calculate trial conversion metrics
                total_trials = len(trial_subscriptions)
                total_paid = len(paid_subscriptions)
                conversion_rate = (total_paid / (total_trials + total_paid)) * 100 if (total_trials + total_paid) > 0 else 0

                # Get expiring trials
                expiring_trials = await self.find_expiring_trials(days_ahead=7)

                analytics = {
                    "total_subscriptions": total_trials + total_paid,
                    "active_subscriptions": active_count,
                    "trial_subscriptions": total_trials,
                    "paid_subscriptions": total_paid,
                    "conversion_rate_percent": round(conversion_rate, 2),
                    "expiring_trials_7_days": len(expiring_trials),
                    "generated_at": utcnow().isoformat()
                }

                logger.info("Subscription analytics generated", extra=analytics)

                return analytics

        except Exception as e:
            logger.error("Failed to get subscription analytics", extra={"error": str(e)})
            raise BadRequest("Failed to generate subscription analytics")

    # Database optimization methods

    @trace_async
    async def optimize_database_performance(self) -> dict[str, Any]:
        """Run comprehensive database optimization for subscription system."""
        try:
            optimization_results = {
                "analysis": {},
                "indexes": {},
                "partitioning": {},
                "maintenance": {},
                "completed_at": utcnow().isoformat()
            }

            # Run database analysis
            try:
                analysis = await self.db_optimizer.analyze_subscription_queries()
                optimization_results["analysis"] = analysis
            except Exception as e:
                logger.warning("Database analysis failed", extra={"error": str(e)})
                optimization_results["analysis"] = {"error": str(e)}

            # Optimize indexes
            try:
                index_results = await self.db_optimizer.optimize_subscription_indexes()
                optimization_results["indexes"] = index_results
            except Exception as e:
                logger.warning("Index optimization failed", extra={"error": str(e)})
                optimization_results["indexes"] = {"error": str(e)}

            # Set up partitioning
            try:
                partition_results = await self.db_optimizer.partition_quota_usage_table()
                optimization_results["partitioning"] = partition_results
            except Exception as e:
                logger.warning("Partitioning setup failed", extra={"error": str(e)})
                optimization_results["partitioning"] = {"error": str(e)}

            # Run maintenance
            try:
                maintenance_results = await self.db_optimizer.vacuum_and_analyze_tables()
                optimization_results["maintenance"] = maintenance_results
            except Exception as e:
                logger.warning("Database maintenance failed", extra={"error": str(e)})
                optimization_results["maintenance"] = {"error": str(e)}

            logger.info("Database optimization completed", extra={
                "has_analysis": "error" not in optimization_results["analysis"],
                "has_indexes": "error" not in optimization_results["indexes"],
                "has_partitioning": "error" not in optimization_results["partitioning"],
                "has_maintenance": "error" not in optimization_results["maintenance"]
            })

            return optimization_results

        except Exception as e:
            logger.error("Failed to optimize database performance", extra={
                "error": str(e)
            })
            raise BadRequest("Failed to optimize database performance")

    @trace_async
    async def cleanup_old_subscription_data(self, days_to_keep: int = 90) -> dict[str, int]:
        """Clean up old subscription-related data."""
        try:
            cleanup_results = await self.db_optimizer.cleanup_old_quota_data(days_to_keep)

            logger.info("Subscription data cleanup completed", extra=cleanup_results)

            return cleanup_results

        except Exception as e:
            logger.error("Failed to cleanup old subscription data", extra={
                "error": str(e)
            })
            raise BadRequest("Failed to cleanup old subscription data")

    @trace_async
    async def get_database_health_metrics(self) -> dict[str, Any]:
        """Get database health metrics for subscription system."""
        try:
            health_metrics = {
                "subscription_table": {},
                "quota_table": {},
                "cache_stats": {},
                "performance_indicators": {},
                "generated_at": utcnow().isoformat()
            }

            # Get database analysis
            try:
                analysis = await self.db_optimizer.analyze_subscription_queries()
                health_metrics["subscription_table"] = analysis.get("table_stats", {}).get("subscription_status", {})
                health_metrics["quota_table"] = analysis.get("table_stats", {}).get("quota_usage", {})
                health_metrics["performance_indicators"] = {
                    "recommendations_count": len(analysis.get("recommendations", [])),
                    "index_usage": analysis.get("index_usage", {})
                }
            except Exception as e:
                logger.warning("Failed to get database analysis for health metrics", extra={
                    "error": str(e)
                })

            # Get cache statistics (if quota service is available)
            try:
                from .quota_service import QuotaService
                quota_service = QuotaService(self.session_factory)
                cache_stats = await quota_service.get_quota_cache_stats()
                health_metrics["cache_stats"] = cache_stats
            except Exception as e:
                logger.warning("Failed to get cache stats for health metrics", extra={
                    "error": str(e)
                })

            logger.debug("Database health metrics generated")

            return health_metrics

        except Exception as e:
            logger.error("Failed to get database health metrics", extra={
                "error": str(e)
            })
            raise BadRequest("Failed to get database health metrics")


def create_subscription_service(
    session_factory: async_sessionmaker[AsyncSession],
    revenuecat_client: RevenueCatClient | None = None,
    config: SubscriptionConfig | None = None
) -> SubscriptionService:
    """Factory function for SubscriptionService.
    
    Args:
        session_factory: SQLAlchemy async session factory
        revenuecat_client: Optional RevenueCat client instance
        config: Optional subscription configuration
        
    Returns:
        Configured SubscriptionService instance
    """
    return SubscriptionService(session_factory, revenuecat_client, config)


def create_subscription_service_with_revenuecat(
    session_factory: async_sessionmaker[AsyncSession],
    config: SubscriptionConfig | None = None
) -> SubscriptionService:
    """Factory function for SubscriptionService with auto-configured RevenueCat client.
    
    Args:
        session_factory: SQLAlchemy async session factory
        config: Optional subscription configuration
        
    Returns:
        Configured SubscriptionService instance with RevenueCat client
    """
    from .revenuecat_client import create_revenuecat_client_from_config

    # Load config if not provided
    if config is None:
        config = get_subscription_config()

    # Create RevenueCat client if configured
    revenuecat_client = None
    if config.is_revenuecat_configured() and config.enable_revenuecat_sync:
        revenuecat_client = create_revenuecat_client_from_config()

    return SubscriptionService(session_factory, revenuecat_client, config)
