"""Legal repository for managing legal documents and user acceptances."""

from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from ...utils.errors import BadRequest, FailedDependency, NotFound
from ...utils.tracing import trace_async
from ...utils.request_tracking import RequestTracker
from ...utils.domain_logger import get_domain_logger
from .schemas import (
    DocumentType,
    LegalDocumentCreate,
    LegalDocumentOut,
    LegalDocumentUpdate,
    UserLegalAcceptanceOut,
    legal_documents_table,
    user_legal_acceptances_table,
)

domain_logger = get_domain_logger(__name__)


class LegalRepository:
    """Repository for legal documents and acceptances."""

    def __init__(self, session: AsyncSession):
        self.session = session

    @trace_async
    async def get_current_document(
        self, document: DocumentType, locale: str, fallback_locales: list[str] | None = None
    ) -> LegalDocumentOut | None:
        """Get current active document for locale with fallback."""
        locales_to_try = [locale]
        if fallback_locales:
            locales_to_try.extend(fallback_locales)

        for try_locale in locales_to_try:
            stmt = (
                sa.select(legal_documents_table)
                .where(
                    sa.and_(
                        legal_documents_table.c.document == document,
                        legal_documents_table.c.locale == try_locale,
                        legal_documents_table.c.is_active.is_(True)
                    )
                )
                .order_by(
                    legal_documents_table.c.effective_at.desc(),
                    legal_documents_table.c.version.desc()
                )
                .limit(1)
            )

            result = await self.session.execute(stmt)
            row = result.fetchone()

            if row:
                return LegalDocumentOut.model_validate(row._asdict())

        return None

    @trace_async
    async def get_document_by_version(
        self, document: DocumentType, locale: str, version: str
    ) -> LegalDocumentOut | None:
        """Get specific document version."""
        stmt = sa.select(legal_documents_table).where(
            sa.and_(
                legal_documents_table.c.document == document,
                legal_documents_table.c.locale == locale,
                legal_documents_table.c.version == version
            )
        )

        result = await self.session.execute(stmt)
        row = result.fetchone()
        return LegalDocumentOut.model_validate(row._asdict()) if row else None

    @trace_async
    async def list_locales(self, document: DocumentType, only_active: bool = True) -> list[str]:
        """List available locales for document."""
        stmt = sa.select(legal_documents_table.c.locale.distinct()).where(
            legal_documents_table.c.document == document
        )

        if only_active:
            stmt = stmt.where(legal_documents_table.c.is_active.is_(True))

        result = await self.session.execute(stmt)
        return [row.locale for row in result.fetchall()]

    @trace_async
    async def create_document(self, data: LegalDocumentCreate) -> LegalDocumentOut:
        """Create new legal document."""
        document_data = data.model_dump()

        stmt = sa.insert(legal_documents_table).values(**document_data).returning(legal_documents_table)
        try:
            result = await self.session.execute(stmt)
            row = result.fetchone()
            if row is None:
                raise FailedDependency("Failed to create legal document")
            return LegalDocumentOut.model_validate(row._asdict())
        except sa.exc.IntegrityError as e:
            raise BadRequest(f"Document creation failed: {str(e)}")

    @trace_async
    async def update_document(self, document_id: UUID, data: LegalDocumentUpdate) -> LegalDocumentOut | None:
        """Update legal document."""
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            # No updates to apply, return current document
            stmt = sa.select(legal_documents_table).where(legal_documents_table.c.id == document_id)
            result = await self.session.execute(stmt)
            row = result.fetchone()
            return LegalDocumentOut.model_validate(row._asdict()) if row else None

        update_data['updated_at'] = sa.func.now()

        update_stmt = (
            sa.update(legal_documents_table)
            .where(legal_documents_table.c.id == document_id)
            .values(**update_data)
            .returning(legal_documents_table)
        )

        result = await self.session.execute(update_stmt)
        row = result.fetchone()
        return LegalDocumentOut.model_validate(row._asdict()) if row else None

    @trace_async
    async def upsert_document(
        self, document: DocumentType, locale: str, version: str,
        title: str, content: str, checksum: str, effective_at: datetime | None = None
    ) -> LegalDocumentOut:
        """Upsert document with conflict handling."""
        stmt = pg_insert(legal_documents_table).values(
            document=document,
            locale=locale,
            version=version,
            title=title,
            content=content,
            checksum=checksum,
            effective_at=effective_at or sa.func.now(),
            is_active=True
        ).on_conflict_do_update(
            index_elements=['document', 'locale', 'version'],
            set_=dict(
                title=pg_insert(legal_documents_table).excluded.title,
                content=pg_insert(legal_documents_table).excluded.content,
                checksum=pg_insert(legal_documents_table).excluded.checksum,
                effective_at=pg_insert(legal_documents_table).excluded.effective_at,
                is_active=pg_insert(legal_documents_table).excluded.is_active,
                updated_at=sa.func.now()
            )
        ).returning(legal_documents_table)

        try:
            result = await self.session.execute(stmt)
            row = result.fetchone()

            if not row:
                raise FailedDependency("Failed to upsert document")

            return LegalDocumentOut.model_validate(row._asdict())
        except sa.exc.IntegrityError as e:
            raise BadRequest(f"Document upsert failed: {str(e)}")

    @trace_async
    async def deactivate_document(
        self, document: DocumentType, locale: str, version: str
    ) -> LegalDocumentOut:
        """Deactivate document."""
        stmt = (
            sa.update(legal_documents_table)
            .where(
                sa.and_(
                    legal_documents_table.c.document == document,
                    legal_documents_table.c.locale == locale,
                    legal_documents_table.c.version == version
                )
            )
            .values(is_active=False, updated_at=sa.func.now())
            .returning(legal_documents_table)
        )

        result = await self.session.execute(stmt)
        row = result.fetchone()

        if not row:
            raise NotFound("Document not found")

        return LegalDocumentOut.model_validate(row._asdict())

    # User acceptance methods

    @trace_async
    async def accept_version(
        self, user_id: UUID, document: DocumentType, version: str, locale: str, error_locale: str = "en-US"
    ) -> UserLegalAcceptanceOut:
        """Accept document version (idempotent). RLS enforced via user_id."""
        from ...utils.i18n import t

        try:
            tracking_context = domain_logger.operation_start("accept_version", user_id=str(user_id), document=document, version=version, locale=locale)

            stmt = pg_insert(user_legal_acceptances_table).values(
                user_id=user_id,
                document=document,
                version=version,
                locale=locale
            ).on_conflict_do_nothing(
                index_elements=['user_id', 'document', 'version']
            ).returning(user_legal_acceptances_table)

            result = await self.session.execute(stmt)
            row = result.fetchone()

            if row:
                acceptance = UserLegalAcceptanceOut.model_validate(row._asdict())
                domain_logger.operation_success(tracking_context, {
                    "user_id": str(user_id),
                    "document": document,
                    "version": version,
                    "locale": locale,
                    "acceptance_id": str(acceptance.id),
                    "operation": "created"
                })
                domain_logger.business_event("legal_document_accepted", {
                    "user_id": str(user_id),
                    "document_type": document,
                    "version": version,
                    "locale": locale,
                    "acceptance_id": str(acceptance.id),
                    "operation": "created"
                })
                return acceptance

            # If no row returned, fetch existing (conflict case)
            select_stmt = sa.select(user_legal_acceptances_table).where(
                sa.and_(
                    user_legal_acceptances_table.c.user_id == user_id,
                    user_legal_acceptances_table.c.document == document,
                    user_legal_acceptances_table.c.version == version
                )
            )

            result = await self.session.execute(select_stmt)
            row = result.fetchone()

            if not row:
                error_key = f"legal.error.{document}_accept_failed" if document in ["privacy", "terms"] else "legal.error.accept_failed"
                raise FailedDependency(t(error_key, locale=error_locale))

            acceptance = UserLegalAcceptanceOut.model_validate(row._asdict())
            domain_logger.operation_success(tracking_context, {
                "user_id": str(user_id),
                "document": document,
                "version": version,
                "locale": locale,
                "acceptance_id": str(acceptance.id),
                "operation": "existing"
            })
            domain_logger.business_event("legal_document_accepted", {
                "user_id": str(user_id),
                "document_type": document,
                "version": version,
                "locale": locale,
                "acceptance_id": str(acceptance.id),
                "operation": "existing"
            })
            return acceptance
        except sa.exc.IntegrityError:
            domain_logger.operation_error(tracking_context, "Integrity error", {
                "user_id": str(user_id),
                "document": document,
                "version": version,
                "locale": locale
            })
            error_key = f"legal.error.{document}_accept_failed" if document in ["privacy", "terms"] else "legal.error.accept_failed"
            raise BadRequest(t(error_key, locale=error_locale))
        except Exception as e:
            domain_logger.operation_error(tracking_context, str(e), {
                "user_id": str(user_id),
                "document": document,
                "version": version,
                "locale": locale
            })
            raise

    @trace_async
    async def get_acceptance(
        self, user_id: UUID, document: DocumentType, version: str
    ) -> UserLegalAcceptanceOut | None:
        """Get specific acceptance. RLS enforced via user_id."""
        stmt = sa.select(user_legal_acceptances_table).where(
            sa.and_(
                user_legal_acceptances_table.c.user_id == user_id,
                user_legal_acceptances_table.c.document == document,
                user_legal_acceptances_table.c.version == version
            )
        )

        result = await self.session.execute(stmt)
        row = result.fetchone()
        return UserLegalAcceptanceOut.model_validate(row._asdict()) if row else None

    @trace_async
    async def has_any_acceptance(self, user_id: UUID, document: DocumentType) -> bool:
        """Check if user has any acceptance for document. RLS enforced via user_id."""
        stmt = sa.select(sa.func.count()).select_from(user_legal_acceptances_table).where(
            sa.and_(
                user_legal_acceptances_table.c.user_id == user_id,
                user_legal_acceptances_table.c.document == document
            )
        )

        result = await self.session.execute(stmt)
        count = result.scalar() or 0
        return count > 0

    @trace_async
    async def list_acceptances(
        self, user_id: UUID, document: DocumentType | None = None
    ) -> list[UserLegalAcceptanceOut]:
        """List user acceptances. RLS enforced via user_id."""
        stmt = (
            sa.select(user_legal_acceptances_table)
            .where(user_legal_acceptances_table.c.user_id == user_id)
            .order_by(user_legal_acceptances_table.c.accepted_at.desc())
        )

        if document:
            stmt = stmt.where(user_legal_acceptances_table.c.document == document)

        result = await self.session.execute(stmt)
        return [UserLegalAcceptanceOut.model_validate(row._asdict()) for row in result.fetchall()]

    @trace_async
    async def delete_acceptance(
        self, user_id: UUID, document: DocumentType, version: str
    ) -> None:
        """Delete specific acceptance. RLS enforced via user_id."""
        stmt = sa.delete(user_legal_acceptances_table).where(
            sa.and_(
                user_legal_acceptances_table.c.user_id == user_id,
                user_legal_acceptances_table.c.document == document,
                user_legal_acceptances_table.c.version == version
            )
        )

        result = await self.session.execute(stmt)
        if result.rowcount == 0:  # type: ignore[attr-defined]
            raise NotFound("Acceptance not found")

    @trace_async
    async def get_latest_acceptance(
        self, user_id: UUID, document: DocumentType
    ) -> UserLegalAcceptanceOut | None:
        """Get user's latest acceptance for document. RLS enforced via user_id."""
        stmt = (
            sa.select(user_legal_acceptances_table)
            .where(
                sa.and_(
                    user_legal_acceptances_table.c.user_id == user_id,
                    user_legal_acceptances_table.c.document == document
                )
            )
            .order_by(user_legal_acceptances_table.c.accepted_at.desc())
            .limit(1)
        )

        result = await self.session.execute(stmt)
        row = result.fetchone()
        return UserLegalAcceptanceOut.model_validate(row._asdict()) if row else None
