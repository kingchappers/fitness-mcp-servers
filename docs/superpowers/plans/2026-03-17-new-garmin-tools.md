# New Garmin Tools Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `get_personal_records`, `get_body_battery`, `get_activity_details`, and `get_menstrual_cycle` tools to `mcp-garmin`.

**Architecture:** Each tool is added to the most fitting existing module (`goals.py`, `daily.py`, `activities.py`, `health.py`). Tests follow the established mock-client pattern. `get_activity_details` requires a response summarizer to strip per-sample arrays.

**Tech Stack:** Python 3.12, `python-garminconnect`, `mcp` SDK, `pytest`, `poetry`

---

## Chunk 1: get_personal_records

**Files:**
- Modify: `mcp-garmin/src/mcp_garmin/tools/goals.py`
- Modify: `mcp-garmin/tests/unit/tools/test_goals.py`

### Task 1: Add get_personal_records — failing test

- [ ] **Step 1: Write the failing test**

**This is a full file replacement** — delete all existing content in `test_goals.py` and replace with the following. The existing parametrized tests for `get_endurance_score` and `get_race_predictions` are preserved under new function names; all `test_date_range_tool_*` tests should pass immediately after this step.

In `mcp-garmin/tests/unit/tools/test_goals.py`, replace the entire file content with:

```python
import json
from unittest.mock import MagicMock

import pytest

from mcp_garmin.tools.goals import DISPATCH, TOOLS

EXPECTED_TOOLS = {"get_endurance_score", "get_race_predictions", "get_personal_records"}
METHOD_MAP = {
    "get_endurance_score": "get_endurance_score",
    "get_race_predictions": "get_race_predictions",
}


def test_tools_list_contains_all() -> None:
    assert {t.name for t in TOOLS} == EXPECTED_TOOLS


@pytest.mark.parametrize("tool_name,method_name", METHOD_MAP.items())
def test_date_range_tool_calls_correct_method(tool_name: str, method_name: str) -> None:
    client = MagicMock()
    getattr(client, method_name).return_value = {}
    DISPATCH[tool_name](client, {"start_date": "2026-02-01", "end_date": "2026-02-20"})
    getattr(client, method_name).assert_called_once_with("2026-02-01", "2026-02-20")


@pytest.mark.parametrize("tool_name", METHOD_MAP)
def test_date_range_tool_returns_json(tool_name: str) -> None:
    client = MagicMock()
    getattr(client, METHOD_MAP[tool_name]).return_value = {"score": 80}
    result = DISPATCH[tool_name](client, {"start_date": "2026-02-01", "end_date": "2026-02-20"})
    data = json.loads(result[0].text)
    assert data["score"] == 80


@pytest.mark.parametrize("tool_name", METHOD_MAP)
def test_date_range_tool_rejects_bad_start_date(tool_name: str) -> None:
    client = MagicMock()
    with pytest.raises(ValueError, match="start_date"):
        DISPATCH[tool_name](client, {"start_date": "bad", "end_date": "2026-02-20"})


@pytest.mark.parametrize("tool_name", METHOD_MAP)
def test_date_range_tool_rejects_bad_end_date(tool_name: str) -> None:
    client = MagicMock()
    with pytest.raises(ValueError, match="end_date"):
        DISPATCH[tool_name](client, {"start_date": "2026-02-01", "end_date": "bad"})


# --- get_personal_records ---


def test_get_personal_records_calls_correct_method() -> None:
    client = MagicMock()
    client.get_personal_record.return_value = []
    DISPATCH["get_personal_records"](client, {})
    client.get_personal_record.assert_called_once_with()


def test_get_personal_records_returns_json() -> None:
    client = MagicMock()
    client.get_personal_record.return_value = [{"typeId": 1, "value": 1200}]
    result = DISPATCH["get_personal_records"](client, {})
    data = json.loads(result[0].text)
    assert data[0]["typeId"] == 1
```

- [ ] **Step 2: Run tests to verify the right tests fail**

