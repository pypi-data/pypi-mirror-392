"""Telemetry domain Pydantic schemas and DTOs."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

import sqlalchemy as sa
from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator
from sqlalchemy import Column, Index, MetaData, Table, Text
from sqlalchemy.dialects.postgresql import ENUM, JSONB, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PGUUID

# SQLAlchemy table definition
metadata = MetaData()

# Define the platform enum to match database
platform_enum = ENUM('ios', 'android', 'web', name='platform_enum', create_type=False)

telemetry_events_table = Table(
    "telemetry_events", metadata,
    Column("event_id", PGUUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
    Column("event_type", Text, nullable=False),
    Column("timestamp", TIMESTAMP(timezone=True), nullable=False),
    Column("user_id", Text, nullable=False),
    Column("device_id", Text, nullable=False),
    Column("app_version", Text),
    Column("os_version", Text),
    Column("platform", platform_enum, nullable=False),
    Column("locale", Text),
    Column("timezone", Text),
    Column("session_id", Text, nullable=False),
    Column("data", JSONB, nullable=False),
    Column("received_at", TIMESTAMP(timezone=True), nullable=False),

    # Indexes for performance
    Index('ix_telemetry_events_user_timestamp', 'user_id', 'timestamp'),
    Index('ix_telemetry_events_session_timestamp', 'session_id', 'timestamp'),
    Index('ix_telemetry_events_type_timestamp', 'event_type', 'timestamp'),
    Index('ix_telemetry_events_received_at', 'received_at'),
)


EventType = Literal[
    "screen_view", "ui_action", "user_action", "flow_step", "error", "performance", "identity",
    # Onboarding
    "onboarding_welcome_continue", "onboarding_consent_accept", "onboarding_profile_success",
    "onboarding_done_finish", "onboarding_completed",
    # Instagram OAuth
    "instagram_oauth_opened", "instagram_oauth_cancelled", "instagram_oauth_completed", "instagram_oauth_failed",
    # Threads/Conversas
    "threads_load_more", "thread_list_loaded", "thread_tracking_reactivated",
    # Thread Deletion Events
    "thread_deletion_ui_started", "thread_deletion_ui_completed", "thread_deletion_ui_failed",
    "thread_deletion_started", "thread_deletion_completed", "thread_deletion_failed", "thread_deletion_cancelled",
    "thread_deletion_modal_failed", "thread_deletion_mutation_started", "thread_deletion_mutation_completed",
    "thread_deletion_mutation_failed", "thread_deletion_preview_loaded", "bulk_thread_deletion_completed",
    "bulk_thread_deletion_failed", "thread_deletion_flow_initiation_failed", "thread_deletion_flow_initiated",
    "integrated_thread_deletion_failed", "integrated_thread_deletion_completed", "thread_deletion_validation_failed",
    "thread_deletion_flow_cancelled", "thread_deletion_realtime_toggled", "thread_deletion_realtime_update",
    "comprehensive_thread_deletion_started", "comprehensive_thread_deletion_completed", "comprehensive_thread_deletion_failed",
    "integration_health_check_failed", "integrated_deletion_flow_completed", "integrated_deletion_flow_failed",
    # Planos/Pagamento
    "plan_badge_tapped", "upgrade_prompt_shown", "payment_flow_started", "upgrade_completed",
    "payment_flow_abandoned", "upgrade_prompt_dismissed",
    # Notificações
    "notification_badge_pressed", "notification_item_pressed", "notification_marked_read", "notification_action_pressed",
    # Push Notifications
    "push_enable_clicked", "push_register_completed", "push_register_failed",
    # Insights/Analytics
    "insights_period_changed", "insights_channel_changed"
]
PlatformType = Literal["ios", "android", "web"]
ErrorType = Literal["network", "js", "logic", "api"]
PerformanceMetric = Literal["cold_start", "time_to_first_interaction", "api_request"]
FlowStatus = Literal["started", "completed", "failed", "skipped"]


class TelemetryEventOut(BaseModel):
    """DTO for telemetry event output."""
    model_config = ConfigDict(from_attributes=True)

    event_id: UUID
    event_type: EventType
    timestamp: datetime
    user_id: str  # Pseudonymized user ID
    device_id: str
    session_id: str
    app_version: str | None = None
    os_version: str | None = None
    platform: PlatformType
    locale: str | None = None
    timezone: str | None = None
    data: dict[str, Any]
    received_at: datetime


class TelemetryEventCreate(BaseModel):
    """DTO for creating telemetry event."""
    model_config = ConfigDict(str_strip_whitespace=True)

    event_id: UUID | None = None  # Auto-generated if not provided
    event_type: EventType
    timestamp: datetime
    user_id: str = Field(..., min_length=1, max_length=256)  # Pseudonymized user ID
    device_id: str = Field(..., min_length=1, max_length=256)
    session_id: str = Field(..., min_length=1, max_length=256)
    app_version: str | None = Field(None, max_length=256)
    os_version: str | None = Field(None, max_length=256)
    platform: PlatformType
    locale: str | None = Field(None, max_length=10)
    timezone: str | None = Field(None, max_length=50)
    data: dict[str, Any] = Field(..., max_length=16384)

    @field_validator("user_id", "device_id", "session_id")
    @classmethod
    def validate_required_ids(cls, v: str) -> str:
        """Validate required ID fields are not empty."""
        if not v or not v.strip():
            raise ValueError("ID fields cannot be empty")
        return v.strip()

    @field_validator("data")
    @classmethod
    def validate_data_size(cls, v: dict[str, Any]) -> dict[str, Any]:
        """Validate data payload size."""
        import json
        try:
            data_size = len(json.dumps(v, separators=(',', ':')).encode('utf-8'))
            if data_size > 16384:  # 16KB limit per event
                raise ValueError("Event data exceeds 16KB limit")
        except (TypeError, ValueError) as e:
            if "exceeds" in str(e):
                raise
            raise ValueError(f"Invalid data format: {str(e)}")
        return v

    @field_validator("data")
    @classmethod
    def validate_data_by_event_type(cls, v: dict[str, Any], info: ValidationInfo) -> dict[str, Any]:
        """Validate data field based on event_type."""
        if not info.data:
            return v

        event_type = info.data.get("event_type")

        # Define validation rules for each event type
        validators = {
            "screen_view": cls._validate_screen_view_data,
            "ui_action": cls._validate_ui_action_data,
            "flow_step": cls._validate_flow_step_data,
            "error": cls._validate_error_data,
            "performance": cls._validate_performance_data,
        }

        validator = validators.get(event_type or "")
        if validator:
            validator(v)

        return v

    @staticmethod
    def _validate_screen_view_data(data: dict[str, Any]) -> None:
        """Validate screen_view event data."""
        if "screen_name" not in data:
            raise ValueError("screen_view requires screen_name in data")
        if "duration_ms" in data and not isinstance(data["duration_ms"], int):
            raise ValueError("duration_ms must be an integer")

    @staticmethod
    def _validate_ui_action_data(data: dict[str, Any]) -> None:
        """Validate ui_action event data."""
        if "action_id" not in data:
            raise ValueError("ui_action requires action_id in data")

    @staticmethod
    def _validate_flow_step_data(data: dict[str, Any]) -> None:
        """Validate flow_step event data."""
        if "flow" not in data or "step" not in data:
            raise ValueError("flow_step requires flow and step in data")
        if "status" in data and data["status"] not in {"started", "completed", "failed", "skipped"}:
            raise ValueError("Invalid flow status")

    @staticmethod
    def _validate_error_data(data: dict[str, Any]) -> None:
        """Validate error event data."""
        if "error_type" not in data or "message" not in data:
            raise ValueError("error requires error_type and message in data")
        if "error_type" in data and data["error_type"] not in {"network", "js", "logic", "api"}:
            raise ValueError("Invalid error_type")

    @staticmethod
    def _validate_performance_data(data: dict[str, Any]) -> None:
        """Validate performance event data."""
        if "metric" not in data or "value_ms" not in data:
            raise ValueError("performance requires metric and value_ms in data")
        if "metric" in data and data["metric"] not in {"cold_start", "time_to_first_interaction", "api_request"}:
            raise ValueError("Invalid performance metric")
        if "value_ms" in data and not isinstance(data["value_ms"], int):
            raise ValueError("value_ms must be an integer")


class TelemetryIngestBatchOut(BaseModel):
    """DTO for telemetry ingestion batch output."""
    model_config = ConfigDict(from_attributes=True)

    ingestion_id: UUID
    user_id: UUID | None = None
    received_count: int
    stored_count: int
    payload_bytes: int
    created_at: datetime

    @property
    def duplicate_count(self) -> int:
        """Calculate number of duplicate events."""
        return self.received_count - self.stored_count

    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        return (self.stored_count / self.received_count * 100) if self.received_count > 0 else 0.0


class TelemetryIngestRequest(BaseModel):
    """DTO for telemetry ingestion request."""
    events: list[dict[str, Any]] = Field(min_length=1, max_length=50)

    @field_validator("events")
    @classmethod
    def validate_events_size(cls, v: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Validate total payload size."""
        import json
        try:
            total_size = sum(len(json.dumps(event, separators=(',', ':')).encode('utf-8')) for event in v)
            if total_size > 500 * 1024:  # 500KB limit
                raise ValueError("Total payload size exceeds 500KB limit")
        except (TypeError, ValueError) as e:
            raise ValueError(f"Invalid event data format: {str(e)}")
        return v


