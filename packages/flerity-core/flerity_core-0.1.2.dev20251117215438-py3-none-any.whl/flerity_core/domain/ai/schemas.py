"""AI module schemas and DTOs."""

from datetime import datetime
from typing import Any, Literal, Protocol
from uuid import UUID

from pydantic import BaseModel, Field
from sqlalchemy import Boolean, Column, Index, MetaData, Table, Text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PGUUID

# Type aliases for better type safety
AIJobKind = Literal["suggestion", "icebreaker"]
AIJobStatus = Literal["queued", "running", "done", "error"]
AITone = Literal["friendly", "witty", "empathetic", "professional"]


# Request DTOs
class SuggestionRequestProtocol(Protocol):
    """Protocol for suggestion requests."""
    tone: AITone
    max_suggestions: int
    last_n_messages: int
    hint: str | None


class SuggestionRequest(BaseModel):
    """Request for generating conversation suggestions."""
    tone: AITone = "friendly"
    max_suggestions: int = Field(default=3, ge=1, le=5)
    last_n_messages: int = Field(default=10, ge=1, le=50)
    hint: str | None = Field(default=None, max_length=200)


class IcebreakerRequestProtocol(Protocol):
    """Protocol for icebreaker requests."""
    tone: AITone
    max_suggestions: int


class IcebreakerRequest(BaseModel):
    """Request for generating icebreakers."""
    tone: AITone = "friendly"
    max_suggestions: int = Field(default=3, ge=1, le=5)
    bio_text: str | None = Field(default=None, max_length=1000, description="Bio text for context")
    image_url: str | None = Field(default=None, max_length=500, description="Profile image URL for visual context")


# Response DTOs
class SuggestionItem(BaseModel):
    """A single suggestion item."""
    text: str


class SuggestionResponse(BaseModel):
    """Response with generated suggestions."""
    thread_id: UUID
    suggestions: list[SuggestionItem]
    generated_at: datetime
    based_on: dict[str, Any]
    generation_id: UUID | None = None  # Audit record ID for feedback


class IcebreakerResponse(BaseModel):
    """Response with generated icebreakers."""
    thread_id: UUID | None
    icebreakers: list[SuggestionItem]
    generated_at: datetime
    generation_id: UUID | None = None  # Audit record ID for feedback


class JobCreatedResponse(BaseModel):
    """Response when async job is created."""
    job_id: UUID
    status: Literal["queued"]
    eta_seconds: int


class JobStatusResponse(BaseModel):
    """Response for job status check."""
    job_id: UUID
    status: AIJobStatus
    result: dict[str, Any] | None
    error: dict[str, Any] | None
    created_at: datetime
    updated_at: datetime


# Context DTOs
class UserLocale(BaseModel):
    """User locale information."""
    language: str = "pt-BR"
    country: str = "BR"
    timezone: str = "America/Sao_Paulo"

    @property
    def culture_key(self) -> str:
        """Get culture key for localization."""
        return f"{self.country}_{self.language.replace('-', '_')}"


class ThreadContext(BaseModel):
    """Context for thread-based AI generation."""
    thread_id: UUID | None = None
    user_id: UUID
    recent_messages: list[dict[str, Any]] = []
    locale: UserLocale = Field(default_factory=UserLocale)
    user_locale: UserLocale = Field(default_factory=UserLocale)  # Alias for compatibility
    user_tier: str | None = None  # User subscription tier for context

    def get_hash(self) -> str:
        """Get hash of context for caching."""
        import hashlib
        content = f"{self.thread_id}:{self.user_id}:{len(self.recent_messages)}"
        return hashlib.sha256(content.encode()).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "thread_id": str(self.thread_id) if self.thread_id else None,
            "user_id": str(self.user_id),
            "recent_messages": self.recent_messages,
            "locale": self.locale.model_dump(),
            "user_locale": self.user_locale.model_dump()
        }


# Job DTOs
class AIJob(BaseModel):
    """AI job model."""
    id: UUID | None = None
    user_id: UUID
    thread_id: UUID | None = None
    kind: AIJobKind
    params: dict[str, Any]
    status: AIJobStatus = "queued"
    result: dict[str, Any] | None = None
    error: dict[str, Any] | None = None
    idem_key: str | None = None
    priority: int = 5
    attempts: int = 0
    created_at: datetime | None = None
    updated_at: datetime | None = None
    expires_at: datetime | None = None


class BlocklistTerm(BaseModel):
    """Blocklist term model."""
    id: str
    language: str
    category: str
    term: str
    severity: str
    is_active: bool


class AIJobOut(BaseModel):
    """AI job output DTO."""
    id: UUID
    user_id: UUID
    thread_id: UUID | None
    kind: AIJobKind
    status: AIJobStatus
    result: dict[str, Any] | None
    error: dict[str, Any] | None
    created_at: datetime
    updated_at: datetime


# Exception classes
class AIProviderTimeout(Exception):
    """AI provider timeout exception."""
    pass


class AIProviderError(Exception):
    """AI provider error exception."""
    pass


class AIProviderRateLimit(Exception):
    """AI provider rate limit exception."""
    pass


class AIContentFlagged(Exception):
    """Content flagged by moderation exception."""
    pass


# Event DTOs
class AIRequestEvent(BaseModel):
    """Event for AI request processing."""
    job_id: UUID
    user_id: UUID
    thread_id: UUID | None
    kind: AIJobKind
    params: dict[str, Any]
    context_digest: str
    trace_id: str
    created_at: datetime


# Prompt Template
class PromptTemplate(BaseModel):
    """Prompt template model."""
    id: UUID
    name: str
    kind: AIJobKind
    context_type: str
    tone: str
    language: str
    country: str = "BR"
    gender: str | None = None
    template: str
    is_active: bool = True
    created_at: datetime
    updated_at: datetime


# Table definitions
metadata = MetaData()

ai_blocklist_table = Table(
    "ai_blocklist", metadata,
    Column("id", PGUUID, primary_key=True, server_default="gen_random_uuid()"),
    Column("language", Text, nullable=False),
    Column("category", Text, nullable=False),
    Column("term", Text, nullable=False),
    Column("severity", Text, nullable=False),
    Column("is_active", Boolean, nullable=False, server_default="true"),
    Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default="now()"),
    Column("updated_at", TIMESTAMP(timezone=True), nullable=False, server_default="now()"),
    Index("ai_blocklist_language_active_idx", "language", "is_active"),
    Index("ai_blocklist_term_language_idx", "term", "language", unique=True)
)

ai_prompts = Table(
    "ai_prompts", metadata,
    Column("id", PGUUID, primary_key=True, server_default="gen_random_uuid()"),
    Column("name", Text, nullable=False),
    Column("kind", Text, nullable=False),
    Column("context_type", Text, nullable=False),
    Column("tone", Text, nullable=False),
    Column("language", Text, nullable=False),
    Column("country", Text, nullable=False, server_default="'BR'"),
    Column("gender", Text, nullable=True),
    Column("template", Text, nullable=False),
    Column("is_active", Boolean, nullable=False, server_default="true"),
    Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default="now()"),
    Column("updated_at", TIMESTAMP(timezone=True), nullable=False, server_default="now()"),
    Index("ai_prompts_kind_context_tone_idx", "kind", "context_type", "tone"),
    Index("ai_prompts_language_country_idx", "language", "country"),
    Index("ai_prompts_active_idx", "is_active")
)



# Table references for repositories
ai_jobs_table = "ai_jobs"
ai_prompts_table = ai_prompts
