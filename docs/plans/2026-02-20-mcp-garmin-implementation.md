# mcp-garmin Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a Python MCP server exposing 17 Garmin Connect tools to Claude, authenticated via pre-generated OAuth tokens with no credentials stored at runtime.

**Architecture:** A thin `server.py` wires the MCP SDK to a tools layer split across domain modules mirroring the python-garminconnect README categories. A module-level Garmin client singleton loads OAuth tokens from `~/.garminconnect` on first use. A standalone `scripts/login.py` handles the one-time interactive token generation.

**Tech Stack:** Python 3.12, `mcp>=1.26`, `garminconnect>=0.2.38`, `pytest`, `pytest-asyncio`, `ruff`, `mypy`, `bandit`

---

## Reference: Design Document

Full design rationale is at `docs/plans/2026-02-20-mcp-garmin-design.md`. Read it before starting.

## Reference: Tool → Library Method Mapping

| MCP Tool | garminconnect method | Params |
|---|---|---|
| `get_daily_stats` | `get_stats(cdate)` | `date` |
| `get_heart_rate` | `get_heart_rates(cdate)` | `date` |
| `get_sleep` | `get_sleep_data(cdate)` | `date` |
| `get_activities` | `get_activities_by_date(startdate, enddate)` | `start_date`, `end_date` |
| `get_hrv` | `get_hrv_data(cdate)` | `date` |
| `get_stress` | `get_stress_data(cdate)` | `date` |
| `get_training_readiness` | `get_training_readiness(cdate)` | `date` |
| `get_max_metrics` | `get_max_metrics(cdate)` | `date` |
| `get_training_status` | `get_training_status(cdate)` | `date` |
| `get_respiration` | `get_respiration_data(cdate)` | `date` |
| `get_spo2` | `get_spo2_data(cdate)` | `date` |
| `get_body_composition` | `get_body_composition(startdate, enddate)` | `start_date`, `end_date` |
| `get_weigh_ins` | `get_weigh_ins(startdate, enddate)` | `start_date`, `end_date` |
| `get_endurance_score` | `get_endurance_score(startdate, enddate)` | `start_date`, `end_date` |
| `get_race_predictions` | `get_race_predictions(startdate, enddate)` | `start_date`, `end_date` |
| `get_hydration` | `get_hydration_data(cdate)` | `date` |

---

## Task 1: Create Module Skeleton

Create all empty files so subsequent tasks can import from each other without `ModuleNotFoundError`.

**Files:**
- Create: `mcp-garmin/src/mcp_garmin/validation.py`
- Create: `mcp-garmin/src/mcp_garmin/client.py`
- Create: `mcp-garmin/src/mcp_garmin/server.py`
- Create: `mcp-garmin/src/mcp_garmin/tools/__init__.py`
- Create: `mcp-garmin/src/mcp_garmin/tools/daily.py`
- Create: `mcp-garmin/src/mcp_garmin/tools/activities.py`
- Create: `mcp-garmin/src/mcp_garmin/tools/health.py`
- Create: `mcp-garmin/src/mcp_garmin/tools/body.py`
- Create: `mcp-garmin/src/mcp_garmin/tools/goals.py`
- Create: `mcp-garmin/src/mcp_garmin/tools/wellness.py`
- Create: `mcp-garmin/scripts/__init__.py`
- Create: `mcp-garmin/scripts/login.py`
- Create: `mcp-garmin/tests/__init__.py`
- Create: `mcp-garmin/tests/unit/__init__.py`
- Create: `mcp-garmin/tests/unit/tools/__init__.py`
- Create: `mcp-garmin/tests/integration/__init__.py`

**Step 1: Create all files**

```bash
cd mcp-garmin
touch src/mcp_garmin/validation.py
touch src/mcp_garmin/client.py
touch src/mcp_garmin/server.py
touch src/mcp_garmin/tools/__init__.py
touch src/mcp_garmin/tools/daily.py
touch src/mcp_garmin/tools/activities.py
touch src/mcp_garmin/tools/health.py
touch src/mcp_garmin/tools/body.py
touch src/mcp_garmin/tools/goals.py
touch src/mcp_garmin/tools/wellness.py
mkdir -p scripts
touch scripts/__init__.py
touch scripts/login.py
touch tests/__init__.py
mkdir -p tests/unit/tools
touch tests/unit/__init__.py
touch tests/unit/tools/__init__.py
mkdir -p tests/integration
touch tests/integration/__init__.py
```

**Step 2: Commit**

```bash
git add -A
git commit -m "chore: create mcp-garmin module skeleton"
```

---

## Task 2: Date Validation Utility

**Files:**
- Write: `mcp-garmin/src/mcp_garmin/validation.py`
- Create: `mcp-garmin/tests/unit/test_validation.py`

**Step 1: Write the failing tests**

Write `tests/unit/test_validation.py`:

```python
import pytest
from mcp_garmin.validation import validate_date


def test_valid_date_passes() -> None:
    validate_date("2026-02-20")  # should not raise


def test_invalid_format_raises() -> None:
    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        validate_date("20-02-2026")


def test_non_date_string_raises() -> None:
    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        validate_date("not-a-date")


def test_empty_string_raises() -> None:
    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        validate_date("")


def test_custom_param_name_in_error() -> None:
    with pytest.raises(ValueError, match="start_date"):
        validate_date("bad", param_name="start_date")
```

**Step 2: Run tests to verify they fail**

```bash
cd mcp-garmin && poetry run pytest tests/unit/test_validation.py -v
```

Expected: `ImportError` — `mcp_garmin.validation` is empty.

**Step 3: Implement validation.py**

```python
import re

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def validate_date(date: str, param_name: str = "date") -> None:
    """Raise ValueError if date is not in YYYY-MM-DD format."""
    if not _DATE_RE.match(date):
        raise ValueError(
            f"Invalid {param_name}: {date!r}. Expected YYYY-MM-DD."
        )
```

