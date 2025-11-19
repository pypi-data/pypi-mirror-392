"""
Thread Deletion Monitoring and Observability

This module provides comprehensive monitoring, alerting, and observability
for the thread deletion system.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from ...utils.logging import get_logger
from ...utils.tracing import trace_async

logger = get_logger(__name__)


class ThreadDeletionMonitor:
    """
    Comprehensive monitoring for thread deletion operations.
    
    Provides:
    - Real-time metrics collection
    - Performance monitoring
    - Error tracking and alerting
    - Health checks
    - Structured logging
    """

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory
        self.metrics = ThreadDeletionMetrics()
        self.alerts = ThreadDeletionAlerts()

    @trace_async
    async def track_deletion_start(
        self,
        thread_id: UUID,
        user_id: UUID,
        client_type: str = "unknown"
    ) -> str:
        """Track the start of a deletion operation."""
        operation_id = f"del_{thread_id}_{datetime.now(UTC).timestamp()}"

        # Record metrics
        self.metrics.record_deletion_start(operation_id, client_type)

        # Structured logging
        logger.info("Thread deletion operation started", extra={
            "event_type": "thread_deletion_started",
            "operation_id": operation_id,
            "thread_id": str(thread_id),
            "user_id": str(user_id),
            "client_type": client_type,
            "timestamp": datetime.now(UTC).isoformat(),
        })

        logger.info("Thread deletion operation started", extra={
            "operation_id": operation_id,
            "thread_id": str(thread_id),
            "user_id": str(user_id),
            "client_type": client_type
        })

        return operation_id

    @trace_async
    async def track_deletion_success(
        self,
        operation_id: str,
        thread_id: UUID,
        user_id: UUID,
        message_count: int,
        duration_ms: float
    ) -> None:
        """Track successful deletion completion."""
        # Record metrics
        self.metrics.record_deletion_success(operation_id, duration_ms, message_count)

        # Structured logging
        logger.info("Thread deletion completed successfully", extra={
            "event_type": "thread_deletion_completed",
            "operation_id": operation_id,
            "thread_id": str(thread_id),
            "user_id": str(user_id),
            "message_count": message_count,
            "duration_ms": duration_ms,
            "timestamp": datetime.now(UTC).isoformat(),
            "status": "success"
        })

        logger.info("Thread deletion completed successfully", extra={
            "operation_id": operation_id,
            "thread_id": str(thread_id),
            "user_id": str(user_id),
            "message_count": message_count,
            "duration_ms": duration_ms
        })

    @trace_async
    async def track_deletion_failure(
        self,
        operation_id: str,
        thread_id: UUID,
        user_id: UUID,
        error: Exception,
        duration_ms: float
    ) -> None:
        """Track deletion failure and trigger alerts."""
        error_type = type(error).__name__
        error_message = str(error)

        # Record metrics
        self.metrics.record_deletion_failure(operation_id, error_type, duration_ms)

        # Structured logging
        logger.error("Thread deletion failed", extra={
            "event_type": "thread_deletion_failed",
            "operation_id": operation_id,
            "thread_id": str(thread_id),
            "user_id": str(user_id),
            "error_type": error_type,
            "error_message": error_message,
            "duration_ms": duration_ms,
            "timestamp": datetime.now(UTC).isoformat(),
            "status": "failed"
        })

        logger.error("Thread deletion failed", extra={
            "operation_id": operation_id,
            "thread_id": str(thread_id),
            "user_id": str(user_id),
            "error_type": error_type,
            "error_message": error_message,
            "duration_ms": duration_ms
        })

        # Check if alert should be triggered
        await self.alerts.check_failure_alert(error_type, error_message)

    @trace_async
    async def track_performance_metrics(
        self,
        operation_type: str,
        duration_ms: float,
        resource_usage: dict[str, Any]
    ) -> None:
        """Track performance metrics for deletion operations."""
        # Record performance metrics
        self.metrics.record_performance(operation_type, duration_ms, resource_usage)

        # Structured logging for performance
        logger.debug("Thread deletion performance metrics", extra={
            "event_type": "thread_deletion_performance",
            "operation_type": operation_type,
            "duration_ms": duration_ms,
            "resource_usage": resource_usage,
            "timestamp": datetime.now(UTC).isoformat(),
        })

        # Check for performance alerts
        await self.alerts.check_performance_alert(operation_type, duration_ms)

    @trace_async
    async def get_monitoring_dashboard(self) -> dict[str, Any]:
        """Get comprehensive monitoring dashboard data."""
        return {
            "timestamp": datetime.now(UTC).isoformat(),
            "metrics": await self.metrics.get_current_metrics(),
            "alerts": await self.alerts.get_active_alerts(),
            "health_status": await self.get_health_status(),
            "performance_summary": await self.metrics.get_performance_summary(),
        }

    @trace_async
    async def get_health_status(self) -> dict[str, Any]:
        """Get overall health status of deletion system."""
        metrics = await self.metrics.get_current_metrics()

        # Determine health based on metrics
        error_rate = metrics.get("error_rate", 0)
        avg_duration = metrics.get("avg_duration_ms", 0)

        if error_rate > 0.1:  # More than 10% error rate
            status = "unhealthy"
            reason = f"High error rate: {error_rate:.2%}"
        elif avg_duration > 5000:  # More than 5 seconds average
            status = "degraded"
            reason = f"High average duration: {avg_duration:.0f}ms"
        else:
            status = "healthy"
            reason = "All metrics within normal ranges"

        return {
            "status": status,
            "reason": reason,
            "last_check": datetime.now(UTC).isoformat(),
            "metrics_summary": {
                "error_rate": error_rate,
                "avg_duration_ms": avg_duration,
                "total_operations": metrics.get("total_operations", 0),
                "success_rate": metrics.get("success_rate", 0),
            }
        }


class ThreadDeletionMetrics:
    """Metrics collection for thread deletion operations."""

    def __init__(self):
        self.operations: dict[str, dict[str, Any]] = {}
        self.performance_data: list[dict[str, Any]] = []
        self.error_counts: dict[str, int] = {}

    def record_deletion_start(self, operation_id: str, client_type: str) -> None:
        """Record the start of a deletion operation."""
        self.operations[operation_id] = {
            "start_time": datetime.now(UTC),
            "client_type": client_type,
            "status": "in_progress"
        }

    def record_deletion_success(
        self,
        operation_id: str,
        duration_ms: float,
        message_count: int
    ) -> None:
        """Record successful deletion."""
        if operation_id in self.operations:
            self.operations[operation_id].update({
                "status": "success",
                "duration_ms": duration_ms,
                "message_count": message_count,
                "end_time": datetime.now(UTC)
            })

    def record_deletion_failure(
        self,
        operation_id: str,
        error_type: str,
        duration_ms: float
    ) -> None:
        """Record deletion failure."""
        if operation_id in self.operations:
            self.operations[operation_id].update({
                "status": "failed",
                "error_type": error_type,
                "duration_ms": duration_ms,
                "end_time": datetime.now(UTC)
            })

        # Track error counts
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1

    def record_performance(
        self,
        operation_type: str,
        duration_ms: float,
        resource_usage: dict[str, Any]
    ) -> None:
        """Record performance metrics."""
        self.performance_data.append({
            "operation_type": operation_type,
            "duration_ms": duration_ms,
            "resource_usage": resource_usage,
            "timestamp": datetime.now(UTC)
        })

        # Keep only last 1000 performance records
        if len(self.performance_data) > 1000:
            self.performance_data = self.performance_data[-1000:]

    async def get_current_metrics(self) -> dict[str, Any]:
        """Get current metrics summary."""
        total_ops = len(self.operations)
        if total_ops == 0:
            return {
                "total_operations": 0,
                "success_rate": 0,
                "error_rate": 0,
                "avg_duration_ms": 0,
            }

        successful_ops = sum(1 for op in self.operations.values() if op["status"] == "success")
        failed_ops = sum(1 for op in self.operations.values() if op["status"] == "failed")

        success_rate = successful_ops / total_ops if total_ops > 0 else 0
        error_rate = failed_ops / total_ops if total_ops > 0 else 0

        # Calculate average duration for completed operations
        completed_ops = [op for op in self.operations.values() if "duration_ms" in op]
        avg_duration = sum(op["duration_ms"] for op in completed_ops) / len(completed_ops) if completed_ops else 0

        return {
            "total_operations": total_ops,
            "successful_operations": successful_ops,
            "failed_operations": failed_ops,
            "success_rate": success_rate,
            "error_rate": error_rate,
            "avg_duration_ms": avg_duration,
            "error_breakdown": dict(self.error_counts),
            "last_updated": datetime.now(UTC).isoformat(),
        }

    async def get_performance_summary(self) -> dict[str, Any]:
        """Get performance metrics summary."""
        if not self.performance_data:
            return {"message": "No performance data available"}

        recent_data = [
            p for p in self.performance_data
            if p["timestamp"] > datetime.now(UTC) - timedelta(hours=1)
        ]

        if not recent_data:
            return {"message": "No recent performance data"}

        durations = [p["duration_ms"] for p in recent_data]

        return {
            "recent_operations": len(recent_data),
            "avg_duration_ms": sum(durations) / len(durations),
            "min_duration_ms": min(durations),
            "max_duration_ms": max(durations),
            "p95_duration_ms": sorted(durations)[int(len(durations) * 0.95)] if durations else 0,
            "time_window": "1 hour",
            "last_updated": datetime.now(UTC).isoformat(),
        }


class ThreadDeletionAlerts:
    """Alert system for thread deletion operations."""

    def __init__(self):
        self.active_alerts: list[dict[str, Any]] = []
        self.alert_thresholds = {
            "error_rate": 0.1,  # 10%
            "avg_duration_ms": 5000,  # 5 seconds
            "consecutive_failures": 5,
        }
        self.consecutive_failure_count = 0

    async def check_failure_alert(self, error_type: str, error_message: str) -> None:
        """Check if failure should trigger an alert."""
        self.consecutive_failure_count += 1

        if self.consecutive_failure_count >= self.alert_thresholds["consecutive_failures"]:
            await self.trigger_alert(
                alert_type="consecutive_failures",
                severity="high",
                message=f"Thread deletion system experiencing {self.consecutive_failure_count} consecutive failures",
                details={
                    "latest_error_type": error_type,
                    "latest_error_message": error_message,
                    "consecutive_count": self.consecutive_failure_count,
                }
            )

    async def check_performance_alert(self, operation_type: str, duration_ms: float) -> None:
        """Check if performance metrics should trigger an alert."""
        if duration_ms > self.alert_thresholds["avg_duration_ms"]:
            await self.trigger_alert(
                alert_type="performance_degradation",
                severity="medium",
                message=f"Thread deletion operation took {duration_ms:.0f}ms (threshold: {self.alert_thresholds['avg_duration_ms']}ms)",
                details={
                    "operation_type": operation_type,
                    "duration_ms": duration_ms,
                    "threshold_ms": self.alert_thresholds["avg_duration_ms"],
                }
            )

    async def trigger_alert(
        self,
        alert_type: str,
        severity: str,
        message: str,
        details: dict[str, Any]
    ) -> None:
        """Trigger an alert."""
        alert = {
            "id": f"alert_{datetime.now(UTC).timestamp()}",
            "type": alert_type,
            "severity": severity,
            "message": message,
            "details": details,
            "triggered_at": datetime.now(UTC).isoformat(),
            "status": "active",
        }

        self.active_alerts.append(alert)

        # Log alert
        logger.warning("Thread deletion alert triggered", extra={
            "alert_type": alert_type,
            "severity": severity,
            "message": message,
            "details": details
        })

        # In a real system, this would send notifications to monitoring systems
        # like PagerDuty, Slack, email, etc.
        await self._send_alert_notification(alert)

    async def _send_alert_notification(self, alert: dict[str, Any]) -> None:
        """Send alert notification (placeholder for real implementation)."""
        # This would integrate with actual alerting systems
        logger.info("Alert notification sent", extra={
            "alert_id": alert["id"],
            "alert_type": alert["type"],
            "severity": alert["severity"]
        })

    async def get_active_alerts(self) -> list[dict[str, Any]]:
        """Get all active alerts."""
        # Remove old alerts (older than 24 hours)
        cutoff_time = datetime.now(UTC) - timedelta(hours=24)
        self.active_alerts = [
            alert for alert in self.active_alerts
            if datetime.fromisoformat(alert["triggered_at"].replace('Z', '+00:00')) > cutoff_time
        ]

        return self.active_alerts

    async def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an active alert."""
        for alert in self.active_alerts:
            if alert["id"] == alert_id:
                alert["status"] = "resolved"
                alert["resolved_at"] = datetime.now(UTC).isoformat()
                logger.info("Alert resolved", extra={"alert_id": alert_id})
                return True
        return False


def create_thread_deletion_monitor(
    session_factory: async_sessionmaker[AsyncSession]
) -> ThreadDeletionMonitor:
    """Factory function for ThreadDeletionMonitor."""
    return ThreadDeletionMonitor(session_factory)
