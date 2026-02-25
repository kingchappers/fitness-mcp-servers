import json
from datetime import date
from unittest.mock import MagicMock

import pytest

from mcp_myfitnesspal.exceptions import MFPShapeError
from mcp_myfitnesspal.tools.nutrition import DISPATCH, TOOLS


def make_fake_day(
    date_val: date = date(2026, 2, 25),
    totals: dict | None = None,
    goals: dict | None = None,
    water: float = 500.0,
    complete: bool = False,
) -> MagicMock:
    day = MagicMock()
    day.date = date_val
    day.totals = totals or {"calories": 2000.0, "protein": 150.0}
    day.goals = goals or {"calories": 2200.0, "protein": 160.0}
    day.water = water
    day.complete = complete
    day.get_as_dict.return_value = {
        "Breakfast": [{"name": "Oats", "nutrition_information": {"calories": 300.0}}]
    }
    return day


def make_client(day: MagicMock) -> MagicMock:
    client = MagicMock()
    client.get_date.return_value = day
    return client


# --- get_nutrition_diary ---


def test_get_nutrition_diary_calls_get_date() -> None:
    day = make_fake_day()
    client = make_client(day)
    DISPATCH["get_nutrition_diary"](client, {"date": "2026-02-25"})
    client.get_date.assert_called_once_with(date(2026, 2, 25))


def test_get_nutrition_diary_returns_meals_and_totals() -> None:
    day = make_fake_day()
    client = make_client(day)
    result = DISPATCH["get_nutrition_diary"](client, {"date": "2026-02-25"})
    data = json.loads(result[0].text)
    assert data["totals"]["calories"] == 2000.0
    assert "Breakfast" in data["meals"]
    assert data["goals"]["calories"] == 2200.0
    assert data["water"] == 500.0
    assert data["complete"] is False


def test_get_nutrition_diary_rejects_bad_date() -> None:
    client = MagicMock()
    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        DISPATCH["get_nutrition_diary"](client, {"date": "bad"})


def test_get_nutrition_diary_raises_shape_error_on_broken_response() -> None:
    client = MagicMock()
    client.get_date.return_value = object()  # missing meals/totals/goals
    with pytest.raises(MFPShapeError):
        DISPATCH["get_nutrition_diary"](client, {"date": "2026-02-25"})


# --- get_nutrition_summary ---


def test_get_nutrition_summary_returns_one_row_per_day() -> None:
    day = make_fake_day()
    client = make_client(day)
    result = DISPATCH["get_nutrition_summary"](
        client, {"start_date": "2026-02-25", "end_date": "2026-02-25"}
    )
    data = json.loads(result[0].text)
    assert len(data) == 1
    assert data[0]["date"] == "2026-02-25"
    assert data[0]["totals"]["calories"] == 2000.0


def test_get_nutrition_summary_iterates_range() -> None:
    day = make_fake_day()
    client = make_client(day)
    DISPATCH["get_nutrition_summary"](
        client, {"start_date": "2026-02-01", "end_date": "2026-02-03"}
    )
    assert client.get_date.call_count == 3


def test_get_nutrition_summary_rejects_bad_dates() -> None:
    client = MagicMock()
    with pytest.raises(ValueError, match="start_date"):
        DISPATCH["get_nutrition_summary"](client, {"start_date": "bad", "end_date": "2026-02-25"})


# --- TOOLS list ---


def test_tools_list_contains_both_tools() -> None:
    names = {t.name for t in TOOLS}
    assert names == {"get_nutrition_diary", "get_nutrition_summary"}
