import json
from unittest.mock import MagicMock

import pytest

from mcp_hevy.tools.workouts import DISPATCH, TOOLS


def make_client(payload: object) -> MagicMock:
    client = MagicMock()
    response = MagicMock()
    response.json.return_value = payload
    response.raise_for_status.return_value = None
    client.get.return_value = response
    return client


def test_get_workouts_calls_correct_endpoint_with_defaults() -> None:
    client = make_client({"workouts": []})
    DISPATCH["get_workouts"](client, {})
    client.get.assert_called_once_with("/v1/workouts", params={"page": 1, "pageSize": 5})


def test_get_workouts_uses_provided_page_and_page_size() -> None:
    client = make_client({"workouts": []})
    DISPATCH["get_workouts"](client, {"page": 2, "page_size": 10})
    client.get.assert_called_once_with("/v1/workouts", params={"page": 2, "pageSize": 10})


def test_get_workouts_returns_json_payload() -> None:
    client = make_client({"workouts": [{"id": "abc"}]})
    result = DISPATCH["get_workouts"](client, {})
    assert json.loads(result[0].text) == {"workouts": [{"id": "abc"}]}


def test_get_workouts_rejects_invalid_page() -> None:
    client = MagicMock()
    with pytest.raises(ValueError, match="page"):
        DISPATCH["get_workouts"](client, {"page": 0})


def test_get_workouts_rejects_page_size_above_max() -> None:
    client = MagicMock()
    with pytest.raises(ValueError, match="page_size"):
        DISPATCH["get_workouts"](client, {"page_size": 11})


def test_get_workouts_accepts_page_size_at_max() -> None:
    client = make_client({"workouts": []})
    DISPATCH["get_workouts"](client, {"page_size": 10})
    client.get.assert_called_once_with("/v1/workouts", params={"page": 1, "pageSize": 10})


def test_get_workout_count_calls_correct_path() -> None:
    client = make_client({"workout_count": 42})
    result = DISPATCH["get_workout_count"](client, {})
    client.get.assert_called_once_with("/v1/workouts/count", params=None)
    assert json.loads(result[0].text) == {"workout_count": 42}


def test_get_workout_requires_workout_id() -> None:
    client = MagicMock()
    with pytest.raises(ValueError, match="workout_id"):
        DISPATCH["get_workout"](client, {})


def test_get_workout_calls_correct_path() -> None:
    client = make_client({"id": "abc"})
    result = DISPATCH["get_workout"](client, {"workout_id": "abc"})
    client.get.assert_called_once_with("/v1/workouts/abc", params=None)
    assert json.loads(result[0].text) == {"id": "abc"}


def test_get_workout_url_encodes_workout_id() -> None:
    client = make_client({"id": "abc/def"})
    DISPATCH["get_workout"](client, {"workout_id": "abc/def"})
    client.get.assert_called_once_with("/v1/workouts/abc%2Fdef", params=None)


def test_tools_list_contains_all_workout_tools() -> None:
    names = {t.name for t in TOOLS}
    assert names == {"get_workouts", "get_workout_count", "get_workout"}
