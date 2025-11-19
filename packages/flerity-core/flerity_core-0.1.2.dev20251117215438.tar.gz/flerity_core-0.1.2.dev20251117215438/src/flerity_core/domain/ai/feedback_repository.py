"""AI Feedback repository."""

import json
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from flerity_core.utils.clock import utcnow
from flerity_core.utils.logging import get_logger

from .feedback_schemas import AIFeedbackOut, FeedbackAction, FeedbackStatsOut

logger = get_logger(__name__)


class AIFeedbackRepository:
    """Repository for AI feedback with RLS support."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        user_id: UUID,
        generation_id: UUID | None,
        thread_id: UUID | None,
        suggestion_text: str,
        suggestion_index: int | None,
        action: FeedbackAction,
        edited_text: str | None,
        context_messages: dict[str, Any] | None,
        prompt_hash: str | None,
        tone: str | None,
        user_locale: str,
        user_gender: str | None,
        user_birth_year: int | None,
        user_country: str | None,
        user_state: str | None,
        user_city: str | None,
        device_id: str | None,
        app_version: str | None,
    ) -> AIFeedbackOut:
        """Create feedback record."""
        stmt = text("""
            INSERT INTO ai_feedback (
                user_id, generation_id, thread_id,
                suggestion_text, suggestion_index, action, edited_text,
                context_messages, prompt_hash, tone,
                user_locale, user_gender, user_birth_year,
                user_country, user_state, user_city,
                device_id, app_version, created_at
            ) VALUES (
                :user_id, :generation_id, :thread_id,
                :suggestion_text, :suggestion_index, :action, :edited_text,
                :context_messages, :prompt_hash, :tone,
                :user_locale, :user_gender, :user_birth_year,
                :user_country, :user_state, :user_city,
                :device_id, :app_version, :created_at
            )
            RETURNING *
        """)

        result = await self.session.execute(stmt, {
            'user_id': user_id,
            'generation_id': generation_id,
            'thread_id': thread_id,
            'suggestion_text': suggestion_text,
            'suggestion_index': suggestion_index,
            'action': action.value,
            'edited_text': edited_text,
            'context_messages': json.dumps(context_messages) if context_messages else None,
            'prompt_hash': prompt_hash,
            'tone': tone,
            'user_locale': user_locale,
            'user_gender': user_gender,
            'user_birth_year': user_birth_year,
            'user_country': user_country,
            'user_state': user_state,
            'user_city': user_city,
            'device_id': device_id,
            'app_version': app_version,
            'created_at': utcnow()
        })

        row = result.fetchone()
        if not row:
            raise Exception("Failed to create feedback")

        logger.info("Feedback created", extra={
            "feedback_id": str(row.id),
            "user_id": str(user_id),
            "action": action.value,
            "tone": tone
        })

        return self._row_to_feedback(row)

    async def get_by_id(self, feedback_id: UUID) -> AIFeedbackOut | None:
        """Get feedback by ID (respects RLS)."""
        stmt = text("SELECT * FROM ai_feedback WHERE id = :feedback_id")
        result = await self.session.execute(stmt, {'feedback_id': feedback_id})
        row = result.fetchone()

        if row:
            return self._row_to_feedback(row)
        return None

    async def get_user_stats(self, user_id: UUID) -> FeedbackStatsOut:
        """Get user feedback statistics."""
        stmt = text("""
            SELECT 
                COUNT(*) as total_feedbacks,
                SUM(CASE WHEN action = 'like' THEN 1 ELSE 0 END) as likes,
                SUM(CASE WHEN action = 'dislike' THEN 1 ELSE 0 END) as dislikes,
                SUM(CASE WHEN action = 'copy' THEN 1 ELSE 0 END) as copies,
                SUM(CASE WHEN action = 'edit' THEN 1 ELSE 0 END) as edits,
                SUM(CASE WHEN action = 'ignore' THEN 1 ELSE 0 END) as ignores,
                MODE() WITHIN GROUP (ORDER BY tone) as favorite_tone
            FROM ai_feedback
            WHERE user_id = :user_id
        """)

        result = await self.session.execute(stmt, {'user_id': user_id})
        row = result.fetchone()

        if not row:
            return FeedbackStatsOut(
                total_feedbacks=0,
                likes=0,
                dislikes=0,
                copies=0,
                edits=0,
                ignores=0,
                favorite_tone=None,
                avg_quality_score=None
            )

        # Calculate avg quality score
        quality_stmt = text("""
            SELECT AVG(
                CASE 
                    WHEN action = 'like' THEN 1.0
                    WHEN action = 'copy' THEN 0.9
                    WHEN action = 'edit' THEN 0.5
                    ELSE 0.0
                END
            ) as avg_quality
            FROM ai_feedback
            WHERE user_id = :user_id
        """)
        quality_result = await self.session.execute(quality_stmt, {'user_id': user_id})
        quality_row = quality_result.fetchone()

        return FeedbackStatsOut(
            total_feedbacks=row.total_feedbacks or 0,
            likes=row.likes or 0,
            dislikes=row.dislikes or 0,
            copies=row.copies or 0,
            edits=row.edits or 0,
            ignores=row.ignores or 0,
            favorite_tone=row.favorite_tone,
            avg_quality_score=float(quality_row.avg_quality) if quality_row and quality_row.avg_quality else None
        )

    async def list_for_training(
        self,
        min_quality_score: float = 0.7,
        days: int = 90,
        limit: int = 10000,
        locale: str | None = None
    ) -> list[dict[str, Any]]:
        """List feedbacks for training (admin only, no RLS)."""
        conditions = [
            "created_at > :cutoff_date"
        ]
        params: dict[str, Any] = {
            'cutoff_date': utcnow() - timedelta(days=days),
            'limit': limit
        }

        if locale:
            conditions.append("user_locale = :locale")
            params['locale'] = locale

        # Calculate quality score in query
        quality_case = """
            CASE 
                WHEN action = 'like' THEN 1.0
                WHEN action = 'copy' THEN 0.9
                WHEN action = 'edit' THEN 0.5
                ELSE 0.0
            END
        """

        where_clause = " AND ".join(conditions)
        stmt = text(f"""
            SELECT 
                id,
                suggestion_text,
                context_messages,
                tone,
                action,
                user_locale,
                user_gender,
                user_birth_year,
                user_country,
                user_state,
                {quality_case} as quality_score,
                prompt_hash,
                created_at
            FROM ai_feedback
            WHERE {where_clause}
              AND {quality_case} >= :min_quality
            ORDER BY created_at DESC
            LIMIT :limit
        """)

        params['min_quality'] = min_quality_score

        result = await self.session.execute(stmt, params)
        rows = result.fetchall()

        return [
            {
                'id': str(row.id),
                'suggestion_text': row.suggestion_text,
                'context_messages': json.loads(row.context_messages) if row.context_messages else None,
                'tone': row.tone,
                'action': row.action,
                'user_locale': row.user_locale,
                'user_gender': row.user_gender,
                'user_birth_year': row.user_birth_year,
                'user_country': row.user_country,
                'user_state': row.user_state,
                'quality_score': float(row.quality_score),
                'prompt_hash': row.prompt_hash,
                'created_at': row.created_at.isoformat()
            }
            for row in rows
        ]

    def _row_to_feedback(self, row) -> AIFeedbackOut:
        """Convert database row to AIFeedbackOut."""
        return AIFeedbackOut(
            id=row.id,
            user_id=row.user_id,
            thread_id=row.thread_id,
            generation_id=row.generation_id,
            suggestion_text=row.suggestion_text,
            suggestion_index=row.suggestion_index,
            action=FeedbackAction(row.action),
            edited_text=row.edited_text,
            tone=row.tone,
            user_locale=row.user_locale,
            user_gender=row.user_gender,
            user_birth_year=row.user_birth_year,
            user_country=row.user_country,
            user_state=row.user_state,
            user_city=row.user_city,
            created_at=row.created_at,
            device_id=row.device_id,
            app_version=row.app_version
        )
