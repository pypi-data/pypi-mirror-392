"""Azure integration helpers shared across infra_core.

This package centralises all Azure-specific modules (storage, monitoring,
function helpers, clients, etc.) so downstream services can import from
`infra_core.azure.*` without guessing module names at the top level.
"""

from __future__ import annotations

from . import (
    client,  # re-export module for monkeypatching
    monitoring,  # re-export module for monkeypatching
)
from .client import AzureFunctionAsyncClient, AzureFunctionSyncClient, RequestOptions
from .exceptions import (
    AzureServiceError,
    AzureTableError,
    JobNotFoundError,
    JobTimeoutError,
    ResumeSourceActive,
    ResumeSourceNotFound,
    RunNotFound,
    RunServiceError,
)
from .function_cli import add_azure_service_arguments
from .job_store import AzureTableJobStore, TableConfig
from .monitoring import HeartbeatMonitor, RunLogWriter, TelemetryClient
from .run_service import RunStorageMixin
from .run_storage import (
    build_manifest,
    build_run_storage_path,
    collect_blob_files,
    collect_local_files,
    resolve_base_path,
)
from .storage import (
    AzureStorageClient,
    AzureStorageSettings,
    blob_path_for,
    download_to_path,
    download_to_path_async,
    download_tree,
    download_tree_async,
    get_client,
    is_enabled,
    list_tree,
    list_tree_async,
    upload_file,
    upload_file_async,
    upload_text,
    upload_text_async,
)

__all__ = [
    "AzureStorageClient",
    "AzureStorageSettings",
    "blob_path_for",
    "download_to_path",
    "download_to_path_async",
    "download_tree",
    "download_tree_async",
    "get_client",
    "is_enabled",
    "list_tree",
    "list_tree_async",
    "upload_file",
    "upload_file_async",
    "upload_text",
    "upload_text_async",
    "RunLogWriter",
    "HeartbeatMonitor",
    "TelemetryClient",
    "AzureTableError",
    "AzureTableJobStore",
    "TableConfig",
    "AzureFunctionAsyncClient",
    "AzureFunctionSyncClient",
    "RequestOptions",
    "build_manifest",
    "build_run_storage_path",
    "collect_blob_files",
    "collect_local_files",
    "resolve_base_path",
    "AzureServiceError",
    "RunServiceError",
    "RunNotFound",
    "ResumeSourceNotFound",
    "ResumeSourceActive",
    "JobNotFoundError",
    "JobTimeoutError",
    "RunStorageMixin",
    "monitoring",
    "client",
    "add_azure_service_arguments",
]
