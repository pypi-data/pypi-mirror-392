"""Threads domain Pydantic schemas and DTOs."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

import sqlalchemy as sa
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import (
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
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PGUUID

# SQLAlchemy table definitions
metadata = MetaData()

# Define the channel enum to match the database
channel_enum = sa.Enum('instagram', 'whatsapp', name='channel_enum', create_type=False)

threads_table = Table(
    "threads", metadata,
    Column("id", PGUUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
    Column("user_id", PGUUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("channel", Text, nullable=False),
    Column("contact_id", Text, nullable=True),
    Column("contact_name", Text, nullable=True),
    Column("contact_handle", Text, nullable=True),
    Column("contact_profile_pic", Text, nullable=True),
    Column("last_activity", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    Column("unread_count", Integer, nullable=False, default=0),
    Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    Column("updated_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),

    # Constraints
    CheckConstraint("unread_count >= 0", name="threads_unread_count_check"),
    UniqueConstraint("user_id", "channel", "contact_id", name="threads_user_channel_contact_unique"),

    # Indexes for performance
    Index("idx_threads_user_last_activity", "user_id", "last_activity"),
    Index("idx_threads_channel_user", "channel", "user_id"),
    Index("idx_threads_contact_id", "contact_id"),
)

messages_table = Table(
    "messages", metadata,
    Column("id", PGUUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
    Column("thread_id", PGUUID, ForeignKey("threads.id", ondelete="CASCADE"), nullable=False),
    Column("sender", Text, nullable=False),
    Column("text", Text, nullable=True),
    Column("media", JSONB, nullable=True),
    Column("timestamp", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    Column("metadata", JSONB, nullable=True),
    Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),

    # Constraints
    CheckConstraint("sender IN ('user', 'contact', 'assistant', 'system')", name="messages_sender_check"),
    CheckConstraint("text IS NOT NULL OR media IS NOT NULL", name="messages_content_check"),

    # Indexes for performance
    Index("idx_messages_thread_timestamp", "thread_id", "timestamp"),
    Index("idx_messages_sender", "sender"),
)


Channel = Literal["instagram", "whatsapp"]
Direction = Literal["forward", "backward"]
MessageSender = Literal["user", "contact", "assistant", "system"]


class ThreadOut(BaseModel):
    """DTO for thread output."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    channel: Channel
    contact_id: str | None = None
    contact_name: str | None = Field(None, max_length=255)
    contact_handle: str | None = Field(None, max_length=100)
    contact_profile_pic: str | None = None
    last_activity: datetime
    unread_count: int = Field(default=0, ge=0)
    is_tracking_enabled: bool = Field(default=False, description="Whether AI tracking is enabled for this thread")
    created_at: datetime
    updated_at: datetime


class MessageOut(BaseModel):
    """DTO for message output."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    thread_id: UUID
    sender: MessageSender
    text: str | None = Field(None, max_length=10000)
    media: dict[str, Any] | None = None
    timestamp: datetime
    metadata: dict[str, Any] | None = None


class ThreadListResponse(BaseModel):
    """DTO for paginated thread list."""
    threads: list[ThreadOut]
    next_cursor: str | None = None


class MessageListResponse(BaseModel):
    """DTO for paginated message list."""
    messages: list[MessageOut]
    next_cursor: str | None = None


class ThreadCreate(BaseModel):
    """DTO for creating a thread."""
    id: UUID | None = None
    user_id: UUID | None = None
    channel: Channel
    contact_id: str | None = None
    contact_name: str | None = Field(None, max_length=255)
    contact_handle: str | None = Field(None, max_length=100)
    contact_profile_pic: str | None = None
    last_activity: datetime | None = None
    unread_count: int = Field(default=0, ge=0)


class ThreadUpdate(BaseModel):
    """DTO for updating a thread."""
    contact_name: str | None = Field(None, max_length=255)
    contact_handle: str | None = Field(None, max_length=100)
    contact_profile_pic: str | None = None
    unread_count: int | None = Field(None, ge=0)


class MessageCreate(BaseModel):
    """DTO for creating a message."""
    id: UUID | None = None
    thread_id: UUID
    sender: MessageSender = "user"
    text: str | None = Field(None, max_length=10000)
    media: dict[str, Any] | None = None
    timestamp: datetime | None = None
    metadata: dict[str, Any] | None = None


class ThreadDeletionResult(BaseModel):
    """DTO for thread deletion result."""
    thread_id: UUID
    deleted_at: datetime
    message_count: int
    tracking_config_deleted: bool = False


class ThreadDeletionPreview(BaseModel):
    """DTO for thread deletion preview."""
    thread_id: UUID
    thread_name: str | None = None
    message_count: int
    has_tracking_config: bool = False
    estimated_deletion_time: float = 0.0  # seconds


# Export schemas and tables for repository use
__all__ = [
    "Channel", "Direction", "MessageSender",
    "ThreadOut", "MessageOut", "ThreadListResponse", "MessageListResponse",
    "ThreadCreate", "ThreadUpdate", "MessageCreate",
    "ThreadDeletionResult", "ThreadDeletionPreview",
    "threads_table", "messages_table"
]
