"""Onboarding service for business logic orchestration and step validation."""

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from ...db.uow import async_uow_factory
from ...utils.domain_logger import get_domain_logger
from ...utils.errors import BadRequest, Conflict, FailedDependency, NotFound, ValidationError
from ...utils.request_tracking import RequestTracker
from ...utils.tracing import trace_async

# Import from repository to maintain consistency
from .repository import STEPS_ORDER, OnboardingRepository
from .schemas import OnboardingProgressOut, OnboardingStatus, OnboardingStep, OnboardingStepOut

domain_logger = get_domain_logger(__name__)


class OnboardingService:
    """Service for onboarding step management and business logic."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory

    @trace_async
    async def get_progress(self, user_id: UUID) -> OnboardingProgressOut:
        """Get onboarding progress for user."""
        with RequestTracker(user_id=user_id, operation="get_progress") as tracker:
            try:
                tracking_context = domain_logger.operation_start("get_progress", user_id=str(user_id))

                async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                    repository = OnboardingRepository(uow.session)
                    progress = await repository.get_progress(user_id)
                    
                    domain_logger.operation_success(tracking_context, {
                        "user_id": str(user_id),
                        "progress_percent": progress.progress_percent,
                        "current_step": progress.current_step,
                        "is_completed": progress.is_completed
                    })
                    tracker.log_success(
                        progress_percent=progress.progress_percent,
                        current_step=progress.current_step,
                        is_completed=progress.is_completed
                    )
                    
                    return progress
            except Exception as e:
                error_id = tracker.log_error(e, context={
                    "user_id": str(user_id)
                })
                
                # Re-raise business logic exceptions as-is
                if isinstance(e, (Conflict, ValidationError, BadRequest, NotFound)):
                    raise
                    
                raise FailedDependency(f"Failed to get progress (Error ID: {error_id})")
    @trace_async
    async def get_status(self, user_id: UUID) -> OnboardingProgressOut:
        """Get onboarding status for user (alias for get_progress)."""
        return await self.get_progress(user_id)

    @trace_async
    async def get_step(self, user_id: UUID, step: OnboardingStep) -> OnboardingStepOut | None:
        """Get specific onboarding step for user."""
        with RequestTracker(user_id=user_id, operation="get_step") as tracker:
            try:
                tracking_context = domain_logger.operation_start("get_step", user_id=str(user_id), step=step)

                async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                    repository = OnboardingRepository(uow.session)
                    result = await repository.get_step(user_id, step)

                domain_logger.operation_success(tracking_context, {
                    "user_id": str(user_id),
                    "step": step,
                    "found": result is not None
                })

                tracker.log_success(step=step, found=result is not None)
                return result

            except Exception as e:
                error_id = tracker.log_error(e, context={
                    "user_id": str(user_id),
                    "step": step,
                    "status": status
                })
                raise FailedDependency(f"Failed to update step (Error ID: {error_id})")
    @trace_async
    async def update_step(
        self, user_id: UUID, step: OnboardingStep, status: OnboardingStatus,
        payload: dict[str, Any] | None = None
    ) -> OnboardingStepOut:
        """Update onboarding step with business rule validation."""
        with RequestTracker(user_id=user_id, operation="update_step") as tracker:
            try:
                tracking_context = domain_logger.operation_start("update_step", user_id=str(user_id), step=step, status=status, has_payload=payload is not None)

                # Validate step-specific business rules
                self._validate_step_rules(step, status, payload)

                # Special validation for 'done' step
                if step == "done" and status == "completed":
                    await self._validate_done_completion(user_id)

                # Update the step
                async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                    repository = OnboardingRepository(uow.session)
                    result = await repository.upsert_step(user_id, step, status, payload)
                    await uow.commit()
                    
                    domain_logger.operation_success(tracking_context, {
                        "user_id": str(user_id),
                        "step": step,
                        "status": status,
                        "step_key": f"{user_id}:{step}"
                    })
                    domain_logger.business_event("onboarding_step_updated", {
                        "user_id": str(user_id),
                        "step": step,
                        "status": status
                    })
                    tracker.log_success(step=step, status=status)
                    
                    return result
            except Exception as e:
                error_id = tracker.log_error(e, context={
                    "user_id": str(user_id),
                    "step": step,
                    "status": status
                })
                
                # Re-raise business logic exceptions as-is
                if isinstance(e, (Conflict, ValidationError, BadRequest)):
                    raise
                    
                raise FailedDependency(f"Failed to update step (Error ID: {error_id})")
    @trace_async
    async def complete_step(
        self, user_id: UUID, step: OnboardingStep, payload: dict[str, Any] | None = None
    ) -> OnboardingStepOut:
        """Mark step as completed with validation."""
        return await self.update_step(user_id, step, "completed", payload)

    @trace_async
    async def start_step(
        self, user_id: UUID, step: OnboardingStep, payload: dict[str, Any] | None = None
    ) -> OnboardingStepOut:
        """Mark step as in progress."""
        return await self.update_step(user_id, step, "in_progress", payload)

    @trace_async
    async def skip_step(
        self, user_id: UUID, step: OnboardingStep, payload: dict[str, Any] | None = None
    ) -> OnboardingStepOut:
        """Skip a specific onboarding step."""
        return await self.update_step(user_id, step, "skipped", payload)

    @trace_async
    async def is_completed(self, user_id: UUID) -> bool:
        """Check if user has completed all onboarding steps."""
        with RequestTracker(user_id=user_id, operation="is_completed") as tracker:
            try:
                tracking_context = domain_logger.operation_start("is_completed", user_id=str(user_id))

                async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                    repository = OnboardingRepository(uow.session)
                    result = await repository.is_completed(user_id)

                domain_logger.operation_success(tracking_context, {
                    "user_id": str(user_id),
                    "is_completed": result
                })

                tracker.log_success(is_completed=result)
                return result

            except Exception as e:
                error_id = tracker.log_error(e, context={
                    "user_id": str(user_id),
                    "step": step,
                    "status": status
                })
                raise FailedDependency(f"Failed to update step (Error ID: {error_id})")
    @trace_async
    async def get_next_step(self, user_id: UUID) -> OnboardingStep | None:
        """Get the next step user should complete."""
        with RequestTracker(user_id=user_id, operation="get_next_step") as tracker:
            try:
                tracking_context = domain_logger.operation_start("get_next_step", user_id=str(user_id))

                async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                    repository = OnboardingRepository(uow.session)
                    result = await repository.get_next_step(user_id)

                domain_logger.operation_success(tracking_context, {
                    "user_id": str(user_id),
                    "next_step": result if result else None
                })

                tracker.log_success(next_step=result if result else None)
                return result

            except Exception as e:
                error_id = tracker.log_error(e, context={
                    "user_id": str(user_id),
                    "step": step,
                    "status": status
                })
                raise FailedDependency(f"Failed to update step (Error ID: {error_id})")
    @trace_async
    async def reset_user(self, user_id: UUID) -> bool:
        """Reset all onboarding steps for user (admin/support use)."""
        with RequestTracker(user_id=user_id, operation="reset_user") as tracker:
            try:
                tracking_context = domain_logger.operation_start("reset_user", user_id=str(user_id))

                async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                    repository = OnboardingRepository(uow.session)
                    result = await repository.reset_user(user_id)
                    await uow.commit()

                domain_logger.operation_success(tracking_context, {
                    "user_id": str(user_id),
                    "reset_successful": result
                })

                domain_logger.business_event("onboarding_reset", {
                    "user_id": str(user_id),
                    "reset_successful": result
                })

                tracker.log_success(reset_successful=result)
                return result

            except Exception as e:
                error_id = tracker.log_error(e, context={
                    "user_id": str(user_id),
                    "step": step,
                    "status": status
                })
                raise FailedDependency(f"Failed to update step (Error ID: {error_id})")
    def _validate_step_rules(
        self, step: OnboardingStep, status: OnboardingStatus, payload: dict[str, Any] | None
    ) -> None:
        """Validate step-specific business rules."""
        if status != "completed":
            return  # Only validate completion requirements

        payload = payload or {}

        # Define validation rules for each step
        validators = {
            "consent": self._validate_consent_step,
            "profile": self._validate_profile_step,
            "preferences": self._validate_preferences_step,
            "connect_channels": self._validate_connect_channels_step,
            "enable_notification": self._validate_notification_step,
        }

        validator = validators.get(step)
        if validator:
            validator(payload)

    def _validate_consent_step(self, payload: dict[str, Any]) -> None:
        """Validate consent step requirements."""
        # Check if consent_accepted is explicitly set to true
        consent_accepted = payload.get("consent_accepted")
        if consent_accepted is not True:
            raise ValidationError("consent_accepted must be true to complete consent step")

        # Consent version is optional but recommended
        if "consent_version" in payload and not payload.get("consent_version"):
            raise ValidationError("consent_version cannot be empty if provided")

    def _validate_profile_step(self, payload: dict[str, Any]) -> None:
        """Validate profile step requirements."""
        bio = payload.get("bio")
        if bio and len(bio) > 300:
            raise ValidationError("Profile bio must be 300 characters or less")

    def _validate_preferences_step(self, payload: dict[str, Any]) -> None:
        """Validate preferences step requirements."""
        topic_ids = payload.get("topicIds", [])
        if not isinstance(topic_ids, list):
            raise ValidationError("preferences.topicIds must be a list")

        avoid_ids = payload.get("avoidIds", [])
        if avoid_ids is not None and not isinstance(avoid_ids, list):
            raise ValidationError("preferences.avoidIds must be a list")

    def _validate_connect_channels_step(self, payload: dict[str, Any]) -> None:
        """Validate connect channels step requirements."""
        instagram = payload.get("instagram_connected")
        whatsapp = payload.get("whatsapp_connected")

        if instagram is not None and not isinstance(instagram, bool):
            raise ValidationError("connect_channels.instagram_connected must be boolean")
        if whatsapp is not None and not isinstance(whatsapp, bool):
            raise ValidationError("connect_channels.whatsapp_connected must be boolean")

    def _validate_notification_step(self, payload: dict[str, Any]) -> None:
        """Validate notification step requirements."""
        notifications = payload.get("notifications_enabled")
        if notifications is not None and not isinstance(notifications, bool):
            raise ValidationError("enable_notification.notifications_enabled must be boolean")

    async def _validate_done_completion(self, user_id: UUID) -> None:
        """Validate that all previous steps are completed before allowing done.completed."""
        async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
            repository = OnboardingRepository(uow.session)
            progress = await repository.get_progress(user_id)

        # Check if all required steps are completed
        required_steps = [step for step in STEPS_ORDER if step != "done"]
        missing_steps = []

        for step in required_steps:
            if step not in progress.completed_steps:
                # Check if step is skippable
                step_info = next((s for s in progress.steps if s.name == step), None)
                if step_info and step_info.required:
                    missing_steps.append(step)

        if missing_steps:
            raise Conflict(f"Cannot complete onboarding: step '{missing_steps[0]}' is not completed")
    @trace_async
    async def complete_consent(
        self, user_id: UUID, consent_version: str, consent_accepted: bool = True
    ) -> OnboardingStepOut:
        """Complete consent step with required data."""
        payload = {
            "consent_accepted": consent_accepted,
            "consent_version": consent_version
        }
        return await self.complete_step(user_id, "consent", payload)

    @trace_async
    async def complete_profile(
        self, user_id: UUID, bio: str | None = None, **profile_data: Any
    ) -> OnboardingStepOut:
        """Complete profile step with optional bio and other profile data."""
        payload = profile_data.copy()
        if bio:
            payload["bio"] = bio
        return await self.complete_step(user_id, "profile", payload)

    @trace_async
    async def complete_preferences(
        self, user_id: UUID, topic_ids: list[UUID] | None = None, avoid_ids: list[UUID] | None = None
    ) -> OnboardingStepOut:
        """Complete preferences step with topic and avoid selections."""
        payload = {
            "topicIds": topic_ids or [],
            "avoidIds": avoid_ids or []
        }
        return await self.complete_step(user_id, "preferences", payload)

    @trace_async
    async def complete_connect_channels(
        self, user_id: UUID, instagram_connected: bool = False, whatsapp_connected: bool = False
    ) -> OnboardingStepOut:
        """Complete connect channels step with connection status."""
        payload = {
            "instagram_connected": instagram_connected,
            "whatsapp_connected": whatsapp_connected
        }
        return await self.complete_step(user_id, "connect_channels", payload)

    @trace_async
    async def complete_enable_notification(
        self, user_id: UUID, notifications_enabled: bool = True
    ) -> OnboardingStepOut:
        """Complete enable notification step."""
        payload = {
            "notifications_enabled": notifications_enabled
        }
        return await self.complete_step(user_id, "enable_notification", payload)

    @trace_async
    async def complete_onboarding(self, user_id: UUID) -> OnboardingStepOut:
        """Complete the entire onboarding process."""
        with RequestTracker(user_id=user_id, operation="complete_onboarding") as tracker:
            try:
                tracking_context = domain_logger.operation_start("complete_onboarding", user_id=str(user_id))

                # This will validate all previous steps are completed
                result = await self.complete_step(user_id, "done")
                
                domain_logger.operation_success(tracking_context, {
                    "user_id": str(user_id),
                    "step": result.step,
                    "progress_percent": 100
                })
                domain_logger.business_event("onboarding_completed", {
                    "user_id": str(user_id),
                    "step": result.step,
                    "completion_timestamp": result.updated_at.isoformat() if result.updated_at else None
                })
                tracker.log_success(
                    step=result.step,
                    progress_percent=100,
                    completion_timestamp=result.updated_at.isoformat() if result.updated_at else None
                )
                
                return result
            except Exception as e:
                error_id = tracker.log_error(e, context={
                    "user_id": str(user_id)
                })
                
                # Re-raise business logic exceptions as-is
                if isinstance(e, (Conflict, ValidationError, BadRequest)):
                    raise
                    
                raise FailedDependency(f"Failed to complete onboarding (Error ID: {error_id})")