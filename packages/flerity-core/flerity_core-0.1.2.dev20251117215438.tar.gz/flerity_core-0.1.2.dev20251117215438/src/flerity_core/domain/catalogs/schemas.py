"""Catalogs domain Pydantic schemas and SQLAlchemy table definitions."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import Boolean, Column, ForeignKey, Index, MetaData, Table, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PGUUID

# SQLAlchemy table definitions
metadata = MetaData()

topics_table = Table(
    "topics", metadata,
    Column("topic_id", PGUUID, primary_key=True),
    Column("name", Text, nullable=False),
    Column("description", Text, nullable=False),
    Column("active", Boolean, nullable=False, default=True),
    Column("created_at", TIMESTAMP(timezone=True), nullable=False),
    Index("idx_topics_active", "active"),
    Index("idx_topics_name", "name"),
    Index("idx_topics_created_at", "created_at"),
)

avoid_table = Table(
    "avoid", metadata,
    Column("avoid_id", PGUUID, primary_key=True),
    Column("description", Text, nullable=False),
    Column("active", Boolean, nullable=False, default=True),
    Column("created_at", TIMESTAMP(timezone=True), nullable=False),
    Index("idx_avoid_active", "active"),
    Index("idx_avoid_description", "description"),
    Index("idx_avoid_created_at", "created_at"),
)

user_topics_table = Table(
    "user_topics", metadata,
    Column("user_id", PGUUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("topic_id", PGUUID, ForeignKey("topics.topic_id", ondelete="CASCADE"), nullable=False),
    Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default="now()"),
    UniqueConstraint("user_id", "topic_id", name="uq_user_topics"),
    Index("idx_user_topics_user_id", "user_id"),
    Index("idx_user_topics_topic_id", "topic_id"),
)

user_avoid_table = Table(
    "user_avoid", metadata,
    Column("user_id", PGUUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("avoid_id", PGUUID, ForeignKey("avoid.avoid_id", ondelete="CASCADE"), nullable=False),
    Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default="now()"),
    UniqueConstraint("user_id", "avoid_id", name="uq_user_avoid"),
    Index("idx_user_avoid_user_id", "user_id"),
    Index("idx_user_avoid_avoid_id", "avoid_id"),
)


class TopicOut(BaseModel):
    """DTO for topic output."""
    model_config = ConfigDict(from_attributes=True)

    topic_id: UUID
    name: str = Field(min_length=1, max_length=120, description="Topic name")
    description: str = Field(min_length=1, max_length=500, description="Topic description")
    active: bool = True
    created_at: datetime


class AvoidOut(BaseModel):
    """DTO for avoid preference output."""
    model_config = ConfigDict(from_attributes=True)

    avoid_id: UUID
    description: str = Field(min_length=1, max_length=120, description="Avoid item description")
    active: bool = True
    created_at: datetime


class CatalogResponse(BaseModel):
    """DTO for catalog response."""
    topics: list[TopicOut] = Field(default_factory=list, description="List of available topics")
    avoids: list[AvoidOut] = Field(default_factory=list, description="List of avoid preferences")


class UserTopicOut(BaseModel):
    """DTO for user topic junction."""
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    topic_id: UUID
    created_at: datetime


class UserAvoidOut(BaseModel):
    """DTO for user avoid junction."""
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    avoid_id: UUID
    created_at: datetime


# Export table definitions for repository use
__all__ = [
    "TopicOut", "AvoidOut", "CatalogResponse", "UserTopicOut", "UserAvoidOut",
    "topics_table", "avoid_table", "user_topics_table", "user_avoid_table"
]
