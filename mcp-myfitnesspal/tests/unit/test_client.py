import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from mcp_myfitnesspal.client import _reset_client, get_client


def test_get_client_raises_if_env_var_not_set() -> None:
    _reset_client()
    env = {k: v for k, v in os.environ.items() if k != "MFP_COOKIE_PATH"}
    with patch.dict(os.environ, env, clear=True):
        with pytest.raises(RuntimeError, match="MFP_COOKIE_PATH"):
            get_client()


def test_get_client_raises_if_file_not_found(tmp_path: Path) -> None:
    _reset_client()
    missing = str(tmp_path / "missing.txt")
    with patch.dict(os.environ, {"MFP_COOKIE_PATH": missing}):
        with pytest.raises(RuntimeError, match="not found"):
            get_client()


def test_get_client_raises_if_permissions_too_open(tmp_path: Path) -> None:
    _reset_client()
    cookie_file = tmp_path / "cookies.txt"
    cookie_file.write_text("# Netscape HTTP Cookie File\n")
    cookie_file.chmod(0o644)
    with patch.dict(os.environ, {"MFP_COOKIE_PATH": str(cookie_file)}):
        with pytest.raises(RuntimeError, match="[Pp]ermission"):
            get_client()


def test_get_client_returns_singleton(tmp_path: Path) -> None:
    _reset_client()
    cookie_file = tmp_path / "cookies.txt"
    cookie_file.write_text("# Netscape HTTP Cookie File\n")
    cookie_file.chmod(0o600)
    with patch.dict(os.environ, {"MFP_COOKIE_PATH": str(cookie_file)}):
        with patch("mcp_myfitnesspal.client.myfitnesspal.Client") as mock_cls:
            mock_cls.return_value = MagicMock()
            c1 = get_client()
            c2 = get_client()
            assert c1 is c2
            mock_cls.assert_called_once()
