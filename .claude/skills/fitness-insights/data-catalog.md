# Data Catalog

All tools are read-only. Dates are `YYYY-MM-DD`. Tool names are shown without their MCP
prefix (in Claude Code they appear as `mcp__garmin__get_sleep`, etc.).

## Core set (pull for every review)

| Server | Calls | Why |
|--------|-------|-----|
| garmin | `get_activities` (window), `get_body_composition` (window), `get_training_status` (today), `get_training_readiness` (today) | Training volume, weight, load, readiness |
| garmin | `get_sleep`, `get_hrv` for each of the last 7 days | Recovery snapshot |
| myfitnesspal | `get_nutrition_summary` (window, ≤ 56 days), `get_nutrition_diary` (yesterday) | Intake trend; MFP's current goals |
| hevy | `get_workouts` pages until results are older than the window; `get_body_measurements` page 1 | Lifting sessions, body fat % |

## Garmin (22 tools)

**Per day (`date`)** — one call per day, so sample them:

| Tool | Answers |
|------|---------|
| `get_daily_stats` | Steps, calories burned, stress, intensity minutes, resting HR |
| `get_heart_rate` | Resting HR plus the day's HR series (~30k chars) |
| `get_sleep` | Duration, deep/light/REM/awake, sleep score, overnight HR/SpO2/respiration averages |
| `get_body_battery` | Energy charged vs drained |
| `get_hrv` | Overnight HRV, weekly average, personal baseline band, status |
| `get_stress` | Stress levels through the day |
| `get_training_readiness` | Readiness score and contributors (sleep, recovery time, HRV, load) |
| `get_training_status` | Productive / maintaining / overreaching / detraining; acute vs chronic load; load focus |
| `get_max_metrics` | VO2 max (run/cycle) and fitness age |
| `get_respiration` | Breathing rate |
| `get_spo2` | Blood oxygen |
| `get_hydration` | Water intake vs goal |

**Date range (`start_date`, `end_date`)**:

| Tool | Answers |
|------|---------|
| `get_activities` | Every workout: type, duration, distance, avg/max HR, pace, calories, training effect |
| `get_body_composition` | Weight, BMI (body fat only if a Garmin smart scale is used) |
| `get_weigh_ins` | Raw weigh-in entries |
| `get_endurance_score` | Endurance score trend |
| `get_race_predictions` | Predicted 5K / 10K / half / marathon times over time |
| `get_menstrual_cycle` | Cycle phase and stats (affects weight, HRV, performance) |

**Other**: `get_personal_records` (all-time PRs, no args); `get_activity_details(activity_id)`
gives splits, laps and HR zones for one activity (IDs come from `get_activities`).

## MyFitnessPal (3 tools)

| Tool | Answers | Notes |
|------|---------|-------|
| `get_nutrition_diary(date)` | Meals, foods, totals, MFP goals, water, `complete` flag | Use for food-level analysis on a few days |
| `get_nutrition_summary(start, end)` | One row per day: totals vs goals | Max 365 days; one scrape per day, so slow |
| `get_weight_log(start, end)` | Weight entries | Only if the user weighs in via MFP |

## Hevy (11 tools)

Paginated tools take `page` (from 1) and `page_size` (default 5, **max 10**), newest first.

| Tool | Answers |
|------|---------|
| `get_workouts` | Workouts with exercises and sets (weight, reps, RPE) |
| `get_workout(workout_id)` | One workout in full |
| `get_workout_count` | Lifetime total; cheap probe |
| `get_exercise_history(exercise_template_id)` | Every logged set of one exercise: best for progression |
| `get_exercise_templates` / `get_exercise_template(id)` | Exercise names, IDs, primary muscle, equipment |
| `get_routines` / `get_routine(id)` / `get_routine_folders` | The planned programme: target sets/reps |
| `get_body_measurements` | Weight, body fat %, waist and other measurements |
| `get_user_info` | Account info |

For lift progression, prefer `get_exercise_history` on the 3–5 main lifts over paging
through every workout. Find IDs from the routine or from recent workouts.

## Overlaps: which source wins

| Metric | Use | Fall back to | Why |
|--------|-----|--------------|-----|
| Body weight | The scale the user weighs on most often | Next most frequent | Different scales and times of day disagree by 0.5–1 kg |
| Body fat % | Hevy `get_body_measurements` | Garmin body composition if a smart scale is used | MFP has none |
| Calories in | MFP | — | Only intake source |
| Calories out | Weight trend vs intake (playbook formula) | Garmin `get_daily_stats` | Wearable burn estimates often run 10–30% high |
| Workouts | Hevy for lifting; Garmin for cardio | Garmin for strength sessions if Hevy is missing | Hevy has sets and reps; Garmin has HR and distance |
| Resting HR | Garmin `get_daily_stats` / `get_sleep` | — | |

## When a server fails

| Symptom | Fix for the user |
|---------|-----------------|
| Garmin auth error / "Username and password are required" | `cd mcp-garmin && poetry run python scripts/login.py` |
| MFP cookie / auth / "Cookie file not found" | `cd mcp-myfitnesspal && poetry run python scripts/login.py` (cookies expire) |
| Hevy 401 | Check `HEVY_API_KEY` in the `claude mcp add` registration; key from hevy.com/settings?developer (needs Hevy Pro) |
| Tool not listed at all | Server not connected; run `/mcp` in Claude Code to reconnect |
