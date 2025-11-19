"""Request tracking utilities for correlation across services."""

import contextvars
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import uuid4

from .logging import get_safe_logger
from .ids import new_uuid, new_correlation_id


# Module-level logger for tests to mock
logger = get_safe_logger("flerity.request_tracker")

# Context variables for request tracking
_correlation_id: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar('correlation_id', default=None)
_trace_id: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar('trace_id', default=None)
_user_id: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar('user_id', default=None)
_operation: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar('operation', default=None)


class RequestTracker:
    """Context manager for tracking requests across services."""
    
    def __init__(
        self,
        user_id: Optional[str] = None,
        operation: Optional[str] = None,
        correlation_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        **extra_context: Any
    ):
        self.user_id = str(user_id) if user_id is not None else None
        self.operation = operation
        self.correlation_id = correlation_id or new_correlation_id()
        self.trace_id = trace_id or str(new_uuid())
        self.extra_context = extra_context
        self.start_time = datetime.utcnow()
        self.logger = logger  # Use module-level logger for tests
        
        # Store previous context values for restoration
        self._prev_correlation_id = None
        self._prev_trace_id = None
        self._prev_user_id = None
        self._prev_operation = None
    
    def __enter__(self) -> 'RequestTracker':
        """Enter context and set tracking variables."""
        # Store previous values
        self._prev_correlation_id = _correlation_id.get()
        self._prev_trace_id = _trace_id.get()
        self._prev_user_id = _user_id.get()
        self._prev_operation = _operation.get()
        
        # Set new values
        _correlation_id.set(self.correlation_id)
        _trace_id.set(self.trace_id)
        if self.user_id:
            _user_id.set(self.user_id)
        if self.operation:
            _operation.set(self.operation)
        
        self.logger.info(
            f"Request started: {self.operation or 'unknown'}",
            extra={
                "correlation_id": self.correlation_id,
                "trace_id": self.trace_id,
                "user_id": self.user_id,
                "operation": self.operation,
                "timestamp": self.start_time.isoformat(),
                **self.extra_context
            }
        )
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context and restore previous values."""
        duration = (datetime.utcnow() - self.start_time).total_seconds()
        
        if exc_type is None:
            self.logger.info(
                f"Request completed: {self.operation or 'unknown'}",
                extra={
                    "correlation_id": self.correlation_id,
                    "trace_id": self.trace_id,
                    "user_id": self.user_id,
                    "operation": self.operation,
                    "duration_seconds": duration,
                    "status": "success"
                }
            )
        else:
            self.logger.error(
                f"Request failed: {self.operation or 'unknown'}",
                extra={
                    "correlation_id": self.correlation_id,
                    "trace_id": self.trace_id,
                    "user_id": self.user_id,
                    "operation": self.operation,
                    "duration_seconds": duration,
                    "status": "error",
                    "error_type": exc_type.__name__ if exc_type else None,
                    "error_message": str(exc_val) if exc_val else None
                }
            )
        
        # Restore previous values
        _correlation_id.set(self._prev_correlation_id)
        _trace_id.set(self._prev_trace_id)
        _user_id.set(self._prev_user_id)
        _operation.set(self._prev_operation)
    
    def log_success(self, result_id: Optional[str] = None, **context: Any) -> None:
        """Log successful operation within request."""
        self.logger.info(
            f"operation_success: {self.operation or 'unknown'}",
            extra={
                "correlation_id": self.correlation_id,
                "trace_id": self.trace_id,
                "user_id": self.user_id,
                "operation": self.operation,
                "result_id": result_id,
                "status": "success",
                **context
            }
        )
    
    def log_error(self, error: Exception, **context: Any) -> str:
        """Log error within request and return error ID."""
        error_id = str(uuid4())
        
        self.logger.error(
            f"operation_error: {self.operation or 'unknown'} (Error ID: {error_id})",
            extra={
                "correlation_id": self.correlation_id,
                "trace_id": self.trace_id,
                "user_id": self.user_id,
                "operation": self.operation,
                "error_id": error_id,
                "error_type": type(error).__name__,
                "error_message": str(error),
                "status": "error",
                **context
            }
        )
        
        return error_id
    
    def get_correlation_id(self) -> str:
        """Get correlation ID."""
        return self.correlation_id
    
    def get_trace_id(self) -> str:
        """Get trace ID."""
        return self.trace_id
    
    def get_user_id(self) -> Optional[str]:
        """Get user ID."""
        return self.user_id
    
    def get_operation(self) -> Optional[str]:
        """Get operation name."""
        return self.operation
    
    def get_request_context(self) -> Dict[str, Any]:
        """Get full request context."""
        duration = (datetime.utcnow() - self.start_time).total_seconds() * 1000  # Convert to milliseconds
        return {
            "user_id": str(self.user_id) if self.user_id else None,
            "operation": self.operation,
            "correlation_id": self.correlation_id,
            "trace_id": self.trace_id,
            "start_time": self.start_time.isoformat(),
            "duration_ms": duration
        }


def get_correlation_id() -> Optional[str]:
    """Get current correlation ID from context."""
    return _correlation_id.get()


def get_trace_id() -> Optional[str]:
    """Get current trace ID from context."""
    return _trace_id.get()


def get_user_id() -> Optional[str]:
    """Get current user ID from context."""
    return _user_id.get()


def get_operation() -> Optional[str]:
    """Get current operation from context."""
    return _operation.get()


def get_request_context() -> Dict[str, Optional[str]]:
    """Get all current request context."""
    return {
        "correlation_id": get_correlation_id(),
        "trace_id": get_trace_id(),
        "user_id": get_user_id(),
        "operation": get_operation()
    }


def set_correlation_id(correlation_id: str) -> None:
    """Set correlation ID in context."""
    _correlation_id.set(correlation_id)


def set_trace_id(trace_id: str) -> None:
    """Set trace ID in context."""
    _trace_id.set(trace_id)


def set_user_id(user_id: str) -> None:
    """Set user ID in context."""
    _user_id.set(user_id)


def set_operation(operation: str) -> None:
    """Set operation in context."""
    _operation.set(operation)
