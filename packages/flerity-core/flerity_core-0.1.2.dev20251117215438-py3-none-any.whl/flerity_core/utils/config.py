"""Configuration management for authentication settings."""

import os


class AuthConfig:
    """Authentication configuration settings."""

    @property
    def access_token_expire_minutes(self) -> int:
        return int(os.getenv("AUTH_ACCESS_TOKEN_EXPIRE_MINUTES", "15"))

    @property
    def refresh_token_expire_days(self) -> int:
        return int(os.getenv("AUTH_REFRESH_TOKEN_EXPIRE_DAYS", "7"))

    @property
    def password_reset_expire_minutes(self) -> int:
        return int(os.getenv("AUTH_PASSWORD_RESET_EXPIRE_MINUTES", "120"))

    @property
    def email_verification_expire_hours(self) -> int:
        return int(os.getenv("AUTH_EMAIL_VERIFICATION_EXPIRE_HOURS", "24"))

    @property
    def max_login_attempts(self) -> int:
        return int(os.getenv("AUTH_MAX_LOGIN_ATTEMPTS", "5"))

    @property
    def lockout_duration_minutes(self) -> int:
        return int(os.getenv("AUTH_LOCKOUT_DURATION_MINUTES", "30"))

    @property
    def bcrypt_rounds(self) -> int:
        return int(os.getenv("AUTH_BCRYPT_ROUNDS", "12"))

    @property
    def jwt_private_key(self) -> str | None:
        return os.getenv("JWT_PRIVATE_KEY")

    @property
    def jwt_public_key(self) -> str | None:
        return os.getenv("JWT_PUBLIC_KEY")


class EmailConfig:
    """Email service configuration settings."""

    @property
    def sendgrid_api_key(self) -> str | None:
        return os.getenv("SENDGRID_API_KEY")

    @property
    def sendgrid_from_email(self) -> str:
        return os.getenv("SENDGRID_FROM_EMAIL", "us@flerity.com")

    @property
    def app_base_url(self) -> str:
        return os.getenv("APP_BASE_URL", "https://app.flerity.com")


# Global config instances
auth_config = AuthConfig()
email_config = EmailConfig()
