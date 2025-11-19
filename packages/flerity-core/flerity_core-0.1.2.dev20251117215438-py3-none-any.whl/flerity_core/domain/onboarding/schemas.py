"""Onboarding domain Pydantic schemas and DTOs."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import Column, Index, MetaData, Table, text
from sqlalchemy.dialects.postgresql import ENUM, JSONB, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PGUUID

# SQLAlchemy table definition
metadata = MetaData()

# Define enum types to match database
onb_step_enum = ENUM(
    'welcome', 'consent', 'profile', 'preferences',
    'connect_channels', 'enable_notification', 'done',
    name='onb_step_enum'
)

onb_status_enum = ENUM(
    'not_started', 'in_progress', 'completed', 'skipped', 'blocked',
    name='onb_status_enum'
)

onboarding_steps_table = Table(
    "onboarding_steps", metadata,
    Column("user_id", PGUUID, nullable=False, primary_key=True),
    Column("step", onb_step_enum, nullable=False, primary_key=True),
    Column("status", onb_status_enum, nullable=False),
    Column("payload", JSONB),
    Column("updated_at", TIMESTAMP(timezone=True), nullable=False, server_default=text('now()')),

    # Indexes for performance
    Index('ix_onboarding_steps_user_updated', 'user_id', 'updated_at'),
    Index('ix_onboarding_steps_user_status', 'user_id', 'status'),
)


OnboardingStep = Literal["welcome", "consent", "profile", "preferences", "connect_channels", "enable_notification", "done"]
OnboardingStatus = Literal["not_started", "in_progress", "completed", "skipped", "blocked"]


class OnboardingStepOut(BaseModel):
    """DTO for onboarding step output."""
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    step: OnboardingStep
    status: OnboardingStatus
    payload: dict[str, Any] | None = None
    updated_at: datetime


class StepInfo(BaseModel):
    """DTO for step information."""
    name: OnboardingStep
    title: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=500)
    skippable: bool = True
    required: bool = False
    requires_data: bool = False

    @field_validator('title', 'description')
    @classmethod
    def validate_non_empty_strings(cls, v: str) -> str:
        """Validate that string fields are not empty."""
        if not v or not v.strip():
            raise ValueError('String fields cannot be empty')
        return v.strip()


class OnboardingProgressOut(BaseModel):
    """DTO for onboarding progress output."""
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    progress_percent: int = Field(..., ge=0, le=100)
    completed_steps: list[OnboardingStep] = Field(default_factory=list)
    skipped_steps: list[OnboardingStep] = Field(default_factory=list)
    current_step: OnboardingStep | None = None
    total_steps: int = Field(default=7, ge=1)
    steps: list[StepInfo] = Field(default_factory=list)
    is_completed: bool = Field(default=False)

    @field_validator('progress_percent')
    @classmethod
    def validate_progress_percent(cls, v: int) -> int:
        """Validate progress percentage is within valid range."""
        if not 0 <= v <= 100:
            raise ValueError('Progress percent must be between 0 and 100')
        return v


class OnboardingStepCreate(BaseModel):
    """DTO for creating onboarding step."""
    user_id: UUID
    step: OnboardingStep
    status: OnboardingStatus = "not_started"
    payload: dict[str, Any] | None = Field(None, max_length=16384)

    @field_validator('payload')
    @classmethod
    def validate_payload_size(cls, v: dict[str, Any] | None) -> dict[str, Any] | None:
        """Validate payload size doesn't exceed limits."""
        if v is not None and len(str(v)) > 16384:
            raise ValueError('Payload too large (max 16KB)')
        return v


class OnboardingStepUpdate(BaseModel):
    """DTO for updating onboarding step."""
    status: OnboardingStatus
    payload: dict[str, Any] | None = Field(None, max_length=16384)

    @field_validator('payload')
    @classmethod
    def validate_payload_size(cls, v: dict[str, Any] | None) -> dict[str, Any] | None:
        """Validate payload size doesn't exceed limits."""
        if v is not None and len(str(v)) > 16384:
            raise ValueError('Payload too large (max 16KB)')
        return v


# Export table definitions for repository use
__all__ = [
    "OnboardingStep", "OnboardingStatus",
    "OnboardingStepOut", "OnboardingProgressOut", "OnboardingStepCreate", "OnboardingStepUpdate",
    "StepInfo", "onboarding_steps_table"
]
