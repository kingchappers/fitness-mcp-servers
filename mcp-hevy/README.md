# mcp-hevy

An MCP server that gives Claude read access to your Hevy strength-training data. Ask Claude about your workouts, routines, exercise history, and body measurements.

Uses the official [Hevy Public API](https://api.hevyapp.com/docs/), authenticated with a personal API key (no OAuth, no cookies, no login script). The API is available to Hevy Pro accounts.

## Setup

### Prerequisites

- Python 3.12+
- [Poetry](https://python-poetry.org/docs/#installation)
- A Hevy Pro account

### 1. Install dependencies

```bash
cd mcp-hevy
poetry install
```

### 2. Generate an API key

Go to [hevy.com/settings?developer](https://hevy.com/settings?developer) and generate a personal API key. Copy it — you'll need it in the next step.

### 3. Register with Claude Code

**Find the paths you need:**

```bash
# Full path to your mcp-hevy directory
pwd   # run this from inside the mcp-hevy directory

# Full path to the poetry executable
which poetry
```

**Register the server** (substitute your actual paths and API key):

```bash
claude mcp add hevy -e HEVY_API_KEY=your-api-key-here -- /opt/homebrew/bin/poetry --directory /Users/yourname/Projects/fitness-mcp-servers/mcp-hevy run mcp-hevy
```

**Verify it was registered:**

```bash
claude mcp list
```

You should see `hevy` in the output with a `connected` status after restarting Claude Code.

**Restart Claude Code** to pick up the new server.

## Tools

| Tool | Parameters | Description |
|------|-----------|-------------|
| `get_workouts` | `page`, `page_size` (optional) | Paginated list of logged workouts |
| `get_workout_count` | none | Total number of workouts logged |
| `get_workout` | `workout_id` | Full details for one workout: exercises, sets, weight, reps |
| `get_routines` | `page`, `page_size` (optional) | Paginated list of saved routines |
| `get_routine` | `routine_id` | Full details for one routine |
| `get_routine_folders` | `page`, `page_size` (optional) | Paginated list of routine folders |
| `get_exercise_templates` | `page`, `page_size` (optional) | Paginated list of exercise templates |
| `get_exercise_template` | `exercise_template_id` | Details for one exercise template |
| `get_exercise_history` | `exercise_template_id` | Historical performance for one exercise |
| `get_body_measurements` | `page`, `page_size` (optional) | Paginated list of body measurements |
| `get_user_info` | none | Basic Hevy account info |

This server is read-only — it does not create or modify data in Hevy.

## Architecture

The server runs as a stdio MCP process launched by Claude Code. It authenticates every Hevy API request with a static `api-key` header, unlike `mcp-garmin` (token file) or `mcp-myfitnesspal` (browser cookies).

```
Claude Code ←─ MCP stdio ─→ mcp-hevy server ←─ HTTPS ─→ Hevy
```

## Development

```bash
# Run unit tests
poetry run pytest tests/unit/

# Run integration tests against the real Hevy API
HEVY_INTEGRATION_TESTS=1 HEVY_API_KEY=your-api-key-here poetry run pytest tests/integration/ -v -s

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

1. Check that both paths in the `claude mcp add` command are absolute. Re-run `which poetry` and `pwd` from inside `mcp-hevy/` and re-register if needed.
2. Test that the server starts on its own before involving Claude Code:
   ```bash
   HEVY_API_KEY=your-api-key-here /opt/homebrew/bin/poetry --directory /absolute/path/to/mcp-hevy run mcp-hevy
   ```
   It should hang (waiting for MCP stdio input). Press `Ctrl-C` to stop. If it errors, fix the error before re-registering.
3. Make sure you've run `poetry install` inside the `mcp-hevy` directory.
4. After any change to the registration, **restart Claude Code completely** — the server list is read at startup.

### "HEVY_API_KEY not set"

Generate a key at [hevy.com/settings?developer](https://hevy.com/settings?developer) and make sure it's in the `env` block of your `claude mcp add` registration, not just your shell.

### Hevy API errors

Tool responses that start with "Hevy API error" include the HTTP status code and Hevy's error body. A 401 means the API key is invalid or missing; check that your account has Hevy Pro (the public API requires it).

## License

Personal use only. Data is subject to [Hevy's Terms of Service](https://www.hevyapp.com/terms).
