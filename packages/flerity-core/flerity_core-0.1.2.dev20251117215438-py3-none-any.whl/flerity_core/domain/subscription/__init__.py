"""Subscription domain - Payment and subscription management."""

from .config import SubscriptionConfig, get_subscription_config, reload_subscription_config
from .quota_reset_task import QuotaResetTask, create_quota_reset_task
from .quota_service import QuotaService, QuotaStatus, create_quota_service
from .revenuecat_client import (
    RevenueCatClient,
    create_revenuecat_client,
    create_revenuecat_client_from_config,
)
from .schemas import QuotaType, QuotaUsageCreate, QuotaUsageOut, QuotaUsageUpdate, SubscriptionTier
from .service import (
    SubscriptionService,
    create_subscription_service,
    create_subscription_service_with_revenuecat,
)

__all__ = [
    # Configuration
    "SubscriptionConfig",
    "get_subscription_config",
    "reload_subscription_config",
    # Services
    "QuotaService",
    "QuotaStatus",
    "QuotaResetTask",
    "SubscriptionService",
    # RevenueCat
    "RevenueCatClient",
    "create_revenuecat_client",
    "create_revenuecat_client_from_config",
    # Schemas
    "QuotaType",
    "SubscriptionTier",
    "QuotaUsageOut",
    "QuotaUsageCreate",
    "QuotaUsageUpdate",
    # Factory functions
    "create_quota_service",
    "create_quota_reset_task",
    "create_subscription_service",
    "create_subscription_service_with_revenuecat",
]
