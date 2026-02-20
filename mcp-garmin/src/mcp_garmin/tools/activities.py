from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

from garminconnect import Garmin  # type: ignore[import-untyped]
from mcp.types import TextContent, Tool

from mcp_garmin.validation import validate_date


def _json_result(data: Any) -> list[TextContent]:
    return [TextContent(type="text", text=json.dumps(data, indent=2))]


def _date_range_tool(name: str, description: str) -> Tool:
    return Tool(
        name=name,
        description=description,
        inputSchema={
            "type": "object",
            "properties": {
                "start_date": {"type": "string", "description": "Start date in YYYY-MM-DD format"},
                "end_date": {"type": "string", "description": "End date in YYYY-MM-DD format"},
            },
            "required": ["start_date", "end_date"],
        },
    )


def get_activities(client: Garmin, arguments: dict[str, str]) -> list[TextContent]:
    validate_date(arguments["start_date"], param_name="start_date")
    validate_date(arguments["end_date"], param_name="end_date")
    return _json_result(
        client.get_activities_by_date(arguments["start_date"], arguments["end_date"])
    )


TOOLS: list[Tool] = [
    _date_range_tool(
        "get_activities",
        "Workouts in a date range with type, duration, heart rate, distance, and pace.",
    ),
]

DISPATCH: dict[str, Callable[[Garmin, dict[str, str]], list[TextContent]]] = {
    "get_activities": get_activities,
}