**Step 4: Run tests to verify they pass**

```bash
cd mcp-garmin && poetry run pytest tests/unit/test_validation.py -v
```

Expected: 5 passed.

**Step 5: Commit**

```bash
git add src/mcp_garmin/validation.py tests/unit/test_validation.py
git commit -m "feat: add date validation utility"
```

---

## Task 3: Garmin Client Singleton

**Files:**
- Write: `mcp-garmin/src/mcp_garmin/client.py`
- Create: `mcp-garmin/tests/unit/test_client.py`

**Step 1: Write the failing tests**

Write `tests/unit/test_client.py`:

```python
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest
from mcp_garmin import client as client_module


def _reset_singleton() -> None:
    """Reset module-level singleton between tests."""
    client_module._client = None


def test_get_client_loads_tokens_from_token_store(tmp_path: Path) -> None:
    _reset_singleton()
    mock_garmin = MagicMock()

    with (
        patch.object(client_module, "TOKEN_STORE", tmp_path),
        patch("mcp_garmin.client.Garmin", return_value=mock_garmin),
    ):
        tmp_path.mkdir(parents=True, exist_ok=True)
        result = client_module.get_client()

    mock_garmin.login.assert_called_once_with(str(tmp_path))
    assert result is mock_garmin


def test_get_client_returns_same_instance_on_second_call(tmp_path: Path) -> None:
    _reset_singleton()
    mock_garmin = MagicMock()

    with (
        patch.object(client_module, "TOKEN_STORE", tmp_path),
        patch("mcp_garmin.client.Garmin", return_value=mock_garmin),
    ):
        tmp_path.mkdir(parents=True, exist_ok=True)
        first = client_module.get_client()
        second = client_module.get_client()

    assert first is second


def test_get_client_raises_when_token_store_missing(tmp_path: Path) -> None:
    _reset_singleton()
    missing = tmp_path / "does_not_exist"

    with patch.object(client_module, "TOKEN_STORE", missing):
        with pytest.raises(RuntimeError, match="scripts/login.py"):
            client_module.get_client()
```

**Step 2: Run tests to verify they fail**

```bash
cd mcp-garmin && poetry run pytest tests/unit/test_client.py -v
```

Expected: `ImportError` — `client.py` is empty.

**Step 3: Implement client.py**

```python
from __future__ import annotations

import logging
from pathlib import Path

from garminconnect import Garmin

logger = logging.getLogger(__name__)

TOKEN_STORE = Path.home() / ".garminconnect"

_client: Garmin | None = None


def get_client() -> Garmin:
    """Return the authenticated Garmin singleton, creating it on first call."""
    global _client
    if _client is None:
        _client = _create_client()
    return _client


def _create_client() -> Garmin:
    if not TOKEN_STORE.exists():
        raise RuntimeError(
            f"Garmin tokens not found at {TOKEN_STORE}. "
            "Run scripts/login.py to authenticate."
        )
    garmin = Garmin()
    garmin.login(str(TOKEN_STORE))
    logger.info("Garmin client authenticated from token store at %s", TOKEN_STORE)
    return garmin
```

**Step 4: Run tests to verify they pass**

```bash
cd mcp-garmin && poetry run pytest tests/unit/test_client.py -v
```

Expected: 3 passed.

**Step 5: Commit**

```bash
git add src/mcp_garmin/client.py tests/unit/test_client.py
git commit -m "feat: add garmin client singleton with token-based auth"
```

---

## Task 4: Daily Health & Activity Tools

Three tools: `get_daily_stats`, `get_heart_rate`, `get_sleep`.

**Files:**
- Write: `mcp-garmin/src/mcp_garmin/tools/daily.py`
- Create: `mcp-garmin/tests/unit/tools/test_daily.py`

**Step 1: Write the failing tests**

Write `tests/unit/tools/test_daily.py`:

```python
import json
from unittest.mock import MagicMock
import pytest
from mcp_garmin.tools.daily import DISPATCH, TOOLS


def make_client(**kwargs: object) -> MagicMock:
    client = MagicMock()
    for method, return_value in kwargs.items():
        getattr(client, method).return_value = return_value
    return client


# --- get_daily_stats ---

def test_get_daily_stats_calls_get_stats() -> None:
    client = make_client(get_stats={"totalSteps": 8000})
    DISPATCH["get_daily_stats"](client, {"date": "2026-02-20"})
    client.get_stats.assert_called_once_with("2026-02-20")


def test_get_daily_stats_returns_json() -> None:
    client = make_client(get_stats={"totalSteps": 8000})
    result = DISPATCH["get_daily_stats"](client, {"date": "2026-02-20"})
    data = json.loads(result[0].text)
    assert data["totalSteps"] == 8000


def test_get_daily_stats_rejects_bad_date() -> None:
    client = MagicMock()
    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        DISPATCH["get_daily_stats"](client, {"date": "bad"})


# --- get_heart_rate ---

def test_get_heart_rate_calls_get_heart_rates() -> None:
    client = make_client(get_heart_rates={"restingHeartRate": 55})
    DISPATCH["get_heart_rate"](client, {"date": "2026-02-20"})
    client.get_heart_rates.assert_called_once_with("2026-02-20")


def test_get_heart_rate_returns_json() -> None:
    client = make_client(get_heart_rates={"restingHeartRate": 55})
    result = DISPATCH["get_heart_rate"](client, {"date": "2026-02-20"})
    data = json.loads(result[0].text)
    assert data["restingHeartRate"] == 55


def test_get_heart_rate_rejects_bad_date() -> None:
    client = MagicMock()
    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        DISPATCH["get_heart_rate"](client, {"date": "not-a-date"})


# --- get_sleep ---

def test_get_sleep_calls_get_sleep_data() -> None:
    client = make_client(get_sleep_data={"sleepTimeSeconds": 28800})
    DISPATCH["get_sleep"](client, {"date": "2026-02-20"})
    client.get_sleep_data.assert_called_once_with("2026-02-20")


def test_get_sleep_returns_json() -> None:
    client = make_client(get_sleep_data={"sleepTimeSeconds": 28800})
    result = DISPATCH["get_sleep"](client, {"date": "2026-02-20"})
    data = json.loads(result[0].text)
    assert data["sleepTimeSeconds"] == 28800


def test_get_sleep_rejects_bad_date() -> None:
    client = MagicMock()
    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        DISPATCH["get_sleep"](client, {"date": "2026/02/20"})


# --- TOOLS list ---

def test_tools_list_contains_all_three() -> None:
    names = {t.name for t in TOOLS}
    assert names == {"get_daily_stats", "get_heart_rate", "get_sleep"}
```

