import json
from unittest.mock import MagicMock

import pytest

from mcp_garmin.tools.goals import DISPATCH, TOOLS

EXPECTED_TOOLS = {"get_endurance_score", "get_race_predictions"}
METHOD_MAP = {
    "get_endurance_score": "get_endurance_score",
    "get_race_predictions": "get_race_predictions",
}


def test_tools_list_contains_both() -> None:
    assert {t.name for t in TOOLS} == EXPECTED_TOOLS


@pytest.mark.parametrize("tool_name,method_name", METHOD_MAP.items())
def test_tool_calls_correct_method(tool_name: str, method_name: str) -> None:
    client = MagicMock()
    getattr(client, method_name).return_value = {}
    DISPATCH[tool_name](client, {"start_date": "2026-02-01", "end_date": "2026-02-20"})
    getattr(client, method_name).assert_called_once_with("2026-02-01", "2026-02-20")


@pytest.mark.parametrize("tool_name", EXPECTED_TOOLS)
def test_tool_returns_json(tool_name: str) -> None:
    client = MagicMock()
    getattr(client, METHOD_MAP[tool_name]).return_value = {"score": 80}
    result = DISPATCH[tool_name](client, {"start_date": "2026-02-01", "end_date": "2026-02-20"})
    data = json.loads(result[0].text)
    assert data["score"] == 80


@pytest.mark.parametrize("tool_name", EXPECTED_TOOLS)
def test_tool_rejects_bad_start_date(tool_name: str) -> None:
    client = MagicMock()
    with pytest.raises(ValueError, match="start_date"):
        DISPATCH[tool_name](client, {"start_date": "bad", "end_date": "2026-02-20"})


@pytest.mark.parametrize("tool_name", EXPECTED_TOOLS)
def test_tool_rejects_bad_end_date(tool_name: str) -> None:
    client = MagicMock()
    with pytest.raises(ValueError, match="end_date"):
        DISPATCH[tool_name](client, {"start_date": "2026-02-01", "end_date": "bad"})
