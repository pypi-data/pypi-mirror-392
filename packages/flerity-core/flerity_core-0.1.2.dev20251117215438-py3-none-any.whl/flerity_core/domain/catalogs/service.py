"""Catalogs service for topics and avoid preferences."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from ...db.uow import async_uow_factory
from ...utils.domain_logger import get_domain_logger
from ...utils.errors import BadRequest
from ...utils.i18n import t
from ...utils.logging import get_safe_logger
from ...utils.request_tracking import RequestTracker
from ...utils.tracing import trace_async
from .repository import CatalogRepository
from .schemas import AvoidOut, CatalogResponse, TopicOut

logger = get_safe_logger(__name__)
domain_logger = get_domain_logger(__name__)


class CatalogsService:
    """Service for catalog operations."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory

    @trace_async
    async def get_catalogs(self) -> CatalogResponse:
        """Get available topics and avoid preferences."""
        with RequestTracker(operation="get_catalogs") as tracker:
            try:
                tracking_context = domain_logger.operation_start("get_catalogs")
                
                async with async_uow_factory(self.session_factory)() as uow:
                    repository = CatalogRepository(uow.session)
                    topics = await repository.get_topics(include_inactive=False)
                    avoids = await repository.get_avoids(include_inactive=False)

                    result = CatalogResponse(topics=topics, avoids=avoids)
                    
                    domain_logger.operation_success(tracking_context, {
                        "topics_count": len(topics),
                        "avoids_count": len(avoids)
                    })
                    domain_logger.business_event("catalogs_retrieved", {
                        "topics_count": len(topics),
                        "avoids_count": len(avoids)
                    })
                    tracker.log_success(topics_count=len(topics), avoids_count=len(avoids))
                    
                    return result
            except Exception as e:
                error_id = tracker.log_error(e, context={"operation": "get_catalogs"})
                domain_logger.operation_error(tracking_context, str(e), {"error_id": error_id})
                raise BadRequest(f"Failed to get catalogs (Error ID: {error_id})")

    @trace_async
    async def list_topics(
        self,
        *,
        limit: int = 50,
        cursor: str | None = None,
        search_query: str | None = None,
        locale: str = "en-US"
    ) -> tuple[list[dict[str, Any]], str | None]:
        """List topics with pagination and search."""
        if limit <= 0 or limit > 100:
            raise BadRequest("Limit must be between 1 and 100")

        with RequestTracker(operation="list_topics") as tracker:
            try:
                tracking_context = domain_logger.operation_start("list_topics", limit=limit, has_cursor=cursor is not None, has_query=search_query is not None, locale=locale)

                async with async_uow_factory(self.session_factory)() as uow:
                    repository = CatalogRepository(uow.session)
                    topics, next_cursor = await repository.list_topics(
                        limit=limit,
                        cursor=cursor,
                        q=search_query,
                        include_inactive=False
                    )

                    # Apply translations
                    translated_topics = self._translate_topics(topics, locale)

                    domain_logger.operation_success(tracking_context, {
                        "topics_count": len(translated_topics),
                        "has_next_cursor": next_cursor is not None,
                        "locale": locale
                    })
                    domain_logger.business_event("topics_listed", {
                        "topics_count": len(translated_topics),
                        "search_query": search_query,
                        "locale": locale
                    })
                    tracker.log_success(topics_count=len(translated_topics), locale=locale)

                    return translated_topics, next_cursor
            except Exception as e:
                error_id = tracker.log_error(e, context={
                    "limit": limit,
                    "locale": locale,
                    "search_query": search_query
                })
                domain_logger.operation_error(tracking_context, str(e), {"error_id": error_id, "limit": limit})
                raise BadRequest(f"Failed to list topics (Error ID: {error_id})")

    @trace_async
    async def list_avoids(
        self,
        *,
        limit: int = 50,
        cursor: str | None = None,
        search_query: str | None = None,
        locale: str = "en-US"
    ) -> tuple[list[dict[str, Any]], str | None]:
        """List avoid items with pagination and search."""
        if limit <= 0 or limit > 100:
            raise BadRequest("Limit must be between 1 and 100")

        with RequestTracker(operation="list_avoids") as tracker:
            try:
                tracking_context = domain_logger.operation_start("list_avoids", limit=limit, has_cursor=cursor is not None, has_query=search_query is not None, locale=locale)

                async with async_uow_factory(self.session_factory)() as uow:
                    repository = CatalogRepository(uow.session)
                    avoids, next_cursor = await repository.list_avoids(
                        limit=limit,
                        cursor=cursor,
                        q=search_query,
                        include_inactive=False
                    )

                    # Apply translations
                    translated_avoids = self._translate_avoids(avoids, locale)

                    domain_logger.operation_success(tracking_context, {
                        "avoids_count": len(translated_avoids),
                        "has_next_cursor": next_cursor is not None,
                        "locale": locale
                    })
                    domain_logger.business_event("avoids_listed", {
                        "avoids_count": len(translated_avoids),
                        "search_query": search_query,
                        "locale": locale
                    })
                    tracker.log_success(avoids_count=len(translated_avoids), locale=locale)

                    return translated_avoids, next_cursor
            except Exception as e:
                error_id = tracker.log_error(e, context={
                    "limit": limit,
                    "locale": locale,
                    "search_query": search_query
                })
                domain_logger.operation_error(tracking_context, str(e), {"error_id": error_id, "limit": limit})
                raise BadRequest(f"Failed to list avoid items (Error ID: {error_id})")

    @trace_async
    async def get_user_topics(self, user_id: UUID) -> list[TopicOut]:
        """Get topics selected by user."""
        with RequestTracker(user_id=user_id, operation="get_user_topics") as tracker:
            try:
                tracking_context = domain_logger.operation_start("get_user_topics", user_id=str(user_id))

                async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                    repository = CatalogRepository(uow.session)
                    topics = await repository.find_user_topics(user_id)
                    
                    domain_logger.operation_success(tracking_context, {
                        "user_id": str(user_id),
                        "topics_count": len(topics)
                    })
                    domain_logger.business_event("user_topics_retrieved", {
                        "user_id": str(user_id),
                        "topics_count": len(topics)
                    })
                    tracker.log_success(topics_count=len(topics))
                    
                    return topics
            except Exception as e:
                error_id = tracker.log_error(e, context={"user_id": str(user_id)})
                domain_logger.operation_error(tracking_context, str(e), {
                    "error_id": error_id,
                    "user_id": str(user_id)
                })
                raise BadRequest(f"Failed to get user topics (Error ID: {error_id})")

    @trace_async
    async def get_user_avoids(self, user_id: UUID) -> list[AvoidOut]:
        """Get avoid items selected by user."""
        with RequestTracker(user_id=user_id, operation="get_user_avoids") as tracker:
            try:
                tracking_context = domain_logger.operation_start("get_user_avoids", user_id=str(user_id))

                async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                    repository = CatalogRepository(uow.session)
                    avoids = await repository.find_user_avoid(user_id)
                    
                    domain_logger.operation_success(tracking_context, {
                        "user_id": str(user_id),
                        "avoids_count": len(avoids)
                    })
                    domain_logger.business_event("user_avoids_retrieved", {
                        "user_id": str(user_id),
                        "avoids_count": len(avoids)
                    })
                    tracker.log_success(avoids_count=len(avoids))
                    
                    return avoids
            except Exception as e:
                error_id = tracker.log_error(e, context={"user_id": str(user_id)})
                domain_logger.operation_error(tracking_context, str(e), {
                    "error_id": error_id,
                    "user_id": str(user_id)
                })
                raise BadRequest(f"Failed to get user avoids (Error ID: {error_id})")

    @trace_async
    async def add_user_topic(self, user_id: UUID, topic_id: UUID) -> bool:
        """Add topic to user preferences."""
        with RequestTracker(user_id=user_id, operation="add_user_topic") as tracker:
            try:
                tracking_context = domain_logger.operation_start("add_user_topic", user_id=str(user_id), topic_id=str(topic_id))

                async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                    repository = CatalogRepository(uow.session)
                    result = await repository.add_user_topic(user_id, topic_id)
                    await uow.commit()
                    
                    domain_logger.operation_success(tracking_context, {
                        "user_id": str(user_id),
                        "topic_id": str(topic_id),
                        "added": result
                    })
                    domain_logger.business_event("user_topic_added", {
                        "user_id": str(user_id),
                        "topic_id": str(topic_id),
                        "success": result
                    })
                    tracker.log_success(topic_id=str(topic_id), added=result)
                    
                    return result
            except Exception as e:
                error_id = tracker.log_error(e, context={
                    "user_id": str(user_id),
                    "topic_id": str(topic_id)
                })
                domain_logger.operation_error(tracking_context, str(e), {
                    "error_id": error_id,
                    "user_id": str(user_id),
                    "topic_id": str(topic_id)
                })
                raise BadRequest(f"Failed to add user topic (Error ID: {error_id})")

    @trace_async
    async def remove_user_topic(self, user_id: UUID, topic_id: UUID) -> bool:
        """Remove topic from user preferences."""
        with RequestTracker(user_id=user_id, operation="remove_user_topic") as tracker:
            try:
                tracking_context = domain_logger.operation_start("remove_user_topic", user_id=str(user_id), topic_id=str(topic_id))

                async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                    repository = CatalogRepository(uow.session)
                    result = await repository.remove_user_topic(user_id, topic_id)
                    await uow.commit()
                    
                    domain_logger.operation_success(tracking_context, {
                        "user_id": str(user_id),
                        "topic_id": str(topic_id),
                        "removed": result
                    })
                    domain_logger.business_event("user_topic_removed", {
                        "user_id": str(user_id),
                        "topic_id": str(topic_id),
                        "success": result
                    })
                    tracker.log_success(topic_id=str(topic_id), removed=result)
                    
                    return result
            except Exception as e:
                error_id = tracker.log_error(e, context={
                    "user_id": str(user_id),
                    "topic_id": str(topic_id)
                })
                domain_logger.operation_error(tracking_context, str(e), {
                    "error_id": error_id,
                    "user_id": str(user_id),
                    "topic_id": str(topic_id)
                })
                raise BadRequest(f"Failed to remove user topic (Error ID: {error_id})")

    @trace_async
    async def add_user_avoid(self, user_id: UUID, avoid_id: UUID) -> bool:
        """Add avoid item to user preferences."""
        with RequestTracker(user_id=user_id, operation="add_user_avoid") as tracker:
            try:
                tracking_context = domain_logger.operation_start("add_user_avoid", user_id=str(user_id), avoid_id=str(avoid_id))

                async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                    repository = CatalogRepository(uow.session)
                    result = await repository.add_user_avoid(user_id, avoid_id)
                    await uow.commit()
                    
                    domain_logger.operation_success(tracking_context, {
                        "user_id": str(user_id),
                        "avoid_id": str(avoid_id),
                        "added": result
                    })
                    domain_logger.business_event("user_avoid_added", {
                        "user_id": str(user_id),
                        "avoid_id": str(avoid_id),
                        "success": result
                    })
                    tracker.log_success(avoid_id=str(avoid_id), added=result)
                    
                    return result
            except Exception as e:
                error_id = tracker.log_error(e, context={
                    "user_id": str(user_id),
                    "avoid_id": str(avoid_id)
                })
                domain_logger.operation_error(tracking_context, str(e), {
                    "error_id": error_id,
                    "user_id": str(user_id),
                    "avoid_id": str(avoid_id)
                })
                raise BadRequest(f"Failed to add user avoid (Error ID: {error_id})")

    @trace_async
    async def remove_user_avoid(self, user_id: UUID, avoid_id: UUID) -> bool:
        """Remove avoid item from user preferences."""
        with RequestTracker(user_id=user_id, operation="remove_user_avoid") as tracker:
            try:
                tracking_context = domain_logger.operation_start("remove_user_avoid", user_id=str(user_id), avoid_id=str(avoid_id))

                async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                    repository = CatalogRepository(uow.session)
                    result = await repository.remove_user_avoid(user_id, avoid_id)
                    await uow.commit()
                    
                    domain_logger.operation_success(tracking_context, {
                        "user_id": str(user_id),
                        "avoid_id": str(avoid_id),
                        "removed": result
                    })
                    domain_logger.business_event("user_avoid_removed", {
                        "user_id": str(user_id),
                        "avoid_id": str(avoid_id),
                        "success": result
                    })
                    tracker.log_success(avoid_id=str(avoid_id), removed=result)
                    
                    return result
            except Exception as e:
                error_id = tracker.log_error(e, context={
                    "user_id": str(user_id),
                    "avoid_id": str(avoid_id)
                })
                domain_logger.operation_error(tracking_context, str(e), {
                    "error_id": error_id,
                    "user_id": str(user_id),
                    "avoid_id": str(avoid_id)
                })
                raise BadRequest(f"Failed to remove user avoid (Error ID: {error_id})")

    def _translate_topics(self, topics: list[dict[str, Any]], locale: str) -> list[dict[str, Any]]:
        """Translate topic names and descriptions based on locale."""
        translated_topics = []

        for topic in topics:
            translated_topic = topic.copy()

            # The name and description fields already contain i18n keys from the database
            name_key = topic.get('name', '')
            description_key = topic.get('description', '')

            # Translate name
            try:
                translated_name = t(name_key, locale=locale)
                # If translation returns the key itself, keep original
                if translated_name != name_key:
                    translated_topic['name'] = translated_name
            except (KeyError, ValueError, Exception):
                # Keep original if translation fails
                pass

            # Translate description
            try:
                translated_desc = t(description_key, locale=locale)
                # If translation returns the key itself, keep original
                if translated_desc != description_key:
                    translated_topic['description'] = translated_desc
            except (KeyError, ValueError, Exception):
                # Keep original if translation fails
                pass

            translated_topics.append(translated_topic)

        return translated_topics

    def _translate_avoids(self, avoids: list[dict[str, Any]], locale: str) -> list[dict[str, Any]]:
        """Translate avoid descriptions based on locale."""
        translated_avoids = []

        for avoid in avoids:
            translated_avoid = avoid.copy()

            # The description field already contains i18n key from the database
            description_key = avoid.get('description', '')

            # Translate description
            try:
                translated_desc = t(description_key, locale=locale)
                # If translation returns the key itself, keep original
                if translated_desc != description_key:
                    translated_avoid['description'] = translated_desc
            except (KeyError, ValueError, Exception):
                # Keep original if translation fails
                pass

            translated_avoids.append(translated_avoid)

        return translated_avoids
