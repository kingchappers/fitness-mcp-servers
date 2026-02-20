from unittest.mock import MagicMock, patch

import pytest
from mcp.types import TextContent

import mcp_garmin.server as server_module


@pytest.fixture(autouse=True)
def reset_client() -> None:
    """Ensure client singleton is reset before each test."""
    import mcp_garmin.client as client_module

    client_module._client = None


async def test_list_tools_returns_all_tools() -> None:
    result = await server_module.list_tools()
    from mcp_garmin import tools

    assert len(result) == len(tools.ALL_TOOLS)


async def test_call_tool_dispatches_correctly() -> None:
    mock_client = MagicMock()
    mock_client.get_stats.return_value = {"totalSteps": 5000}

    with patch("mcp_garmin.server.get_client", return_value=mock_client):
        result = await server_module.call_tool("get_daily_stats", {"date": "2026-02-20"})

    assert isinstance(result[0], TextContent)
    assert "totalSteps" in result[0].text


async def test_call_tool_returns_error_for_unknown_tool() -> None:
    mock_client = MagicMock()
    with patch("mcp_garmin.server.get_client", return_value=mock_client):
        result = await server_module.call_tool("nonexistent_tool", {})
    assert "Unknown tool" in result[0].text


async def test_call_tool_returns_error_on_auth_failure() -> None:
    with patch("mcp_garmin.server.get_client", side_effect=RuntimeError("Tokens not found")):
        result = await server_module.call_tool("get_daily_stats", {"date": "2026-02-20"})
    assert "Tokens not found" in result[0].text


async def test_call_tool_returns_error_on_validation_failure() -> None:
    mock_client = MagicMock()
    with patch("mcp_garmin.server.get_client", return_value=mock_client):
        result = await server_module.call_tool("get_daily_stats", {"date": "bad-date"})
    assert "Invalid" in result[0].text
