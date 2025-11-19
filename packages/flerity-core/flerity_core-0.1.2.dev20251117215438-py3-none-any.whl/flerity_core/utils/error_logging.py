"""Structured error logging utilities for better error tracing and debugging."""

import traceback
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import uuid4

from .logging import get_safe_logger

logger = get_safe_logger(__name__)


class ErrorLogger:
    """Structured error logger with context enrichment."""
    
    @staticmethod
    def log_database_error(
        error: Exception,
        operation: str,
        table: Optional[str] = None,
        user_id: Optional[str] = None,
        query_context: Optional[Dict[str, Any]] = None,
        **extra_context: Any
    ) -> str:
        """Log database errors with structured context.
        
        Args:
            error: The database exception
            operation: Database operation (SELECT, INSERT, UPDATE, DELETE)
            table: Table name if applicable
            user_id: User ID if applicable
            query_context: Additional query context
            **extra_context: Additional context fields
            
        Returns:
            Error ID for tracking
        """
        error_id = str(uuid4())
        
        context = {
            "error_id": error_id,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "database_operation": operation,
            "timestamp": datetime.utcnow().isoformat(),
            "category": "database",
            "severity": "critical",
        }
        
        if table:
            context["table_name"] = table
        if user_id:
            context["user_id"] = user_id
        if query_context:
            context["query_context"] = query_context
            
        # Add specific database error context
        error_msg = str(error).lower()
        if "connection" in error_msg:
            context["database_issue"] = "connection_failed"
            context["likely_cause"] = "database_unavailable_or_network_issue"
        elif "timeout" in error_msg:
            context["database_issue"] = "query_timeout"
            context["likely_cause"] = "slow_query_or_lock_contention"
        elif "syntax" in error_msg:
            context["database_issue"] = "sql_syntax_error"
            context["likely_cause"] = "malformed_query"
        elif "constraint" in error_msg:
            context["database_issue"] = "constraint_violation"
            context["likely_cause"] = "data_integrity_violation"
        elif "permission" in error_msg or "access" in error_msg:
            context["database_issue"] = "permission_denied"
            context["likely_cause"] = "insufficient_database_privileges"
        else:
            context["database_issue"] = "unknown"
            context["likely_cause"] = "investigate_error_details"
        
        context.update(extra_context)
        
        logger.error(
            f"Database operation failed: {operation}",
            extra={
                **context,
                "stack_trace": traceback.format_exc(),
                "requires_investigation": True,
                "alert_dba": context["database_issue"] in ["connection_failed", "query_timeout"]
            }
        )
        
        return error_id
    
    @staticmethod
    def log_api_error(
        error: Exception,
        endpoint: str,
        method: str,
        user_id: Optional[str] = None,
        request_data: Optional[Dict[str, Any]] = None,
        status_code: Optional[int] = None,
        **extra_context: Any
    ) -> str:
        """Log API errors with request context.
        
        Args:
            error: The API exception
            endpoint: API endpoint path
            method: HTTP method
            user_id: User ID if applicable
            request_data: Request payload (will be sanitized)
            status_code: HTTP status code if applicable
            **extra_context: Additional context fields
            
        Returns:
            Error ID for tracking
        """
        error_id = str(uuid4())
        
        context = {
            "error_id": error_id,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "api_endpoint": endpoint,
            "http_method": method,
            "timestamp": datetime.utcnow().isoformat(),
            "category": "api",
            "severity": "high",
        }
        
        if user_id:
            context["user_id"] = user_id
        if status_code:
            context["status_code"] = status_code
        if request_data:
            # Sanitize request data (remove sensitive fields)
            sanitized_data = _sanitize_request_data(request_data)
            context["request_data"] = sanitized_data
            
        context.update(extra_context)
        
        logger.error(
            f"API error in {method} {endpoint}",
            extra={
                **context,
                "stack_trace": traceback.format_exc(),
                "requires_investigation": True,
            }
        )
        
        return error_id
    
    @staticmethod
    def log_external_service_error(
        error: Exception,
        service_name: str,
        operation: str,
        service_url: Optional[str] = None,
        response_status: Optional[int] = None,
        response_time_ms: Optional[float] = None,
        **extra_context: Any
    ) -> str:
        """Log external service errors with service context.
        
        Args:
            error: The service exception
            service_name: Name of external service
            operation: Operation being performed
            service_url: Service URL (will be sanitized)
            response_status: HTTP response status if applicable
            response_time_ms: Response time in milliseconds
            **extra_context: Additional context fields
            
        Returns:
            Error ID for tracking
        """
        error_id = str(uuid4())
        
        context = {
            "error_id": error_id,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "external_service": service_name,
            "service_operation": operation,
            "timestamp": datetime.utcnow().isoformat(),
            "category": "external_service",
            "severity": "high",
        }
        
        if service_url:
            # Sanitize URL (remove credentials)
            context["service_url"] = _sanitize_url(service_url)
        if response_status:
            context["response_status"] = response_status
        if response_time_ms:
            context["response_time_ms"] = response_time_ms
            
        # Determine service health status
        if response_status:
            if response_status >= 500:
                context["service_health"] = "degraded"
                context["likely_cause"] = "service_internal_error"
            elif response_status == 429:
                context["service_health"] = "rate_limited"
                context["likely_cause"] = "rate_limit_exceeded"
            elif response_status >= 400:
                context["service_health"] = "client_error"
                context["likely_cause"] = "invalid_request_or_auth"
            else:
                context["service_health"] = "unknown"
        else:
            context["service_health"] = "unreachable"
            context["likely_cause"] = "network_connectivity_issue"
            
        context.update(extra_context)
        
        logger.error(
            f"External service error: {service_name} - {operation}",
            extra={
                **context,
                "stack_trace": traceback.format_exc(),
                "requires_investigation": True,
                "alert_ops": context["service_health"] in ["unreachable", "degraded"]
            }
        )
        
        return error_id
    
    @staticmethod
    def log_business_logic_error(
        error: Exception,
        business_operation: str,
        user_id: Optional[str] = None,
        entity_id: Optional[str] = None,
        entity_type: Optional[str] = None,
        **extra_context: Any
    ) -> str:
        """Log business logic errors with domain context.
        
        Args:
            error: The business logic exception
            business_operation: Business operation being performed
            user_id: User ID if applicable
            entity_id: Entity ID if applicable
            entity_type: Type of entity (thread, user, etc.)
            **extra_context: Additional context fields
            
        Returns:
            Error ID for tracking
        """
        error_id = str(uuid4())
        
        context = {
            "error_id": error_id,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "business_operation": business_operation,
            "timestamp": datetime.utcnow().isoformat(),
            "category": "business_logic",
            "severity": "medium",
        }
        
        if user_id:
            context["user_id"] = user_id
        if entity_id:
            context["entity_id"] = entity_id
        if entity_type:
            context["entity_type"] = entity_type
            
        context.update(extra_context)
        
        logger.warning(
            f"Business logic error: {business_operation}",
            extra={
                **context,
                "stack_trace": traceback.format_exc(),
                "requires_review": True,
            }
        )
        
        return error_id


