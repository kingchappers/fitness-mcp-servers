from __future__ import annotations

import json
from typing import Any
from urllib.parse import quote as _quote

from mcp.types import TextContent, Tool


def _json_result(data: Any) -> list[TextContent]:
    return [TextContent(type="text", text=json.dumps(data, indent=2))]


def _paginated_tool(name: str, description: str) -> Tool:
    return Tool(
        name=name,
        description=description,
        inputSchema={
            "type": "object",
            "properties": {
                "page": {"type": "integer", "description": "Page number (default 1)"},
                "page_size": {
                    "type": "integer",
                    "description": "Results per page (default 5, max 10)",
                },
            },
        },
    )


def _id_tool(name: str, description: str, id_param: str, id_description: str) -> Tool:
    return Tool(
        name=name,
        description=description,
        inputSchema={
            "type": "object",
            "properties": {
                id_param: {"type": "string", "description": id_description},
            },
            "required": [id_param],
        },
    )


def _url_encode_id(value: str) -> str:
    return _quote(value, safe="")
