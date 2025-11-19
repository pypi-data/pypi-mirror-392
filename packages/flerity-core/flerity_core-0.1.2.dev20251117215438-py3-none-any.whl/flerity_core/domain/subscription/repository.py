"""Subscription repository for managing user subscription status and quota usage."""

from datetime import date
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from ...utils.errors import BadRequest, Conflict, NotFound
from ...utils.logging import get_logger
from ...utils.tracing import trace_async
from .schemas import (
    QuotaType,
    QuotaUsageCreate,
    QuotaUsageOut,
    SubscriptionPlatform,
    SubscriptionStatusCreate,
    SubscriptionStatusOut,
    SubscriptionStatusUpdate,
    SubscriptionTier,
    quota_usage_table,
    subscription_status_table,
)

logger = get_logger(__name__)


class SubscriptionRepository:
    """Repository for subscription status data access operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    @trace_async
    async def get_by_user_id(self, user_id: UUID) -> SubscriptionStatusOut | None:
        """Get subscription status by user ID (RLS enforced)."""
        try:
            stmt = sa.select(subscription_status_table).where(
                subscription_status_table.c.user_id == user_id
            )

            result = await self.session.execute(stmt)
            row = result.fetchone()
            return SubscriptionStatusOut.model_validate(row._asdict()) if row else None
        except sa.exc.SQLAlchemyError as e:
            logger.error("Database error getting subscription", extra={
                "user_id": str(user_id), "error": str(e)
            })
            raise BadRequest("Failed to retrieve subscription")
        except Exception as e:
            logger.error("Unexpected error getting subscription", extra={
                "user_id": str(user_id), "error": str(e)
            })
            raise BadRequest("Failed to retrieve subscription")

    @trace_async
    async def create(self, user_id: UUID, data: SubscriptionStatusCreate, locale: str = "en-US") -> SubscriptionStatusOut:
        """Create new subscription status."""
        from ...utils.i18n import t

        try:
            subscription_data = data.model_dump()
            subscription_data['user_id'] = user_id

            stmt = sa.insert(subscription_status_table).values(**subscription_data).returning(subscription_status_table)
            result = await self.session.execute(stmt)
            row = result.fetchone()

            if not row:
                raise BadRequest(t("subscription.error.apple_sync_failed", locale=locale))

            logger.info("Subscription status created", extra={
                "user_id": str(user_id),
                "entitlement": data.entitlement,
                "platform": data.platform,
            })

            return SubscriptionStatusOut.model_validate(row._asdict())
        except sa.exc.IntegrityError as e:
            logger.error("Subscription creation integrity error", extra={
                "user_id": str(user_id), 
                "error": str(e),
                "error_detail": str(e.orig) if hasattr(e, 'orig') else None,
                "subscription_data": subscription_data
            })
            raise Conflict(t("subscription.error.apple_sync_failed", locale=locale))
        except sa.exc.SQLAlchemyError as e:
            logger.error("Database error creating subscription", extra={
                "user_id": str(user_id), "error": str(e)
            })
            raise BadRequest(t("subscription.error.apple_sync_failed", locale=locale))
        except Exception as e:
            logger.error("Unexpected error creating subscription", extra={
                "user_id": str(user_id), "error": str(e)
            })
            raise BadRequest(t("subscription.error.apple_sync_failed", locale=locale))

    @trace_async
    async def upsert(self, user_id: UUID, data: SubscriptionStatusCreate, locale: str = "en-US") -> SubscriptionStatusOut:
        """Upsert subscription status (idempotent)."""
        from ...utils.i18n import t

        try:
            subscription_data = data.model_dump()
            subscription_data['user_id'] = user_id

            insert_stmt = pg_insert(subscription_status_table).values(**subscription_data)
            stmt = insert_stmt.on_conflict_do_update(
                index_elements=['user_id'],
                set_={
                    'entitlement': insert_stmt.excluded.entitlement,
                    'platform': insert_stmt.excluded.platform,
                    'product_id': insert_stmt.excluded.product_id,
                    'will_renew': insert_stmt.excluded.will_renew,
                    'original_purchase_date': insert_stmt.excluded.original_purchase_date,
                    'expiration_date': insert_stmt.excluded.expiration_date,
                    'grace_period': insert_stmt.excluded.grace_period,
                    'trial': insert_stmt.excluded.trial,
                    'billing_issue': insert_stmt.excluded.billing_issue,
                    'raw': insert_stmt.excluded.raw,
                    # New RevenueCat integration fields
                    'revenuecat_subscriber_id': insert_stmt.excluded.revenuecat_subscriber_id,
                    'subscription_tier': insert_stmt.excluded.subscription_tier,
                    'trial_start_date': insert_stmt.excluded.trial_start_date,
                    'trial_end_date': insert_stmt.excluded.trial_end_date,
                    'updated_at': sa.func.now()
                }
            ).returning(subscription_status_table)

            result = await self.session.execute(stmt)
            row = result.fetchone()

            if not row:
                platform_key = "google_sync_failed" if data.platform == "google" else "apple_sync_failed"
                raise BadRequest(t(f"subscription.error.{platform_key}", locale=locale))

            logger.info("Subscription status upserted", extra={
                "user_id": str(user_id),
                "entitlement": data.entitlement,
                "platform": data.platform,
            })

            return SubscriptionStatusOut.model_validate(row._asdict())
        except sa.exc.SQLAlchemyError as e:
            logger.error("Database error upserting subscription", extra={
                "user_id": str(user_id), "error": str(e)
            })
            platform_key = "google_sync_failed" if data.platform == "google" else "apple_sync_failed"
            raise BadRequest(t(f"subscription.error.{platform_key}", locale=locale))
        except Exception as e:
            logger.error("Unexpected error upserting subscription", extra={
                "user_id": str(user_id), "error": str(e)
            })
            platform_key = "google_sync_failed" if data.platform == "google" else "apple_sync_failed"
            raise BadRequest(t(f"subscription.error.{platform_key}", locale=locale))

    @trace_async
    async def update(self, user_id: UUID, data: SubscriptionStatusUpdate) -> SubscriptionStatusOut | None:
        """Update subscription status."""
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_by_user_id(user_id)

        update_data['updated_at'] = sa.func.now()

        try:
            stmt = (
                sa.update(subscription_status_table)
                .where(subscription_status_table.c.user_id == user_id)
                .values(**update_data)
                .returning(subscription_status_table)
            )

            result = await self.session.execute(stmt)
            row = result.fetchone()

            if row:
                logger.info("Subscription status updated", extra={
                    "user_id": str(user_id),
                    "fields_updated": list(update_data.keys()),
                })
                return SubscriptionStatusOut.model_validate(row._asdict())
            return None
        except sa.exc.SQLAlchemyError as e:
            logger.error("Database error updating subscription", extra={
                "user_id": str(user_id), "error": str(e)
            })
            raise BadRequest("Failed to update subscription")
        except Exception as e:
            logger.error("Unexpected error updating subscription", extra={
                "user_id": str(user_id), "error": str(e)
            })
            raise BadRequest("Failed to update subscription")

    @trace_async
    async def delete(self, user_id: UUID) -> None:
        """Delete subscription status."""
        try:
            stmt = sa.delete(subscription_status_table).where(
                subscription_status_table.c.user_id == user_id
            )

            result = await self.session.execute(stmt)

            if getattr(result, 'rowcount', 0) == 0:
                raise NotFound("Subscription status not found")

            logger.info("Subscription status deleted", extra={
                "user_id": str(user_id),
            })
        except NotFound:
            raise
        except sa.exc.SQLAlchemyError as e:
            logger.error("Database error deleting subscription", extra={
                "user_id": str(user_id), "error": str(e)
            })
            raise BadRequest("Failed to delete subscription")
        except Exception as e:
            logger.error("Unexpected error deleting subscription", extra={
                "user_id": str(user_id), "error": str(e)
            })
            raise BadRequest("Failed to delete subscription")

    @trace_async
    async def is_active(self, user_id: UUID) -> bool:
        """Check if subscription is active."""
        try:
            stmt = sa.select(
                (subscription_status_table.c.expiration_date > sa.func.now()).label('is_active')
            ).where(subscription_status_table.c.user_id == user_id)

            result = await self.session.execute(stmt)
            row = result.fetchone()

            return bool(row.is_active) if row else False
        except sa.exc.SQLAlchemyError as e:
            logger.error("Database error checking subscription active status", extra={
                "user_id": str(user_id), "error": str(e)
            })
            raise BadRequest("Failed to check subscription status")
        except Exception as e:
            logger.error("Unexpected error checking subscription active status", extra={
                "user_id": str(user_id), "error": str(e)
            })
            raise BadRequest("Failed to check subscription status")

    @trace_async
    async def find_expiring_soon(self, days_ahead: int = 7) -> list[SubscriptionStatusOut]:
        """Find subscriptions expiring within specified days."""
        if days_ahead <= 0 or days_ahead > 365:
            raise BadRequest("days_ahead must be between 1 and 365")

        try:
            stmt = sa.select(subscription_status_table).where(
                sa.and_(
                    subscription_status_table.c.expiration_date.between(
                        sa.func.now(),
                        sa.func.now() + sa.text(f"INTERVAL '{days_ahead} days'")
                    ),
                    sa.or_(
                        subscription_status_table.c.will_renew.is_(False),
                        subscription_status_table.c.billing_issue.is_(True)
                    )
                )
            ).order_by(subscription_status_table.c.expiration_date.asc())

            result = await self.session.execute(stmt)
            rows = result.fetchall()

            return [SubscriptionStatusOut.model_validate(row._asdict()) for row in rows]
        except sa.exc.SQLAlchemyError as e:
            logger.error("Database error finding expiring subscriptions", extra={
                "days_ahead": days_ahead, "error": str(e)
            })
            raise BadRequest("Failed to find expiring subscriptions")
        except Exception as e:
            logger.error("Unexpected error finding expiring subscriptions", extra={
                "days_ahead": days_ahead, "error": str(e)
            })
            raise BadRequest("Failed to find expiring subscriptions")

    @trace_async
    async def find_by_platform(self, platform: SubscriptionPlatform) -> list[SubscriptionStatusOut]:
        """Find all subscriptions by platform."""
        try:
            stmt = sa.select(subscription_status_table).where(
                subscription_status_table.c.platform == platform
            ).order_by(subscription_status_table.c.updated_at.desc())

            result = await self.session.execute(stmt)
            rows = result.fetchall()

            return [SubscriptionStatusOut.model_validate(row._asdict()) for row in rows]
        except sa.exc.SQLAlchemyError as e:
            logger.error("Database error finding subscriptions by platform", extra={
                "platform": platform, "error": str(e)
            })
            raise BadRequest("Failed to find subscriptions by platform")
        except Exception as e:
            logger.error("Unexpected error finding subscriptions by platform", extra={
                "platform": platform, "error": str(e)
            })
            raise BadRequest("Failed to find subscriptions by platform")

    @trace_async
    async def count_active_subscriptions(self) -> int:
        """Count active subscriptions."""
        try:
            stmt = sa.select(sa.func.count()).select_from(subscription_status_table).where(
                subscription_status_table.c.expiration_date > sa.func.now()
            )

            result = await self.session.execute(stmt)
            return result.scalar() or 0
        except sa.exc.SQLAlchemyError as e:
            logger.error("Database error counting active subscriptions", extra={"error": str(e)})
            raise BadRequest("Failed to count active subscriptions")
        except Exception as e:
            logger.error("Unexpected error counting active subscriptions", extra={"error": str(e)})
            raise BadRequest("Failed to count active subscriptions")

    # RevenueCat integration methods
    @trace_async
    async def get_by_revenuecat_subscriber_id(self, subscriber_id: str) -> SubscriptionStatusOut | None:
        """Get subscription status by RevenueCat subscriber ID."""
        try:
            stmt = sa.select(subscription_status_table).where(
                subscription_status_table.c.revenuecat_subscriber_id == subscriber_id
            )

            result = await self.session.execute(stmt)
            row = result.fetchone()
            return SubscriptionStatusOut.model_validate(row._asdict()) if row else None
        except sa.exc.SQLAlchemyError as e:
            logger.error("Database error getting subscription by RevenueCat ID", extra={
                "subscriber_id": subscriber_id, "error": str(e)
            })
            raise BadRequest("Failed to retrieve subscription")
        except Exception as e:
            logger.error("Unexpected error getting subscription by RevenueCat ID", extra={
                "subscriber_id": subscriber_id, "error": str(e)
            })
            raise BadRequest("Failed to retrieve subscription")

    @trace_async
    async def find_by_subscription_tier(self, tier: SubscriptionTier) -> list[SubscriptionStatusOut]:
        """Find all subscriptions by tier."""
        try:
            stmt = sa.select(subscription_status_table).where(
                subscription_status_table.c.subscription_tier == tier.value
            ).order_by(subscription_status_table.c.updated_at.desc())

            result = await self.session.execute(stmt)
            rows = result.fetchall()

            return [SubscriptionStatusOut.model_validate(row._asdict()) for row in rows]
        except sa.exc.SQLAlchemyError as e:
            logger.error("Database error finding subscriptions by tier", extra={
                "tier": tier.value, "error": str(e)
            })
            raise BadRequest("Failed to find subscriptions by tier")
        except Exception as e:
            logger.error("Unexpected error finding subscriptions by tier", extra={
                "tier": tier.value, "error": str(e)
            })
            raise BadRequest("Failed to find subscriptions by tier")

    # Quota usage methods
    @trace_async
    async def get_quota_usage(self, user_id: UUID, quota_type: QuotaType, date: date) -> QuotaUsageOut | None:
        """Get quota usage for a specific user, type, and date."""
        try:
            stmt = sa.select(quota_usage_table).where(
                sa.and_(
                    quota_usage_table.c.user_id == user_id,
                    quota_usage_table.c.quota_type == quota_type.value,
                    quota_usage_table.c.date == date
                )
            )

            result = await self.session.execute(stmt)
            row = result.fetchone()
            return QuotaUsageOut.model_validate(row._asdict()) if row else None
        except sa.exc.SQLAlchemyError as e:
            logger.error("Database error getting quota usage", extra={
                "user_id": str(user_id), "quota_type": quota_type.value, "date": str(date), "error": str(e)
            })
            raise BadRequest("Failed to retrieve quota usage")
        except Exception as e:
            logger.error("Unexpected error getting quota usage", extra={
                "user_id": str(user_id), "quota_type": quota_type.value, "date": str(date), "error": str(e)
            })
            raise BadRequest("Failed to retrieve quota usage")

    @trace_async
    async def create_quota_usage(self, user_id: UUID, data: QuotaUsageCreate) -> QuotaUsageOut:
        """Create new quota usage record."""
        try:
            quota_data = data.model_dump()
            quota_data['user_id'] = user_id

            stmt = sa.insert(quota_usage_table).values(**quota_data).returning(quota_usage_table)
            result = await self.session.execute(stmt)
            row = result.fetchone()

            if not row:
                raise BadRequest("Failed to create quota usage")

            logger.info("Quota usage created", extra={
                "user_id": str(user_id),
                "quota_type": data.quota_type.value,
                "date": str(data.date),
                "daily_limit": data.daily_limit,
            })

            return QuotaUsageOut.model_validate(row._asdict())
        except sa.exc.IntegrityError as e:
            logger.error("Quota usage creation integrity error", extra={
                "user_id": str(user_id), "error": str(e)
            })
            raise Conflict("Quota usage already exists for this date and type")
        except sa.exc.SQLAlchemyError as e:
            logger.error("Database error creating quota usage", extra={
                "user_id": str(user_id), "error": str(e)
            })
            raise BadRequest("Failed to create quota usage")
        except Exception as e:
            logger.error("Unexpected error creating quota usage", extra={
                "user_id": str(user_id), "error": str(e)
            })
            raise BadRequest("Failed to create quota usage")

    @trace_async
    async def upsert_quota_usage(self, user_id: UUID, data: QuotaUsageCreate) -> QuotaUsageOut:
        """Upsert quota usage record (idempotent)."""
        try:
            quota_data = data.model_dump()
            quota_data['user_id'] = user_id

            insert_stmt = pg_insert(quota_usage_table).values(**quota_data)
            stmt = insert_stmt.on_conflict_do_update(
                index_elements=['user_id', 'date', 'quota_type'],
                set_={
                    'count': insert_stmt.excluded.count,
                    'daily_limit': insert_stmt.excluded.daily_limit,
                    'updated_at': sa.func.now()
                }
            ).returning(quota_usage_table)

            result = await self.session.execute(stmt)
            row = result.fetchone()

            if not row:
                raise BadRequest("Failed to upsert quota usage")

            logger.info("Quota usage upserted", extra={
                "user_id": str(user_id),
                "quota_type": data.quota_type.value,
                "date": str(data.date),
                "count": data.count,
                "daily_limit": data.daily_limit,
            })

            return QuotaUsageOut.model_validate(row._asdict())
        except sa.exc.SQLAlchemyError as e:
            logger.error("Database error upserting quota usage", extra={
                "user_id": str(user_id), "error": str(e)
            })
            raise BadRequest("Failed to upsert quota usage")
        except Exception as e:
            logger.error("Unexpected error upserting quota usage", extra={
                "user_id": str(user_id), "error": str(e)
            })
            raise BadRequest("Failed to upsert quota usage")

    @trace_async
    async def increment_quota_usage(self, user_id: UUID, quota_type: QuotaType, date: date, daily_limit: int) -> QuotaUsageOut:
        """Increment quota usage count atomically."""
        try:
            # First try to increment existing record
            update_stmt = (
                sa.update(quota_usage_table)
                .where(
                    sa.and_(
                        quota_usage_table.c.user_id == user_id,
                        quota_usage_table.c.quota_type == quota_type.value,
                        quota_usage_table.c.date == date
                    )
                )
                .values(
                    count=quota_usage_table.c.count + 1,
                    updated_at=sa.func.now()
                )
                .returning(quota_usage_table)
            )

            result = await self.session.execute(update_stmt)
            row = result.fetchone()

            if row:
                logger.info("Quota usage incremented", extra={
                    "user_id": str(user_id),
                    "quota_type": quota_type.value,
                    "date": str(date),
                    "new_count": row.count,
                })
                return QuotaUsageOut.model_validate(row._asdict())

            # If no existing record, create one with count=1
            create_data = QuotaUsageCreate(
                quota_type=quota_type,
                date=date,
                count=1,
                daily_limit=daily_limit
            )
            return await self.create_quota_usage(user_id, create_data)

        except sa.exc.SQLAlchemyError as e:
            logger.error("Database error incrementing quota usage", extra={
                "user_id": str(user_id), "quota_type": quota_type.value, "date": str(date), "error": str(e)
            })
            raise BadRequest("Failed to increment quota usage")
        except Exception as e:
            logger.error("Unexpected error incrementing quota usage", extra={
                "user_id": str(user_id), "quota_type": quota_type.value, "date": str(date), "error": str(e)
            })
            raise BadRequest("Failed to increment quota usage")

    @trace_async
    async def get_user_quota_usage_for_date(self, user_id: UUID, date: date) -> list[QuotaUsageOut]:
        """Get all quota usage records for a user on a specific date."""
        try:
            stmt = sa.select(quota_usage_table).where(
                sa.and_(
                    quota_usage_table.c.user_id == user_id,
                    quota_usage_table.c.date == date
                )
            ).order_by(quota_usage_table.c.quota_type)

            result = await self.session.execute(stmt)
            rows = result.fetchall()

            return [QuotaUsageOut.model_validate(row._asdict()) for row in rows]
        except sa.exc.SQLAlchemyError as e:
            logger.error("Database error getting user quota usage", extra={
                "user_id": str(user_id), "date": str(date), "error": str(e)
            })
            raise BadRequest("Failed to retrieve quota usage")
        except Exception as e:
            logger.error("Unexpected error getting user quota usage", extra={
                "user_id": str(user_id), "date": str(date), "error": str(e)
            })
            raise BadRequest("Failed to retrieve quota usage")

    @trace_async
    async def cleanup_old_quota_usage(self, days_to_keep: int = 30) -> int:
        """Clean up old quota usage records."""
        try:
            cutoff_date = sa.func.current_date() - sa.text(f"INTERVAL '{days_to_keep} days'")

            stmt = sa.delete(quota_usage_table).where(
                quota_usage_table.c.date < cutoff_date
            )

            result = await self.session.execute(stmt)
            deleted_count = getattr(result, 'rowcount', 0)

            logger.info("Old quota usage records cleaned up", extra={
                "days_to_keep": days_to_keep,
                "deleted_count": deleted_count,
            })

            return deleted_count
        except sa.exc.SQLAlchemyError as e:
            logger.error("Database error cleaning up quota usage", extra={
                "days_to_keep": days_to_keep, "error": str(e)
            })
            raise BadRequest("Failed to cleanup quota usage")
        except Exception as e:
            logger.error("Unexpected error cleaning up quota usage", extra={
                "days_to_keep": days_to_keep, "error": str(e)
            })
            raise BadRequest("Failed to cleanup quota usage")
