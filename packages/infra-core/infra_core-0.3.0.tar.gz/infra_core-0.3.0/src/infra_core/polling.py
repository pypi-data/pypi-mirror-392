"""Reusable polling utilities for async operations.

Provides generic polling patterns for waiting on remote operations to complete,
with configurable timeouts, intervals, and terminal state detection.

Example:
    >>> from infra_core.polling import poll_until
    >>> def check_status():
    ...     return {"status": "completed", "result": 42}
    >>> result = poll_until(
    ...     check_status,
    ...     is_terminal=lambda r: r["status"] in ("completed", "failed"),
    ...     timeout=600.0,
    ...     poll_interval=5.0
    ... )
    >>> print(result)
    {'status': 'completed', 'result': 42}
"""

from __future__ import annotations

import asyncio
import inspect
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any, Generic, Protocol, TypeVar, cast, runtime_checkable

T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)


class PollingError(Exception):
    """Base exception for polling errors."""

    pass


class PollingTimeoutError(PollingError):
    """Raised when polling exceeds the specified timeout."""

    def __init__(self, message: str, last_response: Any = None):
        super().__init__(message)
        self.last_response = last_response


class PollingFailureError(PollingError):
    """Raised when the polled operation fails."""

    def __init__(self, message: str, response: Any = None):
        super().__init__(message)
        self.response = response


@dataclass(frozen=True, kw_only=True, slots=True)
class PollingConfig:
    """Configuration for polling behavior.

    Attributes:
        timeout: Maximum time to poll in seconds. Defaults to 600.0 (10 minutes).
        poll_interval: Time between status checks in seconds. Defaults to 5.0.
        initial_delay: Optional delay before first poll in seconds.
        max_backoff: Maximum backoff time for exponential backoff in seconds.
        backoff_multiplier: Multiplier for exponential backoff. Set to 1.0 to disable.
        terminal_statuses: Set of status values that indicate completion.
        failure_statuses: Set of status values that indicate failure.
    """

    timeout: float = 600.0
    poll_interval: float = 5.0
    initial_delay: float = 0.0
    max_backoff: float = 60.0
    backoff_multiplier: float = 1.0
    terminal_statuses: frozenset[str] | None = None
    failure_statuses: frozenset[str] | None = None

    def __post_init__(self) -> None:
        if self.timeout <= 0:
            raise ValueError("timeout must be positive")
        if self.poll_interval <= 0:
            raise ValueError("poll_interval must be positive")
        if self.backoff_multiplier < 1.0:
            raise ValueError("backoff_multiplier must be >= 1.0")
        if self.terminal_statuses is not None and not isinstance(self.terminal_statuses, frozenset):
            object.__setattr__(self, "terminal_statuses", frozenset(self.terminal_statuses))
        if self.failure_statuses is not None and not isinstance(self.failure_statuses, frozenset):
            object.__setattr__(self, "failure_statuses", frozenset(self.failure_statuses))


@runtime_checkable
class StatusExtractor(Protocol[T_co]):
    """Protocol for extracting status from a response."""

    def __call__(self, response: Any) -> T_co:
        """Extract status from response.

        Args:
            response: The response object to extract status from.

        Returns:
            The extracted status value.
        """
        ...


