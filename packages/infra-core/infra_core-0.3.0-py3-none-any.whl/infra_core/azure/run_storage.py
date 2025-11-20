"""Shared filesystem/blob storage helpers for Azure-hosted run services.

This module centralises the logic for building run storage paths, enumerating
local artifacts, and mirroring them with Azure Blob Storage. Services can reuse
these helpers to keep manifest generation consistent across crawler and
screenshot workloads.

Example:
    >>> from infra_core.azure.run_storage import build_run_storage_path
    >>> path = build_run_storage_path("CRAWL_STORAGE_BASE", "runs", "batch", "job")
    >>> path.parts[-3:]
    ('runs', 'batch', 'job')
"""

from __future__ import annotations

import logging
import os
import tempfile
from collections.abc import Iterable, Mapping
from pathlib import Path

from .storage import AzureStorageClient, get_client

_DEFAULT_FALLBACK_ENVS: tuple[str, ...] = ("TMP", "TEMP", "TMPDIR")


logger = logging.getLogger(__name__)


def resolve_base_path(env_var: str, *, fallback_envs: Iterable[str] | None = None) -> Path:
    """Resolve the root directory for run storage.

    Prefers the explicit ``env_var`` override, then checks common temporary
    directory variables before falling back to ``tempfile.gettempdir``.

    Args:
        env_var: Name of the environment variable that points to the desired
            base directory.
        fallback_envs: Optional iterable of environment variables to probe
            when ``env_var`` is unset or empty. Defaults to ``TMPDIR``, ``TMP``,
            and ``TEMP``.

    Returns:
        Path to the directory that should contain run artifacts.
    """

    override = (os.getenv(env_var) or "").strip()
    if override:
        return Path(override)

    for candidate in fallback_envs or _DEFAULT_FALLBACK_ENVS:
        value = (os.getenv(candidate) or "").strip()
        if value:
            return Path(value)

    return Path(tempfile.gettempdir())


def build_run_storage_path(env_var: str, *segments: str, fallback_envs: Iterable[str] | None = None) -> Path:
    """Build a run storage path below the resolved base directory.

    Args:
        env_var: Environment variable that controls the storage base.
        *segments: Additional path components appended under the base.
        fallback_envs: Optional override for the fallback variable probe order.

    Returns:
        Full path to the run storage directory.
    """

    base = resolve_base_path(env_var, fallback_envs=fallback_envs)
    path = base
    for segment in segments:
        if segment:
            path /= segment
    return path


def collect_local_files(storage_path: Path) -> list[dict[str, int | str]]:
    """Return file metadata for on-disk artifacts within ``storage_path``.

    Args:
        storage_path: Directory containing run artifacts.

    Returns:
        List of ``{"path": <relative>, "size": <bytes>}`` dictionaries sorted
        lexicographically by path. Returns an empty list when the directory does
        not exist.
    """

    if not storage_path.exists() or not storage_path.is_dir():
        return []

    items: list[dict[str, int | str]] = []
    for path in storage_path.rglob("*"):
        if path.is_file():
            items.append(
                {
                    "path": str(path.relative_to(storage_path)),
                    "size": path.stat().st_size,
                }
            )
    items.sort(key=lambda item: item["path"])
    return items


def collect_blob_files(client: AzureStorageClient, storage_path: Path) -> list[dict[str, int | str]]:
    """Enumerate blob-backed artifacts for ``storage_path`` via ``client``.

    Args:
        client: Azure storage client used to list blob contents.
        storage_path: Local directory whose relative structure is mirrored in
            Azure Blob Storage.

    Returns:
        List of ``{"path": <relative>, "size": <bytes>}`` dictionaries sorted
        lexicographically by path. Returns an empty list if the client is not
        configured or errors occur while listing.
    """

    if not client.is_configured():
        return []

    try:
        entries = client.list_tree(storage_path)
    except Exception as exc:  # pragma: no cover - defensive guard around SDK failures
        logger.warning(
            "Failed to enumerate Azure storage for run manifest",
            extra={"storage_path": str(storage_path), "error": type(exc).__name__},
            exc_info=True,
        )
        return []

    items: list[dict[str, int | str]] = [{"path": relative_path, "size": size} for relative_path, size in entries]
    items.sort(key=lambda item: item["path"])
    return items


def build_manifest(
    storage_path: str | Path,
    *,
    client: AzureStorageClient | None = None,
) -> Mapping[str, object]:
    """Assemble a manifest describing files for the given run storage path.

    Args:
        storage_path: Directory on disk that may contain run artifacts.
        client: Optional Azure storage client. When omitted, the shared
            ``infra_core.azure.storage`` client is used.

    Returns:
        Mapping with ``storage_path`` (string), ``files`` (list of file entries),
        and optional ``blob_prefix`` when Azure storage is configured.
    """

    root = Path(storage_path) if storage_path else None
    if root is None or not str(root).strip():
        return {"storage_path": "", "files": []}

    azure_client = client or get_client()
    files = collect_local_files(root)
    if not files:
        files = collect_blob_files(azure_client, root)

    manifest: dict[str, object] = {
        "storage_path": str(root),
        "files": files,
    }
    if azure_client.is_configured():
        manifest["blob_prefix"] = azure_client.blob_name_for_path(root)
    return manifest


__all__ = [
    "resolve_base_path",
    "build_run_storage_path",
    "collect_local_files",
    "collect_blob_files",
    "build_manifest",
]
