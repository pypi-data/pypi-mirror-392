"""Configuration module for flerity_core.

Provides centralized, deterministic configuration loading from environment variables
with optional .env file support. Framework-agnostic and secure by default.
"""
from __future__ import annotations

import json
import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import Any, TypeVar

T = TypeVar("T")

log = logging.getLogger("flerity.config")

# Secret patterns to mask in logs
SECRET_PATTERNS = ("_KEY", "_TOKEN", "_PASSWORD", "_SECRET", "_DSN")


def _mask_secret(key: str, value: str | None) -> str:
    """Mask sensitive values for logging."""
    if any(pattern in key.upper() for pattern in SECRET_PATTERNS):
        return "***" if value else "None"
    return value or "None"


def _load_env_file() -> None:
    """Load .env file if present."""
    # Look for .env file in current working directory first, then parent directories
    current_dir = Path.cwd()
    env_paths = [
        current_dir / ".env",  # Current directory (e.g., apps/api)
        current_dir.parent / ".env",  # Parent directory (e.g., apps)
        current_dir.parent.parent / ".env"  # Root directory
    ]

    for env_file in env_paths:
        if env_file.exists():
            try:
                with open(env_file) as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            key, value = line.split("=", 1)
                            key, value = key.strip(), value.strip()
                            if key not in os.environ:
                                os.environ[key] = value
                log.debug(f"Loaded .env file from {env_file}")
                return  # Stop after loading the first .env file found
            except Exception as e:
                log.warning(f"Failed to load .env file from {env_file}: {e}")

    log.debug("No .env file found")


def get_env(key: str, default: Any = None, type_: type[Any] = str) -> Any:
    """Get environment variable with type casting and validation.
    
    Args:
        key: Environment variable name
        default: Default value if not found
        type_: Target type for casting
        
    Returns:
        Typed environment variable value
    """
    val = os.getenv(key, default)

    if val is None:
        log.debug(f"Missing env var: {key}")
        return default

    if val == default:
        return default

    try:
        if type_ is bool:
            return str(val).lower() in {"1", "true", "yes", "on"}
        if type_ is list:
            return [x.strip() for x in str(val).split(",") if x.strip()]
        if type_ is dict:
            return json.loads(str(val))
        if type_ in (int, float):
            return type_(val)
        return type_(val)
    except (ValueError, TypeError, json.JSONDecodeError) as e:
        log.error(f"Failed to cast {key}={_mask_secret(key, str(val) if val is not None else None)} to {type_.__name__}: {e}")
        return default


