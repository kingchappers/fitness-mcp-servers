from __future__ import annotations

from collections.abc import Callable
from typing import Any

import httpx
from mcp.types import TextContent, Tool

from mcp_hevy.client import get_json
from mcp_hevy.tools._shared import _id_tool, _json_result, _paginated_tool, _url_encode_id
from mcp_hevy.validation import validate_non_empty_str, validate_positive_int


def get_workouts(client: httpx.Client, arguments: dict[str, Any]) -> list[TextContent]:
    page = validate_positive_int(arguments.get("page"), "page", default=1)
    page_size = validate_positive_int(arguments.get("page_size"), "page_size", default=5)
    data = get_json(client, "/v1/workouts", params={"page": page, "pageSize": page_size})
    return _json_result(data)


def get_workout_count(client: httpx.Client, arguments: dict[str, Any]) -> list[TextContent]:
    return _json_result(get_json(client, "/v1/workouts/count"))


def get_workout(client: httpx.Client, arguments: dict[str, Any]) -> list[TextContent]:
    workout_id = arguments.get("workout_id", "")
    validate_non_empty_str(workout_id, "workout_id")
    return _json_result(get_json(client, f"/v1/workouts/{_url_encode_id(workout_id)}"))


TOOLS: list[Tool] = [
    _paginated_tool("get_workouts", "Paginated list of logged workouts with exercises and sets."),
    Tool(
        name="get_workout_count",
        description="Total number of workouts logged on the account.",
        inputSchema={"type": "object", "properties": {}},
    ),
    _id_tool(
        "get_workout",
        "Full details for one workout: exercises, sets, weight, reps. Use get_workouts for IDs.",
        "workout_id",
        "Workout ID from get_workouts",
    ),
]

DISPATCH: dict[str, Callable[[httpx.Client, dict[str, Any]], list[TextContent]]] = {
    "get_workouts": get_workouts,
    "get_workout_count": get_workout_count,
    "get_workout": get_workout,
}
