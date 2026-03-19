from __future__ import annotations

from collections.abc import Callable
from typing import Any

from garminconnect import Garmin  # type: ignore[import-untyped]
from mcp.types import TextContent, Tool

from mcp_garmin.tools._shared import _date_range_tool, _json_result
from mcp_garmin.validation import validate_date


def get_activities(client: Garmin, arguments: dict[str, str]) -> list[TextContent]:
    validate_date(arguments["start_date"], param_name="start_date")
    validate_date(arguments["end_date"], param_name="end_date")
    return _json_result(
        client.get_activities_by_date(arguments["start_date"], arguments["end_date"])
    )


_ACTIVITY_DETAIL_TIMESERIES_KEYS = frozenset(
    [
        "activityDetailMetrics",
        "geoPolylineDTO",
        "heartRateDTO",
        "metricDescriptors",
    ]
)


def _summarize_activity_details(data: Any) -> Any:
    """Strip per-sample time-series arrays from activity details.

    Removed keys:
    - activityDetailMetrics: per-second metrics array (speed, power, cadence, etc.)
    - geoPolylineDTO: per-point GPS coordinates
    - heartRateDTO: per-second HR values
    - metricDescriptors: index→key mapping for activityDetailMetrics (useless without the data)

    Retained: summary stats, laps, splits, HR zone breakdowns.
    Verify key names against a real API response and adjust if needed.
    """
    if not isinstance(data, dict):
        return data
    return {k: v for k, v in data.items() if k not in _ACTIVITY_DETAIL_TIMESERIES_KEYS}


def get_activity_details(client: Garmin, arguments: dict[str, str]) -> list[TextContent]:
    activity_id = arguments.get("activity_id", "")
    if not activity_id:
        raise ValueError("activity_id is required and must not be empty.")
    return _json_result(_summarize_activity_details(client.get_activity_details(activity_id)))


TOOLS: list[Tool] = [
    _date_range_tool(
        "get_activities",
        "Workouts in a date range with type, duration, heart rate, distance, and pace.",
    ),
    Tool(
        name="get_activity_details",
        description="Splits, laps, and HR zones for one activity. Use get_activities for IDs.",
        inputSchema={
            "type": "object",
            "properties": {
                "activity_id": {"type": "string", "description": "Activity ID from get_activities"},
            },
            "required": ["activity_id"],
        },
    ),
]

DISPATCH: dict[str, Callable[[Garmin, dict[str, str]], list[TextContent]]] = {
    "get_activities": get_activities,
    "get_activity_details": get_activity_details,
}
