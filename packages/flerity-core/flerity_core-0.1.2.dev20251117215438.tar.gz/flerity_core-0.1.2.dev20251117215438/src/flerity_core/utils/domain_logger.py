"""Domain-specific logger with context auto-detection and performance metrics."""

import time
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import uuid4

from .logging import get_safe_logger
from .request_tracking import get_request_context
from .enhanced_logging import EnhancedErrorLogger


class DomainLogger:
    """Enhanced logger for domain operations with context and metrics."""
    
    def __init__(self, domain: str, component: Optional[str] = None):
        self.domain = domain
        self.component = component or domain
        self.logger = get_safe_logger(f"flerity.{domain}")
    
    def _get_base_context(self, operation: Optional[str] = None) -> Dict[str, Any]:
        """Get base context with request tracking and domain info."""
        context = get_request_context()
        context.update({
            "domain": self.domain,
            "component": self.component,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        if operation:
            context["operation"] = operation
            
        return context
    
    def info(self, message: str, operation: Optional[str] = None, **extra: Any) -> None:
        """Log info message with domain context."""
        context = self._get_base_context(operation)
        context.update(extra)
        
        self.logger.info(message, extra=context)
    
    def debug(self, message: str, operation: Optional[str] = None, **extra: Any) -> None:
        """Log debug message with domain context."""
        context = self._get_base_context(operation)
        context.update(extra)
        
        self.logger.debug(message, extra=context)
    
    def warning(self, message: str, operation: Optional[str] = None, **extra: Any) -> None:
        """Log warning message with domain context."""
        context = self._get_base_context(operation)
        context.update(extra)
        
        self.logger.warning(message, extra=context)
    
    def error(self, message: str, operation: Optional[str] = None, error: Optional[Exception] = None, **extra: Any) -> str:
        """Log error message with domain context and return error ID."""
        error_id = str(uuid4())
        context = self._get_base_context(operation)
        context.update({
            "error_id": error_id,
            "severity": "high",
            **extra
        })
        
        if error:
            context.update({
                "error_type": type(error).__name__,
                "error_message": str(error)
            })
        
        self.logger.error(f"{message} (Error ID: {error_id})", extra=context)
        return error_id
    
    def operation_start(self, operation: str, **context: Any) -> Dict[str, Any]:
        """Log operation start and return tracking context."""
        tracking_context = {
            "operation_id": str(uuid4()),
            "operation": operation,
            "start_time": time.time(),
            "domain": self.domain,
            "component": self.component
        }
        tracking_context.update(context)
        
        base_context = self._get_base_context(operation)
        base_context.update(tracking_context)
        
        self.logger.info(f"Operation started: {operation}", extra=base_context)
        return tracking_context
    
    def operation_success(self, tracking_context: Dict[str, Any], result_id: Optional[str] = None, **extra: Any) -> None:
        """Log successful operation completion with performance metrics."""
        duration = time.time() - tracking_context["start_time"]
        
        context = self._get_base_context(tracking_context["operation"])
        context.update({
            "operation_id": tracking_context["operation_id"],
            "duration_seconds": duration,
            "status": "success",
            "result_id": result_id,
            **extra
        })
        
        self.logger.info(
            f"Operation completed: {tracking_context['operation']} ({duration:.3f}s)",
            extra=context
        )
    
    def operation_error(self, tracking_context: Dict[str, Any], error, extra_context: Optional[Dict[str, Any]] = None, **extra: Any) -> str:
        """Log operation error with performance metrics and return error ID."""
        duration = time.time() - tracking_context["start_time"]
        error_id = str(uuid4())
        
        context = self._get_base_context(tracking_context["operation"])
        context.update({
            "operation_id": tracking_context["operation_id"],
            "error_id": error_id,
            "duration_seconds": duration,
            "status": "error",
            "severity": "high",
            **extra
        })
        
        # Add extra context if provided
        if extra_context:
            context.update(extra_context)
        
        # Handle both Exception objects and string error messages
        if isinstance(error, Exception):
            context.update({
                "error_type": type(error).__name__,
                "error_message": str(error)
            })
        else:
            context.update({
                "error_type": "Unknown",
                "error_message": str(error)
            })
        
        self.logger.error(
            f"Operation failed: {tracking_context['operation']} ({duration:.3f}s) (Error ID: {error_id})",
            extra=context
        )
        
        return error_id
    
    def database_operation(self, operation: str, table: Optional[str] = None, query_time: Optional[float] = None, **extra: Any) -> None:
        """Log database operation with performance metrics."""
        context = self._get_base_context(operation)
        context.update({
            "category": "database",
            "table": table,
            "query_time_seconds": query_time,
            **extra
        })
        
        message = f"Database operation: {operation}"
        if table:
            message += f" on {table}"
        if query_time:
            message += f" ({query_time:.3f}s)"
            
        self.logger.info(message, extra=context)
    
    def external_api_call(self, service: str, endpoint: str, method: str = "GET", response_time: Optional[float] = None, status_code: Optional[int] = None, **extra: Any) -> None:
        """Log external API call with performance metrics."""
        context = self._get_base_context(f"{service}_api_call")
        context.update({
            "category": "external_api",
            "service": service,
            "endpoint": endpoint,
            "method": method,
            "response_time_seconds": response_time,
            "status_code": status_code,
            **extra
        })
        
        message = f"External API call: {method} {service}/{endpoint}"
        if response_time:
            message += f" ({response_time:.3f}s)"
        if status_code:
            message += f" [{status_code}]"
            
        self.logger.info(message, extra=context)
    
    def business_event(self, event: str, entity_id: Optional[str] = None, **extra: Any) -> None:
        """Log business domain event."""
        context = self._get_base_context(event)
        context.update({
            "category": "business_event",
            "event": event,
            "entity_id": entity_id,
            **extra
        })
        
        self.logger.info(f"Business event: {event}", extra=context)


# Cache for domain logger instances
_domain_logger_cache: Dict[str, DomainLogger] = {}


def get_domain_logger(domain: str, component: Optional[str] = None) -> DomainLogger:
    """Get domain logger instance."""
    cache_key = f"{domain}:{component or domain}"
    if cache_key not in _domain_logger_cache:
        _domain_logger_cache[cache_key] = DomainLogger(domain, component)
    return _domain_logger_cache[cache_key]


# Convenience functions for common domains
def get_auth_logger() -> DomainLogger:
    """Get auth domain logger."""
    return get_domain_logger("auth")


def get_threads_logger() -> DomainLogger:
    """Get threads domain logger."""
    return get_domain_logger("threads")


def get_ai_logger() -> DomainLogger:
    """Get AI domain logger."""
    return get_domain_logger("ai")


def get_subscription_logger() -> DomainLogger:
    """Get subscription domain logger."""
    return get_domain_logger("subscription")


def get_notifications_logger() -> DomainLogger:
    """Get notifications domain logger."""
    return get_domain_logger("notifications")


def get_analytics_logger() -> DomainLogger:
    """Get analytics domain logger."""
    return get_domain_logger("analytics")


def get_integrations_logger() -> DomainLogger:
    """Get integrations domain logger."""
    return get_domain_logger("integrations")


def get_users_logger() -> DomainLogger:
    """Get users domain logger."""
    return get_domain_logger("users")
