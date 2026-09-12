from unittest.mock import MagicMock, patch

import pytest
from mcp.types import TextContent

import mcp_hevy.server as server_module


@pytest.fixture(autouse=True)
def reset_client() -> None:
    import mcp_hevy.client as client_module

    client_module._client = None


async def test_list_tools_returns_all_tools() -> None:
    result = await server_module.list_tools()
    from mcp_hevy import tools

    assert len(result) == len(tools.ALL_TOOLS)


async def test_call_tool_dispatches_correctly() -> None:
    mock_client = MagicMock()
    response = MagicMock()
    response.json.return_value = {"workouts": []}
    response.raise_for_status.return_value = None
    mock_client.get.return_value = response

    with patch("mcp_hevy.server.get_client", return_value=mock_client):
        result = await server_module.call_tool("get_workouts", {})

    assert isinstance(result[0], TextContent)
    assert "workouts" in result[0].text


async def test_call_tool_returns_error_for_unknown_tool() -> None:
    mock_client = MagicMock()
    with patch("mcp_hevy.server.get_client", return_value=mock_client):
        result = await server_module.call_tool("nonexistent_tool", {})
    assert "Unknown tool" in result[0].text


async def test_call_tool_returns_error_on_auth_failure() -> None:
    with patch(
        "mcp_hevy.server.get_client", side_effect=RuntimeError("HEVY_API_KEY not set")
    ):
        result = await server_module.call_tool("get_workouts", {})
    assert "HEVY_API_KEY" in result[0].text


async def test_call_tool_returns_error_on_validation_failure() -> None:
    mock_client = MagicMock()
    with patch("mcp_hevy.server.get_client", return_value=mock_client):
        result = await server_module.call_tool("get_workouts", {"page": 0})
    assert "Invalid" in result[0].text
