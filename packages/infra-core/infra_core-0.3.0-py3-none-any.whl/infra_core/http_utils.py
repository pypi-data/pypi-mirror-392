"""Lightweight HTTP helper utilities shared across infra_core."""

from __future__ import annotations


def absolute_url(base: str, *segments: str) -> str:
    """Return an absolute URL by joining the base with one or more path segments."""

    url = (base or "").rstrip("/")
    for segment in segments:
        trimmed = (segment or "").strip("/")
        if not trimmed:
            continue
        url = f"{url}/{trimmed}" if url else f"/{trimmed}"
    return url or "/"


__all__ = ["absolute_url"]
