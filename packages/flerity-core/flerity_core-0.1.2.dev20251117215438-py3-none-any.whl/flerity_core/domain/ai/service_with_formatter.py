"""Updated AI service using robust prompt formatter."""

import os
import re
from typing import Any

from flerity_core.src.flerity_core.db.uow import UnitOfWork
from flerity_core.src.flerity_core.domain.ai.prompts_repository import AIPromptsRepository
from flerity_core.src.flerity_core.domain.ai.schemas import ThreadContext, SuggestionRequest, IcebreakerRequest
from flerity_core.src.flerity_core.domain.ai.prompt_formatter import prompt_formatter


class AIServiceWithFormatter:
    """AI service with robust prompt formatting."""

    def __init__(self, prompts_repo: AIPromptsRepository, moderation=None, rag_service=None):
        self.prompts_repo = prompts_repo
        self.moderation = moderation
        self.rag_service = rag_service

    async def _build_suggestion_prompt(
        self,
        context: ThreadContext,
        request: SuggestionRequest,
        variant: Any = None,
        uow: UnitOfWork | None = None
    ) -> str:
        """Build suggestion prompt using database template with robust variable replacement."""
        
        # Get prompt template from database
        prompt_template = await self.prompts_repo.get_prompt(
            kind="suggestion",
            context_type="general",
            tone=request.tone,
            language=getattr(context, 'language', 'pt-BR'),
            country=getattr(context, 'country', 'BR'),
            gender=getattr(context, 'gender', None)
        )
        
        # Fallback to default if no template found
        if not prompt_template:
            prompt_template = await self.prompts_repo.get_fallback_prompt(
                kind="suggestion",
                language=getattr(context, 'language', 'pt-BR')
            )
        
        if not prompt_template:
            # Ultimate fallback - use hardcoded template
            return await self._build_hardcoded_suggestion_prompt(context, request, variant, uow)
        
        # Prepare context data
        messages_context = "\n".join([
            f"{msg.get('sender', 'user')}: {msg.get('text', '')}"
            for msg in context.recent_messages[-request.last_n_messages:]
        ])

        # Sanitize hint and build hint section
        hint_section = await self._build_hint_section(request, getattr(context, 'language', 'pt-BR'))
        
        # Get tone description
        tone_description = self._get_tone_description(request.tone, getattr(context, 'language', 'pt-BR'))

        # RAG Enhancement
        rag_examples = await self._get_rag_examples(context, request, uow)

        # Build variables dictionary
        variables = prompt_formatter.build_suggestion_variables(
            messages_context=messages_context,
            max_suggestions=request.max_suggestions,
            tone_description=tone_description,
            hint_section=hint_section,
            rag_examples=rag_examples
        )

        # Format template with variables
        return prompt_formatter.format_template(prompt_template.template, variables)

    async def _build_icebreaker_prompt(
        self,
        context: ThreadContext,
        request: IcebreakerRequest
    ) -> str:
        """Build icebreaker prompt using database template with robust variable replacement."""
        
        # Get prompt template from database
        prompt_template = await self.prompts_repo.get_prompt(
            kind="icebreaker",
            context_type="general",
            tone=request.style,  # Note: icebreaker uses 'style' field but maps to 'tone' in DB
            language=getattr(context, 'language', 'pt-BR'),
            country=getattr(context, 'country', 'BR'),
            gender=getattr(context, 'gender', None)
        )
        
        # Fallback to default if no template found
        if not prompt_template:
            prompt_template = await self.prompts_repo.get_fallback_prompt(
                kind="icebreaker",
                language=getattr(context, 'language', 'pt-BR')
            )
        
        if not prompt_template:
            # Ultimate fallback - use hardcoded template
            return await self._build_hardcoded_icebreaker_prompt(context, request)

        # Get tone description
        tone_description = self._get_tone_description(request.style, getattr(context, 'language', 'pt-BR'))

        # Build context section
        context_section = self._build_context_section(request, getattr(context, 'language', 'pt-BR'))

        # Build variables dictionary
        variables = prompt_formatter.build_icebreaker_variables(
            max_suggestions=request.max_suggestions,
            tone_description=tone_description,
            context_section=context_section
        )

        # Format template with variables
        return prompt_formatter.format_template(prompt_template.template, variables)

    async def _build_hint_section(self, request: SuggestionRequest, language: str) -> str:
        """Build hint section with sanitization."""
        if not request.hint:
            return ""
        
        sanitized_hint = ""
        if self.moderation:
            try:
                moderation_result = await self.moderation.moderate_input(request.hint, {})
                sanitized_hint = moderation_result.sanitized_text
            except Exception:
                # Fallback to basic sanitization
                hint_text = request.hint
                hint_text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', hint_text)
                hint_text = re.sub(r'\b\d{2,3}[-.\s]?\d{4,5}[-.\s]?\d{4}\b', '[PHONE]', hint_text)
                sanitized_hint = hint_text
        else:
            sanitized_hint = request.hint
        
        # Format hint section based on language
        hint_labels = {
            'pt-BR': f"- Dica adicional: {sanitized_hint}",
            'en-US': f"- Additional hint: {sanitized_hint}",
            'es-ES': f"- Pista adicional: {sanitized_hint}"
        }
        return hint_labels.get(language, hint_labels['pt-BR'])

    def _get_tone_description(self, tone: str, language: str) -> str:
        """Get localized tone description."""
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
        
        tone_map = tone_maps.get(language, tone_maps['pt-BR'])
        return tone_map.get(tone, "amigável")

    def _build_context_section(self, request: IcebreakerRequest, language: str) -> str:
        """Build context section for icebreakers."""
        context_parts = []
        
        if request.bio_text:
            bio_labels = {
                'pt-BR': "Bio da pessoa:",
                'en-US': "Person's bio:",
                'es-ES': "Bio de la persona:"
            }
            bio_label = bio_labels.get(language, "Bio da pessoa:")
            context_parts.append(f"{bio_label}\n{request.bio_text}")
        
        if request.image_url:
            image_labels = {
                'pt-BR': "A pessoa compartilhou uma foto de perfil. Use detalhes visuais para criar icebreakers personalizados.",
                'en-US': "The person shared a profile photo. Use visual details to create personalized icebreakers.",
                'es-ES': "La persona compartió una foto de perfil. Usa detalles visuales para crear icebreakers personalizados."
            }
            image_label = image_labels.get(language, image_labels['pt-BR'])
            context_parts.append(image_label)
        
        if not context_parts:
            return ""
        
        context_instructions = {
            'pt-BR': "\n\nUse essas informações para criar icebreakers personalizados e relevantes.",
            'en-US': "\n\nUse this information to create personalized and relevant icebreakers.",
            'es-ES': "\n\nUsa esta información para crear icebreakers personalizados y relevantes."
        }
        instruction = context_instructions.get(language, context_instructions['pt-BR'])
        return "\n\n" + "\n\n".join(context_parts) + instruction

    async def _get_rag_examples(self, context: ThreadContext, request: SuggestionRequest, uow: UnitOfWork | None) -> str:
        """Get RAG examples if enabled."""
        if not (self.rag_service and uow and os.getenv("ENABLE_RAG_ENHANCEMENT", "false").lower() == "true"):
            return ""
        
        try:
            return await self.rag_service.enhance_prompt_with_examples(
                context_messages=context.recent_messages,
                tone=request.tone,
                uow=uow,
                limit=3,
                min_quality=0.8
            )
        except Exception:
            return ""

    # Keep existing hardcoded fallback methods...
    async def _build_hardcoded_suggestion_prompt(self, context, request, variant=None, uow=None):
        """Fallback to original hardcoded implementation."""
        # Original implementation as safety net
        pass

    async def _build_hardcoded_icebreaker_prompt(self, context, request):
        """Fallback to original hardcoded implementation.""" 
        # Original implementation as safety net
        pass
