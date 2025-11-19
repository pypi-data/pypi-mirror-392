"""Authentication domain Pydantic schemas and SQLAlchemy table definitions."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from uuid import UUID

import sqlalchemy as sa
from pydantic import BaseModel, ConfigDict, EmailStr, Field, ValidationInfo, field_validator
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    ForeignKey,
    Index,
    Integer,
    MetaData,
    Table,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import CITEXT, INET, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PGUUID

# SQLAlchemy table definitions
metadata = MetaData()

user_credentials_table = Table(
    "user_credentials", metadata,
    Column("user_id", PGUUID, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("password_hash", Text, nullable=False),
    Column("password_salt", Text, nullable=False),
    Column("email_verified", Boolean, nullable=False, default=False),
    Column("email_verified_at", TIMESTAMP(timezone=True)),
    Column("password_changed_at", TIMESTAMP(timezone=True), nullable=False),
    Column("failed_attempts", Integer, nullable=False, default=0),
    Column("locked_until", TIMESTAMP(timezone=True)),
    Column("created_at", TIMESTAMP(timezone=True), nullable=False),
    Column("updated_at", TIMESTAMP(timezone=True), nullable=False),
    CheckConstraint("failed_attempts >= 0", name="failed_attempts_positive"),
    Index("idx_user_credentials_locked_until", "locked_until"),
    Index("idx_user_credentials_email_verified", "email_verified"),
)

user_refresh_tokens_table = Table(
    "user_refresh_tokens", metadata,
    Column("id", PGUUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
    Column("user_id", PGUUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("token_hash", Text, nullable=False),
    Column("device_id", Text),
    Column("expires_at", TIMESTAMP(timezone=True), nullable=False),
    Column("revoked_at", TIMESTAMP(timezone=True)),
    Column("last_used_at", TIMESTAMP(timezone=True)),
    Column("created_at", TIMESTAMP(timezone=True), nullable=False),
    UniqueConstraint("token_hash"),
    CheckConstraint("expires_at > created_at", name="expires_future"),
    Index("idx_refresh_tokens_user_id", "user_id"),
    Index("idx_refresh_tokens_expires_at", "expires_at"),
    Index("idx_refresh_tokens_revoked_at", "revoked_at"),
)

jwt_blacklist_table = Table(
    "jwt_blacklist", metadata,
    Column("jti", Text, primary_key=True),
    Column("user_id", PGUUID, ForeignKey("users.id", ondelete="CASCADE")),
    Column("expires_at", TIMESTAMP(timezone=True), nullable=False),
    Column("revoked_at", TIMESTAMP(timezone=True), nullable=False),
    Column("reason", Text),
    Index("idx_jwt_blacklist_expires_at", "expires_at"),
    Index("idx_jwt_blacklist_user_id", "user_id"),
)

password_reset_tokens_table = Table(
    "password_reset_tokens", metadata,
    Column("id", PGUUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
    Column("user_id", PGUUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("token_hash", Text, nullable=False),
    Column("expires_at", TIMESTAMP(timezone=True), nullable=False),
    Column("used_at", TIMESTAMP(timezone=True)),
    Column("created_at", TIMESTAMP(timezone=True), nullable=False),
    UniqueConstraint("token_hash"),
    Index("idx_password_reset_user_id", "user_id"),
    Index("idx_password_reset_expires_at", "expires_at"),
)

email_verification_tokens_table = Table(
    "email_verification_tokens", metadata,
    Column("id", PGUUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
    Column("user_id", PGUUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("token_hash", Text, nullable=False),
    Column("email", CITEXT, nullable=False),
    Column("expires_at", TIMESTAMP(timezone=True), nullable=False),
    Column("verified_at", TIMESTAMP(timezone=True)),
    Column("created_at", TIMESTAMP(timezone=True), nullable=False),
    UniqueConstraint("token_hash"),
    Index("idx_email_verification_user_id", "user_id"),
    Index("idx_email_verification_expires_at", "expires_at"),
)

user_sessions_table = Table(
    "user_sessions", metadata,
    Column("id", PGUUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
    Column("user_id", PGUUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("device_id", Text),
    Column("ip_address", INET),
    Column("user_agent", Text),
    Column("started_at", TIMESTAMP(timezone=True), nullable=False),
    Column("last_activity_at", TIMESTAMP(timezone=True), nullable=False),
    Column("ended_at", TIMESTAMP(timezone=True)),
    Index("idx_user_sessions_user_id", "user_id"),
    Index("idx_user_sessions_last_activity", "last_activity_at"),
    Index("idx_user_sessions_ended_at", "ended_at"),
)


# Enums
class TokenType(str, Enum):
    access = "access"
    refresh = "refresh"
    password_reset = "password_reset"
    email_verification = "email_verification"


# Request Models
class LoginRequest(BaseModel):
    """User login request."""
    email: EmailStr
    password: str = Field(min_length=1, max_length=128, description="User password")
    device_id: str | None = Field(None, max_length=255, description="Device identifier")
    remember_me: bool = False


class RegisterRequest(BaseModel):
    """User registration request."""
    email: EmailStr
    password: str = Field(min_length=8, max_length=128, description="User password")
    confirm_password: str = Field(max_length=128, description="Password confirmation")
    gender: str | None = Field(None, pattern=r'^(male|female|non_binary|other|prefer_not_say)$', description="User gender")
    country: str | None = Field(None, min_length=2, max_length=2, description="ISO country code")
    birth_month: int | None = Field(None, ge=1, le=12, description="Birth month (1-12)")
    birth_year: int | None = Field(None, ge=1900, description="Birth year")
    invitation_code: str | None = Field(None, min_length=1, max_length=50, description="Optional invitation code")

    @field_validator('confirm_password')
    @classmethod
    def passwords_match(cls, v: str, info: ValidationInfo) -> str:
        if 'password' in info.data and v != info.data['password']:
            raise ValueError('Passwords do not match')
        return v

    @field_validator('birth_year')
    @classmethod
    def validate_birth_year(cls, v: int | None) -> int | None:
        if v is None:
            return v
        from datetime import datetime
        current_year = datetime.now().year
        if v > current_year:
            raise ValueError('Birth year cannot be in the future')
        return v


class RefreshTokenRequest(BaseModel):
    """Refresh token request."""
    refresh_token: str = Field(min_length=1, max_length=1024, description="Refresh token")


class ChangePasswordRequest(BaseModel):
    """Change password request for logged-in users."""
    current_password: str = Field(min_length=1, max_length=128, description="Current password")
    new_password: str = Field(min_length=8, max_length=128, description="New password")
    confirm_password: str = Field(max_length=128, description="Password confirmation")

    @field_validator('confirm_password')
    @classmethod
    def passwords_match(cls, v: str, info: ValidationInfo) -> str:
        if 'new_password' in info.data and v != info.data['new_password']:
            raise ValueError('Passwords do not match')
        return v


class PasswordResetRequest(BaseModel):
    """Password reset request."""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation."""
    token: str = Field(min_length=1, max_length=255, description="Reset token")
    new_password: str = Field(min_length=8, max_length=128, description="New password")
    confirm_password: str = Field(max_length=128, description="Password confirmation")

    @field_validator('confirm_password')
    @classmethod
    def passwords_match(cls, v: str, info: ValidationInfo) -> str:
        if 'new_password' in info.data and v != info.data['new_password']:
            raise ValueError('Passwords do not match')
        return v


