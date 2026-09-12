from mcp_hevy.tools import ALL_TOOLS, DISPATCH


def test_all_tools_have_matching_dispatch_entries() -> None:
    tool_names = {t.name for t in ALL_TOOLS}
    assert tool_names == set(DISPATCH.keys())


def test_no_duplicate_tool_names() -> None:
    names = [t.name for t in ALL_TOOLS]
    assert len(names) == len(set(names))


def test_expected_tool_count() -> None:
    assert len(ALL_TOOLS) == 11
