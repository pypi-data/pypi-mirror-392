"""Thread tracking domain Pydantic schemas and DTOs."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from pydantic import BaseModel, ConfigDict
from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Index,
    MetaData,
    Table,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PGUUID

# SQLAlchemy table definition
metadata = MetaData()

thread_tracking_configurations_table = Table(
    "thread_tracking_configurations", metadata,
    Column("id", PGUUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
    Column("user_id", PGUUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("thread_id", PGUUID, ForeignKey("threads.id", ondelete="CASCADE"), nullable=False),
    Column("is_active", Boolean, nullable=False, default=True),
    Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    Column("updated_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),

    # Constraints
    UniqueConstraint("user_id", "thread_id", name="thread_tracking_user_thread_unique"),

    # Indexes for performance
    Index("idx_thread_tracking_user_id", "user_id"),
    Index("idx_thread_tracking_thread_id", "thread_id"),
    Index("idx_thread_tracking_active", "is_active", postgresql_where=sa.text("is_active = true")),
    # Composite indexes for common query patterns
    Index("idx_thread_tracking_user_active", "user_id", "is_active"),
    Index("idx_thread_tracking_user_created", "user_id", "created_at"),
    # Index for MessagesTab thread ordering queries
    Index("idx_thread_tracking_thread_active", "thread_id", "is_active"),
)


class ThreadTrackingConfigurationBase(BaseModel):
    """Base schema for thread tracking configuration."""
    thread_id: UUID
    is_active: bool = True


class ThreadTrackingConfigurationCreate(ThreadTrackingConfigurationBase):
    """Schema for creating a thread tracking configuration."""
    user_id: UUID | None = None  # Will be set from authenticated user context


class ThreadTrackingConfigurationUpdate(BaseModel):
    """Schema for updating a thread tracking configuration."""
    is_active: bool


class ThreadTrackingConfiguration(ThreadTrackingConfigurationBase):
    """Schema for thread tracking configuration output."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime


# Export schemas and table for repository use
__all__ = [
    "ThreadTrackingConfiguration",
    "ThreadTrackingConfigurationCreate",
    "ThreadTrackingConfigurationUpdate",
    "thread_tracking_configurations_table",
]
