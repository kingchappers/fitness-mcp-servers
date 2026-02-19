# Fitness MCP Servers — Project Context

## What This Project Is
Two separate Python MCP servers providing Claude with real-time access to personal fitness and
nutrition data. Claude synthesises data across both servers in conversation rather than joining
data server-side.

## Repo Structure (target)
```
fitness-mcp/
├── CLAUDE.md                  # This file
├── mcp-garmin/
│   ├── server.py              # MCP server entrypoint
│   ├── garmin_client.py       # Garmin Connect integration
│   ├── tools.py               # MCP tool definitions
│   ├── requirements.txt
│   └── README.md
├── mcp-myfitnesspal/
│   ├── server.py              # MCP server entrypoint
│   ├── mfp_client.py          # MFP integration
│   ├── tools.py               # MCP tool definitions
│   ├── requirements.txt
│   └── README.md
└── mcp-config-example.json    # Example MCP config for both servers
```

## Server 1: mcp-garmin

### Library
`python-garminconnect` (unofficial, actively maintained, 105+ API methods)
- Install: `pip install garminconnect`
- GitHub: https://github.com/cyberjunky/python-garminconnect

### Auth
- Credential-based (email + password)
- Tokens stored automatically in `~/.garminconnect`
- Token refresh handled transparently by the library
- Credentials should be loaded from environment variables, not hardcoded:
  `GARMIN_EMAIL` and `GARMIN_PASSWORD`

### Tools to Implement
| Tool | Parameters | Description |
|------|-----------|-------------|
| `get_activities` | `start_date`, `end_date` | Workouts with type, duration, HR, distance |
| `get_daily_stats` | `date` | Steps, calories burned, stress, active minutes |
| `get_heart_rate` | `date` | Resting HR and HR data for the day |
| `get_sleep` | `date` | Sleep duration, stages, score |

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
- Cookies stored in a local file, path set via env var: `MFP_COOKIE_PATH`
- Cookies must be manually refreshed when they expire
- See library docs for how to extract cookies from browser

### Tools to Implement
| Tool | Parameters | Description |
|------|-----------|-------------|
| `get_nutrition_diary` | `date` | Full diary: meals, foods, calories, macros |
| `get_nutrition_summary` | `start_date`, `end_date` | Aggregated nutrition over a date range |
| `get_weight_log` | `start_date`, `end_date` | Weight entries over a date range |

### Reliability: LOW
MFP can change internal structure without warning and break scraping.
This is acceptable for personal use — it is not production-grade.
Isolated in its own server so failures don't affect mcp-garmin.

---

## Build Order
1. **mcp-garmin first** — stable, validate the MCP server pattern end-to-end
2. **mcp-myfitnesspal second** — layer on once Garmin is confirmed working

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

### Security
**CRITICAL: Consult `SECURITY.md` before implementing.**

Key requirements:
- NEVER hardcode credentials (use environment variables)
- Validate all date parameters (ISO 8601 format only)
- Never use `eval()`, `exec()`, or `shell=True`
- Set file permissions to 0600 for tokens and cookies
- Log tool invocations (sanitize credentials from logs)
- Pin dependencies and run `pip-audit` regularly

---

## MCP Config (add to your Claude Code or claude.ai MCP settings)
```json
{
  "mcpServers": {
    "garmin": {
      "command": "python",
      "args": ["/path/to/fitness-mcp/mcp-garmin/server.py"],
      "env": {
        "GARMIN_EMAIL": "your@email.com",
        "GARMIN_PASSWORD": "yourpassword"
      }
    },
    "myfitnesspal": {
      "command": "python",
      "args": ["/path/to/fitness-mcp/mcp-myfitnesspal/server.py"],
      "env": {
        "MFP_COOKIE_PATH": "/path/to/mfp-cookies.txt"
      }
    }
  }
}
```

---

## Key Decisions & Rationale (do not revisit without good reason)

| Decision | Choice | Reason |
|----------|--------|--------|
| Language | Python | Both required libraries are Python-only |
| Two servers vs one | Two servers | MFP fragility isolated; independent failure, deployment, and updates |
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
| `GARMIN_EMAIL` | mcp-garmin | Garmin Connect account email |
| `GARMIN_PASSWORD` | mcp-garmin | Garmin Connect account password |
| `MFP_COOKIE_PATH` | mcp-myfitnesspal | Path to MFP browser session cookie file |
