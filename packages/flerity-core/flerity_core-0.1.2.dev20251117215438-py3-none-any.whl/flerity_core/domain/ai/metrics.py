"""
Enhanced metrics collection for AI module observability.
"""
import time
from contextlib import contextmanager
from typing import Any

try:
    from prometheus_client import Counter, Gauge, Histogram
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
        def labels(self, *args: Any, **kwargs: Any) -> 'MockGauge': return self

    Counter = MockCounter
    Histogram = MockHistogram
    Gauge = MockGauge

from flerity_core.utils.logging import get_logger

logger = get_logger(__name__)


class AIMetrics:
    """Centralized metrics collection for AI module."""

    def __init__(self) -> None:
        # Performance metrics
        self.generation_latency = Histogram(
            "ai_generation_latency_seconds",
            "Time to generate AI response",
            ["kind", "model", "cache_hit", "user_tier"]
        )

        self.cache_requests = Counter(
            "ai_cache_requests_total",
            "Cache requests by hit type",
            ["hit_type"]  # exact, semantic, miss
        )

        # Quality metrics
        self.deduplication_removed = Counter(
            "ai_deduplication_removed_total",
            "Suggestions removed by deduplication"
        )

        self.similarity_scores = Histogram(
            "ai_similarity_scores",
            "Similarity scores for deduplication",
            buckets=[0.1, 0.3, 0.5, 0.7, 0.8, 0.9, 0.95, 0.99, 1.0]
        )

        # Business metrics
        self.suggestions_generated = Counter(
            "ai_suggestions_generated_total",
            "Total suggestions generated",
            ["kind", "tone", "user_tier"]
        )

        self.user_satisfaction = Histogram(
            "ai_user_satisfaction_score",
            "User satisfaction with AI suggestions",
            ["suggestion_type", "tone"]
        )

        # A/B testing metrics
        self.ab_test_assignments = Counter(
            "ai_ab_test_assignments_total",
            "A/B test variant assignments",
            ["experiment", "variant"]
        )

        self.ab_test_conversions = Counter(
            "ai_ab_test_conversions_total",
            "A/B test conversions",
            ["experiment", "variant", "metric"]
        )

        # Error metrics
        self.errors = Counter(
            "ai_errors_total",
            "AI module errors",
            ["error_type", "component"]
        )

        # Rate limiting
        self.rate_limit_exceeded = Counter(
            "ai_rate_limit_exceeded_total",
            "Rate limit exceeded events",
            ["limit_type", "user_tier"]
        )

        # Cost tracking
        self.cost_tracking = Counter(
            "ai_cost_total",
            "Total AI costs",
            ["model", "operation"]
        )

    def record_generation(
        self,
        duration: float,
        kind: str,
        model: str,
        cache_hit: bool,
        user_tier: str = "free"
    ) -> None:
        """Record AI generation metrics."""
        self.generation_latency.labels(
            kind=kind,
            model=model,
            cache_hit="hit" if cache_hit else "miss",
            user_tier=user_tier
        ).observe(duration)

        self.suggestions_generated.labels(
            kind=kind,
            tone="default",
            user_tier=user_tier
        ).inc()

    def record_cache_result(self, hit_type: str) -> None:
        """Record cache hit/miss."""
        self.cache_requests.labels(hit_type=hit_type).inc()

    def record_deduplication(
        self,
        original_count: int,
        final_count: int,
        similarities: list[float] | None = None
    ) -> None:
        """Record deduplication metrics."""
        removed = original_count - final_count
        self.deduplication_removed.inc(removed)

        if similarities:
            for similarity in similarities:
                self.similarity_scores.observe(similarity)

    def record_user_satisfaction(
        self,
        score: float,
        suggestion_type: str,
        tone: str = "default"
    ) -> None:
        """Record user satisfaction score."""
        self.user_satisfaction.labels(
            suggestion_type=suggestion_type,
            tone=tone
        ).observe(score)

    def record_ab_assignment(self, experiment: str, variant: str) -> None:
        """Record A/B test assignment."""
        self.ab_test_assignments.labels(
            experiment=experiment,
            variant=variant
        ).inc()

    def record_ab_conversion(
        self,
        experiment: str,
        variant: str,
        metric: str
    ) -> None:
        """Record A/B test conversion."""
        self.ab_test_conversions.labels(
            experiment=experiment,
            variant=variant,
            metric=metric
        ).inc()

    def record_error(self, error_type: str, component: str) -> None:
        """Record error occurrence."""
        self.errors.labels(
            error_type=error_type,
            component=component
        ).inc()

    def record_rate_limit(self, limit_type: str, user_tier: str) -> None:
        """Record rate limit exceeded."""
        self.rate_limit_exceeded.labels(
            limit_type=limit_type,
            user_tier=user_tier
        ).inc()

    def record_cost(self, amount: float, model: str, operation: str) -> None:
        """Record AI operation cost."""
        self.cost_tracking.labels(
            model=model,
            operation=operation
        ).inc(amount)


class MetricsCollector:
    """Context manager for collecting metrics during AI operations."""

    def __init__(self, metrics: AIMetrics, operation: str):
        self.metrics = metrics
        self.operation = operation
        self.start_time: float | None = None
        self.context: dict[str, Any] = {}

    def __enter__(self) -> 'MetricsCollector':
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type: type | None, _exc_val: Exception | None, exc_tb: Any | None) -> None:
        if self.start_time is not None:
            duration = time.time() - self.start_time

            # Record based on operation type
            if self.operation == "generation":
                self.metrics.record_generation(
                    duration=duration,
                    kind=self.context.get("kind", "unknown"),
                    model=self.context.get("model", "unknown"),
                    cache_hit=self.context.get("cache_hit", False),
                    user_tier=self.context.get("user_tier", "free")
                )

            # Record errors if any
            if exc_type is not None:
                self.metrics.record_error(
                    error_type=exc_type.__name__,
                    component=self.operation
                )

    def set_context(self, **kwargs) -> None:
        """Set context for metrics collection."""
        self.context.update(kwargs)


# Global metrics instance
ai_metrics = AIMetrics()


@contextmanager
def collect_metrics(operation: str) -> Any:  # Generator[MetricsCollector, None, None]
    """Context manager for collecting AI metrics."""
    collector = MetricsCollector(ai_metrics, operation)
    with collector as c:
        yield c
