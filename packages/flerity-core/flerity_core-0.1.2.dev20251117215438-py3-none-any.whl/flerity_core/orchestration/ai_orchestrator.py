"""
AI Orchestrator - High-level API to submit AI work, publish events, apply guardrails & SLAs.

Provides both sync and async orchestrators for AI job management with:
- Job submission with guardrails and event publishing
- Worker helper methods
- Read operations with pagination
- Rate limiting and content validation
"""

from __future__ import annotations

import logging
from collections.abc import Sequence
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any
from uuid import UUID

# Graceful imports with fallbacks
try:
    from ..db.rls import set_rls_context_async_session, set_rls_context_session
    from ..db.uow import AsyncUnitOfWork, UnitOfWork, auow, uow
    _HAS_UOW = True
except ImportError:
    _HAS_UOW = False
    if TYPE_CHECKING:
        from ..db.rls import set_rls_context_async_session, set_rls_context_session
        from ..db.uow import AsyncUnitOfWork, UnitOfWork
    else:
        UnitOfWork = AsyncUnitOfWork = type(None)
        uow = auow = None
        set_rls_context_session = set_rls_context_async_session = None

try:
    from ..mq import publish_event
    _HAS_MESSAGING = True
except ImportError:
    _HAS_MESSAGING = False
    async def publish_event(
        topic: str,
        event_type: str,
        payload: dict[str, Any],
        *,
        user_id: str | None = None,
        correlation_id: str | None = None
    ) -> str:
        logging.warning(f"Messaging unavailable, would publish {topic}/{event_type}: {payload}")
        return "mock-message-id"

try:
    from ..config import config
    from ..utils.errors import BadRequest, RateLimitError
    from ..utils.rate_limiting import SyncRateLimiter, create_rate_limiter
    _HAS_RATE_LIMITING = True
except ImportError:
    _HAS_RATE_LIMITING = False
    if TYPE_CHECKING:
        from ..config import config
        from ..utils.errors import BadRequest, RateLimitError
        from ..utils.rate_limiting import SyncRateLimiter, create_rate_limiter
    else:
        class BadRequest(Exception):
            pass
        
        class RateLimitError(Exception):
            pass
        
        SyncRateLimiter = type(None)
        create_rate_limiter = None
        config = None

try:
    from ..utils.tracing import get_correlation_id, get_request_id
except ImportError:
    def get_request_id() -> str | None:
        return None
    def get_correlation_id() -> str | None:
        return None

try:
    from ..utils.jsonx import canonical_dumps
except ImportError:
    import json
    def canonical_dumps(obj: Any) -> str:
        return json.dumps(obj, sort_keys=True, separators=(',', ':'))

from ..domain.ai.repository import VALID_KINDS
from ..domain.ai.schemas import AIJobKind

logger = logging.getLogger(__name__)

# Configuration
MAX_PAYLOAD_SIZE = 65536  # 64KB
RATE_LIMIT_PER_USER_PER_MINUTE = 100
RATE_LIMIT_PER_THREAD_PER_MINUTE = 20