def poll_until(
    fetch_fn: Callable[[], T],
    is_terminal: Callable[[T], bool],
    *,
    timeout: float = 600.0,
    poll_interval: float = 5.0,
    on_poll: Callable[[T], None] | None = None,
    handle_404: bool = True,
    initial_delay: float = 0.0,
    backoff_multiplier: float = 1.0,
    max_backoff: float = 60.0,
) -> T:
    """Poll a function until a terminal condition is met or timeout.

    Synchronous polling with fixed interval. For async operations,
    use poll_until_async() instead.

    Args:
        fetch_fn: Function that fetches the current state (no arguments).
        is_terminal: Predicate that returns True when state is terminal.
        timeout: Maximum time to poll in seconds.
        poll_interval: Time between polls in seconds.
        on_poll: Optional callback invoked with each polled response.
        handle_404: If True, treat 404 errors as transient within timeout.
        initial_delay: Optional delay before the first poll attempt.
        backoff_multiplier: Multiplier applied to the poll interval after each attempt.
        max_backoff: Maximum sleep interval when applying backoff.

    Returns:
        The last polled response when terminal condition is met.

    Raises:
        PollingTimeoutError: If timeout is reached before terminal condition.
        Exception: Any exception from fetch_fn (unless 404 and handle_404=True).

    Example:
        >>> def fetch():
        ...     return {"status": "running"}
        >>> result = poll_until(
        ...     fetch,
        ...     is_terminal=lambda r: r["status"] == "done",
        ...     timeout=60.0
        ... )
    """
    if timeout <= 0:
        raise ValueError("timeout must be positive")
    if poll_interval <= 0:
        raise ValueError("poll_interval must be positive")
    if initial_delay < 0:
        raise ValueError("initial_delay must be >= 0")
    if backoff_multiplier < 1.0:
        raise ValueError("backoff_multiplier must be >= 1.0")
    if max_backoff <= 0:
        raise ValueError("max_backoff must be positive")

    deadline = time.time() + timeout
    last_response: T | None = None
    base_interval = min(poll_interval, max_backoff)
    sleep_interval = base_interval

    if initial_delay > 0:
        _sleep_with_backoff_sync(
            initial_delay,
            deadline=deadline,
            backoff_multiplier=1.0,
            max_backoff=max_backoff,
            clamp_only=True,
        )

    while True:
        try:
            response = fetch_fn()
        except Exception as exc:
            # Handle 404 as transient error if requested
            if handle_404 and _is_404_error(exc) and time.time() < deadline:
                sleep_interval = _sleep_with_backoff_sync(
                    sleep_interval,
                    deadline=deadline,
                    backoff_multiplier=backoff_multiplier,
                    max_backoff=max_backoff,
                )
                if time.time() >= deadline:
                    raise PollingTimeoutError(
                        f"Polling timed out after {timeout}s without reaching terminal state",
                        last_response=last_response,
                    ) from exc
                continue
            raise

        last_response = response

        # Call progress callback
        if on_poll:
            on_poll(response)

        # Check terminal condition
        if is_terminal(response):
            return response

        # Check timeout
        if time.time() >= deadline:
            raise PollingTimeoutError(
                f"Polling timed out after {timeout}s without reaching terminal state",
                last_response=last_response,
            )

        # Sleep before next poll
        sleep_interval = _sleep_with_backoff_sync(
            sleep_interval,
            deadline=deadline,
            backoff_multiplier=backoff_multiplier,
            max_backoff=max_backoff,
        )


