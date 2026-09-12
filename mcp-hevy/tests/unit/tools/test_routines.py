import json
from unittest.mock import MagicMock

import pytest

from mcp_hevy.tools.routines import DISPATCH, TOOLS


def make_client(payload: object) -> MagicMock:
    client = MagicMock()
    response = MagicMock()
    response.json.return_value = payload
    response.raise_for_status.return_value = None
    client.get.return_value = response
    return client


def test_get_routines_calls_correct_endpoint_with_defaults() -> None:
    client = make_client({"routines": []})
    DISPATCH["get_routines"](client, {})
    client.get.assert_called_once_with("/v1/routines", params={"page": 1, "pageSize": 5})


def test_get_routines_returns_json_payload() -> None:
    client = make_client({"routines": [{"id": "r1"}]})
    result = DISPATCH["get_routines"](client, {})
    assert json.loads(result[0].text) == {"routines": [{"id": "r1"}]}


def test_get_routine_requires_routine_id() -> None:
    client = MagicMock()
    with pytest.raises(ValueError, match="routine_id"):
        DISPATCH["get_routine"](client, {})


def test_get_routine_calls_correct_path() -> None:
    client = make_client({"id": "r1"})
    result = DISPATCH["get_routine"](client, {"routine_id": "r1"})
    client.get.assert_called_once_with("/v1/routines/r1", params=None)
    assert json.loads(result[0].text) == {"id": "r1"}


def test_get_routine_folders_calls_correct_endpoint_with_defaults() -> None:
    client = make_client({"routine_folders": []})
    DISPATCH["get_routine_folders"](client, {})
    client.get.assert_called_once_with(
        "/v1/routine_folders", params={"page": 1, "pageSize": 5}
    )


def test_get_routine_folders_uses_provided_page() -> None:
    client = make_client({"routine_folders": []})
    DISPATCH["get_routine_folders"](client, {"page": 3, "page_size": 20})
    client.get.assert_called_once_with(
        "/v1/routine_folders", params={"page": 3, "pageSize": 20}
    )


def test_tools_list_contains_all_routine_tools() -> None:
    names = {t.name for t in TOOLS}
    assert names == {"get_routines", "get_routine", "get_routine_folders"}
