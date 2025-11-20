"""Tests for infra_core.polling module."""

from __future__ import annotations

import time
from typing import Any

import pytest

from infra_core.polling import (
    PollingConfig,
    PollingError,
    PollingFailureError,
    PollingTimeoutError,
    StatusPoller,
    poll_until,
    poll_until_async,
)


class TestPollingConfig:
    """Tests for PollingConfig dataclass."""

    def test_default_values(self):
        """Test that default values are set correctly."""
        config = PollingConfig()
        assert config.timeout == 600.0
        assert config.poll_interval == 5.0
        assert config.initial_delay == 0.0
        assert config.max_backoff == 60.0
        assert config.backoff_multiplier == 1.0
        assert config.terminal_statuses is None
        assert config.failure_statuses is None

    def test_custom_values(self):
        """Test creating config with custom values."""
        config = PollingConfig(
            timeout=300.0,
            poll_interval=2.0,
            terminal_statuses={"done", "failed"},
        )
        assert config.timeout == 300.0
        assert config.poll_interval == 2.0
        assert config.terminal_statuses == frozenset({"done", "failed"})

    def test_sets_cast_to_frozenset(self):
        """Ensure mutable sets are converted to frozensets for immutability."""
        config = PollingConfig(terminal_statuses={"done"}, failure_statuses={"failed"})

        assert isinstance(config.terminal_statuses, frozenset)
        assert isinstance(config.failure_statuses, frozenset)

    def test_validation_negative_timeout(self):
        """Test that negative timeout raises ValueError."""
        with pytest.raises(ValueError, match="timeout must be positive"):
            PollingConfig(timeout=-1.0)

    def test_validation_zero_poll_interval(self):
        """Test that zero poll_interval raises ValueError."""
        with pytest.raises(ValueError, match="poll_interval must be positive"):
            PollingConfig(poll_interval=0.0)

    def test_validation_invalid_backoff_multiplier(self):
        """Test that backoff_multiplier < 1.0 raises ValueError."""
        with pytest.raises(ValueError, match="backoff_multiplier must be >= 1.0"):
            PollingConfig(backoff_multiplier=0.5)


class TestPollUntil:
    """Tests for poll_until synchronous polling function."""

    def test_poll_until_immediate_success(self):
        """Test polling that succeeds immediately."""
        result = poll_until(
            fetch_fn=lambda: {"status": "completed"},
            is_terminal=lambda r: r["status"] == "completed",
            timeout=10.0,
            poll_interval=1.0,
        )
        assert result == {"status": "completed"}

    def test_poll_until_multiple_polls(self):
        """Test polling that requires multiple attempts."""
        call_count = 0

        def fetch():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                return {"status": "running"}
            return {"status": "completed"}

        result = poll_until(
            fetch_fn=fetch,
            is_terminal=lambda r: r["status"] == "completed",
            timeout=10.0,
            poll_interval=0.1,
        )

        assert result == {"status": "completed"}
        assert call_count == 3

    def test_poll_until_timeout(self):
        """Test polling that times out."""
        with pytest.raises(PollingTimeoutError) as exc_info:
            poll_until(
                fetch_fn=lambda: {"status": "running"},
                is_terminal=lambda r: r["status"] == "completed",
                timeout=0.3,
                poll_interval=0.1,
            )

        assert "timed out" in str(exc_info.value).lower()
        assert exc_info.value.last_response == {"status": "running"}

    def test_poll_until_with_callback(self):
        """Test polling with progress callback."""
        responses = []

        def on_poll(response):
            responses.append(response)

        call_count = 0

        def fetch():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                return {"status": "running", "progress": call_count}
            return {"status": "completed", "progress": call_count}

        result = poll_until(
            fetch_fn=fetch,
            is_terminal=lambda r: r["status"] == "completed",
            timeout=10.0,
            poll_interval=0.1,
            on_poll=on_poll,
        )

        assert result == {"status": "completed", "progress": 3}
        assert len(responses) == 3

    def test_poll_until_backoff_growth(self, monkeypatch):
        """Ensure exponential backoff applies between polls."""
        sleeps: list[float] = []
        monkeypatch.setattr("infra_core.polling.time.sleep", lambda duration: sleeps.append(duration))

        call_count = 0

        def fetch():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                return {"status": "running"}
            return {"status": "completed"}

        poll_until(
            fetch_fn=fetch,
            is_terminal=lambda r: r["status"] == "completed",
            timeout=10.0,
            poll_interval=0.1,
            backoff_multiplier=2.0,
            max_backoff=1.0,
        )

        assert sleeps == [pytest.approx(0.1, rel=0.01), pytest.approx(0.2, rel=0.01)]


