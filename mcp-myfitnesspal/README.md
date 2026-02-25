# mcp-myfitnesspal

An MCP server that gives Claude access to your MyFitnessPal nutrition and weight data. Ask Claude about your daily food diary, macro breakdowns, calorie trends, and weight log.

Uses the unofficial [`python-myfitnesspal`](https://github.com/coddingtonbear/python-myfitnesspal) library, which scrapes MyFitnessPal via browser session cookies. MyFitnessPal has no public API, so cookie-based scraping is the only viable option for personal use. The scraping approach is inherently fragile — if MFP changes its internal structure the library may break without warning. This is accepted as a tradeoff for personal use; it is not production-grade.

## Setup

### Prerequisites

- Python 3.12+
- [Poetry](https://python-poetry.org/docs/#installation)
- A MyFitnessPal account

### 1. Install dependencies

```bash
cd mcp-myfitnesspal
poetry install
poetry run playwright install chromium
```

Playwright is used by the login script to capture browser session cookies automatically.

### 2. Authenticate with MyFitnessPal

Run the one-time login script. It opens a headless browser, logs in to MyFitnessPal, and saves the session cookies to disk.

```bash
poetry run python scripts/login.py
```

The script will print the path where cookies were saved — set that path as your `MFP_COOKIE_PATH` environment variable when registering the server in step 3.

> Re-run this script if the server reports an authentication or cookie error (cookies expire periodically).

### 3. Register with Claude Code

The `claude mcp add` command needs **absolute paths** for both the project directory and the Poetry executable. Using relative paths or relying on `$PATH` is the most common reason this step fails, because Claude Code launches the server in a subprocess that may not inherit your shell's PATH.

**Find the paths you need:**

```bash
# Full path to your mcp-myfitnesspal directory
pwd   # run this from inside the mcp-myfitnesspal directory

# Full path to the poetry executable
which poetry
```

**Register the server** (substitute your actual paths and cookie path):

```bash
claude mcp add myfitnesspal -e MFP_COOKIE_PATH=/Users/yourname/.config/mfp/cookies.json -- /opt/homebrew/bin/poetry --directory /Users/yourname/Projects/fitness-mcp-servers/mcp-myfitnesspal run mcp-myfitnesspal
```

**Verify it was registered:**

```bash
claude mcp list
```

You should see `myfitnesspal` in the output with a `connected` status after restarting Claude Code.

**Restart Claude Code** to pick up the new server.

> If your Poetry is installed somewhere other than `/opt/homebrew/bin/poetry` (common on Linux or non-Homebrew installs), use the path returned by `which poetry` above.

## Tools

All dates use ISO 8601 format: `YYYY-MM-DD`.

| Tool | Parameters | Description |
|------|-----------|-------------|
| `get_nutrition_diary` | `date` | Full diary: meals, foods, calories, macros |
| `get_nutrition_summary` | `start_date`, `end_date` | Aggregated nutrition totals over a date range |
| `get_weight_log` | `start_date`, `end_date` | Weight log entries |

## Architecture

The server runs as a stdio MCP process launched by Claude Code. It loads MFP session cookies from disk at startup, then proxies tool calls to MyFitnessPal via the scraping library.

```
Claude Code ←─ MCP stdio ─→ mcp-myfitnesspal server ←─ HTTPS ─→ MyFitnessPal
```

Cookies must be refreshed manually by re-running `scripts/login.py` when they expire.

## Development

```bash
# Run unit tests
poetry run pytest tests/unit/

# Lint
poetry run ruff check src/

# Type check
poetry run mypy src/

# Security scan
poetry run bandit -r src/

# Audit dependencies for vulnerabilities
poetry run pip-audit
```

## Troubleshooting

### MCP server not connecting

**`claude mcp list` shows the server as `failed` or it doesn't appear:**

1. Check that both paths in the `claude mcp add` command are absolute. Re-run `which poetry` and `pwd` from inside `mcp-myfitnesspal/` and re-register if needed:
   ```bash
   claude mcp remove myfitnesspal
   claude mcp add myfitnesspal -e MFP_COOKIE_PATH=/absolute/path/to/cookies.json -- /absolute/path/to/poetry --directory /absolute/path/to/mcp-myfitnesspal run mcp-myfitnesspal
   ```

2. Test that the server starts on its own before involving Claude Code:
   ```bash
   MFP_COOKIE_PATH=/absolute/path/to/cookies.json /opt/homebrew/bin/poetry --directory /absolute/path/to/mcp-myfitnesspal run mcp-myfitnesspal
   ```
   It should hang (waiting for MCP stdio input). Press `Ctrl-C` to stop. If it errors, fix the error before re-registering.

3. Make sure you've run `poetry install` inside the `mcp-myfitnesspal` directory and that `poetry run mcp-myfitnesspal` works standalone.

4. After any change to the registration, **restart Claude Code completely** — the server list is read at startup.

### Cookies expired

**"Cookie file not found"** or authentication errors from MFP — Re-run `scripts/login.py` to capture a fresh session and update `MFP_COOKIE_PATH` if the cookie path changed.

### MFP format changed

**Tools return unexpected empty data or raise parsing errors** — `python-myfitnesspal` scrapes MyFitnessPal's internal structure, which can change without notice. Check the [library's GitHub issues](https://github.com/coddingtonbear/python-myfitnesspal/issues) for reports of breakage and available fixes or workarounds.

## License

Personal use only. MyFitnessPal data is subject to [MyFitnessPal's Terms of Service](https://www.myfitnesspal.com/terms-of-service).