**Step 2: Run tests to verify they fail**

```bash
cd mcp-garmin && poetry run pytest tests/unit/tools/test_daily.py -v
```

Expected: `ImportError` — `tools/daily.py` is empty.

**Step 3: Implement tools/daily.py**

```python
from __future__ import annotations

import json
from typing import Any, Callable

from garminconnect import Garmin
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


def get_sleep(client: Garmin, arguments: dict[str, str]) -> list[TextContent]:
    validate_date(arguments["date"])
    return _json_result(client.get_sleep_data(arguments["date"]))


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
    _date_tool("get_daily_stats", "Daily activity stats: steps, calories burned, stress, active minutes."),
    _date_tool("get_heart_rate", "Heart rate data for the day including resting HR and HR time series."),
    _date_tool("get_sleep", "Sleep data: duration, stages (deep/light/REM/awake), and sleep score."),
]

DISPATCH: dict[str, Callable[[Garmin, dict[str, str]], list[TextContent]]] = {
    "get_daily_stats": get_daily_stats,
    "get_heart_rate": get_heart_rate,
    "get_sleep": get_sleep,
}
```

**Step 4: Run tests to verify they pass**

```bash
cd mcp-garmin && poetry run pytest tests/unit/tools/test_daily.py -v
```

Expected: 11 passed.

**Step 5: Commit**

```bash
git add src/mcp_garmin/tools/daily.py tests/unit/tools/test_daily.py
git commit -m "feat: add daily health tools (get_daily_stats, get_heart_rate, get_sleep)"
```

---

## Task 5: Activities Tool

One tool: `get_activities`.

**Files:**
- Write: `mcp-garmin/src/mcp_garmin/tools/activities.py`
- Create: `mcp-garmin/tests/unit/tools/test_activities.py`

**Step 1: Write the failing tests**

Write `tests/unit/tools/test_activities.py`:

```python
import json
from unittest.mock import MagicMock
import pytest
from mcp_garmin.tools.activities import DISPATCH, TOOLS


def test_get_activities_calls_correct_method() -> None:
    client = MagicMock()
    client.get_activities_by_date.return_value = []
    DISPATCH["get_activities"](client, {"start_date": "2026-02-01", "end_date": "2026-02-20"})
    client.get_activities_by_date.assert_called_once_with("2026-02-01", "2026-02-20")


def test_get_activities_returns_json() -> None:
    client = MagicMock()
    client.get_activities_by_date.return_value = [{"activityId": 123, "activityType": "running"}]
    result = DISPATCH["get_activities"](client, {"start_date": "2026-02-01", "end_date": "2026-02-20"})
    data = json.loads(result[0].text)
    assert data[0]["activityId"] == 123


def test_get_activities_rejects_bad_start_date() -> None:
    client = MagicMock()
    with pytest.raises(ValueError, match="start_date"):
        DISPATCH["get_activities"](client, {"start_date": "bad", "end_date": "2026-02-20"})


def test_get_activities_rejects_bad_end_date() -> None:
    client = MagicMock()
    with pytest.raises(ValueError, match="end_date"):
        DISPATCH["get_activities"](client, {"start_date": "2026-02-01", "end_date": "bad"})


def test_tools_list_contains_get_activities() -> None:
    names = {t.name for t in TOOLS}
    assert "get_activities" in names
```

**Step 2: Run tests to verify they fail**

```bash
cd mcp-garmin && poetry run pytest tests/unit/tools/test_activities.py -v
```

Expected: `ImportError`.

**Step 3: Implement tools/activities.py**

```python
from __future__ import annotations

import json
from typing import Any, Callable

from garminconnect import Garmin
from mcp.types import TextContent, Tool

from mcp_garmin.validation import validate_date


def _json_result(data: Any) -> list[TextContent]:
    return [TextContent(type="text", text=json.dumps(data, indent=2))]


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


def get_activities(client: Garmin, arguments: dict[str, str]) -> list[TextContent]:
    validate_date(arguments["start_date"], param_name="start_date")
    validate_date(arguments["end_date"], param_name="end_date")
    return _json_result(client.get_activities_by_date(arguments["start_date"], arguments["end_date"]))


TOOLS: list[Tool] = [
    _date_range_tool(
        "get_activities",
        "Workouts in a date range with type, duration, heart rate, distance, and pace.",
    ),
]

DISPATCH: dict[str, Callable[[Garmin, dict[str, str]], list[TextContent]]] = {
    "get_activities": get_activities,
}
```

**Step 4: Run tests to verify they pass**

```bash
cd mcp-garmin && poetry run pytest tests/unit/tools/test_activities.py -v
```

Expected: 5 passed.

**Step 5: Commit**

```bash
git add src/mcp_garmin/tools/activities.py tests/unit/tools/test_activities.py
git commit -m "feat: add activities tool (get_activities)"
```

---

## Task 6: Advanced Health Metrics Tools

Seven tools: `get_hrv`, `get_stress`, `get_training_readiness`, `get_max_metrics`, `get_training_status`, `get_respiration`, `get_spo2`.

All take a single `date` parameter.

