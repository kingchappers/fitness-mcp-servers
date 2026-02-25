# mcp-myfitnesspal Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a Python MCP server that gives Claude access to MyFitnessPal nutrition and weight data via three tools: `get_nutrition_diary`, `get_nutrition_summary`, and `get_weight_log`.

**Architecture:** Mirrors `mcp-garmin` exactly — Poetry project with `src/` layout, MCP stdio server, singleton client, per-module tool files with `TOOLS`/`DISPATCH`, and a one-time Playwright login script that saves browser cookies to a file. Auth uses `myfitnesspal.Client(cookiejar=jar)` with a `MozillaCookieJar` loaded from `MFP_COOKIE_PATH`.

**Tech Stack:** Python 3.12, `mcp>=1.26`, `myfitnesspal==2.1.1`, `playwright` (login script only), Poetry, pytest, ruff, mypy, bandit, pip-audit.

---

## Reference

Before each task, refer to the matching file in `mcp-garmin/` as the structural template:

| New file | Mirrors |
|----------|---------|
| `mcp-myfitnesspal/src/mcp_myfitnesspal/validation.py` | `mcp-garmin/src/mcp_garmin/validation.py` |
| `mcp-myfitnesspal/src/mcp_myfitnesspal/client.py` | `mcp-garmin/src/mcp_garmin/client.py` |
| `mcp-myfitnesspal/src/mcp_myfitnesspal/server.py` | `mcp-garmin/src/mcp_garmin/server.py` |
| `mcp-myfitnesspal/src/mcp_myfitnesspal/tools/__init__.py` | `mcp-garmin/src/mcp_garmin/tools/__init__.py` |

All commands run from inside `mcp-myfitnesspal/` via `poetry run`.

---

## Task 1: Scaffold project structure

**Files:**
- Create: `mcp-myfitnesspal/pyproject.toml`
- Create: `mcp-myfitnesspal/src/mcp_myfitnesspal/__init__.py`
- Create: `mcp-myfitnesspal/src/mcp_myfitnesspal/tools/__init__.py` (empty for now)
- Create: `mcp-myfitnesspal/tests/__init__.py`
- Create: `mcp-myfitnesspal/tests/unit/__init__.py`
- Create: `mcp-myfitnesspal/tests/unit/tools/__init__.py`

**Step 1: Create `pyproject.toml`**

```toml
[project]
name = "mcp-myfitnesspal"
version = "0.1.0"
description = ""
authors = [
    {name = "kingchappers", email = "sam.chapman@outlook.com"}
]
readme = "README.md"
requires-python = ">=3.12,<4.0"
dependencies = [
    "mcp (>=1.26.0,<2.0.0)",
    "myfitnesspal (==2.1.1)",
]

[project.scripts]
mcp-myfitnesspal = "mcp_myfitnesspal.server:main"

[tool.poetry]
packages = [{include = "mcp_myfitnesspal", from = "src"}]

[build-system]
requires = ["poetry-core>=2.0.0,<3.0.0"]
build-backend = "poetry.core.masonry.api"

[dependency-groups]
dev = [
    "ruff (>=0.15.1,<0.16.0)",
    "mypy (>=1.19.1,<2.0.0)",
    "pytest (>=9.0.2,<10.0.0)",
    "pytest-asyncio (>=1.3.0,<2.0.0)",
    "bandit (>=1.9.3,<2.0.0)",
    "pip-audit (>=2.10.0,<3.0.0)",
    "playwright (>=1.50.0,<2.0.0)",
]

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "W", "I", "N", "S", "B", "UP"]
ignore = ["S101"]

[tool.ruff.lint.per-file-ignores]
"tests/**" = ["S"]

[tool.mypy]
python_version = "3.12"
strict = true
warn_return_any = true
warn_unused_configs = true

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

[tool.bandit]
exclude_dirs = ["tests"]
skips = ["B101"]
```

**Step 2: Create empty `__init__.py` files**

Create these empty files:
- `src/mcp_myfitnesspal/__init__.py`
- `src/mcp_myfitnesspal/tools/__init__.py`
- `tests/__init__.py`
- `tests/unit/__init__.py`
- `tests/unit/tools/__init__.py`

**Step 3: Install dependencies**

```bash
cd mcp-myfitnesspal
poetry install
```

Expected: resolves without errors, lockfile created.

**Step 4: Verify ruff works**

```bash
cd mcp-myfitnesspal
poetry run ruff check src/
```

Expected: no output (nothing to lint yet).

**Step 5: Commit**

```bash
git add mcp-myfitnesspal/
git commit -m "chore: scaffold mcp-myfitnesspal project"
```

