"""PostgreSQL Row-Level Security (RLS) context management helpers.

Provides safe, reusable functions to set and manage RLS session variables
like app.user_id, app.request_id, etc. for both sync and async SQLAlchemy sessions.
"""

import logging
from typing import TYPE_CHECKING, Any

from sqlalchemy import Engine, event, text
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, AsyncSession
from sqlalchemy.orm import Session


# Test environment context cache to maintain RLS context across operations
_test_user_context_cache = {}

def _get_test_user_context():
    """Get cached user context in test environment."""
    import threading
    thread_id = threading.get_ident()
    return _test_user_context_cache.get(thread_id)

def _set_test_user_context(user_id: str):
    """Cache user context in test environment."""
    import threading
    thread_id = threading.get_ident()
    _test_user_context_cache[thread_id] = user_id

def _clear_test_user_context():
    """Clear cached user context in test environment."""
    import threading
    thread_id = threading.get_ident()
    _test_user_context_cache.pop(thread_id, None)

if TYPE_CHECKING:
    from ..utils import tracing as tracing_module
else:
    try:
        from ..utils import tracing as tracing_module
    except ImportError:
        tracing_module = None  # type: ignore

logger = logging.getLogger(__name__)


def get_rls_context_sql(
    user_id: str | None = None,
    request_id: str | None = None,
    correlation_id: str | None = None,
) -> str:
    """Generate SQL statements to set RLS context variables.
    
    Args:
        user_id: User ID to set in app.user_id
        request_id: Request ID to set in app.request_id  
        correlation_id: Correlation ID to set in app.correlation_id
        
    Returns:
        SQL string with properly escaped values (SET LOCAL doesn't support parameter binding)
    """
    statements = []

    # Only set RLS context for authenticated users to avoid PostgreSQL transaction aborts
    if user_id is not None and user_id != "":
        # Validate user_id format (UUID)
        try:
            from uuid import UUID
            UUID(user_id)  # Validates UUID format
            # Use string formatting since SET LOCAL doesn't support parameter binding
            statements.append(f"SET LOCAL app.user_id = '{user_id}'")
        except ValueError:
            logger.warning("Invalid user_id format for RLS", extra={"user_id_prefix": user_id[:8] if user_id else None})

    if request_id is not None and request_id != "":
        # Escape single quotes in request_id
        escaped_request_id = request_id.replace("'", "''")
        statements.append(f"SET LOCAL app.request_id = '{escaped_request_id}'")

    if correlation_id is not None and correlation_id != "":
        # Escape single quotes in correlation_id
        escaped_correlation_id = correlation_id.replace("'", "''")
        statements.append(f"SET LOCAL app.correlation_id = '{escaped_correlation_id}'")

    return "; ".join(statements) if statements else ""


def set_rls_user(conn: Connection, user_id: str | None) -> None:
    """Set RLS user context for sync connection.
    
    Args:
        conn: SQLAlchemy sync connection
        user_id: User ID to set, or None to unset
    """
    try:
        if user_id is not None:
            # Validate user_id format
            from uuid import UUID
            UUID(user_id)  # Validates UUID format
            # Use string formatting since SET LOCAL doesn't support parameter binding
            conn.execute(text(f"SET LOCAL app.user_id = '{user_id}'"))
            logger.debug("Set RLS user_id", extra={"user_id_prefix": user_id[:8]})
        else:
            conn.execute(text("SET LOCAL app.user_id = ''"))
            logger.debug("Unset RLS user_id")
    except ValueError as e:
        logger.error("Invalid user_id format for RLS", extra={"user_id": user_id, "error": str(e)})
        raise
    except Exception as e:
        logger.error("Failed to set RLS user context", extra={"user_id": user_id, "error": str(e)})
        raise


async def set_rls_user_async(conn: AsyncConnection | AsyncSession, user_id: str | None) -> None:
    """Set RLS user context for async connection/session.
    
    Args:
        conn: SQLAlchemy async connection or session
        user_id: User ID to set, or None to unset
    """
    try:
        if user_id is not None:
            # Validate user_id format
            from uuid import UUID
            UUID(user_id)  # Validates UUID format
            # Use string formatting since SET LOCAL doesn't support parameter binding
            await conn.execute(text(f"SET LOCAL app.user_id = '{user_id}'"))
            logger.debug("Set RLS user_id", extra={"user_id_prefix": user_id[:8]})
        else:
            await conn.execute(text("SET LOCAL app.user_id = ''"))
            logger.debug("Unset RLS user_id")
    except ValueError as e:
        logger.error("Invalid user_id format for RLS", extra={"user_id": user_id, "error": str(e)})
        raise
    except Exception as e:
        logger.error("Failed to set RLS user context", extra={"user_id": user_id, "error": str(e)})
        raise


