"""Legal domain Pydantic schemas and DTOs."""

from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import (
    Boolean,
    Column,
    Index,
    MetaData,
    Table,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PGUUID

# SQLAlchemy table definitions
metadata = MetaData()

legal_documents_table = Table(
    "legal_documents", metadata,
    Column("id", PGUUID, primary_key=True, server_default=text('gen_random_uuid()')),
    Column("document", Text, nullable=False),
    Column("locale", Text, nullable=False),
    Column("version", Text, nullable=False),
    Column("effective_at", TIMESTAMP(timezone=True)),
    Column("updated_at", TIMESTAMP(timezone=True), nullable=False, server_default=text('now()')),
    Column("title", Text, nullable=False),
    Column("content", Text, nullable=False),
    Column("checksum", Text, nullable=False),
    Column("is_active", Boolean, nullable=False, server_default=text('true')),

    # Constraints and indexes for performance and data integrity
    UniqueConstraint('document', 'locale', 'version', name='uq_legal_documents_doc_locale_version'),
    Index('ix_legal_documents_active_lookup', 'document', 'locale', 'is_active', 'effective_at'),
    Index('ix_legal_documents_version_lookup', 'document', 'locale', 'version'),
)

user_legal_acceptances_table = Table(
    "user_legal_acceptances", metadata,
    Column("id", PGUUID, primary_key=True, server_default=text('gen_random_uuid()')),
    Column("user_id", PGUUID, nullable=False),
    Column("document", Text, nullable=False),
    Column("version", Text, nullable=False),
    Column("locale", Text, nullable=False),
    Column("accepted_at", TIMESTAMP(timezone=True), nullable=False, server_default=text('now()')),

    # Constraints and indexes for RLS and performance
    UniqueConstraint('user_id', 'document', 'version', name='uq_user_legal_acceptances_user_doc_version'),
    Index('ix_user_legal_acceptances_user_document', 'user_id', 'document', 'accepted_at'),
    Index('ix_user_legal_acceptances_user_lookup', 'user_id', 'accepted_at'),
)


DocumentType = Literal["privacy", "terms", "cookies"]


class LegalDocumentOut(BaseModel):
    """DTO for legal document output."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    document: DocumentType
    locale: str
    version: str
    effective_at: datetime | None = None
    updated_at: datetime
    title: str
    content: str
    checksum: str
    is_active: bool = True

    @field_validator("locale", "version", "title", "content", "checksum")
    @classmethod
    def validate_non_empty_strings(cls, v: str) -> str:
        """Validate that string fields are not empty."""
        if not v or not v.strip():
            raise ValueError("String fields cannot be empty")
        return v.strip()

    @field_validator("locale")
    @classmethod
    def validate_locale_format(cls, v: str) -> str:
        """Validate locale format (e.g., en-US, pt-BR)."""
        v = v.strip()
        if not v or len(v) < 2 or '-' not in v:
            raise ValueError("Locale must be in format 'language-country' (e.g., 'en-US')")
        return v

    @field_validator("version")
    @classmethod
    def validate_version_format(cls, v: str) -> str:
        """Validate version format."""
        v = v.strip()
        if not v or len(v) > 50:
            raise ValueError("Version must be non-empty and max 50 characters")
        return v


class LegalDocumentCreate(BaseModel):
    """DTO for creating legal document."""
    document: DocumentType
    locale: str = Field(..., min_length=2, max_length=10)
    version: str = Field(..., min_length=1, max_length=50)
    effective_at: datetime | None = None
    title: str = Field(..., min_length=1, max_length=500)
    content: str = Field(..., min_length=1)
    checksum: str = Field(..., min_length=1, max_length=128)

    @field_validator("locale")
    @classmethod
    def validate_locale_format(cls, v: str) -> str:
        """Validate locale format."""
        if not v or '-' not in v:
            raise ValueError("Locale must be in format 'language-country'")
        return v.strip()

    @field_validator("checksum")
    @classmethod
    def validate_checksum_format(cls, v: str) -> str:
        """Validate checksum format (hex string)."""
        v = v.strip()
        if not v or not all(c in '0123456789abcdefABCDEF' for c in v):
            raise ValueError("Checksum must be a valid hexadecimal string")
        return v.lower()


class UserLegalAcceptanceOut(BaseModel):
    """DTO for user legal acceptance output."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    document: DocumentType
    version: str
    locale: str
    accepted_at: datetime


class LegalDocumentUpdate(BaseModel):
    """DTO for updating legal document."""
    effective_at: datetime | None = None
    title: str | None = Field(None, min_length=1, max_length=500)
    content: str | None = Field(None, min_length=1)
    checksum: str | None = Field(None, min_length=1, max_length=128)
    is_active: bool | None = None

    @field_validator("checksum")
    @classmethod
    def validate_checksum_format(cls, v: str | None) -> str | None:
        """Validate checksum format if provided."""
        if v is None:
            return v
        v = v.strip()
        if not all(c in '0123456789abcdefABCDEF' for c in v):
            raise ValueError("Checksum must be a valid hexadecimal string")
        return v.lower()


class UserLegalAcceptanceCreate(BaseModel):
    """DTO for creating user legal acceptance."""
    user_id: UUID | None = None  # Optional, can be set from RLS context
    document: DocumentType
    version: str = Field(..., min_length=1, max_length=50)
    locale: str = Field(..., min_length=2, max_length=10)

    @field_validator("locale")
    @classmethod
    def validate_locale_format(cls, v: str) -> str:
        """Validate locale format."""
        if not v or '-' not in v:
            raise ValueError("Locale must be in format 'language-country'")
        return v.strip()


# Export table definitions for repository use
__all__ = [
    "DocumentType",
    "LegalDocumentOut", "LegalDocumentCreate", "LegalDocumentUpdate",
    "UserLegalAcceptanceOut", "UserLegalAcceptanceCreate",
    "legal_documents_table", "user_legal_acceptances_table"
]
