# Goal Playbooks

Rates are evidence-based starting ranges, not rules. Adjust them to training age, sex and the
user's own history, and say when you do.

## Shared formulas

- **Empirical maintenance (TDEE)** = avg daily intake − (weight change kg/week × 7700 ÷ 7).
  Use weekly-average weights over 3+ weeks and only complete MFP days. Then compare it with a
  formula estimate (Mifflin-St Jeor × activity factor). If the empirical figure is well below
  the formula, suspect under-logging, which typically runs 10–20%.
- **Estimated 1RM (Epley)** = weight × (1 + reps ÷ 30). Valid up to ~10 reps. Track the best
  e1RM per session for each main lift.
- **Stall** = no e1RM or rep gain on a lift for 3+ sessions.
- **Protein per kg** = avg protein g ÷ body weight kg.
- **Acute:chronic load** comes from `get_training_status`. Below ~0.8 is detraining; above
  ~1.5 raises injury risk.
- **Recovery red flags**: HRV below the personal baseline band for 3+ days, resting HR 5+ bpm
  above its 28-day average, or average sleep under 7 h.

## Playbooks

### Lose fat / get leaner
- **KPI**: weekly-average weight; waist (Hevy measurements) if logged.
- **Target rate**: −0.5 to −1.0% of body weight per week.
- **Extra tools**: Garmin `get_daily_stats` (steps) on sampled days.
- **Checks**: deficit implied by the TDEE formula; protein 1.8–2.4 g/kg; resistance training
  still 2+ sessions/week (protects muscle); weekend vs weekday intake gap.
- **Levers**: weekend intake, protein, steps, liquid calories and snacks.

### Improve muscle definition (body recomposition)
- **KPI**: body fat % trend (Hevy) plus e1RM on main lifts held or rising.
- **Rough targets**: visible definition around 10–12% BF for men and 18–20% for women. BIA
  scales are noisy, so use the trend and say so.
- **Choose a phase from the data**:
  - Above those levels: cut at −0.5 to −0.75%/week.
  - Near them: recomp at maintenance with high protein.
  - Already lean but small: lean bulk (see Build muscle).
- **Checks**: protein ≥ 2.0 g/kg; weekly hard sets per muscle (10–20); strength trend in a
  deficit. Falling e1RM means the deficit is too steep.
- **Levers**: phase choice, protein, volume on lagging muscles, deficit size.

### Build muscle (lean bulk)
- **KPI**: weekly-average weight, e1RM trend, body fat % drift.
- **Target rate**: +0.25 to +0.5%/week for beginners; +0.1 to +0.25%/week for experienced
  lifters.
- **Extra tools**: `get_routines`/`get_routine` (planned vs done), `get_exercise_history` on
  main lifts.
- **Checks**:
  - Gaining faster than target with BF% climbing means the surplus is too big.
  - Flat weight and stalled lifts mean it's too small.
  - Protein 1.6–2.2 g/kg.
  - Logged RPE vs programmed RIR: grinding every set to failure hurts recovery.
- **Levers**: ±100–150 kcal steps, protein distribution, progressive overload on stalled lifts.

### Get stronger
- **KPI**: e1RM per main lift (from `get_exercise_history`); PRs.
- **Target**: beginners add load most weeks; intermediates gain ~1–2.5% e1RM per month.
- **Checks**: stalls; volume and frequency per lift; readiness and sleep on heavy days;
  enough calories (strength stalls in steep deficits).
- **Levers**: deload or reset a stalled lift, rep-range change, add frequency, sleep.

### Run faster (5K / 10K)
- **KPI**: `get_race_predictions` trend; VO2 max (`get_max_metrics`); pace at a given HR.
- **Extra tools**: `get_personal_records`, `get_activity_details` on key sessions (splits,
  HR zones).
- **Checks**:
  - Intensity split: roughly 80% easy and 20% hard by time.
  - Weekly volume rising no more than ~10% per week.
  - Aerobic efficiency: pace at similar average HR over time.
  - At least one quality session a week.
  - Body weight trend (lighter usually means faster, but not at the cost of fuelling).
- **Levers**: add easy volume, one interval session, tempo runs, less grey-zone running.

### Build endurance (half / marathon / cycling / triathlon)
- **KPI**: `get_endurance_score`, weekly volume, long-session duration, race predictions.
- **Checks**: acute:chronic load; long run or ride growing steadily; carb intake 5–8 g/kg on
  heavy days (MFP); recovery red flags.
- **Levers**: long-session progression, fuelling on long days, recovery weeks every 3–4 weeks.

### Hybrid (lift and run)
- **KPI**: main-lift e1RM and run race predictions together.
- **Checks**: hard runs within ~6 h before leg days (interference); total load via training
  status; calories enough for both.
- **Levers**: session order and spacing, keep most runs easy, raise carbs on double days.

### Improve health markers / longevity
- **KPI**: VO2 max and fitness age, resting HR, steps, sleep.
- **Targets**: 150–300 min/week moderate activity (Garmin intensity minutes); 2+ strength
  sessions/week; 7–9 h sleep; daily steps trending up.
- **Levers**: zone 2 volume, strength frequency, sleep consistency.

### Sleep better / recover better / lower stress
- **KPI**: sleep duration and score, HRV status, resting HR, body battery, stress.
- **Extra tools**: sample `get_stress`, `get_body_battery`, `get_respiration` across 7–14 days.
- **Cross-source checks**:
  - Late heavy meals (MFP dinner/snack calories) vs sleep score.
  - Hard evening sessions (activity start times) vs HRV.
  - High-intensity days vs the next night's sleep.
- **Levers**: bedtime consistency, training timing, evening intake, deload.

### Train consistently / build the habit
- **KPI**: sessions per week vs plan; streaks; MFP logging completeness.
- **Checks**: which days get missed (weekday pattern), planned routine vs workouts done.
- **Levers**: fewer, shorter sessions that actually happen; anchor days; minimum viable week.

### Maintain weight while improving fitness
- **KPI**: weight within ±1% band; the performance KPI of the chosen sport.
- **Checks**: intake matches empirical maintenance; protein adequate.

## Modifiers

- **Menstrual cycle** (if the user tracks it): pull `get_menstrual_cycle`. Compare weight,
  HRV and performance by phase before calling a trend.
- **Dietary constraints** (vegetarian, vegan, allergies): every food suggestion respects them.
- **Injury**: suggest no load increases on affected movements; recommend a professional.
- **Medical**: refer out for symptoms, disordered-eating signals, or targets that look
  unsafe (e.g. losing more than 1.5% of body weight a week for weeks on end).
