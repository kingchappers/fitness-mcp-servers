# Fitness MCP Servers — Project Context

## What This Project Is
Three separate Python MCP servers providing Claude with real-time access to personal fitness and
nutrition data. Claude synthesises data across all three servers in conversation rather than
joining data server-side.

## Fitness Insights Skill

`.claude/skills/fitness-insights/` holds a skill that combines all three servers into a
goal-aware progress review: it asks for fitness goals, pulls the right data, checks the
trajectory and ranks what to improve. Claude Code loads it automatically inside this repo.

**When a session in this repo involves reviewing the user's fitness data, first run
`bash scripts/install-skill.sh --check`.** If it reports "not installed", offer to run
`bash scripts/install-skill.sh` so the skill also works outside this repo (it symlinks into
`~/.claude/skills`, so edits here stay live). For claude.ai, `--zip` builds an upload bundle in
`dist/`.

When adding or changing an MCP tool, update `.claude/skills/fitness-insights/data-catalog.md`
to match.

## Repo Structure
Each server is a Poetry project with a `src/` layout and the same shape:
```
fitness-mcp-servers/
├── CLAUDE.md                      # This file
├── .claude/skills/fitness-insights/
│   ├── SKILL.md                   # Review workflow
│   ├── data-catalog.md            # Every tool, cost, source-of-truth rules
│   └── goal-playbooks.md          # Per-goal KPIs, rates, levers
├── scripts/install-skill.sh       # Install / check / zip the skill
├── mcp-garmin/
│   ├── scripts/login.py           # One-time interactive login → token cache
│   ├── src/mcp_garmin/
│   │   ├── server.py              # MCP server entrypoint
│   │   ├── client.py              # Garmin Connect client
│   │   ├── validation.py          # Input validation helpers
│   │   └── tools/                 # activities, body, daily, goals, health, wellness
│   ├── tests/
│   └── pyproject.toml
├── mcp-myfitnesspal/
│   ├── scripts/login.py           # Playwright browser login → cookie file
│   ├── src/mcp_myfitnesspal/
│   │   ├── server.py, client.py, exceptions.py, validation.py
│   │   └── tools/                 # body, nutrition
│   ├── tests/
│   └── pyproject.toml
└── mcp-hevy/
    ├── src/mcp_hevy/
    │   ├── server.py, client.py, validation.py
    │   └── tools/                 # body, exercises, routines, user, workouts
    ├── tests/
    └── pyproject.toml
```

## Server 1: mcp-garmin

### Library
`python-garminconnect` (unofficial, actively maintained, 105+ API methods)
- Install: `pip install garminconnect`
- GitHub: https://github.com/cyberjunky/python-garminconnect

### Auth
- One-time interactive login: `poetry run python scripts/login.py` (credentials prompted,
  never stored on disk)
- OAuth tokens saved to `~/.garminconnect` with `0600` permissions; the server reads only these
- Re-run the login script when the server reports an auth error

### Tools (22)
| Module | Tool | Parameters | Description |
|--------|------|-----------|-------------|
| activities | `get_activities` | `start_date`, `end_date` | Workouts with type, duration, HR, distance, pace |
| activities | `get_activity_details` | `activity_id` | Splits, laps, HR zones (time series stripped) |
| daily | `get_daily_stats` | `date` | Steps, calories burned, stress, active minutes |
| daily | `get_heart_rate` | `date` | Resting HR and HR time series |
| daily | `get_sleep` | `date` | Duration, stages, score (`_summarize_sleep`) |
| daily | `get_body_battery` | `date` | Body battery charge and drain |
| health | `get_hrv`, `get_stress`, `get_training_readiness`, `get_max_metrics`, `get_training_status`, `get_respiration`, `get_spo2` | `date` | HRV, stress, readiness, VO2 max / fitness age, training load, respiration, SpO2 |
| health | `get_menstrual_cycle` | `start_date`, `end_date` | Cycle phase, symptoms, stats |
| body | `get_body_composition`, `get_weigh_ins` | `start_date`, `end_date` | Weight, body fat %, BMI; weigh-in log |
| goals | `get_endurance_score`, `get_race_predictions` | `start_date`, `end_date` | Endurance score; predicted race times |
| goals | `get_personal_records` | — | All-time PRs |
| wellness | `get_hydration` | `date` | Hydration intake |

