import json
from unittest.mock import MagicMock

import pytest

from mcp_garmin.tools.health import DISPATCH, TOOLS

EXPECTED_TOOLS = {
    "get_hrv",
    "get_stress",
    "get_training_readiness",
    "get_max_metrics",
    "get_training_status",
    "get_respiration",
    "get_spo2",
}

METHOD_MAP = {
    "get_hrv": "get_hrv_data",
    "get_stress": "get_stress_data",
    "get_training_readiness": "get_training_readiness",
    "get_max_metrics": "get_max_metrics",
    "get_training_status": "get_training_status",
    "get_respiration": "get_respiration_data",
    "get_spo2": "get_spo2_data",
}


def test_tools_list_contains_all_seven() -> None:
    names = {t.name for t in TOOLS}
    assert names == EXPECTED_TOOLS


@pytest.mark.parametrize("tool_name,method_name", METHOD_MAP.items())
def test_tool_calls_correct_method(tool_name: str, method_name: str) -> None:
    client = MagicMock()
    getattr(client, method_name).return_value = {"value": 42}
    DISPATCH[tool_name](client, {"date": "2026-02-20"})
    getattr(client, method_name).assert_called_once_with("2026-02-20")


@pytest.mark.parametrize("tool_name,method_name", METHOD_MAP.items())
def test_tool_returns_json(tool_name: str, method_name: str) -> None:
    client = MagicMock()
    getattr(client, method_name).return_value = {"value": 42}
    result = DISPATCH[tool_name](client, {"date": "2026-02-20"})
    data = json.loads(result[0].text)
    assert data["value"] == 42


@pytest.mark.parametrize("tool_name", EXPECTED_TOOLS)
def test_tool_rejects_bad_date(tool_name: str) -> None:
    client = MagicMock()
    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        DISPATCH[tool_name](client, {"date": "not-valid"})
