"""
Comprehensive metrics collection for subscription system observability.
"""
import time
from contextlib import contextmanager
from typing import Any
from uuid import UUID

try:
    from prometheus_client import Counter, Gauge, Histogram, Info
    PROMETHEUS_AVAILABLE = True
except ImportError:
    # Placeholder classes for when prometheus_client is not available
    PROMETHEUS_AVAILABLE = False

    class MockCounter:
        def __init__(self, *args: Any, **kwargs: Any) -> None: pass
        def inc(self, *args: Any, **kwargs: Any) -> None: pass
        def labels(self, *args: Any, **kwargs: Any) -> 'MockCounter': return self

    class MockHistogram:
        def __init__(self, *args: Any, **kwargs: Any) -> None: pass
        def observe(self, *args: Any, **kwargs: Any) -> None: pass
        def labels(self, *args: Any, **kwargs: Any) -> 'MockHistogram': return self

    class MockGauge:
        def __init__(self, *args: Any, **kwargs: Any) -> None: pass
        def set(self, *args: Any, **kwargs: Any) -> None: pass
        def inc(self, *args: Any, **kwargs: Any) -> None: pass
        def dec(self, *args: Any, **kwargs: Any) -> None: pass
        def labels(self, *args: Any, **kwargs: Any) -> 'MockGauge': return self

    class MockInfo:
        def __init__(self, *args: Any, **kwargs: Any) -> None: pass
        def info(self, *args: Any, **kwargs: Any) -> None: pass

    Counter = MockCounter
    Histogram = MockHistogram
    Gauge = MockGauge
    Info = MockInfo

from ...utils.logging import get_logger
from .schemas import QuotaType, SubscriptionTier

logger = get_logger(__name__)


