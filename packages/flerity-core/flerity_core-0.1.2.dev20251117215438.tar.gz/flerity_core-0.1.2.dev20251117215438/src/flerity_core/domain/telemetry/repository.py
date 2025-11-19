"""Telemetry repository for event ingestion and querying."""

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.engine import CursorResult
from sqlalchemy.ext.asyncio import AsyncSession

from ...utils.errors import BadRequest, FailedDependency, NotFound
from ...utils.tracing import trace_async
from ...utils.request_tracking import RequestTracker
from ...utils.domain_logger import get_domain_logger
from .schemas import TelemetryEventCreate, TelemetryEventOut, telemetry_events_table

domain_logger = get_domain_logger(__name__)


class TelemetryRepository:
    """Repository for telemetry event management."""

    def __init__(self, session: AsyncSession):
        self.session = session

    @trace_async
    async def get_by_id(self, event_id: UUID) -> TelemetryEventOut:
        """Get telemetry event by ID."""
        stmt = sa.select(telemetry_events_table).where(
            telemetry_events_table.c.event_id == event_id
        )
        result = await self.session.execute(stmt)
        row = result.fetchone()
        if not row:
            raise NotFound(f"Telemetry event {event_id} not found")
        return TelemetryEventOut.model_validate(row._asdict())

    @trace_async
    async def get_by_user(
        self,
        user_id: str,
        limit: int = 100,
        event_type: str | None = None,
        since: datetime | None = None
    ) -> list[TelemetryEventOut]:
        """Get telemetry events for user (pseudonymized user_id)."""
        if limit > 1000:
            raise BadRequest("Limit cannot exceed 1000")
        if limit <= 0:
            raise BadRequest("Limit must be positive")

        stmt = sa.select(telemetry_events_table).where(
            telemetry_events_table.c.user_id == user_id
        )

        if event_type:
            stmt = stmt.where(telemetry_events_table.c.event_type == event_type)

        if since:
            stmt = stmt.where(telemetry_events_table.c.timestamp >= since)

        stmt = stmt.order_by(telemetry_events_table.c.timestamp.desc()).limit(limit)

        result = await self.session.execute(stmt)
        return [TelemetryEventOut.model_validate(row._asdict()) for row in result.fetchall()]

    @trace_async
    async def get_by_session(self, session_id: str) -> list[TelemetryEventOut]:
        """Get all events for a session."""
        stmt = (
            sa.select(telemetry_events_table)
            .where(telemetry_events_table.c.session_id == session_id)
            .order_by(telemetry_events_table.c.timestamp)
        )
        result = await self.session.execute(stmt)
        return [TelemetryEventOut.model_validate(row._asdict()) for row in result.fetchall()]

    @trace_async
    async def create(self, data: TelemetryEventCreate, locale: str = "en-US") -> TelemetryEventOut:
        """Create new telemetry event."""
        with RequestTracker(operation="create_telemetry_event") as tracker:
            try:
                tracking_context = domain_logger.operation_start("create_telemetry_event", event_type=data.event_type, user_id=data.user_id, session_id=data.session_id, locale=locale)
                
                from ...utils.i18n import t

                event_data = data.model_dump()

                # Generate event_id if not provided
                if not event_data.get('event_id'):
                    event_data['event_id'] = uuid4()

                # Set received_at timestamp with timezone
                event_data['received_at'] = datetime.now(UTC)

                stmt = sa.insert(telemetry_events_table).values(**event_data).returning(telemetry_events_table)
                result = await self.session.execute(stmt)
                row = result.fetchone()
                if row is None:
                    raise FailedDependency(t("telemetry.error.ingestion_failed", locale=locale))
                
                telemetry_event = TelemetryEventOut.model_validate(row._asdict())
                
                # Business event logging
                domain_logger.business_event("telemetry_event_created", {
                    "event_id": str(telemetry_event.event_id),
                    "event_type": telemetry_event.event_type,
                    "user_id": telemetry_event.user_id,
                    "session_id": telemetry_event.session_id
                })
                
                domain_logger.operation_success(tracking_context, {
                    "event_id": str(telemetry_event.event_id),
                    "event_type": telemetry_event.event_type
                })
                
                tracker.log_success(result_id=str(telemetry_event.event_id))
                return telemetry_event
                
            except sa.exc.IntegrityError as e:
                error_id = tracker.log_error(e, context={"event_type": data.event_type})
                domain_logger.operation_error(tracking_context, str(e), {
                    "error_id": error_id,
                    "event_type": data.event_type
                })
                raise BadRequest(t("telemetry.error.ingestion_failed", locale=locale))
            except Exception as e:
                error_id = tracker.log_error(e, context={"event_type": data.event_type})
                domain_logger.operation_error(tracking_context, str(e), {
                    "error_id": error_id,
                    "event_type": data.event_type
                })
                raise

    @trace_async
    async def create_batch(self, events: list[TelemetryEventCreate], locale: str = "en-US") -> list[TelemetryEventOut]:
        """Create multiple telemetry events in batch."""
        with RequestTracker(operation="create_telemetry_events_batch") as tracker:
            try:
                tracking_context = domain_logger.operation_start("create_telemetry_events_batch", events_count=len(events), locale=locale)
                
                from ...utils.i18n import t

                if not events:
                    return []

                if len(events) > 100:
                    raise BadRequest(t("telemetry.error.ingestion_failed", locale=locale))

                events_data = []
                received_at = datetime.now(UTC)

                for event in events:
                    event_data = event.model_dump()
                    # Generate event_id if not provided
                    if not event_data.get('event_id'):
                        event_data['event_id'] = uuid4()
                    # Set received_at timestamp with timezone
                    event_data['received_at'] = received_at
                    events_data.append(event_data)

                stmt = sa.insert(telemetry_events_table).values(events_data).returning(telemetry_events_table)
                result = await self.session.execute(stmt)
                telemetry_events = [TelemetryEventOut.model_validate(row._asdict()) for row in result.fetchall()]
                
                # Business event logging
                domain_logger.business_event("telemetry_events_batch_created", {
                    "events_count": len(telemetry_events),
                    "event_types": list(set(event.event_type for event in telemetry_events)),
                    "batch_size": len(events)
                })
                
                domain_logger.operation_success(tracking_context, {
                    "events_count": len(telemetry_events),
                    "batch_size": len(events)
                })
                
                tracker.log_success(result_id=f"batch_{len(telemetry_events)}")
                return telemetry_events
                
            except sa.exc.IntegrityError as e:
                error_id = tracker.log_error(e, context={"events_count": len(events)})
                domain_logger.operation_error(tracking_context, str(e), {
                    "error_id": error_id,
                    "events_count": len(events)
                })
                raise BadRequest(t("telemetry.error.ingestion_failed", locale=locale))
            except Exception as e:
                error_id = tracker.log_error(e, context={"events_count": len(events)})
                domain_logger.operation_error(tracking_context, str(e), {
                    "error_id": error_id,
                    "events_count": len(events)
                })
                raise

    @trace_async
    async def count_by_type(self, event_type: str, since: datetime | None = None) -> int:
        """Count events by type, optionally since a timestamp."""
        stmt = sa.select(sa.func.count()).select_from(telemetry_events_table).where(
            telemetry_events_table.c.event_type == event_type
        )

        if since:
            stmt = stmt.where(telemetry_events_table.c.timestamp >= since)

        result = await self.session.execute(stmt)
        return result.scalar() or 0

    @trace_async
    async def get_event_stats(self, since: datetime | None = None) -> dict[str, int]:
        """Get event count statistics by type."""
        stmt = (
            sa.select(
                telemetry_events_table.c.event_type,
                sa.func.count().label("count")
            )
            .select_from(telemetry_events_table)
            .group_by(telemetry_events_table.c.event_type)
        )

        if since:
            stmt = stmt.where(telemetry_events_table.c.timestamp >= since)

        result = await self.session.execute(stmt)
        return {row[0]: row[1] for row in result.fetchall()}

    @trace_async
    async def cleanup_old_events(self, older_than: datetime, batch_size: int = 1000) -> int:
        """Delete events older than specified timestamp in batches."""
        if batch_size <= 0 or batch_size > 10000:
            raise BadRequest("Batch size must be between 1 and 10000")

        total_deleted = 0

        while True:
            # Delete in batches using subquery (PostgreSQL compatible)
            subquery = (
                sa.select(telemetry_events_table.c.id)
                .where(telemetry_events_table.c.timestamp < older_than)
                .limit(batch_size)
            )
            stmt = (
                sa.delete(telemetry_events_table)
                .where(telemetry_events_table.c.id.in_(subquery))
            )
            result: CursorResult[Any] = await self.session.execute(stmt)  # type: ignore[assignment]
            deleted_count = result.rowcount or 0
            total_deleted += deleted_count

            # If we deleted fewer than batch_size, we're done
            if deleted_count < batch_size:
                break

        return total_deleted