### Reliability: HIGH
Stable unofficial library. Unlikely to break without warning.

---

## Server 2: mcp-myfitnesspal

### Library
`python-myfitnesspal` (cookie-based scraping)
- Install: `pip install myfitnesspal`
- GitHub: https://github.com/coddingtonbear/python-myfitnesspal

### Auth
- Uses browser session cookies (NOT username/password directly)
- `poetry run python scripts/login.py` opens a Playwright browser for login and saves the
  cookies as JSON (needs `poetry run playwright install chromium` once)
- Cookie file path set via env var: `MFP_COOKIE_PATH`
- Cookies expire; re-run the login script when the server reports an auth error

### Tools
| Tool | Parameters | Description |
|------|-----------|-------------|
| `get_nutrition_diary` | `date` | Full diary: meals, foods, totals vs goals, water, `complete` flag |
| `get_nutrition_summary` | `start_date`, `end_date` | One row per day (max 365 days; one scrape per day) |
| `get_weight_log` | `start_date`, `end_date` | Weight entries over a date range |

### Reliability: LOW
MFP can change internal structure without warning and break scraping.
This is acceptable for personal use — it is not production-grade.
Isolated in its own server so failures don't affect mcp-garmin.

---

## Server 3: mcp-hevy

### Library
Direct HTTP calls via `httpx` to the [Hevy Public API](https://api.hevyapp.com/docs/)
(official, requires Hevy Pro)
- Install: `pip install httpx`

### Auth
- API-key based (single `api-key` header, UUID)
- Generated by the user at `https://hevy.com/settings?developer`
- No token/cookie refresh needed — the key does not expire from normal use
- Loaded from environment variable, not hardcoded: `HEVY_API_KEY`

### Tools
Paginated tools: `page_size` defaults to 5 and is capped at 10.

| Tool | Parameters | Description |
|------|-----------|-------------|
| `get_workouts` | `page`, `page_size` | Paginated list of logged workouts |
| `get_workout_count` | — | Total number of workouts logged |
| `get_workout` | `workout_id` | Full details for one workout |
| `get_routines` | `page`, `page_size` | Paginated list of saved routines |
| `get_routine` | `routine_id` | Full details for one routine |
| `get_routine_folders` | `page`, `page_size` | Paginated list of routine folders |
| `get_exercise_templates` | `page`, `page_size` | Paginated list of exercise templates |
| `get_exercise_template` | `exercise_template_id` | Details for one exercise template |
| `get_exercise_history` | `exercise_template_id` | Historical performance for one exercise |
| `get_body_measurements` | `page`, `page_size` | Paginated list of body measurements |
| `get_user_info` | — | Basic Hevy account info |

Read-only: the API also exposes POST/PUT endpoints (create/update workouts, routines,
body measurements) but these are not implemented, matching the pattern of the other
two servers never writing back to the source system.

### Reliability: HIGH
Official API, versioned and documented. Simpler auth than Garmin or MFP (no
token/cookie refresh).

---

## Status
All three servers are implemented. Dependencies are managed with Poetry per server
(`poetry install`, `poetry run pytest`). They were built in order Garmin → MyFitnessPal → Hevy.

---

## MCP Server Implementation Notes

### Framework
Use the official `mcp` Python SDK:
- Install: `pip install mcp`
- Docs: https://github.com/modelcontextprotocol/python-sdk

### Each server should follow this pattern
```python
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

server = Server("mcp-garmin")  # or "mcp-myfitnesspal"

@server.list_tools()
async def list_tools():
    return [...]  # return Tool definitions

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    ...  # dispatch to tool implementations

if __name__ == "__main__":
    import asyncio
    asyncio.run(stdio_server(server))
```

### Date parameter format
Use ISO 8601 strings throughout: `"YYYY-MM-DD"`

### Error handling
- Wrap all external library calls in try/except
- Return meaningful error messages as TextContent rather than raising
- Auth failures should return a clear message indicating cookies/tokens need refreshing

### Response size — REQUIRED check for every new or modified tool

MCP tool responses feed directly into the context window. A response that is too large will either overflow the context or force expensive workarounds. **Before merging any new or modified tool, verify its real response size.**

**How to check:**

Call the tool via its MCP tool definition and note whether the result is truncated or flagged as oversized. Alternatively, call the underlying Garmin library method directly and measure:

```python
import json, garminconnect, os
client = garminconnect.Garmin(...)
client.login()
data = client.get_whatever(date)
print(len(json.dumps(data)))   # characters — aim for < 20,000
```

**Thresholds:**

| Size | Action |
|------|--------|
| < 20 000 chars | Fine — no action needed |
| 20 000 – 100 000 chars | Warning — consider whether all fields are useful |
| > 100 000 chars | Must reduce before the tool is usable |

**How to reduce — in order of preference:**

1. **Strip per-epoch time-series arrays.** Garmin responses often contain minute-by-minute arrays (HR, SpO2, stress, body battery, respiration, movement) that add hundreds of KB while their aggregate values are already present as scalars in the summary object. Remove them with a `_summarize_*` function that allowlists or blocklists keys before returning. See `mcp-garmin/src/mcp_garmin/tools/daily.py::_summarize_sleep` for the established pattern.

2. **Keep only semantically useful fields.** If a response has both a detailed time-series and a pre-computed summary (e.g. `dailySleepDTO` contains `avgHeartRate`, `averageSpO2Value`, etc.), drop the time-series — the summary is what matters for conversational queries.

3. **Add a `_summarize_*` function, not inline filtering.** Keep the transformation in a named function so it is testable and the intent is documented. Test that (a) stripped keys are absent, (b) important summary keys are present, and (c) any small arrays worth keeping (e.g. `sleepLevels`) are retained.

**Known large responses in mcp-garmin:**

| Tool | Raw size | Fix applied |
|------|----------|-------------|
| `get_sleep` | ~273 000 chars | `_summarize_sleep` strips 8 time-series arrays |
| `get_heart_rate` | ~30 000 chars | Fits; monitor if it grows |

### Security
**CRITICAL: Consult `SECURITY.md` before implementing.**

Key requirements:
- NEVER hardcode credentials (use environment variables or the login scripts' token/cookie files)
- Validate all date parameters (ISO 8601 format only)
- Never use `eval()`, `exec()`, or `shell=True`
- Set file permissions to 0600 for tokens and cookies
- Log tool invocations (sanitize credentials from logs)
- Pin dependencies and run `pip-audit` regularly

---

## Registering the Servers with Claude Code
Use absolute paths for both Poetry and the project directory; Claude Code launches servers in a
subprocess that may not inherit your shell's `PATH`. See each server's README for details.
```bash
claude mcp add garmin -- /opt/homebrew/bin/poetry --directory /abs/path/mcp-garmin run mcp-garmin
claude mcp add myfitnesspal -e MFP_COOKIE_PATH=/abs/path/cookies.json -- /opt/homebrew/bin/poetry --directory /abs/path/mcp-myfitnesspal run mcp-myfitnesspal
claude mcp add hevy -e HEVY_API_KEY=your-api-key-here -- /opt/homebrew/bin/poetry --directory /abs/path/mcp-hevy run mcp-hevy
```

---

## Key Decisions & Rationale (do not revisit without good reason)

| Decision | Choice | Reason |
|----------|--------|--------|
| Language | Python | Both required libraries are Python-only |
| Separate servers per source | Three servers | Each source's fragility/reliability isolated; independent failure, deployment, and updates |
| MFP approach | Cookie scraping | Official API closed; no free alternatives exist |
| Garmin approach | python-garminconnect | Official API is business-partners only; this is the standard personal solution |
| Data synthesis | In Claude conversation | No need for server-side joins at this scale |

## Alternatives Rejected
- **Go** — no equivalent libraries for either integration
- **Cronometer** — better nutrition accuracy but no public API (enterprise only)
- **Nutritionix** — removed free tier; enterprise pricing ~$1,850/month
- **Strava API** — public and well-documented but ToS prohibits AI/ML use of data
- **Lifesum / Headspace / Sleep Cycle** — no developer APIs
- **Garmin official API** — business partners only, commercial licence required

---

## Environment Variables Reference
| Variable | Server | Description |
|----------|--------|-------------|
| `MFP_COOKIE_PATH` | mcp-myfitnesspal | Path to the JSON cookie file written by `scripts/login.py` |
| `HEVY_API_KEY` | mcp-hevy | Hevy personal API key (from hevy.com/settings?developer) |