**Files:**
- Write: `mcp-garmin/src/mcp_garmin/tools/health.py`
- Create: `mcp-garmin/tests/unit/tools/test_health.py`

**Step 1: Write the failing tests**

Write `tests/unit/tools/test_health.py`:

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
}

# Mapping: tool name → garminconnect method name
METHOD_MAP = {
    "get_hrv": "get_hrv_data",
    "get_stress": "get_stress_data",
    "get_training_readiness": "get_training_readiness",
    "get_max_metrics": "get_max_metrics",
    "get_training_status": "get_training_status",
    "get_respiration": "get_respiration_data",
    "get_spo2": "get_spo2_data",
}


def test_tools_list_contains_all_seven() -> None:
    names = {t.name for t in TOOLS}
    assert names == EXPECTED_TOOLS


@pytest.mark.parametrize("tool_name,method_name", METHOD_MAP.items())
def test_tool_calls_correct_method(tool_name: str, method_name: str) -> None:
    client = MagicMock()
    getattr(client, method_name).return_value = {"value": 42}
    DISPATCH[tool_name](client, {"date": "2026-02-20"})
    getattr(client, method_name).assert_called_once_with("2026-02-20")


@pytest.mark.parametrize("tool_name,method_name", METHOD_MAP.items())
def test_tool_returns_json(tool_name: str, method_name: str) -> None:
    client = MagicMock()
    getattr(client, method_name).return_value = {"value": 42}
    result = DISPATCH[tool_name](client, {"date": "2026-02-20"})
    data = json.loads(result[0].text)
    assert data["value"] == 42


@pytest.mark.parametrize("tool_name", EXPECTED_TOOLS)
def test_tool_rejects_bad_date(tool_name: str) -> None:
    client = MagicMock()
    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        DISPATCH[tool_name](client, {"date": "not-valid"})
```

**Step 2: Run tests to verify they fail**

```bash
cd mcp-garmin && poetry run pytest tests/unit/tools/test_health.py -v
```

Expected: `ImportError`.

**Step 3: Implement tools/health.py**

```python
from __future__ import annotations

import json
from typing import Any, Callable

from garminconnect import Garmin
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


def _single_date_handler(method_name: str) -> Callable[[Garmin, dict[str, str]], list[TextContent]]:
    def handler(client: Garmin, arguments: dict[str, str]) -> list[TextContent]:
        validate_date(arguments["date"])
        return _json_result(getattr(client, method_name)(arguments["date"]))
    return handler


TOOLS: list[Tool] = [
    _date_tool("get_hrv", "Heart Rate Variability data for the day."),
    _date_tool("get_stress", "Detailed stress data throughout the day."),
    _date_tool("get_training_readiness", "Training readiness score and contributing factors."),
    _date_tool("get_max_metrics", "VO2 max and fitness age estimates."),
    _date_tool("get_training_status", "Current training status and load."),
    _date_tool("get_respiration", "Respiration rate data throughout the day."),
    _date_tool("get_spo2", "Blood oxygen saturation (SpO2) data throughout the day."),
]

DISPATCH: dict[str, Callable[[Garmin, dict[str, str]], list[TextContent]]] = {
    "get_hrv": _single_date_handler("get_hrv_data"),
    "get_stress": _single_date_handler("get_stress_data"),
    "get_training_readiness": _single_date_handler("get_training_readiness"),
    "get_max_metrics": _single_date_handler("get_max_metrics"),
    "get_training_status": _single_date_handler("get_training_status"),
    "get_respiration": _single_date_handler("get_respiration_data"),
    "get_spo2": _single_date_handler("get_spo2_data"),
}
```

**Step 4: Run tests to verify they pass**

```bash
cd mcp-garmin && poetry run pytest tests/unit/tools/test_health.py -v
```

Expected: 22 passed.

**Step 5: Commit**

```bash
git add src/mcp_garmin/tools/health.py tests/unit/tools/test_health.py
git commit -m "feat: add advanced health metrics tools (HRV, stress, training readiness, VO2 max, respiration, SpO2)"
```

---

## Task 7: Body Composition Tools

Two tools: `get_body_composition`, `get_weigh_ins`. Both take date ranges.

**Files:**
- Write: `mcp-garmin/src/mcp_garmin/tools/body.py`
- Create: `mcp-garmin/tests/unit/tools/test_body.py`

**Step 1: Write the failing tests**

Write `tests/unit/tools/test_body.py`:

```python
import json
from unittest.mock import MagicMock
import pytest
from mcp_garmin.tools.body import DISPATCH, TOOLS

EXPECTED_TOOLS = {"get_body_composition", "get_weigh_ins"}
METHOD_MAP = {
    "get_body_composition": "get_body_composition",
    "get_weigh_ins": "get_weigh_ins",
}


def test_tools_list_contains_both() -> None:
    assert {t.name for t in TOOLS} == EXPECTED_TOOLS


@pytest.mark.parametrize("tool_name,method_name", METHOD_MAP.items())
def test_tool_calls_correct_method(tool_name: str, method_name: str) -> None:
    client = MagicMock()
    getattr(client, method_name).return_value = {}
    DISPATCH[tool_name](client, {"start_date": "2026-02-01", "end_date": "2026-02-20"})
    getattr(client, method_name).assert_called_once_with("2026-02-01", "2026-02-20")


@pytest.mark.parametrize("tool_name", EXPECTED_TOOLS)
def test_tool_returns_json(tool_name: str) -> None:
    client = MagicMock()
    getattr(client, METHOD_MAP[tool_name]).return_value = {"weight": 75.5}
    result = DISPATCH[tool_name](client, {"start_date": "2026-02-01", "end_date": "2026-02-20"})
    data = json.loads(result[0].text)
    assert data["weight"] == 75.5


@pytest.mark.parametrize("tool_name", EXPECTED_TOOLS)
def test_tool_rejects_bad_start_date(tool_name: str) -> None:
    client = MagicMock()
    with pytest.raises(ValueError, match="start_date"):
        DISPATCH[tool_name](client, {"start_date": "bad", "end_date": "2026-02-20"})


