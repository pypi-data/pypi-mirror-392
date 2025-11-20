"""Shared exception hierarchy for Azure-hosted services."""

from __future__ import annotations


class AzureServiceError(Exception):
    """Base exception for recoverable Azure service errors."""


class AzureTableError(AzureServiceError):
    """Raised when Azure Table storage cannot be initialised or accessed."""


class JobNotFoundError(AzureServiceError):
    """Raised when a job cannot be found in the backing store."""


class JobTimeoutError(AzureServiceError):
    """Raised when a job exceeds its allowed execution window."""


class RunServiceError(AzureServiceError):
    """Base exception for run-service level failures."""


class RunNotFound(RunServiceError):
    """Raised when a requested run does not exist."""

    def __init__(self, batch_id: str, job_id: str) -> None:
        super().__init__(f"Run '{job_id}' not found in batch '{batch_id}'")
        self.batch_id = batch_id
        self.job_id = job_id


class ResumeSourceNotFound(RunServiceError):
    """Raised when the requested resume source cannot be located."""

    def __init__(self, batch_id: str, job_id: str) -> None:
        super().__init__(f"Run '{job_id}' not found in batch '{batch_id}'")
        self.batch_id = batch_id
        self.job_id = job_id


class ResumeSourceActive(RunServiceError):
    """Raised when a resume source is still running."""

    def __init__(self, job_id: str) -> None:
        super().__init__(f"Cannot resume from a run that is still running ({job_id})")
        self.job_id = job_id


__all__ = [
    "AzureServiceError",
    "AzureTableError",
    "JobNotFoundError",
    "JobTimeoutError",
    "RunServiceError",
    "RunNotFound",
    "ResumeSourceNotFound",
    "ResumeSourceActive",
]
