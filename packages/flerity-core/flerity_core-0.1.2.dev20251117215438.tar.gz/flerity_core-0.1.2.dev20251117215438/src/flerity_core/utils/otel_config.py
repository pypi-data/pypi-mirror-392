"""OpenTelemetry configuration for distributed tracing and metrics.

Exports traces to AWS X-Ray and metrics to CloudWatch.
"""

import os

from opentelemetry import metrics, trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_VERSION, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

try:
    from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    OTLP_AVAILABLE = True
except ImportError:
    OTLP_AVAILABLE = False

from flerity_core.utils.logging import get_logger

logger = get_logger(__name__)


def get_resource() -> Resource:
    """Create resource with service information."""
    return Resource.create({
        SERVICE_NAME: os.getenv("OTEL_SERVICE_NAME", "flerity-api"),
        SERVICE_VERSION: os.getenv("APP_VERSION", "1.0.0"),
        "deployment.environment": os.getenv("ENVIRONMENT", "development"),
    })


def setup_tracing() -> TracerProvider:
    """Configure OpenTelemetry tracing."""
    resource = get_resource()
    provider = TracerProvider(resource=resource)

    # Use OTLP exporter if available and configured
    otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")

    if OTLP_AVAILABLE and otlp_endpoint:
        # Export to AWS X-Ray via OTLP
        otlp_exporter = OTLPSpanExporter(
            endpoint=otlp_endpoint,
            insecure=os.getenv("OTEL_EXPORTER_OTLP_INSECURE", "false").lower() == "true"
        )
        provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
        logger.info(f"OpenTelemetry tracing configured with OTLP endpoint: {otlp_endpoint}")
    else:
        # No exporter in development - traces are collected but not exported
        # This avoids verbose console output while keeping instrumentation active
        logger.debug("OpenTelemetry tracing enabled without exporter (development mode)")

    trace.set_tracer_provider(provider)
    return provider


def setup_metrics() -> MeterProvider:
    """Configure OpenTelemetry metrics."""
    resource = get_resource()

    otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")

    if OTLP_AVAILABLE and otlp_endpoint:
        # Export to CloudWatch via OTLP
        otlp_exporter = OTLPMetricExporter(
            endpoint=otlp_endpoint,
            insecure=os.getenv("OTEL_EXPORTER_OTLP_INSECURE", "false").lower() == "true"
        )
        reader = PeriodicExportingMetricReader(otlp_exporter, export_interval_millis=60000)
        logger.info(f"OpenTelemetry metrics configured with OTLP endpoint: {otlp_endpoint}")
        provider = MeterProvider(resource=resource, metric_readers=[reader])
    else:
        # No exporter in development - metrics are collected but not exported
        # This avoids verbose console output while keeping instrumentation active
        logger.debug("OpenTelemetry metrics enabled without exporter (development mode)")
        provider = MeterProvider(resource=resource)

    metrics.set_meter_provider(provider)
    return provider


def instrument_app(app):
    """Instrument FastAPI application with OpenTelemetry."""
    # Instrument FastAPI
    FastAPIInstrumentor.instrument_app(app)
    logger.info("FastAPI instrumented with OpenTelemetry")


def instrument_sqlalchemy(engine):
    """Instrument SQLAlchemy engine with OpenTelemetry."""
    SQLAlchemyInstrumentor().instrument(engine=engine)
    logger.info("SQLAlchemy instrumented with OpenTelemetry")


def instrument_redis():
    """Instrument Redis client with OpenTelemetry."""
    RedisInstrumentor().instrument()
    logger.info("Redis instrumented with OpenTelemetry")


def initialize_otel(app=None, sqlalchemy_engine=None, enable_redis=True):
    """Initialize OpenTelemetry with all instrumentations.
    
    Args:
        app: FastAPI application instance
        sqlalchemy_engine: SQLAlchemy engine instance
        enable_redis: Whether to instrument Redis
    """
    # Setup tracing and metrics
    setup_tracing()
    setup_metrics()

    # Instrument components
    if app:
        instrument_app(app)

    if sqlalchemy_engine:
        instrument_sqlalchemy(sqlalchemy_engine)

    if enable_redis:
        try:
            instrument_redis()
        except Exception as e:
            logger.warning(f"Failed to instrument Redis: {e}")

    logger.info("OpenTelemetry initialization complete")


def get_tracer(name: str):
    """Get a tracer instance."""
    return trace.get_tracer(name)


def get_meter(name: str):
    """Get a meter instance."""
    return metrics.get_meter(name)
