# Mobile Index Venue Verification — Follow-Up Research

## Context

You are continuing research on the mobile volume index for an OOH (out-of-home) advertising econometrics project. A previous research session completed 7 investigations cross-referencing mobile index spikes against real-world events and venues. The findings are in `docs/Research/venue-verification/` (8 files, summary at `00-SUMMARY.md`).

The executive summary is at `docs/Documentation/mobile-index/executive-summary.md`. The full research findings are at `docs/Documentation/mobile-index/research-findings.md`. The venue verification brief that guided the first round is at `docs/Documentation/mobile-index/venue-verification-brief.md`.

## How the Index Is Constructed

The mobile volume index is built from O2 mobile device people counts at Output Area (OA) level. Understanding the construction is critical for interpreting patterns correctly.

### Pipeline

1. **Raw O2 data** provides hourly people counts per Output Area per date (`cristina.o2_people_counts_filtered_oa_q234_with_day_of_the_week`)
2. **Overnight smoothing**: The source data has a single count at hour 0 (midnight) covering 00:00–04:59. This is divided by 5 and distributed evenly across hours 0–4. Hours 5–23 use raw counts. This means overnight index values are uniform across 5 hours, not actual per-hour measurements.
3. **Day-of-week baseline**: For each OA × day-of-week × hour, the mean and median people count across ALL dates in the dataset (Apr–Dec 2024) is calculated. Monday 15:00 baseline uses all Mondays at 15:00, Saturday 15:00 baseline uses all Saturdays at 15:00, etc.
4. **Index = actual / baseline**: `average_index = actual_people / mean_baseline`, `median_index = actual_people / median_baseline`
5. **Frame mapping**: OA → frame via `oa_frames_map`. Multiple frames in the same OA share identical index values.

### Critical Implications for Research

**Day-of-week normalisation explains venue signal variation.** A Saturday football match is compared against the average *Saturday* — not the average day. If a venue hosts events on 50% of Saturdays, the Saturday baseline already reflects event-level footfall. This is the MI working as designed: it measures deviation from typical patterns. Route models audience based on average behaviour, so if matches are a normal part of a venue's weekly pattern, Route's audiences already incorporate that footfall. The MI correctly shows little deviation at high-frequency venues (Wembley max 1.62x) and large deviation at infrequent-use venues (Sunderland max 35x). If Route's audience models do not fully capture regular event footfall at busy stadiums, that is a limitation of Route's data inputs, not the MI methodology.

**Event days are included in the baseline.** Old Trafford's Saturday baseline includes the ~10 Saturday home matches in the dataset. This means each individual match appears as a smaller deviation than it would against a non-event baseline. This is intentional — Route's audiences model average behaviour including regular events. The 6–11x spikes at Stretford represent the deviation *above* what is typical, not the absolute uplift.

**OA-level granularity.** The index is per Output Area, not per frame. Adjacent footfall generators in the same OA produce identical index values. Old Trafford stadium and Trafford Centre shopping complex share an OA — a Saturday match and a Saturday shopping trip both raise the same index. This cannot be distinguished at the data level.

**Overnight smoothing.** Post-event egress at 23:00–01:00 would appear spread across 00:00–04:00 in the index. Transport hub overnight spikes (Lime Street, Reading) are real in total magnitude but artificially uniform across 5 hours.

Full SQL construction: `docs/Documentation/mobile-index/sql-construction-audit.md`

---

## Database Access

```python
import psycopg2, psycopg2.extras
from src.db.queries.connection import get_db_connection
conn = get_db_connection(use_primary=False)
cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
```

Key tables:
- `mobile_volume_index` — 99.87M rows: `frameid, date_2024, date_2025, hour, average_index, median_index`
- `route_frame_details` — frame metadata: `frameid, town, region, conurbation_name, latitude, longitude, address, postcode, poi, environment_name, barb_region_name`
- `mv_frame_audience_daily` — daily impacts per frame: `frameid, date, campaign_id, impacts_all_adults, playout_count, town, tv_region`
- `mv_campaign_browser` — 836 campaigns: `campaign_id, primary_brand, primary_media_owner`
- `cache_mi_frame_hourly` — 104.7M rows: hourly mobile-indexed impacts