---

## Task 2: Validation helpers

**Files:**
- Create: `mcp-myfitnesspal/src/mcp_myfitnesspal/validation.py`
- Create: `mcp-myfitnesspal/tests/unit/test_validation.py`

**Step 1: Write the failing tests**

```python
# tests/unit/test_validation.py
import pytest
from mcp_myfitnesspal.validation import validate_date, validate_date_range


def test_validate_date_accepts_valid() -> None:
    validate_date("2026-02-25")  # should not raise


def test_validate_date_rejects_wrong_format() -> None:
    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        validate_date("25-02-2026")


def test_validate_date_rejects_invalid_calendar_date() -> None:
    with pytest.raises(ValueError):
        validate_date("2026-02-30")


def test_validate_date_range_accepts_valid() -> None:
    validate_date_range("2026-02-01", "2026-02-25")  # should not raise


def test_validate_date_range_rejects_reversed_range() -> None:
    with pytest.raises(ValueError, match="start_date"):
        validate_date_range("2026-02-25", "2026-02-01")


def test_validate_date_range_rejects_range_over_365_days() -> None:
    with pytest.raises(ValueError, match="365"):
        validate_date_range("2024-01-01", "2026-01-02")


def test_validate_date_range_rejects_bad_start_date() -> None:
    with pytest.raises(ValueError, match="start_date"):
        validate_date_range("bad", "2026-02-25")


def test_validate_date_range_rejects_bad_end_date() -> None:
    with pytest.raises(ValueError, match="end_date"):
        validate_date_range("2026-02-01", "bad")
```

**Step 2: Run tests to verify they fail**

```bash
cd mcp-myfitnesspal
poetry run pytest tests/unit/test_validation.py -v
```

Expected: `ImportError` — module does not exist yet.

**Step 3: Write the implementation**

```python
# src/mcp_myfitnesspal/validation.py
from __future__ import annotations

import re
from datetime import date as _date

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def validate_date(value: str, param_name: str = "date") -> None:
    """Raise ValueError if value is not a valid YYYY-MM-DD calendar date."""
    if not _DATE_RE.match(value):
        raise ValueError(f"Invalid {param_name}: {value!r}. Expected YYYY-MM-DD.")
    try:
        _date.fromisoformat(value)
    except ValueError as err:
        raise ValueError(
            f"Invalid {param_name}: {value!r}. Expected a real calendar date."
        ) from err


def validate_date_range(start: str, end: str) -> None:
    """Raise ValueError if start/end are not valid YYYY-MM-DD dates or range is invalid."""
    validate_date(start, param_name="start_date")
    validate_date(end, param_name="end_date")
    start_dt = _date.fromisoformat(start)
    end_dt = _date.fromisoformat(end)
    if start_dt > end_dt:
        raise ValueError(f"start_date {start!r} must be on or before end_date {end!r}.")
    if (end_dt - start_dt).days > 365:
        raise ValueError(f"Date range exceeds 365 days ({start} to {end}).")
```

**Step 4: Run tests to verify they pass**

```bash
cd mcp-myfitnesspal
poetry run pytest tests/unit/test_validation.py -v
```

Expected: all 8 tests PASS.

**Step 5: Commit**

```bash
git add mcp-myfitnesspal/src/mcp_myfitnesspal/validation.py mcp-myfitnesspal/tests/unit/test_validation.py
git commit -m "feat: add date validation helpers"
```

---

## Task 3: MFPShapeError exception

**Files:**
- Create: `mcp-myfitnesspal/src/mcp_myfitnesspal/exceptions.py`
- Create: `mcp-myfitnesspal/tests/unit/test_exceptions.py`

**Step 1: Write the failing tests**

```python
# tests/unit/test_exceptions.py
import pytest
from mcp_myfitnesspal.exceptions import MFPShapeError, validate_day_shape


def test_mfp_shape_error_is_exception() -> None:
    err = MFPShapeError("test")
    assert isinstance(err, Exception)


def test_validate_day_shape_passes_valid_object() -> None:
    class FakeDay:
        meals = []
        totals = {}
        goals = {}

    validate_day_shape(FakeDay(), "2026-02-25")  # should not raise


def test_validate_day_shape_raises_on_missing_attr() -> None:
    class BrokenDay:
        meals = []
        # missing totals and goals

    with pytest.raises(MFPShapeError, match="totals"):
        validate_day_shape(BrokenDay(), "2026-02-25")


def test_validate_day_shape_error_message_mentions_mfp() -> None:
    class BrokenDay:
        pass

    with pytest.raises(MFPShapeError, match="MyFitnessPal"):
        validate_day_shape(BrokenDay(), "2026-02-25")
```