@pytest.mark.parametrize("tool_name", EXPECTED_TOOLS)
def test_tool_rejects_bad_end_date(tool_name: str) -> None:
    client = MagicMock()
    with pytest.raises(ValueError, match="end_date"):
        DISPATCH[tool_name](client, {"start_date": "2026-02-01", "end_date": "bad"})
```

**Step 2: Run tests to verify they fail**

```bash
cd mcp-garmin && poetry run pytest tests/unit/tools/test_body.py -v
```

Expected: `ImportError`.

**Step 3: Implement tools/body.py**

```python
from __future__ import annotations

import json
from typing import Any, Callable

from garminconnect import Garmin
from mcp.types import TextContent, Tool

from mcp_garmin.validation import validate_date


def _json_result(data: Any) -> list[TextContent]:
    return [TextContent(type="text", text=json.dumps(data, indent=2))]


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


def _range_handler(method_name: str) -> Callable[[Garmin, dict[str, str]], list[TextContent]]:
    def handler(client: Garmin, arguments: dict[str, str]) -> list[TextContent]:
        validate_date(arguments["start_date"], param_name="start_date")
        validate_date(arguments["end_date"], param_name="end_date")
        return _json_result(getattr(client, method_name)(arguments["start_date"], arguments["end_date"]))
    return handler


TOOLS: list[Tool] = [
    _date_range_tool("get_body_composition", "Body composition over a date range: weight, body fat %, BMI."),
    _date_range_tool("get_weigh_ins", "Weight log entries over a date range."),
]

DISPATCH: dict[str, Callable[[Garmin, dict[str, str]], list[TextContent]]] = {
    "get_body_composition": _range_handler("get_body_composition"),
    "get_weigh_ins": _range_handler("get_weigh_ins"),
}
```

**Step 4: Run tests to verify they pass**

```bash
cd mcp-garmin && poetry run pytest tests/unit/tools/test_body.py -v
```

Expected: 10 passed.

**Step 5: Commit**

```bash
git add src/mcp_garmin/tools/body.py tests/unit/tools/test_body.py
git commit -m "feat: add body composition tools (get_body_composition, get_weigh_ins)"
```

---

## Task 8: Goals & Achievements Tools

Two tools: `get_endurance_score`, `get_race_predictions`. Both take date ranges.

**Files:**
- Write: `mcp-garmin/src/mcp_garmin/tools/goals.py`
- Create: `mcp-garmin/tests/unit/tools/test_goals.py`

**Step 1: Write the failing tests**

Write `tests/unit/tools/test_goals.py`:

```python
import json
from unittest.mock import MagicMock
import pytest
from mcp_garmin.tools.goals import DISPATCH, TOOLS

EXPECTED_TOOLS = {"get_endurance_score", "get_race_predictions"}
METHOD_MAP = {
    "get_endurance_score": "get_endurance_score",
    "get_race_predictions": "get_race_predictions",
}


def test_tools_list_contains_both() -> None:
    assert {t.name for t in TOOLS} == EXPECTED_TOOLS


@pytest.mark.parametrize("tool_name,method_name", METHOD_MAP.items())
def test_tool_calls_correct_method(tool_name: str, method_name: str) -> None:
    client = MagicMock()
    getattr(client, method_name).return_value = {}
    DISPATCH[tool_name](client, {"start_date": "2026-02-01", "end_date": "2026-02-20"})
    getattr(client, method_name).assert_called_once_with("2026-02-01", "2026-02-20")


@pytest.mark.parametrize("tool_name", EXPECTED_TOOLS)
def test_tool_returns_json(tool_name: str) -> None:
    client = MagicMock()
    getattr(client, METHOD_MAP[tool_name]).return_value = {"score": 80}
    result = DISPATCH[tool_name](client, {"start_date": "2026-02-01", "end_date": "2026-02-20"})
    data = json.loads(result[0].text)
    assert data["score"] == 80


@pytest.mark.parametrize("tool_name", EXPECTED_TOOLS)
def test_tool_rejects_bad_start_date(tool_name: str) -> None:
    client = MagicMock()
    with pytest.raises(ValueError, match="start_date"):
        DISPATCH[tool_name](client, {"start_date": "bad", "end_date": "2026-02-20"})


@pytest.mark.parametrize("tool_name", EXPECTED_TOOLS)
def test_tool_rejects_bad_end_date(tool_name: str) -> None:
    client = MagicMock()
    with pytest.raises(ValueError, match="end_date"):
        DISPATCH[tool_name](client, {"start_date": "2026-02-01", "end_date": "bad"})
```

**Step 2: Run tests to verify they fail**

```bash
cd mcp-garmin && poetry run pytest tests/unit/tools/test_goals.py -v
```

Expected: `ImportError`.

**Step 3: Implement tools/goals.py**

```python
from __future__ import annotations

import json
from typing import Any, Callable

from garminconnect import Garmin
from mcp.types import TextContent, Tool

from mcp_garmin.validation import validate_date


def _json_result(data: Any) -> list[TextContent]:
    return [TextContent(type="text", text=json.dumps(data, indent=2))]


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


def _range_handler(method_name: str) -> Callable[[Garmin, dict[str, str]], list[TextContent]]:
    def handler(client: Garmin, arguments: dict[str, str]) -> list[TextContent]:
        validate_date(arguments["start_date"], param_name="start_date")
        validate_date(arguments["end_date"], param_name="end_date")
        return _json_result(getattr(client, method_name)(arguments["start_date"], arguments["end_date"]))
    return handler


TOOLS: list[Tool] = [
    _date_range_tool("get_endurance_score", "Endurance score trend over a date range."),
    _date_range_tool("get_race_predictions", "Predicted race finish times (5K, 10K, half marathon, marathon) over a date range."),
]

