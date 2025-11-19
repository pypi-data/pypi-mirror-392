"""Request-scoped context via contextvars with logging, HTTP headers, and async task propagation.

Provides centralized request_id, correlation_id, user_id, locale, timezone management
with safe propagation across asyncio tasks and background jobs.
"""

from __future__ import annotations

import asyncio
import contextvars
import logging
from collections.abc import AsyncGenerator, Awaitable, Callable, Generator, Mapping
from contextlib import asynccontextmanager, contextmanager
from contextvars import ContextVar, Token
from dataclasses import dataclass
from typing import (
    Any,
    TypeVar,
)

# Optional OpenTelemetry imports
try:
    from opentelemetry import trace  # type: ignore[import-not-found]
    from opentelemetry.trace import Tracer  # type: ignore[import-not-found]
except ImportError:
    trace = None
    Tracer = Any

# Context Variables
cv_request_id: ContextVar[str | None] = ContextVar("request_id", default=None)
cv_correlation_id: ContextVar[str | None] = ContextVar("correlation_id", default=None)
cv_user_id: ContextVar[str | None] = ContextVar("user_id", default=None)
cv_locale: ContextVar[str | None] = ContextVar("locale", default=None)
cv_timezone: ContextVar[str | None] = ContextVar("timezone", default=None)
cv_trace_id: ContextVar[str | None] = ContextVar("trace_id", default=None)

# Header constants
HDR_REQUEST_ID = "X-Request-Id"
HDR_CORRELATION_ID = "X-Correlation-Id"
HDR_USER_ID = "X-User-Id"
HDR_LOCALE = "Accept-Language"
HDR_TIMEZONE = "X-Timezone"


@dataclass
class TraceContext:
    """Represents trace context with trace_id and span_id."""
    trace_id: str | None = None
    span_id: str | None = None

    @classmethod
    def from_headers(cls, headers: Mapping[str, str]) -> TraceContext:
        """Create TraceContext from HTTP headers."""
        header_map = {k.lower(): v for k, v in headers.items()}
        return cls(
            trace_id=header_map.get("x-trace-id"),
            span_id=header_map.get("x-span-id")
        )

    def to_headers(self) -> dict[str, str]:
        """Convert TraceContext to HTTP headers."""
        headers = {}
        if self.trace_id:
            headers["X-Trace-Id"] = self.trace_id
        if self.span_id:
            headers["X-Span-Id"] = self.span_id
        return headers


# Getters
def get_request_id() -> str | None:
    """Get current request ID from context."""
    return cv_request_id.get()


def get_correlation_id() -> str | None:
    """Get current correlation ID from context."""
    return cv_correlation_id.get()


def get_user_id() -> str | None:
    """Get current user ID from context."""
    return cv_user_id.get()


def get_locale() -> str | None:
    """Get current locale from context."""
    return cv_locale.get()


def get_timezone() -> str | None:
    """Get current timezone from context."""
    return cv_timezone.get()


def get_trace_id() -> str | None:
    """Get current trace ID from context."""
    return cv_trace_id.get()


# Setters
def set_request_id(v: str | None) -> Token[str | None]:
    """Set request ID in context, returning reset token."""
    return cv_request_id.set(v)


def set_correlation_id(v: str | None) -> Token[str | None]:
    """Set correlation ID in context, returning reset token."""
    return cv_correlation_id.set(v)


def set_user_id(v: str | None) -> Token[str | None]:
    """Set user ID in context, returning reset token."""
    return cv_user_id.set(v)


def set_locale(v: str | None) -> Token[str | None]:
    """Set locale in context, returning reset token."""
    return cv_locale.set(v)


def set_timezone(v: str | None) -> Token[str | None]:
    """Set timezone in context, returning reset token."""
    return cv_timezone.set(v)


def set_trace_id(v: str | None) -> Token[str | None]:
    """Set trace ID in context, returning reset token."""
    return cv_trace_id.set(v)


# Resetters
def reset_request_id(tok: Token[str | None]) -> None:
    """Reset request ID using token."""
    cv_request_id.reset(tok)


def reset_correlation_id(tok: Token[str | None]) -> None:
    """Reset correlation ID using token."""
    cv_correlation_id.reset(tok)


def reset_user_id(tok: Token[str | None]) -> None:
    """Reset user ID using token."""
    cv_user_id.reset(tok)


def reset_locale(tok: Token[str | None]) -> None:
    """Reset locale using token."""
    cv_locale.reset(tok)


