"""Telemetry service using OpenTelemetry for event tracking."""

from __future__ import annotations

from typing import Any

from flerity_core.domain.telemetry.schemas import (
    TelemetryIngestRequest,
    TelemetryIngestResponse,
)
from flerity_core.utils.errors import BadRequest
from flerity_core.utils.logging import get_logger
from flerity_core.utils.otel_config import get_meter, get_tracer
from flerity_core.utils.request_tracking import RequestTracker
from flerity_core.utils.domain_logger import get_domain_logger

logger = get_logger(__name__)
domain_logger = get_domain_logger(__name__)
tracer = get_tracer(__name__)
meter = get_meter(__name__)

# Metrics
telemetry_events_counter = meter.create_counter(
    "telemetry.events.received",
    description="Number of telemetry events received",
    unit="1"
)

telemetry_events_rejected = meter.create_counter(
    "telemetry.events.rejected",
    description="Number of telemetry events rejected",
    unit="1"
)

MAX_EVENTS_PER_BATCH = 100


class TelemetryService:
    """Business logic for telemetry using OpenTelemetry."""

    async def ingest_events(
        self,
        request: TelemetryIngestRequest,
        user_id: str | None = None,
        locale: str = "en-US"
    ) -> TelemetryIngestResponse:
        """Ingest telemetry events and export to OpenTelemetry.
        
        Events are sent as OpenTelemetry spans and metrics instead of database storage.
        """
        with RequestTracker(user_id=user_id, operation="ingest_events") as tracker:
            try:
                tracking_context = domain_logger.operation_start("ingest_events", events_count=len(request.events), locale=locale, user_id=user_id)
                
                events = request.events

                # Validate batch size
                if len(events) > MAX_EVENTS_PER_BATCH:
                    error_msg = f"Batch size cannot exceed {MAX_EVENTS_PER_BATCH}"
                    domain_logger.operation_error(tracking_context, error_msg, {
                        "events_count": len(events),
                        "max_allowed": MAX_EVENTS_PER_BATCH
                    })
                    raise BadRequest(error_msg)

                accepted = 0
                rejected = 0

                for event_data in events:
                    try:
                        # Create span for each event
                        with tracer.start_as_current_span(
                            f"telemetry.{event_data.get('event_type', 'unknown')}",
                            attributes={
                                "user_id": user_id or "anonymous",
                                "device_id": event_data.get("device_id", "unknown"),
                                "session_id": event_data.get("session_id", "unknown"),
                                "platform": event_data.get("platform", "unknown"),
                                "app_version": event_data.get("app_version", "unknown"),
                                "locale": locale,
                                **self._flatten_properties(event_data.get("properties", {}))
                            }
                        ):
                            # Record metric
                            telemetry_events_counter.add(
                                1,
                                {
                                    "event_type": event_data.get("event_type", "unknown"),
                                    "platform": event_data.get("platform", "unknown")
                                }
                            )
                            accepted += 1

                    except Exception as e:
                        logger.warning(f"Failed to process telemetry event: {e}")
                        telemetry_events_rejected.add(1, {"reason": "processing_error"})
                        rejected += 1

                result = TelemetryIngestResponse(
                    ingestion_id="otel",
                    accepted=accepted,
                    duplicates=0,
                    rejected=rejected,
                    received=len(events)
                )
                
                # Business event logging
                domain_logger.business_event("telemetry_events_ingested", {
                    "accepted": accepted,
                    "rejected": rejected,
                    "total_received": len(events),
                    "ingestion_id": "otel",
                    "user_id": user_id,
                    "locale": locale
                })
                
                domain_logger.operation_success(tracking_context, {
                    "accepted": accepted,
                    "rejected": rejected,
                    "total_received": len(events)
                })
                
                tracker.log_success(result_id="otel")
                return result
                
            except Exception as e:
                error_id = tracker.log_error(e, context={
                    "events_count": len(request.events),
                    "locale": locale
                })
                domain_logger.operation_error(tracking_context, str(e), {
                    "error_id": error_id,
                    "events_count": len(request.events)
                })
                raise

    def _flatten_properties(self, properties: dict[str, Any], prefix: str = "prop") -> dict[str, Any]:
        """Flatten nested properties for OpenTelemetry attributes."""
        flattened = {}
        for key, value in properties.items():
            if isinstance(value, (str, int, float, bool)):
                flattened[f"{prefix}.{key}"] = value
            elif isinstance(value, dict):
                flattened.update(self._flatten_properties(value, f"{prefix}.{key}"))
        return flattened


def create_telemetry_service() -> TelemetryService:
    """Factory function to create TelemetryService."""
    return TelemetryService()
