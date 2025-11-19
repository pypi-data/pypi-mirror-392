"""Integration repository for managing user integrations with external providers."""

from typing import Any, cast
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from ...utils.domain_logger import get_domain_logger
from ...utils.errors import BadRequest, Conflict, NotFound
from ...utils.logging import get_logger
from ...utils.request_tracking import RequestTracker
from ...utils.tracing import trace_async
from .schemas import (
    IntegrationAccountCreate,
    IntegrationAccountOut,
    IntegrationAccountUpdate,
    IntegrationType,
    PairingStatus,
    WhatsAppPairingSessionCreate,
    WhatsAppPairingSessionOut,
    WhatsAppPairingSessionUpdate,
    integrations_accounts_table,
    whatsapp_pairing_sessions_table,
)

logger = get_logger(__name__)
domain_logger = get_domain_logger(__name__)


class IntegrationRepository:
    """Repository for integration data access operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    @trace_async
    async def get_by_user_provider(
        self, user_id: UUID, provider: IntegrationType
    ) -> IntegrationAccountOut | None:
        """Get integration by user and provider (RLS enforced)."""
        with RequestTracker(user_id=user_id, operation="get_by_user_provider") as tracker:
            try:
                tracking_context = domain_logger.operation_start("get_by_user_provider", user_id=str(user_id), 
                                            context={"provider": provider})
                
                stmt = sa.select(integrations_accounts_table).where(
                    sa.and_(
                        integrations_accounts_table.c.user_id == user_id,
                        integrations_accounts_table.c.provider == provider
                    )
                )

                result = await self.session.execute(stmt)
                row = result.fetchone()
                integration = IntegrationAccountOut.model_validate(row._asdict()) if row else None
                
                domain_logger.operation_success(tracking_context, user_id=str(user_id), 
                                              context={"found": integration is not None})
                
                tracker.log_success(result_id=str(integration.id) if integration else None)
                return integration
                
            except sa.exc.SQLAlchemyError as e:
                error_id = tracker.log_error(e, context={"user_id": str(user_id), "provider": provider})
                domain_logger.operation_error(tracking_context, error_id=error_id, user_id=str(user_id))
                logger.error("Database error getting integration", extra={
                    "user_id": str(user_id), "provider": provider, "error": str(e)
                })
                raise BadRequest("Failed to retrieve integration")
            except Exception as e:
                error_id = tracker.log_error(e, context={"user_id": str(user_id), "provider": provider})
                domain_logger.operation_error(tracking_context, error_id=error_id, user_id=str(user_id))
                logger.error("Unexpected error getting integration", extra={
                    "user_id": str(user_id), "provider": provider, "error": str(e)
                })
                raise BadRequest("Failed to retrieve integration")

    @trace_async
    async def list_by_user(self, user_id: UUID) -> list[IntegrationAccountOut]:
        """List all integrations for a user (RLS enforced)."""
        try:
            stmt = (
                sa.select(integrations_accounts_table)
                .where(integrations_accounts_table.c.user_id == user_id)
                .order_by(integrations_accounts_table.c.created_at.desc())
            )

            result = await self.session.execute(stmt)
            return [IntegrationAccountOut.model_validate(row._asdict()) for row in result.fetchall()]
        except sa.exc.SQLAlchemyError as e:
            logger.error("Database error listing integrations", extra={
                "user_id": str(user_id), "error": str(e)
            })
            raise BadRequest("Failed to retrieve integrations")
        except Exception as e:
            logger.error("Unexpected error listing integrations", extra={
                "user_id": str(user_id), "error": str(e)
            })
            raise BadRequest("Failed to retrieve integrations")

    @trace_async
    async def create(self, data: IntegrationAccountCreate, locale: str = "en-US") -> IntegrationAccountOut:
        """Create a new integration."""
        from ...utils.i18n import t

        integration_data = data.model_dump()

        try:
            stmt = sa.insert(integrations_accounts_table).values(**integration_data).returning(integrations_accounts_table)
            result = await self.session.execute(stmt)
            row = result.fetchone()
            if row is None:
                provider = integration_data.get("provider", "unknown")
                error_key = f"integrations.error.{provider}_auth_failed" if provider in ["instagram", "whatsapp"] else "integrations.error.auth_failed"
                raise BadRequest(t(error_key, locale=locale))
            return IntegrationAccountOut.model_validate(row._asdict())
        except sa.exc.IntegrityError as e:
            logger.error("Integration creation integrity error", extra={
                "provider": integration_data.get("provider"), "error": str(e)
            })
            provider = integration_data.get("provider", "unknown")
            error_key = f"integrations.error.{provider}_auth_failed" if provider in ["instagram", "whatsapp"] else "integrations.error.auth_failed"
            raise Conflict(t(error_key, locale=locale))
        except sa.exc.SQLAlchemyError as e:
            logger.error("Database error creating integration", extra={
                "provider": integration_data.get("provider"), "error": str(e)
            })
            provider = integration_data.get("provider", "unknown")
            error_key = f"integrations.error.{provider}_auth_failed" if provider in ["instagram", "whatsapp"] else "integrations.error.auth_failed"
            raise BadRequest(t(error_key, locale=locale))
        except Exception as e:
            logger.error("Unexpected error creating integration", extra={
                "provider": integration_data.get("provider"), "error": str(e)
            })
            provider = integration_data.get("provider", "unknown")
            error_key = f"integrations.error.{provider}_auth_failed" if provider in ["instagram", "whatsapp"] else "integrations.error.auth_failed"
            raise BadRequest(t(error_key, locale=locale))

    @trace_async
    async def update(
        self, user_id: UUID, provider: IntegrationType, data: IntegrationAccountUpdate
    ) -> IntegrationAccountOut | None:
        """Update integration."""
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return cast(IntegrationAccountOut | None, await self.get_by_user_provider(user_id, provider))

        update_data['updated_at'] = sa.func.now()

        stmt = (
            sa.update(integrations_accounts_table)
            .where(
                sa.and_(
                    integrations_accounts_table.c.user_id == user_id,
                    integrations_accounts_table.c.provider == provider
                )
            )
            .values(**update_data)
            .returning(integrations_accounts_table)
        )

        result = await self.session.execute(stmt)
        row = result.fetchone()
        if row:
            return IntegrationAccountOut.model_validate(row._asdict())
        return None

    @trace_async
    async def upsert(
        self, user_id: UUID, provider: IntegrationType, meta: dict[str, Any]
    ) -> IntegrationAccountOut:
        """Upsert integration with meta data."""
        stmt = pg_insert(integrations_accounts_table).values(
            user_id=user_id,
            provider=provider,
            status='connected',
            meta=meta
        ).on_conflict_do_update(
            index_elements=['user_id', 'provider'],
            set_=dict(
                meta=pg_insert(integrations_accounts_table).excluded.meta,
                status='connected',
                updated_at=sa.func.now()
            )
        ).returning(integrations_accounts_table)

        result = await self.session.execute(stmt)
        row = result.fetchone()

        if not row:
            raise BadRequest("Failed to upsert integration")

        return IntegrationAccountOut.model_validate(row._asdict())

    @trace_async
    async def delete(self, user_id: UUID, provider: IntegrationType) -> None:
        """Delete integration."""
        stmt = sa.delete(integrations_accounts_table).where(
            sa.and_(
                integrations_accounts_table.c.user_id == user_id,
                integrations_accounts_table.c.provider == provider
            )
        )

        result = await self.session.execute(stmt)
        if getattr(result, 'rowcount', 0) == 0:
            raise NotFound(f"Integration {provider} not found")

    @trace_async
    async def exists(self, user_id: UUID, provider: IntegrationType) -> bool:
        """Check if integration exists."""
        stmt = sa.select(sa.func.count()).select_from(integrations_accounts_table).where(
            sa.and_(
                integrations_accounts_table.c.user_id == user_id,
                integrations_accounts_table.c.provider == provider
            )
        )

        result = await self.session.execute(stmt)
        count = result.scalar()
        return (count or 0) > 0


class WhatsAppPairingRepository:
    """Repository for WhatsApp pairing sessions."""

    def __init__(self, session: AsyncSession):
        self.session = session

    @trace_async
    async def create_session(self, data: WhatsAppPairingSessionCreate) -> WhatsAppPairingSessionOut:
        """Create new pairing session."""
        session_data = data.model_dump()

        try:
            stmt = sa.insert(whatsapp_pairing_sessions_table).values(**session_data).returning(whatsapp_pairing_sessions_table)
            result = await self.session.execute(stmt)
            row = result.fetchone()
            if row is None:
                raise BadRequest("Failed to create WhatsApp pairing session")
            return WhatsAppPairingSessionOut.model_validate(row._asdict())
        except sa.exc.SQLAlchemyError as e:
            logger.error("Database error creating pairing session", extra={"error": str(e)})
            raise BadRequest("Failed to create pairing session")
        except Exception as e:
            logger.error("Unexpected error creating pairing session", extra={"error": str(e)})
            raise BadRequest("Failed to create pairing session")

    @trace_async
    async def get_by_code(self, session_code: str) -> WhatsAppPairingSessionOut | None:
        """Get pairing session by code."""
        stmt = sa.select(whatsapp_pairing_sessions_table).where(
            whatsapp_pairing_sessions_table.c.session_code == session_code
        )

        result = await self.session.execute(stmt)
        row = result.fetchone()
        return WhatsAppPairingSessionOut.model_validate(row._asdict()) if row else None

    @trace_async
    async def get_by_user(self, user_id: UUID) -> list[WhatsAppPairingSessionOut]:
        """Get all pairing sessions for a user."""
        stmt = (
            sa.select(whatsapp_pairing_sessions_table)
            .where(whatsapp_pairing_sessions_table.c.user_id == user_id)
            .order_by(whatsapp_pairing_sessions_table.c.created_at.desc())
        )

        result = await self.session.execute(stmt)
        return [WhatsAppPairingSessionOut.model_validate(row._asdict()) for row in result.fetchall()]

    @trace_async
    async def update(self, session_id: UUID, data: WhatsAppPairingSessionUpdate) -> WhatsAppPairingSessionOut | None:
        """Update pairing session."""
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            select_stmt = sa.select(whatsapp_pairing_sessions_table).where(whatsapp_pairing_sessions_table.c.id == session_id)
            result = await self.session.execute(select_stmt)
            row = result.fetchone()
            return WhatsAppPairingSessionOut.model_validate(row._asdict()) if row else None

        update_data['updated_at'] = sa.func.now()

        update_stmt = (
            sa.update(whatsapp_pairing_sessions_table)
            .where(whatsapp_pairing_sessions_table.c.id == session_id)
            .values(**update_data)
            .returning(whatsapp_pairing_sessions_table)
        )

        result = await self.session.execute(update_stmt)
        row = result.fetchone()
        return WhatsAppPairingSessionOut.model_validate(row._asdict()) if row else None

    @trace_async
    async def update_status(self, session_id: UUID, status: PairingStatus) -> WhatsAppPairingSessionOut:
        """Update pairing session status."""
        stmt = (
            sa.update(whatsapp_pairing_sessions_table)
            .where(whatsapp_pairing_sessions_table.c.id == session_id)
            .values(status=status, updated_at=sa.func.now())
            .returning(whatsapp_pairing_sessions_table)
        )

        result = await self.session.execute(stmt)
        row = result.fetchone()

        if not row:
            raise NotFound("Pairing session not found")

        return WhatsAppPairingSessionOut.model_validate(row._asdict())

    @trace_async
    async def delete_session(self, session_id: UUID) -> None:
        """Delete pairing session."""
        try:
            stmt = sa.delete(whatsapp_pairing_sessions_table).where(
                whatsapp_pairing_sessions_table.c.id == session_id
            )

            result = await self.session.execute(stmt)
            if getattr(result, 'rowcount', 0) == 0:
                raise NotFound("Pairing session not found")
        except NotFound:
            raise
        except sa.exc.SQLAlchemyError as e:
            logger.error("Database error deleting pairing session", extra={
                "session_id": str(session_id), "error": str(e)
            })
            raise BadRequest("Failed to delete pairing session")
        except Exception as e:
            logger.error("Unexpected error deleting pairing session", extra={
                "session_id": str(session_id), "error": str(e)
            })
            raise BadRequest("Failed to delete pairing session")

    @trace_async
    async def cleanup_expired_sessions(self, expiry_hours: int = 24) -> int:
        """Clean up expired pairing sessions."""
        try:
            stmt = sa.delete(whatsapp_pairing_sessions_table).where(
                whatsapp_pairing_sessions_table.c.created_at < sa.func.now() - sa.text(f"INTERVAL '{expiry_hours} hours'")
            )

            result = await self.session.execute(stmt)
            deleted_count = getattr(result, 'rowcount', 0)

            logger.info("Cleaned up expired pairing sessions", extra={
                "deleted_count": deleted_count, "expiry_hours": expiry_hours
            })

            return deleted_count
        except sa.exc.SQLAlchemyError as e:
            logger.error("Database error cleaning up sessions", extra={"error": str(e)})
            raise BadRequest("Failed to cleanup sessions")
        except Exception as e:
            logger.error("Unexpected error cleaning up sessions", extra={"error": str(e)})
            raise BadRequest("Failed to cleanup sessions")

    @trace_async
    async def expire_old_sessions(self) -> int:
        """Expire old pairing sessions."""
        try:
            stmt = (
                sa.update(whatsapp_pairing_sessions_table)
                .where(
                    sa.and_(
                        whatsapp_pairing_sessions_table.c.expires_at < sa.func.now(),
                        whatsapp_pairing_sessions_table.c.status == 'issued'
                    )
                )
                .values(status='expired', updated_at=sa.func.now())
            )

            result = await self.session.execute(stmt)
            expired_count = getattr(result, 'rowcount', 0)

            logger.info("Expired old pairing sessions", extra={"expired_count": expired_count})

            return expired_count
        except sa.exc.SQLAlchemyError as e:
            logger.error("Database error expiring sessions", extra={"error": str(e)})
            raise BadRequest("Failed to expire sessions")
        except Exception as e:
            logger.error("Unexpected error expiring sessions", extra={"error": str(e)})
            raise BadRequest("Failed to expire sessions")
