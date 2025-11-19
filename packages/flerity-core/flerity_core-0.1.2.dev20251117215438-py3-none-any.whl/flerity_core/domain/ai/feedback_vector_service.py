"""AI Feedback Vector service for embeddings and semantic search."""

import json
from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from flerity_core.db.uow import AsyncUnitOfWork
from flerity_core.utils.clock import utcnow
from flerity_core.utils.logging import get_logger

from .embedding_client import EmbeddingClient
from .feedback_repository import AIFeedbackRepository
from .feedback_schemas import FeedbackAction

logger = get_logger(__name__)


class AIFeedbackVectorService:
    """Service for processing feedback embeddings and semantic search."""

    def __init__(self, embedding_client: EmbeddingClient):
        self.embedding_client = embedding_client

    async def process_feedback_event(
        self,
        feedback_id: UUID,
        uow: AsyncUnitOfWork
    ) -> None:
        """
        Process feedback event: generate embeddings and save to vectors table.
        
        Flow:
        1. Fetch feedback from database
        2. Generate embeddings (suggestion + context)
        3. Calculate quality_score
        4. Save to ai_feedback_vectors
        """
        try:
            # Fetch feedback
            feedback_repo = AIFeedbackRepository(uow.session)
            feedback = await feedback_repo.get_by_id(feedback_id)
            
            if not feedback:
                logger.error("Feedback not found", extra={"feedback_id": str(feedback_id)})
                return

            # Generate suggestion embedding
            suggestion_embedding = await self.embedding_client.embed(feedback.suggestion_text)

            # Generate context embedding (if context exists)
            context_embedding = None
            if feedback.context_messages:
                try:
                    context_text = self._build_context_text(feedback.context_messages)
                    if context_text:
                        context_embedding = await self.embedding_client.embed(context_text)
                except Exception as e:
                    logger.warning("Failed to generate context embedding", extra={
                        "feedback_id": str(feedback_id),
                        "error": str(e)
                    })

            # Calculate quality score
            quality_score = self._calculate_quality_score(feedback.action, feedback.edited_text, feedback.suggestion_text)

            # Save to vectors table
            await self._save_vector(
                uow.session,
                feedback_id=feedback_id,
                suggestion_embedding=suggestion_embedding,
                context_embedding=context_embedding,
                tone=feedback.tone,
                action=feedback.action.value,
                quality_score=quality_score
            )

            await uow.commit()

            logger.info("Feedback vector processed", extra={
                "feedback_id": str(feedback_id),
                "quality_score": quality_score,
                "has_context": context_embedding is not None
            })

        except Exception as e:
            logger.error("Failed to process feedback event", extra={
                "feedback_id": str(feedback_id),
                "error": str(e)
            })
            await uow.rollback()
            raise

    async def find_similar_suggestions(
        self,
        context_embedding: list[float],
        tone: str,
        min_quality: float = 0.7,
        limit: int = 10,
        session: AsyncSession | None = None
    ) -> list[dict[str, Any]]:
        """
        Find similar suggestions using semantic search.
        
        Args:
            context_embedding: Embedding of the current context
            tone: Desired tone (friendly, witty, etc)
            min_quality: Minimum quality score
            limit: Maximum number of results
            session: Database session
            
        Returns:
            List of similar suggestions with metadata
        """
        if not session:
            raise ValueError("Session is required")

        # Convert embedding to pgvector format
        embedding_str = "[" + ",".join(str(x) for x in context_embedding) + "]"

        stmt = text("""
            SELECT 
                f.id,
                f.suggestion_text,
                f.tone,
                fv.quality_score,
                fv.context_embedding <=> :embedding::vector as distance
            FROM ai_feedback_vectors fv
            JOIN ai_feedback f ON f.id = fv.feedback_id
            WHERE fv.quality_score >= :min_quality
              AND f.tone = :tone
              AND fv.context_embedding IS NOT NULL
            ORDER BY fv.context_embedding <=> :embedding::vector
            LIMIT :limit
        """)

        result = await session.execute(stmt, {
            'embedding': embedding_str,
            'min_quality': min_quality,
            'tone': tone,
            'limit': limit
        })

        rows = result.fetchall()

        return [
            {
                'id': str(row.id),
                'suggestion_text': row.suggestion_text,
                'tone': row.tone,
                'quality_score': float(row.quality_score),
                'distance': float(row.distance),
                'similarity': 1.0 - float(row.distance)  # Convert distance to similarity
            }
            for row in rows
        ]

    def _calculate_quality_score(self, action: FeedbackAction, edited_text: str | None, original_text: str | None) -> float:
        """
        Calculate quality score based on action.
        
        Scores:
        - like: 1.0 (user approved)
        - copy: 0.9 (user used exactly)
        - edit: 0.5 * similarity (user adjusted)
        - dislike: 0.0 (user rejected)
        - ignore: 0.0 (user ignored)
        """
        if action == FeedbackAction.LIKE:
            return 1.0
        elif action == FeedbackAction.COPY:
            return 0.9
        elif action == FeedbackAction.EDIT:
            # Calculate similarity between edited and original
            if edited_text and original_text:
                similarity = self._calculate_text_similarity(edited_text, original_text)
                return 0.5 * similarity
            return 0.5
        else:  # dislike or ignore
            return 0.0

    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple text similarity (Jaccard similarity)."""
        if not text1 or not text2:
            return 0.0

        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = len(words1 & words2)
        union = len(words1 | words2)

        return intersection / union if union > 0 else 0.0

    def _build_context_text(self, context_messages: dict[str, Any]) -> str:
        """Build text from context messages for embedding."""
        if not context_messages:
            return ""

        messages = []
        for msg in context_messages:
            sender = msg.get("sender", "unknown")
            text = msg.get("text", "")
            if text:
                messages.append(f"{sender}: {text}")

        return "\n".join(messages)

    async def _save_vector(
        self,
        session: AsyncSession,
        feedback_id: UUID,
        suggestion_embedding: list[float],
        context_embedding: list[float] | None,
        tone: str | None,
        action: str,
        quality_score: float
    ) -> None:
        """Save vector to database."""
        # Convert embeddings to pgvector format
        suggestion_vec = "[" + ",".join(str(x) for x in suggestion_embedding) + "]"
        context_vec = "[" + ",".join(str(x) for x in context_embedding) + "]" if context_embedding else None

        stmt = text("""
            INSERT INTO ai_feedback_vectors (
                feedback_id, suggestion_embedding, context_embedding,
                tone, action, quality_score, created_at
            ) VALUES (
                :feedback_id, :suggestion_embedding, :context_embedding,
                :tone, :action, :quality_score, :created_at
            )
            ON CONFLICT (feedback_id) DO UPDATE SET
                suggestion_embedding = EXCLUDED.suggestion_embedding,
                context_embedding = EXCLUDED.context_embedding,
                tone = EXCLUDED.tone,
                action = EXCLUDED.action,
                quality_score = EXCLUDED.quality_score
        """)

        await session.execute(stmt, {
            'feedback_id': feedback_id,
            'suggestion_embedding': suggestion_vec,
            'context_embedding': context_vec,
            'tone': tone,
            'action': action,
            'quality_score': quality_score,
            'created_at': utcnow()
        })
