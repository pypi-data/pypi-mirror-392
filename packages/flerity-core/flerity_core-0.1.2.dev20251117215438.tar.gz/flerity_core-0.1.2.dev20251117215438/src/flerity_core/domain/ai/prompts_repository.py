"""Repository for AI prompts management."""


from sqlalchemy import and_, case, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import PromptTemplate, ai_prompts_table


class AIPromptsRepository:
    """Repository for managing AI prompt templates."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_prompt(
        self,
        kind: str,
        context_type: str,
        tone: str,
        language: str = "pt-BR",
        country: str = "BR",
        gender: str | None = None
    ) -> PromptTemplate | None:
        """Get prompt template by criteria."""

        gender_value = gender or "neutral"

        stmt = (
            select(ai_prompts_table)
            .where(
                and_(
                    ai_prompts_table.c.kind == kind,
                    ai_prompts_table.c.context_type == context_type,
                    ai_prompts_table.c.tone == tone,
                    ai_prompts_table.c.language == language,
                    ai_prompts_table.c.country == country,
                    ai_prompts_table.c.is_active,
                    or_(
                        ai_prompts_table.c.gender == gender_value,
                        ai_prompts_table.c.gender == "neutral",
                        ai_prompts_table.c.gender.is_(None)
                    )
                )
            )
            .order_by(
                case(
                    (ai_prompts_table.c.gender == gender_value, 1),
                    else_=2
                ),
                ai_prompts_table.c.created_at.desc()
            )
            .limit(1)
        )

        result = await self.session.execute(stmt)
        row = result.fetchone()

        if row:
            return PromptTemplate(
                id=row.id,
                name=row.name,
                kind=row.kind,
                context_type=row.context_type,
                tone=row.tone,
                language=row.language,
                country=row.country,
                gender=row.gender,
                template=row.template,
                is_active=row.is_active,
                created_at=row.created_at,
                updated_at=row.updated_at
            )

        return None

    async def get_fallback_prompt(
        self,
        kind: str,
        language: str = "pt-BR"
    ) -> PromptTemplate | None:
        """Get fallback prompt when specific criteria not found."""

        stmt = (
            select(ai_prompts_table)
            .where(
                and_(
                    ai_prompts_table.c.kind == kind,
                    ai_prompts_table.c.language == language,
                    ai_prompts_table.c.context_type == "general",
                    ai_prompts_table.c.tone == "friendly",
                    ai_prompts_table.c.is_active
                )
            )
            .order_by(ai_prompts_table.c.created_at.desc())
            .limit(1)
        )

        result = await self.session.execute(stmt)
        row = result.fetchone()

        if row:
            return PromptTemplate(
                id=row.id,
                name=row.name,
                kind=row.kind,
                context_type=row.context_type,
                tone=row.tone,
                language=row.language,
                country=row.country,
                gender=row.gender,
                template=row.template,
                is_active=row.is_active,
                created_at=row.created_at,
                updated_at=row.updated_at
            )

        return None
