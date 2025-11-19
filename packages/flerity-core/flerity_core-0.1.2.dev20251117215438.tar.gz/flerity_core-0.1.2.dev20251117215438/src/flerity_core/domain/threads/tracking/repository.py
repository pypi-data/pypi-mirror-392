"""Thread tracking repository for tracking configuration operations."""

from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from ....utils.errors import BadRequest, NotFound
from ....utils.logging import get_logger
from ....utils.redis_client import get_redis_client
from ....utils.tracing import trace_async
from .schemas import (
    ThreadTrackingConfiguration,
    ThreadTrackingConfigurationCreate,
    ThreadTrackingConfigurationUpdate,
    thread_tracking_configurations_table,
)

logger = get_logger(__name__)

# Cache configuration
TRACKING_CACHE_KEY = "thread_tracking:{thread_id}"
USER_TRACKING_CACHE_KEY = "user_tracking:{user_id}"
TRACKING_CACHE_TTL = 3600  # 1 hour
USER_TRACKING_CACHE_TTL = 1800  # 30 minutes


class ThreadTrackingRepository:
    """Repository for thread tracking configuration management."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.redis = get_redis_client()
        # Connection pooling optimization: prepare commonly used statements
        self._prepared_statements = {}

    @trace_async
    async def get_by_thread_id(self, thread_id: UUID) -> ThreadTrackingConfiguration | None:
        """Get tracking configuration by thread ID (RLS enforced)."""
        try:
            stmt = sa.select(thread_tracking_configurations_table).where(
                thread_tracking_configurations_table.c.thread_id == thread_id
            )
            result = await self.session.execute(stmt)
            row = result.fetchone()
            if not row:
                return None
            return ThreadTrackingConfiguration.model_validate(dict(row._mapping))
        except sa.exc.SQLAlchemyError as e:
            logger.error("Database error getting tracking configuration", extra={
                "thread_id": str(thread_id), "error": str(e)
            })
            raise BadRequest("Failed to retrieve tracking configuration")
        except Exception as e:
            logger.error("Unexpected error getting tracking configuration", extra={
                "thread_id": str(thread_id), "error": str(e)
            })
            raise BadRequest("Failed to retrieve tracking configuration")

    @trace_async
    async def get_cached_tracking_status(self, thread_id: UUID) -> bool | None:
        """Get cached tracking status without database fallback."""
        try:
            cache_key = TRACKING_CACHE_KEY.format(thread_id=thread_id)
            cached_value = await self.redis.get(cache_key)
            if cached_value is not None:
                return cached_value.lower() == "true"
            return None
        except Exception as e:
            logger.warning("Failed to get cached tracking status", extra={
                "thread_id": str(thread_id),
                "error": str(e)
            })
            return None

    @trace_async
    async def batch_get_tracking_status(self, thread_ids: list[UUID]) -> dict[UUID, bool]:
        """Get tracking status for multiple threads efficiently."""
        if not thread_ids:
            return {}

        result = {}
        cache_keys = [TRACKING_CACHE_KEY.format(thread_id=thread_id) for thread_id in thread_ids]

        try:
            # Try to get all from cache first
            cached_values = []
            try:
                client = await self.redis.get_client()
                cached_values = await client.mget(cache_keys)
            except Exception as cache_error:
                logger.warning("Failed to get cached tracking statuses", extra={
                    "thread_ids": [str(tid) for tid in thread_ids],
                    "cache_error": str(cache_error),
                    "cache_error_type": type(cache_error).__name__
                })
                # Fall back to empty cache values
                cached_values = [None] * len(cache_keys)

            uncached_thread_ids = []
            for i, (thread_id, cached_value) in enumerate(zip(thread_ids, cached_values)):
                if cached_value is not None:
                    result[thread_id] = cached_value.lower() == "true"
                else:
                    uncached_thread_ids.append(thread_id)

            # Query database for uncached values
            if uncached_thread_ids:
                stmt = sa.select(
                    thread_tracking_configurations_table.c.thread_id,
                    thread_tracking_configurations_table.c.is_active
                ).where(
                    sa.and_(
                        thread_tracking_configurations_table.c.thread_id.in_(uncached_thread_ids),
                        thread_tracking_configurations_table.c.is_active
                    )
                )
                db_result = await self.session.execute(stmt)

                # Process database results
                active_threads = {row.thread_id for row in db_result.fetchall()}

                # Cache and add to result
                pipe = client.pipeline()
                for thread_id in uncached_thread_ids:
                    is_active = thread_id in active_threads
                    result[thread_id] = is_active

                    cache_key = TRACKING_CACHE_KEY.format(thread_id=thread_id)
                    pipe.set(cache_key, str(is_active).lower(), ex=TRACKING_CACHE_TTL)

                await pipe.execute()

            return result
        except Exception as e:
            logger.error("Error in batch tracking status lookup", extra={
                "thread_count": len(thread_ids),
                "error": str(e)
            })
            # Fallback to individual lookups
            for thread_id in thread_ids:
                try:
                    result[thread_id] = await self.is_tracking_enabled(thread_id)
                except Exception:
                    result[thread_id] = False

            return result

    @trace_async
    async def bulk_create_tracking_configs(
        self,
        configs: list[ThreadTrackingConfigurationCreate],
        user_id: UUID
    ) -> list[ThreadTrackingConfiguration]:
        """Bulk create tracking configurations for better performance."""
        if not configs:
            return []

        try:
            # Prepare bulk insert data
            config_data_list = []
            for config in configs:
                config_data = config.model_dump(exclude_none=True)
                config_data['user_id'] = user_id
                config_data_list.append(config_data)

            # Use bulk insert with RETURNING
            stmt = sa.insert(thread_tracking_configurations_table).values(config_data_list).returning(
                thread_tracking_configurations_table
            )
            result = await self.session.execute(stmt)

            created_configs = [
                ThreadTrackingConfiguration.model_validate(dict(row._mapping))
                for row in result.fetchall()
            ]

            # Invalidate user cache
            await self.invalidate_user_cache(user_id)

            # Invalidate thread caches in batch
            thread_ids = [config.thread_id for config in created_configs]
            if thread_ids:
                try:
                    client = await self.redis.get_client()
                    pipe = client.pipeline()
                    for thread_id in thread_ids:
                        cache_key = TRACKING_CACHE_KEY.format(thread_id=thread_id)
                        pipe.delete(cache_key)
                    await pipe.execute()
                except Exception as cache_error:
                    logger.warning("Failed to invalidate thread caches", extra={
                        "thread_ids": [str(tid) for tid in thread_ids],
                        "cache_error": str(cache_error),
                        "cache_error_type": type(cache_error).__name__
                    })

            return created_configs
        except sa.exc.IntegrityError as e:
            logger.error("Bulk tracking configuration creation integrity error", extra={"error": str(e)})
            raise BadRequest("Some tracking configurations already exist")
        except sa.exc.SQLAlchemyError as e:
            logger.error("Database error bulk creating tracking configurations", extra={"error": str(e)})
            raise BadRequest("Failed to create tracking configurations")
        except Exception as e:
            logger.error("Unexpected error bulk creating tracking configurations", extra={"error": str(e)})
            raise BadRequest("Failed to create tracking configurations")

    @trace_async
    async def bulk_update_tracking_status(
        self,
        thread_ids: list[UUID],
        is_active: bool,
        user_id: UUID
    ) -> int:
        """Bulk update tracking status for multiple threads."""
        if not thread_ids:
            return 0

        try:
            stmt = (
                sa.update(thread_tracking_configurations_table)
                .where(
                    sa.and_(
                        thread_tracking_configurations_table.c.thread_id.in_(thread_ids),
                        thread_tracking_configurations_table.c.user_id == user_id
                    )
                )
                .values(is_active=is_active, updated_at=sa.func.now())
            )
            result = await self.session.execute(stmt)
            updated_count = getattr(result, 'rowcount', 0)

            # Invalidate caches in batch
            await self.invalidate_user_cache(user_id)

            if thread_ids:
                try:
                    client = await self.redis.get_client()
                    pipe = client.pipeline()
                    for thread_id in thread_ids:
                        cache_key = TRACKING_CACHE_KEY.format(thread_id=thread_id)
                        pipe.delete(cache_key)
                    await pipe.execute()
                except Exception as cache_error:
                    logger.warning("Failed to invalidate thread caches in bulk update", extra={
                        "thread_ids": [str(tid) for tid in thread_ids],
                        "cache_error": str(cache_error),
                        "cache_error_type": type(cache_error).__name__
                    })

            return updated_count
        except sa.exc.SQLAlchemyError as e:
            logger.error("Database error bulk updating tracking status", extra={
                "thread_count": len(thread_ids), "error": str(e)
            })
            raise BadRequest("Failed to update tracking status")
        except Exception as e:
            logger.error("Unexpected error bulk updating tracking status", extra={
                "thread_count": len(thread_ids), "error": str(e)
            })
            raise BadRequest("Failed to update tracking status")

    @trace_async
    async def get_tracking_stats(self, user_id: UUID) -> dict[str, int]:
        """Get tracking statistics for user with optimized query."""
        try:
            stmt = sa.select(
                sa.func.count().label('total'),
                sa.func.sum(sa.case((thread_tracking_configurations_table.c.is_active, 1), else_=0)).label('active'),
                sa.func.sum(sa.case((not thread_tracking_configurations_table.c.is_active, 1), else_=0)).label('inactive')
            ).where(thread_tracking_configurations_table.c.user_id == user_id)

            result = await self.session.execute(stmt)
            row = result.fetchone()

            if row:
                return {
                    'total': row.total or 0,
                    'active': row.active or 0,
                    'inactive': row.inactive or 0
                }
            return {'total': 0, 'active': 0, 'inactive': 0}
        except sa.exc.SQLAlchemyError as e:
            logger.error("Database error getting tracking stats", extra={
                "user_id": str(user_id), "error": str(e)
            })
            raise BadRequest("Failed to get tracking statistics")
        except Exception as e:
            logger.error("Unexpected error getting tracking stats", extra={
                "user_id": str(user_id), "error": str(e)
            })
            raise BadRequest("Failed to get tracking statistics")

    @trace_async
    async def get_by_user_id(self, user_id: UUID) -> list[ThreadTrackingConfiguration]:
        """Get all tracking configurations for user with caching (RLS enforced)."""
        cache_key = USER_TRACKING_CACHE_KEY.format(user_id=user_id)

        try:
            # Try cache first
            cached_json = await self.redis.get(cache_key)
            if cached_json is not None:
                import json
                cached_data = json.loads(cached_json)
                return [
                    ThreadTrackingConfiguration.model_validate(config_data)
                    for config_data in cached_data
                ]

            # Query database
            stmt = sa.select(thread_tracking_configurations_table).where(
                thread_tracking_configurations_table.c.user_id == user_id
            ).order_by(thread_tracking_configurations_table.c.created_at.desc())

            result = await self.session.execute(stmt)
            configs = [
                ThreadTrackingConfiguration.model_validate(dict(row._mapping))
                for row in result.fetchall()
            ]

            # Cache result - serialize to JSON string
            try:
                import json
                cache_data = [config.model_dump(mode='json') for config in configs]
                cache_json = json.dumps(cache_data)
                await self.redis.set(cache_key, cache_json, ex=USER_TRACKING_CACHE_TTL)
            except Exception as cache_error:
                # Log cache error but don't fail the request
                logger.warning("Failed to cache user tracking configurations", extra={
                    "user_id": str(user_id),
                    "cache_error": str(cache_error),
                    "cache_error_type": type(cache_error).__name__
                })

            return configs
        except sa.exc.SQLAlchemyError as e:
            logger.error("Database error getting user tracking configurations", extra={
                "user_id": str(user_id), "error": str(e)
            })
            raise BadRequest("Failed to retrieve tracking configurations")
        except Exception as e:
            logger.error("Unexpected error getting user tracking configurations", extra={
                "user_id": str(user_id), "error": str(e)
            })
            raise BadRequest("Failed to retrieve tracking configurations")

    @trace_async
    async def create(self, data: ThreadTrackingConfigurationCreate, user_id: UUID) -> ThreadTrackingConfiguration:
        """Create new tracking configuration."""
        try:
            config_data = data.model_dump(exclude_none=True)
            config_data['user_id'] = user_id

            stmt = sa.insert(thread_tracking_configurations_table).values(**config_data).returning(
                thread_tracking_configurations_table
            )
            result = await self.session.execute(stmt)
            row = result.fetchone()
            if not row:
                raise BadRequest("Failed to create tracking configuration")

            config = ThreadTrackingConfiguration.model_validate(dict(row._mapping))

            # Invalidate caches in background (non-blocking)
            import asyncio
            asyncio.create_task(self._invalidate_caches_async(config.thread_id, user_id))

            return config
        except sa.exc.IntegrityError as e:
            logger.error("Tracking configuration creation integrity error", extra={"error": str(e)})
            if "thread_tracking_user_thread_unique" in str(e):
                raise BadRequest("Tracking configuration already exists for this thread")
            raise BadRequest("Failed to create tracking configuration")
        except sa.exc.SQLAlchemyError as e:
            logger.error("Database error creating tracking configuration", extra={"error": str(e)})
            raise BadRequest("Failed to create tracking configuration")
        except Exception as e:
            logger.error("Unexpected error creating tracking configuration", extra={"error": str(e)})
            raise BadRequest("Failed to create tracking configuration")

    @trace_async
    async def update(
        self,
        thread_id: UUID,
        data: ThreadTrackingConfigurationUpdate,
        user_id: UUID
    ) -> ThreadTrackingConfiguration:
        """Update tracking configuration (RLS enforced)."""
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            # If no data to update, return existing configuration
            existing = await self.get_by_thread_id(thread_id)
            if not existing:
                raise NotFound(f"Tracking configuration for thread {thread_id} not found")
            return existing

        update_data['updated_at'] = sa.func.now()

        try:
            stmt = (
                sa.update(thread_tracking_configurations_table)
                .where(thread_tracking_configurations_table.c.thread_id == thread_id)
                .values(**update_data)
                .returning(thread_tracking_configurations_table)
            )
            result = await self.session.execute(stmt)
            row = result.fetchone()
            if not row:
                raise NotFound(f"Tracking configuration for thread {thread_id} not found")

            config = ThreadTrackingConfiguration.model_validate(dict(row._mapping))

            # Invalidate caches
            await self._invalidate_caches(thread_id, user_id)

            return config
        except NotFound:
            raise
        except sa.exc.SQLAlchemyError as e:
            logger.error("Database error updating tracking configuration", extra={
                "thread_id": str(thread_id), "error": str(e)
            })
            raise BadRequest("Failed to update tracking configuration")
        except Exception as e:
            logger.error("Unexpected error updating tracking configuration", extra={
                "thread_id": str(thread_id), "error": str(e)
            })
            raise BadRequest("Failed to update tracking configuration")

    @trace_async
    async def delete(self, thread_id: UUID, user_id: UUID) -> None:
        """Delete tracking configuration (RLS enforced)."""
        try:
            stmt = sa.delete(thread_tracking_configurations_table).where(
                thread_tracking_configurations_table.c.thread_id == thread_id
            )
            result = await self.session.execute(stmt)
            if getattr(result, 'rowcount', 0) == 0:
                raise NotFound(f"Tracking configuration for thread {thread_id} not found")

            # Invalidate caches
            await self._invalidate_caches(thread_id, user_id)

        except NotFound:
            raise
        except sa.exc.SQLAlchemyError as e:
            logger.error("Database error deleting tracking configuration", extra={
                "thread_id": str(thread_id), "error": str(e)
            })
            raise BadRequest("Failed to delete tracking configuration")
        except Exception as e:
            logger.error("Unexpected error deleting tracking configuration", extra={
                "thread_id": str(thread_id), "error": str(e)
            })
            raise BadRequest("Failed to delete tracking configuration")

    @trace_async
    async def is_tracking_enabled(self, thread_id: UUID) -> bool:
        """Check if tracking is enabled for thread with caching."""
        cache_key = TRACKING_CACHE_KEY.format(thread_id=thread_id)

        try:
            # Try cache first
            cached_value = await self.redis.get(cache_key)
            if cached_value is not None:
                return cached_value.lower() == "true"

            # Query database
            stmt = sa.select(
                sa.exists().where(
                    sa.and_(
                        thread_tracking_configurations_table.c.thread_id == thread_id,
                        thread_tracking_configurations_table.c.is_active
                    )
                )
            )
            result = await self.session.execute(stmt)
            is_enabled = result.scalar() or False

            # Cache result
            try:
                await self.redis.set(cache_key, str(is_enabled).lower(), ex=TRACKING_CACHE_TTL)
            except Exception as cache_error:
                logger.warning("Failed to cache tracking status", extra={
                    "thread_id": str(thread_id),
                    "cache_error": str(cache_error),
                    "cache_error_type": type(cache_error).__name__
                })

            return is_enabled
        except Exception as e:
            logger.error("Error checking tracking status", extra={
                "thread_id": str(thread_id), "error": str(e)
            })
            # Fallback to database query without caching on error
            try:
                stmt = sa.select(
                    sa.exists().where(
                        sa.and_(
                            thread_tracking_configurations_table.c.thread_id == thread_id,
                            thread_tracking_configurations_table.c.is_active
                        )
                    )
                )
                result = await self.session.execute(stmt)
                return result.scalar() or False
            except Exception as db_error:
                logger.error("Database fallback failed for tracking status", extra={
                    "thread_id": str(thread_id), "error": str(db_error)
                })
                # Default to False if everything fails
                return False

    async def _invalidate_caches(self, thread_id: UUID, user_id: UUID) -> None:
        """Invalidate related caches with Redis pipeline for efficiency."""
        try:
            client = await self.redis.get_client()
            pipe = client.pipeline()

            thread_cache_key = TRACKING_CACHE_KEY.format(thread_id=thread_id)
            user_cache_key = USER_TRACKING_CACHE_KEY.format(user_id=user_id)

            pipe.delete(thread_cache_key)
            pipe.delete(user_cache_key)

            await pipe.execute()

            logger.debug("Caches invalidated", extra={
                "thread_id": str(thread_id),
                "user_id": str(user_id),
                "keys": [thread_cache_key, user_cache_key]
            })
        except Exception as e:
            logger.warning("Failed to invalidate caches", extra={
                "thread_id": str(thread_id),
                "user_id": str(user_id),
                "error": str(e)
            })
            # Don't raise exception as this is a secondary operation

    async def _invalidate_caches_async(self, thread_id: UUID, user_id: UUID) -> None:
        """Invalidate related caches asynchronously without blocking main flow."""
        try:
            await self._invalidate_caches(thread_id, user_id)
        except Exception as e:
            logger.warning("Background cache invalidation failed", extra={
                "thread_id": str(thread_id),
                "user_id": str(user_id),
                "error": str(e)
            })
            # Don't raise exception as this is a background operation

    async def invalidate_user_cache(self, user_id: UUID) -> None:
        """Invalidate user-specific cache."""
        try:
            user_cache_key = USER_TRACKING_CACHE_KEY.format(user_id=user_id)
            await self.redis.delete(user_cache_key)

            logger.debug("User cache invalidated", extra={
                "user_id": str(user_id),
                "key": user_cache_key
            })
        except Exception as e:
            logger.warning("Failed to invalidate user cache", extra={
                "user_id": str(user_id),
                "error": str(e)
            })

    async def invalidate_thread_cache(self, thread_id: UUID) -> None:
        """Invalidate thread-specific cache."""
        try:
            thread_cache_key = TRACKING_CACHE_KEY.format(thread_id=thread_id)
            await self.redis.delete(thread_cache_key)

            logger.debug("Thread cache invalidated", extra={
                "thread_id": str(thread_id),
                "key": thread_cache_key
            })
        except Exception as e:
            logger.warning("Failed to invalidate thread cache", extra={
                "thread_id": str(thread_id),
                "error": str(e)
            })
