"""Notification domain Pydantic schemas and DTOs."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator
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
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PGUUID

# SQLAlchemy table definitions
metadata = MetaData()

notifications_table = Table(
    "notifications", metadata,
    Column("id", PGUUID, primary_key=True, server_default=text('gen_random_uuid()')),
    Column("user_id", PGUUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
    Column("title", Text, nullable=False),
    Column("body", Text, nullable=False),
    Column("type", Text, nullable=False, index=True),
    Column("metadata", JSONB),
    Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'), index=True),
    Column("read_at", TIMESTAMP(timezone=True)),
    CheckConstraint("length(title) > 0", name="title_not_empty"),
    CheckConstraint("length(body) > 0", name="body_not_empty"),
    CheckConstraint("length(type) > 0", name="type_not_empty"),
    Index("idx_notifications_user_unread", "user_id", "read_at", postgresql_where=text("read_at IS NULL")),
)

notif_outbox_table = Table(
    "notif_outbox", metadata,
    Column("id", PGUUID, primary_key=True, server_default=text('gen_random_uuid()')),
    Column("key", Text, nullable=False, unique=True),
    Column("payload", JSONB, nullable=False),
    Column("status", Text, nullable=False, index=True),
    Column("attempts", Integer, nullable=False, server_default=text('0')),
    Column("retry_count", Integer, nullable=False, server_default=text('0')),
    Column("last_error", Text),
    Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'), index=True),
    Column("updated_at", TIMESTAMP(timezone=True), nullable=False, server_default=text('now()')),
    CheckConstraint("status IN ('queued', 'sent', 'failed', 'discarded')", name="outbox_status_valid"),
    CheckConstraint("length(key) > 0", name="outbox_key_not_empty"),
    CheckConstraint("attempts >= 0", name="attempts_non_negative"),
    CheckConstraint("retry_count >= 0", name="retry_count_non_negative"),
)

notif_templates_table = Table(
    "notif_templates", metadata,
    Column("id", PGUUID, primary_key=True, server_default=text('gen_random_uuid()')),
    Column("channel", Text, nullable=False, index=True),
    Column("name", Text, nullable=False),
    Column("version", Text, nullable=False),
    Column("locale", Text, nullable=False),
    Column("subject", Text),
    Column("body", Text, nullable=False),
    Column("checksum", Text, nullable=False),
    Column("active", Boolean, nullable=False, server_default=text('true'), index=True),
    Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default=text('now()')),
    UniqueConstraint("channel", "name", "version", "locale", name="templates_unique_key"),
    CheckConstraint("channel IN ('email', 'push')", name="template_channel_valid"),
    CheckConstraint("length(name) > 0", name="template_name_not_empty"),
    CheckConstraint("length(version) > 0", name="template_version_not_empty"),
    CheckConstraint("length(body) > 0", name="template_body_not_empty"),
)

notif_deliveries_table = Table(
    "notif_deliveries", metadata,
    Column("id", PGUUID, primary_key=True, server_default=text('gen_random_uuid()')),
    Column("outbox_id", PGUUID, ForeignKey("notif_outbox.id", ondelete="CASCADE"), nullable=False, index=True),
    Column("channel", Text, nullable=False, index=True),
    Column("provider", Text, nullable=False),
    Column("recipient", Text, nullable=False),
    Column("status", Text, nullable=False, index=True),
    Column("error_code", Text),
    Column("provider_msg_id", Text),
    Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'), index=True),
    CheckConstraint("length(channel) > 0", name="delivery_channel_not_empty"),
    CheckConstraint("length(provider) > 0", name="delivery_provider_not_empty"),
    CheckConstraint("length(recipient) > 0", name="delivery_recipient_not_empty"),
    CheckConstraint("length(status) > 0", name="delivery_status_not_empty"),
)


class NotificationOut(BaseModel):
    """DTO for notification output."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    title: str = Field(min_length=1, max_length=255)
    body: str = Field(min_length=1, max_length=2000)
    type: str = Field(min_length=1, max_length=50)
    metadata: dict[str, Any] | None = None
    created_at: datetime
    read_at: datetime | None = None


