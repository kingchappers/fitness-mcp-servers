import json
from unittest.mock import MagicMock

import pytest

from mcp_garmin.tools.wellness import DISPATCH, TOOLS


def test_tools_list_contains_get_hydration() -> None:
    assert {t.name for t in TOOLS} == {"get_hydration"}


def test_get_hydration_calls_correct_method() -> None:
    client = MagicMock()
    client.get_hydration_data.return_value = {"totalIntakeInOz": 64}
    DISPATCH["get_hydration"](client, {"date": "2026-02-20"})
    client.get_hydration_data.assert_called_once_with("2026-02-20")


def test_get_hydration_returns_json() -> None:
    client = MagicMock()
    client.get_hydration_data.return_value = {"totalIntakeInOz": 64}
    result = DISPATCH["get_hydration"](client, {"date": "2026-02-20"})
    data = json.loads(result[0].text)
    assert data["totalIntakeInOz"] == 64


def test_get_hydration_rejects_bad_date() -> None:
    client = MagicMock()
    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        DISPATCH["get_hydration"](client, {"date": "bad"})
