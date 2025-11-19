"""AI Feedback schemas and DTOs."""

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class FeedbackAction(str, Enum):
    """User feedback action types."""
    LIKE = "like"
    DISLIKE = "dislike"
    COPY = "copy"
    EDIT = "edit"
    IGNORE = "ignore"


class AIFeedbackCreate(BaseModel):
    """Request to create AI feedback."""
    generation_id: UUID
    suggestion_text: str = Field(max_length=500)
    suggestion_index: int = Field(ge=0, le=4)
    action: FeedbackAction
    edited_text: str | None = Field(None, max_length=500)
    context: dict[str, Any]

    @field_validator("edited_text")
    @classmethod
    def validate_edited_text(cls, v: str | None, info) -> str | None:
        """Validate edited_text is required when action is edit."""
        if info.data.get("action") == FeedbackAction.EDIT and not v:
            raise ValueError("edited_text is required when action is 'edit'")
        return v


class AIFeedbackOut(BaseModel):
    """AI feedback output DTO."""
    id: UUID
    user_id: UUID
    thread_id: UUID | None = None
    generation_id: UUID | None = None
    suggestion_text: str
    suggestion_index: int | None = None
    action: FeedbackAction
    edited_text: str | None = None
    context_messages: dict[str, Any] | None = None
    prompt_hash: str | None = None
    tone: str | None = None
    user_locale: str
    user_gender: str | None = None
    user_birth_year: int | None = None
    user_country: str | None = None
    user_state: str | None = None
    user_city: str | None = None
    created_at: datetime
    device_id: str | None
    app_version: str | None

    class Config:
        from_attributes = True


class FeedbackStatsOut(BaseModel):
    """User feedback statistics."""
    total_feedbacks: int
    likes: int
    dislikes: int
    copies: int
    edits: int
    ignores: int
    favorite_tone: str | None
    avg_quality_score: float | None

    @property
    def satisfaction_rate(self) -> float:
        """Calculate satisfaction rate (likes + copies) / total."""
        if self.total_feedbacks == 0:
            return 0.0
        return (self.likes + self.copies) / self.total_feedbacks

    @property
    def engagement_rate(self) -> float:
        """Calculate engagement rate (non-ignore actions) / total."""
        if self.total_feedbacks == 0:
            return 0.0
        engaged = self.total_feedbacks - self.ignores
        return engaged / self.total_feedbacks
