from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from mcp_garmin import client as client_module


def _reset_singleton() -> None:
    """Reset module-level singleton between tests."""
    client_module._client = None


def test_get_client_loads_tokens_from_token_store(tmp_path: Path) -> None:
    _reset_singleton()
    mock_garmin = MagicMock()

    with (
        patch.object(client_module, "TOKEN_STORE", tmp_path),
        patch("mcp_garmin.client.Garmin", return_value=mock_garmin),
    ):
        tmp_path.mkdir(parents=True, exist_ok=True)
        result = client_module.get_client()

    mock_garmin.login.assert_called_once_with(str(tmp_path))
    assert result is mock_garmin


def test_get_client_returns_same_instance_on_second_call(tmp_path: Path) -> None:
    _reset_singleton()
    mock_garmin = MagicMock()

    with (
        patch.object(client_module, "TOKEN_STORE", tmp_path),
        patch("mcp_garmin.client.Garmin", return_value=mock_garmin),
    ):
        tmp_path.mkdir(parents=True, exist_ok=True)
        first = client_module.get_client()
        second = client_module.get_client()

    assert first is second


def test_get_client_raises_when_token_store_missing(tmp_path: Path) -> None:
    _reset_singleton()
    missing = tmp_path / "does_not_exist"

    with patch.object(client_module, "TOKEN_STORE", missing):
        with pytest.raises(RuntimeError, match="scripts/login.py"):
            client_module.get_client()
