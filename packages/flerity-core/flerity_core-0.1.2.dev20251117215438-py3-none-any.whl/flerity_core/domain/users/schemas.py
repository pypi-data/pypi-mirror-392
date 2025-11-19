"""Users domain schemas."""

from datetime import datetime
from typing import Any
from uuid import UUID

import sqlalchemy as sa
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from sqlalchemy import Column, Index, MetaData, Table, Text
from sqlalchemy.dialects.postgresql import CITEXT, JSONB, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PGUUID

metadata = MetaData()

users_table = Table(
    "users", metadata,
    Column("id", PGUUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
    Column("email", CITEXT, nullable=False, unique=True),
    Column("email_verified", sa.Boolean, default=False),
    Column("gender", Text),
    Column("country", Text),
    Column("city", Text),
    Column("state", Text),
    Column("locale", Text, default='en-US'),
    Column("timezone", Text, default='UTC'),
    Column("bio", Text),
    Column("tone", Text, default='friendly'),
    Column("role", Text, nullable=False, server_default=sa.text("'user'")),
    Column("auth_provider", sa.String(20), default='email'),
    Column("avatar_url", sa.String(500)),
    Column("invitation_code_used", Text),
    Column("birth_month", sa.Integer),
    Column("birth_year", sa.Integer),
    Column("preferences", JSONB, nullable=True, default={}),
    Column("last_login_at", TIMESTAMP(timezone=True)),
    Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
    Column("updated_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
    Column("deleted_at", TIMESTAMP(timezone=True)),

    # Indexes for performance
    Index('ix_users_email', 'email'),
    Index('ix_users_created_at', 'created_at'),
    Index('ix_users_deleted_at', 'deleted_at'),
    Index('ix_users_role', 'role'),
    Index('ix_users_last_login_at', 'last_login_at'),
    Index('ix_users_tone', 'tone'),
    Index('ix_users_birth_year', 'birth_year'),
    Index('ix_users_city', 'city'),
    Index('ix_users_state', 'state'),
)

class CreateUserRequest(BaseModel):
    """Create user request."""
    email: EmailStr
    gender: str | None = Field(None, max_length=50)
    country: str | None = Field(None, max_length=2, min_length=2)
    city: str | None = Field(None, max_length=100)
    state: str | None = Field(None, max_length=100)
    bio: str | None = Field(None, max_length=500)

    @field_validator('gender')
    @classmethod
    def validate_gender(cls, v: str | None) -> str | None:
        """Validate gender field."""
        if v is None:
            return v
        v = v.strip()
        if not v:
            return None
        allowed_genders = {'male', 'female', 'non-binary', 'other', 'prefer-not-to-say'}
        if v.lower() not in allowed_genders:
            raise ValueError(f"Gender must be one of: {', '.join(allowed_genders)}")
        return v.lower()

    @field_validator('country')
    @classmethod
    def validate_country(cls, v: str | None) -> str | None:
        """Validate country code (ISO 3166-1 alpha-2)."""
        if v is None:
            return v
        v = v.strip().upper()
        if not v:
            return None
        if len(v) != 2 or not v.isalpha():
            raise ValueError('Country must be a valid ISO 3166-1 alpha-2 code')
        return v

    @field_validator('city', 'state')
    @classmethod
    def validate_location_field(cls, v: str | None) -> str | None:
        """Validate city and state fields."""
        if v is None:
            return v
        v = v.strip()
        return v if v else None

    @field_validator('bio')
    @classmethod
    def validate_bio(cls, v: str | None) -> str | None:
        """Validate bio field."""
        if v is None:
            return v
        v = v.strip()
        return v if v else None

class UserUpdate(BaseModel):
    """User update DTO."""
    email: EmailStr | None = None
    gender: str | None = Field(None, max_length=50)
    country: str | None = Field(None, max_length=2, min_length=2)
    city: str | None = Field(None, max_length=100)
    state: str | None = Field(None, max_length=100)
    locale: str | None = Field(None, max_length=10)
    timezone: str | None = Field(None, max_length=50)
    bio: str | None = Field(None, max_length=500)
    tone: str | None = Field(None, max_length=20)
    birth_month: int | None = Field(None, ge=1, le=12, description="Birth month (1-12)")
    birth_year: int | None = Field(None, ge=1900, description="Birth year")
    preferences: dict[str, Any] | None = None

    @field_validator('gender')
    @classmethod
    def validate_gender(cls, v: str | None) -> str | None:
        """Validate gender field."""
        if v is None:
            return v
        v = v.strip()
        if not v:
            return None
        allowed_genders = {'male', 'female', 'non-binary', 'other', 'prefer-not-to-say'}
        if v.lower() not in allowed_genders:
            raise ValueError(f"Gender must be one of: {', '.join(allowed_genders)}")
        return v.lower()

    @field_validator('tone')
    @classmethod
    def validate_tone(cls, v: str | None) -> str | None:
        """Validate tone field."""
        if v is None:
            return v
        v = v.strip().lower()
        if not v:
            return None
        allowed_tones = {'friendly', 'witty', 'empathetic', 'professional'}
        if v not in allowed_tones:
            raise ValueError(f"Tone must be one of: {', '.join(allowed_tones)}")
        return v

    @field_validator('country')
    @classmethod
    def validate_country(cls, v: str | None) -> str | None:
        """Validate country code (ISO 3166-1 alpha-2)."""
        if v is None:
            return v
        v = v.strip().upper()
        if not v:
            return None
        if len(v) != 2 or not v.isalpha():
            raise ValueError('Country must be a valid ISO 3166-1 alpha-2 code')
        return v

    @field_validator('city', 'state')
    @classmethod
    def validate_location_field(cls, v: str | None) -> str | None:
        """Validate city and state fields."""
        if v is None:
            return v
        v = v.strip()
        return v if v else None

    @field_validator('locale')
    @classmethod
    def validate_locale(cls, v: str | None) -> str | None:
        """Validate locale format (e.g., en-US, pt-BR)."""
        if v is None:
            return v
        v = v.strip()
        if not v:
            return None
        if '-' not in v or len(v) < 5:
            raise ValueError('Locale must be in format language-country (e.g., en-US)')
        return v

    @field_validator('timezone')
    @classmethod
    def validate_timezone(cls, v: str | None) -> str | None:
        """Validate timezone format."""
        if v is None:
            return v
        v = v.strip()
        if not v:
            return None
        # Basic validation - could be enhanced with pytz validation
        if len(v) > 50:
            raise ValueError('Timezone name too long')
        return v

    @field_validator('bio')
    @classmethod
    def validate_bio(cls, v: str | None) -> str | None:
        """Validate bio field."""
        if v is None:
            return v
        v = v.strip()
        return v if v else None

    @field_validator('birth_year')
    @classmethod
    def validate_birth_year(cls, v: int | None) -> int | None:
        """Validate birth year."""
        if v is None:
            return v
        from datetime import datetime
        current_year = datetime.now().year
        if v > current_year:
            raise ValueError('Birth year cannot be in the future')
        return v

class UserOut(BaseModel):
    """User output DTO."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    email_verified: bool = False
    gender: str | None = None
    country: str | None = None
    city: str | None = None
    state: str | None = None
    locale: str | None = 'en-US'
    timezone: str | None = 'UTC'
    bio: str | None = None
    tone: str | None = 'friendly'
    role: str = 'user'
    invitation_code_used: str | None = None
    birth_month: int | None = None
    birth_year: int | None = None
    preferences: dict[str, Any] | None = Field(default_factory=dict)
    last_login_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class UserPreferencesOut(BaseModel):
    """User preferences output DTO."""
    user_id: UUID
    preferences: dict[str, Any] = Field(default_factory=dict)
    topics: list[dict[str, Any]] = Field(default_factory=list, description="User selected topics")
    avoid: list[dict[str, Any]] = Field(default_factory=list, description="User avoid preferences")
    updated_at: datetime


class UserPreferencesUpdate(BaseModel):
    """User preferences update DTO."""
    language: str | None = Field(None, max_length=10)
    timezone: str | None = Field(None, max_length=50)
    notifications_enabled: bool | None = None
    email_notifications: bool | None = None
    push_notifications: bool | None = None
    tracking_notifications_enabled: bool | None = None
    ai_suggestions_enabled: bool | None = None
    theme: str | None = Field(None, max_length=20)

    @field_validator('language')
    @classmethod
    def validate_language(cls, v: str | None) -> str | None:
        """Validate language code."""
        if v is None:
            return v
        v = v.strip()
        if not v:
            return None
        # Basic validation for language codes
        if len(v) < 2 or len(v) > 10:
            raise ValueError('Language code must be 2-10 characters')
        return v

    @field_validator('theme')
    @classmethod
    def validate_theme(cls, v: str | None) -> str | None:
        """Validate theme selection."""
        if v is None:
            return v
        v = v.strip().lower()
        if not v:
            return None
        allowed_themes = {'light', 'dark', 'auto', 'system'}
        if v not in allowed_themes:
            raise ValueError(f"Theme must be one of: {', '.join(allowed_themes)}")
        return v


# Export schemas and table for repository use
__all__ = [
    'CreateUserRequest', 'UserUpdate', 'UserOut',
    'UserPreferencesOut', 'UserPreferencesUpdate',
    'users_table'
]
