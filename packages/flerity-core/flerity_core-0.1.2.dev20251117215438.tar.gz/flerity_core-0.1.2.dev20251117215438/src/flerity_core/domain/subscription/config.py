"""Configuration management for subscription system."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .schemas import QuotaType, SubscriptionTier


class SubscriptionConfig(BaseSettings):
    """Subscription system configuration settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # RevenueCat Integration Settings
    revenuecat_api_key: str = Field(
        default="",
        description="RevenueCat API key for subscription management"
    )

    revenuecat_webhook_secret: str | None = Field(
        default=None,
        description="RevenueCat webhook secret for signature validation"
    )

    revenuecat_base_url: str = Field(
        default="https://api.revenuecat.com/v1",
        description="RevenueCat API base URL"
    )

    revenuecat_timeout: int = Field(
        default=30,
        description="RevenueCat API request timeout in seconds"
    )

    # RevenueCat App Configuration
    revenuecat_app_id: str | None = Field(
        default=None,
        description="RevenueCat app identifier"
    )

    revenuecat_product_ids: str = Field(
        default="flerity_premium_monthly,flerity_premium_yearly",
        description="Comma-separated list of RevenueCat product IDs"
    )

    # Trial Configuration
    trial_duration_days: int = Field(
        default=15,
        description="Duration of trial period in days"
    )

    # Paid Subscription Configuration
    paid_renewal_period_days: int = Field(
        default=30,
        description="Duration of paid subscription renewal period in days"
    )

    # Quota Limits Configuration
    # Trial tier limits
    trial_icebreaker_limit: int = Field(
        default=10,
        description="Daily icebreaker limit per thread for trial users"
    )

    trial_suggestion_limit: int = Field(
        default=10,
        description="Daily suggestion limit per thread for trial users"
    )

    trial_thread_limit: int = Field(
        default=3,
        description="Maximum number of threads for trial users"
    )

    # Paid tier limits
    paid_icebreaker_limit: int = Field(
        default=50,
        description="Daily icebreaker limit total for paid users"
    )

    paid_suggestion_limit: int = Field(
        default=50,
        description="Daily suggestion limit total for paid users"
    )

    paid_thread_limit: int = Field(
        default=-1,
        description="Maximum number of threads for paid users (-1 = unlimited)"
    )

    # Redis Cache Configuration
    subscription_cache_ttl: int = Field(
        default=300,
        description="Subscription status cache TTL in seconds (5 minutes)"
    )

    entitlement_cache_ttl: int = Field(
        default=300,
        description="Entitlement cache TTL in seconds (5 minutes)"
    )

    quota_cache_ttl: int = Field(
        default=86400,
        description="Quota usage cache TTL in seconds (24 hours)"
    )

    # Feature Flags
    enable_subscription_enforcement: bool = Field(
        default=True,
        description="Enable subscription limit enforcement"
    )

    enable_quota_enforcement: bool = Field(
        default=True,
        description="Enable quota limit enforcement"
    )

    enable_revenuecat_sync: bool = Field(
        default=True,
        description="Enable RevenueCat synchronization"
    )

    enable_webhook_processing: bool = Field(
        default=True,
        description="Enable RevenueCat webhook processing"
    )

    enable_trial_auto_creation: bool = Field(
        default=True,
        description="Automatically create trial subscriptions for new users"
    )

    # Background Task Configuration
    quota_reset_schedule: str = Field(
        default="0 0 * * *",
        description="Cron schedule for daily quota reset (default: midnight UTC)"
    )

    subscription_sync_schedule: str = Field(
        default="0 */6 * * *",
        description="Cron schedule for RevenueCat sync (default: every 6 hours)"
    )

    # Database Optimization Configuration
    quota_data_retention_days: int = Field(
        default=90,
        description="Number of days to retain quota usage data"
    )

    enable_quota_partitioning: bool = Field(
        default=True,
        description="Enable table partitioning for quota_usage table"
    )

    # Monitoring and Alerting
    enable_subscription_metrics: bool = Field(
        default=True,
        description="Enable subscription metrics collection"
    )

    enable_quota_metrics: bool = Field(
        default=True,
        description="Enable quota usage metrics collection"
    )

    alert_on_revenuecat_failures: bool = Field(
        default=True,
        description="Send alerts on RevenueCat API failures"
    )

    alert_on_quota_exceeded: bool = Field(
        default=False,
        description="Send alerts when users exceed quotas"
    )

    # A/B Testing Configuration
    trial_duration_variant_enabled: bool = Field(
        default=False,
        description="Enable A/B testing for trial duration"
    )

    trial_duration_variant_days: int = Field(
        default=30,
        description="Alternative trial duration for A/B testing"
    )

    trial_duration_variant_percentage: int = Field(
        default=50,
        description="Percentage of users in trial duration variant (0-100)"
    )

    def get_quota_limits(self, tier: SubscriptionTier) -> dict[QuotaType, int]:
        """Get quota limits for a subscription tier.
        
        Args:
            tier: Subscription tier
            
        Returns:
            Dictionary mapping quota types to limits
        """
        if tier == SubscriptionTier.TRIAL:
            return {
                QuotaType.ICEBREAKER: self.trial_icebreaker_limit,
                QuotaType.SUGGESTION: self.trial_suggestion_limit,
                QuotaType.THREAD: self.trial_thread_limit,
            }
        elif tier == SubscriptionTier.PAID:
            return {
                QuotaType.ICEBREAKER: self.paid_icebreaker_limit,
                QuotaType.SUGGESTION: self.paid_suggestion_limit,
                QuotaType.THREAD: self.paid_thread_limit,
            }
        else:
            # Default to trial limits for unknown tiers
            return {
                QuotaType.ICEBREAKER: self.trial_icebreaker_limit,
                QuotaType.SUGGESTION: self.trial_suggestion_limit,
                QuotaType.THREAD: self.trial_thread_limit,
            }

    def get_product_ids(self) -> list[str]:
        """Get list of RevenueCat product IDs.
        
        Returns:
            List of product ID strings
        """
        if not self.revenuecat_product_ids:
            return []
        return [pid.strip() for pid in self.revenuecat_product_ids.split(",") if pid.strip()]

    def is_subscription_enforcement_enabled(self) -> bool:
        """Check if subscription enforcement is enabled.
        
        Returns:
            True if enforcement is enabled
        """
        return self.enable_subscription_enforcement

    def is_quota_enforcement_enabled(self) -> bool:
        """Check if quota enforcement is enabled.
        
        Returns:
            True if enforcement is enabled
        """
        return self.enable_quota_enforcement

    def is_revenuecat_configured(self) -> bool:
        """Check if RevenueCat is properly configured.
        
        Returns:
            True if API key is set
        """
        return bool(self.revenuecat_api_key and self.revenuecat_api_key.strip())

    def should_create_trial_for_new_users(self) -> bool:
        """Check if trial subscriptions should be auto-created.
        
        Returns:
            True if auto-creation is enabled
        """
        return self.enable_trial_auto_creation


# Global configuration instance
subscription_config = SubscriptionConfig()


def get_subscription_config() -> SubscriptionConfig:
    """Get the global subscription configuration instance.
    
    Returns:
        SubscriptionConfig instance
    """
    return subscription_config


def reload_subscription_config() -> SubscriptionConfig:
    """Reload subscription configuration from environment.
    
    Returns:
        New SubscriptionConfig instance
    """
    global subscription_config
    subscription_config = SubscriptionConfig()
    return subscription_config