def reset_timezone(tok: Token[str | None]) -> None:
    """Reset timezone using token."""
    cv_timezone.reset(tok)


def reset_trace_id(tok: Token[str | None]) -> None:
    """Reset trace ID using token."""
    cv_trace_id.reset(tok)


def clear_trace_id() -> None:
    """Clear trace ID from context."""
    cv_trace_id.set(None)


# Bulk operations
def get_context() -> dict[str, str]:
    """Get all non-None context values as dict."""
    context = {}
    if request_id := get_request_id():
        context["request_id"] = request_id
    if correlation_id := get_correlation_id():
        context["correlation_id"] = correlation_id
    if user_id := get_user_id():
        context["user_id"] = user_id
    if locale := get_locale():
        context["locale"] = locale
    if timezone := get_timezone():
        context["timezone"] = timezone
    if trace_id := get_trace_id():
        context["trace_id"] = trace_id
    return context


def set_context(**kwargs: str | None) -> dict[str, Token[str | None]]:
    """Set multiple context values, returning tokens by key."""
    tokens = {}
    if "request_id" in kwargs:
        tokens["request_id"] = set_request_id(kwargs["request_id"])
    if "correlation_id" in kwargs:
        tokens["correlation_id"] = set_correlation_id(kwargs["correlation_id"])
    if "user_id" in kwargs:
        tokens["user_id"] = set_user_id(kwargs["user_id"])
    if "locale" in kwargs:
        tokens["locale"] = set_locale(kwargs["locale"])
    if "timezone" in kwargs:
        tokens["timezone"] = set_timezone(kwargs["timezone"])
    if "trace_id" in kwargs:
        tokens["trace_id"] = set_trace_id(kwargs["trace_id"])
    return tokens


def reset_context(tokens: Mapping[str, Token[str | None]]) -> None:
    """Reset multiple context values using tokens."""
    if "request_id" in tokens:
        reset_request_id(tokens["request_id"])
    if "correlation_id" in tokens:
        reset_correlation_id(tokens["correlation_id"])
    if "user_id" in tokens:
        reset_user_id(tokens["user_id"])
    if "locale" in tokens:
        reset_locale(tokens["locale"])
    if "timezone" in tokens:
        reset_timezone(tokens["timezone"])
    if "trace_id" in tokens:
        reset_trace_id(tokens["trace_id"])


# Context managers
@contextmanager
def ctx(**kwargs: str | None) -> Generator[None, None, None]:
    """Context manager to set multiple values, auto-reset on exit."""
    tokens = set_context(**kwargs)
    try:
        yield
    finally:
        reset_context(tokens)


@asynccontextmanager
async def actx(**kwargs: str | None) -> AsyncGenerator[None, None]:
    """Async context manager to set multiple values, auto-reset on exit."""
    tokens = set_context(**kwargs)
    try:
        yield
    finally:
        reset_context(tokens)


# Async task propagation
def spawn_task(coro: Any, *, name: str | None = None) -> asyncio.Task[Any]:
    """Create task that captures current context and runs coro inside it."""
    context = contextvars.copy_context()

    async def runner() -> Any:
        return await coro

    return asyncio.create_task(context.run(lambda: runner()), name=name)


def run_in_context(fn: Callable[..., Any], /, *args: Any, **kwargs: Any) -> Any:
    """Execute callable in a copied context."""
    context = contextvars.copy_context()
    return context.run(fn, *args, **kwargs)


# HTTP headers interop
def apply_incoming_headers(headers: Mapping[str, str], *, prefer_existing: bool = True) -> None:
    """Extract context from incoming headers, optionally preserving existing values."""
    # Create case-insensitive header lookup
    header_map = {k.lower(): v for k, v in headers.items()}

    def maybe_set(cv_setter: Any, header_key: str, current_getter: Any) -> None:
        if header_key.lower() in header_map:
            value = header_map[header_key.lower()].strip()
            if value and (not prefer_existing or current_getter() is None):
                cv_setter(value)

    maybe_set(set_request_id, HDR_REQUEST_ID, get_request_id)
    maybe_set(set_correlation_id, HDR_CORRELATION_ID, get_correlation_id)
    maybe_set(set_user_id, HDR_USER_ID, get_user_id)
    maybe_set(set_locale, HDR_LOCALE, get_locale)
    maybe_set(set_timezone, HDR_TIMEZONE, get_timezone)