# Response Models
class AuthTokenPair(BaseModel):
    """JWT token pair response."""
    access_token: str = Field(min_length=1, description="JWT access token")
    refresh_token: str = Field(min_length=1, description="JWT refresh token")
    expires_in: int = Field(gt=0, description="Access token expiration in seconds")
    token_type: str = Field(default="Bearer", pattern=r'^Bearer$', description="Token type")


class UserProfile(BaseModel):
    """User profile in auth context."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    email_verified: bool
    gender: str | None = None
    country: str | None = None
    created_at: datetime
    last_login_at: datetime | None = None


class AuthResponse(BaseModel):
    """Authentication response."""
    user: UserProfile
    tokens: AuthTokenPair
    session_id: UUID | None = None


class TokenClaims(BaseModel):
    """JWT token claims."""
    sub: UUID = Field(description="User ID")
    email: str = Field(min_length=1, max_length=255, description="User email")
    iat: int = Field(gt=0, description="Issued at timestamp")
    exp: int = Field(gt=0, description="Expiration timestamp")
    jti: str = Field(min_length=1, max_length=255, description="JWT ID for revocation")
    type: TokenType = TokenType.access
    device_id: str | None = Field(None, max_length=255, description="Device identifier")


class TokenValidationResult(BaseModel):
    """Token validation result."""
    valid: bool
    user_id: UUID | None = None
    claims: TokenClaims | None = None
    error: str | None = None


# DTOs for repository layer
class UserCredentialsOut(BaseModel):
    """User credentials DTO."""
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    password_hash: str
    password_salt: str
    email_verified: bool
    email_verified_at: datetime | None = None
    failed_attempts: int = 0
    locked_until: datetime | None = None
    password_changed_at: datetime
    created_at: datetime
    updated_at: datetime


class RefreshTokenOut(BaseModel):
    """Refresh token DTO."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    token_hash: str
    device_id: str | None = None
    expires_at: datetime
    revoked_at: datetime | None = None
    last_used_at: datetime | None = None
    created_at: datetime


