"""Users service for user profile management."""

from datetime import UTC, datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from ...db.uow import async_uow_factory
from ...utils import errors
from ...utils.logging import get_safe_logger
from ...utils.tracing import trace_async
from ...utils.request_tracking import RequestTracker
from ...utils.domain_logger import get_domain_logger
from .repository import UsersRepository
from .schemas import (
    CreateUserRequest,
    UserOut,
    UserPreferencesOut,
    UserPreferencesUpdate,
    UserUpdate,
)

logger = get_safe_logger(__name__)
domain_logger = get_domain_logger("users")

class UsersService:
    """Service for user profile operations."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self.session_factory = session_factory

    @trace_async
    async def create_user(self, request: CreateUserRequest) -> UserOut:
        """Create new user profile."""
        with RequestTracker(operation="create_user") as tracker:
            try:
                tracking_context = tracking_context = domain_logger.operation_start(
                    "create_user",
                    email=request.email,
                    has_bio=bool(request.bio),
                    country=request.country
                )

                # For user registration, we need to use app_user role but without user_id context
                # This is a special case where we create the user before we have their ID
                async with async_uow_factory(self.session_factory, user_id=None)() as uow:
                    # Temporarily disable RLS for this specific operation
                    import os

                    from sqlalchemy import text

                    # Skip SQL commands in test environment
                    if os.getenv("ENV") != "test":
                        domain_logger.info("Setting up session for user registration")

                        # Reset to default role and disable RLS for registration
                        await uow.session.execute(text("RESET ROLE"))
                        await uow.session.execute(text("SET row_security = off"))

                        domain_logger.info("Session configured for user registration")

                    repository = UsersRepository(uow.session)

                    # Check if user exists
                    existing = await repository.get_user_by_email(request.email)
                    if existing:
                        raise errors.Conflict("User already exists")

                    user = await repository.create_user(
                        email=request.email,
                        gender=request.gender,
                        country=request.country,
                        city=request.city,
                        state=request.state,
                        bio=request.bio
                    )

                    await uow.commit()
                    
                    domain_logger.operation_success(
                        tracking_context,
                        result_id=str(user.id),
                        user_id=str(user.id)
                    )
                    
                    tracker.log_success(result_id=str(user.id))
                    created_user: UserOut = user
                    return created_user
                    
            except Exception as e:
                error_id = tracker.log_error(e, error_type="OperationError")
                
                if isinstance(e, (errors.Conflict, errors.BadRequest)):
                    raise
                raise errors.FailedDependency(f"Failed to create user: {str(e)}")

    @trace_async
    async def get_user(self, user_id: UUID) -> UserOut | None:
        """Get user by ID."""
        with RequestTracker(user_id=str(user_id), operation="get_user") as tracker:
            try:
                tracking_context = tracking_context = domain_logger.operation_start(
                    "get_user",
                    user_id=str(user_id)
                )

                async with async_uow_factory(self.session_factory, user_id=None)() as uow:
                    # Disable RLS for user lookup during authentication
                    import os

                    from sqlalchemy import text

                    # Skip SQL commands in test environment
                    if os.getenv("ENV") != "test":
                        await uow.session.execute(text("RESET ROLE"))
                        await uow.session.execute(text("SET row_security = off"))

                    repository = UsersRepository(uow.session)
                    user: UserOut | None = await repository.get_user(user_id)
                    
                    if user:
                        domain_logger.operation_success(
                            tracking_context,
                            result_id=str(user.id)
                        )
                        tracker.log_success(result_id=str(user.id))
                    else:
                        domain_logger.info("User not found", user_id=str(user_id))
                        
                    return user
                
            except Exception as e:
                error_id = tracker.log_error(e, error_type="OperationError")
                raise errors.FailedDependency(f"Failed to retrieve user: {str(e)}")

    @trace_async
    async def get_user_by_email(self, email: str) -> UserOut | None:
        """Get user by email."""
        with RequestTracker(operation="get_user_by_email") as tracker:
            try:
                tracking_context = tracking_context = domain_logger.operation_start(
                    "get_user_by_email",
                    email=email
                )

                async with async_uow_factory(self.session_factory, user_id=None)() as uow:
                    repository = UsersRepository(uow.session)
                    user: UserOut | None = await repository.get_user_by_email(email)
                    
                    if user:
                        domain_logger.operation_success(
                            tracking_context,
                            result_id=str(user.id)
                        )
                        tracker.log_success(result_id=str(user.id))
                    else:
                        domain_logger.info("User not found by email", email=email)
                        
                    return user
                    
            except Exception as e:
                error_id = tracker.log_error(e, error_type="OperationError")
                raise errors.FailedDependency(f"Failed to retrieve user: {str(e)}")

    @trace_async
    async def update_user(self, user_id: UUID, data: UserUpdate, locale: str = "en-US") -> UserOut:
        """Update user profile."""
        with RequestTracker(user_id=str(user_id), operation="update_user") as tracker:
            try:
                tracking_context = tracking_context = domain_logger.operation_start(
                    "update_user",
                    user_id=str(user_id),
                    locale=locale,
                    has_email_update=bool(data.email)
                )

                async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                    repository = UsersRepository(uow.session)

                    # Check if email is being updated and already exists
                    if data.email:
                        existing = await repository.get_user_by_email(data.email)
                        if existing and existing.id != user_id:
                            raise errors.Conflict("Email already in use")

                    user = await repository.update_user(user_id, data, locale)
                    if not user:
                        raise errors.NotFound("User not found")

                    await uow.commit()
                    
                    domain_logger.operation_success(
                        tracking_context,
                        result_id=str(user.id)
                    )
                    tracker.log_success(result_id=str(user.id))
                    
                    updated_user: UserOut = user
                    return updated_user
                    
            except Exception as e:
                error_id = tracker.log_error(e, error_type="OperationError")
                
                if isinstance(e, (errors.Conflict, errors.NotFound, errors.BadRequest)):
                    raise
                raise errors.FailedDependency(f"Failed to update user: {str(e)}")

    @trace_async
    async def delete_user(self, user_id: UUID) -> None:
        """Delete user and ALL related data (GDPR/LGPD compliance)."""
        with RequestTracker(user_id=str(user_id), operation="delete_user") as tracker:
            try:
                tracking_context = tracking_context = domain_logger.operation_start(
                    "delete_user",
                    user_id=str(user_id),
                    compliance_type="GDPR/LGPD"
                )

                async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                    user_id_str = str(user_id)  # Convert UUID to string for PostgreSQL

                    # Delete all user-related data in correct order (foreign keys)
                    # Messages first (references threads)
                    await uow.session.execute(sa.text("DELETE FROM messages WHERE thread_id IN (SELECT id FROM threads WHERE user_id = :user_id)"), {"user_id": user_id_str})

                    # AI generations and jobs
                    await uow.session.execute(sa.text("DELETE FROM ai_generations WHERE thread_id IN (SELECT id FROM threads WHERE user_id = :user_id)"), {"user_id": user_id_str})
                    await uow.session.execute(sa.text("DELETE FROM ai_jobs WHERE user_id = :user_id"), {"user_id": user_id_str})

                    # Threads
                    await uow.session.execute(sa.text("DELETE FROM threads WHERE user_id = :user_id"), {"user_id": user_id_str})

                    # Integrations and WhatsApp sessions
                    await uow.session.execute(sa.text("DELETE FROM integrations_accounts WHERE user_id = :user_id"), {"user_id": user_id_str})
                    await uow.session.execute(sa.text("DELETE FROM whatsapp_pairing_sessions WHERE user_id = :user_id"), {"user_id": user_id_str})

                    # Devices and notifications
                    await uow.session.execute(sa.text("DELETE FROM devices WHERE user_id = :user_id"), {"user_id": user_id_str})
                    await uow.session.execute(sa.text("DELETE FROM notifications WHERE user_id = :user_id"), {"user_id": user_id_str})

                    # User preferences (topics and avoid)
                    await uow.session.execute(sa.text("DELETE FROM user_topics WHERE user_id = :user_id"), {"user_id": user_id_str})
                    await uow.session.execute(sa.text("DELETE FROM user_avoid WHERE user_id = :user_id"), {"user_id": user_id_str})

                    # Legal acceptances and onboarding
                    await uow.session.execute(sa.text("DELETE FROM user_legal_acceptances WHERE user_id = :user_id"), {"user_id": user_id_str})
                    await uow.session.execute(sa.text("DELETE FROM onboarding_steps WHERE user_id = :user_id"), {"user_id": user_id_str})

                    # Subscription status
                    await uow.session.execute(sa.text("DELETE FROM subscription_status WHERE user_id = :user_id"), {"user_id": user_id_str})

                    # Telemetry events (if they contain user_id)
                    await uow.session.execute(sa.text("DELETE FROM telemetry_events WHERE user_id = :user_id"), {"user_id": user_id_str})

                    # Finally delete the user record (hard delete for GDPR)
                    await uow.session.execute(sa.text("DELETE FROM users WHERE id = :user_id"), {"user_id": user_id_str})

                    await uow.commit()

                domain_logger.operation_success(
                    tracking_context,
                    result_id=str(user_id),
                    data_deleted=True
                )
                tracker.log_success(result_id=str(user_id))
                
            except Exception as e:
                error_id = tracker.log_error(e, error_type="OperationError")
                
                if isinstance(e, errors.NotFound):
                    raise
                raise errors.FailedDependency(f"Failed to delete user: {str(e)}")

    @trace_async
    async def list_users(self, limit: int = 50, offset: int = 0) -> list[UserOut]:
        """List users with pagination (admin only)."""
        with RequestTracker(operation="list_users") as tracker:
            try:
                tracking_context = tracking_context = domain_logger.operation_start(
                    "list_users",
                    limit=limit,
                    offset=offset
                )

                if limit > 100:
                    raise errors.BadRequest("Limit cannot exceed 100")
                if limit < 1:
                    raise errors.BadRequest("Limit must be at least 1")
                if offset < 0:
                    raise errors.BadRequest("Offset cannot be negative")

                async with async_uow_factory(self.session_factory, user_id=None)() as uow:
                    repository = UsersRepository(uow.session)
                    users: list[UserOut] = await repository.list_users(limit, offset)
                    
                    domain_logger.operation_success(
                        tracking_context,
                        users_count=len(users)
                    )
                    tracker.log_success(result_count=len(users))
                    
                    return users
                    
            except Exception as e:
                error_id = tracker.log_error(e, error_type="OperationError")
                
                if isinstance(e, errors.BadRequest):
                    raise
                raise errors.FailedDependency(f"Failed to list users: {str(e)}")

    @trace_async
    async def count_users(self) -> int:
        """Count total active users (admin only)."""
        with RequestTracker(operation="count_users") as tracker:
            try:
                tracking_context = tracking_context = domain_logger.operation_start("count_users")

                async with async_uow_factory(self.session_factory, user_id=None)() as uow:
                    repository = UsersRepository(uow.session)
                    count: int = await repository.count_users()
                    
                    domain_logger.operation_success(
                        tracking_context,
                        total_count=count
                    )
                    tracker.log_success(result_count=count)
                    
                    return count
                    
            except Exception as e:
                error_id = tracker.log_error(e, error_type="OperationError")
                raise errors.FailedDependency(f"Failed to count users: {str(e)}")

    @trace_async
    async def update_last_login(self, user_id: UUID) -> bool:
        """Update user's last login timestamp."""
        with RequestTracker(user_id=str(user_id), operation="update_last_login") as tracker:
            try:
                tracking_context = tracking_context = domain_logger.operation_start(
                    "update_last_login",
                    user_id=str(user_id)
                )

                async with async_uow_factory(self.session_factory, user_id=None)() as uow:
                    # Disable RLS for last login update during registration
                    from sqlalchemy import text
                    await uow.session.execute(text("RESET ROLE"))
                    await uow.session.execute(text("SET row_security = off"))

                    repository = UsersRepository(uow.session)
                    result = await repository.update_last_login(user_id, datetime.now(UTC))
                    await uow.commit()
                    
                    domain_logger.operation_success(
                        tracking_context,
                        login_updated=result
                    )
                    tracker.log_success(result_id=str(user_id))
                    
                    success: bool = result
                    return success
                    
            except Exception as e:
                error_id = tracker.log_error(e, error_type="OperationError")
                raise errors.FailedDependency(f"Failed to update last login: {str(e)}")

    @trace_async
    async def get_user_preferences(self, user_id: UUID) -> UserPreferencesOut:
        """Get user preferences."""
        with RequestTracker(user_id=str(user_id), operation="get_user_preferences") as tracker:
            try:
                tracking_context = tracking_context = domain_logger.operation_start(
                    "get_user_preferences",
                    user_id=str(user_id)
                )

                async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                    repository = UsersRepository(uow.session)
                    user = await repository.get_user(user_id)
                    if not user:
                        raise errors.NotFound("User not found")

                    # Import CatalogRepository to get user topics and avoid
                    from ..catalogs.repository import CatalogRepository
                    catalog_repository = CatalogRepository(uow.session)

                    # Get user topics and avoid preferences
                    user_topics = await catalog_repository.find_user_topics(user_id)
                    user_avoids = await catalog_repository.find_user_avoid(user_id)

                    # Build preferences from user data and stored preferences
                    stored_preferences = user.preferences or {}
                    preferences = {
                        "language": user.locale or "en-US",
                        "timezone": user.timezone or "UTC",
                        "notifications_enabled": stored_preferences.get("notifications_enabled", True),
                        "email_notifications": stored_preferences.get("email_notifications", True),
                        "push_notifications": stored_preferences.get("push_notifications", True),
                        "tracking_notifications_enabled": stored_preferences.get("tracking_notifications_enabled", True),
                        "ai_suggestions_enabled": stored_preferences.get("ai_suggestions_enabled", True),
                        "theme": stored_preferences.get("theme", "light")
                    }

                    # Convert topics and avoid to dict format
                    topics_data = [
                        {
                            "topic_id": str(topic.topic_id),
                            "name": topic.name,
                            "description": topic.description,
                            "active": topic.active,
                            "created_at": topic.created_at.isoformat()
                        }
                        for topic in user_topics
                    ]

                    avoid_data = [
                        {
                            "avoid_id": str(avoid.avoid_id),
                            "description": avoid.description,
                            "active": avoid.active,
                            "created_at": avoid.created_at.isoformat()
                        }
                        for avoid in user_avoids
                    ]

                    result = UserPreferencesOut(
                        user_id=user_id,
                        preferences=preferences,
                        topics=topics_data,
                        avoid=avoid_data,
                        updated_at=user.updated_at
                    )
                    
                    domain_logger.operation_success(
                        tracking_context,
                        result_id=str(user_id),
                        topics_count=len(topics_data),
                        avoid_count=len(avoid_data)
                    )
                    tracker.log_success(result_id=str(user_id))
                    
                    return result
                    
            except Exception as e:
                error_id = tracker.log_error(e, error_type="OperationError")
                
                if isinstance(e, errors.NotFound):
                    raise
                raise errors.FailedDependency(f"Failed to get preferences: {str(e)}")

    @trace_async
    async def update_user_preferences(self, user_id: UUID, preferences_data: UserPreferencesUpdate, locale: str = "en-US") -> UserPreferencesOut:
        """Update user preferences."""
        with RequestTracker(user_id=str(user_id), operation="update_user_preferences") as tracker:
            try:
                tracking_context = tracking_context = domain_logger.operation_start(
                    "update_user_preferences",
                    user_id=str(user_id),
                    locale=locale
                )

                async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                    repository = UsersRepository(uow.session)

                    # Get current user to merge preferences
                    current_user = await repository.get_user(user_id)
                    current_preferences = current_user.preferences or {}

                    # Update user locale/timezone if provided
                    update_data = {}
                    if preferences_data.language:
                        update_data["locale"] = preferences_data.language
                    if preferences_data.timezone:
                        update_data["timezone"] = preferences_data.timezone

                    # Update preferences
                    updated_preferences = current_preferences.copy()
                    if preferences_data.notifications_enabled is not None:
                        updated_preferences["notifications_enabled"] = preferences_data.notifications_enabled
                    if preferences_data.email_notifications is not None:
                        updated_preferences["email_notifications"] = preferences_data.email_notifications
                    if preferences_data.push_notifications is not None:
                        updated_preferences["push_notifications"] = preferences_data.push_notifications
                    if preferences_data.tracking_notifications_enabled is not None:
                        updated_preferences["tracking_notifications_enabled"] = preferences_data.tracking_notifications_enabled
                    if preferences_data.ai_suggestions_enabled is not None:
                        updated_preferences["ai_suggestions_enabled"] = preferences_data.ai_suggestions_enabled
                    if preferences_data.theme is not None:
                        updated_preferences["theme"] = preferences_data.theme

                    update_data["preferences"] = updated_preferences

                    if update_data:
                        user_update = UserUpdate(**update_data)
                        updated_user = await repository.update_user(user_id, user_update, locale)
                        if not updated_user:
                            raise errors.NotFound("User not found")

                    await uow.commit()

                    domain_logger.operation_success(
                        tracking_context,
                        result_id=str(user_id),
                        preferences_updated=len(update_data)
                    )
                    tracker.log_success(result_id=str(user_id))

                # Return updated preferences
                updated_preferences_out: UserPreferencesOut = await self.get_user_preferences(user_id)
                return updated_preferences_out
                
            except Exception as e:
                error_id = tracker.log_error(e, error_type="OperationError")
                
                if isinstance(e, (errors.NotFound, errors.BadRequest)):
                    raise
                raise errors.FailedDependency(f"Failed to update preferences: {str(e)}")


def create_users_service(session_factory: async_sessionmaker[AsyncSession]) -> UsersService:
    """Factory function for UsersService."""
    return UsersService(session_factory)