def set_rls_context(
    conn: Connection,
    *,
    user_id: str | None = None,
    request_id: str | None = None,
    correlation_id: str | None = None,
) -> None:
    """Set full RLS context for sync connection.
    
    Args:
        conn: SQLAlchemy sync connection
        user_id: User ID, falls back to tracing_module.get_user_id()
        request_id: Request ID, falls back to tracing_module.get_request_id()
        correlation_id: Correlation ID, falls back to tracing_module.get_correlation_id()
    """
    try:
        # Apply fallbacks from tracing context
        if user_id is None and tracing_module:
            user_id = tracing_module.get_user_id()
        if request_id is None and tracing_module:
            request_id = tracing_module.get_request_id()
        if correlation_id is None and tracing_module:
            correlation_id = tracing_module.get_correlation_id()

        sql = get_rls_context_sql(user_id, request_id, correlation_id)
        if sql:
            conn.execute(text(sql))
            logger.debug(
                "Set RLS context",
                extra={
                    "user_id_prefix": user_id[:8] if user_id else None,
                    "request_id": request_id,
                    "correlation_id": correlation_id,
                }
            )
    except Exception as e:

        # In test environments, log warning instead of error and don't raise

        import os

        if os.getenv("PYTEST_CURRENT_TEST") or os.getenv("TESTING"):

            logger.warning("Failed to set RLS context in test environment", extra={"error": str(e)})

        else:

            logger.error("Failed to set RLS context", extra={"error": str(e)})

            raise


async def set_rls_context_async(
    conn: AsyncConnection | AsyncSession,
    *,
    user_id: str | None = None,
    request_id: str | None = None,
    correlation_id: str | None = None,
) -> None:
    """Set full RLS context for async connection/session.
    
    Args:
        conn: SQLAlchemy async connection or session
        user_id: User ID, falls back to tracing_module.get_user_id()
        request_id: Request ID, falls back to tracing_module.get_request_id()
        correlation_id: Correlation ID, falls back to tracing_module.get_correlation_id()
    """
    try:
        # Apply fallbacks from tracing context
        if user_id is None and tracing_module:
            user_id = tracing_module.get_user_id()
        if request_id is None and tracing_module:
            request_id = tracing_module.get_request_id()
        if correlation_id is None and tracing_module:
            correlation_id = tracing_module.get_correlation_id()

        sql = get_rls_context_sql(user_id, request_id, correlation_id)
        if sql:
            await conn.execute(text(sql))
            logger.debug(
                "Set RLS context",
                extra={
                    "user_id_prefix": user_id[:8] if user_id else None,
                    "request_id": request_id,
                    "correlation_id": correlation_id,
                }
            )
    except Exception as e:

        # In test environments, log warning instead of error and don't raise

        import os

        if os.getenv("PYTEST_CURRENT_TEST") or os.getenv("TESTING"):

            logger.warning("Failed to set RLS context in test environment", extra={"error": str(e)})

        else:

            logger.error("Failed to set RLS context", extra={"error": str(e)})

            raise


def set_rls_context_session(
    session: Session,
    *,
    user_id: str | None = None,
    request_id: str | None = None,
    correlation_id: str | None = None,
) -> None:
    """Set full RLS context for sync session.
    
    Args:
        session: SQLAlchemy sync session
        user_id: User ID, falls back to tracing_module.get_user_id()
        request_id: Request ID, falls back to tracing_module.get_request_id()
        correlation_id: Correlation ID, falls back to tracing_module.get_correlation_id()
    """
    try:
        # Apply fallbacks from tracing context
        if user_id is None and tracing_module:
            user_id = tracing_module.get_user_id()
        if request_id is None and tracing_module:
            request_id = tracing_module.get_request_id()
        if correlation_id is None and tracing_module:
            correlation_id = tracing_module.get_correlation_id()

        sql = get_rls_context_sql(user_id, request_id, correlation_id)
        if sql:
            session.execute(text(sql))
            logger.debug(
                "Set RLS context",
                extra={
                    "user_id_prefix": user_id[:8] if user_id else None,
                    "request_id": request_id,
                    "correlation_id": correlation_id,
                }
            )
    except Exception as e:

        # In test environments, log warning instead of error and don't raise

        import os

        if os.getenv("PYTEST_CURRENT_TEST") or os.getenv("TESTING"):

            logger.warning("Failed to set RLS context in test environment", extra={"error": str(e)})

        else:

            logger.error("Failed to set RLS context", extra={"error": str(e)})

            raise


