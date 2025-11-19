"""Analytics domain Pydantic schemas and SQLAlchemy table definitions."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import Column, Index, Integer, MetaData, Table
from sqlalchemy.dialects.postgresql import UUID as PGUUID

# SQLAlchemy table definitions
metadata = MetaData()

# View table (read-only) - aggregated user analytics
kpi_user_30d_table = Table(
    "kpi_user_30d", metadata,
    Column("user_id", PGUUID, primary_key=True, nullable=False),
    Column("threads_active", Integer, nullable=False, default=0),
    Column("messages_sent", Integer, nullable=False, default=0),
    Column("messages_received", Integer, nullable=False, default=0),
    # Index for performance on user lookups
    Index("idx_kpi_user_30d_user_id", "user_id"),
)


class KPIUser30DOut(BaseModel):
    """DTO for KPI user 30d view output."""
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    threads_active: int = Field(ge=0, description="Number of active threads")
    messages_sent: int = Field(ge=0, description="Number of messages sent")
    messages_received: int = Field(ge=0, description="Number of messages received")


class KPIOut(BaseModel):
    """DTO for generic KPI output."""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(min_length=1, max_length=50, description="KPI unique identifier")
    name: str = Field(min_length=1, max_length=100, description="KPI name")
    value: float | int | str = Field(description="KPI value")
    unit: str | None = Field(None, max_length=20, description="Unit of measurement")
    trend: str | None = Field(None, pattern=r"^(up|down|stable)$", description="Trend direction")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class AnalyticsResponse(BaseModel):
    """DTO for analytics response."""
    kpis: list[KPIOut] = Field(default_factory=list, description="List of KPI metrics")
    period: str | None = Field(None, max_length=50, description="Time period for analytics")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Response metadata")


# ========== TIER 1 ANALYTICS SCHEMAS (NEW) ==========

class MessageBalanceOut(BaseModel):
    """DTO for message balance metrics."""
    user_messages: int = Field(ge=0)
    contact_messages: int = Field(ge=0)
    total_messages: int = Field(ge=0)
    user_percentage: float = Field(ge=0, le=100)
    contact_percentage: float = Field(ge=0, le=100)
    balance_score: float = Field(ge=0, le=100, description="100 = perfect balance (50/50)")


class ResponseTimesOut(BaseModel):
    """DTO for response time metrics."""
    avg_response_hours: float = Field(ge=0)
    min_response_hours: float = Field(ge=0)
    max_response_hours: float = Field(ge=0)
    response_count: int = Field(ge=0)
    interest_level: Literal['very_high', 'high', 'medium', 'low', 'unknown']


class ResponseTrendOut(BaseModel):
    """DTO for response time trend."""
    first_10_avg_hours: float = Field(ge=0)
    last_10_avg_hours: float = Field(ge=0)
    trend_percent: float
    trend_direction: Literal['improving', 'declining', 'stable']
    trend_interpretation: Literal['getting_faster', 'getting_slower', 'consistent', 'insufficient_data']


class ConversationDepthOut(BaseModel):
    """DTO for conversation depth (normalized by time)."""
    total_messages: int = Field(ge=0)
    days_active: float = Field(ge=0)
    messages_per_day: float = Field(ge=0)
    depth_score: int = Field(ge=0, le=100)
    intensity_level: Literal['none', 'low', 'normal', 'high', 'very_high']
    first_message_at: datetime | None
    last_message_at: datetime | None


class RecencyOut(BaseModel):
    """DTO for last message recency."""
    last_message_at: datetime | None
    hours_since_last: float = Field(ge=0)
    days_since_last: float = Field(ge=0)
    status: Literal['active', 'cooling', 'inactive', 'no_messages', 'error']


class MessageLengthDataOut(BaseModel):
    """DTO for message length data per sender."""
    avg_length: float = Field(ge=0)
    avg_response_minutes: float = Field(ge=0)
    message_count: int = Field(ge=0)


class MessageLengthContextOut(BaseModel):
    """DTO for message length with response time context."""
    user: MessageLengthDataOut
    contact: MessageLengthDataOut
    engagement_level: Literal['high', 'medium', 'low', 'unknown']


class EmojiUsageDataOut(BaseModel):
    """DTO for emoji usage data per sender."""
    total_messages: int = Field(ge=0)
    messages_with_emoji: int = Field(ge=0)
    emoji_rate: float = Field(ge=0, le=100)
    usage_level: Literal['none', 'low', 'medium', 'high']


class EmojiUsageOut(BaseModel):
    """DTO for emoji usage metrics."""
    user: EmojiUsageDataOut
    contact: EmojiUsageDataOut


class ContactResponsivenessOut(BaseModel):
    """DTO for contact responsiveness."""
    total_user_messages: int = Field(ge=0)
    responded_messages: int = Field(ge=0)
    responsiveness_rate: float = Field(ge=0, le=100)
    responsiveness_level: Literal['very_responsive', 'responsive', 'somewhat_responsive', 'unresponsive', 'unknown']


class ThreadAnalyticsOut(BaseModel):
    """DTO for comprehensive thread analytics (TIER 1)."""
    thread_id: UUID
    message_balance: MessageBalanceOut
    response_times: ResponseTimesOut
    response_trend: ResponseTrendOut
    conversation_depth: ConversationDepthOut
    recency: RecencyOut
    message_length_context: MessageLengthContextOut
    emoji_usage: EmojiUsageOut
    contact_responsiveness: ContactResponsivenessOut
    calculated_at: datetime


# ========== TIER 2 ANALYTICS SCHEMAS (AI-POWERED) ==========

class AIInterestOut(BaseModel):
    """DTO for AI interest analysis."""
    interest_score: int = Field(ge=0, le=100)
    interest_level: Literal['very_high', 'high', 'medium', 'low']
    reasoning: str
    confidence: int = Field(ge=0, le=100)


class AISentimentOut(BaseModel):
    """DTO for AI sentiment analysis."""
    overall_sentiment: Literal['positive', 'neutral', 'negative']
    user_sentiment: Literal['positive', 'neutral', 'negative']
    contact_sentiment: Literal['positive', 'neutral', 'negative']
    sentiment_trend: Literal['improving', 'stable', 'declining']
    confidence: int = Field(ge=0, le=100)


class AIConversationStageOut(BaseModel):
    """DTO for AI conversation stage detection."""
    stage: Literal['getting_to_know', 'building_rapport', 'flirting', 'planning_date', 'cooling_off', 'ghosting']
    confidence: int = Field(ge=0, le=100)
    next_steps: list[str] = Field(default_factory=list)


class QuestionRateOut(BaseModel):
    """DTO for NLP question rate analysis."""
    user_question_rate: float = Field(ge=0, le=100)
    contact_question_rate: float = Field(ge=0, le=100)
    user_questions: int = Field(ge=0)
    contact_questions: int = Field(ge=0)
    engagement_level: Literal['high', 'medium', 'low']


class RecommendationOut(BaseModel):
    """DTO for AI recommendation."""
    type: Literal['action', 'warning', 'encouragement']
    priority: Literal['high', 'medium', 'low']
    text: str
    reasoning: str


class AIAnalysisOut(BaseModel):
    """DTO for comprehensive AI analysis."""
    interest: AIInterestOut
    sentiment: AISentimentOut
    stage: AIConversationStageOut
    question_rate: QuestionRateOut
    recommendations: list[RecommendationOut] = Field(default_factory=list)


class ConnectionScoreBreakdownOut(BaseModel):
    """DTO for connection score breakdown."""
    ai_interest: float = Field(ge=0, le=100)
    response_trend: float = Field(ge=0, le=100)
    message_balance: float = Field(ge=0, le=100)
    conversation_depth: float = Field(ge=0, le=100)
    contact_responsiveness: float = Field(ge=0, le=100)


class ConnectionScoreOut(BaseModel):
    """DTO for connection score."""
    connection_score: float = Field(ge=0, le=100)
    connection_level: Literal['excellent', 'good', 'fair', 'poor']
    breakdown: ConnectionScoreBreakdownOut


class ThreadAnalyticsTier2Out(BaseModel):
    """DTO for comprehensive thread analytics (TIER 1 + TIER 2)."""
    thread_id: UUID
    # TIER 1 metrics
    message_balance: MessageBalanceOut
    response_times: ResponseTimesOut
    response_trend: ResponseTrendOut
    conversation_depth: ConversationDepthOut
    recency: RecencyOut
    message_length_context: MessageLengthContextOut
    emoji_usage: EmojiUsageOut
    contact_responsiveness: ContactResponsivenessOut
    # TIER 2 metrics
    ai_analysis: AIAnalysisOut
    connection_score: ConnectionScoreOut
    calculated_at: datetime


# Export table definitions for repository use
__all__ = [
    "KPIUser30DOut", "KPIOut", "AnalyticsResponse",
    "MessageBalanceOut", "ResponseTimesOut", "ResponseTrendOut",
    "ConversationDepthOut", "RecencyOut", "MessageLengthDataOut",
    "MessageLengthContextOut", "EmojiUsageDataOut", "EmojiUsageOut",
    "ContactResponsivenessOut", "ThreadAnalyticsOut",
    # TIER 2
    "AIInterestOut", "AISentimentOut", "AIConversationStageOut",
    "QuestionRateOut", "RecommendationOut", "AIAnalysisOut",
    "ConnectionScoreOut", "ConnectionScoreBreakdownOut",
    "ThreadAnalyticsTier2Out",
    "kpi_user_30d_table"
]
