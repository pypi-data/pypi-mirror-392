"""Sync/async retries with exponential backoff, jitter, deadlines, and timeouts.

Provides idempotent-friendly retry decorators and wrappers with flexible error
classification and integration hooks for logging/tracing.
"""

from __future__ import annotations

import asyncio
import inspect
import random
import time
from collections.abc import Awaitable, Callable
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FuturesTimeoutError
from dataclasses import dataclass, replace
from functools import wraps
from typing import Any, TypeVar

T = TypeVar("T")

# Clock helpers (fallback if .clock not available)
def _monotonic_ms() -> int:
    """Get monotonic time in milliseconds."""
    return int(time.perf_counter() * 1000)

def _remaining_ms(deadline_ms: int) -> int:
    """Calculate remaining milliseconds until deadline."""
    return max(0, deadline_ms - _monotonic_ms())

# Try to import from project clock module
try:
    from .clock import monotonic_ms, remaining_ms
except ImportError:
    monotonic_ms = _monotonic_ms
    remaining_ms = _remaining_ms


class RetryError(Exception):
    """Exception raised when retry attempts are exhausted."""

    def __init__(self, message: str, original_exception: BaseException, attempts: int):
        super().__init__(message)
        self.original_exception = original_exception
        self.attempts = attempts

    def __repr__(self) -> str:
        return f"RetryError(message={self.args[0]!r}, original_exception={self.original_exception!r}, attempts={self.attempts})"


@dataclass(frozen=True)
class RetryPolicy:
    """Configuration for retry behavior with exponential backoff and jitter."""

    max_attempts: int = 5
    initial_ms: int = 100
    max_ms: int = 10_000
    multiplier: float = 2.0
    jitter: str = "full"  # none|full|equal|decorrelated
    per_attempt_timeout_ms: int | None = None
    max_elapsed_ms: int | None = None
    deadline_ms: int | None = None
    retry_on: tuple[type[BaseException], ...] = (Exception,)
    retry_if: Callable[[BaseException], bool] | None = None
    backoff_strategy: Callable[[int], float] | None = None
    sleep_hook: Callable[[int, int], None] | None = None
    before_attempt_hook: Callable[[int], None] | None = None
    after_attempt_hook: Callable[[int, BaseException | None], None] | None = None
    name: str | None = None
    fast_first: bool = False
    random_seed: int | None = None

    def __post_init__(self) -> None:
        """Validate policy parameters."""
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be >= 1")
        if self.initial_ms < 0:
            raise ValueError("initial_ms must be >= 0")
        if self.max_ms < self.initial_ms:
            raise ValueError("max_ms must be >= initial_ms")
        if self.multiplier <= 0:
            raise ValueError("multiplier must be > 0")
        if self.jitter not in ("none", "full", "equal", "decorrelated"):
            raise ValueError("jitter must be one of: none, full, equal, decorrelated")
        if self.per_attempt_timeout_ms is not None and self.per_attempt_timeout_ms <= 0:
            raise ValueError("per_attempt_timeout_ms must be > 0")
        if self.max_elapsed_ms is not None and self.max_elapsed_ms <= 0:
            raise ValueError("max_elapsed_ms must be > 0")

    def copy_with(self, **overrides: Any) -> RetryPolicy:
        """Create a copy with specified field overrides."""
        return replace(self, **overrides)


def linear_backoff(base_delay: float, max_delay: float | None = None) -> Callable[[int], float]:
    """Create linear backoff strategy."""
    def backoff_fn(attempt: int) -> float:
        delay = base_delay * attempt
        if max_delay is not None:
            delay = min(delay, max_delay)
        return delay
    return backoff_fn


def exponential_backoff(
    base_delay: float,
    multiplier: float = 2.0,
    max_delay: float | None = None,
    jitter: bool = False
) -> Callable[[int], float]:
    """Create exponential backoff strategy."""
    def backoff_fn(attempt: int) -> float:
        delay = base_delay * (multiplier ** (attempt - 1))
        if max_delay is not None:
            delay = min(delay, max_delay)
        if jitter:
            delay = delay * (0.5 + random.random() * 0.5)
        return delay
    return backoff_fn


