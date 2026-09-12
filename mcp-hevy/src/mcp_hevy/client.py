from __future__ import annotations

import os
from typing import Any

import httpx

_BASE_URL = "https://api.hevyapp.com"

_client: httpx.Client | None = None


def get_client() -> httpx.Client:
    """Return the Hevy httpx.Client singleton, creating it on first call."""
    global _client
    if _client is None:
        _client = _create_client()
    return _client


def _create_client() -> httpx.Client:
    api_key = os.environ.get("HEVY_API_KEY")
    if not api_key:
        raise RuntimeError(
            "HEVY_API_KEY not set. Generate a key at "
            "https://hevy.com/settings?developer and set it in your MCP server config."
        )
    return httpx.Client(base_url=_BASE_URL, headers={"api-key": api_key}, timeout=30.0)


def get_json(client: httpx.Client, path: str, params: dict[str, Any] | None = None) -> Any:
    """GET path and return parsed JSON, raising RuntimeError with context on failure."""
    try:
        response = client.get(path, params=params)
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise RuntimeError(
            f"Hevy API error {exc.response.status_code} for {path}: {exc.response.text}"
        ) from exc
    except httpx.RequestError as exc:
        raise RuntimeError(f"Hevy API request failed for {path}: {exc}") from exc
    return response.json()
