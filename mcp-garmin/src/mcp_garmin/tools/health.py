from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

from garminconnect import Garmin  # type: ignore[import-untyped]
from mcp.types import TextContent, Tool

from mcp_garmin.validation import validate_date


def _json_result(data: Any) -> list[TextContent]:
    return [TextContent(type="text", text=json.dumps(data, indent=2))]


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


def _single_date_handler(
    method_name: str,
) -> Callable[[Garmin, dict[str, str]], list[TextContent]]:
    def handler(client: Garmin, arguments: dict[str, str]) -> list[TextContent]:
        validate_date(arguments["date"])
        return _json_result(getattr(client, method_name)(arguments["date"]))

    return handler


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


def get_menstrual_cycle(client: Garmin, arguments: dict[str, str]) -> list[TextContent]:
    validate_date(arguments["start_date"], param_name="start_date")
    validate_date(arguments["end_date"], param_name="end_date")
    return _json_result(client.get_menstrual_data(arguments["start_date"], arguments["end_date"]))


TOOLS: list[Tool] = [
    _date_tool("get_hrv", "Heart Rate Variability data for the day."),
    _date_tool("get_stress", "Detailed stress data throughout the day."),
    _date_tool("get_training_readiness", "Training readiness score and contributing factors."),
    _date_tool("get_max_metrics", "VO2 max and fitness age estimates."),
    _date_tool("get_training_status", "Current training status and load."),
    _date_tool("get_respiration", "Respiration rate data throughout the day."),
    _date_tool("get_spo2", "Blood oxygen saturation (SpO2) data throughout the day."),
    _date_range_tool(
        "get_menstrual_cycle",
        "Menstrual cycle tracking: phase, symptoms, and cycle stats.",
    ),
]

DISPATCH: dict[str, Callable[[Garmin, dict[str, str]], list[TextContent]]] = {
    "get_hrv": _single_date_handler("get_hrv_data"),
    "get_stress": _single_date_handler("get_stress_data"),
    "get_training_readiness": _single_date_handler("get_training_readiness"),
    "get_max_metrics": _single_date_handler("get_max_metrics"),
    "get_training_status": _single_date_handler("get_training_status"),
    "get_respiration": _single_date_handler("get_respiration_data"),
    "get_spo2": _single_date_handler("get_spo2_data"),
    "get_menstrual_cycle": get_menstrual_cycle,
}