**Step 2: Run tests to verify they fail**

```bash
cd mcp-myfitnesspal
poetry run pytest tests/unit/test_exceptions.py -v
```

Expected: `ImportError`.

**Step 3: Write the implementation**

```python
# src/mcp_myfitnesspal/exceptions.py
from __future__ import annotations


class MFPShapeError(Exception):
    """Raised when a MyFitnessPal response is missing expected fields.

    This typically means MyFitnessPal changed their HTML structure.
    The fix is to update the python-myfitnesspal library.
    """


_DAY_ATTRS = ("meals", "totals", "goals")


def validate_day_shape(day: object, date: str) -> None:
    """Raise MFPShapeError if the Day object is missing expected attributes."""
    missing = [attr for attr in _DAY_ATTRS if not hasattr(day, attr)]
    if missing:
        raise MFPShapeError(
            f"MFP response for {date} is missing fields: {missing}. "
            "MyFitnessPal may have changed their format — "
            "check for python-myfitnesspal updates."
        )
```

**Step 4: Run tests to verify they pass**

```bash
cd mcp-myfitnesspal
poetry run pytest tests/unit/test_exceptions.py -v
```

Expected: all 4 tests PASS.

**Step 5: Commit**

```bash
git add mcp-myfitnesspal/src/mcp_myfitnesspal/exceptions.py mcp-myfitnesspal/tests/unit/test_exceptions.py
git commit -m "feat: add MFPShapeError and day shape validation"
```

---

## Task 4: Client singleton

**Files:**
- Create: `mcp-myfitnesspal/src/mcp_myfitnesspal/client.py`
- Create: `mcp-myfitnesspal/tests/unit/test_client.py`

**Step 1: Write the failing tests**

```python
# tests/unit/test_client.py
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from mcp_myfitnesspal.client import _reset_client, get_client


def test_get_client_raises_if_env_var_not_set() -> None:
    _reset_client()
    env = {k: v for k, v in os.environ.items() if k != "MFP_COOKIE_PATH"}
    with patch.dict(os.environ, env, clear=True):
        with pytest.raises(RuntimeError, match="MFP_COOKIE_PATH"):
            get_client()


def test_get_client_raises_if_file_not_found(tmp_path: Path) -> None:
    _reset_client()
    missing = str(tmp_path / "missing.txt")
    with patch.dict(os.environ, {"MFP_COOKIE_PATH": missing}):
        with pytest.raises(RuntimeError, match="not found"):
            get_client()


def test_get_client_raises_if_permissions_too_open(tmp_path: Path) -> None:
    _reset_client()
    cookie_file = tmp_path / "cookies.txt"
    cookie_file.write_text("# Netscape HTTP Cookie File\n")
    cookie_file.chmod(0o644)
    with patch.dict(os.environ, {"MFP_COOKIE_PATH": str(cookie_file)}):
        with pytest.raises(RuntimeError, match="[Pp]ermission"):
            get_client()


def test_get_client_returns_singleton(tmp_path: Path) -> None:
    _reset_client()
    cookie_file = tmp_path / "cookies.txt"
    cookie_file.write_text("# Netscape HTTP Cookie File\n")
    cookie_file.chmod(0o600)
    with patch.dict(os.environ, {"MFP_COOKIE_PATH": str(cookie_file)}):
        with patch("mcp_myfitnesspal.client.myfitnesspal.Client") as mock_cls:
            mock_cls.return_value = MagicMock()
            c1 = get_client()
            c2 = get_client()
            assert c1 is c2
            mock_cls.assert_called_once()
```

**Step 2: Run tests to verify they fail**

```bash
cd mcp-myfitnesspal
poetry run pytest tests/unit/test_client.py -v
```

Expected: `ImportError`.

**Step 3: Write the implementation**