class TestPollUntilAsync:
    """Tests for poll_until_async asynchronous polling function."""

    @pytest.mark.asyncio
    async def test_poll_until_async_immediate_success(self):
        """Test async polling that succeeds immediately."""

        async def fetch():
            return {"status": "completed"}

        result = await poll_until_async(
            fetch_fn=fetch,
            is_terminal=lambda r: r["status"] == "completed",
            timeout=10.0,
            poll_interval=0.1,
        )
        assert result == {"status": "completed"}

    @pytest.mark.asyncio
    async def test_poll_until_async_multiple_polls(self):
        """Test async polling that requires multiple attempts."""
        call_count = 0

        async def fetch():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                return {"status": "running"}
            return {"status": "completed"}

        result = await poll_until_async(
            fetch_fn=fetch,
            is_terminal=lambda r: r["status"] == "completed",
            timeout=10.0,
            poll_interval=0.1,
        )

        assert result == {"status": "completed"}
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_poll_until_async_timeout(self):
        """Test async polling that times out."""

        async def fetch():
            return {"status": "running"}

        with pytest.raises(PollingTimeoutError) as exc_info:
            await poll_until_async(
                fetch_fn=fetch,
                is_terminal=lambda r: r["status"] == "completed",
                timeout=0.3,
                poll_interval=0.1,
            )

        assert "timed out" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_poll_until_async_with_sync_function(self):
        """Test async polling with synchronous fetch function."""
        call_count = 0

        def fetch():  # Sync function
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                return {"status": "running"}
            return {"status": "completed"}

        result = await poll_until_async(
            fetch_fn=fetch,
            is_terminal=lambda r: r["status"] == "completed",
            timeout=10.0,
            poll_interval=0.1,
        )

        assert result == {"status": "completed"}
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_poll_until_async_awaitable_callback(self):
        """Ensure async callbacks are awaited between polls."""
        call_order: list[str] = []

        async def fetch():
            if len(call_order) < 1:
                return {"status": "running"}
            return {"status": "completed"}

        async def on_poll(response: Any) -> None:
            call_order.append(response["status"])

        result = await poll_until_async(
            fetch_fn=fetch,
            is_terminal=lambda r: r["status"] == "completed",
            timeout=10.0,
            poll_interval=0.01,
            on_poll=on_poll,
        )

        assert result == {"status": "completed"}
        assert call_order == ["running", "completed"]


