"""Integrations domain Pydantic schemas and DTOs."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import (
    CheckConstraint,
    Column,
    ForeignKey,
    MetaData,
    Table,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PGUUID

# SQLAlchemy table definitions
metadata = MetaData()

integrations_accounts_table = Table(
    "integrations_accounts", metadata,
    Column("id", PGUUID, primary_key=True, server_default=text('gen_random_uuid()')),
    Column("user_id", PGUUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
    Column("provider", Text, nullable=False, index=True),
    Column("external_user_id", Text),
    Column("status", Text, nullable=False),
    Column("meta", JSONB),
    Column("connected_at", TIMESTAMP(timezone=True)),
    Column("disconnected_at", TIMESTAMP(timezone=True)),
    Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default=text('now()')),
    Column("updated_at", TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'), index=True),
    UniqueConstraint("user_id", "provider", name="integrations_accounts_user_provider_key"),
    CheckConstraint("provider IN ('instagram', 'whatsapp')", name="provider_valid"),
    CheckConstraint("status IN ('connected', 'disconnected', 'pending')", name="status_valid"),
)

whatsapp_pairing_sessions_table = Table(
    "whatsapp_pairing_sessions", metadata,
    Column("id", PGUUID, primary_key=True, server_default=text('gen_random_uuid()')),
    Column("user_id", PGUUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
    Column("session_code", Text, nullable=False, unique=True),
    Column("expires_at", TIMESTAMP(timezone=True), nullable=False, index=True),
    Column("status", Text, nullable=False),
    Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'), index=True),
    Column("updated_at", TIMESTAMP(timezone=True), nullable=False, server_default=text('now()')),
    CheckConstraint("status IN ('issued', 'consumed', 'expired', 'cancelled')", name="pairing_status_valid"),
    CheckConstraint("length(session_code) > 0", name="session_code_not_empty"),
    CheckConstraint("expires_at > created_at", name="expires_after_created"),
)


IntegrationType = Literal["instagram", "whatsapp"]
IntegrationStatus = Literal["connected", "disconnected", "pending"]


class IntegrationAccountOut(BaseModel):
    """DTO for integration account output."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    provider: IntegrationType
    external_user_id: str | None = None
    status: IntegrationStatus
    meta: dict[str, Any] | None = None
    connected_at: datetime | None = None
    disconnected_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class IntegrationAccountCreate(BaseModel):
    """DTO for creating integration account."""
    user_id: UUID | None = None  # Optional, can be set from RLS context
    provider: IntegrationType
    external_user_id: str | None = Field(None, max_length=255)
    status: IntegrationStatus = "pending"
    meta: dict[str, Any] | None = None
    connected_at: datetime | None = None

    @field_validator('external_user_id')
    @classmethod
    def validate_external_user_id(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            from ...utils.errors import BadRequest
            raise BadRequest('External user ID cannot be empty')
        return v.strip() if v else None


class IntegrationAccountUpdate(BaseModel):
    """DTO for updating integration account."""
    external_user_id: str | None = Field(None, max_length=255)
    status: IntegrationStatus | None = None
    meta: dict[str, Any] | None = None
    connected_at: datetime | None = None
    disconnected_at: datetime | None = None

    @field_validator('external_user_id')
    @classmethod
    def validate_external_user_id(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            from ...utils.errors import BadRequest
            raise BadRequest('External user ID cannot be empty')
        return v.strip() if v else None


class IntegrationListResponse(BaseModel):
    """DTO for integration list."""
    integrations: list[IntegrationAccountOut]


# WhatsApp pairing schemas
PairingStatus = Literal["issued", "consumed", "expired", "cancelled"]


class WhatsAppPairingSessionOut(BaseModel):
    """DTO for WhatsApp pairing session output."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    session_code: str = Field(min_length=1, max_length=50)
    expires_at: datetime
    status: PairingStatus
    created_at: datetime
    updated_at: datetime | None = None


class WhatsAppPairingSessionCreate(BaseModel):
    """DTO for creating WhatsApp pairing session."""
    user_id: UUID | None = None  # Optional, can be set from RLS context
    session_code: str = Field(min_length=1, max_length=50)
    expires_at: datetime
    status: PairingStatus = "issued"

    @field_validator('session_code')
    @classmethod
    def validate_session_code(cls, v: str) -> str:
        if not v or not v.strip():
            from ...utils.errors import BadRequest
            raise BadRequest('Session code cannot be empty')
        return v.strip()


class WhatsAppPairingSessionUpdate(BaseModel):
    """DTO for updating WhatsApp pairing session."""
    status: PairingStatus | None = None


# Export table definitions for repository use
__all__ = [
    "IntegrationType", "IntegrationStatus", "PairingStatus",
    "IntegrationAccountOut", "IntegrationAccountCreate", "IntegrationAccountUpdate",
    "IntegrationListResponse", "WhatsAppPairingSessionOut", "WhatsAppPairingSessionCreate", "WhatsAppPairingSessionUpdate",
    "integrations_accounts_table", "whatsapp_pairing_sessions_table"
]