```python
# src/mcp_myfitnesspal/client.py
from __future__ import annotations

import http.cookiejar
import logging
import os
from pathlib import Path

import myfitnesspal  # type: ignore[import-untyped]

logger = logging.getLogger(__name__)

_client: myfitnesspal.Client | None = None


def get_client() -> myfitnesspal.Client:
    """Return the authenticated MFP singleton, creating it on first call."""
    global _client
    if _client is None:
        _client = _create_client()
    return _client


def _reset_client() -> None:
    """Reset the singleton. Used in tests only."""
    global _client
    _client = None


def _create_client() -> myfitnesspal.Client:
    cookie_path_str = os.environ.get("MFP_COOKIE_PATH")
    if not cookie_path_str:
        raise RuntimeError(
            "MFP_COOKIE_PATH is not set. "
            "Run scripts/login.py to generate a cookie file, then set MFP_COOKIE_PATH."
        )

    cookie_path = Path(cookie_path_str)
    if not cookie_path.exists():
        raise RuntimeError(
            f"Cookie file not found at {cookie_path}. Run scripts/login.py to generate it."
        )

    file_mode = cookie_path.stat().st_mode & 0o777
    if file_mode & 0o077:
        raise RuntimeError(
            f"Cookie file {cookie_path} has insecure permissions ({oct(file_mode)}). "
            f"Run: chmod 600 {cookie_path}"
        )

    jar = http.cookiejar.MozillaCookieJar()
    jar.load(str(cookie_path), ignore_discard=True, ignore_expires=True)

    logger.info("MFP client authenticated from cookie file at %s", cookie_path)
    return myfitnesspal.Client(cookiejar=jar)
```

**Step 4: Run tests to verify they pass**

```bash
cd mcp-myfitnesspal
poetry run pytest tests/unit/test_client.py -v
```

Expected: all 4 tests PASS.

**Step 5: Commit**

```bash
git add mcp-myfitnesspal/src/mcp_myfitnesspal/client.py mcp-myfitnesspal/tests/unit/test_client.py
git commit -m "feat: add MFP client singleton with cookie auth"
```

---

## Task 5: Nutrition tools

**Files:**
- Create: `mcp-myfitnesspal/src/mcp_myfitnesspal/tools/nutrition.py`
- Create: `mcp-myfitnesspal/tests/unit/tools/test_nutrition.py`

### Library API summary

`client.get_date(date)` returns a `Day` object. Serialise it as:
```python
{
    "date": "2026-02-25",
    "meals": day.get_as_dict(),   # {"Breakfast": [{"name": "...", "nutrition_information": {...}}]}
    "totals": day.totals,          # {"calories": 2000.0, "protein": 150.0, ...}
    "goals": day.goals,            # {"calories": 2200.0, "protein": 160.0, ...}
    "water": day.water,            # float
    "complete": day.complete,      # bool
}
```

`get_nutrition_summary` iterates the date range (max 365 days) returning one `{"date", "totals"}` row per day.

**Step 1: Write the failing tests**

```python
# tests/unit/tools/test_nutrition.py
import json
from datetime import date
from unittest.mock import MagicMock

import pytest

from mcp_myfitnesspal.exceptions import MFPShapeError
from mcp_myfitnesspal.tools.nutrition import DISPATCH, TOOLS


def make_fake_day(
    date_val: date = date(2026, 2, 25),
    totals: dict | None = None,
    goals: dict | None = None,
    water: float = 500.0,
    complete: bool = False,
) -> MagicMock:
    day = MagicMock()
    day.date = date_val
    day.totals = totals or {"calories": 2000.0, "protein": 150.0}
    day.goals = goals or {"calories": 2200.0, "protein": 160.0}
    day.water = water
    day.complete = complete
    day.get_as_dict.return_value = {
        "Breakfast": [{"name": "Oats", "nutrition_information": {"calories": 300.0}}]
    }
    return day


def make_client(day: MagicMock) -> MagicMock:
    client = MagicMock()
    client.get_date.return_value = day
    return client


# --- get_nutrition_diary ---


def test_get_nutrition_diary_calls_get_date() -> None:
    day = make_fake_day()
    client = make_client(day)
    DISPATCH["get_nutrition_diary"](client, {"date": "2026-02-25"})
    client.get_date.assert_called_once_with(date(2026, 2, 25))


def test_get_nutrition_diary_returns_meals_and_totals() -> None:
    day = make_fake_day()
    client = make_client(day)
    result = DISPATCH["get_nutrition_diary"](client, {"date": "2026-02-25"})
    data = json.loads(result[0].text)
    assert data["totals"]["calories"] == 2000.0
    assert "Breakfast" in data["meals"]
    assert data["goals"]["calories"] == 2200.0
    assert data["water"] == 500.0
    assert data["complete"] is False


def test_get_nutrition_diary_rejects_bad_date() -> None:
    client = MagicMock()
    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        DISPATCH["get_nutrition_diary"](client, {"date": "bad"})


def test_get_nutrition_diary_raises_shape_error_on_broken_response() -> None:
    client = MagicMock()
    client.get_date.return_value = object()  # missing meals/totals/goals
    with pytest.raises(MFPShapeError):
        DISPATCH["get_nutrition_diary"](client, {"date": "2026-02-25"})


# --- get_nutrition_summary ---


def test_get_nutrition_summary_returns_one_row_per_day() -> None:
    day = make_fake_day()
    client = make_client(day)
    result = DISPATCH["get_nutrition_summary"](
        client, {"start_date": "2026-02-25", "end_date": "2026-02-25"}
    )
    data = json.loads(result[0].text)
    assert len(data) == 1
    assert data[0]["date"] == "2026-02-25"
    assert data[0]["totals"]["calories"] == 2000.0


def test_get_nutrition_summary_iterates_range() -> None:
    day = make_fake_day()
    client = make_client(day)
    DISPATCH["get_nutrition_summary"](
        client, {"start_date": "2026-02-01", "end_date": "2026-02-03"}
    )
    assert client.get_date.call_count == 3


def test_get_nutrition_summary_rejects_bad_dates() -> None:
    client = MagicMock()
    with pytest.raises(ValueError, match="start_date"):
        DISPATCH["get_nutrition_summary"](
            client, {"start_date": "bad", "end_date": "2026-02-25"}
        )


# --- TOOLS list ---


def test_tools_list_contains_both_tools() -> None:
    names = {t.name for t in TOOLS}
    assert names == {"get_nutrition_diary", "get_nutrition_summary"}
```

