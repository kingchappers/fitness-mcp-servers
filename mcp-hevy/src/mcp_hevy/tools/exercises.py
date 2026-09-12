from __future__ import annotations

from collections.abc import Callable
from typing import Any

import httpx
from mcp.types import TextContent, Tool

from mcp_hevy.client import get_json
from mcp_hevy.tools._shared import _id_tool, _json_result, _paginated_tool, _url_encode_id
from mcp_hevy.validation import validate_non_empty_str, validate_positive_int


def get_exercise_templates(client: httpx.Client, arguments: dict[str, Any]) -> list[TextContent]:
    page = validate_positive_int(arguments.get("page"), "page", default=1)
    page_size = validate_positive_int(
        arguments.get("page_size"), "page_size", default=5, maximum=10
    )
    data = get_json(client, "/v1/exercise_templates", params={"page": page, "pageSize": page_size})
    return _json_result(data)


def get_exercise_template(client: httpx.Client, arguments: dict[str, Any]) -> list[TextContent]:
    template_id = validate_non_empty_str(
        arguments.get("exercise_template_id"), "exercise_template_id"
    )
    return _json_result(get_json(client, f"/v1/exercise_templates/{_url_encode_id(template_id)}"))


def get_exercise_history(client: httpx.Client, arguments: dict[str, Any]) -> list[TextContent]:
    template_id = validate_non_empty_str(
        arguments.get("exercise_template_id"), "exercise_template_id"
    )
    return _json_result(get_json(client, f"/v1/exercise_history/{_url_encode_id(template_id)}"))


TOOLS: list[Tool] = [
    _paginated_tool(
        "get_exercise_templates", "Paginated list of exercise templates available on the account."
    ),
    _id_tool(
        "get_exercise_template",
        "Details for one exercise template (muscle group, equipment). "
        "Use get_exercise_templates for IDs.",
        "exercise_template_id",
        "Exercise template ID from get_exercise_templates",
    ),
    _id_tool(
        "get_exercise_history",
        "Historical performance for one exercise across all logged workouts.",
        "exercise_template_id",
        "Exercise template ID from get_exercise_templates",
    ),
]

DISPATCH: dict[str, Callable[[httpx.Client, dict[str, Any]], list[TextContent]]] = {
    "get_exercise_templates": get_exercise_templates,
    "get_exercise_template": get_exercise_template,
    "get_exercise_history": get_exercise_history,
}
