import json
from unittest.mock import MagicMock

import pytest

from mcp_garmin.tools.activities import DISPATCH, TOOLS


def test_get_activities_calls_correct_method() -> None:
    client = MagicMock()
    client.get_activities_by_date.return_value = []
    DISPATCH["get_activities"](client, {"start_date": "2026-02-01", "end_date": "2026-02-20"})
    client.get_activities_by_date.assert_called_once_with("2026-02-01", "2026-02-20")


def test_get_activities_returns_json() -> None:
    client = MagicMock()
    client.get_activities_by_date.return_value = [{"activityId": 123, "activityType": "running"}]
    result = DISPATCH["get_activities"](
        client, {"start_date": "2026-02-01", "end_date": "2026-02-20"}
    )
    data = json.loads(result[0].text)
    assert data[0]["activityId"] == 123


def test_get_activities_rejects_bad_start_date() -> None:
    client = MagicMock()
    with pytest.raises(ValueError, match="start_date"):
        DISPATCH["get_activities"](client, {"start_date": "bad", "end_date": "2026-02-20"})


def test_get_activities_rejects_bad_end_date() -> None:
    client = MagicMock()
    with pytest.raises(ValueError, match="end_date"):
        DISPATCH["get_activities"](client, {"start_date": "2026-02-01", "end_date": "bad"})


def test_tools_list_contains_get_activities() -> None:
    names = {t.name for t in TOOLS}
    assert "get_activities" in names


# --- get_activity_details ---


def test_get_activity_details_calls_correct_method() -> None:
    client = MagicMock()
    client.get_activity_details.return_value = {"activityId": 999}
    DISPATCH["get_activity_details"](client, {"activity_id": "999"})
    client.get_activity_details.assert_called_once_with("999")


def test_get_activity_details_returns_json() -> None:
    client = MagicMock()
    client.get_activity_details.return_value = {"activityId": 999, "distance": 5000.0}
    result = DISPATCH["get_activity_details"](client, {"activity_id": "999"})
    data = json.loads(result[0].text)
    assert data["activityId"] == 999


def test_get_activity_details_strips_timeseries() -> None:
    raw = {
        "activityId": 999,
        "distance": 5000.0,
        "activityDetailMetrics": [{"metrics": [1, 2, 3]}] * 3600,
        "geoPolylineDTO": {"polyline": [[0.0, 0.0]] * 3600},
        "heartRateDTO": {"heartRateValues": [[0, 120]] * 3600},
        "metricDescriptors": [{"metricsIndex": 0, "key": "directSpeed"}] * 50,
    }
    client = MagicMock()
    client.get_activity_details.return_value = raw
    result = DISPATCH["get_activity_details"](client, {"activity_id": "999"})
    data = json.loads(result[0].text)

    for key in ("activityDetailMetrics", "geoPolylineDTO", "heartRateDTO", "metricDescriptors"):
        assert key not in data, f"Expected {key!r} to be stripped"

    assert data["activityId"] == 999
    assert data["distance"] == 5000.0


def test_tools_list_contains_both_activity_tools() -> None:
    names = {t.name for t in TOOLS}
    assert "get_activities" in names
    assert "get_activity_details" in names
