# New Garmin Tools Design

Date: 2026-03-17

## Overview

Add 4 new tools to `mcp-garmin`: `get_personal_records`, `get_body_battery`,
`get_activity_details`, and `get_menstrual_cycle`.

## Tools

### get_personal_records
- **File:** `goals.py`
- **Parameters:** none
- **Returns:** All personal records (best times/distances for running, cycling, etc.)
- **Garmin method:** `client.get_personal_record()`
- **Response size:** Expected small; no summarization needed

### get_body_battery
- **File:** `daily.py`
- **Parameters:** `date` (YYYY-MM-DD)
- **Returns:** Body battery charge/drain throughout the day
- **Garmin method:** `client.get_body_battery(date)`
- **Response size:** May contain time-series; add `_summarize_body_battery` if > 20 000 chars

### get_activity_details
- **File:** `activities.py`
- **Parameters:** `activity_id` (string)
- **Returns:** Full data for a specific activity: splits, laps, HR zones
- **Garmin method:** `client.get_activity_details(activity_id)`
- **Response size:** Likely large (per-sample GPS/HR arrays). Must add `_summarize_activity_details` to strip time-series samples; retain summary stats, laps, and HR zone breakdowns.

### get_menstrual_cycle
- **File:** `health.py`
- **Parameters:** `start_date`, `end_date` (YYYY-MM-DD)
- **Returns:** Menstrual cycle data over the date range
- **Garmin method:** `client.get_menstrual_data(start_date, end_date)`
- **Response size:** Expected moderate; check after first real call

## Placement (Option A — add to existing files)

| Tool | File | Reason |
|------|------|--------|
| `get_personal_records` | `goals.py` | Fits with race predictions and endurance score |
| `get_body_battery` | `daily.py` | Daily wellness metric alongside HR and sleep |
| `get_activity_details` | `activities.py` | Natural companion to `get_activities` |
| `get_menstrual_cycle` | `health.py` | Health metric alongside HRV, stress, training readiness |

## Registration

Each tool's `TOOLS` and `DISPATCH` entries are already aggregated in `tools/__init__.py`.
New tools in existing files are picked up automatically — no changes to `__init__.py` needed.

## Response Size Policy

Per `CLAUDE.md`:
- Check `len(json.dumps(data))` after first real call
- < 20 000 chars: fine
- 20 000–100 000: consider filtering
- > 100 000: must reduce before tool is usable

`get_activity_details` is the highest-risk tool. Strip per-sample arrays (GPS coordinates,
HR samples, speed samples) and keep: summary stats, laps array, HR zone breakdowns.

## Testing

Follow the existing pattern:
- Unit tests mock the Garmin client
- Test that each handler calls the correct client method with validated args
- For `get_activity_details`: test that `_summarize_activity_details` strips sample arrays
  and retains lap/zone data
- Tests live in `tests/unit/tools/` alongside existing test files