**Important:** `date_2024` contains the original dates (the source data maps 2024 dates to 2025 via `date_2025`). Always use `date_2024` when cross-referencing against real-world fixture calendars.

## Research Tasks

### 1. The Unexplained 58% — Classify Non-Venue Spikes

273 frames spike above 5x with no stadium within 2km. These are potentially more commercially valuable than the event signal.

**Task:** Pull these 273 frames and classify them by `environment_name`, `poi`, `town`, and proximity to transport hubs, shopping centres, and high streets. Look for clustering patterns. Are they near retail parks? Train stations? Nightlife districts? City centre roadside? Create a taxonomy of non-venue spike drivers.

```sql
-- Frames that spike above 5x but are NOT within 2km of any of the 22 venues
-- (use the venue coordinates from docs/Research/venue-verification/07-venue-distance-matrix.md)
-- Then join to route_frame_details for environment_name, poi, town
```

### 2. Identify the #1 Spike Date — 27 Oct 2024

This is the biggest spike date nationally (735 spike-hours, 152 frames) but wasn't matched to a specific event. Liverpool (40 frames) and Manchester (31 frames) dominate.

**Task:** Pull the top spiking towns and frames for this date. The `date_2024` will be 27 Oct 2024 (a Sunday) or possibly 26 Oct 2024 (Saturday). Cross-reference against Premier League fixtures for that weekend. Web search for "Premier League fixtures 26 October 2024" and "27 October 2024". Likely candidates: Liverpool vs Arsenal, Man City home game, or a combination of Saturday 3pm kickoffs carrying into Sunday.

### 3. Cardiff Deep Dive — Principality Stadium

580 spike-days, 18 frames within 500m — the densest venue coverage in the dataset.

**Task:** Pull all spike dates (index > 3.0) for the Cardiff frames within 1km of Principality Stadium (lat: 51.4782, lon: -3.1826). Map `date_2024` values and cross-reference against:
- Wales rugby internationals (Six Nations, Autumn internationals)
- Cardiff City FC fixtures
- Concerts and events at Principality Stadium
- Major events (e.g. Anthony Joshua fights, Speedway GP)

What proportion of spikes are rugby vs football vs concerts vs other? Cardiff hosts far more diverse events than a typical football-only stadium.

### 4. MI Coverage Gap Analysis

Only 554 of 7,202 frames within 1km of the 22 venues have mobile index data (7.7%). Some venues have virtually zero MI coverage.

**Task:** For each of the 22 venues, count: (a) total OOH frames within 1km, (b) frames with MI data, (c) MI coverage percentage. Then do the same analysis at a regional level — is MI coverage geographically biased toward London/South East, or evenly distributed? Map the coverage density to identify systematic gaps.

```sql
-- Count frames with/without MI data by region
SELECT r.region,
       COUNT(DISTINCT r.frameid) as total_frames,
       COUNT(DISTINCT m.frameid) as mi_frames,
       ROUND(100.0 * COUNT(DISTINCT m.frameid) / NULLIF(COUNT(DISTINCT r.frameid), 0), 1) as pct
FROM route_frame_details r
LEFT JOIN (SELECT DISTINCT frameid FROM mobile_volume_index) m ON r.frameid = m.frameid
GROUP BY r.region
ORDER BY total_frames DESC
```

### 5. Seasonal/Weather Patterns

Do spikes correlate with seasons or just events?

**Task:** For frames NOT near any venue (the 273 from task 1), compare average index values by month and day-of-week. Are summer months higher than winter? Do weekday patterns differ from weekends outside of event contexts? This tests whether the mobile index captures weather/seasonal footfall variation beyond just events.

## Output

Save each investigation as a numbered markdown file in `docs/Research/venue-verification/` following the existing pattern (e.g. `08-non-venue-spikes.md`, `09-top-spike-date.md`, etc.). Update `00-SUMMARY.md` with new findings.

Write standalone Python scripts to `scripts/` following the existing pattern (e.g. `scripts/research_non_venue_spikes.py`). Each script should connect to the local database, run its queries, and print results to stdout.

## Important Notes

- Use British English spelling throughout
- All Python files need ABOUTME headers
- The `route_frame_details` table has duplicate rows per frame with slight `environment_name` differences — use `DISTINCT` or `MAX()` when aggregating
- Web searches are needed for fixture verification (tasks 2 and 3)
- Close database connections when done
