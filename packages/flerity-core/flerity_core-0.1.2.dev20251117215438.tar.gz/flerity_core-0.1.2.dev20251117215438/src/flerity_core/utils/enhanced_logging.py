"""Enhanced logging utilities with Sentry integration and structured error context."""

import sentry_sdk
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import uuid4

from .logging import get_safe_logger
from .error_logging import ErrorLogger


class EnhancedErrorLogger(ErrorLogger):
    """Enhanced error logger with Sentry integration and improved context."""
    
    @staticmethod
    def log_subscription_error(
        error: Exception,
        operation: str,
        user_id: Optional[str] = None,
        subscription_tier: Optional[str] = None,
        revenuecat_subscriber_id: Optional[str] = None,
        **extra_context: Any
    ) -> str:
        """Log subscription-specific errors with enhanced context.
        
        Args:
            error: The subscription exception
            operation: Subscription operation (get_status, sync_revenuecat, etc.)
            user_id: User ID if applicable
            subscription_tier: Current subscription tier
            revenuecat_subscriber_id: RevenueCat subscriber ID
            **extra_context: Additional context fields
            
        Returns:
            Error ID for tracking
        """
        error_id = str(uuid4())
        
        context = {
            "error_id": error_id,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "subscription_operation": operation,
            "timestamp": datetime.utcnow().isoformat(),
            "category": "subscription",
            "severity": "high",
            "component": "subscription_service",
        }
        
        if user_id:
            context["user_id"] = user_id
        if subscription_tier:
            context["subscription_tier"] = subscription_tier
        if revenuecat_subscriber_id:
            context["revenuecat_subscriber_id"] = revenuecat_subscriber_id
            
        # Add operation-specific context
        if operation == "get_subscription_status":
            context["actionable_steps"] = [
                "Check RevenueCat API connectivity",
                "Verify subscriber ID exists",
                "Check subscription cache"
            ]
        elif operation == "sync_revenuecat":
            context["actionable_steps"] = [
                "Verify RevenueCat webhook configuration",
                "Check API credentials",
                "Review subscription data consistency"
            ]
        elif operation == "quota_check":
            context["actionable_steps"] = [
                "Verify quota limits configuration",
                "Check usage calculation logic",
                "Review subscription tier mapping"
            ]
            
        context.update(extra_context)
        
        logger = get_safe_logger("flerity.subscription.service")
        logger.error(
            f"Subscription operation failed: {operation} (Error ID: {error_id})",
            extra=context
        )
        
        # Send to Sentry with structured context
        with sentry_sdk.push_scope() as scope:
            scope.set_tag("error_category", "subscription")
            scope.set_tag("operation", operation)
            scope.set_context("subscription", {
                "user_id": user_id,
                "tier": subscription_tier,
                "revenuecat_id": revenuecat_subscriber_id,
                "error_id": error_id
            })
            sentry_sdk.capture_exception(error)
        
        return error_id
    
    @staticmethod
    def log_push_notification_error(
        error: Exception,
        operation: str,
        platform: Optional[str] = None,
        user_id: Optional[str] = None,
        push_token: Optional[str] = None,
        **extra_context: Any
    ) -> str:
        """Log push notification errors with enhanced context.
        
        Args:
            error: The push notification exception
            operation: Push operation (create_endpoint, send_notification, etc.)
            platform: Platform (ios, android)
            user_id: User ID if applicable
            push_token: Push token (will be masked)
            **extra_context: Additional context fields
            
        Returns:
            Error ID for tracking
        """
        error_id = str(uuid4())
        
        context = {
            "error_id": error_id,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "push_operation": operation,
            "timestamp": datetime.utcnow().isoformat(),
            "category": "push_notifications",
            "severity": "high",
            "component": "push_sender",
        }
        
        if platform:
            context["platform"] = platform
        if user_id:
            context["user_id"] = user_id
        if push_token:
            # Mask push token for security
            context["push_token_prefix"] = push_token[:8] + "..." if len(push_token) > 8 else "[MASKED]"
            
        # Add operation-specific context
        if operation == "create_sns_endpoint":
            context["actionable_steps"] = [
                "Verify AWS SNS platform application ARN configuration",
                "Check push token validity",
                "Review AWS credentials and permissions"
            ]
            context["aws_service"] = "SNS"
        elif operation == "send_notification":
            context["actionable_steps"] = [
                "Check SNS endpoint status",
                "Verify message payload format",
                "Review platform-specific requirements"
            ]
        elif operation == "platform_arn_missing":
            context["actionable_steps"] = [
                "Configure platform application ARN in environment",
                "Verify AWS SNS platform application setup",
                "Check environment variable naming"
            ]
            context["severity"] = "critical"
            
        context.update(extra_context)
        
        logger = get_safe_logger("flerity.notifications.push_sender")
        logger.error(
            f"Push notification failed: {operation} (Error ID: {error_id})",
            extra=context
        )
        
        # Send to Sentry with structured context
        with sentry_sdk.push_scope() as scope:
            scope.set_tag("error_category", "push_notifications")
            scope.set_tag("operation", operation)
            scope.set_tag("platform", platform or "unknown")
            scope.set_context("push_notification", {
                "user_id": user_id,
                "platform": platform,
                "error_id": error_id,
                "has_token": bool(push_token)
            })
            sentry_sdk.capture_exception(error)
        
        return error_id


# Convenience functions for enhanced logging
def log_subscription_error(error: Exception, operation: str, **context) -> str:
    """Convenience function for subscription errors."""
    return EnhancedErrorLogger.log_subscription_error(error, operation, **context)


def log_push_error(error: Exception, operation: str, **context) -> str:
    """Convenience function for push notification errors."""
    return EnhancedErrorLogger.log_push_notification_error(error, operation, **context)
