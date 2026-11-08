---
name: fitness-insights
description: Use when the user asks how their training, nutrition, body composition, running, sleep or recovery is going, wants a progress check-in or trajectory review, asks what to improve to reach a fitness goal, or wants to set or revisit fitness goals, and Garmin, MyFitnessPal or Hevy MCP tools are available.
---

# Fitness Insights

## Overview

Turn Garmin (activity, recovery, cardio fitness), MyFitnessPal (nutrition, weight) and Hevy
(lifting, body fat %) into one goal-aware verdict: **is the user on track, and what are the
few changes that would matter most?**

Core principle: every number is judged against the user's *stated goal and target rate*.
Without a goal there is no "on track", so goals come before data.

Reference files in this directory (read when the step says to):
- `data-catalog.md` — every tool, what it returns, cost, and which source wins when two overlap
- `goal-playbooks.md` — per-goal KPIs, target rates, tools to pull, and common levers

## Workflow

### 1. Probe the servers (parallel, one cheap call each)

| Server | Probe call |
|--------|-----------|
| garmin | `get_daily_stats` for yesterday |
| myfitnesspal | `get_nutrition_diary` for yesterday |
| hevy | `get_workout_count` |

If a probe fails, tell the user which server is down and the fix from the catalog's
"When a server fails" table, then continue with the rest. Name the missing source in the
report's data-gaps line.

### 2. Establish goals and context

If memory or the conversation already holds a goal profile, restate it in one line and ask
whether it still holds. Otherwise ask (use AskUserQuestion when available, otherwise plain
questions), at most 4 questions per round:

1. **Primary goal** — offer these examples, and accept anything else:
   - Lose fat / get leaner
   - Improve muscle definition (body recomposition: keep or build muscle while losing fat)
   - Build muscle (lean bulk)
   - Get stronger on specific lifts
   - Run faster (5K / 10K)
   - Build endurance (half marathon, marathon, cycling, triathlon)
   - Hybrid: lift and run well at the same time
   - Improve health markers (VO2 max, resting HR, fitness age)
   - Sleep better / recover better / lower stress
   - Train consistently / build the habit
   - Maintain weight while improving fitness
2. **Target and deadline** — a measurable end state ("sub-25 5K by March", "12% BF by summer").
3. **Profile** — sex, age, height, dietary constraints, injuries, training days per week.
   Skip anything memory already has.
4. **Secondary goal** (optional) — note conflicts (e.g. fat loss + marathon PR) and ask which wins.

Map the answer to a playbook in `goal-playbooks.md`. Combined goals take the primary's KPIs
plus the secondary's guardrails.

### 3. Pick the window

Default: **last 28 days**, compared with the **28 days before** (trajectory needs a "before").
Pass whole ranges to range tools. Sample per-day tools (sleep, HRV, readiness, stress) on the
last 7 days only. Keep MFP ranges ≤ 56 days; it scrapes one page per day.

### 4. Pull data

Always pull the **core set** from `data-catalog.md`, then the goal's extra tools from the
playbook. Issue independent calls in parallel.

### 5. Clean before computing

- Drop MFP days marked `complete: false` or with calories below ~40% of the user's average.
  Report how many were dropped.
- Flag likely duplicate MFP entries (same food logged 2+ times in one meal).
- Compare the user's plan targets with MFP's own `goals`. MFP's adaptive goals drift.
- Use weekly averages for weight, never single weigh-ins. Treat single BIA body-fat readings
  as noise; use the trend over 3+ readings.
- One source of truth per metric (catalog's overlap table). Don't average across scales.

### 6. Analyse

For each playbook KPI compute: current value, previous-window value, rate per week, target
rate, and status (on track / ahead / behind / off course). Then project the current rate to the
goal deadline. Run the cross-source checks in the playbook. These are the insights no single
app can give (e.g. intake vs weight trend → real maintenance calories).

### 7. Report

The report is, in order:

1. **Verdict** — one sentence: on track or not, and the projected outcome at the deadline.
2. **Scorecard** — table: metric | previous 28d | last 28d | rate/week | target | status.
3. **Working** — up to 3 things to keep doing, each tied to a number.
4. **Levers** — the top 3 changes ranked by expected impact on the primary goal. Each one is
   concrete and quantified ("+30 g protein/day: add a second whey shake on rest days").
5. **Data gaps** — sources down, days dropped, metrics with too little history to trust.
6. **Next check-in** — date and what will decide the next adjustment.

### 8. Persist

Offer to save the goal profile, targets and this check-in's key numbers to memory, so the next
review compares against them. Update an existing goal memory instead of creating a new one.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Analysing before asking the goal | Step 2 first; "good" depends on the goal |
| Calling per-day Garmin tools for 28 days | Sample 7 days; use range tools for trends |
| Trusting MFP calories as exact | Assume 10–20% under-logging; calibrate with weight trend |
| Reading one weigh-in or BIA reading as a trend | Weekly averages; 3+ readings |
| Ten generic tips | Three ranked, quantified levers tied to the primary goal |
| Silently skipping a dead server | Say which one, give the fix, list it under data gaps |
