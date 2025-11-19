"""RAG (Retrieval-Augmented Generation) service for AI suggestions.

This service enhances prompts with examples from successful past suggestions
using semantic search over feedback vectors.
"""

import logging
from typing import Any
from uuid import UUID

from flerity_core.domain.ai.embedding_client import EmbeddingClient
from flerity_core.domain.ai.feedback_vector_service import AIFeedbackVectorService
from flerity_core.db.uow import AsyncUnitOfWork

logger = logging.getLogger(__name__)


class RAGService:
    """Service for enhancing prompts with successful examples."""

    def __init__(
        self,
        embedding_client: EmbeddingClient,
        vector_service: AIFeedbackVectorService
    ):
        self.embedding_client = embedding_client
        self.vector_service = vector_service

    async def enhance_prompt_with_examples(
        self,
        context_messages: list[dict[str, Any]],
        tone: str,
        uow: AsyncUnitOfWork,
        limit: int = 3,
        min_quality: float = 0.8
    ) -> str:
        """
        Enhance prompt with successful examples using semantic search.
        
        Flow:
        1. Build context text from messages
        2. Generate embedding for context
        3. Find similar successful suggestions
        4. Format examples for prompt
        
        Args:
            context_messages: Recent conversation messages
            tone: Desired tone (friendly, witty, etc)
            uow: Unit of work with database session
            limit: Maximum number of examples
            min_quality: Minimum quality score for examples
            
        Returns:
            Formatted examples string to append to prompt
        """
        try:
            # Build context text
            context_text = self._build_context_text(context_messages)
            if not context_text:
                logger.debug("No context text for RAG enhancement")
                return ""

            # Generate embedding
            context_embedding = await self.embedding_client.embed(context_text)

            # Find similar suggestions
            similar = await self.vector_service.find_similar_suggestions(
                context_embedding=context_embedding,
                tone=tone,
                min_quality=min_quality,
                limit=limit,
                session=uow.session
            )

            if not similar:
                logger.debug("No similar suggestions found for RAG", extra={
                    "tone": tone,
                    "min_quality": min_quality
                })
                return ""

            # Format examples
            examples = self._format_examples(similar)

            logger.info("RAG enhancement applied", extra={
                "tone": tone,
                "examples_count": len(similar),
                "avg_quality": sum(s["quality_score"] for s in similar) / len(similar)
            })

            return examples

        except Exception as e:
            logger.error("Failed to enhance prompt with RAG", extra={
                "error": str(e),
                "tone": tone
            })
            # Fail gracefully - return empty string
            return ""

    def _build_context_text(self, messages: list[dict[str, Any]]) -> str:
        """Build text from context messages."""
        if not messages:
            return ""

        parts = []
        for msg in messages[-5:]:  # Last 5 messages
            sender = msg.get("sender", "unknown")
            text = msg.get("text", "")
            if text:
                parts.append(f"{sender}: {text}")

        return "\n".join(parts)

    def _format_examples(self, similar: list[dict[str, Any]]) -> str:
        """Format similar suggestions as examples for prompt."""
        if not similar:
            return ""

        examples = [
            f"Example {i+1} (quality: {s['quality_score']:.2f}): {s['suggestion_text']}"
            for i, s in enumerate(similar)
        ]

        return "\n\nSuccessful examples from similar contexts:\n" + "\n".join(examples)
