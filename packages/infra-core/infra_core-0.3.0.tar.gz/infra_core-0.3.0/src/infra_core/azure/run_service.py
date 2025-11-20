"""Shared run service primitives for Azure-backed HTTP handlers.

This module exposes the storage mixin used by the crawler and screenshot
services. The mixin centralises Azure Storage client wiring and manifest
generation so individual services can focus on their domain-specific
behaviour (resume handling, progress tracking, etc.).

Example:
    >>> from infra_core.azure.run_service import RunStorageMixin
    >>> class DemoService(RunStorageMixin):
    ...     def describe(self, record) -> dict[str, object]:
    ...         return self.build_result_manifest(record)
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .exceptions import (  # re-exported for backwards compatibility
    ResumeSourceActive,
    ResumeSourceNotFound,
    RunNotFound,
    RunServiceError,
)
from .run_storage import build_manifest
from .storage import AzureStorageClient, get_client


class RunStorageMixin:
    """Mixin that provides shared manifest helpers for Azure-backed services."""

    def __init__(self, *, azure_client: AzureStorageClient | None = None) -> None:
        self._azure_client = azure_client

    def build_result_manifest(self, record: Any) -> Mapping[str, object]:
        """Return a manifest for the run described by ``record``.

        Args:
            record: Object with a ``run_storage_path`` attribute referencing the
                local directory that holds run artifacts.

        Returns:
            Mapping compatible with existing HTTP payloads containing
            ``storage_path``, ``files``, and optionally ``blob_prefix``.
        """

        storage_root = str(getattr(record, "run_storage_path", "") or "").strip()
        return build_manifest(storage_root, client=self._client())

    def _client(self) -> AzureStorageClient:
        if self._azure_client is not None:
            return self._azure_client
        return get_client()


__all__ = [
    "RunServiceError",
    "RunNotFound",
    "ResumeSourceNotFound",
    "ResumeSourceActive",
    "RunStorageMixin",
]
