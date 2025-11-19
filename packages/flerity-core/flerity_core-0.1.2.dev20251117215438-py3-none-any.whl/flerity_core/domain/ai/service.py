"""AI service with Phase 4 optimizations."""

import hashlib
import os
from typing import Any
from uuid import UUID

from flerity_core.db.uow import UnitOfWork
from flerity_core.utils.clock import utcnow
from flerity_core.utils.logging import get_logger
from flerity_core.utils.request_tracking import RequestTracker
from flerity_core.utils.domain_logger import get_domain_logger

# Use relative imports
from .schemas import (
    AIProviderTimeout,
    IcebreakerRequest,
    IcebreakerResponse,
    JobCreatedResponse,
    SuggestionItem,
    SuggestionRequest,
    SuggestionResponse,
    ThreadContext,
)

logger = get_logger(__name__)
domain_logger = get_domain_logger(__name__)


class PromptNotFoundError(Exception):
    """Raised when AI prompt template is not found in database."""
    
    def __init__(self, kind: str, tone: str, language: str):
        self.kind = kind
        self.tone = tone
        self.language = language
        super().__init__(f"Prompt not found: kind={kind}, tone={tone}, language={language}")


class AIService:
    """AI service with Phase 4 optimizations."""

    def __init__(
        self,
        bedrock_client: Any,
        rate_limiter: Any | None = None,
        moderation_service: Any | None = None,
        cache: Any | None = None,
        deduplication: Any | None = None,
        ab_testing: Any | None = None,
        metrics: Any | None = None,
        prompts_repo: Any | None = None,
        rag_service: Any | None = None
    ):
        self.bedrock_client = bedrock_client
        self.rate_limiter = rate_limiter
        self.moderation = moderation_service
        self.cache = cache
        self.deduplication = deduplication
        self.ab_testing = ab_testing
        self.metrics = metrics
        self.prompts_repo = prompts_repo
        self.rag_service = rag_service
        self.circuit_breaker = None

    async def generate_suggestions_sync(
        self,
        thread_id: UUID,
        request: SuggestionRequest,
        context: ThreadContext,
        uow: UnitOfWork | None = None
    ) -> SuggestionResponse | JobCreatedResponse:
        """Generate suggestions - simplified implementation."""
        
        user_id = getattr(context, 'user_id', None)
        with RequestTracker(user_id=user_id, operation="generate_suggestions_sync") as tracker:
            tracking_context = None
            try:
                tracking_context = tracking_context = domain_logger.operation_start("generate_suggestions_sync",
                        thread_id=str(thread_id),
                        user_id=str(user_id) if user_id else None,
                        tone=request.tone,
                        max_suggestions=request.max_suggestions,
                        last_n_messages=request.last_n_messages
                    )

                logger.info("Starting suggestions generation", extra={"thread_id": str(thread_id)})

                # Build prompt
                prompt = await self._build_suggestion_prompt(context, request, None, uow)

                # Generate response
                timeout_ms = int(os.getenv("AI_SYNC_TIMEOUT_MS", "30000"))
                timeout_seconds = timeout_ms / 1000.0
                response = await self.bedrock_client.generate_text(prompt, timeout=timeout_seconds)

                # Parse suggestions
                suggestions = self._parse_suggestions(response)

                # Create audit record
                generation_id = None
                if uow:
                    import hashlib
                    generation_id = await self._create_audit_record(
                        thread_id=thread_id,
                        kind="suggestion",
                        prompt_hash=hashlib.sha256(prompt.encode()).hexdigest(),
                        params=request.model_dump(),
                        output={"suggestions": [s.model_dump() for s in suggestions]},
                        uow=uow
                    )

                result = SuggestionResponse(
                    thread_id=thread_id,
                    suggestions=suggestions,
                    generated_at=utcnow(),
                    based_on={"last_n_messages": request.last_n_messages},
                    generation_id=generation_id
                )

                tracker.log_success(result_id=str(generation_id) if generation_id else None)
                domain_logger.operation_success(tracking_context,
                        result_id=str(generation_id) if generation_id else None,
                        thread_id=str(thread_id),
                        generation_id=str(generation_id) if generation_id else None,
                        suggestions_count=len(suggestions)
                    )
                domain_logger.business_event(
                    event="ai_suggestions_generated",
                    context={
                        "thread_id": str(thread_id),
                        "user_id": str(user_id) if user_id else None,
                        "suggestions_count": len(suggestions),
                        "tone": request.tone
                    }
                )

                return result

            except Exception as e:
                error_id = tracker.log_error(e, context={"thread_id": str(thread_id)})
                if tracking_context:
                    domain_logger.operation_error(tracking_context, error=e,
                            thread_id=str(thread_id),
                            error_id=error_id,
                            tone=request.tone
                        )
                logger.error("Suggestions generation failed", extra={"error": str(e)})
                raise

    async def generate_icebreaker_sync(
        self,
        thread_id: UUID | None,
        request: IcebreakerRequest,
        context: ThreadContext,
        uow: UnitOfWork | None = None
    ) -> IcebreakerResponse | JobCreatedResponse:
        """Generate icebreaker with Phase 4 optimizations."""
        
        user_id = getattr(context, 'user_id', None)
        with RequestTracker(user_id=user_id, operation="generate_icebreaker_sync") as tracker:
            try:
                tracking_context = domain_logger.operation_start("generate_icebreaker_sync", thread_id=str(thread_id) if thread_id else None, user_id=str(user_id) if user_id else None, tone=request.tone, max_suggestions=request.max_suggestions, has_bio=bool(request.bio_text), has_image=bool(getattr(request, 'image_url', None)))

                logger.info("Starting icebreaker generation", extra={"thread_id": str(thread_id) if thread_id else None})

                # Build prompt
                logger.info("Building icebreaker prompt")
                prompt = await self._build_icebreaker_prompt(context, request)
                logger.info("Prompt built successfully", extra={"prompt_length": len(prompt)})

                # Moderate input
                final_prompt = prompt
                if self.moderation:
                    logger.info("Starting moderation")
                    try:
                        moderation_input = await self.moderation.moderate_input(prompt, {})
                        final_prompt = moderation_input.sanitized_text
                        logger.info("Moderation completed")
                    except Exception as e:
                        logger.warning("Moderation failed", extra={"error": str(e)})
                        pass
                else:
                    logger.info("No moderation configured")

                # Generate response
                logger.info("Calling Bedrock for text generation")
                timeout_ms = int(os.getenv("AI_SYNC_TIMEOUT_MS", "30000"))  # 30 seconds default
                timeout_seconds = timeout_ms / 1000.0
                response = await self.bedrock_client.generate_text(
                    final_prompt,
                    timeout=timeout_seconds,
                    image_url=request.image_url if hasattr(request, 'image_url') else None
                )
                logger.info("Bedrock call successful")

                # Parse icebreakers
                icebreakers = self._parse_icebreakers(response)

                # Moderate output
                if self.moderation:
                    try:
                        for icebreaker in icebreakers:
                            await self.moderation.moderate_output(icebreaker.text, {})
                    except Exception:
                        pass

                # Create audit record
                generation_id = None
                if uow:
                    generation_id = await self._create_audit_record(
                        thread_id=thread_id,
                        kind="icebreaker",
                        prompt_hash=hashlib.sha256(prompt.encode()).hexdigest(),
                        params=request.model_dump(),
                        output={"icebreakers": [i.model_dump() for i in icebreakers]},
                        uow=uow
                    )

                result = IcebreakerResponse(
                    thread_id=thread_id,
                    icebreakers=icebreakers,
                    generated_at=utcnow(),
                    generation_id=generation_id
                )

                tracker.log_success(result_id=str(generation_id) if generation_id else None)
                domain_logger.operation_success({"operation": "generate_icebreaker_sync", "operation_id": "auto", "start_time": 0, **{
                        "thread_id": str(thread_id) if thread_id else None,
                        "generation_id": str(generation_id) if generation_id else None,
                        "icebreakers_count": len(icebreakers)
                    }})
                domain_logger.business_event(
                    event="ai_icebreakers_generated",
                    context={
                        "thread_id": str(thread_id) if thread_id else None,
                        "user_id": str(user_id) if user_id else None,
                        "icebreakers_count": len(icebreakers),
                        "tone": request.tone,
                        "has_bio": bool(request.bio_text)
                    }
                )

                return result

            except AIProviderTimeout as e:
                error_id = tracker.log_error(e, context={"thread_id": str(thread_id) if thread_id else None})
                domain_logger.operation_error({"operation": "generate_icebreaker_sync", "operation_id": "auto", "start_time": 0, **{
                        "thread_id": str(thread_id) if thread_id else None,
                        "error_id": error_id,
                        "error_type": "timeout"
                    }}, error=e)
                raise
            except Exception as e:
                error_id = tracker.log_error(e, context={"thread_id": str(thread_id) if thread_id else None})
                domain_logger.operation_error({"operation": "generate_icebreaker_sync", "operation_id": "auto", "start_time": 0, **{
                        "thread_id": str(thread_id) if thread_id else None,
                        "error_id": error_id,
                        "tone": request.tone
                    }}, error=e)
                raise

    async def _build_suggestion_prompt(
        self,
        context: ThreadContext,
        request: SuggestionRequest,
        variant: Any = None,
        uow: UnitOfWork | None = None
    ) -> str:
        """Build suggestion prompt from database template or hardcoded fallback."""
        domain_logger.info(
            "Building suggestion prompt",
            extra={
                "tone": request.tone,
                "language": context.locale.language,
                "has_hint": bool(request.hint)
            }
        )

        # If no prompts repo, use hardcoded fallback
        if not self.prompts_repo or not uow:
            return await self._build_hardcoded_suggestion_prompt(context, request, variant, uow)
        
        # Get prompt template from database
        template = await self.prompts_repo.get_prompt(
            kind="suggestion",
            context_type="general", 
            tone=request.tone,
            language=context.locale.language,
            country=context.locale.country,
            gender="neutral"
        )
        
        if not template:
            raise PromptNotFoundError(
                kind="suggestion",
                tone=request.tone,
                language=context.locale.language
            )
        
        # Build variables for template
        messages_context = "\n".join([
            f"{msg.get('sender', 'user')}: {msg.get('text', '')}"
            for msg in context.recent_messages
            if msg.get('text') and msg.get('text').strip()
        ])
        
        # Sanitize hint
        sanitized_hint = ""
        if request.hint:
            if self.moderation:
                try:
                    moderation_result = await self.moderation.moderate_input(request.hint, {})
                    sanitized_hint = moderation_result.sanitized_text
                except Exception:
                    import re
                    hint_text = request.hint
                    hint_text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', hint_text)
                    hint_text = re.sub(r'\b\d{2,3}[-.\s]?\d{4,5}[-.\s]?\d{4}\b', '[PHONE]', hint_text)
                    sanitized_hint = hint_text
            else:
                sanitized_hint = request.hint
        
        # Format hint section
        hint_section = ""
        if sanitized_hint:
            hint_labels = {
                'pt-BR': f"- Dica adicional: {sanitized_hint}",
                'en-US': f"- Additional hint: {sanitized_hint}",
                'es-ES': f"- Pista adicional: {sanitized_hint}"
            }
            hint_section = hint_labels.get(context.locale.language, hint_labels['pt-BR'])
        
        # Get tone description
        tone_maps = {
            'pt-BR': {
                "friendly": "amigável e caloroso",
                "witty": "espirituoso e divertido", 
                "empathetic": "empático e compreensivo",
                "professional": "respeitoso e educado"
            },
            'en-US': {
                "friendly": "friendly and warm",
                "witty": "witty and fun",
                "empathetic": "empathetic and understanding", 
                "professional": "respectful and polite"
            },
            'es-ES': {
                "friendly": "amigable y cálido",
                "witty": "ingenioso y divertido",
                "empathetic": "empático y comprensivo",
                "professional": "respetuoso y educado"
            }
        }
        tone_map = tone_maps.get(context.locale.language, tone_maps['pt-BR'])
        tone_description = tone_map.get(request.tone, tone_maps['pt-BR']['friendly'])
        
        # Calculate age range
        age_range = "25-45"  # Default
        if hasattr(context, 'user_birth_year') and context.user_birth_year:
            from datetime import datetime
            current_year = datetime.now().year
            current_age = current_year - context.user_birth_year
            min_age = max(18, current_age - 5)
            max_age = min(65, current_age + 5)
            age_range = f"{min_age}-{max_age}"
        
        # RAG Enhancement
        rag_examples = ""
        if self.rag_service and uow and os.getenv("ENABLE_RAG_ENHANCEMENT", "false").lower() == "true":
            try:
                rag_examples = await self.rag_service.enhance_prompt_with_examples(
                    context_messages=context.recent_messages,
                    tone=request.tone,
                    uow=uow,
                    limit=3,
                    min_quality=0.8
                )
            except Exception as e:
                logger.warning("RAG enhancement failed, continuing without examples")
        
        # Format template with variables
        variables = {
            'messages_context': messages_context,
            'max_suggestions': str(request.max_suggestions),
            'tone_description': tone_description,
            'hint_section': hint_section,
            'rag_examples': rag_examples,
            'age_range': age_range
        }
        
        return template.format(**variables)

    async def _build_icebreaker_prompt(
        self,
        context: ThreadContext,
        request: IcebreakerRequest
    ) -> str:
        """Build icebreaker prompt from database template or hardcoded fallback."""
        domain_logger.info(
            "Building icebreaker prompt",
            extra={
                "tone": request.tone,
                "language": context.locale.language,
                "has_bio": bool(request.bio_text),
                "has_image": bool(getattr(request, 'image_url', None))
            }
        )

        # If no prompts repo, use hardcoded fallback
        if not self.prompts_repo:
            return await self._build_hardcoded_icebreaker_prompt(context, request)
        
        # Get prompt template from database
        template = await self.prompts_repo.get_prompt(
            kind="icebreaker",
            context_type="general",
            tone=request.tone,  # Updated to use tone instead of style
            language=context.locale.language,
            country=context.locale.country,
            gender="neutral"
        )
        
        if not template:
            raise PromptNotFoundError(
                kind="icebreaker", 
                tone=request.tone,
                language=context.locale.language
            )
        
        # Build context section
        context_parts = []
        if request.bio_text:
            bio_labels = {
                'pt-BR': "Bio da pessoa:",
                'en-US': "Person's bio:",
                'es-ES': "Bio de la persona:"
            }
            bio_label = bio_labels.get(context.locale.language, "Bio da pessoa:")
            context_parts.append(f"{bio_label}\n{request.bio_text}")
        
        if hasattr(request, 'image_url') and request.image_url:
            image_labels = {
                'pt-BR': "A pessoa compartilhou uma foto de perfil. Use detalhes visuais para criar icebreakers personalizados.",
                'en-US': "The person shared a profile photo. Use visual details to create personalized icebreakers.",
                'es-ES': "La persona compartió una foto de perfil. Usa detalles visuales para crear icebreakers personalizados."
            }
            image_label = image_labels.get(context.locale.language, image_labels['pt-BR'])
            context_parts.append(image_label)
        
        context_section = ""
        if context_parts:
            context_instructions = {
                'pt-BR': "\n\nUse essas informações para criar icebreakers personalizados e relevantes.",
                'en-US': "\n\nUse this information to create personalized and relevant icebreakers.",
                'es-ES': "\n\nUsa esta información para crear icebreakers personalizados y relevantes."
            }
            instruction = context_instructions.get(context.locale.language, context_instructions['pt-BR'])
            context_section = "\n\n" + "\n\n".join(context_parts) + instruction
        
        # Get tone description
        tone_maps = {
            'pt-BR': {
                "friendly": "amigável e acolhedor",
                "witty": "espirituoso e bem-humorado",
                "empathetic": "empático e interessado", 
                "professional": "respeitoso e educado"
            },
            'en-US': {
                "friendly": "friendly and welcoming",
                "witty": "witty and humorous",
                "empathetic": "empathetic and interested",
                "professional": "respectful and polite"
            },
            'es-ES': {
                "friendly": "amigable y acogedor",
                "witty": "ingenioso y divertido",
                "empathetic": "empático e interesado",
                "professional": "respetuoso y educado"
            }
        }
        tone_map = tone_maps.get(context.locale.language, tone_maps['pt-BR'])
        tone_description = tone_map.get(request.tone, tone_maps['pt-BR']['friendly'])
        
        # Calculate age range
        age_range = "25-45"  # Default
        if hasattr(context, 'user_birth_year') and context.user_birth_year:
            from datetime import datetime
            current_year = datetime.now().year
            current_age = current_year - context.user_birth_year
            min_age = max(18, current_age - 5)
            max_age = min(65, current_age + 5)
            age_range = f"{min_age}-{max_age}"
        
        # Format template with variables
        variables = {
            'max_suggestions': str(request.max_suggestions),
            'tone_description': tone_description,
            'context_section': context_section,
            'age_range': age_range
        }
        
        return template.format(**variables)

    def _parse_suggestions(self, response: str) -> list[SuggestionItem]:
        """Parse LLM response into suggestions."""
        domain_logger.info(
            "Parsing AI response into suggestions",
            extra={"response_length": len(response)}
        )

        import json
        import re

        try:
            # Try to parse as JSON first
            suggestions_list = json.loads(response.strip())
            result = [SuggestionItem(text=str(s)) for s in suggestions_list]
            domain_logger.info(
                "Successfully parsed JSON response",
                extra={"suggestions_count": len(result)}
            )
            return result
        except json.JSONDecodeError:
            # Try to extract JSON array from response
            json_match = re.search(r'\[.*?\]', response, re.DOTALL)
            if json_match:
                try:
                    suggestions_list = json.loads(json_match.group())
                    result = [SuggestionItem(text=str(s)) for s in suggestions_list]
                    domain_logger.info(
                        "Successfully parsed extracted JSON",
                        extra={"suggestions_count": len(result)}
                    )
                    return result
                except json.JSONDecodeError:
                    pass

            # Fallback: split by lines and clean
            lines = [line.strip() for line in response.split('\n') if line.strip()]
            suggestions = []
            for line in lines:
                # Skip JSON markers and empty lines
                if line in ['```json', '```', '[', ']'] or not line:
                    continue

                # Remove numbering, quotes, etc.
                clean_line = re.sub(r'^\d+\.?\s*', '', line)
                clean_line = clean_line.strip('"\'')
                clean_line = clean_line.rstrip(',')  # Remove trailing comma

                if clean_line and len(clean_line) > 5:  # Only meaningful suggestions
                    suggestions.append(SuggestionItem(text=clean_line))
            
            result = suggestions[:5]  # Max 5 suggestions
            domain_logger.info(
                "Used fallback parsing method",
                extra={"suggestions_count": len(result)}
            )
            return result

    def _parse_icebreakers(self, response: str) -> list[SuggestionItem]:
        """Parse LLM response into icebreakers."""
        domain_logger.info(
            "Parsing AI response into icebreakers",
            extra={"response_length": len(response)}
        )
        return self._parse_suggestions(response)  # Same parsing logic

    async def _create_audit_record(
        self,
        thread_id: UUID,
        kind: str,
        prompt_hash: str,
        params: dict[str, Any],
        output: dict[str, Any],
        uow: UnitOfWork
    ) -> UUID | None:
        """Create audit record for AI generation. Returns generation_id."""
        domain_logger.info(
            "Creating AI generation audit record",
            extra={
                "thread_id": str(thread_id),
                "kind": kind,
                "prompt_hash": prompt_hash[:16] + "..."
            }
        )

        try:
            # Import here to avoid circular imports
            from sqlalchemy.ext.asyncio import AsyncSession

            from flerity_core.domain.ai.repository import AIGenerationRepository

            # Type assertion for session
            session = uow.session
            assert isinstance(session, AsyncSession), "Expected AsyncSession"

            repo = AIGenerationRepository(session)
            generation_id = await repo.create_generation_record(
                thread_id=thread_id,
                kind=kind,
                prompt_hash=prompt_hash,
                params=params,
                output=output
            )

            domain_logger.info(
                "AI generation audit record created",
                extra={
                    "generation_id": str(generation_id),
                    "thread_id": str(thread_id),
                    "kind": kind
                }
            )

            return generation_id
        except Exception as e:
            domain_logger.warning(
                "Failed to create AI generation audit record",
                extra={
                    "thread_id": str(thread_id),
                    "kind": kind,
                    "error": str(e)
                }
            )
            # Ignore audit failures for now
            return None

    async def get_job_status(self, job_id: UUID, uow: UnitOfWork) -> dict[str, Any] | None:
        """Get AI job status by ID."""
        with RequestTracker(user_id=None, operation="get_job_status") as tracker:
            try:
                tracking_context = domain_logger.operation_start("get_job_status", job_id=str(job_id))

                from .repository import AIJobsRepository

                repo = AIJobsRepository(uow.session)
                job = await repo.get_by_id(job_id)

                if not job:
                    domain_logger.operation_success({"operation": "get_job_status", "operation_id": "auto", "start_time": 0, **{"job_id": str(job_id), "found": False}})
                    tracker.log_success()
                    return None

                result = {
                    "id": str(job.id),
                    "user_id": str(job.user_id),
                    "thread_id": str(job.thread_id) if job.thread_id else None,
                    "kind": job.kind,
                    "status": job.status,
                    "params": job.params,
                    "result": job.result,
                    "error": job.error,
                    "created_at": job.created_at.isoformat() if job.created_at else None,
                    "updated_at": job.updated_at.isoformat() if job.updated_at else None
                }

                tracker.log_success(result_id=str(job_id))
                domain_logger.operation_success({"operation": "get_job_status", "operation_id": "auto", "start_time": 0, **{
                        "job_id": str(job_id),
                        "found": True,
                        "status": job.status,
                        "kind": job.kind
                    }})

                return result

            except Exception as e:
                error_id = tracker.log_error(e, context={"job_id": str(job_id)})
                domain_logger.operation_error({"operation": "get_job_status", "operation_id": "auto", "start_time": 0, **{"job_id": str(job_id), "error_id": error_id}}, error=e)
                raise

    def _build_topic_guidance(self, topics: list[Any] | None, avoids: list[Any] | None, language: str) -> str:
        """Build topic guidance string for AI prompts."""
        if not topics and not avoids:
            return ""
        
        guidance_parts = []
        
        # Language-specific labels
        labels = {
            'en': {'focus': 'Focus on topics:', 'avoid': 'Avoid topics:'},
            'pt-BR': {'focus': 'Focar em tópicos:', 'avoid': 'Evitar tópicos:'},
            'es-ES': {'focus': 'Enfocarse en temas:', 'avoid': 'Evitar temas:'}
        }
        
        # Default to English if language not supported
        lang_labels = labels.get(language, labels['en'])
        
        if topics:
            topic_names = [topic.name for topic in topics if hasattr(topic, 'name') and topic.name]
            if topic_names:
                guidance_parts.append(f"{lang_labels['focus']} {', '.join(topic_names)}")
        
        if avoids:
            avoid_descriptions = [avoid.description for avoid in avoids if hasattr(avoid, 'description') and avoid.description]
            if avoid_descriptions:
                guidance_parts.append(f"{lang_labels['avoid']} {', '.join(avoid_descriptions)}")
        
        return "\n".join(guidance_parts)

    async def _build_hardcoded_suggestion_prompt(
        self,
        context: ThreadContext,
        request: SuggestionRequest,
        variant: Any = None,
        uow: UnitOfWork | None = None
    ) -> str:
        """Hardcoded fallback for suggestion prompts."""
        
        # Build messages context
        messages_context = "\n".join([
            f"{msg.get('sender', 'user')}: {msg.get('text', '')}"
            for msg in context.recent_messages[-request.last_n_messages:]
            if msg.get('text') and msg.get('text').strip()
        ])
        
        # Build hint section
        hint_section = ""
        if request.hint:
            hint_section = f"\nDica adicional: {request.hint}"
        
        # Get tone description
        tone_descriptions = {
            'casual': 'casual e descontraído',
            'friendly': 'amigável e caloroso',
            'professional': 'profissional e respeitoso',
            'flirty': 'divertido e interessante',
            'confident': 'confiante e direto'
        }
        tone_desc = tone_descriptions.get(request.tone, 'natural e autêntico')
        
        # Build the prompt
        prompt = f"""Você é um assistente especializado em conversas no Instagram e WhatsApp.

Contexto da conversa:
{messages_context}

Tarefa: Gere {request.max_suggestions} sugestões de mensagem com tom {tone_desc}.{hint_section}

Diretrizes:
- Seja natural e autêntico
- Mantenha o contexto da conversa
- Use linguagem adequada para redes sociais
- Evite ser repetitivo
- Seja criativo mas apropriado

Formato de resposta:
1. [primeira sugestão]
2. [segunda sugestão]
3. [terceira sugestão]

Sugestões:"""
        
        return prompt

    async def _build_hardcoded_icebreaker_prompt(
        self,
        context: ThreadContext,
        request: IcebreakerRequest,
        variant: Any = None,
        uow: UnitOfWork | None = None
    ) -> str:
        """Hardcoded fallback for icebreaker prompts."""
        
        # Get tone description
        tone_descriptions = {
            'casual': 'casual e descontraído',
            'friendly': 'amigável e caloroso', 
            'professional': 'profissional e respeitoso',
            'flirty': 'divertido e interessante',
            'confident': 'confiante e direto'
        }
        tone_desc = tone_descriptions.get(request.tone, 'natural e autêntico')
        
        # Build context info
        context_info = ""
        if hasattr(context, 'contact_name') and context.contact_name:
            context_info = f"Nome do contato: {context.contact_name}\n"
        
        # Build bio section (IcebreakerRequest uses bio_text, not hint)
        bio_section = ""
        if request.bio_text:
            bio_section = f"\nInformações do perfil: {request.bio_text}"
        
        # Build the prompt
        prompt = f"""Você é um assistente especializado em criar mensagens iniciais (icebreakers) para Instagram e WhatsApp.

{context_info}Tarefa: Gere {request.max_suggestions} icebreakers com tom {tone_desc}.{bio_section}

Diretrizes:
- Seja natural e interessante
- Crie uma primeira impressão positiva
- Use linguagem adequada para redes sociais
- Seja criativo mas respeitoso
- Evite clichês ou frases muito óbvias

Formato de resposta:
1. [primeiro icebreaker]
2. [segundo icebreaker]
3. [terceiro icebreaker]

Icebreakers:"""
        
        return prompt