DISPATCH: dict[str, Callable[[Garmin, dict[str, str]], list[TextContent]]] = {
    "get_endurance_score": _range_handler("get_endurance_score"),
    "get_race_predictions": _range_handler("get_race_predictions"),
}
```

**Step 4: Run tests to verify they pass**

```bash
cd mcp-garmin && poetry run pytest tests/unit/tools/test_goals.py -v
```

Expected: 10 passed.

**Step 5: Commit**

```bash
git add src/mcp_garmin/tools/goals.py tests/unit/tools/test_goals.py
git commit -m "feat: add goals tools (get_endurance_score, get_race_predictions)"
```

---

## Task 9: Hydration & Wellness Tool

One tool: `get_hydration`. Takes a single date.

**Files:**
- Write: `mcp-garmin/src/mcp_garmin/tools/wellness.py`
- Create: `mcp-garmin/tests/unit/tools/test_wellness.py`

**Step 1: Write the failing tests**

Write `tests/unit/tools/test_wellness.py`:

```python
import json
from unittest.mock import MagicMock
import pytest
from mcp_garmin.tools.wellness import DISPATCH, TOOLS


def test_tools_list_contains_get_hydration() -> None:
    assert {t.name for t in TOOLS} == {"get_hydration"}


def test_get_hydration_calls_correct_method() -> None:
    client = MagicMock()
    client.get_hydration_data.return_value = {"totalIntakeInOz": 64}
    DISPATCH["get_hydration"](client, {"date": "2026-02-20"})
    client.get_hydration_data.assert_called_once_with("2026-02-20")


def test_get_hydration_returns_json() -> None:
    client = MagicMock()
    client.get_hydration_data.return_value = {"totalIntakeInOz": 64}
    result = DISPATCH["get_hydration"](client, {"date": "2026-02-20"})
    data = json.loads(result[0].text)
    assert data["totalIntakeInOz"] == 64


def test_get_hydration_rejects_bad_date() -> None:
    client = MagicMock()
    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        DISPATCH["get_hydration"](client, {"date": "bad"})
```

**Step 2: Run tests to verify they fail**

```bash
cd mcp-garmin && poetry run pytest tests/unit/tools/test_wellness.py -v
```

Expected: `ImportError`.

**Step 3: Implement tools/wellness.py**

```python
from __future__ import annotations

import json
from typing import Any, Callable

from garminconnect import Garmin
from mcp.types import TextContent, Tool

from mcp_garmin.validation import validate_date


def _json_result(data: Any) -> list[TextContent]:
    return [TextContent(type="text", text=json.dumps(data, indent=2))]


def get_hydration(client: Garmin, arguments: dict[str, str]) -> list[TextContent]:
    validate_date(arguments["date"])
    return _json_result(client.get_hydration_data(arguments["date"]))


TOOLS: list[Tool] = [
    Tool(
        name="get_hydration",
        description="Hydration intake data for the day.",
        inputSchema={
            "type": "object",
            "properties": {
                "date": {"type": "string", "description": "Date in YYYY-MM-DD format"},
            },
            "required": ["date"],
        },
    ),
]

DISPATCH: dict[str, Callable[[Garmin, dict[str, str]], list[TextContent]]] = {
    "get_hydration": get_hydration,
}
```

**Step 4: Run tests to verify they pass**

```bash
cd mcp-garmin && poetry run pytest tests/unit/tools/test_wellness.py -v
```

Expected: 4 passed.

**Step 5: Commit**

```bash
git add src/mcp_garmin/tools/wellness.py tests/unit/tools/test_wellness.py
git commit -m "feat: add wellness tool (get_hydration)"
```

---

## Task 10: Tools Aggregator

Wire all tool modules together in `tools/__init__.py`.

**Files:**
- Write: `mcp-garmin/src/mcp_garmin/tools/__init__.py`
- Create: `mcp-garmin/tests/unit/tools/test_aggregator.py`

**Step 1: Write the failing tests**

Write `tests/unit/tools/test_aggregator.py`:

```python
from mcp_garmin import tools

