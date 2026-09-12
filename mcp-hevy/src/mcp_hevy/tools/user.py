from __future__ import annotations

from collections.abc import Callable
from typing import Any

import httpx
from mcp.types import TextContent, Tool

from mcp_hevy.client import get_json
from mcp_hevy.tools._shared import _json_result


def get_user_info(client: httpx.Client, arguments: dict[str, Any]) -> list[TextContent]:
    return _json_result(get_json(client, "/v1/user/info"))


TOOLS: list[Tool] = [
    Tool(
        name="get_user_info",
        description="Basic Hevy account info for the authenticated user.",
        inputSchema={"type": "object", "properties": {}},
    ),
]

DISPATCH: dict[str, Callable[[httpx.Client, dict[str, Any]], list[TextContent]]] = {
    "get_user_info": get_user_info,
}
