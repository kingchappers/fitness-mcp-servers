# fitness-mcp-servers

Three MCP servers that give Claude real-time access to your personal fitness and nutrition data. Ask Claude to analyse your training load, nutrition trends, sleep quality, body composition, or anything across all data sources — it synthesises the data in conversation.

| Server | Data source | Reliability |
|--------|------------|-------------|
| [`mcp-garmin`](./mcp-garmin/) | Garmin Connect (workouts, sleep, HR, HRV, training load, body composition) | High |
| [`mcp-myfitnesspal`](./mcp-myfitnesspal/) | MyFitnessPal (nutrition diary, macros, weight log) | Low — cookie scraping, may break without warning |
| [`mcp-hevy`](./mcp-hevy/) | Hevy (strength workouts, routines, exercise history, body measurements) | High — official API |

## Architecture

Each server runs as an independent stdio MCP process. Claude Code launches them at startup and routes tool calls to the appropriate server. Data is never joined server-side — Claude synthesises across all of them in the conversation.

```
Claude Code ←─ MCP stdio ─→ mcp-garmin          ←─ HTTPS ─→ Garmin Connect
            ←─ MCP stdio ─→ mcp-myfitnesspal     ←─ HTTPS ─→ MyFitnessPal
            ←─ MCP stdio ─→ mcp-hevy             ←─ HTTPS ─→ Hevy
```

The multi-server design means a MyFitnessPal scraping failure doesn't affect Garmin or Hevy data.

## Setup

Each server has its own setup guide:

- **[mcp-garmin setup](./mcp-garmin/README.md)** — credential-based auth, tokens stored in `~/.garminconnect`
- **[mcp-myfitnesspal setup](./mcp-myfitnesspal/README.md)** — cookie-based auth, requires Playwright for initial login
- **[mcp-hevy setup](./mcp-hevy/README.md)** — API key auth, generate one at hevy.com/settings?developer

### Quick overview

1. `cd mcp-garmin && poetry install` then `poetry run python scripts/login.py`
2. `cd mcp-myfitnesspal && poetry install && poetry run playwright install chromium` then `poetry run python scripts/login.py`
3. `cd mcp-hevy && poetry install` (generate an API key at hevy.com/settings?developer)
4. Register all three servers with Claude Code (see individual READMEs for the exact `claude mcp add` commands)
5. Restart Claude Code

## Requirements

- Python 3.12+
- [Poetry](https://python-poetry.org/docs/#installation)
- A Garmin Connect account
- A MyFitnessPal account
- A Hevy Pro account

## Example questions

Once all servers are connected, you can ask Claude things like:

- *"How did my sleep quality correlate with my training load last week?"*
- *"I ran a hard session on Tuesday — what did my nutrition look like that day?"*
- *"Show me my weight trend and calorie intake over the past month."*
- *"What's my current VO2 max and training readiness?"*
- *"How much protein am I averaging, and is that enough given my activity level?"*

## Tools

### mcp-garmin

| Tool | Parameters | Description |
|------|-----------|-------------|
| `get_daily_stats` | `date` | Steps, calories burned, stress, active minutes |
| `get_heart_rate` | `date` | Resting HR and HR time series |
| `get_sleep` | `date` | Sleep duration, stages, score |
| `get_hydration` | `date` | Hydration intake |
| `get_activities` | `start_date`, `end_date` | Workouts with type, duration, HR, distance, pace |
| `get_hrv` | `date` | Heart Rate Variability |
| `get_stress` | `date` | Stress data throughout the day |
| `get_respiration` | `date` | Respiration rate |
| `get_spo2` | `date` | Blood oxygen saturation |
| `get_training_readiness` | `date` | Readiness score and contributing factors |
| `get_training_status` | `date` | Current training status and load |
| `get_max_metrics` | `date` | VO2 max and fitness age |
| `get_endurance_score` | `start_date`, `end_date` | Endurance score trend |
| `get_race_predictions` | `start_date`, `end_date` | Predicted race times (5K, 10K, half, marathon) |
| `get_body_composition` | `start_date`, `end_date` | Weight, body fat %, BMI |
| `get_weigh_ins` | `start_date`, `end_date` | Weight log entries |

### mcp-myfitnesspal

| Tool | Parameters | Description |
|------|-----------|-------------|
| `get_nutrition_diary` | `date` | Full diary: meals, foods, calories, macros |
| `get_nutrition_summary` | `start_date`, `end_date` | Aggregated nutrition totals over a date range |
| `get_weight_log` | `start_date`, `end_date` | Weight log entries |

### mcp-hevy

| Tool | Parameters | Description |
|------|-----------|-------------|
| `get_workouts` | `page`, `page_size` | Paginated list of logged workouts |
| `get_workout_count` | none | Total number of workouts logged |
| `get_workout` | `workout_id` | Full details for one workout |
| `get_routines` | `page`, `page_size` | Paginated list of saved routines |
| `get_routine` | `routine_id` | Full details for one routine |
| `get_routine_folders` | `page`, `page_size` | Paginated list of routine folders |
| `get_exercise_templates` | `page`, `page_size` | Paginated list of exercise templates |
| `get_exercise_template` | `exercise_template_id` | Details for one exercise template |
| `get_exercise_history` | `exercise_template_id` | Historical performance for one exercise |
| `get_body_measurements` | `page`, `page_size` | Paginated list of body measurements |
| `get_user_info` | none | Basic Hevy account info |

All dates use ISO 8601 format: `YYYY-MM-DD`.

## Security

See [SECURITY.md](./SECURITY.md). Credentials are loaded from environment variables only — never hardcoded. Token and cookie files are stored with `600` permissions.

## License

Personal use only. Data is subject to [Garmin's Terms of Service](https://www.garmin.com/en-US/privacy/connect/policy/), [MyFitnessPal's Terms of Service](https://www.myfitnesspal.com/terms-of-service), and [Hevy's Terms of Service](https://www.hevyapp.com/terms).