**Step 2: Run tests to verify they fail**

```bash
cd mcp-myfitnesspal
poetry run pytest tests/unit/tools/test_nutrition.py -v
```

Expected: `ImportError`.

**Step 3: Write the implementation**

```python
# src/mcp_myfitnesspal/tools/nutrition.py
from __future__ import annotations

import json
from collections.abc import Callable
from datetime import date, timedelta
from typing import Any

import myfitnesspal  # type: ignore[import-untyped]
from mcp.types import TextContent, Tool

from mcp_myfitnesspal.exceptions import validate_day_shape
from mcp_myfitnesspal.validation import validate_date, validate_date_range


def _json_result(data: Any) -> list[TextContent]:
    return [TextContent(type="text", text=json.dumps(data, indent=2))]


def _serialise_day(day: Any, date_str: str) -> dict[str, Any]:
    validate_day_shape(day, date_str)
    return {
        "date": date_str,
        "meals": day.get_as_dict(),
        "totals": day.totals,
        "goals": day.goals,
        "water": day.water,
        "complete": day.complete,
    }


def get_nutrition_diary(
    client: myfitnesspal.Client, arguments: dict[str, str]
) -> list[TextContent]:
    date_str = arguments["date"]
    validate_date(date_str)
    day = client.get_date(date.fromisoformat(date_str))
    return _json_result(_serialise_day(day, date_str))


def get_nutrition_summary(
    client: myfitnesspal.Client, arguments: dict[str, str]
) -> list[TextContent]:
    start_str = arguments["start_date"]
    end_str = arguments["end_date"]
    validate_date_range(start_str, end_str)
    current = date.fromisoformat(start_str)
    end = date.fromisoformat(end_str)
    rows = []
    while current <= end:
        day = client.get_date(current)
        validate_day_shape(day, str(current))
        rows.append({"date": str(current), "totals": day.totals})
        current += timedelta(days=1)
    return _json_result(rows)


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


def _date_range_tool(name: str, description: str) -> Tool:
    return Tool(
        name=name,
        description=description,
        inputSchema={
            "type": "object",
            "properties": {
                "start_date": {
                    "type": "string",
                    "description": "Start date in YYYY-MM-DD format",
                },
                "end_date": {"type": "string", "description": "End date in YYYY-MM-DD format"},
            },
            "required": ["start_date", "end_date"],
        },
    )


TOOLS: list[Tool] = [
    _date_tool(
        "get_nutrition_diary",
        "Full diary for a single day: meals, foods, calories, macros, and daily totals vs goals.",
    ),
    _date_range_tool(
        "get_nutrition_summary",
        "Aggregated daily nutrition totals over a date range. One row per day.",
    ),
]

DISPATCH: dict[str, Callable[[myfitnesspal.Client, dict[str, str]], list[TextContent]]] = {
    "get_nutrition_diary": get_nutrition_diary,
    "get_nutrition_summary": get_nutrition_summary,
}
```

**Step 4: Run tests to verify they pass**

```bash
cd mcp-myfitnesspal
poetry run pytest tests/unit/tools/test_nutrition.py -v
```

Expected: all 8 tests PASS.

**Step 5: Commit**

```bash
git add mcp-myfitnesspal/src/mcp_myfitnesspal/tools/nutrition.py mcp-myfitnesspal/tests/unit/tools/test_nutrition.py
git commit -m "feat: add get_nutrition_diary and get_nutrition_summary tools"
```

