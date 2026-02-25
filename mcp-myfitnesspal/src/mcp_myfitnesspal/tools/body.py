from __future__ import annotations

import json
from collections.abc import Callable
from datetime import date
from typing import Any

import myfitnesspal  # type: ignore[import-untyped]
from mcp.types import TextContent, Tool

from mcp_myfitnesspal.validation import validate_date_range


def _json_result(data: Any) -> list[TextContent]:
    return [TextContent(type="text", text=json.dumps(data, indent=2))]


def get_weight_log(
    client: myfitnesspal.Client, arguments: dict[str, str]
) -> list[TextContent]:
    start_str = arguments["start_date"]
    end_str = arguments["end_date"]
    validate_date_range(start_str, end_str)
    measurements = client.get_measurements(
        "Weight",
        date.fromisoformat(start_str),
        date.fromisoformat(end_str),
    )
    entries = [{"date": str(d), "weight": w} for d, w in sorted(measurements.items())]
    return _json_result(entries)


TOOLS: list[Tool] = [
    Tool(
        name="get_weight_log",
        description="Weight log entries over a date range.",
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
    ),
]

DISPATCH: dict[str, Callable[[myfitnesspal.Client, dict[str, str]], list[TextContent]]] = {
    "get_weight_log": get_weight_log,
}
