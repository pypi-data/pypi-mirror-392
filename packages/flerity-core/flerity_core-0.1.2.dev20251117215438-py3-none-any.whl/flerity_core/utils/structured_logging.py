"""Structured logging utilities for thread tracking and monitoring."""

import logging
from datetime import UTC, datetime
from typing import Any
from uuid import UUID


class ThreadTrackingLogger:
    """Structured logger for thread tracking operations."""

    def __init__(self, component: str = "thread_tracking", service: str = "flerity"):
        """Initialize the structured logger.
        
        Args:
            component: Component name for logging context
            service: Service name for logging context
        """
        self.component = component
        self.service = service
        self.logger = logging.getLogger(f"{service}.{component}")

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
        return extra

    def tracking_enabled(self, user_id: UUID, thread_id: UUID, config_id: UUID) -> None:
        """Log when tracking is enabled for a thread.
        
        Args:
            user_id: User ID
            thread_id: Thread ID
            config_id: Configuration ID
        """
        self.logger.info(
            "Thread tracking enabled",
            extra=self._base_extra(
                user_id=str(user_id),
                thread_id=str(thread_id),
                config_id=str(config_id),
                action="tracking_enabled"
            )
        )

    def tracking_disabled(self, user_id: UUID, thread_id: UUID, config_id: UUID) -> None:
        """Log when tracking is disabled for a thread.
        
        Args:
            user_id: User ID
            thread_id: Thread ID
            config_id: Configuration ID
        """
        self.logger.info(
            "Thread tracking disabled",
            extra=self._base_extra(
                user_id=str(user_id),
                thread_id=str(thread_id),
                config_id=str(config_id),
                action="tracking_disabled"
            )
        )

    def tracking_reactivated(self, user_id: UUID, thread_id: UUID, config_id: UUID) -> None:
        """Log when tracking is reactivated for a thread.
        
        Args:
            user_id: User ID
            thread_id: Thread ID
            config_id: Configuration ID
        """
        self.logger.info(
            "Thread tracking reactivated",
            extra=self._base_extra(
                user_id=str(user_id),
                thread_id=str(thread_id),
                config_id=str(config_id),
                action="tracking_reactivated"
            )
        )

    def tracking_check(self, thread_id: UUID, is_tracked: bool) -> None:
        """Log tracking check results.
        
        Args:
            thread_id: Thread ID
            is_tracked: Whether the thread is being tracked
        """
        self.logger.debug(
            "Thread tracking check",
            extra=self._base_extra(
                thread_id=str(thread_id),
                is_tracked=is_tracked,
                action="tracking_check"
            )
        )

    def tracking_error(self, error: Exception, context: dict[str, Any] | None = None) -> None:
        """Log tracking errors.
        
        Args:
            error: The exception that occurred
            context: Additional context information
        """
        extra = self._base_extra(
            error_type=type(error).__name__,
            error_message=str(error),
            action="tracking_error"
        )
        if context:
            extra.update(context)

        self.logger.error(
            "Thread tracking error",
            extra=extra,
            exc_info=error
        )


# Global logger instance
tracking_logger = ThreadTrackingLogger()
