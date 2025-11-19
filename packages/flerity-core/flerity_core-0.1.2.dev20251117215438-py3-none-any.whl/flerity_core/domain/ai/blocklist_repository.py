"""Repository for AI blocklist management."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from flerity_core.utils.logging import get_logger

logger = get_logger(__name__)


class BlocklistRepository:
    """Repository for managing AI content blocklist."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_active_terms(self, language: str) -> list[dict[str, any]]:
        """Get all active blocked terms for a language."""
        from flerity_core.domain.ai.schemas import ai_blocklist_table

        stmt = select(ai_blocklist_table).where(
            ai_blocklist_table.c.language == language,
            ai_blocklist_table.c.is_active
        ).order_by(
            ai_blocklist_table.c.severity.desc(),
            ai_blocklist_table.c.term
        )

        result = await self.session.execute(stmt)
        rows = result.fetchall()

        return [
            {
                "id": str(row.id),
                "language": row.language,
                "category": row.category,
                "term": row.term,
                "severity": row.severity,
                "is_active": row.is_active
            }
            for row in rows
        ]

    async def get_terms_by_category(self, language: str, category: str) -> list[dict[str, any]]:
        """Get blocked terms by language and category."""
        from flerity_core.domain.ai.schemas import ai_blocklist_table

        stmt = select(ai_blocklist_table).where(
            ai_blocklist_table.c.language == language,
            ai_blocklist_table.c.category == category,
            ai_blocklist_table.c.is_active
        ).order_by(
            ai_blocklist_table.c.severity.desc(),
            ai_blocklist_table.c.term
        )

        result = await self.session.execute(stmt)
        rows = result.fetchall()

        return [
            {
                "id": str(row.id),
                "language": row.language,
                "category": row.category,
                "term": row.term,
                "severity": row.severity,
                "is_active": row.is_active
            }
            for row in rows
        ]