def prepare_outgoing_headers(extra: Mapping[str, str] | None = None) -> dict[str, str]:
    """Build headers from current context plus extra, omitting None values."""
    headers = {}

    if request_id := get_request_id():
        headers[HDR_REQUEST_ID] = request_id
    if correlation_id := get_correlation_id():
        headers[HDR_CORRELATION_ID] = correlation_id
    if user_id := get_user_id():
        headers[HDR_USER_ID] = user_id
    if locale := get_locale():
        headers[HDR_LOCALE] = locale
    if timezone := get_timezone():
        headers[HDR_TIMEZONE] = timezone

    if extra:
        headers.update(extra)

    return headers


# Logging integration
def record_log_context(record: dict[str, Any]) -> dict[str, Any]:
    """Merge current context keys into log record (non-destructive)."""
    result = record.copy()
    result.update(get_context())
    return result


class ContextLoggingFilter(logging.Filter):
    """Logging filter that injects context into log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        context = get_context()
        for key, value in context.items():
            setattr(record, key, value)
        return True


def logging_filter_factory() -> logging.Filter:
    """Create logging filter that injects context into log records."""
    return ContextLoggingFilter()


def structlog_processor(event_dict: dict[str, Any]) -> dict[str, Any]:
    """Structlog processor to merge context into event dict."""
    context = get_context()
    # Context values take precedence over existing keys
    return {**event_dict, **context}


# Correlation utilities
def ensure_correlation_id(generator: Callable[[], str]) -> str:
    """Ensure correlation ID is set, generating if needed."""
    if correlation_id := get_correlation_id():
        return correlation_id

    new_id = generator()
    set_correlation_id(new_id)
    return new_id


def ensure_request_id(generator: Callable[[], str]) -> str:
    """Ensure request ID is set, generating if needed."""
    if request_id := get_request_id():
        return request_id

    new_id = generator()
    set_request_id(new_id)
    return new_id


# OpenTelemetry utilities
def get_tracer(name: str | None = None) -> Tracer | None:
    """Get OpenTelemetry tracer with consistent naming."""
    try:
        from opentelemetry import trace
        tracer_name = name or "flerity_core"
        return trace.get_tracer(tracer_name)
    except ImportError:
        return None


# Module-level tracer and trace for testing compatibility
tracer = get_tracer()
try:
    from opentelemetry import trace
except ImportError:
    trace = None


def otel_span_attrs() -> dict[str, str]:
    """Get context attributes suitable for OpenTelemetry spans."""
    attrs = {}
    if request_id := get_request_id():
        attrs["request_id"] = request_id
    if correlation_id := get_correlation_id():
        attrs["correlation_id"] = correlation_id
    if user_id := get_user_id():
        attrs["user_id"] = user_id
    return attrs


@contextmanager
def trace_span(operation_name: str, tracer_name: str | None = None, **attrs: Any) -> Generator[Any, None, None]:
    """Context manager for creating OpenTelemetry spans with flerity context."""
    current_tracer = tracer if tracer else get_tracer(tracer_name)
    if not current_tracer:
        yield None
        return

    # Try to use OpenTelemetry if available, otherwise work with mocked tracer
    try:
        from opentelemetry import trace as otel_trace

        with current_tracer.start_as_current_span(operation_name) as span:
            # Add context attributes
            span_attrs = otel_span_attrs()
            span_attrs["operation.name"] = operation_name
            span_attrs.update(attrs)

            for key, value in span_attrs.items():
                span.set_attribute(key, str(value))

            try:
                yield span
            except Exception as e:
                if span and span.is_recording():
                    span.set_status(otel_trace.Status(otel_trace.StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                raise
    except ImportError:
        # OpenTelemetry not available, work with mocked tracer for testing
        span = current_tracer.start_span(operation_name)
        try:
            yield span
        finally:
            # Try to call __exit__ if it exists (for proper mocks)
            if hasattr(span, '__exit__'):
                span.__exit__(None, None, None)


@asynccontextmanager
async def atrace_span(operation_name: str, tracer_name: str | None = None, **attrs: Any) -> AsyncGenerator[Any, None]:
    """Async context manager for creating OpenTelemetry spans with flerity context."""
    current_tracer = get_tracer(tracer_name)
    if not current_tracer:
        yield None
        return

    try:
        from opentelemetry import trace
    except ImportError:
        yield None
        return

    with current_tracer.start_as_current_span(operation_name) as span:
        # Add context attributes
        span_attrs = otel_span_attrs()
        span_attrs["operation.name"] = operation_name
        span_attrs.update(attrs)

        for key, value in span_attrs.items():
            span.set_attribute(key, str(value))

        try:
            yield span
        except Exception as e:
            if span and span.is_recording():
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                span.record_exception(e)
            raise


def trace_operation(operation_name: str) -> Callable[[Callable[..., _T]], Callable[..., _T]]:
    """OpenTelemetry tracing decorator for operations with context integration."""
    def decorator(func: Callable[..., _T]) -> Callable[..., _T]:
        if asyncio.iscoroutinefunction(func):
            from functools import wraps

            @wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                try:
                    from opentelemetry import trace
                    tracer = trace.get_tracer(__name__)

                    with tracer.start_as_current_span(operation_name) as span:
                        # Add context attributes
                        span_attrs = otel_span_attrs()
                        span_attrs["operation.name"] = operation_name
                        span_attrs["function.name"] = func.__name__
                        span_attrs["function.module"] = func.__module__

                        for key, value in span_attrs.items():
                            span.set_attribute(key, value)

                        try:
                            result = await func(*args, **kwargs)
                            span.set_status(trace.Status(trace.StatusCode.OK))
                            return result
                        except Exception as e:
                            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                            span.record_exception(e)
                            raise
                except ImportError:
                    # OpenTelemetry not available, run function normally
                    return await func(*args, **kwargs)

            async_wrapper.__wrapped__ = func
            return async_wrapper
        else:
            from functools import wraps

            @wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                try:
                    from opentelemetry import trace
                    tracer = trace.get_tracer(__name__)

                    with tracer.start_as_current_span(operation_name) as span:
                        # Add context attributes
                        span_attrs = otel_span_attrs()
                        span_attrs["operation.name"] = operation_name
                        span_attrs["function.name"] = func.__name__
                        span_attrs["function.module"] = func.__module__

                        for key, value in span_attrs.items():
                            span.set_attribute(key, value)

                        try:
                            result = func(*args, **kwargs)
                            span.set_status(trace.Status(trace.StatusCode.OK))
                            return result
                        except Exception as e:
                            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                            span.record_exception(e)
                            raise
                except ImportError:
                    # OpenTelemetry not available, run function normally
                    return func(*args, **kwargs)

            sync_wrapper.__wrapped__ = func
            return sync_wrapper

    return decorator


def inject_otel_current_span(attrs: Mapping[str, str] | None = None) -> None:
    """Inject context into current OpenTelemetry span (no-op if OTel not available)."""
    try:
        from opentelemetry import trace

        span = trace.get_current_span()
        if span and span.is_recording():
            # Add context attributes
            span_attrs = otel_span_attrs()
            if attrs:
                span_attrs.update(attrs)

            for key, value in span_attrs.items():
                span.set_attribute(key, value)
    except ImportError:
        # OpenTelemetry not available, silently ignore
        pass
    except Exception:
        # Any other error with span injection, silently ignore to avoid breaking operations
        pass


def start_span(name: str) -> Any:
    """Start a new tracing span."""
    try:
        current_tracer = tracer if tracer else get_tracer()
        if current_tracer:
            return current_tracer.start_span(name)
        return None
    except ImportError:
        return None


def end_span(span: Any) -> None:
    """End a tracing span."""
    if span and hasattr(span, 'end'):
        span.end()


def set_span_attributes(span: Any, attributes: dict[str, Any]) -> None:
    """Set attributes on a span."""
    if not span or not attributes:
        return

    for key, value in attributes.items():
        if value is not None and hasattr(span, 'set_attribute'):
            span.set_attribute(key, str(value))


def get_current_span() -> Any:
    """Get current OpenTelemetry span."""
    try:
        if trace:
            return trace.get_current_span()
        else:
            from opentelemetry import trace as otel_trace
            return otel_trace.get_current_span()
    except ImportError:
        return None


def add_trace_attribute(key: str, value: Any) -> None:
    """Add attribute to current OpenTelemetry span."""
    span = get_current_span()
    if span and span.is_recording():
        span.set_attribute(key, str(value))


def create_child_span(name: str, attributes: dict[str, Any] | None = None) -> Any:
    """Create a child span from current span."""
    try:
        current_tracer = tracer if tracer else get_tracer()
        if not current_tracer:
            return None

        parent = get_current_span()
        span = current_tracer.start_span(name, parent=parent)

        if attributes:
            for key, value in attributes.items():
                span.set_attribute(key, str(value))

        return span
    except ImportError:
        return None



_T = TypeVar('_T')

def trace_async(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
    """Async tracing decorator - simplified version to avoid type issues."""
    # For production readiness, return function as-is
    # TODO: Implement proper OpenTelemetry tracing with correct type handling
    return func