ALL_EXPECTED = {
    "get_daily_stats", "get_heart_rate", "get_sleep",
    "get_activities",
    "get_hrv", "get_stress", "get_training_readiness",
    "get_max_metrics", "get_training_status", "get_respiration", "get_spo2",
    "get_body_composition", "get_weigh_ins",
    "get_endurance_score", "get_race_predictions",
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
```

**Step 2: Run tests to verify they fail**

```bash
cd mcp-garmin && poetry run pytest tests/unit/tools/test_aggregator.py -v
```

Expected: `ImportError` — `tools/__init__.py` is empty.

**Step 3: Implement tools/__init__.py**

```python
from mcp.types import Tool
from mcp.types import TextContent
from garminconnect import Garmin
from typing import Callable

from mcp_garmin.tools.activities import DISPATCH as _ACTIVITY_DISPATCH, TOOLS as _ACTIVITY_TOOLS
from mcp_garmin.tools.body import DISPATCH as _BODY_DISPATCH, TOOLS as _BODY_TOOLS
from mcp_garmin.tools.daily import DISPATCH as _DAILY_DISPATCH, TOOLS as _DAILY_TOOLS
from mcp_garmin.tools.goals import DISPATCH as _GOALS_DISPATCH, TOOLS as _GOALS_TOOLS
from mcp_garmin.tools.health import DISPATCH as _HEALTH_DISPATCH, TOOLS as _HEALTH_TOOLS
from mcp_garmin.tools.wellness import DISPATCH as _WELLNESS_DISPATCH, TOOLS as _WELLNESS_TOOLS

ALL_TOOLS: list[Tool] = (
    _DAILY_TOOLS
    + _ACTIVITY_TOOLS
    + _HEALTH_TOOLS
    + _BODY_TOOLS
    + _GOALS_TOOLS
    + _WELLNESS_TOOLS
)

DISPATCH: dict[str, Callable[[Garmin, dict[str, str]], list[TextContent]]] = {
    **_DAILY_DISPATCH,
    **_ACTIVITY_DISPATCH,
    **_HEALTH_DISPATCH,
    **_BODY_DISPATCH,
    **_GOALS_DISPATCH,
    **_WELLNESS_DISPATCH,
}
```

**Step 4: Run tests to verify they pass**

```bash
cd mcp-garmin && poetry run pytest tests/unit/tools/test_aggregator.py -v
```

Expected: 3 passed.

**Step 5: Run all unit tests to confirm nothing is broken**

```bash
cd mcp-garmin && poetry run pytest tests/unit/ -v
```

Expected: all passed.

**Step 6: Commit**

```bash
git add src/mcp_garmin/tools/__init__.py tests/unit/tools/test_aggregator.py
git commit -m "feat: add tools aggregator"
```

---

## Task 11: MCP Server

Wire the MCP SDK to the tools layer.

**Files:**
- Write: `mcp-garmin/src/mcp_garmin/server.py`
- Create: `mcp-garmin/tests/unit/test_server.py`
- Modify: `mcp-garmin/pyproject.toml` (add script entry point)

**Step 1: Write the failing tests**

Write `tests/unit/test_server.py`:

```python
from unittest.mock import MagicMock, patch
import pytest
from mcp.types import TextContent
import mcp_garmin.server as server_module


@pytest.fixture(autouse=True)
def reset_client() -> None:
    """Ensure client singleton is reset before each test."""
    import mcp_garmin.client as client_module
    client_module._client = None


async def test_list_tools_returns_all_tools() -> None:
    result = await server_module.list_tools()
    from mcp_garmin import tools
    assert len(result) == len(tools.ALL_TOOLS)


async def test_call_tool_dispatches_correctly() -> None:
    mock_client = MagicMock()
    mock_client.get_stats.return_value = {"totalSteps": 5000}

    with patch("mcp_garmin.server.get_client", return_value=mock_client):
        result = await server_module.call_tool("get_daily_stats", {"date": "2026-02-20"})

    assert isinstance(result[0], TextContent)
    assert "totalSteps" in result[0].text


async def test_call_tool_returns_error_for_unknown_tool() -> None:
    mock_client = MagicMock()
    with patch("mcp_garmin.server.get_client", return_value=mock_client):
        result = await server_module.call_tool("nonexistent_tool", {})
    assert "Unknown tool" in result[0].text


async def test_call_tool_returns_error_on_auth_failure() -> None:
    with patch("mcp_garmin.server.get_client", side_effect=RuntimeError("Tokens not found")):
        result = await server_module.call_tool("get_daily_stats", {"date": "2026-02-20"})
    assert "Tokens not found" in result[0].text


async def test_call_tool_returns_error_on_validation_failure() -> None:
    mock_client = MagicMock()
    with patch("mcp_garmin.server.get_client", return_value=mock_client):
        result = await server_module.call_tool("get_daily_stats", {"date": "bad-date"})
    assert "Invalid" in result[0].text
```

**Step 2: Run tests to verify they fail**

```bash
cd mcp-garmin && poetry run pytest tests/unit/test_server.py -v
```

Expected: `ImportError` — `server.py` is empty.

**Step 3: Implement server.py**

```python
from __future__ import annotations

import asyncio
import logging

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from mcp_garmin import tools
from mcp_garmin.client import get_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

server: Server = Server("mcp-garmin")


@server.list_tools()
async def list_tools() -> list[Tool]:
    return tools.ALL_TOOLS


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, str]) -> list[TextContent]:
    logger.info("Tool called: %s", name)
    try:
        client = get_client()
        handler = tools.DISPATCH.get(name)
        if handler is None:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
        return handler(client, arguments)
    except RuntimeError as exc:
        logger.error("Auth error in tool %s: %s", name, exc)
        return [TextContent(type="text", text=str(exc))]
    except ValueError as exc:
        logger.error("Validation error in tool %s: %s", name, exc)
        return [TextContent(type="text", text=f"Invalid argument: {exc}")]
    except Exception as exc:
        logger.error("Unexpected error in tool %s: %s", name, exc, exc_info=True)
        return [TextContent(type="text", text=f"Unexpected error: {exc}")]


def main() -> None:
    asyncio.run(stdio_server(server))


if __name__ == "__main__":
    main()
```

**Step 4: Add script entry point to pyproject.toml**

In `mcp-garmin/pyproject.toml`, add after the `[project]` section:

```toml
[project.scripts]
mcp-garmin = "mcp_garmin.server:main"
```

**Step 5: Run tests to verify they pass**

```bash
cd mcp-garmin && poetry run pytest tests/unit/test_server.py -v
```

Expected: 5 passed.

**Step 6: Run all unit tests**

```bash
cd mcp-garmin && poetry run pytest tests/unit/ -v
```

Expected: all passed.

**Step 7: Commit**

```bash
git add src/mcp_garmin/server.py tests/unit/test_server.py pyproject.toml
git commit -m "feat: add MCP server entrypoint"
```

---

## Task 12: Login Script

**Files:**
- Write: `mcp-garmin/scripts/login.py`

No unit tests — this is a thin interactive wrapper around the garminconnect library.

**Step 1: Implement scripts/login.py**

```python
#!/usr/bin/env python3
"""One-time Garmin Connect authentication.

Prompts for credentials interactively, authenticates via Garmin SSO,
and saves OAuth tokens to ~/.garminconnect. Credentials are never stored.
"""

from __future__ import annotations

import getpass
import sys
from pathlib import Path

from garminconnect import Garmin

TOKEN_STORE = Path.home() / ".garminconnect"


