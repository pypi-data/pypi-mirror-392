"""Devices domain Pydantic schemas and DTOs."""

from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

import sqlalchemy as sa
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    ForeignKey,
    MetaData,
    Table,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PGUUID

# SQLAlchemy table definition
metadata = MetaData()

# Define the platform enum to match the database
platform_enum = sa.Enum('ios', 'android', 'web', name='platform_enum', create_type=False)

devices_table = Table(
    "devices", metadata,
    Column("id", PGUUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
    Column("user_id", PGUUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
    Column("device_id", Text, nullable=False),
    Column("platform", platform_enum, nullable=False, index=True),
    Column("push_token", Text, nullable=False),
    Column("app_version", Text),
    Column("os_version", Text),
    Column("device_model", Text),
    Column("locale", Text),
    Column("timezone", Text),
    Column("is_sandbox", Boolean, nullable=False, server_default=sa.text("false")),
    Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    Column("updated_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()"), index=True),
    UniqueConstraint("user_id", "device_id", name="devices_user_id_device_id_key"),
    CheckConstraint("length(device_id) > 0", name="device_id_not_empty"),
    CheckConstraint("length(push_token) > 0", name="push_token_not_empty"),
)

Platform = Literal["ios", "android", "web"]


class DeviceOut(BaseModel):
    """DTO for device output."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    device_id: str = Field(min_length=1, max_length=255)
    platform: Platform
    push_token: str = Field(min_length=1, max_length=1024)
    app_version: str | None = Field(None, max_length=50)
    os_version: str | None = Field(None, max_length=50)
    device_model: str | None = Field(None, max_length=100)
    locale: str | None = Field(None, pattern=r'^[a-z]{2}(-[A-Z]{2})?$')
    timezone: str | None = Field(None, max_length=50)
    is_sandbox: bool = False
    created_at: datetime
    updated_at: datetime


class DeviceCreate(BaseModel):
    """DTO for creating/upserting a device."""
    id: UUID | None = None
    user_id: UUID | None = None
    device_id: str = Field(min_length=1, max_length=255)
    platform: Platform
    push_token: str = Field(min_length=1, max_length=1024)
    app_version: str | None = Field(None, max_length=50)
    os_version: str | None = Field(None, max_length=50)
    device_model: str | None = Field(None, max_length=100)
    locale: str | None = Field(None, pattern=r'^[a-z]{2}(-[A-Z]{2})?$')
    timezone: str | None = Field(None, max_length=50)
    is_sandbox: bool = False

    @field_validator('device_id')
    @classmethod
    def validate_device_id(cls, v: str) -> str:
        if not v or not v.strip():
            from ...utils.errors import BadRequest
            raise BadRequest('Device ID cannot be empty')
        return v.strip()

    @field_validator('push_token')
    @classmethod
    def validate_push_token(cls, v: str) -> str:
        if not v or not v.strip():
            from ...utils.errors import BadRequest
            raise BadRequest('Push token cannot be empty')
        return v.strip()


class DeviceUpdate(BaseModel):
    """DTO for updating a device."""
    push_token: str | None = Field(None, min_length=1, max_length=1024)
    app_version: str | None = Field(None, max_length=50)
    os_version: str | None = Field(None, max_length=50)
    device_model: str | None = Field(None, max_length=100)
    locale: str | None = Field(None, pattern=r'^[a-z]{2}(-[A-Z]{2})?$')
    timezone: str | None = Field(None, max_length=50)
    is_sandbox: bool | None = None

    @field_validator('push_token')
    @classmethod
    def validate_push_token(cls, v: str | None) -> str | None:
        if v is not None:
            if not v or not v.strip():
                from ...utils.errors import BadRequest
                raise BadRequest('Push token cannot be empty')
            return v.strip()
        return None


# Export schemas and tables for repository use
__all__ = [
    "Platform",
    "DeviceOut", "DeviceCreate", "DeviceUpdate",
    "devices_table"
]