```bash
cd mcp-garmin && poetry run pytest tests/unit/tools/test_goals.py -v
```

Expected: `PASSED` on all `test_date_range_tool_*` tests (these test existing tools). `FAILED` on exactly these three: `test_tools_list_contains_all`, `test_get_personal_records_calls_correct_method`, `test_get_personal_records_returns_json`.

### Task 2: Implement get_personal_records

- [ ] **Step 3: Add the tool and handler to goals.py**

In `mcp-garmin/src/mcp_garmin/tools/goals.py`:

**3a.** Insert this function before the `DISPATCH` dict (after the `TOOLS` list):

```python
def get_personal_records(client: Garmin, arguments: dict[str, str]) -> list[TextContent]:
    return _json_result(client.get_personal_record())
```

**3b.** Append one entry to the existing `TOOLS` list (add before the closing `]`):

```python
    Tool(
        name="get_personal_records",
        description="All-time personal records: best times and distances for running, cycling, and other activities.",
        inputSchema={"type": "object", "properties": {}, "required": []},
    ),
```

**3c.** Append one entry to the existing `DISPATCH` dict (add before the closing `}`):

```python
    "get_personal_records": get_personal_records,
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd mcp-garmin && poetry run pytest tests/unit/tools/test_goals.py -v
```

Expected: All tests PASS.

- [ ] **Step 4b: Run full suite to catch regressions**

```bash
cd mcp-garmin && poetry run pytest -v
```

Expected: All tests PASS.

- [ ] **Step 5: Commit**

```bash
git add mcp-garmin/src/mcp_garmin/tools/goals.py mcp-garmin/tests/unit/tools/test_goals.py
git commit -m "feat(mcp-garmin): add get_personal_records tool"
```

---

## Chunk 2: get_body_battery

**Files:**
- Modify: `mcp-garmin/src/mcp_garmin/tools/daily.py`
- Modify: `mcp-garmin/tests/unit/tools/test_daily.py`

> **Note on the Garmin client method:** `python-garminconnect` exposes `get_body_battery(startdate, enddate)` (date range). For a single-date tool, call it as `client.get_body_battery(date, date)`. Verify with `help(client.get_body_battery)` or the library source before implementing.

### Task 3: Add get_body_battery — failing test

- [ ] **Step 1: Write the failing test**

Append to `mcp-garmin/tests/unit/tools/test_daily.py`:

```python
# --- get_body_battery ---


def test_get_body_battery_calls_correct_method() -> None:
    client = make_client(get_body_battery=[{"date": "2026-02-20", "charged": 80, "drained": 30}])
    DISPATCH["get_body_battery"](client, {"date": "2026-02-20"})
    client.get_body_battery.assert_called_once_with("2026-02-20", "2026-02-20")


def test_get_body_battery_returns_json() -> None:
    client = make_client(get_body_battery=[{"date": "2026-02-20", "charged": 80, "drained": 30}])
    result = DISPATCH["get_body_battery"](client, {"date": "2026-02-20"})
    data = json.loads(result[0].text)
    assert data[0]["charged"] == 80


def test_get_body_battery_rejects_bad_date() -> None:
    client = MagicMock()
    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        DISPATCH["get_body_battery"](client, {"date": "bad"})
```

Also update the tools-list assertion at the bottom of `test_daily.py`:

```python
def test_tools_list_contains_all() -> None:
    names = {t.name for t in TOOLS}
    assert names == {"get_daily_stats", "get_heart_rate", "get_sleep", "get_body_battery"}
```

(Replace the existing `test_tools_list_contains_all_three` function.)

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd mcp-garmin && poetry run pytest tests/unit/tools/test_daily.py -v
```

Expected: FAIL on `test_tools_list_contains_all` and the three new `get_body_battery` tests.

### Task 4: Implement get_body_battery

- [ ] **Step 3: Add handler and tool definition to daily.py**

In `mcp-garmin/src/mcp_garmin/tools/daily.py`, add the handler function after `get_sleep`:

```python
def get_body_battery(client: Garmin, arguments: dict[str, str]) -> list[TextContent]:
    validate_date(arguments["date"])
    date = arguments["date"]
    return _json_result(client.get_body_battery(date, date))
