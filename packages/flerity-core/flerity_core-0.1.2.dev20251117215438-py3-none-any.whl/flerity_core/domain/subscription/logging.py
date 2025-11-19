"""Structured logging utilities for subscription system operations."""

import logging
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from ...utils.logging import get_logger, log_event, record_with_context
from .schemas import QuotaType, SubscriptionTier


class SubscriptionLogger:
    """Structured logger for subscription operations with audit trail."""

    def __init__(self, component: str = "subscription", service: str = "flerity"):
        """Initialize the subscription logger.
        
        Args:
            component: Component name for logging context
            service: Service name for logging context
        """
        self.component = component
        self.service = service
        self.logger = get_logger(f"{service}.{component}")

    def _base_extra(self, **kwargs: Any) -> dict[str, Any]:
        """Create base extra fields for structured logging.
        
        Args:
            **kwargs: Additional fields to include
            
        Returns:
            Dictionary with base logging fields
        """
        extra = {
            "service": self.service,
            "component": self.component,
            "timestamp": datetime.now(UTC).isoformat(),
        }
        extra.update(kwargs)
        return record_with_context(extra)

    # Subscription Status Logging

    def subscription_created(
        self,
        user_id: UUID,
        tier: SubscriptionTier,
        entitlement: str,
        trial: bool = False,
        trial_end_date: datetime | None = None
    ) -> None:
        """Log subscription creation event."""
        log_event(
            self.logger,
            "subscription_created",
            **self._base_extra(
                user_id=str(user_id),
                subscription_tier=tier.value,
                entitlement=entitlement,
                trial=trial,
                trial_end_date=trial_end_date.isoformat() if trial_end_date else None,
                action="subscription_created"
            )
        )

    def subscription_updated(
        self,
        user_id: UUID,
        old_tier: SubscriptionTier | None,
        new_tier: SubscriptionTier,
        old_entitlement: str | None,
        new_entitlement: str,
        reason: str = "manual_update"
    ) -> None:
        """Log subscription update event."""
        log_event(
            self.logger,
            "subscription_updated",
            **self._base_extra(
                user_id=str(user_id),
                old_tier=old_tier.value if old_tier else None,
                new_tier=new_tier.value,
                old_entitlement=old_entitlement,
                new_entitlement=new_entitlement,
                reason=reason,
                action="subscription_updated"
            )
        )

    def subscription_deleted(self, user_id: UUID, reason: str = "user_request") -> None:
        """Log subscription deletion event."""
        log_event(
            self.logger,
            "subscription_deleted",
            **self._base_extra(
                user_id=str(user_id),
                reason=reason,
                action="subscription_deleted"
            )
        )

    def subscription_synced_with_revenuecat(
        self,
        user_id: UUID,
        revenuecat_subscriber_id: str,
        sync_result: str,
        entitlements_count: int = 0
    ) -> None:
        """Log RevenueCat synchronization event."""
        log_event(
            self.logger,
            "subscription_synced_revenuecat",
            **self._base_extra(
                user_id=str(user_id),
                revenuecat_subscriber_id=revenuecat_subscriber_id,
                sync_result=sync_result,
                entitlements_count=entitlements_count,
                action="revenuecat_sync"
            )
        )

    def subscription_cache_hit(self, user_id: UUID, cache_key: str) -> None:
        """Log subscription cache hit."""
        self.logger.debug(
            "Subscription cache hit",
            extra=self._base_extra(
                user_id=str(user_id),
                cache_key=cache_key,
                action="cache_hit"
            )
        )

    def subscription_cache_miss(self, user_id: UUID, cache_key: str) -> None:
        """Log subscription cache miss."""
        self.logger.debug(
            "Subscription cache miss",
            extra=self._base_extra(
                user_id=str(user_id),
                cache_key=cache_key,
                action="cache_miss"
            )
        )

    def subscription_cache_invalidated(self, user_id: UUID, keys_deleted: int) -> None:
        """Log subscription cache invalidation."""
        self.logger.info(
            "Subscription cache invalidated",
            extra=self._base_extra(
                user_id=str(user_id),
                keys_deleted=keys_deleted,
                action="cache_invalidated"
            )
        )

    # Trial Management Logging

    def trial_created(
        self,
        user_id: UUID,
        trial_start_date: datetime,
        trial_end_date: datetime,
        trial_duration_days: int
    ) -> None:
        """Log trial subscription creation."""
        log_event(
            self.logger,
            "trial_created",
            **self._base_extra(
                user_id=str(user_id),
                trial_start_date=trial_start_date.isoformat(),
                trial_end_date=trial_end_date.isoformat(),
                trial_duration_days=trial_duration_days,
                action="trial_created"
            )
        )

    def trial_upgraded_to_paid(
        self,
        user_id: UUID,
        revenuecat_subscriber_id: str,
        product_id: str | None = None
    ) -> None:
        """Log trial to paid upgrade."""
        log_event(
            self.logger,
            "trial_upgraded_to_paid",
            **self._base_extra(
                user_id=str(user_id),
                revenuecat_subscriber_id=revenuecat_subscriber_id,
                product_id=product_id,
                action="trial_upgrade"
            )
        )

    def trial_expired(self, user_id: UUID, trial_end_date: datetime) -> None:
        """Log trial expiration."""
        log_event(
            self.logger,
            "trial_expired",
            **self._base_extra(
                user_id=str(user_id),
                trial_end_date=trial_end_date.isoformat(),
                action="trial_expired"
            )
        )

    def trial_extended(
        self,
        user_id: UUID,
        old_end_date: datetime,
        new_end_date: datetime,
        additional_days: int,
        reason: str = "manual_extension"
    ) -> None:
        """Log trial period extension."""
        log_event(
            self.logger,
            "trial_extended",
            **self._base_extra(
                user_id=str(user_id),
                old_end_date=old_end_date.isoformat(),
                new_end_date=new_end_date.isoformat(),
                additional_days=additional_days,
                reason=reason,
                action="trial_extended"
            )
        )

    # Quota Usage Logging

    def quota_checked(
        self,
        user_id: UUID,
        quota_type: QuotaType,
        current_usage: int,
        limit: int,
        remaining: int,
        is_exceeded: bool,
        thread_id: UUID | None = None,
        tier: SubscriptionTier | None = None
    ) -> None:
        """Log quota check operation."""
        self.logger.debug(
            "Quota checked",
            extra=self._base_extra(
                user_id=str(user_id),
                quota_type=quota_type.value,
                current_usage=current_usage,
                limit=limit,
                remaining=remaining,
                is_exceeded=is_exceeded,
                thread_id=str(thread_id) if thread_id else None,
                subscription_tier=tier.value if tier else None,
                action="quota_checked"
            )
        )

    def quota_incremented(
        self,
        user_id: UUID,
        quota_type: QuotaType,
        amount: int,
        new_usage: int,
        limit: int,
        thread_id: UUID | None = None,
        tier: SubscriptionTier | None = None
    ) -> None:
        """Log quota usage increment."""
        log_event(
            self.logger,
            "quota_incremented",
            **self._base_extra(
                user_id=str(user_id),
                quota_type=quota_type.value,
                increment_amount=amount,
                new_usage=new_usage,
                limit=limit,
                thread_id=str(thread_id) if thread_id else None,
                subscription_tier=tier.value if tier else None,
                action="quota_incremented"
            )
        )

    def quota_exceeded(
        self,
        user_id: UUID,
        quota_type: QuotaType,
        current_usage: int,
        limit: int,
        thread_id: UUID | None = None,
        tier: SubscriptionTier | None = None
    ) -> None:
        """Log quota limit violation."""
        self.logger.warning(
            "Quota limit exceeded",
            extra=self._base_extra(
                user_id=str(user_id),
                quota_type=quota_type.value,
                current_usage=current_usage,
                limit=limit,
                thread_id=str(thread_id) if thread_id else None,
                subscription_tier=tier.value if tier else None,
                action="quota_exceeded",
                severity="warning"
            )
        )

    def quota_reset(
        self,
        user_id: UUID | None = None,
        quota_type: QuotaType | None = None,
        reset_count: int = 0,
        reset_scope: str = "daily"
    ) -> None:
        """Log quota reset operation."""
        log_event(
            self.logger,
            "quota_reset",
            **self._base_extra(
                user_id=str(user_id) if user_id else None,
                quota_type=quota_type.value if quota_type else None,
                reset_count=reset_count,
                reset_scope=reset_scope,
                action="quota_reset"
            )
        )

    # RevenueCat Webhook Logging

    def webhook_received(
        self,
        event_type: str,
        app_user_id: str,
        event_id: str,
        product_id: str | None = None
    ) -> None:
        """Log RevenueCat webhook event received."""
        log_event(
            self.logger,
            "revenuecat_webhook_received",
            **self._base_extra(
                event_type=event_type,
                app_user_id=app_user_id,
                event_id=event_id,
                product_id=product_id,
                action="webhook_received"
            )
        )

    def webhook_processed(
        self,
        event_type: str,
        app_user_id: str,
        event_id: str,
        processing_result: str,
        processing_time_ms: float | None = None
    ) -> None:
        """Log RevenueCat webhook event processed."""
        log_event(
            self.logger,
            "revenuecat_webhook_processed",
            **self._base_extra(
                event_type=event_type,
                app_user_id=app_user_id,
                event_id=event_id,
                processing_result=processing_result,
                processing_time_ms=processing_time_ms,
                action="webhook_processed"
            )
        )

    def webhook_duplicate(
        self,
        event_type: str,
        app_user_id: str,
        event_id: str
    ) -> None:
        """Log duplicate RevenueCat webhook event."""
        self.logger.info(
            "Duplicate RevenueCat webhook event ignored",
            extra=self._base_extra(
                event_type=event_type,
                app_user_id=app_user_id,
                event_id=event_id,
                action="webhook_duplicate"
            )
        )

    def webhook_signature_invalid(
        self,
        payload_length: int,
        signature_provided: bool
    ) -> None:
        """Log invalid webhook signature."""
        self.logger.error(
            "Invalid RevenueCat webhook signature",
            extra=self._base_extra(
                payload_length=payload_length,
                signature_provided=signature_provided,
                action="webhook_signature_invalid",
                severity="error"
            )
        )

    def webhook_parsing_failed(
        self,
        payload_length: int,
        error_message: str
    ) -> None:
        """Log webhook parsing failure."""
        self.logger.error(
            "Failed to parse RevenueCat webhook",
            extra=self._base_extra(
                payload_length=payload_length,
                error_message=error_message,
                action="webhook_parsing_failed",
                severity="error"
            )
        )

    # Feature Entitlement Logging

    def feature_entitlement_checked(
        self,
        user_id: UUID,
        feature: str,
        is_enabled: bool,
        entitlement: str,
        tier: SubscriptionTier,
        cache_hit: bool = False
    ) -> None:
        """Log feature entitlement check."""
        self.logger.debug(
            "Feature entitlement checked",
            extra=self._base_extra(
                user_id=str(user_id),
                feature=feature,
                is_enabled=is_enabled,
                entitlement=entitlement,
                subscription_tier=tier.value,
                cache_hit=cache_hit,
                action="feature_entitlement_checked"
            )
        )

    def feature_access_denied(
        self,
        user_id: UUID,
        feature: str,
        required_entitlements: list[str],
        current_entitlement: str,
        tier: SubscriptionTier
    ) -> None:
        """Log feature access denial."""
        self.logger.warning(
            "Feature access denied",
            extra=self._base_extra(
                user_id=str(user_id),
                feature=feature,
                required_entitlements=required_entitlements,
                current_entitlement=current_entitlement,
                subscription_tier=tier.value,
                action="feature_access_denied",
                severity="warning"
            )
        )

    # Error and Exception Logging

    def subscription_error(
        self,
        operation: str,
        error: Exception,
        user_id: UUID | None = None,
        context: dict[str, Any] | None = None
    ) -> None:
        """Log subscription operation error."""
        extra = self._base_extra(
            operation=operation,
            error_type=type(error).__name__,
            error_message=str(error),
            user_id=str(user_id) if user_id else None,
            action="subscription_error",
            severity="error"
        )

        if context:
            extra.update(context)

        self.logger.error(
            f"Subscription operation failed: {operation}",
            extra=extra,
            exc_info=error
        )

    def revenuecat_api_error(
        self,
        operation: str,
        error: Exception,
        user_id: UUID | None = None,
        retry_count: int = 0
    ) -> None:
        """Log RevenueCat API error."""
        self.logger.error(
            f"RevenueCat API error: {operation}",
            extra=self._base_extra(
                operation=operation,
                error_type=type(error).__name__,
                error_message=str(error),
                user_id=str(user_id) if user_id else None,
                retry_count=retry_count,
                action="revenuecat_api_error",
                severity="error"
            ),
            exc_info=error
        )

    def quota_service_error(
        self,
        operation: str,
        error: Exception,
        user_id: UUID | None = None,
        quota_type: QuotaType | None = None
    ) -> None:
        """Log quota service error."""
        self.logger.error(
            f"Quota service error: {operation}",
            extra=self._base_extra(
                operation=operation,
                error_type=type(error).__name__,
                error_message=str(error),
                user_id=str(user_id) if user_id else None,
                quota_type=quota_type.value if quota_type else None,
                action="quota_service_error",
                severity="error"
            ),
            exc_info=error
        )

    # Performance and Monitoring Logging

    def operation_performance(
        self,
        operation: str,
        duration_ms: float,
        user_id: UUID | None = None,
        success: bool = True,
        cache_hit: bool = False
    ) -> None:
        """Log operation performance metrics."""
        level = logging.DEBUG if duration_ms < 100 else logging.INFO
        if duration_ms > 1000:  # Log slow operations as warnings
            level = logging.WARNING

        self.logger.log(
            level,
            f"Subscription operation performance: {operation}",
            extra=self._base_extra(
                operation=operation,
                duration_ms=duration_ms,
                user_id=str(user_id) if user_id else None,
                success=success,
                cache_hit=cache_hit,
                action="operation_performance"
            )
        )

    def bulk_operation_completed(
        self,
        operation: str,
        total_items: int,
        successful_items: int,
        failed_items: int,
        duration_ms: float
    ) -> None:
        """Log bulk operation completion."""
        log_event(
            self.logger,
            "bulk_operation_completed",
            **self._base_extra(
                operation=operation,
                total_items=total_items,
                successful_items=successful_items,
                failed_items=failed_items,
                success_rate=round((successful_items / total_items) * 100, 2) if total_items > 0 else 0,
                duration_ms=duration_ms,
                action="bulk_operation_completed"
            )
        )

    # Database and Cache Logging

    def database_query_slow(
        self,
        query_type: str,
        duration_ms: float,
        table: str,
        user_id: UUID | None = None
    ) -> None:
        """Log slow database query."""
        self.logger.warning(
            f"Slow database query: {query_type}",
            extra=self._base_extra(
                query_type=query_type,
                duration_ms=duration_ms,
                table=table,
                user_id=str(user_id) if user_id else None,
                action="database_query_slow",
                severity="warning"
            )
        )

    def cache_operation(
        self,
        operation: str,
        cache_key: str,
        success: bool,
        duration_ms: float | None = None,
        error: str | None = None
    ) -> None:
        """Log cache operation."""
        level = logging.DEBUG if success else logging.WARNING

        self.logger.log(
            level,
            f"Cache operation: {operation}",
            extra=self._base_extra(
                operation=operation,
                cache_key=cache_key,
                success=success,
                duration_ms=duration_ms,
                error=error,
                action="cache_operation"
            )
        )

    # Audit Trail Logging

    def audit_subscription_change(
        self,
        user_id: UUID,
        change_type: str,
        old_values: dict[str, Any],
        new_values: dict[str, Any],
        changed_by: str | None = None,
        reason: str | None = None
    ) -> None:
        """Log subscription change for audit trail."""
        log_event(
            self.logger,
            "subscription_audit_change",
            **self._base_extra(
                user_id=str(user_id),
                change_type=change_type,
                old_values=old_values,
                new_values=new_values,
                changed_by=changed_by,
                reason=reason,
                action="audit_change"
            )
        )

    def audit_quota_adjustment(
        self,
        user_id: UUID,
        quota_type: QuotaType,
        adjustment_type: str,
        old_usage: int,
        new_usage: int,
        adjusted_by: str | None = None,
        reason: str | None = None
    ) -> None:
        """Log quota adjustment for audit trail."""
        log_event(
            self.logger,
            "quota_audit_adjustment",
            **self._base_extra(
                user_id=str(user_id),
                quota_type=quota_type.value,
                adjustment_type=adjustment_type,
                old_usage=old_usage,
                new_usage=new_usage,
                adjusted_by=adjusted_by,
                reason=reason,
                action="audit_adjustment"
            )
        )


# Global logger instances
subscription_logger = SubscriptionLogger("subscription")
quota_logger = SubscriptionLogger("quota")
webhook_logger = SubscriptionLogger("webhook")
