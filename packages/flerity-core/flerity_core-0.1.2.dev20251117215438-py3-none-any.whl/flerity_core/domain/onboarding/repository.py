"""Onboarding repository for managing user onboarding steps."""

from typing import Any
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from ...utils.errors import BadRequest, FailedDependency, NotFound
from ...utils.tracing import trace_async
from ...utils.request_tracking import RequestTracker
from ...utils.domain_logger import get_domain_logger
from .schemas import (
    OnboardingProgressOut,
    OnboardingStatus,
    OnboardingStep,
    OnboardingStepCreate,
    OnboardingStepOut,
    OnboardingStepUpdate,
    StepInfo,
    onboarding_steps_table,
)

domain_logger = get_domain_logger(__name__)

# Constants
STEPS_ORDER: list[OnboardingStep] = [
    "welcome",
    "consent",
    "profile",
    "preferences",
    "connect_channels",
    "enable_notification",
    "done"
]


class OnboardingRepository:
    """Repository for onboarding step data access operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    @trace_async
    async def get_user_steps(self, user_id: UUID) -> list[OnboardingStepOut]:
        """Get all onboarding steps for user. RLS enforced via user_id."""
        try:
            tracking_context = domain_logger.operation_start("get_user_steps", user_id=str(user_id))

            stmt = sa.select(onboarding_steps_table).where(
                onboarding_steps_table.c.user_id == user_id
            ).order_by(onboarding_steps_table.c.updated_at.desc())

            result = await self.session.execute(stmt)
            steps = [OnboardingStepOut.model_validate(row._asdict()) for row in result.fetchall()]

            domain_logger.operation_success(tracking_context, {
                "user_id": str(user_id),
                "step_count": len(steps)
            })

            return steps
        except Exception as e:
            domain_logger.operation_error(tracking_context, str(e), {
                "user_id": str(user_id)
            })
            raise BadRequest(f"Failed to get user steps: {str(e)}")

    @trace_async
    async def get_step(self, user_id: UUID, step: OnboardingStep) -> OnboardingStepOut | None:
        """Get specific onboarding step for user. RLS enforced via user_id."""
        stmt = sa.select(onboarding_steps_table).where(
            sa.and_(
                onboarding_steps_table.c.user_id == user_id,
                sa.text("onboarding_steps.step::text = :step")
            )
        ).params(step=step)

        result = await self.session.execute(stmt)
        row = result.fetchone()
        return OnboardingStepOut.model_validate(row._asdict()) if row else None

    @trace_async
    async def create(self, data: OnboardingStepCreate) -> OnboardingStepOut:
        """Create new onboarding step."""
        step_data = data.model_dump()

        try:
            stmt = sa.insert(onboarding_steps_table).values(**step_data).returning(onboarding_steps_table)
            result = await self.session.execute(stmt)
            row = result.fetchone()
            if row is None:
                raise FailedDependency("Failed to create onboarding step")
            return OnboardingStepOut.model_validate(row._asdict())
        except sa.exc.IntegrityError as e:
            raise BadRequest(f"Step creation failed: {str(e)}")

    @trace_async
    async def upsert_step(
        self, user_id: UUID, step: OnboardingStep, status: OnboardingStatus,
        payload: dict[str, Any] | None = None
    ) -> OnboardingStepOut:
        """Upsert onboarding step (idempotent). RLS enforced via user_id."""
        try:
            tracking_context = domain_logger.operation_start("upsert_step", user_id=str(user_id), step=step, status=status, has_payload=payload is not None)

            # Validate step is in allowed steps
            if step not in STEPS_ORDER:
                raise BadRequest(f"Invalid step: {step}")

            # Validate payload size
            if payload and len(str(payload)) > 16384:  # 16KB limit
                raise BadRequest("Payload too large (max 16KB)")

            stmt = pg_insert(onboarding_steps_table).values(
                user_id=user_id,
                step=step,
                status=status,
                payload=payload,
                updated_at=sa.func.now()
            ).on_conflict_do_update(
                index_elements=['user_id', 'step'],
                set_=dict(
                    status=pg_insert(onboarding_steps_table).excluded.status,
                    payload=pg_insert(onboarding_steps_table).excluded.payload,
                    updated_at=sa.func.now()
                )
            ).returning(onboarding_steps_table)

            result = await self.session.execute(stmt)
            row = result.fetchone()

            if not row:
                raise FailedDependency("Failed to upsert step")

            step_out = OnboardingStepOut.model_validate(row._asdict())

            domain_logger.operation_success(tracking_context, {
                "user_id": str(user_id),
                "step": step,
                "status": status,
                "step_id": str(step_out.id)
            })
            domain_logger.business_event("onboarding_step_upserted", {
                "user_id": str(user_id),
                "step": step,
                "status": status,
                "step_id": str(step_out.id),
                "has_payload": payload is not None
            })

            return step_out
        except sa.exc.IntegrityError as e:
            domain_logger.operation_error(tracking_context, str(e), {
                "user_id": str(user_id),
                "step": step,
                "status": status
            })
            raise BadRequest(f"Step upsert failed: {str(e)}")
        except Exception as e:
            domain_logger.operation_error(tracking_context, str(e), {
                "user_id": str(user_id),
                "step": step,
                "status": status
            })
            raise

    @trace_async
    async def update_step(
        self, user_id: UUID, step: OnboardingStep, data: OnboardingStepUpdate
    ) -> OnboardingStepOut | None:
        """Update existing onboarding step. RLS enforced via user_id."""
        # Validate step is in allowed steps
        if step not in STEPS_ORDER:
            raise BadRequest(f"Invalid step: {step}")

        # Validate payload size
        if data.payload and len(str(data.payload)) > 16384:  # 16KB limit
            raise BadRequest("Payload too large (max 16KB)")

        update_data = data.model_dump(exclude_unset=True)
        update_data['updated_at'] = sa.func.now()

        stmt: sa.Update = (
            sa.update(onboarding_steps_table)
            .where(
                sa.and_(
                    onboarding_steps_table.c.user_id == user_id,
                    sa.text("onboarding_steps.step::text = :step")
                )
            )
            .params(step=step)
            .values(**update_data)
            .returning(onboarding_steps_table)
        )

        result = await self.session.execute(stmt)
        row = result.fetchone()
        return OnboardingStepOut.model_validate(dict(row._mapping)) if row else None

    @trace_async
    async def get_progress(self, user_id: UUID) -> OnboardingProgressOut:
        """Get onboarding progress summary for user. RLS enforced via user_id."""
        steps = await self.get_user_steps(user_id)

        # Create lookup for existing steps
        step_lookup = {step.step: step for step in steps}

        # Calculate progress
        completed_steps: list[OnboardingStep] = []
        skipped_steps: list[OnboardingStep] = []
        current_step: OnboardingStep | None = None

        for step_name in STEPS_ORDER:
            if step_name in step_lookup:
                step_obj = step_lookup[step_name]
                status = step_obj.status
                if status == "completed":
                    completed_steps.append(step_name)
                elif status == "skipped":
                    skipped_steps.append(step_name)
                elif current_step is None and status not in ("completed", "skipped"):
                    current_step = step_name
            else:
                # Missing step - this is the current step
                if current_step is None:
                    current_step = step_name

        # If all steps completed or skipped, current_step should be None
        if len(completed_steps) + len(skipped_steps) == len(STEPS_ORDER):
            current_step = None
        elif current_step is None:
            current_step = STEPS_ORDER[0]  # Default to first step

        # Progress includes both completed and skipped steps
        progress_percent = round(((len(completed_steps) + len(skipped_steps)) / len(STEPS_ORDER)) * 100)

        # Create steps info list with static configuration
        steps_info = self._build_steps_info()

        return OnboardingProgressOut(
            user_id=user_id,
            progress_percent=progress_percent,
            completed_steps=completed_steps,
            skipped_steps=skipped_steps,
            current_step=current_step,
            total_steps=len(STEPS_ORDER),
            steps=steps_info
        )

    @trace_async
    async def delete_step(self, user_id: UUID, step: OnboardingStep) -> None:
        """Delete specific onboarding step. RLS enforced via user_id."""
        stmt: sa.Delete = sa.delete(onboarding_steps_table).where(
            sa.and_(
                onboarding_steps_table.c.user_id == user_id,
                sa.text("onboarding_steps.step::text = :step")
            )
        ).params(step=step)

        result = await self.session.execute(stmt)
        if result.rowcount == 0:  # type: ignore[attr-defined]
            raise NotFound("Onboarding step not found")

    @trace_async
    async def reset_user(self, user_id: UUID) -> bool:
        """Reset all onboarding steps for user (admin/support use). RLS enforced via user_id."""
        try:
            tracking_context = domain_logger.operation_start("reset_user", user_id=str(user_id))

            stmt = sa.delete(onboarding_steps_table).where(
                onboarding_steps_table.c.user_id == user_id
            )

            result = await self.session.execute(stmt)
            reset_successful = bool(result.rowcount and result.rowcount > 0)

            domain_logger.operation_success(tracking_context, {
                "user_id": str(user_id),
                "reset_successful": reset_successful,
                "deleted_steps": result.rowcount or 0
            })
            domain_logger.business_event("onboarding_user_reset", {
                "user_id": str(user_id),
                "reset_successful": reset_successful,
                "deleted_steps": result.rowcount or 0
            })

            return reset_successful
        except Exception as e:
            domain_logger.operation_error(tracking_context, str(e), {
                "user_id": str(user_id)
            })
            raise BadRequest(f"Failed to reset user onboarding: {str(e)}")

    @trace_async
    async def is_completed(self, user_id: UUID) -> bool:
        """Check if user has completed all onboarding steps. RLS enforced via user_id."""
        progress: OnboardingProgressOut = await self.get_progress(user_id)
        return bool(progress.progress_percent == 100)

    @trace_async
    async def get_next_step(self, user_id: UUID) -> OnboardingStep | None:
        """Get the next step user should complete. RLS enforced via user_id."""
        progress: OnboardingProgressOut = await self.get_progress(user_id)
        next_step: OnboardingStep | None = progress.current_step
        return next_step

    def _build_steps_info(self) -> list[StepInfo]:
        """Build static steps configuration."""
        step_config = [
            ("welcome", "Welcome", "Welcome to the app", True, False, False),
            ("consent", "Privacy Consent", "Accept privacy policy and terms", False, True, True),
            ("profile", "Profile Setup", "Set up your profile information", True, False, True),
            ("preferences", "Preferences", "Choose your preferences", True, False, True),
            ("connect_channels", "Connect Channels", "Connect your social media channels", True, False, False),
            ("enable_notification", "Enable Notifications", "Enable push notifications", True, False, False),
            ("done", "Complete", "Complete your onboarding", False, False, False),
        ]

        return [
            StepInfo(
                name=name,  # type: ignore  # We know these are valid OnboardingStep values
                title=title,
                description=description,
                skippable=skippable,
                required=required,
                requires_data=requires_data
            )
            for name, title, description, skippable, required, requires_data in step_config
        ]