```

Add to the `TOOLS` list:

```python
_date_tool("get_body_battery", "Body battery charge and drain data for the day."),
```

Add to `DISPATCH`:

```python
"get_body_battery": get_body_battery,
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd mcp-garmin && poetry run pytest tests/unit/tools/test_daily.py -v
```

Expected: All tests PASS.

- [ ] **Step 5: Commit**

```bash
git add mcp-garmin/src/mcp_garmin/tools/daily.py mcp-garmin/tests/unit/tools/test_daily.py
git commit -m "feat(mcp-garmin): add get_body_battery tool"
```

---

## Chunk 3: get_activity_details

**Files:**
- Modify: `mcp-garmin/src/mcp_garmin/tools/activities.py`
- Modify: `mcp-garmin/tests/unit/tools/test_activities.py`

> **Response size warning:** `get_activity_details` returns per-second `activityDetailMetrics` arrays and `geoPolylineDTO` GPS data that can exceed 100 000 chars. The summarizer below strips these. Verify the exact key names against a real API response after first use; adjust `_ACTIVITY_DETAIL_TIMESERIES_KEYS` accordingly.

### Task 5: Add get_activity_details — failing tests

- [ ] **Step 1: Write the failing tests**

Append to `mcp-garmin/tests/unit/tools/test_activities.py`:

```python
# --- get_activity_details ---


def test_get_activity_details_calls_correct_method() -> None:
    client = MagicMock()
    client.get_activity_details.return_value = {"activityId": 999}
    DISPATCH["get_activity_details"](client, {"activity_id": "999"})
    client.get_activity_details.assert_called_once_with("999")


def test_get_activity_details_returns_json() -> None:
    client = MagicMock()
    client.get_activity_details.return_value = {"activityId": 999, "distance": 5000.0}
    result = DISPATCH["get_activity_details"](client, {"activity_id": "999"})
    data = json.loads(result[0].text)
    assert data["activityId"] == 999


def test_get_activity_details_strips_timeseries() -> None:
    raw = {
        "activityId": 999,
        "distance": 5000.0,
        "activityDetailMetrics": [{"metrics": [1, 2, 3]}] * 3600,
        "geoPolylineDTO": {"polyline": [[0.0, 0.0]] * 3600},
        "heartRateDTO": {"heartRateValues": [[0, 120]] * 3600},
        "metricDescriptors": [{"metricsIndex": 0, "key": "directSpeed"}] * 50,
    }
    client = MagicMock()
    client.get_activity_details.return_value = raw
    result = DISPATCH["get_activity_details"](client, {"activity_id": "999"})
    data = json.loads(result[0].text)

    for key in ("activityDetailMetrics", "geoPolylineDTO", "heartRateDTO", "metricDescriptors"):
        assert key not in data, f"Expected {key!r} to be stripped"

    assert data["activityId"] == 999
    assert data["distance"] == 5000.0


def test_tools_list_contains_both_activity_tools() -> None:
    names = {t.name for t in TOOLS}
    assert "get_activities" in names
    assert "get_activity_details" in names
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd mcp-garmin && poetry run pytest tests/unit/tools/test_activities.py -v
```

Expected: FAIL on all four new tests.

### Task 6: Implement get_activity_details

- [ ] **Step 3: Add summarizer, handler, tool, and dispatch entry to activities.py**

In `mcp-garmin/src/mcp_garmin/tools/activities.py`, add after the existing `get_activities` function:

```python
_ACTIVITY_DETAIL_TIMESERIES_KEYS = frozenset([
    "activityDetailMetrics",
    "geoPolylineDTO",
    "heartRateDTO",
    "metricDescriptors",
])


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
    return _json_result(_summarize_activity_details(client.get_activity_details(arguments["activity_id"])))