class SubscriptionMetrics:
    """Centralized metrics collection for subscription system."""

    def __init__(self) -> None:
        # Business Metrics - Subscription Management
        self.subscription_status_changes = Counter(
            "subscription_status_changes_total",
            "Total subscription status changes",
            ["from_tier", "to_tier", "change_type", "source"]
        )

        self.active_subscriptions = Gauge(
            "subscription_active_total",
            "Current number of active subscriptions",
            ["tier", "entitlement"]
        )

        self.trial_conversions = Counter(
            "subscription_trial_conversions_total",
            "Trial to paid conversions",
            ["conversion_type", "product_id"]
        )

        self.subscription_churn = Counter(
            "subscription_churn_total",
            "Subscription cancellations and expirations",
            ["churn_type", "tier", "reason"]
        )

        # Business Metrics - Revenue Tracking
        self.revenue_events = Counter(
            "subscription_revenue_events_total",
            "Revenue-related events",
            ["event_type", "product_id", "platform"]
        )

        self.subscription_lifetime_value = Histogram(
            "subscription_lifetime_value_days",
            "Subscription lifetime in days",
            ["tier", "churn_reason"],
            buckets=[1, 7, 14, 30, 60, 90, 180, 365, float("inf")]
        )

        # Business Metrics - Usage Patterns
        self.quota_usage_patterns = Histogram(
            "subscription_quota_usage_ratio",
            "Quota usage as ratio of limit",
            ["quota_type", "tier"],
            buckets=[0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 1.0, float("inf")]
        )

        self.quota_violations = Counter(
            "subscription_quota_violations_total",
            "Quota limit violations",
            ["quota_type", "tier", "violation_type"]
        )

        self.feature_usage = Counter(
            "subscription_feature_usage_total",
            "Feature usage by subscription tier",
            ["feature", "tier", "access_granted"]
        )

        # Technical Metrics - Performance
        self.operation_duration = Histogram(
            "subscription_operation_duration_seconds",
            "Duration of subscription operations",
            ["operation", "success", "cache_hit"],
            buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
        )

        self.database_query_duration = Histogram(
            "subscription_database_query_duration_seconds",
            "Database query duration",
            ["query_type", "table"],
            buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
        )

        self.cache_operations = Counter(
            "subscription_cache_operations_total",
            "Cache operations",
            ["operation", "result", "cache_type"]
        )

        self.cache_hit_rate = Gauge(
            "subscription_cache_hit_rate",
            "Cache hit rate percentage",
            ["cache_type"]
        )

        # Technical Metrics - RevenueCat Integration
        self.revenuecat_api_calls = Counter(
            "subscription_revenuecat_api_calls_total",
            "RevenueCat API calls",
            ["operation", "status_code", "success"]
        )

        self.revenuecat_api_duration = Histogram(
            "subscription_revenuecat_api_duration_seconds",
            "RevenueCat API call duration",
            ["operation", "success"],
            buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0]
        )

        self.webhook_events = Counter(
            "subscription_webhook_events_total",
            "RevenueCat webhook events",
            ["event_type", "processing_result"]
        )

        self.webhook_processing_duration = Histogram(
            "subscription_webhook_processing_duration_seconds",
            "Webhook processing duration",
            ["event_type", "success"],
            buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
        )

        # Technical Metrics - Error Tracking
        self.errors = Counter(
            "subscription_errors_total",
            "Subscription system errors",
            ["error_type", "component", "operation"]
        )

        self.revenuecat_sync_failures = Counter(
            "subscription_revenuecat_sync_failures_total",
            "RevenueCat synchronization failures",
            ["failure_type", "retry_count"]
        )

        # System Health Metrics
        self.quota_cache_size = Gauge(
            "subscription_quota_cache_size",
            "Number of quota entries in cache"
        )

        self.subscription_cache_size = Gauge(
            "subscription_cache_size",
            "Number of subscription entries in cache"
        )

        self.background_task_duration = Histogram(
            "subscription_background_task_duration_seconds",
            "Background task execution duration",
            ["task_name", "success"],
            buckets=[1.0, 5.0, 10.0, 30.0, 60.0, 300.0, 600.0]
        )

        # System Information
        self.system_info = Info(
            "subscription_system_info",
            "Subscription system information"
        )

    def record_subscription_status_change(
        self,
        from_tier: SubscriptionTier | None,
        to_tier: SubscriptionTier,
        change_type: str,
        source: str = "api"
    ) -> None:
        """Record subscription status change."""
        self.subscription_status_changes.labels(
            from_tier=from_tier.value if from_tier else "none",
            to_tier=to_tier.value,
            change_type=change_type,
            source=source
        ).inc()

    def update_active_subscriptions(
        self,
        tier: SubscriptionTier,
        entitlement: str,
        count: int
    ) -> None:
        """Update active subscription count."""
        self.active_subscriptions.labels(
            tier=tier.value,
            entitlement=entitlement
        ).set(count)

    def record_trial_conversion(
        self,
        conversion_type: str,
        product_id: str
    ) -> None:
        """Record trial to paid conversion."""
        self.trial_conversions.labels(
            conversion_type=conversion_type,
            product_id=product_id
        ).inc()

    def record_subscription_churn(
        self,
        churn_type: str,
        tier: SubscriptionTier,
        reason: str
    ) -> None:
        """Record subscription churn event."""
        self.subscription_churn.labels(
            churn_type=churn_type,
            tier=tier.value,
            reason=reason
        ).inc()

    def record_revenue_event(
        self,
        event_type: str,
        product_id: str,
        platform: str
    ) -> None:
        """Record revenue-related event."""
        self.revenue_events.labels(
            event_type=event_type,
            product_id=product_id,
            platform=platform
        ).inc()

    def record_subscription_lifetime(
        self,
        lifetime_days: int,
        tier: SubscriptionTier,
        churn_reason: str
    ) -> None:
        """Record subscription lifetime value."""
        self.subscription_lifetime_value.labels(
            tier=tier.value,
            churn_reason=churn_reason
        ).observe(lifetime_days)

    def record_quota_usage_pattern(
        self,
        quota_type: QuotaType,
        tier: SubscriptionTier,
        usage_ratio: float
    ) -> None:
        """Record quota usage pattern."""
        self.quota_usage_patterns.labels(
            quota_type=quota_type.value,
            tier=tier.value
        ).observe(usage_ratio)

    def record_quota_violation(
        self,
        quota_type: QuotaType,
        tier: SubscriptionTier,
        violation_type: str
    ) -> None:
        """Record quota violation."""
        self.quota_violations.labels(
            quota_type=quota_type.value,
            tier=tier.value,
            violation_type=violation_type
        ).inc()

    def record_feature_usage(
        self,
        feature: str,
        tier: SubscriptionTier,
        access_granted: bool
    ) -> None:
        """Record feature usage attempt."""
        self.feature_usage.labels(
            feature=feature,
            tier=tier.value,
            access_granted=str(access_granted).lower()
        ).inc()

    def record_operation_duration(
        self,
        operation: str,
        duration: float,
        success: bool,
        cache_hit: bool = False
    ) -> None:
        """Record operation duration."""
        self.operation_duration.labels(
            operation=operation,
            success=str(success).lower(),
            cache_hit=str(cache_hit).lower()
        ).observe(duration)

    def record_database_query(
        self,
        query_type: str,
        table: str,
        duration: float
    ) -> None:
        """Record database query metrics."""
        self.database_query_duration.labels(
            query_type=query_type,
            table=table
        ).observe(duration)

    def record_cache_operation(
        self,
        operation: str,
        result: str,
        cache_type: str = "redis"
    ) -> None:
        """Record cache operation."""
        self.cache_operations.labels(
            operation=operation,
            result=result,
            cache_type=cache_type
        ).inc()

    def update_cache_hit_rate(
        self,
        cache_type: str,
        hit_rate_percentage: float
    ) -> None:
        """Update cache hit rate."""
        self.cache_hit_rate.labels(
            cache_type=cache_type
        ).set(hit_rate_percentage)

    def record_revenuecat_api_call(
        self,
        operation: str,
        status_code: int,
        duration: float,
        success: bool
    ) -> None:
        """Record RevenueCat API call metrics."""
        self.revenuecat_api_calls.labels(
            operation=operation,
            status_code=str(status_code),
            success=str(success).lower()
        ).inc()

        self.revenuecat_api_duration.labels(
            operation=operation,
            success=str(success).lower()
        ).observe(duration)

    def record_webhook_event(
        self,
        event_type: str,
        processing_result: str,
        processing_duration: float
    ) -> None:
        """Record webhook event processing."""
        self.webhook_events.labels(
            event_type=event_type,
            processing_result=processing_result
        ).inc()

        self.webhook_processing_duration.labels(
            event_type=event_type,
            success=str(processing_result == "success").lower()
        ).observe(processing_duration)

    def record_error(
        self,
        error_type: str,
        component: str,
        operation: str
    ) -> None:
        """Record error occurrence."""
        self.errors.labels(
            error_type=error_type,
            component=component,
            operation=operation
        ).inc()

    def record_revenuecat_sync_failure(
        self,
        failure_type: str,
        retry_count: int
    ) -> None:
        """Record RevenueCat sync failure."""
        self.revenuecat_sync_failures.labels(
            failure_type=failure_type,
            retry_count=str(retry_count)
        ).inc()

    def update_quota_cache_size(self, size: int) -> None:
        """Update quota cache size."""
        self.quota_cache_size.set(size)

    def update_subscription_cache_size(self, size: int) -> None:
        """Update subscription cache size."""
        self.subscription_cache_size.set(size)

    def record_background_task(
        self,
        task_name: str,
        duration: float,
        success: bool
    ) -> None:
        """Record background task execution."""
        self.background_task_duration.labels(
            task_name=task_name,
            success=str(success).lower()
        ).observe(duration)

    def update_system_info(self, info: dict[str, str]) -> None:
        """Update system information."""
        self.system_info.info(info)


