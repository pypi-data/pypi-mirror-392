"""
Domain-level exception classes for Flerity backend services.

This module provides a structured error hierarchy that can be used across
API, worker, and webhook services. All exceptions are JSON-serializable
and include HTTP status code mappings for web frameworks.
"""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from fastapi import FastAPI, Request


class AppError(Exception):
    """Base class for all domain-level application errors.
    
    Provides structured error information that can be serialized to JSON
    and mapped to appropriate HTTP status codes.
    """

    def __init__(
        self,
        message: str,
        code: str | None = None,
        status_code: int | None = None,
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code or self._default_code()
        self.status_code = status_code or self._default_status_code()
        self.details = details or {}

    def _default_code(self) -> str:
        """Generate default error code from class name."""
        return self.__class__.__name__.replace("Error", "").lower() + "_error"

    def _default_status_code(self) -> int:
        """Default HTTP status code for this error type."""
        return 500

    def to_dict(self) -> dict[str, Any]:
        """Convert error to JSON-serializable dictionary."""
        error_dict: dict[str, Any] = {
            "code": self.code,
            "message": self.message,
        }
        if self.details:
            error_dict["details"] = self.details

        return {"error": error_dict}


class ValidationError(AppError):
    """Raised when input validation fails."""

    def _default_status_code(self) -> int:
        return 400


class UnauthorizedError(AppError):
    """Raised when authentication is required but missing or invalid."""

    def _default_status_code(self) -> int:
        return 401


class ForbiddenError(AppError):
    """Raised when user lacks permission for the requested operation."""

    def _default_status_code(self) -> int:
        return 403


class NotFoundError(AppError):
    """Raised when a requested resource cannot be found."""

    def _default_status_code(self) -> int:
        return 404


class ConflictError(AppError):
    """Raised when operation conflicts with current resource state."""

    def _default_status_code(self) -> int:
        return 409


class RateLimitError(AppError):
    """Raised when rate limits are exceeded."""

    def _default_code(self) -> str:
        return "rate_limit_exceeded"

    def _default_status_code(self) -> int:
        return 429


class QuotaExceededError(AppError):
    """Raised when usage quota limits are exceeded."""

    def __init__(
        self,
        quota_type: str,
        current_usage: int,
        limit: int,
        reset_time: str | None = None,
        message: str | None = None,
        thread_id: str | None = None,
        locale: str | None = None,
    ):
        from datetime import datetime

        if message is None:
            message = self._generate_descriptive_message(quota_type, current_usage, limit, thread_id, locale)

        details = {
            "quota_type": quota_type,
            "current_usage": current_usage,
            "limit": limit,
            "upgrade_required": True,
            "upgrade_benefits": self._get_upgrade_benefits(quota_type, locale),
            "upgrade_message": self._get_upgrade_message(quota_type, locale)
        }

        if reset_time:
            if isinstance(reset_time, datetime):
                details["reset_time"] = reset_time.isoformat()
            else:
                details["reset_time"] = reset_time

        if thread_id:
            details["thread_id"] = thread_id

        super().__init__(message=message, details=details)

    def _generate_descriptive_message(
        self,
        quota_type: str,
        current_usage: int,
        limit: int,
        thread_id: str | None = None,
        locale: str | None = None
    ) -> str:
        """Generate descriptive error message based on quota type using i18n."""
        try:
            from flerity_core.utils.i18n import t

            # Use trial-specific message for limits typical of trial users
            if limit <= 10:  # Typical trial limits
                key = f"quota.exceeded.{quota_type}.trial"
                return t(key, locale=locale, limit=limit, current_usage=current_usage)
            else:
                key = f"quota.exceeded.{quota_type}.general"
                return t(key, locale=locale, limit=limit, current_usage=current_usage)
        except Exception:
            # Fallback to English if i18n fails
            quota_messages = {
                "icebreaker": {
                    "trial": f"You've reached your daily limit of {limit} icebreaker requests. Upgrade to get 50 icebreakers per day!",
                    "general": f"Daily icebreaker limit reached ({current_usage}/{limit}). Your quota will reset tomorrow."
                },
                "suggestion": {
                    "trial": f"You've reached your daily limit of {limit} suggestion requests. Upgrade to get 50 suggestions per day!",
                    "general": f"Daily suggestion limit reached ({current_usage}/{limit}). Your quota will reset tomorrow."
                },
                "thread": {
                    "trial": f"You've reached the maximum of {limit} conversation threads. Upgrade for unlimited threads!",
                    "general": f"Thread limit reached ({current_usage}/{limit}). Please delete some threads or upgrade your plan."
                }
            }

            if quota_type in quota_messages:
                if limit <= 10:  # Typical trial limits
                    return quota_messages[quota_type]["trial"]
                else:
                    return quota_messages[quota_type]["general"]

            # Final fallback message
            return f"{quota_type.title()} quota exceeded: {current_usage}/{limit}"

    def _get_upgrade_benefits(self, quota_type: str, locale: str | None = None) -> list[str]:
        """Get list of upgrade benefits based on quota type using i18n."""
        try:
            from flerity_core.utils.i18n import t

            key = f"quota.upgrade.benefits.{quota_type}"
            benefits = t(key, locale=locale)

            # If translation returns the key (not found), use fallback
            if benefits == key:
                raise ValueError("Translation not found")

            # The translation should be a list, but t() returns a string
            # We need to handle this differently - let's use fallback for now
            raise ValueError("Use fallback")

        except Exception:
            # Fallback to English benefits
            benefits_map = {
                "icebreaker": [
                    "50 icebreaker requests per day (vs 10 per thread)",
                    "Unlimited conversation threads",
                    "Advanced AI suggestions",
                    "Priority support"
                ],
                "suggestion": [
                    "50 suggestion requests per day (vs 10 per thread)",
                    "Unlimited conversation threads",
                    "Advanced AI suggestions",
                    "Priority support"
                ],
                "thread": [
                    "Unlimited conversation threads (vs 3)",
                    "50 AI requests per day total",
                    "Advanced AI suggestions",
                    "Priority support"
                ]
            }

            return benefits_map.get(quota_type, [
                "Unlimited access to premium features",
                "Higher usage limits",
                "Priority support"
            ])

    def _get_upgrade_message(self, quota_type: str, locale: str | None = None) -> str:
        """Get upgrade call-to-action message using i18n."""
        try:
            from flerity_core.utils.i18n import t

            key = f"quota.upgrade.messages.{quota_type}"
            return t(key, locale=locale)
        except Exception:
            # Fallback to English messages
            messages = {
                "icebreaker": "Upgrade to Premium to get 5x more icebreakers and unlimited threads!",
                "suggestion": "Upgrade to Premium to get 5x more suggestions and unlimited threads!",
                "thread": "Upgrade to Premium for unlimited threads and 50 AI requests per day!"
            }

            return messages.get(quota_type, "Upgrade to Premium for unlimited access to all features!")

    def _default_code(self) -> str:
        return "quota_exceeded"

    def _default_status_code(self) -> int:
        return 429


class DependencyError(AppError):
    """Raised when external dependency fails."""

    def _default_code(self) -> str:
        return "dependency_failed"

    def _default_status_code(self) -> int:
        return 424


class InternalError(AppError):
    """Raised for unexpected internal errors."""

    def _default_status_code(self) -> int:
        return 500


class ServiceUnavailableError(AppError):
    """Raised when service is temporarily unavailable."""

    def _default_code(self) -> str:
        return "service_unavailable"

    def _default_status_code(self) -> int:
        return 503


# HTTP status code mapping for all error types
ERROR_HTTP_MAP: dict[type[AppError], int] = {
    ValidationError: 400,
    UnauthorizedError: 401,
    ForbiddenError: 403,
    NotFoundError: 404,
    ConflictError: 409,
    RateLimitError: 429,
    QuotaExceededError: 429,
    DependencyError: 424,
    InternalError: 500,
    ServiceUnavailableError: 503,
}


def http_status_for_error(exc: Exception) -> int:
    """Get HTTP status code for an exception.
    
    Args:
        exc: Exception instance
        
    Returns:
        HTTP status code (defaults to 500 for unknown errors)
    """
    if isinstance(exc, AppError):
        return exc.status_code

    # Check if exception type is in our mapping
    exc_type = type(exc)
    for error_type, status_code in ERROR_HTTP_MAP.items():
        if exc_type == error_type:
            return status_code
    return 500


def register_error_handlers(app: "FastAPI") -> None:
    """Register FastAPI exception handlers for all domain errors.
    
    Args:
        app: FastAPI application instance
    """
    try:
        from fastapi.responses import JSONResponse
    except ImportError:
        raise ImportError("FastAPI is required for error handler registration")

    for exc_cls in ERROR_HTTP_MAP:
        @app.exception_handler(exc_cls)
        async def _handler(request: "Request", exc: AppError) -> JSONResponse:
            return JSONResponse(
                status_code=exc.status_code,
                content=exc.to_dict(),
            )


# Convenience aliases for common patterns
BadRequest = ValidationError
Unauthorized = UnauthorizedError
Forbidden = ForbiddenError
NotFound = NotFoundError
Conflict = ConflictError
TooManyRequests = RateLimitError
FailedDependency = DependencyError
