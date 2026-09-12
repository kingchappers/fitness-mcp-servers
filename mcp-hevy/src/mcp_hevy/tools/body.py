from __future__ import annotations

from collections.abc import Callable
from typing import Any

import httpx
from mcp.types import TextContent, Tool

from mcp_hevy.client import get_json
from mcp_hevy.tools._shared import _json_result, _paginated_tool
from mcp_hevy.validation import validate_positive_int


def get_body_measurements(client: httpx.Client, arguments: dict[str, Any]) -> list[TextContent]:
    page = validate_positive_int(arguments.get("page"), "page", default=1)
    page_size = validate_positive_int(
        arguments.get("page_size"), "page_size", default=5, maximum=10
    )
    data = get_json(client, "/v1/body_measurements", params={"page": page, "pageSize": page_size})
    return _json_result(data)


TOOLS: list[Tool] = [
    _paginated_tool(
        "get_body_measurements", "Paginated list of logged body measurements (weight, waist, etc.)."
    ),
]

DISPATCH: dict[str, Callable[[httpx.Client, dict[str, Any]], list[TextContent]]] = {
    "get_body_measurements": get_body_measurements,
}