---

## Task 6: Body tools

**Files:**
- Create: `mcp-myfitnesspal/src/mcp_myfitnesspal/tools/body.py`
- Create: `mcp-myfitnesspal/tests/unit/tools/test_body.py`

### Library API

`client.get_measurements("Weight", lower_bound, upper_bound)` returns `dict[datetime.date, float]`.
Serialise as `[{"date": "2026-02-25", "weight": 82.5}, ...]` sorted by date.

**Step 1: Write the failing tests**

```python
# tests/unit/tools/test_body.py
import json
from datetime import date
from unittest.mock import MagicMock

import pytest

from mcp_myfitnesspal.tools.body import DISPATCH, TOOLS


def make_client(measurements: dict) -> MagicMock:
    client = MagicMock()
    client.get_measurements.return_value = measurements
    return client


def test_get_weight_log_calls_get_measurements() -> None:
    client = make_client({date(2026, 2, 25): 82.5})
    DISPATCH["get_weight_log"](client, {"start_date": "2026-02-20", "end_date": "2026-02-25"})
    client.get_measurements.assert_called_once_with(
        "Weight",
        date(2026, 2, 20),
        date(2026, 2, 25),
    )


def test_get_weight_log_returns_list_of_entries() -> None:
    client = make_client({date(2026, 2, 25): 82.5, date(2026, 2, 24): 82.8})
    result = DISPATCH["get_weight_log"](
        client, {"start_date": "2026-02-24", "end_date": "2026-02-25"}
    )
    data = json.loads(result[0].text)
    assert len(data) == 2
    weights = {row["date"]: row["weight"] for row in data}
    assert weights["2026-02-25"] == 82.5
    assert weights["2026-02-24"] == 82.8


def test_get_weight_log_returns_empty_list_when_no_data() -> None:
    client = make_client({})
    result = DISPATCH["get_weight_log"](
        client, {"start_date": "2026-02-20", "end_date": "2026-02-25"}
    )
    data = json.loads(result[0].text)
    assert data == []


def test_get_weight_log_rejects_bad_start_date() -> None:
    client = MagicMock()
    with pytest.raises(ValueError, match="start_date"):
        DISPATCH["get_weight_log"](client, {"start_date": "bad", "end_date": "2026-02-25"})


def test_get_weight_log_rejects_bad_end_date() -> None:
    client = MagicMock()
    with pytest.raises(ValueError, match="end_date"):
        DISPATCH["get_weight_log"](client, {"start_date": "2026-02-01", "end_date": "bad"})


def test_tools_list_contains_get_weight_log() -> None:
    names = {t.name for t in TOOLS}
    assert "get_weight_log" in names
```

**Step 2: Run tests to verify they fail**

```bash
cd mcp-myfitnesspal
poetry run pytest tests/unit/tools/test_body.py -v
```

Expected: `ImportError`.

**Step 3: Write the implementation**

```python
# src/mcp_myfitnesspal/tools/body.py
from __future__ import annotations

import json
from collections.abc import Callable
from datetime import date
from typing import Any

import myfitnesspal  # type: ignore[import-untyped]
from mcp.types import TextContent, Tool

from mcp_myfitnesspal.validation import validate_date_range


def _json_result(data: Any) -> list[TextContent]:
    return [TextContent(type="text", text=json.dumps(data, indent=2))]


def get_weight_log(
    client: myfitnesspal.Client, arguments: dict[str, str]
) -> list[TextContent]:
    start_str = arguments["start_date"]
    end_str = arguments["end_date"]
    validate_date_range(start_str, end_str)
    measurements = client.get_measurements(
        "Weight",
        date.fromisoformat(start_str),
        date.fromisoformat(end_str),
    )
    entries = [{"date": str(d), "weight": w} for d, w in sorted(measurements.items())]
    return _json_result(entries)


TOOLS: list[Tool] = [
    Tool(
        name="get_weight_log",
        description="Weight log entries over a date range.",
        inputSchema={
            "type": "object",
            "properties": {
                "start_date": {
                    "type": "string",
                    "description": "Start date in YYYY-MM-DD format",
                },
                "end_date": {"type": "string", "description": "End date in YYYY-MM-DD format"},
            },
            "required": ["start_date", "end_date"],
        },
    ),
]

DISPATCH: dict[str, Callable[[myfitnesspal.Client, dict[str, str]], list[TextContent]]] = {
    "get_weight_log": get_weight_log,
}
```

**Step 4: Run tests to verify they pass**

```bash
cd mcp-myfitnesspal
poetry run pytest tests/unit/tools/test_body.py -v
```