class SubscriptionMetricsCollector:
    """Context manager for collecting metrics during subscription operations."""

    def __init__(self, metrics: SubscriptionMetrics, operation: str):
        self.metrics = metrics
        self.operation = operation
        self.start_time: float | None = None
        self.context: dict[str, Any] = {}
        self.success = True
        self.cache_hit = False

    def __enter__(self) -> 'SubscriptionMetricsCollector':
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type: type | None, _exc_val: Exception | None, exc_tb: Any | None) -> None:
        if self.start_time is not None:
            duration = time.time() - self.start_time

            # Record operation duration
            self.metrics.record_operation_duration(
                operation=self.operation,
                duration=duration,
                success=self.success and exc_type is None,
                cache_hit=self.cache_hit
            )

            # Record errors if any
            if exc_type is not None:
                self.metrics.record_error(
                    error_type=exc_type.__name__,
                    component="subscription",
                    operation=self.operation
                )

    def set_context(self, **kwargs) -> None:
        """Set context for metrics collection."""
        self.context.update(kwargs)

    def set_success(self, success: bool) -> None:
        """Set operation success status."""
        self.success = success

    def set_cache_hit(self, cache_hit: bool) -> None:
        """Set cache hit status."""
        self.cache_hit = cache_hit


class QuotaMetricsCollector:
    """Specialized metrics collector for quota operations."""

    def __init__(self, metrics: SubscriptionMetrics):
        self.metrics = metrics

    def record_quota_check(
        self,
        user_id: UUID,
        quota_type: QuotaType,
        tier: SubscriptionTier,
        current_usage: int,
        limit: int,
        is_exceeded: bool
    ) -> None:
        """Record quota check metrics."""
        # Record usage pattern
        if limit > 0:
            usage_ratio = current_usage / limit
            self.metrics.record_quota_usage_pattern(quota_type, tier, usage_ratio)

        # Record violation if exceeded
        if is_exceeded:
            self.metrics.record_quota_violation(
                quota_type=quota_type,
                tier=tier,
                violation_type="limit_exceeded"
            )

    def record_quota_increment(
        self,
        user_id: UUID,
        quota_type: QuotaType,
        tier: SubscriptionTier,
        amount: int,
        new_usage: int,
        limit: int
    ) -> None:
        """Record quota increment metrics."""
        # Record usage pattern after increment
        if limit > 0:
            usage_ratio = new_usage / limit
            self.metrics.record_quota_usage_pattern(quota_type, tier, usage_ratio)

        # Check if this increment caused a violation
        if new_usage > limit and limit > 0:
            self.metrics.record_quota_violation(
                quota_type=quota_type,
                tier=tier,
                violation_type="increment_exceeded"
            )