async def poll_until_async(
    fetch_fn: Callable[[], Awaitable[T]] | Callable[[], T],
    is_terminal: Callable[[T], bool],
    *,
    timeout: float = 600.0,
    poll_interval: float = 5.0,
    on_poll: Callable[[Any], Awaitable[None] | None] | None = None,
    handle_404: bool = True,
    initial_delay: float = 0.0,
    backoff_multiplier: float = 1.0,
    max_backoff: float = 60.0,
) -> T:
    """Async version of poll_until().

    Poll an async or sync function until a terminal condition is met.

    Args:
        fetch_fn: Async or sync function that fetches the current state.
        is_terminal: Predicate that returns True when state is terminal.
        timeout: Maximum time to poll in seconds.
        poll_interval: Time between polls in seconds.
        on_poll: Optional callback invoked with each polled response.
        handle_404: If True, treat 404 errors as transient within timeout.
        initial_delay: Optional delay before the first poll attempt.
        backoff_multiplier: Multiplier applied to the poll interval after each attempt.
        max_backoff: Maximum sleep interval when applying backoff.

    Returns:
        The last polled response when terminal condition is met.

    Raises:
        PollingTimeoutError: If timeout is reached before terminal condition.
        Exception: Any exception from fetch_fn (unless 404 and handle_404=True).

    Example:
        >>> async def fetch():
        ...     return {"status": "running"}
        >>> result = await poll_until_async(
        ...     fetch,
        ...     is_terminal=lambda r: r["status"] == "done",
        ...     timeout=60.0
        ... )
    """
    if timeout <= 0:
        raise ValueError("timeout must be positive")
    if poll_interval <= 0:
        raise ValueError("poll_interval must be positive")
    if initial_delay < 0:
        raise ValueError("initial_delay must be >= 0")
    if backoff_multiplier < 1.0:
        raise ValueError("backoff_multiplier must be >= 1.0")
    if max_backoff <= 0:
        raise ValueError("max_backoff must be positive")

    loop = asyncio.get_running_loop()
    deadline = loop.time() + timeout
    last_response: T | None = None
    base_interval = min(poll_interval, max_backoff)
    sleep_interval = base_interval

    if initial_delay > 0:
        await _sleep_with_backoff_async(
            initial_delay,
            loop=loop,
            deadline=deadline,
            backoff_multiplier=1.0,
            max_backoff=max_backoff,
            clamp_only=True,
        )

    while True:
        try:
            # Call fetch_fn (supports both sync and async)
            if asyncio.iscoroutinefunction(fetch_fn):
                response = await cast(Callable[[], Awaitable[T]], fetch_fn)()
            else:
                response = await asyncio.to_thread(cast(Callable[[], T], fetch_fn))
        except Exception as exc:
            # Handle 404 as transient error if requested
            if handle_404 and _is_404_error(exc) and loop.time() < deadline:
                sleep_interval = await _sleep_with_backoff_async(
                    sleep_interval,
                    loop=loop,
                    deadline=deadline,
                    backoff_multiplier=backoff_multiplier,
                    max_backoff=max_backoff,
                )
                if loop.time() >= deadline:
                    raise PollingTimeoutError(
                        f"Polling timed out after {timeout}s without reaching terminal state",
                        last_response=last_response,
                    ) from exc
                continue
            raise

        last_response = response

        # Call progress callback
        if on_poll:
            maybe_awaitable = on_poll(response)
            if inspect.isawaitable(maybe_awaitable):
                await maybe_awaitable

        # Check terminal condition
        if is_terminal(response):
            return response

        # Check timeout
        if loop.time() >= deadline:
            raise PollingTimeoutError(
                f"Polling timed out after {timeout}s without reaching terminal state",
                last_response=last_response,
            )

        # Sleep before next poll
        sleep_interval = await _sleep_with_backoff_async(
            sleep_interval,
            loop=loop,
            deadline=deadline,
            backoff_multiplier=backoff_multiplier,
            max_backoff=max_backoff,
        )


class StatusPoller(Generic[T]):
    """Reusable poller for checking status of async operations.

    Provides a higher-level interface with built-in status extraction,
    terminal state checking, and failure detection.

    Args:
        fetch_fn: Function that fetches current state.
        config: Polling configuration.
        status_extractor: Optional function to extract status from response.
            Defaults to lambda r: r.get("status").

    Example:
        >>> poller = StatusPoller(
        ...     fetch_fn=lambda: api.get_job("job-123"),
        ...     config=PollingConfig(
        ...         timeout=300.0,
        ...         terminal_statuses={"completed", "failed"}
        ...     )
        ... )
        >>> result = poller.poll()
    """

    def __init__(
        self,
        fetch_fn: Callable[[], T],
        config: PollingConfig | None = None,
        status_extractor: StatusExtractor[str] | None = None,
    ):
        self._fetch_fn = fetch_fn
        self._config = config or PollingConfig()
        self._status_extractor = status_extractor or _default_status_extractor

    def poll(self, *, on_poll: Callable[[T], None] | None = None) -> T:
        """Poll until terminal status or timeout (synchronous).

        Args:
            on_poll: Optional callback invoked with each polled response.

        Returns:
            The final response when terminal state is reached.

        Raises:
            PollingTimeoutError: If timeout is reached.
            PollingFailureError: If a failure status is detected.
        """

        def is_terminal(response: T) -> bool:
            return self._check_terminal(response)

        return poll_until(
            self._fetch_fn,
            is_terminal,
            timeout=self._config.timeout,
            poll_interval=self._config.poll_interval,
            on_poll=on_poll,
            handle_404=True,
            initial_delay=self._config.initial_delay,
            backoff_multiplier=self._config.backoff_multiplier,
            max_backoff=self._config.max_backoff,
        )

    async def poll_async(self, *, on_poll: Callable[[T], Awaitable[None] | None] | None = None) -> T:
        """Poll until terminal status or timeout (asynchronous).

        Args:
            on_poll: Optional callback invoked with each polled response.

        Returns:
            The final response when terminal state is reached.

        Raises:
            PollingTimeoutError: If timeout is reached.
            PollingFailureError: If a failure status is detected.
        """

        def is_terminal(response: T) -> bool:
            return self._check_terminal(response)

        return await poll_until_async(
            self._fetch_fn,
            is_terminal,
            timeout=self._config.timeout,
            poll_interval=self._config.poll_interval,
            on_poll=on_poll,
            handle_404=True,
            initial_delay=self._config.initial_delay,
            backoff_multiplier=self._config.backoff_multiplier,
            max_backoff=self._config.max_backoff,
        )

    def _check_terminal(self, response: T) -> bool:
        """Check if response represents a terminal state.

        Args:
            response: The response to check.

        Returns:
            True if terminal state reached.

        Raises:
            PollingFailureError: If response indicates failure.
        """
        status = self._status_extractor(response)

        # Check for failure status
        if self._config.failure_statuses and status in self._config.failure_statuses:
            error_message = _extract_error_message(response)
            raise PollingFailureError(
                f"Operation failed with status '{status}': {error_message}",
                response=response,
            )

        # Check for terminal status
        if self._config.terminal_statuses:
            return status in self._config.terminal_statuses

        # Fallback: common terminal statuses
        return status in {"completed", "failed", "cancelled", "succeeded"}


