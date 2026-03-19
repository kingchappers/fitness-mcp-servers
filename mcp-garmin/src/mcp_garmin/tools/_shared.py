from __future__ import annotations

import json
from typing import Any

from mcp.types import TextContent, Tool


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
