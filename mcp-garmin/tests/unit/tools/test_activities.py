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
