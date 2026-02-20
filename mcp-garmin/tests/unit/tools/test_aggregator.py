from mcp_garmin import tools

ALL_EXPECTED = {
    "get_daily_stats",
    "get_heart_rate",
    "get_sleep",
    "get_activities",
    "get_hrv",
    "get_stress",
    "get_training_readiness",
    "get_max_metrics",
    "get_training_status",
    "get_respiration",
    "get_spo2",
    "get_body_composition",
    "get_weigh_ins",
    "get_endurance_score",
    "get_race_predictions",
    "get_hydration",
}


def test_all_tools_present() -> None:
    names = {t.name for t in tools.ALL_TOOLS}
    assert names == ALL_EXPECTED


def test_dispatch_covers_all_tools() -> None:
    assert set(tools.DISPATCH.keys()) == ALL_EXPECTED


def test_no_duplicate_tool_names() -> None:
    names = [t.name for t in tools.ALL_TOOLS]
    assert len(names) == len(set(names))
