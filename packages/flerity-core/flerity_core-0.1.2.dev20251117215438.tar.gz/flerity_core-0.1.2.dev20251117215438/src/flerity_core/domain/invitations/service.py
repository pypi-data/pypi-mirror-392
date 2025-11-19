"""Service layer for invitation codes domain."""
from uuid import UUID

from flerity_core.domain.invitations.repository import InvitationsRepository
from flerity_core.domain.invitations.schemas import (
    InvitationCodeCreate,
    InvitationCodeOut,
    InvitationCodeStats,
    InvitationCodeUsageOut,
)
from flerity_core.utils.codes import generate_invitation_code
from flerity_core.utils.request_tracking import RequestTracker
from flerity_core.utils.domain_logger import get_domain_logger
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

domain_logger = get_domain_logger(__name__)


class InvitationsService:
    """Service for invitation codes business logic."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory

    async def create_invitation_code(
        self,
        data: InvitationCodeCreate,
        created_by: UUID | None = None,
    ) -> InvitationCodeOut:
        """Create new invitation code with auto-generated code."""
        with RequestTracker(user_id=str(created_by) if created_by else None, operation="create_invitation_code") as tracker:
            try:
                tracking_context = domain_logger.operation_start("create_invitation_code", type=data.type, max_uses=data.max_uses, expires_at=str(data.expires_at) if data.expires_at else None, created_by=str(created_by) if created_by else None)
                
                async with self.session_factory() as session:
                    repository = InvitationsRepository(session)

                    # Generate unique code
                    code = generate_invitation_code()

                    # Set default metadata based on type
                    metadata = data.metadata or self._get_default_metadata(data.type)

                    result = await repository.create_invitation_code(
                        code=code,
                        type=data.type,
                        max_uses=data.max_uses,
                        expires_at=data.expires_at,
                        created_by=created_by,
                        metadata=metadata,
                    )
                    await session.commit()
                    
                    # Business event logging
                    domain_logger.business_event("invitation_code_created", {
                        "invitation_id": str(result.id),
                        "code": code,
                        "type": data.type,
                        "max_uses": data.max_uses,
                        "created_by": str(created_by) if created_by else None,
                        "metadata": metadata
                    })
                    
                    domain_logger.operation_success(tracking_context, {
                        "invitation_id": str(result.id),
                        "code": code,
                        "type": data.type
                    })
                    
                    tracker.log_success(result_id=str(result.id))
                    return result
                    
            except Exception as e:
                error_id = tracker.log_error(e, context={
                    "type": data.type,
                    "max_uses": data.max_uses
                })
                domain_logger.operation_error(tracking_context, str(e), {
                    "error_id": error_id,
                    "type": data.type
                })
                raise

    async def validate_invitation_code(self, code: str) -> InvitationCodeOut:
        """Validate invitation code for usage."""
        with RequestTracker(operation="validate_invitation_code") as tracker:
            try:
                tracking_context = domain_logger.operation_start("validate_invitation_code", code=code)
                
                async with self.session_factory() as session:
                    repository = InvitationsRepository(session)
                    result = await repository.validate_invitation_code(code)
                    
                    domain_logger.operation_success(tracking_context, {
                        "code": code,
                        "invitation_id": str(result.id),
                        "is_valid": True,
                        "type": result.type
                    })
                    
                    tracker.log_success(result_id=str(result.id))
                    return result
                    
            except Exception as e:
                error_id = tracker.log_error(e, context={"code": code})
                domain_logger.operation_error(tracking_context, str(e), {
                    "error_id": error_id,
                    "code": code
                })
                raise

    async def use_invitation_code(
        self,
        code: str,
        user_id: UUID,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> InvitationCodeUsageOut:
        """Use invitation code and apply benefits."""
        with RequestTracker(user_id=str(user_id), operation="use_invitation_code") as tracker:
            try:
                tracking_context = domain_logger.operation_start("use_invitation_code", code=code, user_id=str(user_id), ip_address=ip_address, has_user_agent=bool(user_agent))
                
                async with self.session_factory() as session:
                    repository = InvitationsRepository(session)
                    result = await repository.use_invitation_code(
                        code=code,
                        user_id=user_id,
                        ip_address=ip_address,
                        user_agent=user_agent,
                    )
                    await session.commit()
                    
                    # Business event logging
                    domain_logger.business_event("invitation_code_used", {
                        "usage_id": str(result.id),
                        "code": code,
                        "user_id": str(user_id),
                        "invitation_id": str(result.invitation_id),
                        "ip_address": ip_address,
                        "used_at": str(result.used_at)
                    })
                    
                    domain_logger.operation_success(tracking_context, {
                        "usage_id": str(result.id),
                        "code": code,
                        "user_id": str(user_id)
                    })
                    
                    tracker.log_success(result_id=str(result.id))
                    return result
                    
            except Exception as e:
                error_id = tracker.log_error(e, context={
                    "code": code,
                    "user_id": str(user_id)
                })
                domain_logger.operation_error(tracking_context, str(e), {
                    "error_id": error_id,
                    "code": code,
                    "user_id": str(user_id)
                })
                raise

    async def list_invitation_codes(
        self,
        limit: int = 20,
        offset: int = 0,
        active_only: bool = False,
    ) -> list[InvitationCodeOut]:
        """List invitation codes (admin only)."""
        with RequestTracker(operation="list_invitation_codes") as tracker:
            try:
                tracking_context = domain_logger.operation_start("list_invitation_codes", limit=limit, offset=offset, active_only=active_only)
                
                async with self.session_factory() as session:
                    repository = InvitationsRepository(session)
                    result = await repository.list_invitation_codes(
                        limit=limit,
                        offset=offset,
                        active_only=active_only,
                    )
                    
                    domain_logger.operation_success(tracking_context, {
                        "count": len(result),
                        "limit": limit,
                        "offset": offset,
                        "active_only": active_only
                    })
                    
                    tracker.log_success(result_id=f"count_{len(result)}")
                    return result
                    
            except Exception as e:
                error_id = tracker.log_error(e, context={
                    "limit": limit,
                    "offset": offset,
                    "active_only": active_only
                })
                domain_logger.operation_error(tracking_context, str(e), {
                    "error_id": error_id,
                    "limit": limit
                })
                raise

    async def get_invitation_code_stats(self) -> InvitationCodeStats:
        """Get invitation code statistics."""
        with RequestTracker(operation="get_invitation_code_stats") as tracker:
            try:
                tracking_context = domain_logger.operation_start("get_invitation_code_stats", {})
                
                async with self.session_factory() as session:
                    repository = InvitationsRepository(session)
                    result = await repository.get_invitation_code_stats()
                    
                    domain_logger.operation_success(tracking_context, {
                        "total_codes": result.total_codes,
                        "active_codes": result.active_codes,
                        "total_uses": result.total_uses
                    })
                    
                    tracker.log_success(result_id="stats")
                    return result
                    
            except Exception as e:
                error_id = tracker.log_error(e, context={})
                domain_logger.operation_error(tracking_context, str(e), {
                    "error_id": error_id
                })
                raise

    def _get_default_metadata(self, code_type: str) -> dict:
        """Get default metadata based on invitation code type."""
        metadata_map = {
            "free": {
                "trial_days": 0,
                "features": ["basic"]
            },
            "premium": {
                "trial_days": 30,
                "features": ["premium", "ai_unlimited"]
            },
            "trial": {
                "trial_days": 7,
                "features": ["premium"]
            }
        }
        return metadata_map.get(code_type, {})
