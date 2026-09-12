from unittest.mock import MagicMock

import httpx
import pytest

import mcp_hevy.client as client_module
from mcp_hevy.client import get_client, get_json


@pytest.fixture(autouse=True)
def reset_client_singleton() -> None:
    client_module._client = None


def test_get_client_raises_when_api_key_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("HEVY_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="HEVY_API_KEY"):
        get_client()


def test_get_client_returns_httpx_client_with_api_key_header(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("HEVY_API_KEY", "test-key-123")
    client = get_client()
    assert isinstance(client, httpx.Client)
    assert client.headers["api-key"] == "test-key-123"
    assert str(client.base_url) == "https://api.hevyapp.com"


def test_get_client_returns_singleton(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HEVY_API_KEY", "test-key-123")
    assert get_client() is get_client()


def _make_response(json_data: object, status_ok: bool = True) -> MagicMock:
    response = MagicMock()
    response.json.return_value = json_data
    if status_ok:
        response.raise_for_status.return_value = None
    else:
        request = httpx.Request("GET", "https://api.hevyapp.com/v1/workouts")
        response.status_code = 401
        response.text = '{"message": "Unauthorized"}'
        response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "401", request=request, response=response
        )
    return response


def test_get_json_returns_parsed_json_on_success() -> None:
    client = MagicMock()
    client.get.return_value = _make_response({"workouts": []})
    result = get_json(client, "/v1/workouts", params={"page": 1})
    assert result == {"workouts": []}
    client.get.assert_called_once_with("/v1/workouts", params={"page": 1})


def test_get_json_raises_runtime_error_on_http_status_error() -> None:
    client = MagicMock()
    client.get.return_value = _make_response(None, status_ok=False)
    with pytest.raises(RuntimeError, match="401"):
        get_json(client, "/v1/workouts")


def test_get_json_raises_runtime_error_on_request_error() -> None:
    client = MagicMock()
    client.get.side_effect = httpx.ConnectError("connection refused")
    with pytest.raises(RuntimeError, match="Hevy API request failed"):
        get_json(client, "/v1/workouts")
