"""Catalog repository for topics and avoid items management."""

import base64
import json
from collections.abc import Iterable, Sequence
from typing import Any
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import and_, delete, func, insert, or_, select, text, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ...utils.errors import BadRequest, ConflictError, Unauthorized
from ...utils.logging import get_logger
from ...utils.tracing import atrace_span
from ...utils.validation import require_len as validate_string_length
from .schemas import (
    AvoidOut,
    TopicOut,
    avoid_table,
    topics_table,
    user_avoid_table,
    user_topics_table,
)

logger = get_logger(__name__)


class CatalogRepository:
    """Unified repository for topics and avoid catalogs."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # Helper methods
    def _row_to_dict_topic(self, row: Any) -> dict[str, Any]:
        """Convert topic database row to dictionary."""
        return {
            'topic_id': row.topic_id,
            'name': row.name,
            'description': row.description,
            'active': row.active,
            'created_at': row.created_at
        }

    def _row_to_dict_avoid(self, row: Any) -> dict[str, Any]:
        """Convert avoid database row to dictionary."""
        return {
            'avoid_id': row.avoid_id,
            'description': row.description,
            'active': row.active,
            'created_at': row.created_at
        }

    def _encode_cursor(self, last_created_at: Any, last_id: UUID) -> str:
        """Encode pagination cursor."""
        cursor_data = {
            'last_created_at': last_created_at.isoformat() if last_created_at else None,
            'last_id': str(last_id)
        }
        return base64.urlsafe_b64encode(json.dumps(cursor_data).encode()).decode()

    def _decode_cursor(self, cursor: str) -> tuple[str | None, UUID]:
        """Decode pagination cursor."""
        try:
            cursor_data = json.loads(base64.urlsafe_b64decode(cursor.encode()).decode())
            last_created_at = cursor_data.get('last_created_at')
            if last_created_at:
                from datetime import datetime
                last_created_at = datetime.fromisoformat(last_created_at.replace('Z', '+00:00'))
            return last_created_at, UUID(cursor_data['last_id'])
        except (ValueError, KeyError, json.JSONDecodeError, TypeError) as e:
            logger.warning("Invalid cursor format", extra={"cursor": cursor, "error": str(e)})
            raise BadRequest("Invalid cursor format")

    # TOPICS METHODS

    async def get_topics(self, include_inactive: bool = False) -> list[TopicOut]:
        """Get all topics, optionally including inactive ones."""
        query = select(topics_table)
        if not include_inactive:
            query = query.where(topics_table.c.active.is_(True))
        query = query.order_by(topics_table.c.name)

        result = await self.session.execute(query)
        return [TopicOut.model_validate(self._row_to_dict_topic(row)) for row in result.fetchall()]

    async def get_topic_by_id(self, topic_id: UUID, include_inactive: bool = False) -> TopicOut | None:
        """Get topic by ID."""
        query = select(topics_table).where(topics_table.c.topic_id == topic_id)
        if not include_inactive:
            query = query.where(topics_table.c.active.is_(True))

        result = await self.session.execute(query)
        row = result.fetchone()
        return TopicOut.model_validate(self._row_to_dict_topic(row)) if row else None

    async def list_topics(
        self,
        *,
        limit: int = 50,
        cursor: str | None = None,
        q: str | None = None,
        include_inactive: bool = False
    ) -> tuple[list[dict[str, Any]], str | None]:
        """List topics with cursor-based pagination."""
        async with atrace_span("catalog_repository.list_topics", limit=limit, has_cursor=bool(cursor), has_query=bool(q)):
            if limit <= 0 or limit > 100:
                raise BadRequest("Limit must be between 1 and 100")

            if q and len(q) > 80:
                raise BadRequest("Search query too long")

            # Validate search query to prevent injection
            if q:
                q = validate_string_length(q.strip(), min_len=1, max_len=80, name="search_query")

            query = select(topics_table)
            conditions: list[Any] = []

            if not include_inactive:
                conditions.append(topics_table.c.active.is_(True))

            if q:
                # Use parameterized query to prevent SQL injection
                conditions.append(topics_table.c.name.ilike(text(":search_pattern")))
                query = query.params(search_pattern=f"%{q}%")

            if cursor:
                last_created_at, last_id = self._decode_cursor(cursor)
                if last_created_at:
                    cursor_condition = or_(
                        topics_table.c.created_at < last_created_at,
                        and_(
                            topics_table.c.created_at == last_created_at,
                            topics_table.c.topic_id < last_id
                        )
                    )
                    conditions.append(cursor_condition)

            if conditions:
                if len(conditions) == 1:
                    query = query.where(conditions[0])
                else:
                    query = query.where(sa.and_(*conditions))

            query = query.order_by(topics_table.c.created_at.desc(), topics_table.c.topic_id.desc()).limit(limit + 1)

            result = await self.session.execute(query)
            rows = result.fetchall()

            items = [self._row_to_dict_topic(row) for row in rows[:limit]]
            next_cursor = None

            if len(rows) > limit:
                last_row = rows[limit - 1]
                next_cursor = self._encode_cursor(last_row.created_at, last_row.topic_id)

            return items, next_cursor

    async def topics_exist_all(self, topic_ids: Sequence[UUID], *, include_inactive: bool = False) -> bool:
        """Check if all given topic IDs exist."""
        async with atrace_span("catalog_repository.topics_exist_all", count=len(topic_ids)):
            if not topic_ids:
                return True

            query = select(func.count()).select_from(topics_table).where(topics_table.c.topic_id.in_(topic_ids))

            if not include_inactive:
                query = query.where(topics_table.c.active.is_(True))

            result = await self.session.execute(query)
            count = result.scalar()

            return count == len(topic_ids)

    async def filter_existing_topics(self, topic_ids: Iterable[UUID], *, include_inactive: bool = False) -> list[UUID]:
        """Return subset of topic IDs that exist."""
        async with atrace_span("catalog_repository.filter_existing_topics"):
            topic_ids_list = list(topic_ids)
            if not topic_ids_list:
                return []

            query = select(topics_table.c.topic_id).where(topics_table.c.topic_id.in_(topic_ids_list))

            if not include_inactive:
                query = query.where(topics_table.c.active.is_(True))

            result = await self.session.execute(query)
            existing_ids = {row.topic_id for row in result.fetchall()}

            return [tid for tid in topic_ids_list if tid in existing_ids]

    async def upsert_topic(
        self,
        *,
        topic_id: UUID,
        name: str,
        description: str,
        active: bool = True,
        admin: bool = False
    ) -> dict[str, Any]:
        """Upsert topic (admin only)."""
        async with atrace_span("catalog_repository.upsert_topic", topic_id=str(topic_id)):
            if not admin:
                raise Unauthorized("Admin access required for upsert operations")

            name = validate_string_length(name, min_len=1, max_len=120, name="name")
            description = validate_string_length(description, min_len=1, max_len=500, name="description")

            from sqlalchemy.dialects.postgresql import insert as pg_insert

            stmt = pg_insert(topics_table).values(
                topic_id=topic_id,
                name=name,
                description=description,
                active=active,
                created_at=func.now()
            )

            upsert_stmt = stmt.on_conflict_do_update(
                index_elements=['topic_id'],
                set_=dict(
                    name=stmt.excluded.name,
                    description=stmt.excluded.description,
                    active=stmt.excluded.active
                )
            ).returning(topics_table)

            result = await self.session.execute(upsert_stmt)
            row = result.fetchone()
            if not row:
                raise ConflictError("Failed to upsert topic")
            return self._row_to_dict_topic(row)

    async def deactivate_topic(self, topic_id: UUID, *, admin: bool = False) -> None:
        """Deactivate topic (admin only)."""
        async with atrace_span("catalog_repository.deactivate_topic", topic_id=str(topic_id)):
            if not admin:
                raise Unauthorized("Admin access required for deactivate operations")

            stmt = update(topics_table).where(
                and_(topics_table.c.topic_id == topic_id, topics_table.c.active.is_(True))
            ).values(active=False)

            await self.session.execute(stmt)

    # AVOID METHODS

    async def get_avoids(self, include_inactive: bool = False) -> list[AvoidOut]:
        """Get all avoid items, optionally including inactive ones."""
        query = select(avoid_table)
        if not include_inactive:
            query = query.where(avoid_table.c.active.is_(True))
        query = query.order_by(avoid_table.c.description)

        result = await self.session.execute(query)
        return [AvoidOut.model_validate(self._row_to_dict_avoid(row)) for row in result.fetchall()]

    async def get_avoid_by_id(self, avoid_id: UUID, include_inactive: bool = False) -> AvoidOut | None:
        """Get avoid item by ID."""
        query = select(avoid_table).where(avoid_table.c.avoid_id == avoid_id)
        if not include_inactive:
            query = query.where(avoid_table.c.active.is_(True))

        result = await self.session.execute(query)
        row = result.fetchone()
        return AvoidOut.model_validate(self._row_to_dict_avoid(row)) if row else None

    async def list_avoids(
        self,
        *,
        limit: int = 50,
        cursor: str | None = None,
        q: str | None = None,
        include_inactive: bool = False
    ) -> tuple[list[dict[str, Any]], str | None]:
        """List avoid items with cursor-based pagination."""
        async with atrace_span("catalog_repository.list_avoids", limit=limit, has_cursor=bool(cursor), has_query=bool(q)):
            if limit <= 0 or limit > 100:
                raise BadRequest("Limit must be between 1 and 100")

            if q and len(q) > 80:
                raise BadRequest("Search query too long")

            # Validate search query to prevent injection
            if q:
                q = validate_string_length(q.strip(), min_len=1, max_len=80, name="search_query")

            query = select(avoid_table)
            conditions: list[Any] = []

            if not include_inactive:
                conditions.append(avoid_table.c.active.is_(True))

            if q:
                # Use parameterized query to prevent SQL injection
                conditions.append(avoid_table.c.description.ilike(text(":search_pattern")))
                query = query.params(search_pattern=f"%{q}%")

            if cursor:
                last_created_at, last_id = self._decode_cursor(cursor)
                if last_created_at:
                    cursor_condition = or_(
                        avoid_table.c.created_at < last_created_at,
                        and_(
                            avoid_table.c.created_at == last_created_at,
                            avoid_table.c.avoid_id < last_id
                        )
                    )
                    conditions.append(cursor_condition)

            if conditions:
                if len(conditions) == 1:
                    query = query.where(conditions[0])
                else:
                    query = query.where(sa.and_(*conditions))

            query = query.order_by(avoid_table.c.created_at.desc(), avoid_table.c.avoid_id.desc()).limit(limit + 1)

            result = await self.session.execute(query)
            rows = result.fetchall()

            items = [self._row_to_dict_avoid(row) for row in rows[:limit]]
            next_cursor = None

            if len(rows) > limit:
                last_row = rows[limit - 1]
                next_cursor = self._encode_cursor(last_row.created_at, last_row.avoid_id)

            return items, next_cursor

    async def avoids_exist_all(self, avoid_ids: Sequence[UUID], *, include_inactive: bool = False) -> bool:
        """Check if all given avoid IDs exist."""
        async with atrace_span("catalog_repository.avoids_exist_all", count=len(avoid_ids)):
            if not avoid_ids:
                return True

            query = select(func.count()).select_from(avoid_table).where(avoid_table.c.avoid_id.in_(avoid_ids))

            if not include_inactive:
                query = query.where(avoid_table.c.active.is_(True))

            result = await self.session.execute(query)
            count = result.scalar()

            return count == len(avoid_ids)

    async def filter_existing_avoids(self, avoid_ids: Iterable[UUID], *, include_inactive: bool = False) -> list[UUID]:
        """Return subset of avoid IDs that exist."""
        async with atrace_span("catalog_repository.filter_existing_avoids"):
            avoid_ids_list = list(avoid_ids)
            if not avoid_ids_list:
                return []

            query = select(avoid_table.c.avoid_id).where(avoid_table.c.avoid_id.in_(avoid_ids_list))

            if not include_inactive:
                query = query.where(avoid_table.c.active.is_(True))

            result = await self.session.execute(query)
            existing_ids = {row.avoid_id for row in result.fetchall()}

            return [aid for aid in avoid_ids_list if aid in existing_ids]

    async def upsert_avoid(
        self,
        *,
        avoid_id: UUID,
        description: str,
        active: bool = True,
        admin: bool = False
    ) -> dict[str, Any]:
        """Upsert avoid item (admin only)."""
        async with atrace_span("catalog_repository.upsert_avoid", avoid_id=str(avoid_id)):
            if not admin:
                raise Unauthorized("Admin access required for upsert operations")

            description = validate_string_length(description, min_len=1, max_len=120, name="description")

            from sqlalchemy.dialects.postgresql import insert as pg_insert

            insert_stmt = pg_insert(avoid_table).values(
                avoid_id=avoid_id,
                description=description,
                active=active,
                created_at=func.now()
            )

            upsert_stmt = insert_stmt.on_conflict_do_update(
                index_elements=['avoid_id'],
                set_=dict(
                    description=insert_stmt.excluded.description,
                    active=insert_stmt.excluded.active
                )
            ).returning(avoid_table)

            result = await self.session.execute(upsert_stmt)
            row = result.fetchone()
            if not row:
                raise ConflictError("Failed to upsert avoid item")
            return self._row_to_dict_avoid(row)

    async def deactivate_avoid(self, avoid_id: UUID, *, admin: bool = False) -> None:
        """Deactivate avoid item (admin only)."""
        async with atrace_span("catalog_repository.deactivate_avoid", avoid_id=str(avoid_id)):
            if not admin:
                raise Unauthorized("Admin access required for deactivate operations")

            stmt = update(avoid_table).where(
                and_(avoid_table.c.avoid_id == avoid_id, avoid_table.c.active.is_(True))
            ).values(active=False)

            await self.session.execute(stmt)

    # LEGACY METHODS (for backward compatibility)

    async def validate_topics_exist(self, topic_ids: list[UUID]) -> None:
        """Validate that all topic IDs exist. Raises exception if any don't exist."""
        if not topic_ids:
            return

        exists = await self.topics_exist_all(topic_ids)
        if not exists:
            raise BadRequest("One or more topic IDs do not exist")

    async def validate_avoids_exist(self, avoid_ids: list[UUID]) -> None:
        """Validate that all avoid IDs exist. Raises exception if any don't exist."""
        if not avoid_ids:
            return

        exists = await self.avoids_exist_all(avoid_ids)
        if not exists:
            raise BadRequest("One or more avoid IDs do not exist")

    # CRUD aliases for backward compatibility
    async def find_topic_by_id(self, topic_id: UUID) -> TopicOut | None:
        """Find topic by ID (alias for get_topic_by_id)."""
        return await self.get_topic_by_id(topic_id)

    async def find_all_topics(self, limit: int = 100, search: str | None = None) -> list[TopicOut]:
        """Find all topics with optional search."""
        items, _ = await self.list_topics(limit=limit, q=search)
        return [TopicOut.model_validate(item) for item in items]

    async def create_topic(self, data: dict[str, Any]) -> TopicOut:
        """Create new topic."""
        if 'name' not in data and 'description' in data:
            data['name'] = data['description']
        if 'active' not in data:
            data['active'] = True

        stmt = insert(topics_table).values(**data).returning(topics_table)
        result = await self.session.execute(stmt)
        row = result.fetchone()
        return TopicOut.model_validate(self._row_to_dict_topic(row))

    async def delete_topic(self, topic_id: UUID) -> bool:
        """Delete topic."""
        stmt = delete(topics_table).where(topics_table.c.topic_id == topic_id)
        result = await self.session.execute(stmt)
        return getattr(result, 'rowcount', 0) > 0

    async def find_avoid_by_id(self, avoid_id: UUID) -> AvoidOut | None:
        """Find avoid item by ID (alias for get_avoid_by_id)."""
        return await self.get_avoid_by_id(avoid_id)

    async def find_all_avoid(self, limit: int = 100, search: str | None = None) -> list[AvoidOut]:
        """Find all avoid items with optional search."""
        items, _ = await self.list_avoids(limit=limit, q=search)
        return [AvoidOut.model_validate(item) for item in items]

    async def create_avoid(self, data: dict[str, Any]) -> AvoidOut:
        """Create new avoid item."""
        if 'active' not in data:
            data['active'] = True

        stmt = insert(avoid_table).values(**data).returning(avoid_table)
        result = await self.session.execute(stmt)
        row = result.fetchone()
        return AvoidOut.model_validate(self._row_to_dict_avoid(row))

    async def delete_avoid(self, avoid_id: UUID) -> bool:
        """Delete avoid item."""
        stmt = delete(avoid_table).where(avoid_table.c.avoid_id == avoid_id)
        result = await self.session.execute(stmt)
        return getattr(result, 'rowcount', 0) > 0

    # USER PREFERENCES METHODS (RLS enforced)
    async def find_user_topics(self, user_id: UUID) -> list[TopicOut]:
        """Find topics selected by user."""
        stmt = select(
            topics_table.c.topic_id,
            topics_table.c.name,
            topics_table.c.description,
            topics_table.c.active,
            topics_table.c.created_at
        ).select_from(
            topics_table.join(user_topics_table, topics_table.c.topic_id == user_topics_table.c.topic_id)
        ).where(
            and_(
                user_topics_table.c.user_id == func.app.current_user_id(),
                topics_table.c.active.is_(True)
            )
        ).order_by(topics_table.c.name)

        result = await self.session.execute(stmt)
        return [TopicOut.model_validate(self._row_to_dict_topic(row)) for row in result.fetchall()]

    async def find_user_avoid(self, user_id: UUID) -> list[AvoidOut]:
        """Find avoid items selected by user."""
        stmt = select(
            avoid_table.c.avoid_id,
            avoid_table.c.description,
            avoid_table.c.active,
            avoid_table.c.created_at
        ).select_from(
            avoid_table.join(user_avoid_table, avoid_table.c.avoid_id == user_avoid_table.c.avoid_id)
        ).where(
            and_(
                user_avoid_table.c.user_id == func.app.current_user_id(),
                avoid_table.c.active.is_(True)
            )
        ).order_by(avoid_table.c.description)

        result = await self.session.execute(stmt)
        return [AvoidOut.model_validate(self._row_to_dict_avoid(row)) for row in result.fetchall()]

    async def add_user_topic(self, user_id: UUID, topic_id: UUID) -> bool:
        """Add topic to user preferences."""
        from sqlalchemy.dialects.postgresql import insert as pg_insert
        stmt = pg_insert(user_topics_table).values(
            user_id=user_id,
            topic_id=topic_id
        ).on_conflict_do_nothing()

        try:
            await self.session.execute(stmt)
            return True
        except IntegrityError as e:
            logger.warning("Failed to add user topic", extra={"user_id": str(user_id), "topic_id": str(topic_id), "error": str(e)})
            return False

    async def remove_user_topic(self, user_id: UUID, topic_id: UUID) -> bool:
        """Remove topic from user preferences."""
        stmt = delete(user_topics_table).where(
            and_(
                user_topics_table.c.user_id == user_id,
                user_topics_table.c.topic_id == topic_id
            )
        )
        result = await self.session.execute(stmt)
        return getattr(result, 'rowcount', 0) > 0

    async def add_user_avoid(self, user_id: UUID, avoid_id: UUID) -> bool:
        """Add avoid item to user preferences."""
        from sqlalchemy.dialects.postgresql import insert as pg_insert
        stmt = pg_insert(user_avoid_table).values(
            user_id=user_id,
            avoid_id=avoid_id
        ).on_conflict_do_nothing()

        try:
            await self.session.execute(stmt)
            return True
        except IntegrityError as e:
            logger.warning("Failed to add user avoid", extra={"user_id": str(user_id), "avoid_id": str(avoid_id), "error": str(e)})
            return False

    async def remove_user_avoid(self, user_id: UUID, avoid_id: UUID) -> bool:
        """Remove avoid item from user preferences."""
        stmt = delete(user_avoid_table).where(
            and_(
                user_avoid_table.c.user_id == user_id,
                user_avoid_table.c.avoid_id == avoid_id
            )
        )
        result = await self.session.execute(stmt)
        return getattr(result, 'rowcount', 0) > 0
