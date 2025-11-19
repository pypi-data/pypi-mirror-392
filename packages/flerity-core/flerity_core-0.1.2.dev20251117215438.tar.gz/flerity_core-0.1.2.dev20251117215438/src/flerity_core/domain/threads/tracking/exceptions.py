"""Thread tracking domain-specific exceptions."""


class ThreadTrackingException(Exception):
    """Base exception for thread tracking operations."""
    pass


class ThreadNotFound(ThreadTrackingException):
    """Raised when thread is not found."""
    pass


class TrackingConfigurationExists(ThreadTrackingException):
    """Raised when trying to create duplicate tracking configuration."""
    pass


class UnauthorizedTrackingAccess(ThreadTrackingException):
    """Raised when user tries to access tracking config they don't own."""
    pass
