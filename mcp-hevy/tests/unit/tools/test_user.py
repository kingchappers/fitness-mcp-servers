import json
from unittest.mock import MagicMock

from mcp_hevy.tools.user import DISPATCH, TOOLS


def test_get_user_info_calls_correct_path() -> None:
    client = MagicMock()
    response = MagicMock()
    response.json.return_value = {"username": "someone"}
    response.raise_for_status.return_value = None
    client.get.return_value = response

    result = DISPATCH["get_user_info"](client, {})

    client.get.assert_called_once_with("/v1/user/info", params=None)
    assert json.loads(result[0].text) == {"username": "someone"}


def test_tools_list_contains_get_user_info() -> None:
    names = {t.name for t in TOOLS}
    assert names == {"get_user_info"}