class TestStatusPoller:
    """Tests for StatusPoller high-level polling class."""

    def test_status_poller_success(self):
        """Test successful polling with StatusPoller."""
        call_count = 0

        def fetch():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                return {"status": "running"}
            return {"status": "completed"}

        config = PollingConfig(
            timeout=10.0,
            poll_interval=0.1,
            terminal_statuses={"completed", "failed"},
        )
        poller = StatusPoller(fetch_fn=fetch, config=config)

        result = poller.poll()
        assert result == {"status": "completed"}
        assert call_count == 3

    def test_status_poller_failure_detection(self):
        """Test that StatusPoller detects failure statuses."""

        def fetch():
            return {"status": "failed", "error": "Something went wrong"}

        config = PollingConfig(
            timeout=10.0,
            poll_interval=0.1,
            terminal_statuses={"completed", "failed"},
            failure_statuses={"failed"},
        )
        poller = StatusPoller(fetch_fn=fetch, config=config)

        with pytest.raises(PollingFailureError) as exc_info:
            poller.poll()

        assert "failed" in str(exc_info.value).lower()
        assert exc_info.value.response == {"status": "failed", "error": "Something went wrong"}

    def test_status_poller_timeout(self):
        """Test StatusPoller timeout."""

        def fetch():
            return {"status": "running"}

        config = PollingConfig(
            timeout=0.3,
            poll_interval=0.1,
            terminal_statuses={"completed"},
        )
        poller = StatusPoller(fetch_fn=fetch, config=config)

        with pytest.raises(PollingTimeoutError):
            poller.poll()

    @pytest.mark.asyncio
    async def test_status_poller_async(self):
        """Test async polling with StatusPoller."""
        call_count = 0

        async def fetch():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                return {"status": "running"}
            return {"status": "completed"}

        config = PollingConfig(
            timeout=10.0,
            poll_interval=0.1,
            terminal_statuses={"completed", "failed"},
        )
        poller = StatusPoller(fetch_fn=fetch, config=config)

        result = await poller.poll_async()
        assert result == {"status": "completed"}
        assert call_count == 3

    def test_status_poller_with_initial_delay(self):
        """Test StatusPoller with initial delay."""
        call_count = 0

        def fetch():
            nonlocal call_count
            call_count += 1
            return {"status": "completed"}

        config = PollingConfig(
            timeout=10.0,
            poll_interval=0.1,
            initial_delay=0.2,
            terminal_statuses={"completed"},
        )
        poller = StatusPoller(fetch_fn=fetch, config=config)

        start_time = time.time()
        poller.poll()
        elapsed = time.time() - start_time

        # Should have waited at least initial_delay
        assert elapsed >= 0.2
        assert call_count == 1

    def test_status_poller_custom_status_extractor(self):
        """Test StatusPoller with custom status extractor."""

        def fetch():
            return {"result": {"state": "done"}}

        def extract_status(response):
            return response["result"]["state"]

        config = PollingConfig(
            timeout=10.0,
            poll_interval=0.1,
            terminal_statuses={"done"},
        )
        poller = StatusPoller(
            fetch_fn=fetch,
            config=config,
            status_extractor=extract_status,
        )

        result = poller.poll()
        assert result == {"result": {"state": "done"}}


class TestPollingExceptions:
    """Tests for polling exception types."""

    def test_polling_timeout_error_attributes(self):
        """Test PollingTimeoutError attributes."""
        error = PollingTimeoutError(
            message="Timeout after 30s",
            last_response={"status": "running"},
        )

        assert "Timeout after 30s" in str(error)
        assert error.last_response == {"status": "running"}

    def test_polling_failure_error_attributes(self):
        """Test PollingFailureError attributes."""
        error = PollingFailureError(
            message="Operation failed",
            response={"status": "failed", "error": "Invalid input"},
        )

        assert "Operation failed" in str(error)
        assert error.response == {"status": "failed", "error": "Invalid input"}

    def test_exception_hierarchy(self):
        """Test that exceptions inherit from PollingError."""
        assert issubclass(PollingTimeoutError, PollingError)
        assert issubclass(PollingFailureError, PollingError)
        assert issubclass(PollingError, Exception)


class TestEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_poll_until_with_exception_in_fetch(self):
        """Test polling when fetch_fn raises exception."""

        def fetch():
            raise RuntimeError("Simulated error")

        with pytest.raises(RuntimeError, match="Simulated error"):
            poll_until(
                fetch_fn=fetch,
                is_terminal=lambda r: False,
                timeout=1.0,
                poll_interval=0.1,
            )

    def test_status_poller_fallback_terminal_statuses(self):
        """Test StatusPoller with no configured terminal statuses (uses fallback)."""

        def fetch():
            return {"status": "completed"}

        config = PollingConfig(
            timeout=10.0,
            poll_interval=0.1,
            # No terminal_statuses specified - uses fallback
        )
        poller = StatusPoller(fetch_fn=fetch, config=config)

        result = poller.poll()
        assert result == {"status": "completed"}

    def test_default_status_extractor_with_non_dict(self):
        """Test default status extractor with non-dict response."""

        # Create a mock object with a status attribute
        class MockResponse:
            status = "completed"

        def fetch():
            return MockResponse()

        config = PollingConfig(
            timeout=10.0,
            poll_interval=0.1,
            terminal_statuses={"completed"},
        )
        poller = StatusPoller(fetch_fn=fetch, config=config)

        result = poller.poll()
        assert isinstance(result, MockResponse)
        assert result.status == "completed"
