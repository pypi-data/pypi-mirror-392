"""Repository for invitation codes domain."""

from datetime import UTC, datetime
from uuid import UUID

import sqlalchemy as sa
from flerity_core.utils.errors import BadRequest, Conflict, NotFound
from flerity_core.utils.request_tracking import RequestTracker
from flerity_core.utils.domain_logger import get_domain_logger
from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import (
    InvitationCodeOut,
    InvitationCodeStats,
    InvitationCodeUsageOut,
    invitation_code_usage_table,
    invitation_codes_table,
)

domain_logger = get_domain_logger(__name__)


class InvitationsRepository:
    """Repository for invitation codes operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_invitation_code(
        self,
        code: str,
        type: str,
        max_uses: int,
        expires_at: datetime | None = None,
        created_by: UUID | None = None,
        metadata: dict | None = None,
    ) -> InvitationCodeOut:
        """Create new invitation code."""
        with RequestTracker(user_id=str(created_by) if created_by else None, operation="create_invitation_code_db") as tracker:
            try:
                domain_logger.database_operation("create_invitation_code", {
                    "code": code,
                    "type": type,
                    "max_uses": max_uses,
                    "created_by": str(created_by) if created_by else None
                })
                
                # Check if code already exists
                existing = await self.session.scalar(
                    sa.select(invitation_codes_table.c.id).where(invitation_codes_table.c.code == code)
                )
                if existing:
                    raise Conflict("invitation_code_already_exists")

                stmt = sa.insert(invitation_codes_table).values(
                    code=code,
                    type=type,
                    max_uses=max_uses,
                    expires_at=expires_at,
                    created_by=created_by,
                    metadata=metadata,
                ).returning(invitation_codes_table)

                result = await self.session.execute(stmt)
                row = result.fetchone()
                if not row:
                    raise BadRequest("Failed to create invitation code")

                invitation_code = InvitationCodeOut.model_validate(dict(row._mapping))
                
                domain_logger.business_event("invitation_code_db_created", {
                    "invitation_id": str(invitation_code.id),
                    "code": code,
                    "type": type,
                    "max_uses": max_uses
                })
                
                tracker.log_success(result_id=str(invitation_code.id))
                return invitation_code
                
            except Exception as e:
                error_id = tracker.log_error(e, context={"code": code, "type": type})
                domain_logger.operation_error(tracking_context, str(e), {
                    "error_id": error_id,
                    "code": code
                })
                raise

    async def get_invitation_code(self, code: str) -> InvitationCodeOut | None:
        """Get invitation code by code."""
        result = await self.session.execute(
            sa.select(invitation_codes_table).where(invitation_codes_table.c.code == code)
        )
        row = result.fetchone()

        if not row:
            return None

        return InvitationCodeOut.model_validate(dict(row._mapping))

    async def validate_invitation_code(self, code: str) -> InvitationCodeOut:
        """Validate invitation code for usage."""
        result = await self.session.execute(
            sa.select(invitation_codes_table).where(invitation_codes_table.c.code == code)
        )
        row = result.fetchone()

        if not row:
            raise NotFound("invitation_code_not_found")

        invitation_code = InvitationCodeOut.model_validate(dict(row._mapping))

        if not invitation_code.is_active:
            raise BadRequest("invitation_code_inactive")

        if invitation_code.expires_at and invitation_code.expires_at < datetime.now(UTC):
            raise BadRequest("invitation_code_expired")

        if invitation_code.current_uses >= invitation_code.max_uses:
            raise BadRequest("invitation_code_max_uses_exceeded")

        return invitation_code

    async def use_invitation_code(
        self,
        code: str,
        user_id: UUID,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> InvitationCodeUsageOut:
        """Use invitation code and record usage."""
        with RequestTracker(user_id=str(user_id), operation="use_invitation_code_db") as tracker:
            try:
                domain_logger.database_operation("use_invitation_code", {
                    "code": code,
                    "user_id": str(user_id),
                    "ip_address": ip_address,
                    "has_user_agent": bool(user_agent)
                })
                
                # Validate code first
                await self.validate_invitation_code(code)

                # Check if user already used this code
                existing_usage = await self.session.scalar(
                    sa.select(invitation_code_usage_table.c.id).where(
                        invitation_code_usage_table.c.invitation_code == code,
                        invitation_code_usage_table.c.user_id == user_id
                    )
                )
                if existing_usage:
                    raise Conflict("invitation_code_already_used_by_user")

                # Increment usage count
                await self.session.execute(
                    sa.update(invitation_codes_table)
                    .where(invitation_codes_table.c.code == code)
                    .values(current_uses=invitation_codes_table.c.current_uses + 1)
                )

                # Record usage
                stmt = sa.insert(invitation_code_usage_table).values(
                    invitation_code=code,
                    user_id=user_id,
                    ip_address=ip_address,
                    user_agent=user_agent,
                ).returning(invitation_code_usage_table)

                result = await self.session.execute(stmt)
                row = result.fetchone()
                if not row:
                    raise BadRequest("Failed to record invitation code usage")

                usage = InvitationCodeUsageOut.model_validate(dict(row._mapping))
                
                domain_logger.business_event("invitation_code_db_used", {
                    "usage_id": str(usage.id),
                    "code": code,
                    "user_id": str(user_id),
                    "ip_address": ip_address
                })
                
                tracker.log_success(result_id=str(usage.id))
                return usage
                
            except Exception as e:
                error_id = tracker.log_error(e, context={"code": code, "user_id": str(user_id)})
                domain_logger.operation_error(tracking_context, str(e), {
                    "error_id": error_id,
                    "code": code
                })
                raise

    async def list_invitation_codes(
        self,
        limit: int = 20,
        offset: int = 0,
        active_only: bool = False,
    ) -> list[InvitationCodeOut]:
        """List invitation codes (admin only)."""
        query = sa.select(invitation_codes_table).order_by(invitation_codes_table.c.created_at.desc())

        if active_only:
            query = query.where(
                invitation_codes_table.c.is_active,
                sa.or_(
                    invitation_codes_table.c.expires_at.is_(None),
                    invitation_codes_table.c.expires_at > datetime.now(UTC)
                )
            )

        query = query.limit(limit).offset(offset)

        result = await self.session.execute(query)
        return [InvitationCodeOut.model_validate(dict(row._mapping)) for row in result]

    async def get_invitation_code_stats(self) -> InvitationCodeStats:
        """Get invitation code statistics."""
        total_codes = await self.session.scalar(
            sa.select(sa.func.count(invitation_codes_table.c.id))
        ) or 0

        active_codes = await self.session.scalar(
            sa.select(sa.func.count(invitation_codes_table.c.id)).where(
                invitation_codes_table.c.is_active,
                sa.or_(
                    invitation_codes_table.c.expires_at.is_(None),
                    invitation_codes_table.c.expires_at > datetime.now(UTC)
                )
            )
        ) or 0

        total_uses = await self.session.scalar(
            sa.select(sa.func.sum(invitation_codes_table.c.current_uses))
        ) or 0

        conversion_rate = (total_uses / total_codes * 100) if total_codes > 0 else 0.0

        return InvitationCodeStats(
            total_codes=total_codes,
            active_codes=active_codes,
            total_uses=total_uses,
            conversion_rate=round(conversion_rate, 2)
        )