def _default_status_extractor(response: Any) -> str:
    """Extract status from response dict.

    Args:
        response: Response object (expected to be dict-like).

    Returns:
        The status string, or "unknown" if not found.
    """
    if isinstance(response, dict):
        status = response.get("status")
        if isinstance(status, str):
            return status
        if status is not None:
            return str(status)
        return "unknown"
    if hasattr(response, "status"):
        return str(response.status)
    return "unknown"


def _extract_error_message(response: Any) -> str:
    """Extract error message from response.

    Args:
        response: Response object.

    Returns:
        Error message if found, otherwise generic message.
    """
    if isinstance(response, dict):
        message = response.get("error_message") or response.get("error") or response.get("message")
        if message is not None:
            return str(message)
        return "No error message provided"
    if hasattr(response, "error_message"):
        return str(response.error_message)
    return "No error message provided"


def _is_404_error(exc: Exception) -> bool:
    """Check if exception is a 404 HTTP error.

    Args:
        exc: The exception to check.

    Returns:
        True if exception represents a 404 error.
    """
    response = getattr(exc, "response", None)
    status_code = getattr(response, "status_code", None)
    if status_code is None:
        return False
    try:
        return int(status_code) == 404
    except (TypeError, ValueError):
        return False


def _sleep_with_backoff_sync(
    interval: float,
    *,
    deadline: float,
    backoff_multiplier: float,
    max_backoff: float,
    clamp_only: bool = False,
) -> float:
    """Sleep for the provided interval (clamped to deadline) and return next interval."""

    interval = max(interval, 0.0)
    remaining = deadline - time.time()
    if interval <= 0 or remaining <= 0:
        return interval

    time.sleep(min(interval, remaining))

    if clamp_only:
        return interval

    next_interval = interval * backoff_multiplier
    if next_interval <= interval:
        return min(interval, max_backoff)
    return min(next_interval, max_backoff)


async def _sleep_with_backoff_async(
    interval: float,
    *,
    loop: asyncio.AbstractEventLoop,
    deadline: float,
    backoff_multiplier: float,
    max_backoff: float,
    clamp_only: bool = False,
) -> float:
    """Async counterpart that sleeps then returns the next interval."""

    interval = max(interval, 0.0)
    remaining = deadline - loop.time()
    if interval <= 0 or remaining <= 0:
        return interval

    await asyncio.sleep(min(interval, remaining))

    if clamp_only:
        return interval

    next_interval = interval * backoff_multiplier
    if next_interval <= interval:
        return min(interval, max_backoff)
    return min(next_interval, max_backoff)
