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


def get_personal_records(client: Garmin, arguments: dict[str, str]) -> list[TextContent]:
    return _json_result(client.get_personal_record())


TOOLS: list[Tool] = [
    _date_range_tool("get_endurance_score", "Endurance score trend over a date range."),
    _date_range_tool(
        "get_race_predictions",
        "Predicted race finish times (5K, 10K, half marathon, marathon) over a date range.",
    ),
    Tool(
        name="get_personal_records",
        description="All-time personal records for running, cycling, and other activities.",
        inputSchema={"type": "object", "properties": {}, "required": []},
    ),
]

DISPATCH: dict[str, Callable[[Garmin, dict[str, str]], list[TextContent]]] = {
    "get_endurance_score": _range_handler("get_endurance_score"),
    "get_race_predictions": _range_handler("get_race_predictions"),
    "get_personal_records": get_personal_records,
}