Expected: all 6 tests PASS.

**Step 5: Commit**

```bash
git add mcp-myfitnesspal/src/mcp_myfitnesspal/tools/body.py mcp-myfitnesspal/tests/unit/tools/test_body.py
git commit -m "feat: add get_weight_log tool"
```

---

## Task 7: Tools aggregator

**Files:**
- Modify: `mcp-myfitnesspal/src/mcp_myfitnesspal/tools/__init__.py`
- Create: `mcp-myfitnesspal/tests/unit/tools/test_aggregator.py`

**Step 1: Write the failing test**

```python
# tests/unit/tools/test_aggregator.py
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
```

**Step 2: Run tests to verify they fail**

```bash
cd mcp-myfitnesspal
poetry run pytest tests/unit/tools/test_aggregator.py -v
```

Expected: `ImportError` (tools `__init__.py` is empty).

**Step 3: Write the implementation**

```python
# src/mcp_myfitnesspal/tools/__init__.py
from collections.abc import Callable

import myfitnesspal  # type: ignore[import-untyped]
from mcp.types import TextContent, Tool

from mcp_myfitnesspal.tools.body import DISPATCH as _BODY_DISPATCH
from mcp_myfitnesspal.tools.body import TOOLS as _BODY_TOOLS
from mcp_myfitnesspal.tools.nutrition import DISPATCH as _NUTRITION_DISPATCH
from mcp_myfitnesspal.tools.nutrition import TOOLS as _NUTRITION_TOOLS

ALL_TOOLS: list[Tool] = _NUTRITION_TOOLS + _BODY_TOOLS

DISPATCH: dict[str, Callable[[myfitnesspal.Client, dict[str, str]], list[TextContent]]] = {
    **_NUTRITION_DISPATCH,
    **_BODY_DISPATCH,
}
```

**Step 4: Run tests to verify they pass**

```bash
cd mcp-myfitnesspal
poetry run pytest tests/unit/tools/test_aggregator.py -v
```

Expected: all 3 tests PASS.

**Step 5: Run the full test suite**

```bash
cd mcp-myfitnesspal
poetry run pytest tests/unit/ -v
```

Expected: all tests PASS.

**Step 6: Commit**

```bash
git add mcp-myfitnesspal/src/mcp_myfitnesspal/tools/__init__.py mcp-myfitnesspal/tests/unit/tools/test_aggregator.py
git commit -m "feat: add tools aggregator"
```

---

## Task 8: MCP server entrypoint

**Files:**
- Create: `mcp-myfitnesspal/src/mcp_myfitnesspal/server.py`

No unit tests — thin wiring layer verified by the import check below.

**Step 1: Write the implementation**

```python
# src/mcp_myfitnesspal/server.py
from __future__ import annotations

import asyncio
import logging

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from mcp_myfitnesspal import tools
from mcp_myfitnesspal.client import get_client
from mcp_myfitnesspal.exceptions import MFPShapeError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

server: Server = Server("mcp-myfitnesspal")


@server.list_tools()  # type: ignore[no-untyped-call, untyped-decorator]
async def list_tools() -> list[Tool]:
    return tools.ALL_TOOLS


@server.call_tool()  # type: ignore[untyped-decorator]
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
    except MFPShapeError as exc:
        logger.error("MFP shape error in tool %s: %s", name, exc)
        return [TextContent(type="text", text=str(exc))]
    except ValueError as exc:
        logger.error("Validation error in tool %s: %s", name, exc)
        return [TextContent(type="text", text=f"Invalid argument: {exc}")]
    except Exception as exc:
        logger.error("Unexpected error in tool %s: %s", name, exc, exc_info=True)
        return [TextContent(type="text", text=f"Unexpected error: {exc}")]


async def _run() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def main() -> None:
    asyncio.run(_run())


if __name__ == "__main__":
    main()
```

**Step 2: Verify the entrypoint is importable**

```bash
cd mcp-myfitnesspal
poetry run python -c "from mcp_myfitnesspal.server import main; print('OK')"
```

Expected: `OK`.

**Step 3: Commit**

```bash
git add mcp-myfitnesspal/src/mcp_myfitnesspal/server.py
git commit -m "feat: add MCP server entrypoint"
```

---

## Task 9: Playwright login script

**Files:**
- Create: `mcp-myfitnesspal/scripts/login.py`

**Step 1: Install the Playwright browser binary (one-time)**

```bash
cd mcp-myfitnesspal
poetry run playwright install chromium
```

Expected: Chromium downloaded to Playwright's cache.

**Step 2: Write the script**

