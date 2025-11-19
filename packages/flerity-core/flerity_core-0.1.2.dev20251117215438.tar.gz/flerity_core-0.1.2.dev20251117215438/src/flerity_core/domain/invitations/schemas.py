"""Invitations domain Pydantic schemas and DTOs."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    ForeignKey,
    Integer,
    MetaData,
    Table,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import INET, JSONB, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PGUUID

# SQLAlchemy table definitions
metadata = MetaData()

invitation_codes_table = Table(
    "invitation_codes", metadata,
    Column("id", PGUUID, primary_key=True, server_default=text('gen_random_uuid()')),
    Column("code", Text, nullable=False, unique=True),
    Column("type", Text, nullable=False),
    Column("max_uses", Integer, nullable=False, server_default=text('1')),
    Column("current_uses", Integer, nullable=False, server_default=text('0')),
    Column("expires_at", TIMESTAMP(timezone=True)),
    Column("created_by", PGUUID, ForeignKey("users.id")),
    Column("is_active", Boolean, nullable=False, server_default=text('true')),
    Column("metadata", JSONB),
    Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default=text('now()')),
    Column("updated_at", TIMESTAMP(timezone=True), nullable=False, server_default=text('now()')),
    CheckConstraint("type IN ('free', 'premium', 'trial')", name="invitation_code_type_valid"),
    CheckConstraint("max_uses > 0", name="invitation_code_max_uses_positive"),
    CheckConstraint("current_uses >= 0", name="invitation_code_current_uses_non_negative"),
)

invitation_code_usage_table = Table(
    "invitation_code_usage", metadata,
    Column("id", PGUUID, primary_key=True, server_default=text('gen_random_uuid()')),
    Column("invitation_code", Text, ForeignKey("invitation_codes.code"), nullable=False),
    Column("user_id", PGUUID, ForeignKey("users.id"), nullable=False),
    Column("used_at", TIMESTAMP(timezone=True), nullable=False, server_default=text('now()')),
    Column("ip_address", INET),
    Column("user_agent", Text),
)


InvitationCodeType = Literal["free", "premium", "trial"]


class InvitationCodeOut(BaseModel):
    """DTO for invitation code output."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    type: InvitationCodeType
    max_uses: int
    current_uses: int
    expires_at: datetime | None = None
    created_by: UUID | None = None
    is_active: bool
    metadata: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime


class InvitationCodeCreate(BaseModel):
    """DTO for creating invitation codes."""

    type: InvitationCodeType
    max_uses: int = Field(default=1, ge=1, le=1000)
    expires_at: datetime | None = None
    metadata: dict[str, Any] | None = None


class InvitationCodeUsageOut(BaseModel):
    """DTO for invitation code usage output."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    invitation_code: str
    user_id: UUID
    used_at: datetime
    ip_address: str | None = None
    user_agent: str | None = None


class InvitationCodeValidation(BaseModel):
    """DTO for invitation code validation."""

    code: str = Field(min_length=1, max_length=50)


class InvitationCodeStats(BaseModel):
    """DTO for invitation code statistics."""

    total_codes: int
    active_codes: int
    total_uses: int
    conversion_rate: float
