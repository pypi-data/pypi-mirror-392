"""Legal service for business logic orchestration and locale resolution."""

from datetime import datetime
from typing import cast
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from ...db.uow import async_uow_factory
from ...utils.domain_logger import get_domain_logger
from ...utils.errors import BadRequest, FailedDependency, NotFound
from ...utils.request_tracking import RequestTracker
from ...utils.tracing import trace_async
from .repository import LegalRepository
from .schemas import DocumentType, LegalDocumentCreate, LegalDocumentOut, UserLegalAcceptanceOut

# Default locale configuration
DEFAULT_LOCALE = "en-US"
DEFAULT_FALLBACK_LOCALES = ["en-US"]

domain_logger = get_domain_logger(__name__)


class LegalService:
    """Service for legal document management and user acceptances."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory

    def _resolve_locale_fallbacks(
        self, locale: str | None, fallback_locales: list[str] | None = None
    ) -> tuple[str, list[str]]:
        """Resolve primary locale and fallback chain."""
        primary_locale = locale or DEFAULT_LOCALE

        # Build fallback chain
        fallbacks = []
        if fallback_locales:
            fallbacks.extend(fallback_locales)
        else:
            # Default fallback chain
            if primary_locale != DEFAULT_LOCALE:
                fallbacks.append(DEFAULT_LOCALE)

        # Remove duplicates while preserving order
        unique_fallbacks = []
        seen = {primary_locale}
        for fb in fallbacks:
            if fb not in seen:
                unique_fallbacks.append(fb)
                seen.add(fb)

        return primary_locale, unique_fallbacks

    @trace_async
    async def get_current_document(
        self, document: DocumentType, locale: str | None = None,
        fallback_locales: list[str] | None = None
    ) -> LegalDocumentOut | None:
        """Get current active document for locale with fallback."""
        try:
            primary_locale, fallbacks = self._resolve_locale_fallbacks(locale, fallback_locales)

            # Legal documents are public, use isolated session without RLS
            from ...db.engine import get_auth_session_factory
            auth_session_factory = get_auth_session_factory()

            async with auth_session_factory() as session:
                # Disable RLS for public legal documents
                from sqlalchemy import text
                await session.execute(text("RESET ROLE"))
                await session.execute(text("SET row_security = off"))

                repository = LegalRepository(session)
                result: LegalDocumentOut | None = await repository.get_current_document(document, primary_locale, fallbacks)
                return result
        except Exception as e:
            raise FailedDependency(f"Failed to retrieve document: {str(e)}")

    @trace_async
    async def get_document_by_version(
        self, document: DocumentType, locale: str, version: str
    ) -> LegalDocumentOut | None:
        """Get specific document version."""
        if not locale or not version:
            raise BadRequest("Locale and version are required")

        try:
            # Legal documents are public, use isolated session without RLS
            from ...db.engine import get_auth_session_factory
            auth_session_factory = get_auth_session_factory()

            async with auth_session_factory() as session:
                # Disable RLS for public legal documents
                from sqlalchemy import text
                await session.execute(text("RESET ROLE"))
                await session.execute(text("SET row_security = off"))

                repository = LegalRepository(session)
                result: LegalDocumentOut | None = await repository.get_document_by_version(document, locale, version)
                return result
        except Exception as e:
            raise FailedDependency(f"Failed to retrieve document version: {str(e)}")

    @trace_async
    async def get_privacy_policy(
        self, locale: str | None = None, fallback_locales: list[str] | None = None
    ) -> LegalDocumentOut:
        """Get current privacy policy."""
        document: LegalDocumentOut | None = await self.get_current_document("privacy", locale, fallback_locales)
        if not document:
            raise NotFound("Privacy policy not found for requested locale")
        return document

    @trace_async
    async def get_terms_of_service(
        self, locale: str | None = None, fallback_locales: list[str] | None = None
    ) -> LegalDocumentOut:
        """Get current terms of service."""
        document: LegalDocumentOut | None = await self.get_current_document("terms", locale, fallback_locales)
        if not document:
            raise NotFound("Terms of service not found for requested locale")
        return document

    @trace_async
    async def accept_document(
        self, user_id: UUID, document: DocumentType, version: str, locale: str, error_locale: str = "en-US"
    ) -> UserLegalAcceptanceOut:
        """Accept document version with validation."""
        with RequestTracker(user_id=user_id, operation="accept_document") as tracker:
            try:
                tracking_context = domain_logger.operation_start("accept_document", user_id=str(user_id), document=document, version=version, locale=locale)

                if not version:
                    raise BadRequest("Version is required")
                if not locale:
                    raise BadRequest("Locale is required")

                # First, verify document exists using isolated session (legal documents are public)
                from ...db.engine import get_auth_session_factory
                auth_session_factory = get_auth_session_factory()

                async with auth_session_factory() as session:
                    repository = LegalRepository(session)
                    doc = await repository.get_document_by_version(document, locale, version)
                    if not doc:
                        raise NotFound(f"Document {document} version {version} not found for locale {locale}")
                    if not doc.is_active:
                        raise BadRequest(f"Document {document} version {version} is not active")

                # Then, create acceptance record using RLS context (user-specific data)
                async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                    repository = LegalRepository(uow.session)
                    result: UserLegalAcceptanceOut = await repository.accept_version(user_id, document, version, locale, error_locale)
                    await uow.commit()
                    
                    domain_logger.operation_success(tracking_context, {
                        "user_id": str(user_id),
                        "document": document,
                        "version": version,
                        "locale": locale,
                        "acceptance_id": str(result.id)
                    })
                    domain_logger.business_event("legal_document_accepted", {
                        "user_id": str(user_id),
                        "document_type": document,
                        "version": version,
                        "locale": locale,
                        "acceptance_id": str(result.id)
                    })
                    tracker.log_success(
                        document=document,
                        version=version,
                        locale=locale,
                        acceptance_id=str(result.id)
                    )
                    
                    return result
            except Exception as e:
                error_id = tracker.log_error(e, context={
                    "user_id": str(user_id),
                    "document": document,
                    "version": version,
                    "locale": locale
                })
                domain_logger.operation_error(tracking_context, str(e), {
                    "error_id": error_id,
                    "user_id": str(user_id),
                    "document": document
                })
                raise BadRequest(f"Failed to accept document (Error ID: {error_id})")
            await uow.commit()
            return result

    @trace_async
    async def accept_privacy_policy(
        self, user_id: UUID, locale: str
    ) -> UserLegalAcceptanceOut:
        """Accept current privacy policy version."""
        with RequestTracker(user_id=user_id, operation="accept_privacy_policy") as tracker:
            try:
                tracking_context = domain_logger.operation_start("accept_privacy_policy", user_id=str(user_id), locale=locale)

                current_doc: LegalDocumentOut = await self.get_privacy_policy(locale=locale)
                result: UserLegalAcceptanceOut = await self.accept_document(user_id, "privacy", current_doc.version, locale, locale)
                
                domain_logger.operation_success(tracking_context, {
                    "user_id": str(user_id),
                    "locale": locale,
                    "version": current_doc.version,
                    "acceptance_id": str(result.id)
                })
                domain_logger.business_event("privacy_policy_accepted", {
                    "user_id": str(user_id),
                    "version": current_doc.version,
                    "locale": locale
                })
                tracker.log_success(version=current_doc.version, locale=locale)
                
                return result
            except Exception as e:
                error_id = tracker.log_error(e, context={
                    "user_id": str(user_id),
                    "locale": locale
                })
                domain_logger.operation_error(tracking_context, str(e), {
                    "error_id": error_id,
                    "user_id": str(user_id)
                })
                raise BadRequest(f"Failed to accept privacy policy (Error ID: {error_id})")

    @trace_async
    async def accept_terms_of_service(
        self, user_id: UUID, locale: str
    ) -> UserLegalAcceptanceOut:
        """Accept current terms of service version."""
        with RequestTracker(user_id=user_id, operation="accept_terms_of_service") as tracker:
            try:
                tracking_context = domain_logger.operation_start("accept_terms_of_service", user_id=str(user_id), locale=locale)

                current_doc: LegalDocumentOut = await self.get_terms_of_service(locale=locale)
                result: UserLegalAcceptanceOut = await self.accept_document(user_id, "terms", current_doc.version, locale, locale)
                
                domain_logger.operation_success(tracking_context, {
                    "user_id": str(user_id),
                    "locale": locale,
                    "version": current_doc.version,
                    "acceptance_id": str(result.id)
                })
                domain_logger.business_event("terms_of_service_accepted", {
                    "user_id": str(user_id),
                    "version": current_doc.version,
                    "locale": locale
                })
                tracker.log_success(version=current_doc.version, locale=locale)
                
                return result
            except Exception as e:
                error_id = tracker.log_error(e, context={
                    "user_id": str(user_id),
                    "locale": locale
                })
                domain_logger.operation_error(tracking_context, str(e), {
                    "error_id": error_id,
                    "user_id": str(user_id)
                })
                raise BadRequest(f"Failed to accept terms of service (Error ID: {error_id})")

    @trace_async
    async def get_user_acceptance(
        self, user_id: UUID, document: DocumentType, version: str
    ) -> UserLegalAcceptanceOut | None:
        """Get specific user acceptance."""
        async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
            repository = LegalRepository(uow.session)
            result: UserLegalAcceptanceOut | None = await repository.get_acceptance(user_id, document, version)
            return result

    @trace_async
    async def has_user_accepted(self, user_id: UUID, document: DocumentType) -> bool:
        """Check if user has accepted any version of document."""
        async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
            repository = LegalRepository(uow.session)
            result: bool = await repository.has_any_acceptance(user_id, document)
            return result

    @trace_async
    async def list_user_acceptances(
        self, user_id: UUID, document: DocumentType | None = None
    ) -> list[UserLegalAcceptanceOut]:
        """List user's document acceptances."""
        async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
            repository = LegalRepository(uow.session)
            result: list[UserLegalAcceptanceOut] = await repository.list_acceptances(user_id, document)
            return result

    @trace_async
    async def list_document_locales(
        self, document: DocumentType, only_active: bool = True
    ) -> list[str]:
        """List available locales for document."""
        # Legal documents are public, use isolated session without RLS
        from ...db.engine import get_auth_session_factory
        auth_session_factory = get_auth_session_factory()

        async with auth_session_factory() as session:
            # Disable RLS for public legal documents
            from sqlalchemy import text
            await session.execute(text("RESET ROLE"))
            await session.execute(text("SET row_security = off"))

            repository = LegalRepository(session)
            result: list[str] = await repository.list_locales(document, only_active)
            return result

    @trace_async
    async def create_document(self, data: LegalDocumentCreate) -> LegalDocumentOut:
        """Create new legal document (admin only)."""
        async with async_uow_factory(self.session_factory, user_id=None)() as uow:
            repository = LegalRepository(uow.session)
            result: LegalDocumentOut = await repository.create_document(data)
            await uow.commit()
            return result

    @trace_async
    async def upsert_document(
        self, document: DocumentType, locale: str, version: str,
        title: str, content: str, checksum: str, effective_at: datetime | None = None
    ) -> LegalDocumentOut:
        """Upsert document with conflict handling (admin only)."""
        if not all([locale, version, title, content, checksum]):
            raise BadRequest("All document fields are required")

        try:
            async with async_uow_factory(self.session_factory, user_id=None)() as uow:
                repository = LegalRepository(uow.session)
                result: LegalDocumentOut = await repository.upsert_document(
                    document, locale, version, title, content, checksum, effective_at
                )
                await uow.commit()
                return result
        except Exception as e:
            raise FailedDependency(f"Failed to upsert document: {str(e)}")

    @trace_async
    async def deactivate_document(
        self, document: DocumentType, locale: str, version: str
    ) -> LegalDocumentOut:
        """Deactivate document version."""
        async with async_uow_factory(self.session_factory)() as uow:
            repository = LegalRepository(uow.session)
            result: LegalDocumentOut = await repository.deactivate_document(document, locale, version)
            await uow.commit()
            return result

    @trace_async
    async def delete_user_acceptance(
        self, user_id: UUID, document: DocumentType, version: str
    ) -> None:
        """Delete specific user acceptance."""
        if not version:
            raise BadRequest("Version is required")

        try:
            async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                repository = LegalRepository(uow.session)
                await repository.delete_acceptance(user_id, document, version)
                await uow.commit()
        except Exception as e:
            raise FailedDependency(f"Failed to delete acceptance: {str(e)}")

    @trace_async
    async def get_user_latest_acceptance(
        self, user_id: UUID, document: DocumentType
    ) -> UserLegalAcceptanceOut | None:
        """Get user's latest acceptance for document."""
        try:
            async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                repository = LegalRepository(uow.session)
                result: UserLegalAcceptanceOut | None = await repository.get_latest_acceptance(user_id, document)
                return result
        except Exception as e:
            raise FailedDependency(f"Failed to retrieve latest acceptance: {str(e)}")

    @trace_async
    async def check_compliance_status(
        self, user_id: UUID, locale: str | None = None
    ) -> dict[DocumentType, bool]:
        """Check user's compliance status for all document types."""
        try:
            async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                repository = LegalRepository(uow.session)

                status: dict[DocumentType, bool] = {}
                for doc_type_str in ["privacy", "terms", "cookies"]:
                    doc_type = cast(DocumentType, doc_type_str)
                    # Get current document
                    current_doc = await self.get_current_document(doc_type, locale)
                    if not current_doc:
                        status[doc_type] = False
                        continue

                    # Check if user has accepted current version
                    acceptance = await repository.get_acceptance(
                        user_id, doc_type, current_doc.version
                    )
                    status[doc_type] = acceptance is not None

                return status
        except Exception as e:
            raise FailedDependency(f"Failed to check compliance status: {str(e)}")


def create_legal_service(session_factory: async_sessionmaker[AsyncSession]) -> LegalService:
    """Factory function for LegalService."""
    return LegalService(session_factory)
