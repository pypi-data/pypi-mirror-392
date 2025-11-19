"""Authentication service for user credentials and token management.

This service handles all authentication operations including user registration,
login, token management, password reset, and email verification. It follows
the domain-driven design pattern and integrates with the repository layer
for data persistence and external services for notifications.

Key features:
- Secure password hashing with bcrypt
- JWT token generation and validation
- Account lockout protection
- Password reset workflows
- Email verification
- Session management
"""

import hashlib
import secrets
import traceback
from datetime import timedelta
from typing import Any
from uuid import UUID

import bcrypt
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from ...db.uow import async_uow_factory
from ...utils.clock import utcnow
from ...utils.config import auth_config
from ...utils.request_tracking import RequestTracker
from ...utils.domain_logger import get_auth_logger
from ...utils.errors import BadRequest, Conflict, Unauthorized
from ...utils.i18n import t
from ...utils.jwt import generate_access_token
from ...utils.jwt import validate_token as jwt_validate_token
from ...utils.logging import get_safe_logger
from ...utils.tracing import trace_async
from ..users.service import UsersService
from .repository import AuthRepository
from .schemas import (
    AuthResponse,
    AuthTokenPair,
    ChangePasswordRequest,
    LoginRequest,
    PasswordResetConfirm,
    PasswordResetRequest,
    RefreshTokenRequest,
    RegisterRequest,
    SocialAuthResponse,
    SocialLoginRequest,
    TokenValidationResult,
    UserProfile,
)
from .social_validators import AppleTokenValidator, GoogleTokenValidator

logger = get_safe_logger(__name__)

