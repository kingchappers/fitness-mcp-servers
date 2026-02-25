from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

from garminconnect import Garmin  # type: ignore[import-untyped]
from mcp.types import TextContent, Tool

from mcp_garmin.validation import validate_date


def _json_result(data: Any) -> list[TextContent]:
    return [TextContent(type="text", text=json.dumps(data, indent=2))]


def get_daily_stats(client: Garmin, arguments: dict[str, str]) -> list[TextContent]:
    validate_date(arguments["date"])
    return _json_result(client.get_stats(arguments["date"]))


def get_heart_rate(client: Garmin, arguments: dict[str, str]) -> list[TextContent]:
    validate_date(arguments["date"])
    return _json_result(client.get_heart_rates(arguments["date"]))


_SLEEP_TIMESERIES_KEYS = frozenset(
    [
        "sleepMovement",
        "sleepHeartRate",
        "sleepBodyBattery",
        "sleepStress",
        "sleepRestlessMoments",
        "hrvData",
        "wellnessEpochRespirationDataDTOList",
        "wellnessEpochSPO2DataDTOList",
    ]
)


def _summarize_sleep(data: Any) -> Any:
    """Strip per-epoch time-series arrays that balloon the response to 200k+.

    Summary statistics for all dropped arrays are already present in
    ``dailySleepDTO`` or as top-level scalar fields (e.g. ``avgOvernightHrv``,
    ``restingHeartRate``, ``bodyBatteryChange``).  ``sleepLevels`` (sleep-stage
    transitions, ~24 items) is retained as it provides useful timeline context.
    """
    if not isinstance(data, dict):
        return data
    return {k: v for k, v in data.items() if k not in _SLEEP_TIMESERIES_KEYS}


def get_sleep(client: Garmin, arguments: dict[str, str]) -> list[TextContent]:
    validate_date(arguments["date"])
    return _json_result(_summarize_sleep(client.get_sleep_data(arguments["date"])))


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


TOOLS: list[Tool] = [
    _date_tool(
        "get_daily_stats", "Daily activity stats: steps, calories burned, stress, active minutes."
    ),
    _date_tool(
        "get_heart_rate", "Heart rate data for the day including resting HR and HR time series."
    ),
    _date_tool(
        "get_sleep", "Sleep data: duration, stages (deep/light/REM/awake), and sleep score."
    ),
]

DISPATCH: dict[str, Callable[[Garmin, dict[str, str]], list[TextContent]]] = {
    "get_daily_stats": get_daily_stats,
    "get_heart_rate": get_heart_rate,
    "get_sleep": get_sleep,
}