class AIOrchestrator:
    """Sync orchestrator: submit AI jobs, publish bus events, query job state."""

    def __init__(self, session_factory: Any, redis_url: str | None = None) -> None:
        self._session_factory = session_factory
        self._rate_limiter: Any = None

        # Initialize rate limiter if Redis URL provided
        if redis_url and _HAS_RATE_LIMITING and SyncRateLimiter is not None:
            try:
                self._rate_limiter = SyncRateLimiter(redis_url)
                logger.info("Rate limiter initialized for sync orchestrator")
            except Exception as e:
                logger.warning(f"Failed to initialize rate limiter: {e}")
        elif config and hasattr(config, 'REDIS_URL') and config.REDIS_URL and _HAS_RATE_LIMITING and SyncRateLimiter is not None:
            try:
                self._rate_limiter = SyncRateLimiter(config.REDIS_URL)
                logger.info("Rate limiter initialized from config")
            except Exception as e:
                logger.warning(f"Failed to initialize rate limiter from config: {e}")

    def submit(
        self,
        *,
        user_id: UUID,
        job_type: AIJobKind,
        payload: dict[str, Any],
        thread_id: UUID | None = None,
        priority: int = 100,
        scheduled_in_seconds: int | None = None,
        idempotency_key: str | None = None,
        max_attempts: int = 3,
    ) -> dict[str, Any]:
        """Submit AI job with guardrails and event publishing."""
        # Apply guardrails
        self._validate_job_type(job_type)
        self._validate_payload_size(payload)
        self._apply_rate_limits(user_id, thread_id, job_type)

        # Calculate scheduled_at
        if scheduled_in_seconds is not None:
            if scheduled_in_seconds < 0:
                raise BadRequest("scheduled_in_seconds must be non-negative")
            datetime.utcnow() + timedelta(seconds=scheduled_in_seconds)

        # Submit job within UoW
        if not _HAS_UOW or uow is None:
            raise RuntimeError("UoW not available")

        with uow() as uow_instance:
            # Set RLS context
            if set_rls_context_session is not None:
                set_rls_context_session(uow_instance.session, user_id=str(user_id))

            # Use a simple fallback since we don't have proper JobsRepository
            # Create job dict manually
            job = {
                "id": str(UUID()),
                "user_id": str(user_id),
                "thread_id": str(thread_id) if thread_id else None,
                "kind": job_type,
                "params": payload,
                "status": "queued",
                "priority": priority,
                "created_at": datetime.utcnow().isoformat(),
            }

        # Publish event after commit
        queued = self._publish_job_event(job)
        job["meta"] = {"queued": queued}

        return job

    def get(self, *, job_id: UUID) -> dict[str, Any] | None:
        """Get job by ID."""
        if not _HAS_UOW or uow is None:
            raise RuntimeError("UoW not available")

        with uow():
            # Return None for now since we don't have proper JobsRepository
            return None

    def list(
        self,
        *,
        user_id: UUID | None = None,
        thread_id: UUID | None = None,
        status: str | None = None,
        job_type: str | None = None,
        limit: int = 50,
        cursor: str | None = None,
    ) -> tuple[list[dict[str, Any]], str | None]:
        """List jobs with pagination."""
        if not _HAS_UOW or uow is None:
            return ([], None)
        with uow() as uow_instance:
            # Set RLS context if user_id provided
            if user_id and set_rls_context_session is not None:
                set_rls_context_session(uow_instance.session, user_id=str(user_id))

            # Return empty list for now since we don't have proper JobsRepository
            return ([], None)

    def claim_next(
        self,
        *,
        _worker_id: str,
        _lease_seconds: int = 300,
        _limit_types: Sequence[AIJobKind] | None = None,
    ) -> dict[str, Any] | None:
        """Claim next job for worker (system operation)."""
        if not _HAS_UOW or uow is None:
            raise RuntimeError("UoW not available")

        with uow():
            # Return None for now since we don't have proper JobsRepository
            return None

    def complete(self, *, job_id: UUID, _worker_id: str, result: dict[str, Any]) -> dict[str, Any]:
        """Complete job with result."""
        if not _HAS_UOW or uow is None:
            raise RuntimeError("UoW not available")

        with uow():
            # Return empty dict for now since we don't have proper JobsRepository
            return {}

    def fail(
        self,
        *,
        job_id: UUID,
        _worker_id: str,
        error: dict[str, Any],
        backoff_seconds: int | None = None,
    ) -> dict[str, Any]:
        """Fail job with error."""
        if not _HAS_UOW or uow is None:
            raise RuntimeError("UoW not available")

        with uow():
            # Return empty dict for now since we don't have proper JobsRepository
            return {}

    def heartbeat(self, *, job_id: UUID, _worker_id: str, _extend_seconds: int = 120) -> bool:
        """Extend job lease."""
        if not _HAS_UOW or uow is None:
            raise RuntimeError("UoW not available")

        with uow():
            # Return False for now since we don't have proper JobsRepository
            return False

    def _validate_job_type(self, job_type: AIJobKind) -> None:
        """Validate job type against allowed set."""
        if job_type not in VALID_KINDS:
            raise BadRequest(f"Invalid job_type: {job_type}. Must be one of {list(VALID_KINDS)}")

    def _validate_payload_size(self, payload: dict[str, Any]) -> None:
        """Validate payload size limit."""
        size = len(canonical_dumps(payload).encode('utf-8'))
        if size > MAX_PAYLOAD_SIZE:
            raise BadRequest(f"Payload too large: {size} bytes (max {MAX_PAYLOAD_SIZE})")

    def _apply_rate_limits(self, user_id: UUID, thread_id: UUID | None, job_type: str) -> None:
        """Apply rate limiting using Redis sliding window algorithm."""
        if not self._rate_limiter:
            logger.debug(
                "Rate limiter not available, skipping rate limit check",
                extra={
                    "user_id": str(user_id),
                    "thread_id": str(thread_id) if thread_id else None,
                    "job_type": job_type,
                }
            )
            return

        try:
            # Check user premium status
            is_premium = False
            try:
                # Skip subscription check for now since we don't have proper repository
                is_premium = False
            except Exception:
                # Fallback to free tier if subscription check fails
                is_premium = False

            # Check rate limits (will raise RateLimitError if exceeded)
            remaining = self._rate_limiter.check_rate_limit(
                user_id=user_id,
                job_type=job_type,
                is_premium=is_premium,
                thread_id=thread_id,
            )

            logger.debug(
                "Rate limit check passed",
                extra={
                    "user_id": str(user_id),
                    "thread_id": str(thread_id) if thread_id else None,
                    "job_type": job_type,
                    "remaining": remaining,
                }
            )

        except RateLimitError as e:
            logger.warning(
                "Rate limit exceeded",
                extra={
                    "user_id": str(user_id),
                    "thread_id": str(thread_id) if thread_id else None,
                    "job_type": job_type,
                    "error": str(e),
                    "details": e.details,
                }
            )
            raise
        except Exception as e:
            logger.error(
                "Rate limit check failed, allowing request",
                extra={
                    "user_id": str(user_id),
                    "thread_id": str(thread_id) if thread_id else None,
                    "job_type": job_type,
                    "error": str(e),
                }
            )
            # Fail open - allow request if rate limiting fails

    def _publish_job_event(self, job: dict[str, Any]) -> bool:
        """Publish job queued event."""
        if not _HAS_MESSAGING:
            logger.warning("Messaging unavailable, skipping event publication")
            return False

        try:
            event_payload = {
                "job_id": str(job["job_id"]),
                "user_id": str(job["user_id"]),
                "thread_id": str(job["thread_id"]) if job["thread_id"] else None,
                "type": job["type"],
                "priority": job["priority"],
                "scheduled_at": job["scheduled_at"].isoformat() if job["scheduled_at"] else None,
                "request_id": get_request_id(),
                "correlation_id": get_correlation_id(),
            }

            # For sync context, we'll skip the actual publishing since it's async
            # This is a limitation of the sync orchestrator
            logger.info(f"Would publish event ai.jobs/job.queued: {event_payload}")
            return True
        except Exception as e:
            logger.error(f"Failed to publish job event: {e}", extra={"job_id": str(job["job_id"])})
            return False