def main() -> None:
    print("Garmin Connect — one-time login")
    print(f"Tokens will be saved to: {TOKEN_STORE}")
    print()

    email = input("Email: ").strip()
    password = getpass.getpass("Password: ")

    def prompt_mfa() -> str:
        return input("MFA code: ").strip()

    print("\nAuthenticating...")
    try:
        client = Garmin(email=email, password=password, prompt_mfa=prompt_mfa)
        client.login()
    except Exception as exc:
        print(f"Login failed: {exc}", file=sys.stderr)
        sys.exit(1)

    TOKEN_STORE.mkdir(mode=0o700, parents=True, exist_ok=True)
    client.garth.dump(str(TOKEN_STORE))

    for token_file in TOKEN_STORE.iterdir():
        token_file.chmod(0o600)

    print(f"\nTokens saved to {TOKEN_STORE}")
    print("You can now run the MCP server — no credentials required.")


if __name__ == "__main__":
    main()
```

**Step 2: Verify it is importable (syntax check)**

```bash
cd mcp-garmin && poetry run python -c "import scripts.login"
```

Expected: no output (no errors).

**Step 3: Commit**

```bash
git add scripts/login.py
git commit -m "feat: add interactive login script for one-time token generation"
```

---

## Task 13: Static Analysis

Run all linters and type checkers and fix any issues.

**Step 1: Run ruff**

```bash
cd mcp-garmin && poetry run ruff check src/ tests/ scripts/ --fix
```

Fix any reported issues before proceeding.

**Step 2: Run mypy**

```bash
cd mcp-garmin && poetry run mypy src/
```

Fix any type errors before proceeding.

**Step 3: Run bandit**

```bash
cd mcp-garmin && poetry run bandit -c pyproject.toml -r src/
```

Fix any HIGH or MEDIUM severity issues before proceeding.

**Step 4: Run full test suite**

```bash
cd mcp-garmin && poetry run pytest tests/unit/ -v
```

Expected: all passed.

**Step 5: Commit any fixes**

```bash
git add -A
git commit -m "chore: fix linter and type checker issues"
```

---

## Task 14: Integration Tests

Write integration tests that call the real Garmin API, gated behind an env var.

**Files:**
- Write: `mcp-garmin/tests/integration/test_integration.py`

**Step 1: Implement integration tests**

Write `tests/integration/test_integration.py`:

```python
"""Integration tests — call the real Garmin API.

Run with:
    GARMIN_INTEGRATION_TESTS=1 poetry run pytest tests/integration/ -v

Requires tokens present in ~/.garminconnect (run scripts/login.py first).
"""

from __future__ import annotations

import os
import pytest
from mcp_garmin.client import get_client
import mcp_garmin.client as client_module

TODAY = "2026-02-20"
RANGE_START = "2026-02-01"
RANGE_END = "2026-02-20"

if not os.getenv("GARMIN_INTEGRATION_TESTS"):
    pytest.skip("Set GARMIN_INTEGRATION_TESTS=1 to run", allow_module_level=True)


@pytest.fixture(autouse=True)
def reset_client() -> None:
    client_module._client = None


def test_get_daily_stats_returns_data() -> None:
    from mcp_garmin.tools.daily import DISPATCH
    client = get_client()
    result = DISPATCH["get_daily_stats"](client, {"date": TODAY})
    assert result[0].text  # non-empty response


def test_get_heart_rate_returns_data() -> None:
    from mcp_garmin.tools.daily import DISPATCH
    client = get_client()
    result = DISPATCH["get_heart_rate"](client, {"date": TODAY})
    assert result[0].text


def test_get_sleep_returns_data() -> None:
    from mcp_garmin.tools.daily import DISPATCH
    client = get_client()
    result = DISPATCH["get_sleep"](client, {"date": TODAY})
    assert result[0].text


def test_get_activities_returns_data() -> None:
    from mcp_garmin.tools.activities import DISPATCH
    client = get_client()
    result = DISPATCH["get_activities"](client, {"start_date": RANGE_START, "end_date": RANGE_END})
    assert result[0].text


def test_get_hrv_returns_data() -> None:
    from mcp_garmin.tools.health import DISPATCH
    client = get_client()
    result = DISPATCH["get_hrv"](client, {"date": TODAY})
    assert result[0].text


def test_get_body_composition_returns_data() -> None:
    from mcp_garmin.tools.body import DISPATCH
    client = get_client()
    result = DISPATCH["get_body_composition"](client, {"start_date": RANGE_START, "end_date": RANGE_END})
    assert result[0].text


def test_get_hydration_returns_data() -> None:
    from mcp_garmin.tools.wellness import DISPATCH
    client = get_client()
    result = DISPATCH["get_hydration"](client, {"date": TODAY})
    assert result[0].text
```

**Step 2: Verify unit tests still pass (integration tests skipped)**

```bash
cd mcp-garmin && poetry run pytest tests/ -v
```

Expected: unit tests pass, integration tests skipped with "Set GARMIN_INTEGRATION_TESTS=1".

**Step 3: Commit**

```bash
git add tests/integration/test_integration.py
git commit -m "test: add integration test suite"
```

---

## Task 15: Final Verification

**Step 1: Run full linting pipeline**

```bash
cd mcp-garmin && poetry run ruff check src/ tests/ scripts/ && poetry run ruff format --check src/ tests/ scripts/
```

**Step 2: Run mypy**

```bash
cd mcp-garmin && poetry run mypy src/
```

**Step 3: Run bandit**

```bash
cd mcp-garmin && poetry run bandit -c pyproject.toml -r src/
```

**Step 4: Run unit tests**

```bash
cd mcp-garmin && poetry run pytest tests/unit/ -v
```

**Step 5: Verify server entrypoint is importable**

```bash
cd mcp-garmin && poetry run python -c "from mcp_garmin.server import main; print('OK')"
```

Expected: `OK`

**Step 6: Run pre-commit on all files**

```bash
cd /Users/samuelchapman/Projects/fitness-mcp-servers && poetry run pre-commit run --all-files
```

Expected: all checks pass.
