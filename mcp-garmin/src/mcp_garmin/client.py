from __future__ import annotations

import logging
from pathlib import Path

from garminconnect import Garmin  # type: ignore[import-untyped]

logger = logging.getLogger(__name__)

TOKEN_STORE = Path.home() / ".garminconnect"

_client: Garmin | None = None


def get_client() -> Garmin:
    """Return the authenticated Garmin singleton, creating it on first call."""
    global _client
    if _client is None:
        _client = _create_client()
    return _client


def _create_client() -> Garmin:
    if not TOKEN_STORE.exists():
        raise RuntimeError(
            f"Garmin tokens not found at {TOKEN_STORE}. Run scripts/login.py to authenticate."
        )
    garmin = Garmin()
    garmin.login(str(TOKEN_STORE))
    logger.info("Garmin client authenticated from token store at %s", TOKEN_STORE)
    return garmin