def _sanitize_request_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Remove sensitive fields from request data."""
    sensitive_keys = {
        "password", "token", "secret", "api_key", "access_token",
        "refresh_token", "authorization", "credit_card", "ssn",
        "email", "phone", "cpf", "private_key"
    }
    
    if isinstance(data, dict):
        sanitized = {}
        for key, value in data.items():
            if key.lower() in sensitive_keys:
                sanitized[key] = "[REDACTED]"
            elif isinstance(value, dict):
                sanitized[key] = _sanitize_request_data(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    _sanitize_request_data(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                sanitized[key] = value
        return sanitized
    elif isinstance(data, list):
        return [
            _sanitize_request_data(item) if isinstance(item, dict) else item
            for item in data
        ]
    else:
        return data


def _sanitize_url(url: str) -> str:
    """Remove credentials from URL."""
    try:
        from urllib.parse import urlparse, urlunparse
        parsed = urlparse(url)
        # Remove username and password
        sanitized = parsed._replace(netloc=parsed.hostname + (f":{parsed.port}" if parsed.port else ""))
        return urlunparse(sanitized)
    except Exception:
        # Fallback: just return the URL without credentials
        if "@" in url:
            parts = url.split("@")
            if len(parts) > 1:
                return f"[CREDENTIALS_REDACTED]@{parts[-1]}"
        return url


# Convenience functions for common error types
def log_db_error(error: Exception, operation: str, **context) -> str:
    """Convenience function for database errors."""
    return ErrorLogger.log_database_error(error, operation, **context)


def log_api_error(error: Exception, endpoint: str, method: str, **context) -> str:
    """Convenience function for API errors."""
    return ErrorLogger.log_api_error(error, endpoint, method, **context)


def log_service_error(error: Exception, service: str, operation: str, **context) -> str:
    """Convenience function for external service errors."""
    return ErrorLogger.log_external_service_error(error, service, operation, **context)


def log_business_error(error: Exception, operation: str, **context) -> str:
    """Convenience function for business logic errors."""
    return ErrorLogger.log_business_logic_error(error, operation, **context)