class TelemetryIngestResponse(BaseModel):
    """DTO for telemetry ingestion response."""
    ingestion_id: str
    accepted: int
    duplicates: int
    rejected: int
    received: int

    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        return (self.accepted / self.received * 100) if self.received > 0 else 0.0


class TelemetryStatsOut(BaseModel):
    """DTO for telemetry statistics output."""
    total_batches: int
    total_received: int
    total_stored: int
    avg_payload_bytes: float
    duplicate_rate: float

    @property
    def overall_success_rate(self) -> float:
        """Calculate overall success rate as percentage."""
        return (self.total_stored / self.total_received * 100) if self.total_received > 0 else 0.0


class TelemetryEventStatsOut(BaseModel):
    """DTO for event type statistics."""
    event_counts: dict[str, int]
    total_events: int

    @property
    def most_common_event(self) -> str | None:
        """Get the most common event type."""
        if not self.event_counts:
            return None
        return max(self.event_counts, key=lambda x: self.event_counts[x])


# Export schemas and table for repository use
__all__ = [
    "EventType", "PlatformType", "ErrorType", "PerformanceMetric", "FlowStatus",
    "TelemetryEventOut", "TelemetryEventCreate",
    "TelemetryIngestBatchOut", "TelemetryIngestRequest", "TelemetryIngestResponse",
    "TelemetryStatsOut", "TelemetryEventStatsOut",
    "telemetry_events_table"
]
