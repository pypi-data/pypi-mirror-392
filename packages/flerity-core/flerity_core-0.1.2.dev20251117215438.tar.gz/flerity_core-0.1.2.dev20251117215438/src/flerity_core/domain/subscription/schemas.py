"""Subscription domain Pydantic schemas and DTOs."""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Date,
    ForeignKey,
    Index,
    Integer,
    MetaData,
    Table,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PGUUID


# Enums for subscription system
class SubscriptionTier(str, Enum):
    """Subscription tier enumeration."""
    TRIAL = "trial"
    PAID = "paid"


class QuotaType(str, Enum):
    """Quota type enumeration."""
    ICEBREAKER = "icebreaker"
    SUGGESTION = "suggestion"
    THREAD = "thread"


# SQLAlchemy table definition
metadata = MetaData()

subscription_status_table = Table(
    "subscription_status", metadata,
    Column("user_id", PGUUID, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("entitlement", Text, nullable=False, server_default=text("'free'"), index=True),
    Column("platform", Text, index=True),
    Column("product_id", Text),
    Column("will_renew", Boolean, server_default=text('true')),
    Column("original_purchase_date", TIMESTAMP(timezone=True)),
    Column("expiration_date", TIMESTAMP(timezone=True), index=True),
    Column("grace_period", Boolean, server_default=text('false')),
    Column("trial", Boolean, server_default=text('false')),
    Column("billing_issue", Boolean, server_default=text('false')),
    Column("raw", JSONB),
    Column("updated_at", TIMESTAMP(timezone=True), nullable=False, server_default=text('now()')),
    # New RevenueCat integration fields
    Column("revenuecat_subscriber_id", Text, index=True),
    Column("subscription_tier", Text, nullable=False, server_default=text("'trial'"), index=True),
    Column("trial_start_date", TIMESTAMP(timezone=True)),
    Column("trial_end_date", TIMESTAMP(timezone=True)),
    CheckConstraint("platform IN ('google', 'apple') OR platform IS NULL", name="platform_valid"),
    CheckConstraint("length(entitlement) > 0", name="entitlement_not_empty"),
    CheckConstraint("expiration_date IS NULL OR expiration_date > original_purchase_date", name="expiration_after_purchase"),
    CheckConstraint("subscription_tier IN ('trial', 'paid')", name="subscription_tier_valid"),
    CheckConstraint("trial_end_date IS NULL OR trial_end_date > trial_start_date", name="trial_end_after_start"),
    Index("idx_subscription_active", "expiration_date", postgresql_where=text("expiration_date > now()")),
    Index("idx_subscription_revenuecat", "revenuecat_subscriber_id"),
    Index("idx_subscription_tier", "subscription_tier"),
)

quota_usage_table = Table(
    "quota_usage", metadata,
    Column("id", PGUUID, primary_key=True, server_default=text('gen_random_uuid()')),
    Column("user_id", PGUUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
    Column("quota_type", Text, nullable=False),
    Column("date", Date, nullable=False),
    Column("count", Integer, nullable=False, server_default=text('0')),
    Column("daily_limit", Integer, nullable=False),
    Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default=text('now()')),
    Column("updated_at", TIMESTAMP(timezone=True), nullable=False, server_default=text('now()')),
    CheckConstraint("quota_type IN ('icebreaker', 'suggestion', 'thread')", name="quota_type_valid"),
    CheckConstraint("count >= 0", name="count_non_negative"),
    CheckConstraint("daily_limit > 0", name="daily_limit_positive"),
    Index("idx_quota_user_date_type", "user_id", "date", "quota_type", unique=True),
    Index("idx_quota_date", "date"),
)


SubscriptionPlatform = Literal["google", "apple"]


class SubscriptionStatusOut(BaseModel):
    """DTO for subscription status output."""
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    active: bool = Field(default=False, description="Whether subscription is currently active")
    entitlement: str = Field(default="free", min_length=1, max_length=50)
    platform: SubscriptionPlatform | None = None
    product_id: str | None = Field(None, max_length=255)
    will_renew: bool | None = None
    original_purchase_date: datetime | None = None
    expiration_date: datetime | None = None
    grace_period: bool | None = None
    trial: bool | None = None
    billing_issue: bool | None = None
    raw: dict[str, Any] | None = None
    updated_at: datetime
    # New RevenueCat integration fields
    revenuecat_subscriber_id: str | None = None
    subscription_tier: SubscriptionTier = SubscriptionTier.TRIAL
    trial_start_date: datetime | None = None
    trial_end_date: datetime | None = None


class SubscriptionStatusCreate(BaseModel):
    """DTO for creating subscription status."""
    user_id: UUID | None = None  # Optional, can be set from RLS context
    entitlement: str = Field(default="free", min_length=1, max_length=50)
    platform: SubscriptionPlatform | None = None
    product_id: str | None = Field(None, max_length=255)
    will_renew: bool = True
    original_purchase_date: datetime | None = None
    expiration_date: datetime | None = None
    grace_period: bool = False
    trial: bool = False
    billing_issue: bool = False
    raw: dict[str, Any] | None = None
    # New RevenueCat integration fields
    revenuecat_subscriber_id: str | None = None
    subscription_tier: SubscriptionTier = SubscriptionTier.TRIAL
    trial_start_date: datetime | None = None
    trial_end_date: datetime | None = None

    @field_validator('entitlement')
    @classmethod
    def validate_entitlement(cls, v: str) -> str:
        if not v or not v.strip():
            from ...utils.errors import BadRequest
            raise BadRequest('Entitlement cannot be empty')
        return v.strip()

    @field_validator('product_id')
    @classmethod
    def validate_product_id(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            from ...utils.errors import BadRequest
            raise BadRequest('Product ID cannot be empty')
        return v.strip() if v else None

    @field_validator('revenuecat_subscriber_id')
    @classmethod
    def validate_revenuecat_subscriber_id(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            from ...utils.errors import BadRequest
            raise BadRequest('RevenueCat subscriber ID cannot be empty')
        return v.strip() if v else None


class SubscriptionStatusUpdate(BaseModel):
    """DTO for subscription status updates."""
    entitlement: str | None = Field(None, min_length=1, max_length=50)
    platform: SubscriptionPlatform | None = None
    product_id: str | None = Field(None, max_length=255)
    will_renew: bool | None = None
    original_purchase_date: datetime | None = None
    expiration_date: datetime | None = None
    grace_period: bool | None = None
    trial: bool | None = None
    billing_issue: bool | None = None
    raw: dict[str, Any] | None = None
    # New RevenueCat integration fields
    revenuecat_subscriber_id: str | None = None
    subscription_tier: SubscriptionTier | None = None
    trial_start_date: datetime | None = None
    trial_end_date: datetime | None = None

    @field_validator('entitlement')
    @classmethod
    def validate_entitlement(cls, v: str | None) -> str | None:
        if v is not None and (not v or not v.strip()):
            from ...utils.errors import BadRequest
            raise BadRequest('Entitlement cannot be empty')
        return v.strip() if v else None

    @field_validator('product_id')
    @classmethod
    def validate_product_id(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            from ...utils.errors import BadRequest
            raise BadRequest('Product ID cannot be empty')
        return v.strip() if v else None

    @field_validator('revenuecat_subscriber_id')
    @classmethod
    def validate_revenuecat_subscriber_id(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            from ...utils.errors import BadRequest
            raise BadRequest('RevenueCat subscriber ID cannot be empty')
        return v.strip() if v else None


# Quota Usage models
class QuotaUsageOut(BaseModel):
    """DTO for quota usage output."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    quota_type: QuotaType
    date: date
    count: int = Field(ge=0)
    daily_limit: int = Field(gt=0)
    created_at: datetime
    updated_at: datetime


class QuotaUsageCreate(BaseModel):
    """DTO for creating quota usage."""
    user_id: UUID | None = None  # Optional, can be set from RLS context
    quota_type: QuotaType
    date: date
    count: int = Field(default=0, ge=0)
    daily_limit: int = Field(gt=0)


class QuotaUsageUpdate(BaseModel):
    """DTO for quota usage updates."""
    count: int | None = Field(None, ge=0)
    daily_limit: int | None = Field(None, gt=0)


# Purchase request models
class GooglePurchaseRequest(BaseModel):
    """Google Play purchase sync request."""
    purchase_token: str = Field(min_length=1, max_length=1000)
    product_id: str = Field(min_length=1, max_length=255)
    app_user_id: str = Field(min_length=1, max_length=255)

    @field_validator('purchase_token', 'product_id', 'app_user_id')
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            from ...utils.errors import BadRequest
            raise BadRequest('Field cannot be empty')
        return v.strip()


class ApplePurchaseRequest(BaseModel):
    """App Store purchase sync request."""
    transaction_id: str = Field(min_length=1, max_length=255)
    receipt_data: str = Field(min_length=1, max_length=10000)
    app_user_id: str = Field(min_length=1, max_length=255)

    @field_validator('transaction_id', 'receipt_data', 'app_user_id')
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            from ...utils.errors import BadRequest
            raise BadRequest('Field cannot be empty')
        return v.strip()


# RevenueCat webhook event models
class RevenueCatWebhookEventType(str, Enum):
    """RevenueCat webhook event types.
    
    See: https://www.revenuecat.com/docs/integrations/webhooks/event-types-and-fields
    """
    # Subscription lifecycle events
    INITIAL_PURCHASE = "INITIAL_PURCHASE"
    RENEWAL = "RENEWAL"
    CANCELLATION = "CANCELLATION"
    UNCANCELLATION = "UNCANCELLATION"
    NON_RENEWING_PURCHASE = "NON_RENEWING_PURCHASE"
    EXPIRATION = "EXPIRATION"

    # Billing and payment events
    BILLING_ISSUE = "BILLING_ISSUE"
    PRODUCT_CHANGE = "PRODUCT_CHANGE"

    # Refund events (critical for revenue tracking)
    REFUND = "REFUND"
    REFUND_REVERSED = "REFUND_REVERSED"

    # Subscription management (Android specific)
    SUBSCRIPTION_PAUSED = "SUBSCRIPTION_PAUSED"
    SUBSCRIPTION_EXTENDED = "SUBSCRIPTION_EXTENDED"

    # Transfer and test events
    TRANSFER = "TRANSFER"
    TEST = "TEST"


class RevenueCatWebhookEvent(BaseModel):
    """RevenueCat webhook event model.
    
    See: https://www.revenuecat.com/docs/integrations/webhooks/event-types-and-fields
    """
    api_version: str
    event: dict[str, Any]

    @property
    def event_id(self) -> str | None:
        """Get unique event ID (recommended for idempotency)."""
        return self.event.get("id")

    @property
    def event_type(self) -> str:
        """Get the event type."""
        return self.event.get("type", "")

    @property
    def app_user_id(self) -> str:
        """Get the app user ID."""
        return self.event.get("app_user_id", "")

    @property
    def original_app_user_id(self) -> str:
        """Get the original app user ID."""
        return self.event.get("original_app_user_id", "")

    @property
    def product_id(self) -> str | None:
        """Get the product ID."""
        return self.event.get("product_id")

    @property
    def period_type(self) -> str | None:
        """Get the period type (NORMAL, TRIAL, INTRO)."""
        return self.event.get("period_type")

    @property
    def purchased_at_ms(self) -> int | None:
        """Get the purchase timestamp in milliseconds."""
        return self.event.get("purchased_at_ms")

    @property
    def expiration_at_ms(self) -> int | None:
        """Get the expiration timestamp in milliseconds."""
        return self.event.get("expiration_at_ms")

    @property
    def event_timestamp_ms(self) -> int | None:
        """Get the event timestamp in milliseconds."""
        return self.event.get("event_timestamp_ms")

    @property
    def store(self) -> str | None:
        """Get the store (app_store, play_store, stripe, promotional)."""
        return self.event.get("store")

    @property
    def environment(self) -> str | None:
        """Get the environment (PRODUCTION, SANDBOX)."""
        return self.event.get("environment")

    @property
    def entitlement_ids(self) -> list[str]:
        """Get the entitlement IDs."""
        return self.event.get("entitlement_ids", [])

    @property
    def entitlement_id(self) -> str | None:
        """Get the first entitlement ID (for convenience)."""
        ids = self.entitlement_ids
        return ids[0] if ids else None

    @property
    def transaction_id(self) -> str | None:
        """Get the transaction ID."""
        return self.event.get("transaction_id")

    @property
    def original_transaction_id(self) -> str | None:
        """Get the original transaction ID."""
        return self.event.get("original_transaction_id")

    @property
    def is_trial_conversion(self) -> bool:
        """Check if this is a trial conversion."""
        return self.event.get("is_trial_conversion", False)

    @property
    def price_in_purchased_currency(self) -> float | None:
        """Get the price in purchased currency."""
        return self.event.get("price_in_purchased_currency")

    @property
    def currency(self) -> str | None:
        """Get the currency code."""
        return self.event.get("currency")

    @property
    def takehome_percentage(self) -> float | None:
        """Get the takehome percentage after store fees."""
        return self.event.get("takehome_percentage")

    @property
    def country_code(self) -> str | None:
        """Get the country code."""
        return self.event.get("country_code")

    @property
    def subscriber_attributes(self) -> dict[str, Any]:
        """Get subscriber attributes."""
        return self.event.get("subscriber_attributes", {})


class RevenueCatWebhookRequest(BaseModel):
    """RevenueCat webhook request model for validation."""
    api_version: str = Field(..., description="RevenueCat API version")
    event: dict[str, Any] = Field(..., description="Event data")

    @field_validator('event')
    @classmethod
    def validate_event(cls, v: dict[str, Any]) -> dict[str, Any]:
        """Validate event structure."""
        if not isinstance(v, dict):
            raise ValueError("Event must be a dictionary")

        required_fields = ["type", "app_user_id"]
        for field in required_fields:
            if field not in v:
                raise ValueError(f"Event missing required field: {field}")

        return v


class RevenueCatWebhookResponse(BaseModel):
    """RevenueCat webhook response model."""
    status: str = Field(default="received", description="Processing status")
    message: str = Field(default="Webhook received successfully", description="Response message")
    event_id: str | None = Field(None, description="Event ID for tracking")
    processed_at: datetime = Field(default_factory=lambda: datetime.utcnow(), description="Processing timestamp")


# Export table definitions for repository use
__all__ = [
    "SubscriptionPlatform", "SubscriptionTier", "QuotaType",
    "SubscriptionStatusOut", "SubscriptionStatusCreate", "SubscriptionStatusUpdate",
    "QuotaUsageOut", "QuotaUsageCreate", "QuotaUsageUpdate",
    "GooglePurchaseRequest", "ApplePurchaseRequest",
    "RevenueCatWebhookEventType", "RevenueCatWebhookEvent", "RevenueCatWebhookRequest", "RevenueCatWebhookResponse",
    "subscription_status_table", "quota_usage_table"
]