class RevenueCatMetricsCollector:
    """Specialized metrics collector for RevenueCat operations."""

    def __init__(self, metrics: SubscriptionMetrics):
        self.metrics = metrics

    def record_api_call(
        self,
        operation: str,
        duration: float,
        status_code: int,
        success: bool
    ) -> None:
        """Record RevenueCat API call."""
        self.metrics.record_revenuecat_api_call(
            operation=operation,
            status_code=status_code,
            duration=duration,
            success=success
        )

    def record_webhook_processing(
        self,
        event_type: str,
        processing_duration: float,
        success: bool,
        duplicate: bool = False
    ) -> None:
        """Record webhook processing."""
        if duplicate:
            result = "duplicate"
        elif success:
            result = "success"
        else:
            result = "failure"

        self.metrics.record_webhook_event(
            event_type=event_type,
            processing_result=result,
            processing_duration=processing_duration
        )

    def record_sync_failure(
        self,
        failure_type: str,
        retry_count: int = 0
    ) -> None:
        """Record synchronization failure."""
        self.metrics.record_revenuecat_sync_failure(
            failure_type=failure_type,
            retry_count=retry_count
        )


# Global metrics instances
subscription_metrics = SubscriptionMetrics()
quota_metrics_collector = QuotaMetricsCollector(subscription_metrics)
revenuecat_metrics_collector = RevenueCatMetricsCollector(subscription_metrics)


@contextmanager
def collect_subscription_metrics(operation: str):
    """Context manager for collecting subscription metrics."""
    collector = SubscriptionMetricsCollector(subscription_metrics, operation)
    with collector as c:
        yield c


@contextmanager
def collect_database_metrics(query_type: str, table: str):
    """Context manager for collecting database metrics."""
    start_time = time.time()
    try:
        yield
    finally:
        duration = time.time() - start_time
        subscription_metrics.record_database_query(query_type, table, duration)


@contextmanager
def collect_revenuecat_metrics(operation: str):
    """Context manager for collecting RevenueCat API metrics."""
    start_time = time.time()
    success = True
    status_code = 200

    try:
        yield
    except Exception as e:
        success = False
        # Try to extract status code from exception if available
        if hasattr(e, 'status_code'):
            status_code = e.status_code
        else:
            status_code = 500
        raise
    finally:
        duration = time.time() - start_time
        revenuecat_metrics_collector.record_api_call(
            operation=operation,
            duration=duration,
            status_code=status_code,
            success=success
        )


def initialize_subscription_metrics() -> None:
    """Initialize subscription system metrics with default values."""
    try:
        # Set system information
        subscription_metrics.update_system_info({
            "version": "1.0.0",
            "component": "subscription_system",
            "prometheus_available": str(PROMETHEUS_AVAILABLE).lower()
        })

        # Initialize cache hit rates
        subscription_metrics.update_cache_hit_rate("subscription", 0.0)
        subscription_metrics.update_cache_hit_rate("quota", 0.0)

        # Initialize cache sizes
        subscription_metrics.update_subscription_cache_size(0)
        subscription_metrics.update_quota_cache_size(0)

        logger.info("Subscription metrics initialized successfully")

    except Exception as e:
        logger.error("Failed to initialize subscription metrics", extra={
            "error": str(e)
        })


def get_subscription_metrics_summary() -> dict[str, Any]:
    """Get a summary of current subscription metrics."""
    try:
        # This would typically query the metrics registry
        # For now, return a basic summary
        return {
            "metrics_available": PROMETHEUS_AVAILABLE,
            "initialized": True,
            "collectors": [
                "subscription_metrics",
                "quota_metrics_collector",
                "revenuecat_metrics_collector"
            ]
        }
    except Exception as e:
        logger.error("Failed to get metrics summary", extra={
            "error": str(e)
        })
        return {
            "metrics_available": False,
            "error": str(e)
        }
