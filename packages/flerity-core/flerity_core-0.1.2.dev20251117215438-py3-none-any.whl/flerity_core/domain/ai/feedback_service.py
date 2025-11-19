"""AI Feedback service."""

from typing import TYPE_CHECKING, Any
from uuid import UUID

from flerity_core.db.uow import AsyncUnitOfWork
from flerity_core.utils.errors import BadRequest, NotFoundError
from flerity_core.utils.logging import get_logger

from .feedback_repository import AIFeedbackRepository
from .feedback_schemas import AIFeedbackCreate, AIFeedbackOut, FeedbackStatsOut
from .moderation import ModerationService
from .repository import AIGenerationRepository
from .schemas import UserLocale

logger = get_logger(__name__)


class AIFeedbackService:
    """Service for AI feedback collection and processing."""

    def __init__(self, moderation_service: ModerationService):
        self.moderation = moderation_service

    async def submit_feedback(
        self,
        user_id: UUID,
        request: AIFeedbackCreate,
        uow: AsyncUnitOfWork,
        user_locale: str = "pt-BR",
        user_gender: str | None = None,
        user_birth_year: int | None = None,
        user_country: str | None = None,
        user_state: str | None = None,
        user_city: str | None = None,
        device_id: str | None = None,
        app_version: str | None = None
    ) -> AIFeedbackOut:
        """
        Submit user feedback on AI suggestion.
        
        Flow:
        1. Fetch generation context (bio/image) if generation_id provided
        2. Apply moderation (PII filtering)
        3. Save feedback to database
        4. Enqueue outbox event for async processing
        5. Return feedback
        """
        from ...utils.request_tracking import RequestTracker
        from ...utils.domain_logger import get_domain_logger
        
        domain_logger = get_domain_logger(__name__)
        
        with RequestTracker(user_id=user_id, operation="submit_feedback") as tracker:
            try:
                tracking_context = domain_logger.operation_start(
                    operation="submit_feedback",
                    context={
                        "user_id": str(user_id),
                        "action": request.action.value,
                        "generation_id": str(request.generation_id) if request.generation_id else None
                    }
                )

                # Fetch generation context if available
                context_messages = None
                prompt_hash = None
                
                if request.generation_id:
                    gen_repo = AIGenerationRepository(uow.session)
                    generation = await gen_repo.get_by_id(request.generation_id)
                    
                    if generation:
                        params = generation['params']
                        prompt_hash = generation['prompt_hash']
                        
                        # Build context from generation params
                        context_parts = []
                        
                        # Add bio if present
                        if params.get('bio_text'):
                            context_parts.append({
                                "sender": "system",
                                "text": f"Bio: {params['bio_text']}"
                            })
                        
                        # Add image info (but not base64 data - too large for embedding)
                        if params.get('image_url'):
                            context_parts.append({
                                "sender": "system", 
                                "text": "Image: [profile photo provided]"
                            })
                        
                        if context_parts:
                            context_messages = context_parts
                
                # Override with context from request if provided
                if request.context.get("last_messages"):
                    context_messages = request.context.get("last_messages")
                
                # Get tone and thread_id from request context
                tone = request.context.get("tone")
                thread_id = request.context.get("thread_id")
                
                # Apply moderation to suggestion text
                locale = UserLocale(language=user_locale, country=user_country or "BR")
                try:
                    moderation_result = await self.moderation.moderate_input(
                        request.suggestion_text,
                        locale
                    )
                    sanitized_text = moderation_result.sanitized_text
                except Exception as e:
                    logger.warning("Moderation failed, using original text", extra={
                        "error": str(e),
                        "user_id": str(user_id)
                    })
                    sanitized_text = request.suggestion_text

                # Apply moderation to edited text if present
                sanitized_edited_text = None
                if request.edited_text:
                    try:
                        edited_moderation = await self.moderation.moderate_input(
                            request.edited_text,
                            locale
                        )
                        sanitized_edited_text = edited_moderation.sanitized_text
                    except Exception as e:
                        logger.warning("Moderation of edited text failed", extra={
                            "error": str(e),
                            "user_id": str(user_id)
                        })
                        sanitized_edited_text = request.edited_text

                # Save feedback
                feedback_repo = AIFeedbackRepository(uow.session)
                feedback = await feedback_repo.create(
                    user_id=user_id,
                    generation_id=request.generation_id,
                    thread_id=UUID(thread_id) if thread_id else None,
                    suggestion_text=sanitized_text,
                    suggestion_index=request.suggestion_index,
                    action=request.action,
                    edited_text=sanitized_edited_text,
                    context_messages=context_messages,
                    prompt_hash=prompt_hash,
                    tone=tone,
                    user_locale=user_locale,
                    user_gender=user_gender,
                    user_birth_year=user_birth_year,
                    user_country=user_country,
                    user_state=user_state,
                    user_city=user_city,
                    device_id=device_id,
                    app_version=app_version
                )

                # Enqueue event for async processing (embeddings generation)
                from flerity_core.outbox.dispatcher import enqueue_outbox
                await enqueue_outbox(
                    session=uow.session,
                    topic="ai.feedback.created",
                    payload={
                        "feedback_id": str(feedback.id),
                        "user_id": str(user_id),
                        "action": request.action.value,
                        "tone": tone
                    }
                )
                
                # Commit transaction (includes feedback + outbox event)
                await uow.commit()
                
                tracker.log_success(result_id=str(feedback.id))
                tracking_context = domain_logger.operation_start("submit_feedback")

                domain_logger.operation_success(tracking_context,
                    context={
                        "user_id": str(user_id),
                        "feedback_id": str(feedback.id),
                        "action": request.action.value,
                        "moderated": sanitized_text != request.suggestion_text
                    }
                )
                domain_logger.business_event(
                    event="ai_feedback_submitted",
                    context={
                        "user_id": str(user_id),
                        "feedback_id": str(feedback.id),
                        "action": request.action.value,
                        "generation_id": str(request.generation_id) if request.generation_id else None
                    }
                )
                
                logger.info("Feedback saved and event enqueued", extra={
                    "feedback_id": str(feedback.id),
                    "action": request.action.value
                })

                return feedback
                
            except Exception as e:
                error_id = tracker.log_error(e, context={
                    "user_id": str(user_id),
                    "action": request.action.value
                })
                tracking_context = domain_logger.operation_start("submit_feedback")

                domain_logger.operation_error(tracking_context,
                    error=e,
                    context={"user_id": str(user_id), "error_id": error_id}
                )
                logger.error(f"Failed to submit feedback (Error ID: {error_id})", extra={
                    "user_id": str(user_id), "error": str(e), "error_id": error_id
                })
                raise BadRequest(f"Failed to submit feedback (Error ID: {error_id})")

    async def get_user_stats(
        self,
        user_id: UUID,
        uow: AsyncUnitOfWork
    ) -> FeedbackStatsOut:
        """Get user feedback statistics."""
        from ...utils.request_tracking import RequestTracker
        from ...utils.domain_logger import get_domain_logger
        
        domain_logger = get_domain_logger(__name__)
        
        with RequestTracker(user_id=user_id, operation="get_user_stats") as tracker:
            try:
                tracking_context = domain_logger.operation_start(
                    operation="get_user_stats",
                    context={"user_id": str(user_id)}
                )

                feedback_repo = AIFeedbackRepository(uow.session)
                stats = await feedback_repo.get_user_stats(user_id)
                
                tracker.log_success(result_id=str(user_id))
                tracking_context = domain_logger.operation_start("get_user_stats")

                domain_logger.operation_success(tracking_context,
                    context={
                        "user_id": str(user_id),
                        "total_feedbacks": stats.total_feedbacks,
                        "satisfaction_rate": stats.satisfaction_rate
                    }
                )
                
                logger.info("User stats retrieved", extra={
                    "user_id": str(user_id),
                    "total_feedbacks": stats.total_feedbacks
                })
                
                return stats
                
            except Exception as e:
                error_id = tracker.log_error(e, context={"user_id": str(user_id)})
                tracking_context = domain_logger.operation_start("get_user_stats")

                domain_logger.operation_error(tracking_context,
                    error=e,
                    context={"user_id": str(user_id), "error_id": error_id}
                )
                logger.error(f"Failed to get user stats (Error ID: {error_id})", extra={
                    "user_id": str(user_id), "error": str(e), "error_id": error_id
                })
                raise BadRequest(f"Failed to get user stats (Error ID: {error_id})")