```

Add to `TOOLS`:

```python
Tool(
    name="get_activity_details",
    description="Full details for a single activity by ID: splits, laps, and HR zone breakdown. Get activity IDs from get_activities.",
    inputSchema={
        "type": "object",
        "properties": {
            "activity_id": {"type": "string", "description": "Activity ID from get_activities"},
        },
        "required": ["activity_id"],
    },
),
```

Add to `DISPATCH`:

```python
"get_activity_details": get_activity_details,
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd mcp-garmin && poetry run pytest tests/unit/tools/test_activities.py -v
```

Expected: All tests PASS.

- [ ] **Step 5: Commit**

```bash
git add mcp-garmin/src/mcp_garmin/tools/activities.py mcp-garmin/tests/unit/tools/test_activities.py
git commit -m "feat(mcp-garmin): add get_activity_details tool with response summarizer"
```

---

## Chunk 4: get_menstrual_cycle

**Files:**
- Modify: `mcp-garmin/src/mcp_garmin/tools/health.py`
- Modify: `mcp-garmin/tests/unit/tools/test_health.py`

> **Note on the Garmin client method:** Verify the exact method name before implementing. Likely `client.get_menstrual_data(start_date, end_date)` — check with `dir(client)` or the python-garminconnect source.

### Task 7: Add get_menstrual_cycle — failing tests

- [ ] **Step 1: Write the failing tests**

In `mcp-garmin/tests/unit/tools/test_health.py`, update `EXPECTED_TOOLS` to include the new tool and add test cases. Replace the file content with:

```python
import json
from unittest.mock import MagicMock

import pytest

from mcp_garmin.tools.health import DISPATCH, TOOLS

EXPECTED_TOOLS = {
    "get_hrv",
    "get_stress",
    "get_training_readiness",
    "get_max_metrics",
    "get_training_status",
    "get_respiration",
    "get_spo2",
    "get_menstrual_cycle",
}

SINGLE_DATE_METHOD_MAP = {
    "get_hrv": "get_hrv_data",
    "get_stress": "get_stress_data",
    "get_training_readiness": "get_training_readiness",
    "get_max_metrics": "get_max_metrics",
    "get_training_status": "get_training_status",
    "get_respiration": "get_respiration_data",
    "get_spo2": "get_spo2_data",
}


def test_tools_list_contains_all() -> None:
    names = {t.name for t in TOOLS}
    assert names == EXPECTED_TOOLS


@pytest.mark.parametrize("tool_name,method_name", SINGLE_DATE_METHOD_MAP.items())
def test_single_date_tool_calls_correct_method(tool_name: str, method_name: str) -> None:
    client = MagicMock()
    getattr(client, method_name).return_value = {"value": 42}
    DISPATCH[tool_name](client, {"date": "2026-02-20"})
    getattr(client, method_name).assert_called_once_with("2026-02-20")


@pytest.mark.parametrize("tool_name,method_name", SINGLE_DATE_METHOD_MAP.items())
def test_single_date_tool_returns_json(tool_name: str, method_name: str) -> None:
    client = MagicMock()
    getattr(client, method_name).return_value = {"value": 42}
    result = DISPATCH[tool_name](client, {"date": "2026-02-20"})
    data = json.loads(result[0].text)
    assert data["value"] == 42


@pytest.mark.parametrize("tool_name", SINGLE_DATE_METHOD_MAP)
def test_single_date_tool_rejects_bad_date(tool_name: str) -> None:
    client = MagicMock()
    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        DISPATCH[tool_name](client, {"date": "not-valid"})


# --- get_menstrual_cycle ---


def test_get_menstrual_cycle_calls_correct_method() -> None:
    client = MagicMock()
    client.get_menstrual_data.return_value = []
    DISPATCH["get_menstrual_cycle"](client, {"start_date": "2026-02-01", "end_date": "2026-02-28"})
    client.get_menstrual_data.assert_called_once_with("2026-02-01", "2026-02-28")


