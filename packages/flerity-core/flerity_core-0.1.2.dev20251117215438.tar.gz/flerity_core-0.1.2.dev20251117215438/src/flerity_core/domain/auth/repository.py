"""Authentication repository for user credentials and token management."""

from datetime import datetime, timedelta
from typing import Any, cast
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.engine import CursorResult
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ...utils.clock import utcnow
from ...utils.errors import ConflictError
from ...utils.logging import get_logger
from ...utils.tracing import trace_async
from ...utils.request_tracking import RequestTracker
from ...utils.domain_logger import get_auth_logger
from .schemas import (
    EmailVerificationTokenOut,
    PasswordResetTokenOut,
    RefreshTokenOut,
    SessionOut,
    SocialAccountOut,
    UserCredentialsOut,
    email_verification_tokens_table,
    jwt_blacklist_table,
    password_reset_tokens_table,
    social_accounts_table,
    user_credentials_table,
    user_refresh_tokens_table,
    user_sessions_table,
)

logger = get_logger(__name__)


class AuthRepository:
    """Repository for authentication operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # User Credentials Operations
    @trace_async
    async def get_user_credentials(self, user_id: UUID) -> UserCredentialsOut | None:
        """Get user credentials by user ID."""
        domain_logger = get_auth_logger()
        
        with RequestTracker(operation="get_user_credentials", user_id=str(user_id)) as tracker:
            try:
                stmt = sa.select(user_credentials_table).where(
                    user_credentials_table.c.user_id == user_id
                )
                result = await self.session.execute(stmt)
                row = result.fetchone()
                
                credentials = UserCredentialsOut.model_validate(row._asdict()) if row else None
                found = credentials is not None
                
                tracking_context = domain_logger.operation_start("get_user_credentials")

                
                domain_logger.operation_success(tracking_context,
                    user_id=str(user_id),
                    found=found
                )
                tracker.log_success(result_id=f"found:{found}")
                
                return credentials
            except Exception as e:
                error_id = tracker.log_error(e, error_type=type(e).__name__)
                tracking_context = domain_logger.operation_start("get_user_credentials")

                domain_logger.operation_error(tracking_context,
                    error=str(e),
                    error_id=error_id,
                    user_id=str(user_id)
                )
                raise

    @trace_async
    async def get_user_credentials_by_email(self, email: str) -> UserCredentialsOut | None:
        """Get user credentials by email (join with users table)."""
        domain_logger = get_auth_logger()
        
        with RequestTracker(operation="get_user_credentials_by_email", email=email) as tracker:
            try:
                from ...domain.users.schemas import users_table

                stmt = (
                    sa.select(user_credentials_table)
                    .select_from(
                        user_credentials_table.join(
                            users_table,
                            user_credentials_table.c.user_id == users_table.c.id
                        )
                    )
                    .where(users_table.c.email == email)
                )
                result = await self.session.execute(stmt)
                row = result.fetchone()
                
                credentials = UserCredentialsOut.model_validate(row._asdict()) if row else None
                found = credentials is not None
                
                tracking_context = domain_logger.operation_start("get_user_credentials_by_email")

                
                domain_logger.operation_success(tracking_context,
                    email=email,
                    found=found
                )
                tracker.log_success(result_id=f"found:{found}")
                
                return credentials
            except Exception as e:
                error_id = tracker.log_error(e, error_type=type(e).__name__)
                tracking_context = domain_logger.operation_start("get_user_credentials_by_email")

                domain_logger.operation_error(tracking_context,
                    error=str(e),
                    error_id=error_id,
                    email=email
                )
                raise

    @trace_async
    async def create_user_credentials(self, user_id: UUID, password_hash: str, password_salt: str, locale: str = "en-US") -> UserCredentialsOut:
        """Create new user credentials."""
        from ...utils.i18n import t

        now = utcnow()
        stmt = sa.insert(user_credentials_table).values(
            user_id=user_id,
            password_hash=password_hash,
            password_salt=password_salt,
            email_verified=False,
            password_changed_at=now,
            failed_attempts=0,
            created_at=now,
            updated_at=now
        ).returning(user_credentials_table)

        result = await self.session.execute(stmt)
        row = result.fetchone()
        if row is None:
            raise ConflictError(t("auth.error.registration_failed", locale=locale))
        return UserCredentialsOut.model_validate(row._asdict())

    @trace_async
    async def update_password(self, user_id: UUID, password_hash: str, password_salt: str) -> bool:
        """Update user password."""
        now = utcnow()
        stmt = (
            sa.update(user_credentials_table)
            .where(user_credentials_table.c.user_id == user_id)
            .values(
                password_hash=password_hash,
                password_salt=password_salt,
                password_changed_at=now,
                failed_attempts=0,
                locked_until=None,
                updated_at=now
            )
        )
        result = cast(CursorResult[Any], await self.session.execute(stmt))
        return (getattr(result, 'rowcount', 0) or 0) > 0

    @trace_async
    async def increment_failed_attempts(self, user_id: UUID, lockout_duration: timedelta | None = None) -> bool:
        """Increment failed login attempts and optionally lock account."""
        now = utcnow()
        values = {
            "failed_attempts": user_credentials_table.c.failed_attempts + 1,
            "updated_at": now
        }

        if lockout_duration:
            values["locked_until"] = now + lockout_duration

        stmt = (
            sa.update(user_credentials_table)
            .where(user_credentials_table.c.user_id == user_id)
            .values(**values)
        )
        result = cast(CursorResult[Any], await self.session.execute(stmt))
        return getattr(result, 'rowcount', 0) > 0

    @trace_async
    async def reset_failed_attempts(self, user_id: UUID) -> bool:
        """Reset failed attempts and unlock account."""
        stmt = (
            sa.update(user_credentials_table)
            .where(user_credentials_table.c.user_id == user_id)
            .values(
                failed_attempts=0,
                locked_until=None,
                updated_at=utcnow()
            )
        )
        result = cast(CursorResult[Any], await self.session.execute(stmt))
        return getattr(result, 'rowcount', 0) > 0

    @trace_async
    async def verify_email(self, user_id: UUID) -> bool:
        """Mark user email as verified."""
        now = utcnow()

        # Update user_credentials table
        stmt = (
            sa.update(user_credentials_table)
            .where(user_credentials_table.c.user_id == user_id)
            .values(
                email_verified=True,
                email_verified_at=now,
                updated_at=now
            )
        )
        result = cast(CursorResult[Any], await self.session.execute(stmt))

        # Also update users table
        from ...domain.users.schemas import users_table
        users_stmt = (
            sa.update(users_table)
            .where(users_table.c.id == user_id)
            .values(
                email_verified=True,
                updated_at=now
            )
        )
        await self.session.execute(users_stmt)

        logger.info("Email verified in both tables", extra={
            "user_id": str(user_id),
            "credentials_updated": getattr(result, 'rowcount', 0) > 0
        })

        return getattr(result, 'rowcount', 0) > 0

    # Refresh Token Operations
    @trace_async
    async def create_refresh_token(self, user_id: UUID, token_hash: str, device_id: str | None, expires_at: datetime, locale: str = "en-US") -> RefreshTokenOut:
        """Create new refresh token."""
        from ...utils.i18n import t

        stmt = sa.insert(user_refresh_tokens_table).values(
            id=uuid4(),
            user_id=user_id,
            token_hash=token_hash,
            device_id=device_id,
            expires_at=expires_at,
            created_at=utcnow()
        ).returning(user_refresh_tokens_table)

        result = await self.session.execute(stmt)
        row = result.fetchone()
        if row is None:
            raise ConflictError(t("auth.error.registration_failed", locale=locale))
        return RefreshTokenOut.model_validate(row._asdict())

    @trace_async
    async def get_refresh_token(self, token_hash: str) -> RefreshTokenOut | None:
        """Get refresh token by hash."""
        stmt = sa.select(user_refresh_tokens_table).where(
            sa.and_(
                user_refresh_tokens_table.c.token_hash == token_hash,
                user_refresh_tokens_table.c.revoked_at.is_(None),
                user_refresh_tokens_table.c.expires_at > utcnow()
            )
        )
        result = await self.session.execute(stmt)
        row = result.fetchone()
        return RefreshTokenOut.model_validate(row._asdict()) if row else None

    @trace_async
    async def update_refresh_token_usage(self, token_hash: str) -> bool:
        """Update refresh token last used timestamp."""
        stmt = (
            sa.update(user_refresh_tokens_table)
            .where(user_refresh_tokens_table.c.token_hash == token_hash)
            .values(last_used_at=utcnow())
        )
        result = cast(CursorResult[Any], await self.session.execute(stmt))
        return getattr(result, 'rowcount', 0) > 0

    @trace_async
    async def revoke_refresh_token(self, token_hash: str) -> bool:
        """Revoke refresh token."""
        stmt = (
            sa.update(user_refresh_tokens_table)
            .where(user_refresh_tokens_table.c.token_hash == token_hash)
            .values(revoked_at=utcnow())
        )
        result = await self.session.execute(stmt)
        return getattr(result, 'rowcount', 0) > 0

    @trace_async
    async def revoke_user_refresh_tokens(self, user_id: UUID, device_id: str | None = None) -> int:
        """Revoke all refresh tokens for user (optionally filtered by device)."""
        where_clause = [
            user_refresh_tokens_table.c.user_id == user_id,
            user_refresh_tokens_table.c.revoked_at.is_(None)
        ]

        if device_id:
            where_clause.append(user_refresh_tokens_table.c.device_id == device_id)

        stmt = (
            sa.update(user_refresh_tokens_table)
            .where(sa.and_(*where_clause))
            .values(revoked_at=utcnow())
        )
        result = await self.session.execute(stmt)
        return getattr(result, 'rowcount', 0)

    @trace_async
    async def cleanup_expired_refresh_tokens(self) -> int:
        """Remove expired refresh tokens."""
        domain_logger = get_auth_logger()
        
        with RequestTracker(operation="cleanup_expired_refresh_tokens") as tracker:
            try:
                stmt = sa.delete(user_refresh_tokens_table).where(
                    user_refresh_tokens_table.c.expires_at < utcnow()
                )
                result = await self.session.execute(stmt)
                count = getattr(result, 'rowcount', 0)
                
                tracking_context = domain_logger.operation_start("cleanup_expired_refresh_tokens")

                
                domain_logger.operation_success(tracking_context,
                    tokens_removed=count
                )
                tracker.log_success(result_id=f"removed:{count}")
                
                return count
            except Exception as e:
                error_id = tracker.log_error(e, error_type=type(e).__name__)
                tracking_context = domain_logger.operation_start("cleanup_expired_refresh_tokens")

                domain_logger.operation_error(tracking_context,
                    error=str(e),
                    error_id=error_id
                )
                raise

    # JWT Blacklist Operations
    @trace_async
    async def blacklist_jwt(self, jti: str, user_id: UUID | None, expires_at: datetime, reason: str | None = None) -> bool:
        """Add JWT to blacklist."""
        try:
            stmt = sa.insert(jwt_blacklist_table).values(
                jti=jti,
                user_id=user_id,
                expires_at=expires_at,
                revoked_at=utcnow(),
                reason=reason
            )
            await self.session.execute(stmt)
            return True
        except IntegrityError:
            # JTI already blacklisted
            return True

    @trace_async
    async def is_jwt_blacklisted(self, jti: str) -> bool:
        """Check if JWT is blacklisted."""
        stmt = sa.select(sa.func.count()).select_from(jwt_blacklist_table).where(
            jwt_blacklist_table.c.jti == jti
        )
        result = await self.session.execute(stmt)
        return (result.scalar() or 0) > 0

    @trace_async
    async def cleanup_expired_blacklist(self) -> int:
        """Remove expired blacklisted tokens."""
        domain_logger = get_auth_logger()
        
        with RequestTracker(operation="cleanup_expired_blacklist") as tracker:
            try:
                stmt = sa.delete(jwt_blacklist_table).where(
                    jwt_blacklist_table.c.expires_at < utcnow()
                )
                result = await self.session.execute(stmt)
                count = getattr(result, 'rowcount', 0)
                
                tracking_context = domain_logger.operation_start("cleanup_expired_blacklist")

                
                domain_logger.operation_success(tracking_context,
                    tokens_removed=count
                )
                tracker.log_success(result_id=f"removed:{count}")
                
                return count
            except Exception as e:
                error_id = tracker.log_error(e, error_type=type(e).__name__)
                tracking_context = domain_logger.operation_start("cleanup_expired_blacklist")

                domain_logger.operation_error(tracking_context,
                    error=str(e),
                    error_id=error_id
                )
                raise

    # Password Reset Operations
    @trace_async
    async def create_password_reset_token(self, user_id: UUID, token_hash: str, expires_at: datetime) -> PasswordResetTokenOut:
        """Create password reset token."""
        stmt = sa.insert(password_reset_tokens_table).values(
            id=uuid4(),
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
            created_at=utcnow()
        ).returning(password_reset_tokens_table)

        result = await self.session.execute(stmt)
        row = result.fetchone()
        if row is None:
            raise ConflictError("Failed to create password reset token")
        return PasswordResetTokenOut.model_validate(row._asdict())

    @trace_async
    async def get_password_reset_token(self, token_hash: str) -> PasswordResetTokenOut | None:
        """Get valid password reset token."""
        logger.debug("Looking for password reset token", extra={
            "token_hash_preview": token_hash[:20] + "..."
        })

        stmt = sa.select(password_reset_tokens_table).where(
            sa.and_(
                password_reset_tokens_table.c.token_hash == token_hash,
                password_reset_tokens_table.c.used_at.is_(None),
                password_reset_tokens_table.c.expires_at > utcnow()
            )
        )
        result = await self.session.execute(stmt)
        row = result.fetchone()

        if row:
            logger.debug("Password reset token found and valid", extra={
                "token_id": str(row.id),
                "user_id": str(row.user_id),
                "expires_at": row.expires_at.isoformat()
            })
            return PasswordResetTokenOut.model_validate(row._asdict())
        else:
            logger.warning("Password reset token not found or invalid", extra={
                "token_hash_preview": token_hash[:20] + "..."
            })

            # Check if token exists but is expired or already used
            check_stmt = sa.select(password_reset_tokens_table).where(
                password_reset_tokens_table.c.token_hash == token_hash
            )
            check_result = await self.session.execute(check_stmt)
            check_row = check_result.fetchone()

            if check_row:
                logger.info("Token exists but is invalid", extra={
                    "token_id": str(check_row.id),
                    "user_id": str(check_row.user_id),
                    "expires_at": check_row.expires_at.isoformat(),
                    "used_at": check_row.used_at.isoformat() if check_row.used_at else None,
                    "is_expired": check_row.expires_at <= utcnow()
                })
            else:
                logger.warning("Token does not exist in database")

            return None

    @trace_async
    async def use_password_reset_token(self, token_hash: str) -> bool:
        """Mark password reset token as used."""
        stmt = (
            sa.update(password_reset_tokens_table)
            .where(password_reset_tokens_table.c.token_hash == token_hash)
            .values(used_at=utcnow())
        )
        result = await self.session.execute(stmt)
        return getattr(result, 'rowcount', 0) > 0

    # Email Verification Operations
    @trace_async
    async def create_email_verification_token(self, user_id: UUID, token_hash: str, email: str, expires_at: datetime) -> EmailVerificationTokenOut:
        """Create email verification token."""
        stmt = sa.insert(email_verification_tokens_table).values(
            id=uuid4(),
            user_id=user_id,
            token_hash=token_hash,
            email=email,
            expires_at=expires_at,
            created_at=utcnow()
        ).returning(email_verification_tokens_table)

        result = await self.session.execute(stmt)
        row = result.fetchone()
        if row is None:
            raise ConflictError("Failed to create email verification token")
        return EmailVerificationTokenOut.model_validate(row._asdict())

    @trace_async
    async def get_email_verification_token(self, token_hash: str) -> EmailVerificationTokenOut | None:
        """Get valid email verification token."""
        logger.debug("Looking for verification token", extra={
            "token_hash_preview": token_hash[:20] + "..."
        })

        stmt = sa.select(email_verification_tokens_table).where(
            sa.and_(
                email_verification_tokens_table.c.token_hash == token_hash,
                email_verification_tokens_table.c.verified_at.is_(None),
                email_verification_tokens_table.c.expires_at > utcnow()
            )
        )
        result = await self.session.execute(stmt)
        row = result.fetchone()

        if row:
            logger.debug("Verification token found and valid", extra={
                "token_id": str(row.id),
                "email": row.email,
                "expires_at": row.expires_at.isoformat()
            })
            return EmailVerificationTokenOut.model_validate(row._asdict())
        else:
            logger.warning("Verification token not found or invalid", extra={
                "token_hash_preview": token_hash[:20] + "..."
            })

            # Check if token exists but is expired or already used
            check_stmt = sa.select(email_verification_tokens_table).where(
                email_verification_tokens_table.c.token_hash == token_hash
            )
            check_result = await self.session.execute(check_stmt)
            check_row = check_result.fetchone()

            if check_row:
                logger.info("Token exists but is invalid", extra={
                    "token_id": str(check_row.id),
                    "email": check_row.email,
                    "expires_at": check_row.expires_at.isoformat(),
                    "verified_at": check_row.verified_at.isoformat() if check_row.verified_at else None,
                    "is_expired": check_row.expires_at <= utcnow()
                })
            else:
                logger.warning("Token does not exist in database")

            return None

    @trace_async
    async def verify_email_token(self, token_hash: str) -> bool:
        """Mark email verification token as used."""
        stmt = (
            sa.update(email_verification_tokens_table)
            .where(email_verification_tokens_table.c.token_hash == token_hash)
            .values(verified_at=utcnow())
        )
        result = await self.session.execute(stmt)
        return getattr(result, 'rowcount', 0) > 0

    # Session Operations
    @trace_async
    async def create_session(self, user_id: UUID, device_id: str | None, ip_address: str | None, user_agent: str | None) -> SessionOut:
        """Create new user session."""
        now = utcnow()
        stmt = sa.insert(user_sessions_table).values(
            id=uuid4(),
            user_id=user_id,
            device_id=device_id,
            ip_address=ip_address,
            user_agent=user_agent,
            started_at=now,
            last_activity_at=now
        ).returning(user_sessions_table)

        result = await self.session.execute(stmt)
        row = result.fetchone()
        if row is None:
            raise ConflictError("Failed to create session")
        return SessionOut.model_validate(row._asdict())

    @trace_async
    async def update_session_activity(self, session_id: UUID) -> bool:
        """Update session last activity."""
        stmt = (
            sa.update(user_sessions_table)
            .where(user_sessions_table.c.id == session_id)
            .values(last_activity_at=utcnow())
        )
        result = await self.session.execute(stmt)
        return getattr(result, 'rowcount', 0) > 0

    @trace_async
    async def end_session(self, session_id: UUID) -> bool:
        """End user session."""
        stmt = (
            sa.update(user_sessions_table)
            .where(user_sessions_table.c.id == session_id)
            .values(ended_at=utcnow())
        )
        result = await self.session.execute(stmt)
        return getattr(result, 'rowcount', 0) > 0

    @trace_async
    async def get_active_sessions(self, user_id: UUID) -> list[SessionOut]:
        """Get active sessions for user."""
        stmt = sa.select(user_sessions_table).where(
            sa.and_(
                user_sessions_table.c.user_id == user_id,
                user_sessions_table.c.ended_at.is_(None)
            )
        ).order_by(user_sessions_table.c.last_activity_at.desc())

        result = await self.session.execute(stmt)
        return [SessionOut.model_validate(row._asdict()) for row in result.fetchall()]

    # Social Account Operations
    @trace_async
    async def find_user_by_social_account(self, provider: str, provider_user_id: str) -> UUID | None:
        """Find user by social account provider and ID."""
        stmt = sa.select(social_accounts_table.c.user_id).where(
            sa.and_(
                social_accounts_table.c.provider == provider,
                social_accounts_table.c.provider_user_id == provider_user_id
            )
        )
        result = await self.session.execute(stmt)
        row = result.fetchone()
        return row.user_id if row else None

    @trace_async
    async def find_user_by_email(self, email: str) -> UUID | None:
        """Find user by email."""
        from ...domain.users.schemas import users_table

        stmt = sa.select(users_table.c.id).where(users_table.c.email == email)
        result = await self.session.execute(stmt)
        row = result.fetchone()
        return row.id if row else None

    @trace_async
    async def create_user_with_social_account(
        self,
        email: str | None,
        name: str | None,
        provider: str,
        provider_user_id: str,
        avatar_url: str | None = None,
        locale: str = "en-US"
    ) -> UUID:
        """Create user with social account."""
        from ...domain.users.schemas import users_table
        from ...utils.i18n import t

        now = utcnow()
        user_id = uuid4()

        # Validate and sanitize inputs
        if name and len(name) > 255:
            name = name[:255]
        if email and len(email) > 255:
            email = email[:255]

        try:
            # Create user (only with columns that exist in users table)
            user_stmt = sa.insert(users_table).values(
                id=user_id,
                email=email,
                email_verified=True,  # Social login emails are pre-verified
                auth_provider=provider,
                avatar_url=avatar_url,
                locale=locale,
                created_at=now,
                updated_at=now
            )
            await self.session.execute(user_stmt)

            # Create social account
            social_stmt = sa.insert(social_accounts_table).values(
                id=uuid4(),
                user_id=user_id,
                provider=provider,
                provider_user_id=provider_user_id,
                email=email,
                name=name,
                avatar_url=avatar_url,
                created_at=now,
                updated_at=now
            )
            await self.session.execute(social_stmt)

            # Don't commit here - let UoW handle it
            logger.info("Created user with social account", extra={
                "user_id": str(user_id),
                "provider": provider,
                "has_email": email is not None
            })

            return user_id

        except IntegrityError as e:
            # Don't rollback here - let UoW handle it
            logger.error("Failed to create user with social account", extra={
                "provider": provider,
                "error": str(e)
            })
            raise ConflictError(t("auth.error.user_creation_failed", locale=locale))

    @trace_async
    async def link_social_account(
        self,
        user_id: UUID,
        provider: str,
        provider_user_id: str,
        email: str | None,
        name: str | None,
        avatar_url: str | None = None
    ) -> SocialAccountOut:
        """Link social account to existing user."""
        now = utcnow()
        social_id = uuid4()

        try:
            stmt = sa.insert(social_accounts_table).values(
                id=social_id,
                user_id=user_id,
                provider=provider,
                provider_user_id=provider_user_id,
                email=email,
                name=name,
                avatar_url=avatar_url,
                created_at=now,
                updated_at=now
            ).returning(social_accounts_table)

            result = await self.session.execute(stmt)
            row = result.fetchone()
            if row is None:
                raise ConflictError("Failed to link social account")

            logger.info("Linked social account to user", extra={
                "user_id": str(user_id),
                "provider": provider,
                "social_account_id": str(social_id)
            })

            return SocialAccountOut.model_validate(row._asdict())

        except IntegrityError:
            # Account already linked
            raise ConflictError("Social account already linked to user")

    @trace_async
    async def get_user_social_accounts(self, user_id: UUID) -> list[SocialAccountOut]:
        """Get all social accounts for user."""
        stmt = sa.select(social_accounts_table).where(
            social_accounts_table.c.user_id == user_id
        ).order_by(social_accounts_table.c.created_at.desc())

        result = await self.session.execute(stmt)
        return [SocialAccountOut.model_validate(row._asdict()) for row in result.fetchall()]

    @trace_async
    async def unlink_social_account(self, user_id: UUID, provider: str) -> bool:
        """Unlink social account from user."""
        stmt = sa.delete(social_accounts_table).where(
            sa.and_(
                social_accounts_table.c.user_id == user_id,
                social_accounts_table.c.provider == provider
            )
        )
        result = await self.session.execute(stmt)

        success = getattr(result, 'rowcount', 0) > 0
        if success:
            logger.info("Unlinked social account", extra={
                "user_id": str(user_id),
                "provider": provider
            })

        return success