class AuthService:
    """Service for authentication operations."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession], email_service: Any | None = None) -> None:
        self.session_factory = session_factory
        self.email_service = email_service
        self.users_service = UsersService(session_factory)

    @trace_async
    async def login(self, request: LoginRequest, locale: str = "en-US") -> AuthResponse:
        """Authenticate user and return tokens."""
        domain_logger = get_auth_logger()
        
        with RequestTracker(operation="login", email=request.email.split("@")[0]) as tracker:
            try:
                logger.info("Login attempt started", extra={"locale": locale})

                # Use session factory directly for auth operations
                logger.debug("Creating auth session")
                async with self.session_factory() as session:
                    # Disable RLS for auth operations
                    logger.debug("Disabling RLS for auth session")
                    from sqlalchemy import text
                    await session.execute(text("RESET ROLE"))
                    await session.execute(text("SET row_security = off"))

                    repository = AuthRepository(session)

                    # Get user credentials
                    logger.debug("Fetching user credentials by email")
                credentials = await repository.get_user_credentials_by_email(request.email)
                if not credentials:
                    logger.warning("Login failed - user not found", extra={
                        "email_domain": request.email.split("@")[1] if "@" in request.email else "invalid"
                    })
                    raise Unauthorized(t("auth.error.invalid_credentials", locale=locale))

                logger.debug("User credentials found", extra={
                    "user_id": str(credentials.user_id),
                    "email_verified": credentials.email_verified,
                    "failed_attempts": credentials.failed_attempts
                })

                # Check if account is locked
                if credentials.locked_until and credentials.locked_until > utcnow():
                    logger.warning("Login failed - account locked", extra={
                        "user_id": str(credentials.user_id),
                        "locked_until": credentials.locked_until.isoformat()
                    })
                    raise Unauthorized(t("auth.error.account_locked", locale=locale))

                # Verify password
                logger.debug("Verifying password")
                if not self._verify_password(request.password, credentials.password_hash, credentials.password_salt):
                    # Increment failed attempts
                    lockout_duration = None
                    if credentials.failed_attempts + 1 >= auth_config.max_login_attempts:
                        lockout_duration = timedelta(minutes=auth_config.lockout_duration_minutes)

                    await repository.increment_failed_attempts(credentials.user_id, lockout_duration)
                    logger.warning("Login failed - invalid password", extra={
                        "user_id": str(credentials.user_id),
                        "failed_attempts": credentials.failed_attempts + 1,
                        "will_lock": lockout_duration is not None
                    })
                    raise Unauthorized(t("auth.error.invalid_credentials", locale=locale))

                logger.debug("Password verified successfully")

                # Reset failed attempts on successful login
                if credentials.failed_attempts > 0:
                    logger.debug("Resetting failed login attempts", extra={
                        "user_id": str(credentials.user_id),
                        "previous_failed_attempts": credentials.failed_attempts
                    })
                    await repository.reset_failed_attempts(credentials.user_id)

                # Get user profile using users repository in same session
                logger.debug("Fetching user profile")
                from ..users.repository import UsersRepository
                users_repository = UsersRepository(session)
                user = await users_repository.get_user(credentials.user_id)
                if not user:
                    logger.error("User not found after credential validation", extra={
                        "user_id": str(credentials.user_id),
                        "step": "get_user_profile"
                    })
                    raise Unauthorized(t("auth.error.invalid_credentials", locale=locale))

                logger.debug("User profile retrieved", extra={
                    "user_id": str(user.id),
                    "has_gender": bool(user.gender),
                    "has_country": bool(user.country)
                })

                # Update last login timestamp in same session
                logger.debug("Updating last login timestamp")
                from datetime import UTC, datetime
                await users_repository.update_last_login(credentials.user_id, datetime.now(UTC))

                # Create session
                logger.debug("Creating user session", extra={
                    "user_id": str(credentials.user_id),
                    "has_device_id": bool(request.device_id)
                })
                session_obj = await repository.create_session(
                    user_id=credentials.user_id,
                    device_id=request.device_id,
                    ip_address=None,
                    user_agent=None
                )

                logger.debug("Session created", extra={
                    "session_id": str(session_obj.id),
                    "user_id": str(credentials.user_id)
                })

                # Commit the transaction
                logger.debug("Committing auth transaction")
                await session.commit()
                logger.debug("Auth transaction committed successfully")

                # Generate tokens after user is fully committed
                logger.debug("Generating token pair", extra={"user_id": str(credentials.user_id)})
                tokens = await self._generate_token_pair(credentials.user_id, user.email, request.device_id, locale)
                logger.debug("Token pair generated successfully")

                logger.info("Login successful", extra={
                    "user_id": str(credentials.user_id),
                    "session_id": str(session_obj.id),
                    "email_verified": credentials.email_verified
                })

                # Log successful login with domain logger
                domain_logger.business_event(
                    "user_login_success",
                    entity_id=str(credentials.user_id),
                    email_verified=credentials.email_verified,
                    session_id=str(session_obj.id)
                )

                tracker.log_success(result_id=str(credentials.user_id))

                return AuthResponse(
                    user=UserProfile(
                        id=user.id,
                        email=user.email,
                        email_verified=credentials.email_verified,
                        gender=user.gender,
                        country=user.country,
                        created_at=user.created_at,
                        last_login_at=user.last_login_at
                    ),
                    tokens=tokens,
                    session_id=session_obj.id
                )
            except (Unauthorized, Conflict) as e:
                logger.warning("Login failed with expected error", extra={
                    "error_type": type(e).__name__,
                    "error_message": str(e)
                })
                
                # Log failed login attempt
                domain_logger.business_event(
                    "user_login_failed",
                    error_type=type(e).__name__,
                    reason="authentication_failed"
                )
                
                error_id = tracker.log_error(e, error_type=type(e).__name__)
                raise e
            except Exception as e:
                logger.error("Login error - unexpected exception", extra={
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "has_email": bool(request.email),
                    "locale": locale
                }, exc_info=True)
                
                error_id = tracker.log_error(e, error_type=type(e).__name__, locale=locale)
                raise Unauthorized(t("auth.error.authentication_failed", locale=locale))

    @trace_async
    async def register(self, request: RegisterRequest, locale: str = "en-US") -> AuthResponse:
        """Register new user and return tokens."""
        domain_logger = get_auth_logger()
        
        with RequestTracker(operation="register", email=request.email.split("@")[0]) as tracker:
            logger.debug("Registration attempt", extra={"has_email": bool(request.email)})

            user = None  # Initialize to avoid UnboundLocalError in exception handler
            try:
                # Use isolated auth engine to avoid RLS interference
                from ...db.engine import get_auth_session_factory
                auth_session_factory = get_auth_session_factory()

                async with auth_session_factory() as auth_session:
                    # Disable RLS only in this isolated session
                    from sqlalchemy import text
                    await auth_session.execute(text("RESET ROLE"))
                    await auth_session.execute(text("SET row_security = off"))

                    # Check if user already exists
                    auth_repository = AuthRepository(auth_session)
                    existing = await auth_repository.get_user_credentials_by_email(request.email)
                if existing:
                    logger.warning("Registration failed - email exists")
                    raise Conflict(t("auth.error.user_exists", locale=locale))

                # Validate invitation code if provided
                invitation_code_data = None
                if request.invitation_code:
                    from ..invitations.repository import InvitationsRepository
                    invitations_repo = InvitationsRepository(auth_session)
                    invitation_code_data = await invitations_repo.validate_invitation_code(request.invitation_code)

                # Create user directly in this transaction
                from ..users.repository import UsersRepository
                users_repository = UsersRepository(auth_session)

                # Check if user exists by email
                existing_user = await users_repository.get_user_by_email(request.email)
                if existing_user:
                    raise Conflict(t("auth.error.user_exists", locale=locale))

                # Create user
                user = await users_repository.create_user(
                    email=request.email,
                    gender=request.gender,
                    country=request.country,
                    bio="",
                    invitation_code_used=request.invitation_code
                )

                # Hash password and create credentials in same transaction
                password_salt = secrets.token_hex(16)
                password_hash = self._hash_password(request.password, password_salt)

                await auth_repository.create_user_credentials(
                    user_id=user.id,
                    password_hash=password_hash,
                    password_salt=password_salt,
                    locale=locale
                )

                # Use invitation code if provided
                if request.invitation_code and invitation_code_data:
                    from ..invitations.repository import InvitationsRepository
                    invitations_repo = InvitationsRepository(auth_session)
                    await invitations_repo.use_invitation_code(
                        code=request.invitation_code,
                        user_id=user.id
                    )

                # Create trial subscription for new user
                from ..subscription.service import SubscriptionService
                subscription_service = SubscriptionService(auth_session_factory)
                try:
                    await subscription_service.create_trial_subscription(user.id)
                    logger.debug("Trial subscription created", extra={"user_id": str(user.id)})
                except Exception as e:
                    logger.warning("Failed to create trial subscription", extra={
                        "user_id": str(user.id),
                        "error": str(e)
                    })
                    # Don't fail registration if subscription creation fails

                # Update last_login_at in same transaction
                from datetime import UTC, datetime
                await users_repository.update_last_login(user.id, datetime.now(UTC))

                # Generate email verification token
                verification_token = secrets.token_urlsafe(32)
                token_hash = self._hash_token(verification_token)
                expires_at = utcnow() + timedelta(hours=24)

                logger.debug("Creating email verification token", extra={
                    "user_id": str(user.id),
                    "expires_at": expires_at.isoformat()
                })

                # Store verification token
                verification_token_obj = await auth_repository.create_email_verification_token(
                    user_id=user.id,
                    token_hash=token_hash,
                    email=user.email,
                    expires_at=expires_at
                )

                logger.debug("Email verification token created successfully", extra={
                    "token_id": str(verification_token_obj.id),
                    "user_id": str(user.id)
                })

                # Enqueue email via outbox
                from ...outbox.dispatcher import enqueue_outbox
                await enqueue_outbox(
                    session=auth_session,
                    topic="email.verification.requested",
                    payload={
                        "email": user.email,
                        "token": verification_token,
                        "user_name": user.email.split("@")[0],
                        "locale": locale
                    }
                )

                # Commit the isolated auth transaction
                await auth_session.commit()

                # Generate tokens after user is fully committed
                tokens = await self._generate_token_pair(user.id, user.email, locale=locale)

                logger.info("Registration successful", extra={"user_id": str(user.id)})

                # Log successful registration with domain logger
                domain_logger.business_event(
                    "user_registration_success",
                    entity_id=str(user.id),
                    email_verified=False,
                    has_invitation_code=bool(request.invitation_code)
                )

                tracker.log_success(result_id=str(user.id))

                return AuthResponse(
                    user=UserProfile(
                        id=user.id,
                        email=user.email,
                        email_verified=False,
                        gender=user.gender,
                        country=user.country,
                        created_at=user.created_at
                    ),
                    tokens=tokens
                )
            except (BadRequest, Conflict) as e:
                logger.warning("Registration validation error", extra={
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "email": request.email,
                    "has_invitation_code": bool(request.invitation_code)
                })
                
                # Log failed registration attempt
                domain_logger.business_event(
                    "user_registration_failed",
                    error_type=type(e).__name__,
                    reason="validation_error",
                    has_invitation_code=bool(request.invitation_code)
                )
                
                error_id = tracker.log_error(e, error_type=type(e).__name__)
                raise e
            except Exception as e:
                from ...utils.logging import safe_log_error
                logger.error("Registration unexpected error", extra={
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "email": request.email,
                "user_id": str(user.id) if user else None,
                "has_invitation_code": bool(request.invitation_code),
                "traceback": traceback.format_exc()
            })
            
            error_id = tracker.log_error(e, error_type=type(e).__name__, user_id=str(user.id) if user else None)
            safe_log_error(logger, "Registration error", e,
                user_id=str(user.id) if user else None
            )
            raise BadRequest(t("auth.error.registration_failed", locale=locale))

    @trace_async
    async def refresh_token(self, request: RefreshTokenRequest) -> AuthTokenPair:
        """Refresh access token using refresh token."""
        domain_logger = get_auth_logger()
        
        with RequestTracker(operation="refresh_token", token_hash=self._hash_token(request.refresh_token)[:8]) as tracker:
            try:
                logger.debug("Token refresh attempt")

                # Hash the refresh token to find it
                token_hash = self._hash_token(request.refresh_token)

                # Use isolated auth engine to avoid RLS interference
                from ...db.engine import get_auth_session_factory
                auth_session_factory = get_auth_session_factory()

                async with auth_session_factory() as auth_session:
                    # Disable RLS only in this isolated session
                    from sqlalchemy import text
                    await auth_session.execute(text("RESET ROLE"))
                    await auth_session.execute(text("SET row_security = off"))

                    repository = AuthRepository(auth_session)

                    # Get refresh token from database
                    refresh_token = await repository.get_refresh_token(token_hash)
                    if not refresh_token:
                        logger.warning("Token refresh failed - invalid token")
                        raise Unauthorized(t("auth.error.invalid_token"))

                    # Get user email using users repository in same session
                    from ..users.repository import UsersRepository
                    users_repository = UsersRepository(auth_session)
                    user = await users_repository.get_user(refresh_token.user_id)
                    if not user:
                        logger.warning("Token refresh failed - user not found", extra={"user_id": str(refresh_token.user_id)})
                        raise Unauthorized(t("auth.error.invalid_token"))

                    # Commit the isolated auth transaction
                    await auth_session.commit()

                # Generate new token pair
                tokens = await self._generate_token_pair(refresh_token.user_id, user.email, refresh_token.device_id)

                logger.debug("Token refreshed successfully", extra={"user_id": str(refresh_token.user_id)})
                
                domain_logger.business_event(
                    "token_refresh_success",
                    entity_id=str(refresh_token.user_id),
                    device_id=refresh_token.device_id
                )
                
                tracker.log_success(result_id=str(refresh_token.user_id))
                return tokens
            except Unauthorized as e:
                domain_logger.business_event(
                    "token_refresh_failed",
                    error_type=type(e).__name__,
                    reason="invalid_token"
                )
                error_id = tracker.log_error(e, error_type=type(e).__name__)
                raise e
            except Exception as e:
                logger.error("Token refresh error", extra={"error": str(e)})
                error_id = tracker.log_error(e, error_type=type(e).__name__)
                raise Unauthorized(t("auth.error.token_refresh_failed"))

    @trace_async
    async def logout(self, user_id: UUID, device_id: str | None = None) -> bool:
        """Logout user and revoke tokens."""
        domain_logger = get_auth_logger()
        
        with RequestTracker(operation="logout", user_id=str(user_id)) as tracker:
            try:
                logger.debug("User logout", extra={"user_id": str(user_id)})

                # Use isolated auth engine to avoid RLS interference
                from ...db.engine import get_auth_session_factory
                auth_session_factory = get_auth_session_factory()

                async with auth_session_factory() as auth_session:
                    # Disable RLS only in this isolated session
                    from sqlalchemy import text
                    await auth_session.execute(text("RESET ROLE"))
                    await auth_session.execute(text("SET row_security = off"))

                    repository = AuthRepository(auth_session)

                    # Revoke refresh tokens
                    revoked_count = await repository.revoke_user_refresh_tokens(user_id, device_id)

                    # Commit the isolated auth transaction
                    await auth_session.commit()

                    logger.debug("User logged out", extra={"user_id": str(user_id), "revoked_tokens": revoked_count})
                    
                    domain_logger.business_event(
                        "user_logout_success",
                        entity_id=str(user_id),
                        device_id=device_id,
                        revoked_tokens=revoked_count
                    )
                    
                    tracker.log_success(result_id=str(user_id))
                    return True
            except Exception as e:
                logger.error("Logout error", extra={"error": str(e), "user_id": str(user_id)})
                
                domain_logger.business_event(
                    "user_logout_failed",
                    entity_id=str(user_id),
                    error_type=type(e).__name__
                )
                
                error_id = tracker.log_error(e, error_type=type(e).__name__, user_id=str(user_id))
                return False

    @trace_async
    async def validate_token(self, token: str) -> TokenValidationResult:
        """Validate JWT access token."""
        try:
            claims = jwt_validate_token(token)

            async with async_uow_factory(self.session_factory)() as uow:
                repository = AuthRepository(uow.session)

                # Check if token is blacklisted
                is_blacklisted = await repository.is_jwt_blacklisted(claims.jti)
                if is_blacklisted:
                    return TokenValidationResult(
                        valid=False,
                        error="Token has been revoked"
                    )

            return TokenValidationResult(
                valid=True,
                user_id=claims.sub,
                claims=claims
            )
        except Exception as e:
            logger.warning("Token validation failed", extra={"error": str(e)})
            return TokenValidationResult(
                valid=False,
                error=str(e)
            )

    @trace_async
    async def request_password_reset(self, request: PasswordResetRequest, locale: str = "en-US") -> bool:
        """Request password reset token."""
        domain_logger = get_auth_logger()
        
        with RequestTracker(operation="request_password_reset", email=request.email.split("@")[0]) as tracker:
            try:
                logger.debug("Password reset requested", extra={"has_email": bool(request.email)})

                async with async_uow_factory(self.session_factory)() as uow:
                    repository = AuthRepository(uow.session)

                    # Get user credentials
                    credentials = await repository.get_user_credentials_by_email(request.email)
                    if not credentials:
                        # Don't reveal if email exists
                        logger.debug("Password reset requested for non-existent email")
                        domain_logger.business_event(
                            "password_reset_requested_nonexistent",
                            email_domain=request.email.split("@")[1] if "@" in request.email else "invalid"
                        )
                        tracker.log_success(result_id="nonexistent")
                        return True

                    # Get user info for email
                    from ..users.repository import UsersRepository
                    users_repo = UsersRepository(uow.session)
                    user = await users_repo.get_user(credentials.user_id)
                    if not user:
                        logger.debug("Password reset requested for non-existent user")
                        tracker.log_success(result_id="nonexistent")
                        return True

                    # Generate reset token (6 digits in XXX-XXX format)
                    import random
                    reset_code = f"{random.randint(100, 999)}-{random.randint(100, 999)}"
                    token_hash = self._hash_token(reset_code)
                    expires_at = utcnow() + timedelta(minutes=auth_config.password_reset_expire_minutes)

                    # Store reset token
                    await repository.create_password_reset_token(
                        user_id=credentials.user_id,
                        token_hash=token_hash,
                        expires_at=expires_at
                    )

                    # Enqueue email via outbox
                    from ...outbox.dispatcher import enqueue_outbox
                    await enqueue_outbox(
                        session=uow.session,
                        topic="email.password_reset.requested",
                        payload={
                            "email": user.email,
                            "token": reset_code,
                            "user_name": user.email.split("@")[0],
                            "locale": locale
                        }
                    )

                    logger.debug("Password reset token created", extra={"user_id": str(credentials.user_id)})
                    
                    domain_logger.business_event(
                        "password_reset_requested",
                        entity_id=str(credentials.user_id),
                        locale=locale
                    )
                    
                    tracker.log_success(result_id=str(credentials.user_id))
                    return True
            except Exception as e:
                logger.error("Password reset request error", extra={"error": str(e)})
                
                domain_logger.business_event(
                    "password_reset_request_failed",
                    error_type=type(e).__name__
                )
                
                error_id = tracker.log_error(e, error_type=type(e).__name__)
                return False

    @trace_async
    async def reset_password(self, request: PasswordResetConfirm, locale: str = "en-US") -> bool:
        """Reset password using reset token."""
        domain_logger = get_auth_logger()
        
        with RequestTracker(operation="reset_password", token=request.token[:8]) as tracker:
            try:
                logger.debug("Password reset confirmation", extra={
                    "token_length": len(request.token),
                    "has_token": bool(request.token)
                })

                # Hash token to find it
                token_hash = self._hash_token(request.token)
                logger.debug("Token hash generated for reset", extra={
                    "hash_length": len(token_hash)
                })

                # Use isolated auth engine to avoid RLS interference
                from ...db.engine import get_auth_session_factory
                auth_session_factory = get_auth_session_factory()

                async with auth_session_factory() as auth_session:
                    # Disable RLS only in this isolated session
                    from sqlalchemy import text
                    await auth_session.execute(text("RESET ROLE"))
                    await auth_session.execute(text("SET row_security = off"))

                    repository = AuthRepository(auth_session)

                    # Get reset token
                    reset_token = await repository.get_password_reset_token(token_hash)
                    if not reset_token:
                        logger.warning("Password reset failed - invalid token", extra={
                            "token": request.token,
                            "token_hash_preview": token_hash[:20] + "..."
                        })
                        raise BadRequest(t("auth.error.invalid_reset_token", locale=locale))

                    logger.debug("Reset token found and valid", extra={
                        "token_id": str(reset_token.id),
                        "user_id": str(reset_token.user_id),
                        "expires_at": reset_token.expires_at.isoformat()
                    })

                    # Hash new password
                    password_salt = secrets.token_hex(16)
                    password_hash = self._hash_password(request.new_password, password_salt)

                    # Update password
                    success: bool = await repository.update_password(
                        user_id=reset_token.user_id,
                        password_hash=password_hash,
                        password_salt=password_salt
                    )

                    if success:
                        # Mark token as used
                        await repository.use_password_reset_token(token_hash)

                        # Revoke all refresh tokens for security
                        await repository.revoke_user_refresh_tokens(reset_token.user_id)

                        logger.info("Password reset successfully", extra={"user_id": str(reset_token.user_id)})

                    # Commit the isolated auth transaction
                    await auth_session.commit()

                    domain_logger.business_event(
                        "password_reset_success",
                        entity_id=str(reset_token.user_id),
                        locale=locale
                    )
                    
                    tracker.log_success(result_id=str(reset_token.user_id))
                    return success
            except BadRequest as e:
                domain_logger.business_event(
                    "password_reset_failed",
                    error_type=type(e).__name__,
                    reason="invalid_token"
                )
                error_id = tracker.log_error(e, error_type=type(e).__name__)
                raise e
            except Exception as e:
                logger.error("Password reset error", extra={"error": str(e)})
                error_id = tracker.log_error(e, error_type=type(e).__name__)
                raise BadRequest(t("auth.error.password_reset_failed", locale=locale))

    @trace_async
    async def change_password(self, user_id: UUID, request: ChangePasswordRequest, locale: str = "en-US") -> bool:
        """Change password for authenticated user."""
        domain_logger = get_auth_logger()
        
        with RequestTracker(operation="change_password", user_id=str(user_id)) as tracker:
            try:
                logger.debug("Password change attempt", extra={"user_id": str(user_id)})

                async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                    repository = AuthRepository(uow.session)

                    # Get current credentials
                    credentials = await repository.get_user_credentials(user_id)
                    if not credentials:
                        logger.warning("Password change failed - user not found", extra={"user_id": str(user_id)})
                        raise BadRequest(t("auth.error.user_not_found", locale=locale))

                    # Verify current password
                    if not self._verify_password(request.current_password, credentials.password_hash, credentials.password_salt):
                        logger.warning("Password change failed - invalid current password", extra={"user_id": str(user_id)})
                        raise BadRequest(t("auth.error.invalid_current_password", locale=locale))

                    # Hash new password
                    password_salt = secrets.token_hex(16)
                    password_hash = self._hash_password(request.new_password, password_salt)

                    # Update password
                    success = await repository.update_password(
                        user_id=user_id,
                        password_hash=password_hash,
                        password_salt=password_salt
                    )

                    if success:
                        logger.info("Password changed successfully", extra={"user_id": str(user_id)})
                        
                        domain_logger.business_event(
                            "password_change_success",
                            entity_id=str(user_id),
                            locale=locale
                        )
                        
                        tracker.log_success(result_id=str(user_id))

                    return success
            except BadRequest as e:
                domain_logger.business_event(
                    "password_change_failed",
                    entity_id=str(user_id),
                    error_type=type(e).__name__,
                    reason="validation_error"
                )
                error_id = tracker.log_error(e, error_type=type(e).__name__, user_id=str(user_id))
                raise e
            except Exception as e:
                logger.error("Password change error", extra={"user_id": str(user_id), "error": str(e)})
                error_id = tracker.log_error(e, error_type=type(e).__name__, user_id=str(user_id))
                raise BadRequest(t("auth.error.password_change_failed", locale=locale))

    @trace_async
    async def verify_email(self, token: str) -> bool:
        """Verify email using verification token."""
        domain_logger = get_auth_logger()
        
        with RequestTracker(operation="verify_email", token=token[:8]) as tracker:
            try:
                logger.debug("Email verification attempt")

                # Hash token to find it
                token_hash = self._hash_token(token)
                logger.debug("Token hash generated", extra={
                    "token_length": len(token),
                    "hash_length": len(token_hash)
                })

                async with async_uow_factory(self.session_factory)() as uow:
                    repository = AuthRepository(uow.session)

                    # Get verification token
                    verification_token = await repository.get_email_verification_token(token_hash)

                    if not verification_token:
                        logger.warning("Email verification failed - token not found or invalid", extra={
                            "token_hash_preview": token_hash[:20] + "..."
                        })
                        raise BadRequest(t("auth.error.invalid_verification_token"))

                    logger.debug("Verification token found", extra={
                        "token_id": str(verification_token.id),
                        "user_id": str(verification_token.user_id),
                        "email": verification_token.email,
                        "expires_at": verification_token.expires_at.isoformat()
                    })

                    # Mark email as verified
                    await repository.verify_email(verification_token.user_id)
                    logger.debug("User email marked as verified", extra={
                        "user_id": str(verification_token.user_id)
                    })

                    # Mark token as used
                    await repository.verify_email_token(token_hash)
                    logger.debug("Verification token marked as used", extra={
                        "token_id": str(verification_token.id)
                    })

                    logger.info("Email verified successfully", extra={"user_id": str(verification_token.user_id)})
                    
                    domain_logger.business_event(
                        "email_verification_success",
                        entity_id=str(verification_token.user_id),
                        email=verification_token.email
                    )
                    
                    tracker.log_success(result_id=str(verification_token.user_id))
                    return True
            except BadRequest as e:
                logger.warning("Email verification failed with BadRequest", extra={"error": str(e)})
                
                domain_logger.business_event(
                    "email_verification_failed",
                    error_type=type(e).__name__,
                    reason="invalid_token"
                )
                
                error_id = tracker.log_error(e, error_type=type(e).__name__)
                raise e
            except Exception as e:
                logger.error("Email verification error", extra={
                    "error": str(e),
                    "error_type": type(e).__name__
                }, exc_info=True)
                error_id = tracker.log_error(e, error_type=type(e).__name__)
                raise BadRequest(t("auth.error.email_verification_failed"))

    @trace_async
    async def resend_email_verification(self, user_id: UUID, locale: str = "en-US") -> bool:
        """Resend email verification for user."""
        domain_logger = get_auth_logger()
        
        with RequestTracker(operation="resend_email_verification", user_id=str(user_id)) as tracker:
            try:
                logger.debug("Resend email verification", extra={"user_id": str(user_id)})

                async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                    repository = AuthRepository(uow.session)

                    # Get user credentials to check if already verified
                    credentials = await repository.get_user_credentials(user_id)
                    if not credentials:
                        raise BadRequest(t("auth.error.user_not_found", locale=locale))

                    if credentials.email_verified:
                        raise BadRequest(t("auth.error.email_already_verified", locale=locale))

                    # Get user email
                    from ..users.repository import UsersRepository
                    users_repo = UsersRepository(uow.session)
                    user = await users_repo.get_user(user_id)
                    if not user:
                        raise BadRequest(t("auth.error.user_not_found", locale=locale))

                    # Generate new verification token
                    verification_token = secrets.token_urlsafe(32)
                    token_hash = self._hash_token(verification_token)
                    expires_at = utcnow() + timedelta(hours=24)

                    # Store verification token
                    await repository.create_email_verification_token(
                        user_id=user_id,
                        token_hash=token_hash,
                        email=user.email,
                        expires_at=expires_at
                    )

                    # Enqueue email via outbox
                    from ...outbox.dispatcher import enqueue_outbox
                    await enqueue_outbox(
                        session=uow.session,
                        topic="email.verification.requested",
                        payload={
                            "email": user.email,
                            "token": verification_token,
                            "user_name": user.email.split("@")[0],
                            "locale": locale
                        }
                    )

                    logger.debug("Email verification token created", extra={"user_id": str(user_id)})
                    
                    domain_logger.business_event(
                        "email_verification_resent",
                        entity_id=str(user_id),
                        email=user.email,
                        locale=locale
                    )
                    
                    tracker.log_success(result_id=str(user_id))
                    return True

            except BadRequest as e:
                domain_logger.business_event(
                    "email_verification_resend_failed",
                    entity_id=str(user_id),
                    error_type=type(e).__name__,
                    reason="validation_error"
                )
                error_id = tracker.log_error(e, error_type=type(e).__name__, user_id=str(user_id))
                raise e
            except Exception as e:
                logger.error("Resend email verification error", extra={"user_id": str(user_id), "error": str(e)})
                error_id = tracker.log_error(e, error_type=type(e).__name__, user_id=str(user_id))
                raise BadRequest(t("auth.error.verification_resend_failed", locale=locale))

    @trace_async
    async def cleanup_expired_tokens(self) -> dict[str, int]:
        """Clean up expired tokens and sessions."""
        domain_logger = get_auth_logger()
        
        with RequestTracker(operation="cleanup_expired_tokens") as tracker:
            try:
                logger.info("Cleaning up expired tokens")

                async with async_uow_factory(self.session_factory)() as uow:
                    repository = AuthRepository(uow.session)

                    refresh_count = await repository.cleanup_expired_refresh_tokens()
                    blacklist_count = await repository.cleanup_expired_blacklist()

                    logger.info("Token cleanup completed", extra={
                        "refresh_tokens_removed": refresh_count,
                        "blacklist_entries_removed": blacklist_count
                    })
                    
                    domain_logger.business_event(
                        "token_cleanup_success",
                        refresh_tokens_removed=refresh_count,
                        blacklist_entries_removed=blacklist_count
                    )
                    
                    tracker.log_success(result_id=f"refresh:{refresh_count},blacklist:{blacklist_count}")

                    return {
                        "refresh_tokens_removed": refresh_count,
                        "blacklist_entries_removed": blacklist_count
                    }
            except Exception as e:
                logger.error("Token cleanup error", extra={"error": str(e)})
                
                domain_logger.business_event(
                    "token_cleanup_failed",
                    error_type=type(e).__name__
                )
                
                error_id = tracker.log_error(e, error_type=type(e).__name__)
                return {"refresh_tokens_removed": 0, "blacklist_entries_removed": 0}

    # Private helper methods
    def _hash_password(self, password: str, salt: str) -> str:
        """Hash password with bcrypt and additional salt."""
        # Combine password with salt
        salted_password = f"{password}{salt}".encode()
        # Use bcrypt with proper rounds for security
        return bcrypt.hashpw(salted_password, bcrypt.gensalt(rounds=auth_config.bcrypt_rounds)).decode('utf-8')

    def _verify_password(self, password: str, password_hash: str, salt: str) -> bool:
        """Verify password against hash."""
        salted_password = f"{password}{salt}".encode()
        return bcrypt.checkpw(salted_password, password_hash.encode('utf-8'))

    def _hash_token(self, token: str) -> str:
        """Hash token for storage using SHA-256 (appropriate for tokens)."""
        return hashlib.sha256(token.encode('utf-8')).hexdigest()

    async def _generate_token_pair(self, user_id: UUID, email: str, device_id: str | None = None, locale: str = "en-US") -> AuthTokenPair:
        """Generate JWT access and refresh token pair."""
        # Generate access token
        access_token = generate_access_token(
            user_id=user_id,
            email=email,
            expires_minutes=auth_config.access_token_expire_minutes,
            device_id=device_id
        )

        # Generate refresh token
        refresh_token = secrets.token_urlsafe(32)

        # Store refresh token
        token_hash = self._hash_token(refresh_token)
        expires_at = utcnow() + timedelta(days=auth_config.refresh_token_expire_days)

        # Use isolated auth engine to avoid RLS interference
        from ...db.engine import get_auth_session_factory
        auth_session_factory = get_auth_session_factory()

        async with auth_session_factory() as auth_session:
            # Disable RLS only in this isolated session
            from sqlalchemy import text
            await auth_session.execute(text("RESET ROLE"))
            await auth_session.execute(text("SET row_security = off"))

            repository = AuthRepository(auth_session)
            await repository.create_refresh_token(
                user_id=user_id,
                token_hash=token_hash,
                device_id=device_id,
                expires_at=expires_at,
                locale=locale
            )

            # Commit the isolated auth transaction
            await auth_session.commit()

        return AuthTokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=auth_config.access_token_expire_minutes * 60
        )

    @trace_async
    async def authenticate_social_user(self, request: SocialLoginRequest, locale: str = "en-US") -> SocialAuthResponse:
        """Authenticate user via social provider."""
        domain_logger = get_auth_logger()
        
        with RequestTracker(operation="authenticate_social_user", provider=request.provider) as tracker:
            try:
                logger.info("Social login attempt", extra={
                    "provider": request.provider,
                    "locale": locale
                })

                # Initialize validators
                from ...config import Config
                config = Config()

                # Validate provider-specific configuration
                if request.provider == "apple" and not config.APPLE_CLIENT_ID:
                    raise BadRequest(t("auth.error.apple_not_configured", locale=locale))
                if request.provider == "google" and not config.GOOGLE_CLIENT_ID:
                    raise BadRequest(t("auth.error.google_not_configured", locale=locale))

                apple_validator = AppleTokenValidator(client_id=config.APPLE_CLIENT_ID or "")
                google_validator = GoogleTokenValidator()

                # Validate token with provider
                if request.provider == "apple":
                    user_info = await apple_validator.validate_token(request.access_token)
                elif request.provider == "google":
                    user_info = await google_validator.validate_token(request.access_token)
                else:
                    raise BadRequest(t("auth.error.unsupported_provider", locale=locale))

                # Validate email format if present
                if user_info.email:
                    from email_validator import EmailNotValidError, validate_email
                    try:
                        validate_email(user_info.email)
                    except EmailNotValidError:
                        logger.warning("Invalid email from social provider", extra={
                            "provider": request.provider,
                            "email": user_info.email
                        })
                        user_info.email = None  # Ignore invalid email

                # Use regular UoW pattern for consistency
                async with async_uow_factory(self.session_factory, user_id=None)() as uow:
                    repository = AuthRepository(uow.session)
                    is_new_user = False
                    user_id = None

                    # Check if user exists by social account
                    user_id = await repository.find_user_by_social_account(
                        request.provider,
                        user_info.provider_user_id
                    )

                    if not user_id:
                        # Check if user exists by email
                        if user_info.email:
                            user_id = await repository.find_user_by_email(user_info.email)

                            if user_id:
                                # Link social account to existing user
                                await repository.link_social_account(
                                    user_id,
                                    request.provider,
                                    user_info.provider_user_id,
                                    user_info.email,
                                    user_info.name,
                                    user_info.avatar_url
                                )
                                logger.info("Linked social account to existing user", extra={
                                    "user_id": str(user_id),
                                    "provider": request.provider
                                })
                            else:
                                # Create new user with social account
                                user_id = await repository.create_user_with_social_account(
                                    user_info.email,
                                    user_info.name or request.name,
                                    request.provider,
                                    user_info.provider_user_id,
                                    user_info.avatar_url,
                                    locale
                                )
                                is_new_user = True
                                logger.info("Created new user with social account", extra={
                                    "user_id": str(user_id),
                                    "provider": request.provider
                                })
                        else:
                            # Create user without email
                            user_id = await repository.create_user_with_social_account(
                                None,
                                request.name or f"Usuário {request.provider}",
                                request.provider,
                                user_info.provider_user_id,
                                user_info.avatar_url,
                                locale
                            )
                            is_new_user = True
                            logger.info("Created new user without email", extra={
                                "user_id": str(user_id),
                                "provider": request.provider
                            })

                    # Get user profile and social accounts before commit
                    social_accounts = await repository.get_user_social_accounts(user_id)
                    linked_accounts = [acc.provider for acc in social_accounts]

                    # Get user data before commit (no RLS needed, we're in system context)
                    from ...domain.users.schemas import users_table
                    user_stmt = sa.select(users_table).where(users_table.c.id == user_id)
                    user_result = await uow.session.execute(user_stmt)
                    user_row = user_result.first()
                    if not user_row:
                        raise BadRequest(t("auth.error.user_not_found", locale=locale))

                    # Commit via UoW
                    await uow.commit()

                # Convert to UserOut DTO
                from ..users.schemas import UserOut
                user = UserOut.model_validate(user_row._asdict())

                # Generate tokens
                tokens = await self._generate_token_pair(
                    user_id=user_id,
                    email=user.email or "",
                    device_id=None,
                    locale=locale
                )

                # Update last login
                await self.users_service.update_last_login(user_id)

                logger.info("Social login successful", extra={
                    "user_id": str(user_id),
                    "provider": request.provider,
                    "is_new_user": is_new_user,
                    "linked_accounts": linked_accounts
                })

                domain_logger.business_event(
                    "social_login_success",
                    entity_id=str(user_id),
                    provider=request.provider,
                    is_new_user=is_new_user,
                    linked_accounts=linked_accounts
                )
                
                tracker.log_success(result_id=str(user_id))

                return SocialAuthResponse(
                    user=user,
                    tokens=tokens,
                    is_new_user=is_new_user,
                    linked_accounts=linked_accounts
                )
            except BadRequest as e:
                domain_logger.business_event(
                    "social_login_failed",
                    provider=request.provider,
                    error_type=type(e).__name__,
                    reason="validation_error"
                )
                error_id = tracker.log_error(e, error_type=type(e).__name__, provider=request.provider)
                raise e
            except Exception as e:
                print(f"❌ Social authentication failed: {type(e).__name__}: {str(e)}")
                import traceback
                traceback.print_exc()
                logger.error("Social authentication failed", extra={
                    "provider": request.provider,
                    "error": str(e)
                })
                error_id = tracker.log_error(e, error_type=type(e).__name__, provider=request.provider)
                raise BadRequest(t("auth.error.social_login_failed", locale=locale))