```python
#!/usr/bin/env python3
"""One-time MyFitnessPal authentication via browser.

Opens a Chromium window. Log in to MyFitnessPal, then press Enter.
Saves cookies to the path set by MFP_COOKIE_PATH (default: ~/.mfp/cookies.txt).
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

MFP_URL = "https://www.myfitnesspal.com/account/login"
DEFAULT_COOKIE_PATH = Path.home() / ".mfp" / "cookies.txt"


def main() -> None:
    cookie_path = Path(os.environ.get("MFP_COOKIE_PATH", str(DEFAULT_COOKIE_PATH)))

    print("MyFitnessPal — one-time login")
    print(f"Cookies will be saved to: {cookie_path}")
    print()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto(MFP_URL)

        print("A browser window has opened.")
        print("Log in to MyFitnessPal, then press Enter here to save your cookies.")
        input()

        pw_cookies = context.cookies()
        browser.close()

    if not pw_cookies:
        print("No cookies captured. Did you log in?", file=sys.stderr)
        sys.exit(1)

    cookie_path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    _write_netscape_cookies(pw_cookies, cookie_path)
    cookie_path.chmod(0o600)

    print(f"\nCookies saved to {cookie_path}")
    print("Set MFP_COOKIE_PATH to this path and run the MCP server.")


def _write_netscape_cookies(cookies: list[dict], path: Path) -> None:
    """Write Playwright cookies to Netscape format (readable by MozillaCookieJar)."""
    lines = ["# Netscape HTTP Cookie File\n"]
    for c in cookies:
        domain = c.get("domain", "")
        flag = "TRUE" if domain.startswith(".") else "FALSE"
        path_val = c.get("path", "/")
        secure = "TRUE" if c.get("secure", False) else "FALSE"
        expires = int(c.get("expires", 0))
        if expires < 0:
            expires = 2147483647  # session cookies: use far-future expiry
        name = c.get("name", "")
        value = c.get("value", "")
        lines.append(f"{domain}\t{flag}\t{path_val}\t{secure}\t{expires}\t{name}\t{value}\n")
    path.write_text("".join(lines))


if __name__ == "__main__":
    main()
```

**Step 3: Verify the script lints cleanly**

```bash
cd mcp-myfitnesspal
poetry run ruff check scripts/login.py
```

Expected: no errors.

**Step 4: Commit**

```bash
git add mcp-myfitnesspal/scripts/login.py
git commit -m "feat: add Playwright login script for MFP cookie extraction"
```

---

## Task 10: Polish, verify, and README

**Files:**
- Create: `mcp-myfitnesspal/README.md`

**Step 1: Run the full test suite**

```bash
cd mcp-myfitnesspal
poetry run pytest tests/unit/ -v
```

Expected: all tests PASS.

**Step 2: Ruff lint + format**

```bash
cd mcp-myfitnesspal
poetry run ruff check src/ scripts/
poetry run ruff format --check src/ scripts/
```

If format check fails, auto-fix with: `poetry run ruff format src/ scripts/`

**Step 3: Type check**

```bash
cd mcp-myfitnesspal
poetry run mypy src/
```

`myfitnesspal` is untyped — its imports already have `# type: ignore[import-untyped]` in the code above. Fix any remaining errors.

**Step 4: Security scan**

```bash
cd mcp-myfitnesspal
poetry run bandit -r src/
poetry run pip-audit
```

Expected: no high-severity findings.

**Step 5: Write README**

Model it on `mcp-garmin/README.md`. Sections:

1. One-paragraph description
2. **Setup:**
   - Prerequisites (Python 3.12+, Poetry, Chromium via Playwright)
   - Step 1: `poetry install && poetry run playwright install chromium`
   - Step 2: `poetry run python scripts/login.py` → set `MFP_COOKIE_PATH`
   - Step 3: `claude mcp add myfitnesspal -- /path/to/poetry --directory /path/to/mcp-myfitnesspal run mcp-myfitnesspal`
3. **Tools table** (3 tools)
4. **Development commands**
5. **Troubleshooting**: cookies expired (re-run login.py), MFP format changed (update library)

**Step 6: Final commit**

```bash
git add mcp-myfitnesspal/README.md
git commit -m "docs: add mcp-myfitnesspal README"
```

---

## Final verification

Run all checks before raising a PR:

```bash
cd mcp-myfitnesspal
poetry run pytest tests/unit/ -v
poetry run ruff check src/ scripts/
poetry run ruff format --check src/ scripts/
poetry run mypy src/
poetry run bandit -r src/
poetry run pip-audit
```

All commands must exit 0.