class NotificationCreate(BaseModel):
    """DTO for creating notification."""
    user_id: UUID | None = None  # Optional, can be set from RLS context
    title: str = Field(min_length=1, max_length=255)
    body: str = Field(min_length=1, max_length=2000)
    type: str = Field(min_length=1, max_length=50)
    metadata: dict[str, Any] | None = None

    @field_validator('title', 'body', 'type')
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            from ...utils.errors import BadRequest
            raise BadRequest('Field cannot be empty')
        return v.strip()


class NotificationUpdate(BaseModel):
    """DTO for updating notification."""
    title: str | None = Field(None, min_length=1, max_length=255)
    body: str | None = Field(None, min_length=1, max_length=2000)
    type: str | None = Field(None, min_length=1, max_length=50)
    metadata: dict[str, Any] | None = None

    @field_validator('title', 'body', 'type')
    @classmethod
    def validate_not_empty(cls, v: str | None) -> str | None:
        if v is not None and (not v or not v.strip()):
            from ...utils.errors import BadRequest
            raise BadRequest('Field cannot be empty')
        return v.strip() if v else None


class NotificationListResponse(BaseModel):
    """DTO for paginated notification list."""
    notifications: list[NotificationOut]
    next_cursor: str | None = None


class MarkAsReadRequest(BaseModel):
    """DTO for marking notifications as read."""
    notification_ids: list[UUID] = Field(alias="notificationIds")


# Outbox schemas
OutboxStatus = Literal["queued", "sent", "failed", "discarded"]


class NotificationOutboxOut(BaseModel):
    """DTO for notification outbox output."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    key: str = Field(min_length=1, max_length=255)
    payload: dict[str, Any]
    status: OutboxStatus
    attempts: int = 0
    retry_count: int = 0
    last_error: str | None = None
    created_at: datetime
    updated_at: datetime


class NotificationOutboxCreate(BaseModel):
    """DTO for creating outbox entry."""
    key: str = Field(min_length=1, max_length=255)
    payload: dict[str, Any]

    @field_validator('key')
    @classmethod
    def validate_key(cls, v: str) -> str:
        if not v or not v.strip():
            from ...utils.errors import BadRequest
            raise BadRequest('Key cannot be empty')
        return v.strip()


class NotificationOutboxUpdate(BaseModel):
    """DTO for updating outbox entry."""
    status: OutboxStatus | None = None
    last_error: str | None = None


# Template schemas
TemplateChannel = Literal["email", "push"]


class NotificationTemplateOut(BaseModel):
    """DTO for notification template output."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    channel: TemplateChannel
    name: str
    version: str
    locale: str
    subject: str | None = None
    body: str
    checksum: str
    active: bool = True
    created_at: datetime


class NotificationTemplateCreate(BaseModel):
    """DTO for creating notification template."""
    channel: TemplateChannel
    name: str
    version: str
    locale: str
    subject: str | None = None
    body: str
    checksum: str
    active: bool = True


class NotificationTemplateUpdate(BaseModel):
    """DTO for updating notification template."""
    subject: str | None = None
    body: str | None = None
    checksum: str | None = None
    active: bool | None = None


# Delivery schemas
class NotificationDeliveryOut(BaseModel):
    """DTO for notification delivery output."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    outbox_id: UUID
    channel: str
    provider: str
    recipient: str
    status: str
    error_code: str | None = None
    provider_msg_id: str | None = None
    created_at: datetime


class NotificationDeliveryCreate(BaseModel):
    """DTO for creating notification delivery."""
    outbox_id: UUID
    channel: str
    provider: str
    recipient: str
    status: str
    error_code: str | None = None
    provider_msg_id: str | None = None


# Export table definitions for repository use
__all__ = [
    "NotificationOut", "NotificationCreate", "NotificationUpdate", "NotificationListResponse", "MarkAsReadRequest",
    "OutboxStatus", "NotificationOutboxOut", "NotificationOutboxCreate", "NotificationOutboxUpdate",
    "TemplateChannel", "NotificationTemplateOut", "NotificationTemplateCreate", "NotificationTemplateUpdate",
    "NotificationDeliveryOut", "NotificationDeliveryCreate",
    "notifications_table", "notif_outbox_table", "notif_templates_table", "notif_deliveries_table"
]