def compute_backoff_ms(attempt: int, policy: RetryPolicy, *, rnd: random.Random) -> int:
    """Compute backoff delay in milliseconds for given attempt."""
    if policy.backoff_strategy is not None:
        # Use custom backoff strategy (returns seconds, convert to ms)
        delay_seconds = policy.backoff_strategy(attempt)
        return int(delay_seconds * 1000)

    # Use built-in exponential backoff
    if attempt <= 1:
        base = policy.initial_ms
    else:
        base = min(policy.max_ms, int(policy.initial_ms * (policy.multiplier ** (attempt - 1))))

    if policy.jitter == "none":
        return base
    elif policy.jitter == "full":
        return rnd.randint(0, base)
    elif policy.jitter == "equal":
        return rnd.randint(base // 2, base)
    elif policy.jitter == "decorrelated":
        # Use previous base * 3 as upper bound, with minimum of base
        return min(policy.max_ms, rnd.randint(base, base * 3))

    return base


def next_sleep_ms(attempt: int, policy: RetryPolicy, rnd: random.Random) -> int:
    """Calculate next sleep duration considering fast_first setting."""
    if attempt == 1 and policy.fast_first:
        return 0
    return compute_backoff_ms(attempt, policy, rnd=rnd)


def remaining_budget_ms(start_ms: int, policy: RetryPolicy) -> int | None:
    """Calculate remaining time budget in milliseconds."""
    current_ms = monotonic_ms()
    elapsed_ms = current_ms - start_ms

    # Deadline takes precedence over max_elapsed
    if policy.deadline_ms is not None:
        return remaining_ms(policy.deadline_ms)
    elif policy.max_elapsed_ms is not None:
        return max(0, policy.max_elapsed_ms - elapsed_ms)

    return None


def _is_retryable(exc: BaseException, policy: RetryPolicy) -> bool:
    """Check if exception is retryable according to policy."""
    # Never retry cancellation or keyboard interrupt
    if isinstance(exc, (asyncio.CancelledError, KeyboardInterrupt)):
        return False

    # Check if exception type matches retry_on
    if not policy.retry_on or not isinstance(exc, policy.retry_on):
        return False

    # Apply additional predicate if provided
    if policy.retry_if is not None:
        return policy.retry_if(exc)

    return True


def with_attempt_timeout_sync(fn: Callable[..., T], timeout_ms: int | None, /, *args: Any, **kwargs: Any) -> T:
    """Execute function with timeout (cooperative - uses ThreadPoolExecutor for true timeout)."""
    if timeout_ms is None:
        return fn(*args, **kwargs)

    # Use ThreadPoolExecutor for true timeout capability
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(fn, *args, **kwargs)
        try:
            return future.result(timeout=timeout_ms / 1000.0)
        except FuturesTimeoutError:
            future.cancel()
            raise TimeoutError(f"Function timed out after {timeout_ms}ms")


async def with_attempt_timeout_async(awaitable: Awaitable[T], timeout_ms: int | None) -> T:
    """Execute awaitable with timeout using asyncio.wait_for."""
    if timeout_ms is None:
        return await awaitable

    try:
        return await asyncio.wait_for(awaitable, timeout=timeout_ms / 1000.0)
    except TimeoutError:
        raise TimeoutError(f"Operation timed out after {timeout_ms}ms")


def retry_call(fn: Callable[..., T], /, *args: Any, policy: RetryPolicy | None = None, **kwargs: Any) -> T:
    """Execute function with retries according to policy."""
    if policy is None:
        policy = RetryPolicy()

    rnd = random.Random(policy.random_seed)
    start_ms = monotonic_ms()
    last_exception = None

    for attempt in range(1, policy.max_attempts + 1):
        # Check remaining budget before attempt
        budget = remaining_budget_ms(start_ms, policy)
        if budget is not None and budget <= 0:
            break

        # Call before_attempt hook
        if policy.before_attempt_hook:
            policy.before_attempt_hook(attempt)

        try:
            # Execute with per-attempt timeout
            result = with_attempt_timeout_sync(fn, policy.per_attempt_timeout_ms, *args, **kwargs)

            # Call after_attempt hook on success
            if policy.after_attempt_hook:
                policy.after_attempt_hook(attempt, None)

            return result

        except BaseException as exc:
            last_exception = exc

            # Call after_attempt hook on failure
            if policy.after_attempt_hook:
                policy.after_attempt_hook(attempt, exc)

            # Check if we should retry
            if not _is_retryable(exc, policy):
                raise

            # If we've reached max attempts, break to raise RetryError
            if attempt >= policy.max_attempts:
                break

            # Calculate sleep duration
            sleep_ms = next_sleep_ms(attempt, policy, rnd)

            # Respect remaining budget
            budget = remaining_budget_ms(start_ms, policy)
            if budget is not None:
                sleep_ms = min(sleep_ms, budget)
                if sleep_ms <= 0:
                    break

            # Call sleep hook
            if policy.sleep_hook:
                policy.sleep_hook(attempt, sleep_ms)

            # Sleep before next attempt
            if sleep_ms > 0:
                time.sleep(sleep_ms / 1000.0)

    # Re-raise last exception if we exhausted retries
    if last_exception:
        raise RetryError(
            f"Max retry attempts ({policy.max_attempts}) exceeded",
            last_exception,
            attempts=policy.max_attempts
        )

    # This should not happen, but just in case
    raise RuntimeError("Retry loop completed without result or exception")


async def aretry(fn: Callable[..., Awaitable[T]] | Callable[..., T], /, *args: Any, policy: RetryPolicy | None = None, **kwargs: Any) -> T:
    """Execute function/coroutine with async retries according to policy."""
    if policy is None:
        policy = RetryPolicy()

    rnd = random.Random(policy.random_seed)
    start_ms = monotonic_ms()
    last_exception = None

    for attempt in range(1, policy.max_attempts + 1):
        # Check remaining budget before attempt
        budget = remaining_budget_ms(start_ms, policy)
        if budget is not None and budget <= 0:
            break

        # Call before_attempt hook
        if policy.before_attempt_hook:
            policy.before_attempt_hook(attempt)

        try:
            # Execute function and handle both sync and async cases
            raw_result = fn(*args, **kwargs)
            if inspect.iscoroutine(raw_result) or hasattr(raw_result, '__await__'):
                result: T = await with_attempt_timeout_async(raw_result, policy.per_attempt_timeout_ms)
            else:
                # Sync function in async context
                if policy.per_attempt_timeout_ms:
                    # Run in executor with timeout
                    loop = asyncio.get_event_loop()
                    result = await asyncio.wait_for(
                        loop.run_in_executor(None, lambda: raw_result),
                        timeout=policy.per_attempt_timeout_ms / 1000.0
                    )
                else:
                    result = raw_result

            # Call after_attempt hook on success
            if policy.after_attempt_hook:
                policy.after_attempt_hook(attempt, None)

            return result

        except BaseException as exc:
            last_exception = exc

            # Call after_attempt hook on failure
            if policy.after_attempt_hook:
                policy.after_attempt_hook(attempt, exc)

            # Check if we should retry
            if not _is_retryable(exc, policy):
                raise

            # If we've reached max attempts, break to raise RetryError
            if attempt >= policy.max_attempts:
                break

            # Calculate sleep duration
            sleep_ms = next_sleep_ms(attempt, policy, rnd)

            # Respect remaining budget
            budget = remaining_budget_ms(start_ms, policy)
            if budget is not None:
                sleep_ms = min(sleep_ms, budget)
                if sleep_ms <= 0:
                    break

            # Call sleep hook
            if policy.sleep_hook:
                policy.sleep_hook(attempt, sleep_ms)

            # Sleep before next attempt
            if sleep_ms > 0:
                await asyncio.sleep(sleep_ms / 1000.0)

    # Re-raise last exception if we exhausted retries
    if last_exception:
        raise RetryError(
            f"Max retry attempts ({policy.max_attempts}) exceeded",
            last_exception,
            attempts=policy.max_attempts
        )

    # This should not happen, but just in case
    raise RuntimeError("Retry loop completed without result or exception")


def retry(
    max_attempts: int = 3,
    retry_on: tuple[type[BaseException], ...] = (Exception,),
    backoff_strategy: Callable[[int], float] | None = None,
    config: RetryPolicy | None = None
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator for sync functions with retry behavior."""
    # Validate parameters immediately if not using config
    if config is None and max_attempts < 1:
        raise ValueError("max_attempts must be >= 1")

    def decorator(fn: Callable[..., T]) -> Callable[..., T]:
        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            if config is not None:
                policy = config
            else:
                # Convert list to tuple if needed
                retry_on_tuple = tuple(retry_on) if isinstance(retry_on, list) else retry_on
                policy = RetryPolicy(
                    max_attempts=max_attempts,
                    retry_on=retry_on_tuple,
                    backoff_strategy=backoff_strategy
                )
            return retry_call(fn, *args, policy=policy, **kwargs)

        # Preserve function metadata
        wrapper.__wrapped__ = fn
        return wrapper
    return decorator


def async_retry(
    max_attempts: int = 3,
    retry_on: tuple[type[BaseException], ...] = (Exception,),
    backoff_strategy: Callable[[int], float] | None = None,
    config: RetryPolicy | None = None
) -> Callable[[Callable[..., Any]], Callable[..., Awaitable[Any]]]:
    """Decorator for async functions with retry behavior."""
    # Validate parameters immediately if not using config
    if config is None and max_attempts < 1:
        raise ValueError("max_attempts must be >= 1")

    def decorator(fn: Callable[..., Any]) -> Callable[..., Awaitable[Any]]:
        @wraps(fn)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            if config is not None:
                policy = config
            else:
                # Convert list to tuple if needed
                retry_on_tuple = tuple(retry_on) if isinstance(retry_on, list) else retry_on
                policy = RetryPolicy(
                    max_attempts=max_attempts,
                    retry_on=retry_on_tuple,
                    backoff_strategy=backoff_strategy
                )
            return await aretry(fn, *args, policy=policy, **kwargs)

        # Preserve function metadata
        wrapper.__wrapped__ = fn
        return wrapper
    return decorator


def retrying(policy: RetryPolicy | None = None) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator for sync functions with retry behavior."""
    def decorator(fn: Callable[..., T]) -> Callable[..., T]:
        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            return retry_call(fn, *args, policy=policy, **kwargs)
        return wrapper
    return decorator


def aretrying(policy: RetryPolicy | None = None) -> Callable[[Callable[..., Any]], Callable[..., Awaitable[Any]]]:
    """Decorator for async functions with retry behavior."""
    def decorator(fn: Callable[..., Any]) -> Callable[..., Awaitable[Any]]:
        @wraps(fn)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            return await aretry(fn, *args, policy=policy, **kwargs)
        return wrapper
    return decorator
