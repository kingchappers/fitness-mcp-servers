from __future__ import annotations

import http.cookiejar
import logging
import os
from pathlib import Path

import myfitnesspal  # type: ignore[import-untyped]

logger = logging.getLogger(__name__)

_client: myfitnesspal.Client | None = None


def get_client() -> myfitnesspal.Client:
    """Return the authenticated MFP singleton, creating it on first call."""
    global _client
    if _client is None:
        _client = _create_client()
    return _client


def _reset_client() -> None:
    """Reset the singleton. Used in tests only."""
    global _client
    _client = None


def _create_client() -> myfitnesspal.Client:
    cookie_path_str = os.environ.get("MFP_COOKIE_PATH")
    if not cookie_path_str:
        raise RuntimeError(
            "MFP_COOKIE_PATH is not set. "
            "Run scripts/login.py to generate a cookie file, then set MFP_COOKIE_PATH."
        )

    cookie_path = Path(cookie_path_str)
    if not cookie_path.exists():
        raise RuntimeError(
            f"Cookie file not found at {cookie_path}. Run scripts/login.py to generate it."
        )

    file_mode = cookie_path.stat().st_mode & 0o777
    if file_mode & 0o077:
        raise RuntimeError(
            f"Cookie file {cookie_path} has insecure permissions ({oct(file_mode)}). "
            f"Run: chmod 600 {cookie_path}"
        )

    jar = http.cookiejar.MozillaCookieJar()
    jar.load(str(cookie_path), ignore_discard=True, ignore_expires=True)

    logger.info("MFP client authenticated from cookie file at %s", cookie_path)
    return myfitnesspal.Client(cookiejar=jar)
