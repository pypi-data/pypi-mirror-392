"""
Database interaction type protocols for framework-agnostic typing.

Provides lightweight Protocol interfaces that mirror SQLAlchemy 2.x surface area
without importing SQLAlchemy in every file. Supports both sync and async variants.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Protocol, TypeVar, cast

# JSON-compatible type aliases
JSONScalar = str | int | float | bool | None
JSON = JSONScalar | dict[str, "JSON"] | list["JSON"]
StrDict = dict[str, str]
AnyMapping = Mapping[str, Any]
RowLike = Mapping[str, Any]

T = TypeVar("T")


class CursorResultP(Protocol):
    """Sync cursor result protocol for database query results.
    
    Provides type-safe interface for SQLAlchemy cursor results without
    importing SQLAlchemy in every file that needs database typing.
    """

    rowcount: int

    def fetchone(self) -> RowLike | None:
        """Fetch one row or None if no rows available."""
        ...

    def fetchall(self) -> list[RowLike]:
        """Fetch all remaining rows."""
        ...

    def first(self) -> RowLike | None:
        """Fetch first row or None."""
        ...

    def scalar(self) -> Any:
        """Fetch scalar value from first column of first row."""
        ...

    def scalars(self) -> list[Any]:
        """Fetch all scalar values from first column."""
        ...


class AsyncCursorResultP(Protocol):
    """Async cursor result protocol for database query results.
    
    Provides type-safe interface for SQLAlchemy async cursor results.
    """

    rowcount: int

    async def fetchone(self) -> RowLike | None:
        """Fetch one row or None if no rows available."""
        ...

    async def fetchall(self) -> list[RowLike]:
        """Fetch all remaining rows."""
        ...

    async def first(self) -> RowLike | None:
        """Fetch first row or None."""
        ...

    async def scalar(self) -> Any:
        """Fetch scalar value from first column of first row."""
        ...

    async def scalars(self) -> list[Any]:
        """Fetch all scalar values from first column."""
        ...


class TransactionP(Protocol):
    """Sync transaction protocol for database transactions.
    
    Provides interface for transaction lifecycle management.
    """

    def commit(self) -> None:
        """Commit the transaction."""
        ...

    def rollback(self) -> None:
        """Rollback the transaction."""
        ...

    def close(self) -> None:
        """Close the transaction."""
        ...


class AsyncTransactionP(Protocol):
    """Async transaction protocol for database transactions.
    
    Provides interface for async transaction lifecycle management.
    """

    async def commit(self) -> None:
        """Commit the transaction."""
        ...

    async def rollback(self) -> None:
        """Rollback the transaction."""
        ...

    async def close(self) -> None:
        """Close the transaction."""
        ...


class ConnectionP(Protocol):
    """Sync database connection protocol.
    
    Provides interface for database connection operations.
    """

    def execute(self, statement: Any, /, *args: Any, **kwargs: Any) -> CursorResultP:
        """Execute a SQL statement."""
        ...

    def begin(self) -> TransactionP:
        """Begin a new transaction."""
        ...

    def begin_nested(self) -> TransactionP:
        """Begin a nested transaction (savepoint)."""
        ...

    def close(self) -> None:
        """Close the connection."""
        ...

    @property
    def closed(self) -> bool:
        """True if connection is closed."""
        ...


class AsyncConnectionP(Protocol):
    """Async database connection protocol.
    
    Provides interface for async database connection operations.
    """

    async def execute(self, statement: Any, /, *args: Any, **kwargs: Any) -> AsyncCursorResultP:
        """Execute a SQL statement asynchronously."""
        ...

    async def begin(self) -> AsyncTransactionP:
        """Begin a new transaction."""
        ...

    async def begin_nested(self) -> AsyncTransactionP:
        """Begin a nested transaction (savepoint)."""
        ...

    async def close(self) -> None:
        """Close the connection."""
        ...

    @property
    def closed(self) -> bool:
        """True if connection is closed."""
        ...


class SessionP(Protocol):
    """Sync database session protocol.
    
    Provides interface for SQLAlchemy session operations with transaction management.
    """

    def execute(self, statement: Any, /, *args: Any, **kwargs: Any) -> CursorResultP:
        """Execute a SQL statement."""
        ...

    def begin(self) -> TransactionP:
        """Begin a new transaction."""
        ...

    def begin_nested(self) -> TransactionP:
        """Begin a nested transaction (savepoint)."""
        ...

    def commit(self) -> None:
        """Commit the current transaction."""
        ...

    def rollback(self) -> None:
        """Rollback the current transaction."""
        ...

    def close(self) -> None:
        """Close the session."""
        ...

    def connection(self) -> ConnectionP:
        """Get the underlying connection."""
        ...

    @property
    def bind(self) -> EngineP | None:
        """The engine bound to this session."""
        ...

    @property
    def in_transaction(self) -> bool:
        """True if session is in a transaction."""
        ...

    @property
    def closed(self) -> bool:
        """True if session is closed."""
        ...


class AsyncSessionP(Protocol):
    """Async database session protocol.
    
    Provides interface for SQLAlchemy async session operations with transaction management.
    """

    async def execute(self, statement: Any, /, *args: Any, **kwargs: Any) -> AsyncCursorResultP:
        """Execute a SQL statement asynchronously."""
        ...

    async def begin(self) -> AsyncTransactionP:
        """Begin a new transaction."""
        ...

    async def begin_nested(self) -> AsyncTransactionP:
        """Begin a nested transaction (savepoint)."""
        ...

    async def commit(self) -> None:
        """Commit the current transaction."""
        ...

    async def rollback(self) -> None:
        """Rollback the current transaction."""
        ...

    async def close(self) -> None:
        """Close the session."""
        ...

    async def connection(self) -> AsyncConnectionP:
        """Get the underlying connection."""
        ...

    @property
    def bind(self) -> AsyncEngineP | None:
        """The engine bound to this session."""
        ...

    @property
    def in_transaction(self) -> bool:
        """True if session is in a transaction."""
        ...

    @property
    def closed(self) -> bool:
        """True if session is closed."""
        ...


class EngineP(Protocol):
    """Sync database engine protocol.
    
    Provides interface for SQLAlchemy engine operations.
    """

    def connect(self) -> ConnectionP:
        """Create a new connection."""
        ...

    def dispose(self) -> None:
        """Dispose of the connection pool."""
        ...

    @property
    def pool(self) -> Any:
        """The connection pool."""
        ...

    @property
    def dialect(self) -> Any:
        """The database dialect."""
        ...


class AsyncEngineP(Protocol):
    """Async database engine protocol.
    
    Provides interface for SQLAlchemy async engine operations.
    """

    async def connect(self) -> AsyncConnectionP:
        """Create a new async connection."""
        ...

    async def dispose(self) -> None:
        """Dispose of the connection pool."""
        ...

    @property
    def sync_engine(self) -> Any:
        """The underlying sync engine."""
        ...

    @property
    def pool(self) -> Any:
        """The connection pool."""
        ...

    @property
    def dialect(self) -> Any:
        """The database dialect."""
        ...


    def all(self) -> list[T]:
        """Return all scalar results as a list."""
        ...

    def first(self) -> T | None:
        """Return first scalar result or None."""
        ...


    async def all(self) -> list[T]:
        """Return all scalar results as a list."""
        ...

    async def first(self) -> T | None:
        """Return first scalar result or None."""
        ...


# Adapter utilities for type-checker compatibility (zero runtime cost)

def as_sessionp(obj: Any) -> SessionP:
    """Cast object to SessionP protocol for type checking."""
    return cast(SessionP, obj)


def as_async_sessionp(obj: Any) -> AsyncSessionP:
    """Cast object to AsyncSessionP protocol for type checking."""
    return cast(AsyncSessionP, obj)


def as_connectionp(obj: Any) -> ConnectionP:
    """Cast object to ConnectionP protocol for type checking."""
    return cast(ConnectionP, obj)


def as_async_connectionp(obj: Any) -> AsyncConnectionP:
    """Cast object to AsyncConnectionP protocol for type checking."""
    return cast(AsyncConnectionP, obj)


def as_enginep(obj: Any) -> EngineP:
    """Cast object to EngineP protocol for type checking."""
    return cast(EngineP, obj)


def as_async_enginep(obj: Any) -> AsyncEngineP:
    """Cast object to AsyncEngineP protocol for type checking."""
    return cast(AsyncEngineP, obj)


def as_cursor_resultp(obj: Any) -> CursorResultP:
    """Cast object to CursorResultP protocol for type checking."""
    return cast(CursorResultP, obj)


def as_async_cursor_resultp(obj: Any) -> AsyncCursorResultP:
    """Cast object to AsyncCursorResultP protocol for type checking."""
    return cast(AsyncCursorResultP, obj)
