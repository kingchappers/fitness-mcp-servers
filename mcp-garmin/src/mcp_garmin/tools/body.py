from __future__ import annotations

from collections.abc import Callable

from garminconnect import Garmin  # type: ignore[import-untyped]
from mcp.types import TextContent, Tool

from mcp_garmin.tools._shared import _date_range_tool, _json_result
from mcp_garmin.validation import validate_date


def _range_handler(
    method_name: str,
) -> Callable[[Garmin, dict[str, str]], list[TextContent]]:
    def handler(client: Garmin, arguments: dict[str, str]) -> list[TextContent]:
        validate_date(arguments["start_date"], param_name="start_date")
        validate_date(arguments["end_date"], param_name="end_date")
        return _json_result(
            getattr(client, method_name)(arguments["start_date"], arguments["end_date"])
        )

    return handler


TOOLS: list[Tool] = [
    _date_range_tool(
        "get_body_composition", "Body composition over a date range: weight, body fat %, BMI."
    ),
    _date_range_tool("get_weigh_ins", "Weight log entries over a date range."),
]

DISPATCH: dict[str, Callable[[Garmin, dict[str, str]], list[TextContent]]] = {
    "get_body_composition": _range_handler("get_body_composition"),
    "get_weigh_ins": _range_handler("get_weigh_ins"),
}