def test_get_menstrual_cycle_returns_json() -> None:
    client = MagicMock()
    client.get_menstrual_data.return_value = [{"startDate": "2026-02-01", "phase": "menstrual"}]
    result = DISPATCH["get_menstrual_cycle"](
        client, {"start_date": "2026-02-01", "end_date": "2026-02-28"}
    )
    data = json.loads(result[0].text)
    assert data[0]["phase"] == "menstrual"


def test_get_menstrual_cycle_rejects_bad_start_date() -> None:
    client = MagicMock()
    with pytest.raises(ValueError, match="start_date"):
        DISPATCH["get_menstrual_cycle"](client, {"start_date": "bad", "end_date": "2026-02-28"})


def test_get_menstrual_cycle_rejects_bad_end_date() -> None:
    client = MagicMock()
    with pytest.raises(ValueError, match="end_date"):
        DISPATCH["get_menstrual_cycle"](client, {"start_date": "2026-02-01", "end_date": "bad"})
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd mcp-garmin && poetry run pytest tests/unit/tools/test_health.py -v
```

Expected: FAIL on `test_tools_list_contains_all` and all four `get_menstrual_cycle` tests.

### Task 8: Implement get_menstrual_cycle

- [ ] **Step 3: Add handler, tool definition, and dispatch entry to health.py**

In `mcp-garmin/src/mcp_garmin/tools/health.py`, add a date-range handler after `_single_date_handler`:

```python
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
```

Add to `TOOLS`:

```python
_date_range_tool(
    "get_menstrual_cycle",
    "Menstrual cycle tracking data over a date range: phase, symptoms, and cycle stats.",
),
```

Add to `DISPATCH`:

```python
"get_menstrual_cycle": get_menstrual_cycle,
```

- [ ] **Step 4: Run all health tests to verify they pass**

```bash
cd mcp-garmin && poetry run pytest tests/unit/tools/test_health.py -v
```

Expected: All tests PASS.

- [ ] **Step 5: Run the full test suite**

```bash
cd mcp-garmin && poetry run pytest -v
```

Expected: All tests PASS.

- [ ] **Step 6: Commit**

```bash
git add mcp-garmin/src/mcp_garmin/tools/health.py mcp-garmin/tests/unit/tools/test_health.py
git commit -m "feat(mcp-garmin): add get_menstrual_cycle tool"
```

---

## Post-Implementation: Response Size Check

After all 4 tools are implemented, run a live size check for each new tool using real Garmin data. This is especially critical for `get_activity_details`.

- [ ] **Check get_activity_details response size**

In a Python REPL (after Garmin auth):

```python
import json
details = client.get_activity_details("<a_real_activity_id>")
print(f"Raw size: {len(json.dumps(details))} chars")
print("Keys:", list(details.keys()))
```

If raw size > 20 000 chars, verify that `_summarize_activity_details` reduces it sufficiently. If new large keys are found that aren't in `_ACTIVITY_DETAIL_TIMESERIES_KEYS`, add them.

- [ ] **Check get_body_battery response size**

```python
data = client.get_body_battery("2026-03-17", "2026-03-17")
print(f"Raw size: {len(json.dumps(data))} chars")
```

If > 20 000 chars, add a `_summarize_body_battery` function following the same pattern as `_summarize_sleep` in `daily.py`.

- [ ] **Check get_menstrual_cycle response size**

```python
data = client.get_menstrual_data("2026-03-01", "2026-03-17")
print(f"Raw size: {len(json.dumps(data))} chars")
```

If > 20 000 chars, add a `_summarize_menstrual_cycle` function in `health.py` to strip any per-day detail arrays.

- [ ] **Check get_personal_records response size**

```python
data = client.get_personal_record()
print(f"Raw size: {len(json.dumps(data))} chars")
```

Expected small (< 5 000 chars). No action needed unless unexpectedly large.