class Config:
    """Global runtime configuration."""

    def __init__(self) -> None:
        # Core app settings
        self.APP_NAME: str = get_env("APP_NAME", "flerity") or "flerity"
        self.ENV: str = get_env("ENV", "dev") or "dev"
        self.DEBUG: bool = get_env("DEBUG", False, bool) or False
        self.LOG_LEVEL: str = get_env("LOG_LEVEL", "INFO") or "INFO"
        self.TZ: str = get_env("TZ", "UTC") or "UTC"

        # Build info
        self.VERSION: str = get_env("VERSION", "1.0.0") or "1.0.0"
        self.BUILD_ID: str = get_env("BUILD_ID", "dev-build") or "dev-build"
        self.BUILD_TIME: str = get_env("BUILD_TIME", "2024-01-01T00:00:00Z") or "2024-01-01T00:00:00Z"

        # Database & Cache
        self.DATABASE_URL: str = get_env("DATABASE_URL", "postgresql://pedroaf@localhost:5432/flerity") or "postgresql://pedroaf@localhost:5432/flerity"
        self.REDIS_URL: str = get_env("REDIS_URL", "redis://localhost:6379/0") or "redis://localhost:6379/0"
        
        # SQS Configuration
        self.SQS_QUEUE_URL: str | None = get_env("SQS_QUEUE_URL", None)

        # Rate limiting
        self.RATE_LIMITING_ENABLED: bool = get_env("RATE_LIMITING_ENABLED", True, bool) or True
        self.RATE_LIMIT_USER_PER_MINUTE: int = get_env("RATE_LIMIT_USER_PER_MINUTE", 10, int) or 10
        self.RATE_LIMIT_USER_PER_HOUR: int = get_env("RATE_LIMIT_USER_PER_HOUR", 100, int) or 100
        self.RATE_LIMIT_PREMIUM_USER_PER_MINUTE: int = get_env("RATE_LIMIT_PREMIUM_USER_PER_MINUTE", 20, int) or 20
        self.RATE_LIMIT_PREMIUM_USER_PER_HOUR: int = get_env("RATE_LIMIT_PREMIUM_USER_PER_HOUR", 200, int) or 200
        self.RATE_LIMIT_GLOBAL_PER_HOUR: int = get_env("RATE_LIMIT_GLOBAL_PER_HOUR", 1000, int) or 1000

        # CORS settings
        self.CORS_ALLOWED_ORIGINS: str | list[str] | None = get_env("CORS_ALLOWED_ORIGINS", None)

        # External services
        self.OPENAI_API_KEY: str | None = get_env("OPENAI_API_KEY", None)
        self.SENTRY_DSN: str | None = get_env("SENTRY_DSN", None)

        # Instagram/Meta integration
        self.META_APP_ID: str | None = get_env("META_APP_ID", None)
        self.META_APP_SECRET: str | None = get_env("META_APP_SECRET", None)

        # Social authentication
        self.APPLE_CLIENT_ID: str | None = get_env("APPLE_CLIENT_ID", None)
        self.APPLE_TEAM_ID: str | None = get_env("APPLE_TEAM_ID", None)
        self.GOOGLE_CLIENT_ID: str | None = get_env("GOOGLE_CLIENT_ID", None)

        # Social auth timeouts (seconds)
        self.SOCIAL_AUTH_TIMEOUT: int = get_env("SOCIAL_AUTH_TIMEOUT", 10, int) or 10

        # Webhook secrets
        self.REVENUECAT_WEBHOOK_SECRET: str | None = get_env("REVENUECAT_WEBHOOK_SECRET", None)
        self.INSTAGRAM_WEBHOOK_SECRET: str | None = get_env("INSTAGRAM_WEBHOOK_SECRET", None)
        self.INSTAGRAM_VERIFY_TOKEN: str | None = get_env("INSTAGRAM_VERIFY_TOKEN", None)
        self.WHATSAPP_WEBHOOK_SECRET: str | None = get_env("WHATSAPP_WEBHOOK_SECRET", None)

        # AWS SNS Push Notifications
        self.AWS_REGION: str = get_env("AWS_REGION", "us-east-1") or "us-east-1"
        self.AWS_SNS_PLATFORM_APPLICATION_ARN_IOS: str | None = get_env(
            "AWS_SNS_PLATFORM_APPLICATION_ARN_IOS",
            "arn:aws:sns:us-east-1:955063685462:app/APNS/Flertify"
        )
        self.AWS_SNS_PLATFORM_APPLICATION_ARN_IOS_SANDBOX: str | None = get_env(
            "AWS_SNS_PLATFORM_APPLICATION_ARN_IOS_SANDBOX", None
        )
        self.AWS_SNS_PLATFORM_APPLICATION_ARN_ANDROID: str | None = get_env(
            "AWS_SNS_PLATFORM_APPLICATION_ARN_ANDROID", None
        )

        # Features
        self.TELEMETRY_ENABLED: bool = get_env("TELEMETRY_ENABLED", True, bool) or True

        # Tracking & Observability Configuration
        self.TRACKING_ENABLED: bool = get_env("TRACKING_ENABLED", True, bool) or True
        self.REQUEST_TRACKING_ENABLED: bool = get_env("REQUEST_TRACKING_ENABLED", True, bool) or True
        self.DOMAIN_LOGGING_ENABLED: bool = get_env("DOMAIN_LOGGING_ENABLED", True, bool) or True
        self.BUSINESS_EVENTS_ENABLED: bool = get_env("BUSINESS_EVENTS_ENABLED", True, bool) or True
        self.ERROR_TRACKING_ENABLED: bool = get_env("ERROR_TRACKING_ENABLED", True, bool) or True
        
        # Sentry Configuration
        self.SENTRY_ENVIRONMENT: str = get_env("SENTRY_ENVIRONMENT", self.ENV) or self.ENV
        self.SENTRY_TRACES_SAMPLE_RATE: float = get_env("SENTRY_TRACES_SAMPLE_RATE", 0.1, float) or 0.1
        self.SENTRY_PROFILES_SAMPLE_RATE: float = get_env("SENTRY_PROFILES_SAMPLE_RATE", 0.1, float) or 0.1
        
        # OpenTelemetry Configuration
        self.OTEL_ENABLED: bool = get_env("OTEL_ENABLED", True, bool) or True
        self.OTEL_SERVICE_NAME: str = get_env("OTEL_SERVICE_NAME", f"{self.APP_NAME}-{self.ENV}") or f"{self.APP_NAME}-{self.ENV}"
        self.OTEL_SERVICE_VERSION: str = get_env("OTEL_SERVICE_VERSION", self.VERSION) or self.VERSION
        self.OTEL_EXPORTER_OTLP_ENDPOINT: str | None = get_env("OTEL_EXPORTER_OTLP_ENDPOINT", None)
        self.OTEL_TRACES_EXPORTER: str = get_env("OTEL_TRACES_EXPORTER", "console") or "console"
        self.OTEL_METRICS_EXPORTER: str = get_env("OTEL_METRICS_EXPORTER", "console") or "console"
        
        # Structured Logging Configuration
        self.LOG_FORMAT: str = get_env("LOG_FORMAT", "json") or "json"  # json or text
        self.LOG_CORRELATION_ID_ENABLED: bool = get_env("LOG_CORRELATION_ID_ENABLED", True, bool) or True
        self.LOG_REQUEST_ID_ENABLED: bool = get_env("LOG_REQUEST_ID_ENABLED", True, bool) or True
        self.LOG_USER_ID_ENABLED: bool = get_env("LOG_USER_ID_ENABLED", True, bool) or True

        # Validate required settings in production
        if self.is_prod:
            self._validate_required()

        self._log_config()

    @property
    def is_prod(self) -> bool:
        """Check if running in production environment."""
        return self.ENV.lower() == "prod"

    @property
    def is_dev(self) -> bool:
        """Check if running in development environment."""
        return self.ENV.lower() == "dev"

    @property
    def log_level(self) -> str:
        """Get appropriate log level based on environment."""
        if self.is_prod:
            return "INFO"
        elif self.ENV.lower() == "staging":
            return "INFO"
        else:
            return "DEBUG"

    @property
    def enable_pii_redaction(self) -> bool:
        """Enable PII redaction in production and staging."""
        return self.is_prod or self.ENV.lower() == "staging"

    def _validate_required(self) -> None:
        """Validate required configuration in production."""
        required = ["DATABASE_URL", "REDIS_URL"]
        missing = [key for key in required if not getattr(self, key, None)]

        if missing:
            raise ValueError(f"Missing required config in production: {missing}")

        # Validate rate limiting settings
        if self.RATE_LIMITING_ENABLED:
            if self.RATE_LIMIT_USER_PER_MINUTE <= 0 or self.RATE_LIMIT_USER_PER_HOUR <= 0:
                raise ValueError("Rate limit values must be positive integers")

        # Validate social auth configuration
        if not self.APPLE_CLIENT_ID:
            log.warning("APPLE_CLIENT_ID not configured - Apple login will be disabled")
        if not self.GOOGLE_CLIENT_ID:
            log.warning("GOOGLE_CLIENT_ID not configured - Google login will be disabled")
            
        # Validate tracking configuration
        if self.TRACKING_ENABLED and not self.SENTRY_DSN:
            log.warning("SENTRY_DSN not configured - error tracking will be limited")
            
        # Validate OpenTelemetry configuration
        if self.OTEL_ENABLED and self.OTEL_TRACES_EXPORTER not in ["console", "otlp", "jaeger"]:
            log.warning(f"Invalid OTEL_TRACES_EXPORTER: {self.OTEL_TRACES_EXPORTER}")
            
        # Validate sample rates
        if not (0.0 <= self.SENTRY_TRACES_SAMPLE_RATE <= 1.0):
            raise ValueError("SENTRY_TRACES_SAMPLE_RATE must be between 0.0 and 1.0")
        if not (0.0 <= self.SENTRY_PROFILES_SAMPLE_RATE <= 1.0):
            raise ValueError("SENTRY_PROFILES_SAMPLE_RATE must be between 0.0 and 1.0")

    def _log_config(self) -> None:
        """Log current configuration (with secrets masked)."""
        config_items = []
        for key, value in self.__dict__.items():
            if not key.startswith("_"):
                masked_value = _mask_secret(key, str(value)) if value else None
                config_items.append(f"{key}={masked_value}")

        log.info(f"Config loaded: ENV={self.ENV}, {', '.join(config_items[:3])}...")

    def reload(self) -> None:
        """Reload configuration from environment."""
        _load_env_file()
        # Create a new instance and copy its attributes
        new_config = Config()
        self.__dict__.update(new_config.__dict__)


@lru_cache(maxsize=1)
def _create_config() -> Config:
    """Create singleton config instance."""
    _load_env_file()
    return Config()


def reload_config() -> Config:
    """Reload configuration and return new instance."""
    _create_config.cache_clear()
    return _create_config()


# Global config instance
config = _create_config()
