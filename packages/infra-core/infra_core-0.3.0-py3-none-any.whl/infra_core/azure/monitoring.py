"""Shared run logging, heartbeat, and telemetry helpers for Azure services."""

from __future__ import annotations

import json
import logging
import os
import threading
import time
from collections.abc import Callable, Mapping
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any, Final

from ..fs_utils import ensure_parent
from . import storage as azure_storage

logger = logging.getLogger(__name__)

UtcNowFunc = Callable[[], str]


class TelemetryEvent(str, Enum):
    """Canonical telemetry events emitted by shared services."""

    STARTED = "started"
    PROGRESS = "progress"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"

    def __str__(self) -> str:
        return self.value


TELEMETRY_EVENTS: Final[frozenset[str]] = frozenset(event.value for event in TelemetryEvent)


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


class RunLogWriter:
    """Append structured log entries for a run and mirror them to blob storage."""

    def __init__(
        self,
        storage_root: Path,
        *,
        azure_client: azure_storage.AzureStorageClient | None = None,
        utc_now: UtcNowFunc | None = None,
    ):
        self._log_path = storage_root / "_logs" / "run.log"
        self._lock = threading.Lock()
        self._azure_client = azure_client
        self._utc_now = utc_now or _utc_now

    @property
    def path(self) -> Path:
        return self._log_path

    def write(self, event: str, **properties: Any) -> dict[str, Any]:
        record: dict[str, Any] = {"timestamp": self._utc_now(), "event": event}
        record.update(properties)
        line = json.dumps(record, ensure_ascii=False) + "\n"
        with self._lock:
            ensure_parent(self._log_path)
            with self._log_path.open("a", encoding="utf-8") as handle:
                handle.write(line)
        self._mirror()
        return record

    def _mirror(self) -> None:
        client = self._azure_client or azure_storage.get_client()
        if hasattr(client, "is_configured") and not client.is_configured():  # pragma: no cover - optional path
            return
        try:
            client.upload_file(self._log_path)
        except Exception:  # pragma: no cover - defensive
            logger.debug("Failed to upload run log %s", self._log_path, exc_info=True)


class HeartbeatMonitor:
    """Persist heartbeat metadata and trigger callbacks when slugs stall."""

    def __init__(
        self,
        storage_root: Path,
        *,
        interval_seconds: float = 30.0,
        slug_timeout_seconds: float | None = 300.0,
        log_writer: RunLogWriter | None = None,
        on_timeout: Callable[[str, float], None] | None = None,
        force_first_slug_timeout: bool = False,
        force_first_slug_delay: float = 0.0,
        azure_client: azure_storage.AzureStorageClient | None = None,
        utc_now: UtcNowFunc | None = None,
    ):
        self._heartbeat_path = storage_root / "_state" / "heartbeat.json"
        self._interval = max(0.05, float(interval_seconds))
        self._slug_timeout = float(slug_timeout_seconds) if slug_timeout_seconds else None
        self._log_writer = log_writer
        self._on_timeout = on_timeout
        self._azure_client = azure_client
        self._utc_now = utc_now or _utc_now

        self._lock = threading.Lock()
        self._current_slug: str | None = None
        self._slug_started_at: float | None = None
        self._last_persist: float = 0.0
        self._timed_out_slug: str | None = None

        self._force_first_slug_timeout = force_first_slug_timeout
        self._force_first_slug_delay = max(0.0, float(force_first_slug_delay))
        self._force_timeout_fired = False
        self._timers: list[threading.Timer] = []

        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, name="heartbeat-monitor", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        with self._lock:
            for timer in self._timers:
                timer.cancel()
            self._timers.clear()
        if self._thread:
            self._thread.join(timeout=self._interval)
        self._persist(force=True)

    def set_slug(self, slug: str | None) -> None:
        with self._lock:
            self._current_slug = slug
            self._slug_started_at = time.monotonic() if slug else None
            self._timed_out_slug = None
            force_timeout = self._force_first_slug_timeout and not self._force_timeout_fired and slug is not None
            if force_timeout:
                self._force_timeout_fired = True
                timer = threading.Timer(
                    self._force_first_slug_delay,
                    self._trigger_timeout,
                    args=(slug, self._force_first_slug_delay),
                )
                timer.daemon = True
                self._timers.append(timer)
                timer.start()
        self._persist(force=True)

    def pulse(self) -> None:
        self._persist()

    # Internal -----------------------------------------------------------------

    def _run(self) -> None:
        while not self._stop.wait(self._interval):
            self._persist()
            self._check_timeout()

    def _persist(self, force: bool = False) -> None:
        now_monotonic = time.monotonic()
        with self._lock:
            if not force and (now_monotonic - self._last_persist) < self._interval:
                return
            heartbeat = {"timestamp": self._utc_now(), "slug": self._current_slug}
            self._last_persist = now_monotonic
        ensure_parent(self._heartbeat_path)
        self._heartbeat_path.write_text(json.dumps(heartbeat, ensure_ascii=False) + "\n", encoding="utf-8")
        self._mirror(heartbeat)
        if self._log_writer:
            self._log_writer.write("heartbeat", **heartbeat)

    def _mirror(self, heartbeat: dict[str, Any]) -> None:
        client = self._azure_client or azure_storage.get_client()
        if hasattr(client, "is_configured") and not client.is_configured():  # pragma: no cover - optional path
            return
        writer = getattr(client, "write_json", None)
        if callable(writer):
            try:
                writer(self._heartbeat_path, heartbeat)
                return
            except Exception:  # pragma: no cover - defensive
                logger.debug("Failed to write heartbeat JSON via client", exc_info=True)
        uploader = getattr(client, "upload_file", None)
        if callable(uploader):
            try:
                uploader(self._heartbeat_path)
            except Exception:  # pragma: no cover - defensive
                logger.debug(
                    "Failed to upload heartbeat file %s",
                    self._heartbeat_path,
                    exc_info=True,
                )

    def _check_timeout(self) -> None:
        if self._slug_timeout is None:
            return
        with self._lock:
            slug = self._current_slug
            started_at = self._slug_started_at
            timed_out_slug = self._timed_out_slug
        if not slug or started_at is None:
            return
        elapsed = time.monotonic() - started_at
        if elapsed >= self._slug_timeout and slug != timed_out_slug:
            self._trigger_timeout(slug, elapsed)

    def _trigger_timeout(self, slug: str, elapsed: float) -> None:
        with self._lock:
            if self._timed_out_slug == slug:
                return
            self._timed_out_slug = slug
        if self._log_writer:
            self._log_writer.write("heartbeat_timeout", slug=slug, elapsed_seconds=round(elapsed, 2))
        if self._on_timeout:
            try:
                self._on_timeout(slug, elapsed)
            except Exception:  # pragma: no cover - defensive
                logger.warning("Heartbeat timeout callback failed for %s", slug, exc_info=True)


