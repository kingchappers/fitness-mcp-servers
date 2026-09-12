import json
from unittest.mock import MagicMock

import pytest

from mcp_hevy.tools.exercises import DISPATCH, TOOLS


def make_client(payload: object) -> MagicMock:
    client = MagicMock()
    response = MagicMock()
    response.json.return_value = payload
    response.raise_for_status.return_value = None
    client.get.return_value = response
    return client


def test_get_exercise_templates_calls_correct_endpoint_with_defaults() -> None:
    client = make_client({"exercise_templates": []})
    DISPATCH["get_exercise_templates"](client, {})
    client.get.assert_called_once_with(
        "/v1/exercise_templates", params={"page": 1, "pageSize": 5}
    )


def test_get_exercise_template_requires_id() -> None:
    client = MagicMock()
    with pytest.raises(ValueError, match="exercise_template_id"):
        DISPATCH["get_exercise_template"](client, {})


def test_get_exercise_template_calls_correct_path() -> None:
    client = make_client({"id": "et1"})
    result = DISPATCH["get_exercise_template"](client, {"exercise_template_id": "et1"})
    client.get.assert_called_once_with("/v1/exercise_templates/et1", params=None)
    assert json.loads(result[0].text) == {"id": "et1"}


def test_get_exercise_template_url_encodes_template_id() -> None:
    client = make_client({"id": "abc/def"})
    DISPATCH["get_exercise_template"](client, {"exercise_template_id": "abc/def"})
    client.get.assert_called_once_with("/v1/exercise_templates/abc%2Fdef", params=None)


def test_get_exercise_history_requires_id() -> None:
    client = MagicMock()
    with pytest.raises(ValueError, match="exercise_template_id"):
        DISPATCH["get_exercise_history"](client, {})


def test_get_exercise_history_calls_correct_path() -> None:
    client = make_client({"history": []})
    result = DISPATCH["get_exercise_history"](client, {"exercise_template_id": "et1"})
    client.get.assert_called_once_with("/v1/exercise_history/et1", params=None)
    assert json.loads(result[0].text) == {"history": []}


def test_get_exercise_history_url_encodes_template_id() -> None:
    client = make_client({"history": []})
    DISPATCH["get_exercise_history"](client, {"exercise_template_id": "abc/def"})
    client.get.assert_called_once_with("/v1/exercise_history/abc%2Fdef", params=None)


def test_tools_list_contains_all_exercise_tools() -> None:
    names = {t.name for t in TOOLS}
    assert names == {
        "get_exercise_templates",
        "get_exercise_template",
        "get_exercise_history",
    }
