"""Outbox domain schemas and table definitions."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict
from sqlalchemy import Column, Integer, MetaData, Table, Text, text
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PGUUID

# SQLAlchemy table definitions
metadata = MetaData()

outbox_table = Table(
    "outbox", metadata,
    Column("id", PGUUID, primary_key=True),
    Column("user_id", PGUUID),
    Column("topic", Text, nullable=False),
    Column("status", Text, nullable=False, server_default=text("'queued'")),
    Column("priority", Integer, nullable=False, server_default=text("100")),
    Column("attempts", Integer, nullable=False, server_default=text("0")),
    Column("max_attempts", Integer, nullable=False, server_default=text("5")),
    Column("scheduled_at", TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")),
    Column("payload", JSONB, nullable=False),
    Column("result", JSONB),
    Column("error", JSONB),
    Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")),
    Column("updated_at", TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")),
)

OutboxStatus = Literal["queued", "processing", "succeeded", "failed", "dead"]


class OutboxItemOut(BaseModel):
    """DTO for outbox item output."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID | None = None
    topic: str
    status: OutboxStatus
    priority: int = 100
    attempts: int = 0
    max_attempts: int = 5
    scheduled_at: datetime
    payload: dict[str, Any]
    result: dict[str, Any] | None = None
    error: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime


class OutboxItemCreate(BaseModel):
    """DTO for creating outbox item."""
    user_id: UUID | None = None
    topic: str
    payload: dict[str, Any]
    priority: int = 100
    scheduled_at: datetime | None = None


class OutboxItemUpdate(BaseModel):
    """DTO for updating outbox item."""
    status: OutboxStatus | None = None
    attempts: int | None = None
    result: dict[str, Any] | None = None
    error: dict[str, Any] | None = None
    scheduled_at: datetime | None = None


# Export table definitions for repository use
__all__ = [
    "OutboxStatus", "OutboxItemOut", "OutboxItemCreate", "OutboxItemUpdate",
    "outbox_table"
]