class TelemetryClient:
    """Structured telemetry logger backed by Application Insights instrumentation."""

    def __init__(
        self,
        *,
        service_name: str = "infra_core",
        logger_name: str | None = None,
    ):
        self._service_name = service_name
        self._logger = logging.getLogger(logger_name or f"{service_name}.azure.telemetry")
        self._enabled = bool(
            os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING") or os.getenv("APPINSIGHTS_INSTRUMENTATIONKEY")
        )
        if self._enabled:
            self.track_event(
                TelemetryEvent.STARTED,
                metadata={"stage": "telemetry_initialized"},
            )

    def validate_event(self, name: TelemetryEvent | str) -> TelemetryEvent:
        """Return a normalized telemetry event or raise ``ValueError`` if invalid."""

        return _normalize_telemetry_event(name)

    def track_event(self, name: TelemetryEvent | str, **properties: Any) -> None:
        event = self.validate_event(name)
        payload = self._build_payload(event, dict(properties))
        if not self._enabled:
            return
        self._logger.info("telemetry_event %s", json.dumps(payload, ensure_ascii=False, default=str))

    def track_error(self, name: TelemetryEvent | str, **properties: Any) -> None:
        event = self.validate_event(name)
        payload = self._build_payload(event, dict(properties))
        if not self._enabled:
            return
        self._logger.error("telemetry_error %s", json.dumps(payload, ensure_ascii=False, default=str))

    def _build_payload(self, event: TelemetryEvent, properties: dict[str, Any]) -> dict[str, Any]:
        metadata: dict[str, Any] = dict(properties)
        service = _coerce_required_str(metadata.pop("service", self._service_name), field="service")
        batch_id = _coerce_optional_str(metadata.pop("batch_id", None), field="batch_id")
        job_id = _coerce_optional_str(metadata.pop("job_id", None), field="job_id")
        slug = _coerce_optional_str(metadata.pop("slug", None), field="slug")

        explicit_metadata = metadata.pop("metadata", None)
        metadata_payload: dict[str, Any] = {}
        if explicit_metadata is not None:
            if not isinstance(explicit_metadata, Mapping):
                raise ValueError("metadata must be a mapping when provided")
            metadata_payload = dict(explicit_metadata)
        if metadata:
            metadata_payload.update(metadata)

        for key in metadata_payload:
            if not isinstance(key, str):
                raise ValueError("metadata keys must be strings")

        payload: dict[str, Any] = {
            "service": service,
            "event": event.value,
            "batch_id": batch_id,
            "job_id": job_id,
            "slug": slug,
        }
        if metadata_payload:
            payload["metadata"] = metadata_payload
        return payload


def _normalize_telemetry_event(name: TelemetryEvent | str) -> TelemetryEvent:
    if isinstance(name, TelemetryEvent):
        return name
    event = str(name or "").strip().lower()
    if not event:
        raise ValueError("telemetry event name is required")
    for candidate in TelemetryEvent:
        if candidate.value == event:
            return candidate
    raise ValueError(
        f"telemetry event '{name}' is not one of: {', '.join(sorted(event.value for event in TelemetryEvent))}"
    )


def _coerce_optional_str(value: Any, *, field: str) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        stripped = value.strip()
        return stripped or None
    raise ValueError(f"{field} must be a string when provided")


def _coerce_required_str(value: Any, *, field: str) -> str:
    result = _coerce_optional_str(value, field=field)
    if result is None:
        raise ValueError(f"{field} must be a non-empty string")
    return result


__all__ = [
    "RunLogWriter",
    "HeartbeatMonitor",
    "TelemetryClient",
    "TelemetryEvent",
    "TELEMETRY_EVENTS",
]
