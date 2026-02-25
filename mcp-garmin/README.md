# mcp-garmin

An MCP server that gives Claude access to your Garmin Connect fitness data. Ask Claude about your workouts, sleep, heart rate, training load, body composition, and more.

Uses the unofficial [`python-garminconnect`](https://github.com/cyberjunky/python-garminconnect) library. The official Garmin API requires a business partnership; this is the standard solution for personal use.

## Setup

### Prerequisites

- Python 3.12+
- [Poetry](https://python-poetry.org/docs/#installation)
- A Garmin Connect account

### 1. Install dependencies

```bash
cd mcp-garmin
poetry install
```

Verify it worked — this should print the server version and exit cleanly:

```bash
poetry run mcp-garmin --help 2>&1 || echo "install OK"
```

### 2. Authenticate with Garmin Connect

Run the one-time login script. It prompts for your credentials interactively — they are never stored on disk.

```bash
poetry run python scripts/login.py
```

OAuth tokens are saved to `~/.garminconnect` with `600` permissions. The MCP server reads from there at runtime — no credentials needed after this step.

> Re-run this script if the server reports an authentication error (tokens expire periodically).

### 3. Register with Claude Code

The `claude mcp add` command needs **absolute paths** for both the project directory and the Poetry executable. Using relative paths or relying on `$PATH` is the most common reason this step fails, because Claude Code launches the server in a subprocess that may not inherit your shell's PATH.

**Find the paths you need:**

```bash
# Full path to your mcp-garmin directory
pwd   # run this from inside the mcp-garmin directory

# Full path to the poetry executable
which poetry
```

**Register the server** (substitute your actual paths):

```bash
claude mcp add garmin -- /opt/homebrew/bin/poetry --directory /Users/yourname/Projects/fitness-mcp-servers/mcp-garmin run mcp-garmin
```

**Verify it was registered:**

```bash
claude mcp list
```

You should see `garmin` in the output with a `connected` status after restarting Claude Code.

**Restart Claude Code** to pick up the new server. The server starts fresh on each session — no background process to manage.

> If your Poetry is installed somewhere other than `/opt/homebrew/bin/poetry` (common on Linux or non-Homebrew installs), use the path returned by `which poetry` above.

## Tools

All dates use ISO 8601 format: `YYYY-MM-DD`.

### Daily

| Tool | Parameters | Description |
|------|-----------|-------------|
| `get_daily_stats` | `date` | Steps, calories burned, stress, active minutes |
| `get_heart_rate` | `date` | Resting HR and HR time series |
| `get_sleep` | `date` | Sleep duration, stages (deep/light/REM/awake), score |
| `get_hydration` | `date` | Hydration intake |

### Activities

| Tool | Parameters | Description |
|------|-----------|-------------|
| `get_activities` | `start_date`, `end_date` | Workouts with type, duration, HR, distance, pace |

### Health Metrics

| Tool | Parameters | Description |
|------|-----------|-------------|
| `get_hrv` | `date` | Heart Rate Variability |
| `get_stress` | `date` | Detailed stress data throughout the day |
| `get_respiration` | `date` | Respiration rate time series |
| `get_spo2` | `date` | Blood oxygen saturation (SpO2) |

### Training

| Tool | Parameters | Description |
|------|-----------|-------------|
| `get_training_readiness` | `date` | Readiness score and contributing factors |
| `get_training_status` | `date` | Current training status and load |
| `get_max_metrics` | `date` | VO2 max and fitness age estimates |
| `get_endurance_score` | `start_date`, `end_date` | Endurance score trend |
| `get_race_predictions` | `start_date`, `end_date` | Predicted race times (5K, 10K, half, marathon) |

### Body

| Tool | Parameters | Description |
|------|-----------|-------------|
| `get_body_composition` | `start_date`, `end_date` | Weight, body fat %, BMI |
| `get_weigh_ins` | `start_date`, `end_date` | Weight log entries |

## Architecture

The server runs as a stdio MCP process launched by Claude Code. It authenticates once at startup using tokens from `~/.garminconnect`, then proxies tool calls to the Garmin Connect API.

```
Claude Code ←─ MCP stdio ─→ mcp-garmin server ←─ HTTPS ─→ Garmin Connect
```

Token refresh is handled transparently by `python-garminconnect`.

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

1. Check that both paths in the `claude mcp add` command are absolute. Re-run `which poetry` and `pwd` from inside `mcp-garmin/` and re-register if needed:
   ```bash
   claude mcp remove garmin
   claude mcp add garmin -- /absolute/path/to/poetry --directory /absolute/path/to/mcp-garmin run mcp-garmin
   ```

2. Test that the server starts on its own before involving Claude Code:
   ```bash
   /opt/homebrew/bin/poetry --directory /absolute/path/to/mcp-garmin run mcp-garmin
   ```
   It should hang (waiting for MCP stdio input). Press `Ctrl-C` to stop. If it errors, fix the error before re-registering.

3. Make sure you've run `poetry install` inside the `mcp-garmin` directory and that `poetry run mcp-garmin` works standalone.

4. After any change to the registration, **restart Claude Code completely** — the server list is read at startup.

### Authentication errors

**"Garmin tokens not found"** — Run `scripts/login.py` to authenticate.

**"Login failed"** — Tokens have expired. Re-run `scripts/login.py`.

### Data issues

**Tool returns empty data** — Some metrics require a compatible Garmin device (e.g. HRV requires a watch with HRV tracking). Check that your device records the relevant metric.

## License

Personal use only. Garmin Connect data is subject to [Garmin's Terms of Service](https://www.garmin.com/en-US/privacy/connect/policy/).
