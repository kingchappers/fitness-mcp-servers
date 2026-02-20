# mcp-garmin Design

Date: 2026-02-20

## Overview

An MCP server providing Claude with real-time access to Garmin Connect data via the
`python-garminconnect` library. Claude calls tools exposed by this server to retrieve fitness,
health, and activity data.

## Package Structure

```
mcp-garmin/
├── scripts/
│   └── login.py               # One-time interactive token generation
├── src/mcp_garmin/
│   ├── __init__.py
│   ├── server.py              # MCP entry point: list_tools + call_tool dispatch
│   ├── client.py              # Garmin auth, client singleton, token loading
│   └── tools/
│       ├── __init__.py        # Aggregates Tool definitions + dispatch map
│       ├── daily.py           # Daily Health & Activity
│       ├── activities.py      # Activities & Workouts
│       ├── health.py          # Advanced Health Metrics
│       ├── body.py            # Body Composition & Weight
│       ├── goals.py           # Goals & Achievements
│       └── wellness.py        # Hydration & Wellness
└── tests/
    ├── unit/                  # Mocked tests, always run
    └── integration/           # Real API tests, gated behind env var
```

Tool modules follow the category structure from the `python-garminconnect` README, making it
easy to add tools from new domains by adding a new module.

## Tools (17 total)

| Module | MCP Tool Name | garminconnect method |
|---|---|---|
| `daily.py` | `get_daily_stats` | `get_stats` |
| `daily.py` | `get_heart_rate` | `get_heart_rates` |
| `daily.py` | `get_sleep` | `get_sleep_data` |
| `activities.py` | `get_activities` | `get_activities_by_date` |
| `health.py` | `get_hrv` | `get_hrv_data` |
| `health.py` | `get_stress` | `get_stress_data` |
| `health.py` | `get_training_readiness` | `get_training_readiness` |
| `health.py` | `get_max_metrics` | `get_max_metrics` |
| `health.py` | `get_training_status` | `get_training_status` |
| `health.py` | `get_respiration` | `get_respiration_data` |
| `health.py` | `get_spo2` | `get_spo2_data` |
| `body.py` | `get_body_composition` | `get_body_composition` |
| `body.py` | `get_weigh_ins` | `get_weigh_ins` |
| `goals.py` | `get_endurance_score` | `get_endurance_score` |
| `goals.py` | `get_race_predictions` | `get_race_predictions` |
| `wellness.py` | `get_hydration` | `get_hydration_data` |

All tool parameters use ISO 8601 date strings (`YYYY-MM-DD`). All responses are
pretty-printed JSON returned as `TextContent`.

## Authentication

No credentials are stored in the MCP server configuration.

**One-time setup:** Run `python scripts/login.py`. The script prompts for Garmin email and
password interactively (never stored), authenticates via Garmin SSO, and saves OAuth tokens
to `~/.garminconnect`. Tokens are valid for ~1 year and refresh automatically.

**Every subsequent run:** `client.py` loads tokens from `~/.garminconnect` at startup. No
credentials required. If tokens are missing or expired, the server returns a clear message
directing the user to re-run `scripts/login.py`.

## Data Flow

```
Claude calls tool
  → server.call_tool(name, arguments)
  → validate date params (ISO 8601 regex)
  → client.get_client() — module-level singleton
      → loads tokens from ~/.garminconnect on first call
      → subsequent calls reuse the authenticated instance
  → tools.DISPATCH[name](client, arguments)
  → garminconnect API call
  → json.dumps(result, indent=2) returned as TextContent
```

## Error Handling

- Date params validated before any API call; invalid format returns a descriptive error as
  `TextContent` without raising
- All `garminconnect` calls wrapped in `try/except`; auth failures return:
  `"Tokens not found or expired — run scripts/login.py to re-authenticate"`
- No bare `except` clauses; specific exceptions caught with a broad fallback for unexpected errors
- Errors logged with tool name and sanitised arguments (credentials never logged)

## Testing

**Unit tests** (`tests/unit/`) — always run, no network or credentials required:
- Mock the `Garmin` client
- Verify each tool handler returns correctly shaped JSON
- Verify date validation rejects invalid input
- Verify auth errors return the correct message

**Integration tests** (`tests/integration/`) — call the real Garmin API:
- Gated behind `GARMIN_INTEGRATION_TESTS=1` env var
- Require tokens present in `~/.garminconnect`
- Never run in CI automatically

## Key Decisions

| Decision | Choice | Reason |
|---|---|---|
| Tool module structure | Mirrors python-garminconnect README categories | Natural extension path as new tools are added |
| Response format | Pretty-printed JSON string | Readable by Claude, parseable downstream |
| Auth | Token-only at runtime, interactive script for setup | No credentials in config files or env vars |
| Client | Module-level singleton | One login per server process; library handles token refresh |
| Test layers | Unit (mocked) + integration (gated) | Fast CI with real-API coverage available locally |
