import json
from unittest.mock import MagicMock

import pytest

from mcp_garmin.tools.daily import DISPATCH, TOOLS


def make_client(**kwargs: object) -> MagicMock:
    client = MagicMock()
    for method, return_value in kwargs.items():
        getattr(client, method).return_value = return_value
    return client


# --- get_daily_stats ---


def test_get_daily_stats_calls_get_stats() -> None:
    client = make_client(get_stats={"totalSteps": 8000})
    DISPATCH["get_daily_stats"](client, {"date": "2026-02-20"})
    client.get_stats.assert_called_once_with("2026-02-20")


def test_get_daily_stats_returns_json() -> None:
    client = make_client(get_stats={"totalSteps": 8000})
    result = DISPATCH["get_daily_stats"](client, {"date": "2026-02-20"})
    data = json.loads(result[0].text)
    assert data["totalSteps"] == 8000


def test_get_daily_stats_rejects_bad_date() -> None:
    client = MagicMock()
    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        DISPATCH["get_daily_stats"](client, {"date": "bad"})


# --- get_heart_rate ---


def test_get_heart_rate_calls_get_heart_rates() -> None:
    client = make_client(get_heart_rates={"restingHeartRate": 55})
    DISPATCH["get_heart_rate"](client, {"date": "2026-02-20"})
    client.get_heart_rates.assert_called_once_with("2026-02-20")


def test_get_heart_rate_returns_json() -> None:
    client = make_client(get_heart_rates={"restingHeartRate": 55})
    result = DISPATCH["get_heart_rate"](client, {"date": "2026-02-20"})
    data = json.loads(result[0].text)
    assert data["restingHeartRate"] == 55


def test_get_heart_rate_rejects_bad_date() -> None:
    client = MagicMock()
    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        DISPATCH["get_heart_rate"](client, {"date": "not-a-date"})


# --- get_sleep ---


def test_get_sleep_calls_get_sleep_data() -> None:
    client = make_client(get_sleep_data={"sleepTimeSeconds": 28800})
    DISPATCH["get_sleep"](client, {"date": "2026-02-20"})
    client.get_sleep_data.assert_called_once_with("2026-02-20")


def test_get_sleep_returns_json() -> None:
    client = make_client(get_sleep_data={"sleepTimeSeconds": 28800})
    result = DISPATCH["get_sleep"](client, {"date": "2026-02-20"})
    data = json.loads(result[0].text)
    assert data["sleepTimeSeconds"] == 28800


def test_get_sleep_strips_timeseries_arrays() -> None:
    raw = {
        "dailySleepDTO": {"sleepTimeSeconds": 28800},
        "avgOvernightHrv": 45,
        "sleepMovement": [{"startGMT": "2026-02-23T00:00:00", "activityLevel": 0.1}] * 548,
        "sleepHeartRate": [[1771804800000, 54]] * 215,
        "sleepBodyBattery": [[1771804800000, 80]] * 143,
        "sleepStress": [[1771804800000, 10]] * 143,
        "sleepRestlessMoments": [{"startGMT": "2026-02-23T01:00:00"}] * 19,
        "hrvData": [{"startTimestampGMT": "2026-02-23T00:00:00"}] * 86,
        "wellnessEpochRespirationDataDTOList": [{"startGMT": "2026-02-23T00:00:00"}] * 215,
        "wellnessEpochSPO2DataDTOList": [{"startGMT": "2026-02-23T00:00:00"}] * 417,
        "sleepLevels": [{"startGMT": "2026-02-23T00:00:00", "activityLevel": 0}] * 24,
    }
    client = make_client(get_sleep_data=raw)
    result = DISPATCH["get_sleep"](client, {"date": "2026-02-20"})
    data = json.loads(result[0].text)

    stripped_keys = {
        "sleepMovement",
        "sleepHeartRate",
        "sleepBodyBattery",
        "sleepStress",
        "sleepRestlessMoments",
        "hrvData",
        "wellnessEpochRespirationDataDTOList",
        "wellnessEpochSPO2DataDTOList",
    }
    for key in stripped_keys:
        assert key not in data, f"Expected {key!r} to be stripped"

    assert data["dailySleepDTO"] == {"sleepTimeSeconds": 28800}
    assert data["avgOvernightHrv"] == 45
    assert data["sleepLevels"] == raw["sleepLevels"]


def test_get_sleep_rejects_bad_date() -> None:
    client = MagicMock()
    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        DISPATCH["get_sleep"](client, {"date": "2026/02/20"})


# --- TOOLS list ---


def test_tools_list_contains_all_three() -> None:
    names = {t.name for t in TOOLS}
    assert names == {"get_daily_stats", "get_heart_rate", "get_sleep"}
