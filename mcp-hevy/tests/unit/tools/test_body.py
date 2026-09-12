import json
from unittest.mock import MagicMock

from mcp_hevy.tools.body import DISPATCH, TOOLS


def make_client(payload: object) -> MagicMock:
    client = MagicMock()
    response = MagicMock()
    response.json.return_value = payload
    response.raise_for_status.return_value = None
    client.get.return_value = response
    return client


def test_get_body_measurements_calls_correct_endpoint_with_defaults() -> None:
    client = make_client({"body_measurements": []})
    DISPATCH["get_body_measurements"](client, {})
    client.get.assert_called_once_with(
        "/v1/body_measurements", params={"page": 1, "pageSize": 5}
    )


def test_get_body_measurements_uses_provided_page() -> None:
    client = make_client({"body_measurements": []})
    DISPATCH["get_body_measurements"](client, {"page": 2, "page_size": 8})
    client.get.assert_called_once_with(
        "/v1/body_measurements", params={"page": 2, "pageSize": 8}
    )


def test_get_body_measurements_returns_json_payload() -> None:
    client = make_client({"body_measurements": [{"waist": 80}]})
    result = DISPATCH["get_body_measurements"](client, {})
    assert json.loads(result[0].text) == {"body_measurements": [{"waist": 80}]}


def test_tools_list_contains_get_body_measurements() -> None:
    names = {t.name for t in TOOLS}
    assert names == {"get_body_measurements"}
