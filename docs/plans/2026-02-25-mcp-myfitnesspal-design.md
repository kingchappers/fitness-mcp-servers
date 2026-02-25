# mcp-myfitnesspal Design

**Date:** 2026-02-25
**Status:** Approved

## Overview

A Python MCP server that gives Claude access to MyFitnessPal nutrition and weight data. Follows the same structure and conventions as `mcp-garmin`.

## Directory Layout

```
mcp-myfitnesspal/
├── pyproject.toml
├── README.md
├── scripts/
│   └── login.py              # Playwright: open browser → user logs in → save cookies
└── src/mcp_myfitnesspal/
    ├── __init__.py
    ├── server.py             # MCP stdio entrypoint
    ├── client.py             # get_client() singleton, loads cookie file
    ├── validation.py         # validate_date / validate_date_range
    ├── exceptions.py         # MFPShapeError
    └── tools/
        ├── __init__.py       # ALL_TOOLS + DISPATCH aggregator
        ├── nutrition.py      # get_nutrition_diary, get_nutrition_summary
        └── body.py           # get_weight_log
```

CI auto-discovers this directory via `pyproject.toml` — no workflow changes needed.

## Tools

| Tool | Parameters | Library call | Notes |
|------|-----------|-------------|-------|
| `get_nutrition_diary` | `date` | `client.get_date(date)` | Meals, per-food entries, daily totals, goals |
| `get_nutrition_summary` | `start_date`, `end_date` | `client.get_date()` × N days | Iterates range, returns one totals row per day |
| `get_weight_log` | `start_date`, `end_date` | `client.get_measurements("Weight", start, end)` | Returns `{date: weight}` dict |

## Authentication

**Approach:** Playwright-assisted cookie extraction (Approach B).

MFP added a CAPTCHA to their login in August 2022, making credential-based auth impossible. The `python-myfitnesspal` library uses `browser_cookie3` to read from the live browser, or accepts an explicit `CookieJar`. We use the explicit `CookieJar` path for reliability in subprocesses.

### Login script (`scripts/login.py`)

1. Launch Playwright in headed (non-headless) mode
2. Navigate to `https://www.myfitnesspal.com/account/login`
3. Wait for user to log in manually
4. Extract cookies from the page context
5. Write to Netscape-format `.txt` file at `MFP_COOKIE_PATH`
6. Set file permissions to `0o600`

Re-run when cookies expire (~30 days).

### Runtime (`client.py`)

```python
jar = http.cookiejar.MozillaCookieJar()
jar.load(MFP_COOKIE_PATH, ignore_discard=True, ignore_expires=True)
client = myfitnesspal.Client(cookiejar=jar)
```

`MFP_COOKIE_PATH` is required. Server exits with a clear `RuntimeError` if unset or file missing.

## Error Handling

### MFP shape validation

`python-myfitnesspal` is fragile — MFP can change their HTML without notice. Each tool validates the shape of the library response before returning:

```python
class MFPShapeError(Exception):
    """Raised when MFP response is missing expected fields."""

def _validate_day(day: object, date: str) -> None:
    for attr in ("meals", "totals", "goals"):
        if not hasattr(day, attr):
            raise MFPShapeError(
                f"MFP response for {date} is missing '{attr}'. "
                "MyFitnessPal may have changed their format — "
                "check for python-myfitnesspal updates."
            )
```

The server catches `MFPShapeError` and returns a clear text message to Claude rather than an opaque traceback.

### Server error hierarchy

| Exception | Meaning | User message |
|-----------|---------|-------------|
| `RuntimeError` | Auth failure (cookie file missing/invalid) | "MFP cookies not found. Run scripts/login.py." |
| `MFPShapeError` | MFP changed their format | "MFP data format has changed. Check for library updates." |
| `ValueError` | Bad date parameter | "Invalid argument: ..." |
| `Exception` | Unexpected error | "Unexpected error: ..." |

## Response Size

MFP diary data contains no per-epoch time-series arrays (unlike Garmin sleep data), so no stripping is needed. A diary with many food entries is verbose but bounded — a day with 20 foods is roughly 5–10 KB. Monitor if it becomes a problem.

## Testing

Unit tests mock `myfitnesspal.Client` using the same `make_client()` pattern as mcp-garmin. No real MFP calls in CI. Tests cover:

- Correct library methods called with correct arguments
- JSON output shape
- Date validation rejection
- `MFPShapeError` raised on missing fields
- `TOOLS` list contains expected tool names

## Security

- `MFP_COOKIE_PATH` loaded from environment variable only — never hardcoded
- Cookie file must exist and have `0o600` permissions; server raises `RuntimeError` otherwise
- All date parameters validated with `validate_date` / `validate_date_range` before use
- No `eval`, `exec`, or `shell=True`
- Dependencies pinned in `pyproject.toml`; `pip-audit` runs in CI
