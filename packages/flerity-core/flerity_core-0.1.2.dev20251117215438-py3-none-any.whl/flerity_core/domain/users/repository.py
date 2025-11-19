"""Users repository for user profile management."""

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.engine import CursorResult
from sqlalchemy.ext.asyncio import AsyncSession

from ...utils.errors import BadRequest, Conflict, FailedDependency, NotFound
from ...utils.i18n import t
from ...utils.tracing import trace_async
from ...utils.request_tracking import RequestTracker
from ...utils.domain_logger import get_users_logger
from ..auth.schemas import user_credentials_table
from .schemas import UserOut, UserUpdate, users_table


class UsersRepository:
    """Repository for user operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    @trace_async
    async def get_user(self, user_id: UUID) -> UserOut | None:
        """Get user by ID. RLS enforced via user_id."""
        domain_logger = get_users_logger()
        
        with RequestTracker(operation="get_user", user_id=str(user_id)) as tracker:
            try:
                stmt = self._build_user_select_query().where(
                    sa.and_(
                        users_table.c.id == user_id,
                        users_table.c.deleted_at.is_(None)
                    )
                )
                result = await self.session.execute(stmt)
                row = result.fetchone()
                
                user = UserOut.model_validate(dict(row._mapping)) if row else None
                found = user is not None
                
                tracking_context = domain_logger.operation_start("get_user")
                domain_logger.operation_success(
                    tracking_context,
                    user_id=str(user_id),
                    found=found
                )
                tracker.log_success(result_id=f"found:{found}")
                
                return user
            except Exception as e:
                error_id = tracker.log_error(e, error_type=type(e).__name__)
                tracking_context = domain_logger.operation_start("get_user")
                domain_logger.operation_error(
                    tracking_context,
                    error=str(e),
                    error_id=error_id,
                    user_id=str(user_id)
                )
                raise

    @trace_async
    async def get_user_by_email(self, email: str) -> UserOut | None:
        """Get user by email."""
        if not email or not email.strip():
            raise BadRequest("Email cannot be empty")

        stmt = self._build_user_select_query().where(
            sa.and_(
                users_table.c.email == email.strip().lower(),
                users_table.c.deleted_at.is_(None)
            )
        )
        result = await self.session.execute(stmt)
        row = result.fetchone()
        return UserOut.model_validate(dict(row._mapping)) if row else None

    @trace_async
    async def create_user(self, email: str, gender: str | None = None, country: str | None = None, city: str | None = None, state: str | None = None, bio: str | None = None, invitation_code_used: str | None = None) -> UserOut:
        """Create new user."""
        domain_logger = get_users_logger()
        
        with RequestTracker(operation="create_user", email=email) as tracker:
            try:
                if not email or not email.strip():
                    raise BadRequest("Email cannot be empty")

                now = datetime.now(UTC)

                stmt = sa.insert(users_table).values(
                    id=uuid4(),
                    email=email.strip().lower(),
                    gender=gender,
                    country=country,
                    city=city,
                    state=state,
                    bio=bio,
                    invitation_code_used=invitation_code_used,
                    created_at=now,
                    updated_at=now
                ).returning(users_table)

                result = await self.session.execute(stmt)
                row = result.fetchone()
                if row is None:
                    raise FailedDependency("Failed to create user")
                
                user = UserOut.model_validate(dict(row._mapping))
                
                tracking_context = domain_logger.operation_start("create_user")
                domain_logger.operation_success(
                    tracking_context,
                    user_id=str(user.id),
                    email=email
                )
                tracker.log_success(result_id=str(user.id))
                
                return user
            except (BadRequest, Conflict, FailedDependency):
                raise
            except sa.exc.IntegrityError as e:
                error_id = tracker.log_error(e, error_type=type(e).__name__)
                tracking_context = domain_logger.operation_start("create_user")
                domain_logger.operation_error(
                    tracking_context,
                    error=str(e),
                    error_id=error_id,
                    email=email
                )
                if "unique" in str(e).lower():
                    raise Conflict("User with this email already exists")
                raise BadRequest(f"User creation failed: {str(e)}")
            except Exception as e:
                error_id = tracker.log_error(e, error_type=type(e).__name__)
                tracking_context = domain_logger.operation_start("create_user")
                domain_logger.operation_error(
                    tracking_context,
                    error=str(e),
                    error_id=error_id,
                    email=email
                )
                raise

    @trace_async
    async def update_user(self, user_id: UUID, data: UserUpdate, locale: str = "en-US") -> UserOut | None:
        """Update user by ID. RLS enforced via user_id."""
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            existing_user: UserOut | None = await self.get_user(user_id)
            return existing_user

        # Normalize email if provided
        if 'email' in update_data and update_data['email']:
            update_data['email'] = update_data['email'].strip().lower()

        update_data['updated_at'] = datetime.now(UTC)

        try:
            stmt = (
                sa.update(users_table)
                .where(
                    sa.and_(
                        users_table.c.id == user_id,
                        users_table.c.deleted_at.is_(None)
                    )
                )
                .values(**update_data)
                .returning(users_table)
            )

            result = await self.session.execute(stmt)
            row = result.fetchone()
            return UserOut.model_validate(dict(row._mapping)) if row else None
        except sa.exc.IntegrityError as e:
            error_str = str(e).lower()
            if "unique" in error_str:
                raise Conflict(t("users.error.email_already_in_use", locale=locale))
            elif "users_timezone_check" in error_str:
                raise BadRequest(t("users.error.invalid_timezone", locale=locale))
            elif "check" in error_str:
                raise BadRequest(t("users.error.invalid_data_format", locale=locale))
            raise BadRequest(t("users.error.update_failed", locale=locale))

    @trace_async
    async def delete_user(self, user_id: UUID) -> None:
        """Soft delete user by ID. RLS enforced via user_id."""
        now = datetime.now(UTC)
        stmt = (
            sa.update(users_table)
            .where(
                sa.and_(
                    users_table.c.id == user_id,
                    users_table.c.deleted_at.is_(None)
                )
            )
            .values(deleted_at=now, updated_at=now)
        )

        result: CursorResult[Any] = await self.session.execute(stmt)  # type: ignore[assignment]
        if result.rowcount == 0:
            raise NotFound("User not found")

    @trace_async
    async def list_users(self, limit: int = 50, offset: int = 0) -> list[UserOut]:
        """List users with pagination (admin only)."""
        if limit <= 0 or limit > 1000:
            raise BadRequest("Limit must be between 1 and 1000")
        if offset < 0:
            raise BadRequest("Offset must be non-negative")

        stmt = (
            self._build_user_select_query()
            .where(users_table.c.deleted_at.is_(None))
            .order_by(users_table.c.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        result = await self.session.execute(stmt)
        return [UserOut.model_validate(dict(row._mapping)) for row in result.fetchall()]

    @trace_async
    async def count_users(self) -> int:
        """Count total active users (admin only)."""
        stmt = sa.select(sa.func.count()).select_from(users_table).where(
            users_table.c.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    @trace_async
    async def update_last_login(self, user_id: UUID, last_login_at: datetime) -> bool:
        """Update user's last login timestamp. RLS enforced via user_id."""
        stmt = (
            sa.update(users_table)
            .where(
                sa.and_(
                    users_table.c.id == user_id,
                    users_table.c.deleted_at.is_(None)
                )
            )
            .values(last_login_at=last_login_at, updated_at=datetime.now(UTC))
        )
        result: CursorResult[Any] = await self.session.execute(stmt)  # type: ignore[assignment]
        return bool(result.rowcount and result.rowcount > 0)

    def _build_user_select_query(self) -> sa.Select[tuple[Any, ...]]:
        """Build common user select query with email verification."""
        return (
            sa.select(
                users_table.c.id,
                users_table.c.email,
                users_table.c.gender,
                users_table.c.country,
                users_table.c.city,
                users_table.c.state,
                users_table.c.locale,
                users_table.c.timezone,
                users_table.c.bio,
                users_table.c.tone,
                users_table.c.birth_month,
                users_table.c.birth_year,
                users_table.c.last_login_at,
                users_table.c.created_at,
                users_table.c.updated_at,
                sa.func.coalesce(user_credentials_table.c.email_verified, False).label('email_verified')
            )
            .select_from(
                users_table.outerjoin(
                    user_credentials_table,
                    users_table.c.id == user_credentials_table.c.user_id
                )
            )
        )
