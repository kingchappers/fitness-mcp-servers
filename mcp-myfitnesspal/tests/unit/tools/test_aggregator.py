from mcp_myfitnesspal import tools

ALL_EXPECTED = {"get_nutrition_diary", "get_nutrition_summary", "get_weight_log"}


def test_all_tools_present() -> None:
    names = {t.name for t in tools.ALL_TOOLS}
    assert names == ALL_EXPECTED


def test_dispatch_covers_all_tools() -> None:
    assert set(tools.DISPATCH.keys()) == ALL_EXPECTED


def test_no_duplicate_tool_names() -> None:
    names = [t.name for t in tools.ALL_TOOLS]
    assert len(names) == len(set(names))
