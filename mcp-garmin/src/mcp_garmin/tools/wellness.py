from __future__ import annotations

from collections.abc import Callable

from garminconnect import Garmin  # type: ignore[import-untyped]
from mcp.types import TextContent, Tool

from mcp_garmin.tools._shared import _json_result
from mcp_garmin.validation import validate_date


def get_hydration(client: Garmin, arguments: dict[str, str]) -> list[TextContent]:
    validate_date(arguments["date"])
    return _json_result(client.get_hydration_data(arguments["date"]))


TOOLS: list[Tool] = [
    Tool(
        name="get_hydration",
        description="Hydration intake data for the day.",
        inputSchema={
            "type": "object",
            "properties": {
                "date": {"type": "string", "description": "Date in YYYY-MM-DD format"},
            },
            "required": ["date"],
        },
    ),
]

DISPATCH: dict[str, Callable[[Garmin, dict[str, str]], list[TextContent]]] = {
    "get_hydration": get_hydration,
}
