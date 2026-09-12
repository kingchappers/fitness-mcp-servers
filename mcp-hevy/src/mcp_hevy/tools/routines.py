from __future__ import annotations

from collections.abc import Callable
from typing import Any

import httpx
from mcp.types import TextContent, Tool

from mcp_hevy.client import get_json
from mcp_hevy.tools._shared import _id_tool, _json_result, _paginated_tool
from mcp_hevy.validation import validate_non_empty_str, validate_positive_int


def get_routines(client: httpx.Client, arguments: dict[str, Any]) -> list[TextContent]:
    page = validate_positive_int(arguments.get("page"), "page", default=1)
    page_size = validate_positive_int(arguments.get("page_size"), "page_size", default=5)
    data = get_json(client, "/v1/routines", params={"page": page, "pageSize": page_size})
    return _json_result(data)


def get_routine(client: httpx.Client, arguments: dict[str, Any]) -> list[TextContent]:
    routine_id = arguments.get("routine_id", "")
    validate_non_empty_str(routine_id, "routine_id")
    return _json_result(get_json(client, f"/v1/routines/{routine_id}"))


def get_routine_folders(client: httpx.Client, arguments: dict[str, Any]) -> list[TextContent]:
    page = validate_positive_int(arguments.get("page"), "page", default=1)
    page_size = validate_positive_int(arguments.get("page_size"), "page_size", default=5)
    data = get_json(client, "/v1/routine_folders", params={"page": page, "pageSize": page_size})
    return _json_result(data)


TOOLS: list[Tool] = [
    _paginated_tool("get_routines", "Paginated list of saved workout routines."),
    _id_tool(
        "get_routine",
        "Full details for one routine: exercises, target sets/reps. Use get_routines for IDs.",
        "routine_id",
        "Routine ID from get_routines",
    ),
    _paginated_tool("get_routine_folders", "Paginated list of folders used to organize routines."),
]

DISPATCH: dict[str, Callable[[httpx.Client, dict[str, Any]], list[TextContent]]] = {
    "get_routines": get_routines,
    "get_routine": get_routine,
    "get_routine_folders": get_routine_folders,
}
