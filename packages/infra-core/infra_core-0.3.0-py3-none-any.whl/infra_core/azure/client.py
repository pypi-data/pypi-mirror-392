"""Shared Azure Function HTTP clients (async + sync)."""

from __future__ import annotations

import asyncio
import os
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import httpx

from ..http_async import AsyncHttpClient, request_async
from ..http_utils import absolute_url


def _merge_headers(defaults: Mapping[str, str], overrides: Mapping[str, str] | None) -> dict[str, str]:
    merged = dict(defaults)
    if overrides:
        merged.update(overrides)
    return merged


@dataclass(frozen=True)
class RequestOptions:
    timeout: float | httpx.Timeout | None = None
    delay: float | None = None
    max_retries: int | None = None
    backoff: float | None = None
    max_backoff: float | None = None


class AzureFunctionAsyncClient:
    """Async HTTP client with retry/backoff tailored for Azure Function APIs."""

    def __init__(
        self,
        base_url: str,
        *,
        api_key: str | None = None,
        timeout: float = 30.0,
        http_client: AsyncHttpClient | None = None,
        default_headers: Mapping[str, str] | None = None,
    ) -> None:
        if not base_url:
            raise ValueError("base_url is required")
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._timeout = timeout
        self._client = http_client or AsyncHttpClient()
        self._headers = dict(default_headers or {})

    async def request(
        self,
        method: str,
        path: str,
        *,
        headers: Mapping[str, str] | None = None,
        params: Mapping[str, Any] | None = None,
        json: Any = None,
        data: Any = None,
        content: Any = None,
        options: RequestOptions | None = None,
    ) -> httpx.Response:
        url = self._url(path)
        merged_headers = _merge_headers(self._headers, headers)
        if self._api_key:
            merged_headers.setdefault("x-functions-key", self._api_key)
        opts = options or RequestOptions()
        timeout = opts.timeout if opts.timeout is not None else self._timeout
        return await request_async(
            method,
            url,
            headers=merged_headers,
            params=params,
            json=json,
            data=data,
            content=content,
            timeout=timeout,
            delay=opts.delay or 0.0,
            max_retries=opts.max_retries if opts.max_retries is not None else 2,
            backoff=opts.backoff if opts.backoff is not None else 1.0,
            max_backoff=opts.max_backoff if opts.max_backoff is not None else 60.0,
            client=self._client,
        )

    async def request_json(self, method: str, path: str, **kwargs: Any) -> Any:
        response = await self.request(method, path, **kwargs)
        if not response.content:
            return {}
        return response.json()

    async def get_json(self, path: str, **kwargs: Any) -> Any:
        return await self.request_json("GET", path, **kwargs)

    async def post_json(self, path: str, *, json: Any, **kwargs: Any) -> Any:
        return await self.request_json("POST", path, json=json, **kwargs)

    async def delete(self, path: str, **kwargs: Any) -> None:
        response = await self.request("DELETE", path, **kwargs)
        response.read()

    def _url(self, path: str) -> str:
        return absolute_url(self._base_url, path)

    @classmethod
    def from_env(
        cls,
        *,
        base_url_env: str,
        api_key_env: str | None = None,
        **kwargs: Any,
    ) -> AzureFunctionAsyncClient:
        base_url = os.getenv(base_url_env)
        if not base_url:
            raise RuntimeError(f"{base_url_env} environment variable is required")
        api_key = os.getenv(api_key_env) if api_key_env else None
        return cls(base_url, api_key=api_key, **kwargs)


class AzureFunctionSyncClient:
    """Synchronous wrapper around the async Azure Function client."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._async_client = AzureFunctionAsyncClient(*args, **kwargs)

    def request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        return asyncio.run(self._async_client.request(method, path, **kwargs))

    def request_json(self, method: str, path: str, **kwargs: Any) -> Any:
        return asyncio.run(self._async_client.request_json(method, path, **kwargs))

    def get_json(self, path: str, **kwargs: Any) -> Any:
        return self.request_json("GET", path, **kwargs)

    def post_json(self, path: str, *, json: Any, **kwargs: Any) -> Any:
        return self.request_json("POST", path, json=json, **kwargs)

    def delete(self, path: str, **kwargs: Any) -> None:
        asyncio.run(self._async_client.delete(path, **kwargs))

    @classmethod
    def from_env(
        cls,
        *,
        base_url_env: str,
        api_key_env: str | None = None,
        **kwargs: Any,
    ) -> AzureFunctionSyncClient:
        base_url = os.getenv(base_url_env)
        if not base_url:
            raise RuntimeError(f"{base_url_env} environment variable is required")
        api_key = os.getenv(api_key_env) if api_key_env else None
        return cls(base_url, api_key=api_key, **kwargs)


__all__ = [
    "AzureFunctionAsyncClient",
    "AzureFunctionSyncClient",
    "RequestOptions",
]
