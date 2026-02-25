from __future__ import annotations

import json
from collections.abc import Callable
from datetime import date, timedelta
from typing import Any

import myfitnesspal  # type: ignore[import-untyped]
from mcp.types import TextContent, Tool

from mcp_myfitnesspal.exceptions import validate_day_shape
from mcp_myfitnesspal.validation import validate_date, validate_date_range


def _json_result(data: Any) -> list[TextContent]:
    return [TextContent(type="text", text=json.dumps(data, indent=2))]


def _serialise_day(day: Any, date_str: str) -> dict[str, Any]:
    validate_day_shape(day, date_str)
    return {
        "date": date_str,
        "meals": day.get_as_dict(),
        "totals": day.totals,
        "goals": day.goals,
        "water": day.water,
        "complete": day.complete,
    }


def get_nutrition_diary(
    client: myfitnesspal.Client, arguments: dict[str, str]
) -> list[TextContent]:
    date_str = arguments["date"]
    validate_date(date_str)
    day = client.get_date(date.fromisoformat(date_str))
    return _json_result(_serialise_day(day, date_str))


def get_nutrition_summary(
    client: myfitnesspal.Client, arguments: dict[str, str]
) -> list[TextContent]:
    start_str = arguments["start_date"]
    end_str = arguments["end_date"]
    validate_date_range(start_str, end_str)
    current = date.fromisoformat(start_str)
    end = date.fromisoformat(end_str)
    rows = []
    while current <= end:
        day = client.get_date(current)
        validate_day_shape(day, str(current))
        rows.append({"date": str(current), "totals": day.totals})
        current += timedelta(days=1)
    return _json_result(rows)


def _date_tool(name: str, description: str) -> Tool:
    return Tool(
        name=name,
        description=description,
        inputSchema={
            "type": "object",
            "properties": {
                "date": {"type": "string", "description": "Date in YYYY-MM-DD format"},
            },
            "required": ["date"],
        },
    )


def _date_range_tool(name: str, description: str) -> Tool:
    return Tool(
        name=name,
        description=description,
        inputSchema={
            "type": "object",
            "properties": {
                "start_date": {
                    "type": "string",
                    "description": "Start date in YYYY-MM-DD format",
                },
                "end_date": {"type": "string", "description": "End date in YYYY-MM-DD format"},
            },
            "required": ["start_date", "end_date"],
        },
    )


TOOLS: list[Tool] = [
    _date_tool(
        "get_nutrition_diary",
        "Full diary for a single day: meals, foods, calories, macros, and daily totals vs goals.",
    ),
    _date_range_tool(
        "get_nutrition_summary",
        "Aggregated daily nutrition totals over a date range. One row per day.",
    ),
]

DISPATCH: dict[str, Callable[[myfitnesspal.Client, dict[str, str]], list[TextContent]]] = {
    "get_nutrition_diary": get_nutrition_diary,
    "get_nutrition_summary": get_nutrition_summary,
}