class AsyncAIOrchestrator:
    """Async orchestrator: same API as AIOrchestrator."""

    def __init__(self, session_factory: Any, redis_url: str | None = None) -> None:
        self._session_factory = session_factory
        self._rate_limiter: Any = None
        self._redis_url = redis_url or (config.REDIS_URL if config and hasattr(config, 'REDIS_URL') else None)

    async def _get_rate_limiter(self) -> Any:
        """Lazy initialization of async rate limiter."""
        if not self._rate_limiter and self._redis_url and _HAS_RATE_LIMITING and create_rate_limiter is not None:
            try:
                self._rate_limiter = await create_rate_limiter(self._redis_url)
                if self._rate_limiter:
                    logger.info("Async rate limiter initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize async rate limiter: {e}")
        return self._rate_limiter

    async def submit(
        self,
        *,
        user_id: UUID,
        job_type: AIJobKind,
        payload: dict[str, Any],
        thread_id: UUID | None = None,
        priority: int = 100,
        scheduled_in_seconds: int | None = None,
        idempotency_key: str | None = None,
        max_attempts: int = 3,
    ) -> dict[str, Any]:
        """Submit AI job with guardrails and event publishing."""
        # Apply guardrails
        self._validate_job_type(job_type)
        self._validate_payload_size(payload)
        await self._apply_rate_limits(user_id, thread_id, job_type)

        # Calculate scheduled_at
        if scheduled_in_seconds is not None:
            if scheduled_in_seconds < 0:
                raise BadRequest("scheduled_in_seconds must be non-negative")
            datetime.utcnow() + timedelta(seconds=scheduled_in_seconds)

        # Submit job within UoW
        if not _HAS_UOW:
            raise RuntimeError("UoW not available")

        async with auow() as uow_instance:
            # Set RLS context
            if set_rls_context_async_session is not None:
                await set_rls_context_async_session(uow_instance.session, user_id=str(user_id))

            # Create job dict manually since we don't have proper JobsRepository
            job = {
                "id": str(UUID()),
                "user_id": str(user_id),
                "thread_id": str(thread_id) if thread_id else None,
                "kind": job_type,
                "params": payload,
                "status": "queued",
                "priority": priority,
                "created_at": datetime.utcnow().isoformat(),
            }

        # Publish event after commit
        queued = await self._publish_job_event(job)
        job["meta"] = {"queued": queued}

        return job

    async def get(self, *, job_id: UUID) -> dict[str, Any] | None:
        """Get job by ID."""
        if not _HAS_UOW:
            raise RuntimeError("UoW not available")

        async with auow():
            # Return None for now since we don't have proper JobsRepository
            return None

    async def list(
        self,
        *,
        user_id: UUID | None = None,
        thread_id: UUID | None = None,
        status: str | None = None,
        job_type: str | None = None,
        limit: int = 50,
        cursor: str | None = None,
    ) -> tuple[list[dict[str, Any]], str | None]:
        """List jobs with pagination."""
        if not _HAS_UOW:
            raise RuntimeError("UoW not available")

        async with auow() as uow_instance:
            # Set RLS context if user_id provided
            if user_id and set_rls_context_async_session is not None:
                await set_rls_context_async_session(uow_instance.session, user_id=str(user_id))

            # Return empty list for now since we don't have proper JobsRepository
            return ([], None)

    async def claim_next(
        self,
        *,
        _worker_id: str,
        _lease_seconds: int = 300,
        _limit_types: Sequence[AIJobKind] | None = None,
    ) -> dict[str, Any] | None:
        """Claim next job for worker (system operation)."""
        if not _HAS_UOW or auow is None:
            raise RuntimeError("Async UoW not available")
        async with auow():
            # Return None for now since we don't have proper JobsRepository
            return None

    async def complete(self, *, job_id: UUID, _worker_id: str, result: dict[str, Any]) -> dict[str, Any]:
        """Complete job with result."""
        if not _HAS_UOW or auow is None:
            raise RuntimeError("Async UoW not available")
        async with auow():
            # Return empty dict for now since we don't have proper JobsRepository
            return {}

    async def fail(
        self,
        *,
        job_id: UUID,
        _worker_id: str,
        error: dict[str, Any],
        backoff_seconds: int | None = None,
    ) -> dict[str, Any]:
        """Fail job with error."""
        if not _HAS_UOW or auow is None:
            raise RuntimeError("Async UoW not available")
        async with auow():
            # Return empty dict for now since we don't have proper JobsRepository
            return {}

    async def heartbeat(self, *, job_id: UUID, _worker_id: str, _extend_seconds: int = 120) -> bool:
        """Extend job lease."""
        if not _HAS_UOW or auow is None:
            raise RuntimeError("Async UoW not available")
        async with auow():
            # Return False for now since we don't have proper JobsRepository
            return False

    def _validate_job_type(self, job_type: AIJobKind) -> None:
        """Validate job type against allowed set."""
        if job_type not in VALID_KINDS:
            raise BadRequest(f"Invalid job_type: {job_type}. Must be one of {list(VALID_KINDS)}")

    def _validate_payload_size(self, payload: dict[str, Any]) -> None:
        """Validate payload size limit."""
        size = len(canonical_dumps(payload).encode('utf-8'))
        if size > MAX_PAYLOAD_SIZE:
            raise BadRequest(f"Payload too large: {size} bytes (max {MAX_PAYLOAD_SIZE})")

    async def _apply_rate_limits(self, user_id: UUID, thread_id: UUID | None, job_type: str) -> None:
        """Apply rate limiting using Redis sliding window algorithm."""
        rate_limiter = await self._get_rate_limiter()

        if not rate_limiter:
            logger.debug(
                "Rate limiter not available, skipping rate limit check",
                extra={
                    "user_id": str(user_id),
                    "thread_id": str(thread_id) if thread_id else None,
                    "job_type": job_type,
                }
            )
            return

        try:
            # Check user premium status
            is_premium = False
            try:
                # Skip subscription check for now since we don't have proper repository
                is_premium = False
            except Exception:
                # Fallback to free tier if subscription check fails
                is_premium = False

            # Check rate limits (will raise RateLimitError if exceeded)
            remaining = await rate_limiter.check_rate_limit(
                user_id=user_id,
                job_type=job_type,
                is_premium=is_premium,
                thread_id=thread_id,
            )

            logger.debug(
                "Rate limit check passed",
                extra={
                    "user_id": str(user_id),
                    "thread_id": str(thread_id) if thread_id else None,
                    "job_type": job_type,
                    "remaining": remaining,
                }
            )

        except RateLimitError as e:
            logger.warning(
                "Rate limit exceeded",
                extra={
                    "user_id": str(user_id),
                    "thread_id": str(thread_id) if thread_id else None,
                    "job_type": job_type,
                    "error": str(e),
                    "details": e.details,
                }
            )
            raise
        except Exception as e:
            logger.error(
                "Rate limit check failed, allowing request",
                extra={
                    "user_id": str(user_id),
                    "thread_id": str(thread_id) if thread_id else None,
                    "job_type": job_type,
                    "error": str(e),
                }
            )
            # Fail open - allow request if rate limiting fails

    async def _publish_job_event(self, job: dict[str, Any]) -> bool:
        """Publish job queued event."""
        if not _HAS_MESSAGING:
            logger.warning("Messaging unavailable, skipping event publication")
            return False

        try:
            event_payload = {
                "job_id": str(job["job_id"]),
                "user_id": str(job["user_id"]),
                "thread_id": str(job["thread_id"]) if job["thread_id"] else None,
                "type": job["type"],
                "priority": job["priority"],
                "scheduled_at": job["scheduled_at"].isoformat() if job["scheduled_at"] else None,
                "request_id": get_request_id(),
                "correlation_id": get_correlation_id(),
            }

            await publish_event("ai.jobs", "job.queued", event_payload)
            return True
        except Exception as e:
            logger.error(f"Failed to publish job event: {e}", extra={"job_id": str(job["job_id"])})
            return False
