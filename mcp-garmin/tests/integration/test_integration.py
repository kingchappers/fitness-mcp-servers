"""Integration tests — call the real Garmin API.

Run with:
    GARMIN_INTEGRATION_TESTS=1 poetry run pytest tests/integration/ -v

Requires tokens present in ~/.garminconnect (run scripts/login.py first).
"""

from __future__ import annotations

import os

import pytest

import mcp_garmin.client as client_module
from mcp_garmin.client import get_client

TODAY = "2026-02-20"
RANGE_START = "2026-02-01"
RANGE_END = "2026-02-20"

if not os.getenv("GARMIN_INTEGRATION_TESTS"):
    pytest.skip("Set GARMIN_INTEGRATION_TESTS=1 to run", allow_module_level=True)


@pytest.fixture(autouse=True)
def reset_client() -> None:
    client_module._client = None


def test_get_daily_stats_returns_data() -> None:
    from mcp_garmin.tools.daily import DISPATCH

    client = get_client()
    result = DISPATCH["get_daily_stats"](client, {"date": TODAY})
    assert result[0].text  # non-empty response


def test_get_heart_rate_returns_data() -> None:
    from mcp_garmin.tools.daily import DISPATCH

    client = get_client()
    result = DISPATCH["get_heart_rate"](client, {"date": TODAY})
    assert result[0].text


def test_get_sleep_returns_data() -> None:
    from mcp_garmin.tools.daily import DISPATCH

    client = get_client()
    result = DISPATCH["get_sleep"](client, {"date": TODAY})
    assert result[0].text


def test_get_activities_returns_data() -> None:
    from mcp_garmin.tools.activities import DISPATCH

    client = get_client()
    result = DISPATCH["get_activities"](client, {"start_date": RANGE_START, "end_date": RANGE_END})
    assert result[0].text


def test_get_hrv_returns_data() -> None:
    from mcp_garmin.tools.health import DISPATCH

    client = get_client()
    result = DISPATCH["get_hrv"](client, {"date": TODAY})
    assert result[0].text


def test_get_body_composition_returns_data() -> None:
    from mcp_garmin.tools.body import DISPATCH

    client = get_client()
    result = DISPATCH["get_body_composition"](
        client, {"start_date": RANGE_START, "end_date": RANGE_END}
    )
    assert result[0].text


def test_get_hydration_returns_data() -> None:
    from mcp_garmin.tools.wellness import DISPATCH

    client = get_client()
    result = DISPATCH["get_hydration"](client, {"date": TODAY})
    assert result[0].text