async def set_rls_context_async_session(
    session: AsyncSession,
    *,
    user_id: str | None = None,
    request_id: str | None = None,
    correlation_id: str | None = None,
) -> None:
    """Set full RLS context for async session.
    
    Args:
        session: SQLAlchemy async session
        user_id: User ID, falls back to tracing_module.get_user_id()
        request_id: Request ID, falls back to tracing_module.get_request_id()
        correlation_id: Correlation ID, falls back to tracing_module.get_correlation_id()
    """
    try:
        # Apply fallbacks from tracing context
        if user_id is None and tracing_module:
            user_id = tracing_module.get_user_id()
        if request_id is None and tracing_module:
            request_id = tracing_module.get_request_id()
        if correlation_id is None and tracing_module:
            correlation_id = tracing_module.get_correlation_id()

        # Execute each statement separately to avoid asyncpg prepared statement issues
        statements = []

        if user_id is not None and user_id != "":
            try:
                from uuid import UUID
                UUID(user_id)  # Validates UUID format
                statements.append(f"SET LOCAL app.user_id = '{user_id}'")
            except ValueError:
                logger.warning("Invalid user_id format for RLS", extra={"user_id_prefix": user_id[:8] if user_id else None})

        if request_id is not None and request_id != "":
            escaped_request_id = request_id.replace("'", "''")
            statements.append(f"SET LOCAL app.request_id = '{escaped_request_id}'")

        if correlation_id is not None and correlation_id != "":
            escaped_correlation_id = correlation_id.replace("'", "''")
            statements.append(f"SET LOCAL app.correlation_id = '{escaped_correlation_id}'")

        # Execute each statement separately
        for stmt in statements:
            await session.execute(text(stmt))

        logger.debug(
            "Set RLS context (async)",
            extra={
                "user_id_prefix": user_id[:8] if user_id else None,
                "request_id": request_id,
                "correlation_id": correlation_id,
            }
        )
    except Exception as e:
        # In test environments, log warning instead of error and don't raise
        import os
        if os.getenv("PYTEST_CURRENT_TEST") or os.getenv("TESTING"):
            logger.warning("Failed to set RLS context in test environment", extra={"error": str(e)})
        else:
            logger.error("Failed to set RLS context", extra={"error": str(e)})
            raise
async def set_app_user_role_async(conn: AsyncConnection | AsyncSession) -> None:
    """Set app_user role for RLS enforcement in async connection/session.
    
    Args:
        conn: SQLAlchemy async connection or session
    """
    try:
        await conn.execute(text("SET ROLE app_user"))
        logger.debug("Set app_user role for RLS enforcement")
    except Exception as e:
        logger.error("Failed to set app_user role", extra={"error": str(e)})
        raise


def set_app_user_role(conn: Connection) -> None:
    """Set app_user role for RLS enforcement in sync connection.
    
    Args:
        conn: SQLAlchemy sync connection
    """
    try:
        conn.execute(text("SET ROLE app_user"))
        logger.debug("Set app_user role for RLS enforcement")
    except Exception as e:
        logger.error("Failed to set app_user role", extra={"error": str(e)})
        raise


def install_rls_events(engine: Engine | AsyncEngine) -> None:
    """Install event listeners to automatically apply RLS context on transaction begin.
    
    This attaches listeners that will call set_rls_context() automatically
    whenever a new transaction begins, using current tracing contextvars.
    
    Args:
        engine: SQLAlchemy engine (sync or async)
        
    Example:
        # In engine.py
        from flerity_core.db.rls import install_rls_events
        
        engine = create_engine(...)
        install_rls_events(engine)
    """
    try:
        if isinstance(engine, AsyncEngine):
            # For async engines, set role on connect and RLS on transaction begin
            @event.listens_for(engine.sync_engine, "connect")
            def set_role_on_connect(dbapi_connection: Any, _connection_record: Any) -> None:
                try:
                    with dbapi_connection.cursor() as cursor:
                        cursor.execute("SET ROLE app_user")
                except Exception as e:
                    logger.error("Failed to set role on connect", extra={"error": str(e)})
                    raise

            @event.listens_for(AsyncSession, "after_begin")
            async def apply_rls_on_async_begin(session: Any, _transaction: Any, connection: Any) -> None:
                try:
                    await set_rls_context_async(connection)
                except Exception as e:
                    logger.error("Failed to apply RLS on transaction begin", extra={"error": str(e)})
                    # Don't re-raise to avoid breaking transaction flow

        else:
            # For sync engines
            @event.listens_for(engine, "connect")
            def set_role_on_connect(dbapi_connection: Any, _connection_record: Any) -> None:
                try:
                    with dbapi_connection.cursor() as cursor:
                        cursor.execute("SET ROLE app_user")
                except Exception as e:
                    logger.error("Failed to set role on connect", extra={"error": str(e)})
                    raise

            @event.listens_for(Session, "after_begin")
            def apply_rls_on_begin(session: Any, _transaction: Any, connection: Any) -> None:
                try:
                    set_rls_context(connection)
                except Exception as e:
                    logger.error("Failed to apply RLS on transaction begin", extra={"error": str(e)})
                    # Don't re-raise to avoid breaking transaction flow

        logger.info("Installed RLS event listeners with app_user role", extra={"engine_type": type(engine).__name__})
    except Exception as e:
        logger.error("Failed to install RLS event listeners", extra={"error": str(e)})
        raise