class SessionOut(BaseModel):
    """User session DTO."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    device_id: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    started_at: datetime
    last_activity_at: datetime
    ended_at: datetime | None = None


class PasswordResetTokenOut(BaseModel):
    """Password reset token DTO."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    token_hash: str
    expires_at: datetime
    used_at: datetime | None = None
    created_at: datetime


class EmailVerificationTokenOut(BaseModel):
    """Email verification token DTO."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    token_hash: str
    email: str
    expires_at: datetime
    verified_at: datetime | None = None
    created_at: datetime


# Social authentication table
social_accounts_table = Table(
    "social_accounts", metadata,
    Column("id", PGUUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
    Column("user_id", PGUUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("provider", Text, nullable=False),
    Column("provider_user_id", Text, nullable=False),
    Column("email", Text),
    Column("name", Text),
    Column("avatar_url", Text),
    Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    Column("updated_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    CheckConstraint("provider IN ('apple', 'google')", name="valid_provider"),
    UniqueConstraint("provider", "provider_user_id", name="social_accounts_provider_user_unique"),
    Index("idx_social_accounts_user_id", "user_id"),
    Index("idx_social_accounts_provider", "provider", "provider_user_id"),
)


# Social authentication schemas
class SocialProvider(str, Enum):
    apple = "apple"
    google = "google"


class SocialLoginRequest(BaseModel):
    """Social login request."""
    provider: SocialProvider
    access_token: str = Field(min_length=1, max_length=2048, description="Provider access token")
    email: EmailStr | None = Field(None, description="User email from provider")
    name: str | None = Field(None, max_length=255, description="User name from provider")
    provider_user_id: str = Field(min_length=1, max_length=255, description="Provider user ID")

    @field_validator('provider_user_id')
    @classmethod
    def validate_provider_user_id(cls, v: str) -> str:
        # Remove whitespace and validate format
        v = v.strip()
        if not v:
            raise ValueError('Provider user ID cannot be empty')
        # Basic alphanumeric validation (providers use different formats)
        if not v.replace('-', '').replace('_', '').replace('.', '').isalnum():
            raise ValueError('Invalid provider user ID format')
        return v


class SocialUserInfo(BaseModel):
    """Social user information from provider."""
    provider_user_id: str
    email: str | None = None
    name: str | None = None
    avatar_url: str | None = None
    email_verified: bool = False


class SocialAuthResponse(BaseModel):
    """Social authentication response."""
    user: UserProfile
    tokens: AuthTokenPair
    is_new_user: bool
    linked_accounts: list[str] = Field(description="List of linked social providers")
    session_id: UUID | None = None


class SocialAccountOut(BaseModel):
    """Social account DTO."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    provider: str
    provider_user_id: str
    email: str | None = None
    name: str | None = None
    avatar_url: str | None = None
    created_at: datetime
    updated_at: datetime


# Export table definitions for repository use
__all__ = [
    # Request/Response models
    "LoginRequest", "RegisterRequest", "RefreshTokenRequest",
    "PasswordResetRequest", "PasswordResetConfirm", "ChangePasswordRequest",
    "AuthTokenPair", "UserProfile", "AuthResponse", "TokenClaims", "TokenValidationResult",
    # Social auth models
    "SocialLoginRequest", "SocialUserInfo", "SocialAuthResponse", "SocialAccountOut", "SocialProvider",
    # DTOs
    "UserCredentialsOut", "RefreshTokenOut", "SessionOut",
    "PasswordResetTokenOut", "EmailVerificationTokenOut",
    # Enums
    "TokenType",
    # Tables
    "user_credentials_table", "user_refresh_tokens_table", "jwt_blacklist_table",
    "password_reset_tokens_table", "email_verification_tokens_table", "user_sessions_table",
    "social_accounts_table"
]
