"""Utilities for building consistent Azure Function HTTP responses."""

from __future__ import annotations

import json
import logging
import sys
from collections.abc import Mapping, Sequence
from http import HTTPStatus
from types import ModuleType
from typing import Any, cast

from ..http_utils import absolute_url as _absolute_url

logger = logging.getLogger(__name__)


def bootstrap_logging(
    *,
    level: int = logging.INFO,
    logger_names: Sequence[str] | None = None,
) -> None:
    """Configure stdout logging suitable for Azure Functions."""

    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )
    for name in logger_names or ():
        logging.getLogger(name).setLevel(level)


def json_response(
    payload: Mapping[str, Any],
    *,
    status: HTTPStatus = HTTPStatus.OK,
    headers: Mapping[str, str] | None = None,
) -> Any:
    """Return an azure.functions.HttpResponse with the given JSON payload."""

    func = _require_azure_functions()
    response_headers = {"Cache-Control": "no-store"}
    if headers:
        response_headers.update(headers)
    return func.HttpResponse(
        body=json.dumps(payload, ensure_ascii=False, indent=2),
        status_code=int(status),
        mimetype="application/json",
        headers=response_headers,
    )


def error_response(
    code: str,
    message: str,
    *,
    status: HTTPStatus,
    log: logging.Logger | None = None,
) -> Any:
    """Return a standardised error response."""

    (log or logger).error("API error [%s]: %s", code, message)
    return json_response({"error": {"code": code, "message": message}}, status=status)


def absolute_url(request_url: str | Any, *segments: str) -> str:
    """Build an absolute URL for a request and path segments."""

    base = str(request_url)
    return _absolute_url(base, *segments)


def _require_azure_functions() -> ModuleType:
    try:
        import azure.functions as func
    except ModuleNotFoundError as exc:  # pragma: no cover - requires Azure runtime
        raise RuntimeError("azure.functions is required to build Azure Function responses.") from exc
    return cast(ModuleType, func)


__all__ = ["bootstrap_logging", "json_response", "error_response", "absolute_url"]
