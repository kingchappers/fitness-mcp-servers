import json
from datetime import date
from unittest.mock import MagicMock

import pytest

from mcp_myfitnesspal.tools.body import DISPATCH, TOOLS


def make_client(measurements: dict) -> MagicMock:
    client = MagicMock()
    client.get_measurements.return_value = measurements
    return client


def test_get_weight_log_calls_get_measurements() -> None:
    client = make_client({date(2026, 2, 25): 82.5})
    DISPATCH["get_weight_log"](client, {"start_date": "2026-02-20", "end_date": "2026-02-25"})
    client.get_measurements.assert_called_once_with(
        "Weight",
        date(2026, 2, 20),
        date(2026, 2, 25),
    )


def test_get_weight_log_returns_list_of_entries() -> None:
    client = make_client({date(2026, 2, 25): 82.5, date(2026, 2, 24): 82.8})
    result = DISPATCH["get_weight_log"](
        client, {"start_date": "2026-02-24", "end_date": "2026-02-25"}
    )
    data = json.loads(result[0].text)
    assert len(data) == 2
    weights = {row["date"]: row["weight"] for row in data}
    assert weights["2026-02-25"] == 82.5
    assert weights["2026-02-24"] == 82.8


def test_get_weight_log_returns_empty_list_when_no_data() -> None:
    client = make_client({})
    result = DISPATCH["get_weight_log"](
        client, {"start_date": "2026-02-20", "end_date": "2026-02-25"}
    )
    data = json.loads(result[0].text)
    assert data == []


def test_get_weight_log_rejects_bad_start_date() -> None:
    client = MagicMock()
    with pytest.raises(ValueError, match="start_date"):
        DISPATCH["get_weight_log"](client, {"start_date": "bad", "end_date": "2026-02-25"})


def test_get_weight_log_rejects_bad_end_date() -> None:
    client = MagicMock()
    with pytest.raises(ValueError, match="end_date"):
        DISPATCH["get_weight_log"](client, {"start_date": "2026-02-01", "end_date": "bad"})


def test_tools_list_contains_get_weight_log() -> None:
    names = {t.name for t in TOOLS}
    assert "get_weight_log" in names
