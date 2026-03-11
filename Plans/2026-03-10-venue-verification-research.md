# Mobile Index Venue Verification Research Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Verify that mobile index spikes genuinely correspond to real-world event venues (football, rugby, concerts) by cross-referencing frame coordinates, spike dates, and fixture schedules.

**Architecture:** Seven independent research tasks, each producing a markdown findings document in `docs/Research/venue-verification/`. A single research script per task queries the local PostgreSQL database and writes structured output. A final summary document consolidates all findings with confidence ratings.

**Tech Stack:** Python 3.11, psycopg2, local PostgreSQL (`get_db_connection(use_primary=False)`), haversine distance calculations, web search for fixture verification.

**Research output folder:** `docs/Research/venue-verification/`

**Source brief:** `docs/Documentation/MOBILE_INDEX_VENUE_VERIFICATION_BRIEF.md`

---

## Chunk 1: Database Queries and Distance Calculations

### Task 1: Frame Proximity to Venues

**Files:**
- Create: `scripts/research_venue_proximity.py`
- Output: `docs/Research/venue-verification/01-frame-proximity.md`

**Context:** The brief lists 22 venues with known coordinates. We need to calculate the haversine distance between each spiking frame (average_index > 5.0) and the nearest venue, then classify: <500m strong, 500m–1km likely, >1km needs explanation.

- [ ] **Step 1: Create the proximity research script**

The script should:
1. Query all frames from `route_frame_details` where the frame appears in `mobile_volume_index` with `average_index > 5.0`
2. Define the 22 venue coordinates from the brief (hardcoded list)
3. Calculate haversine distance from each frame to every venue
4. Find the nearest venue for each frame
5. Classify into proximity bands (<500m, 500m–1km, 1–2km, >2km)
6. Write results to stdout in markdown format

Key function — haversine (no external dependency needed):
```python
import math

def haversine_m(lat1, lon1, lat2, lon2):
    """Distance in metres between two lat/lon points."""
    R = 6_371_000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
```

Key SQL:
```sql
SELECT DISTINCT r.frameid, r.town, r.latitude, r.longitude, r.address, r.postcode, r.poi
FROM route_frame_details r
WHERE r.frameid IN (
    SELECT DISTINCT frameid FROM mobile_volume_index WHERE average_index > 5.0
)
ORDER BY r.town
```

- [ ] **Step 2: Run the script**

```bash
cd /Users/ianwyatt/PycharmProjects/Route-Playout-Econometrics_POC
uv run python scripts/research_venue_proximity.py > docs/Research/venue-verification/01-frame-proximity.md
```

- [ ] **Step 3: Review output and fix any issues**

Check that:
- Frame coordinates are sensible (UK lat/lon range: 49–61°N, -8–2°E)
- Distance calculations pass a sanity check (known distances between venues)
- Classification bands contain reasonable counts

---

### Task 2: Sunderland Smoking Gun Verification

**Files:**
- Create: `scripts/research_sunderland_deep_dive.py`
- Output: `docs/Research/venue-verification/02-sunderland-smoking-gun.md`

**Context:** Frame `1234860534` hit 35x index at 22:00 on a specific date, with a clear ingress ramp from 15:00. Three adjacent frames spike simultaneously. We need to confirm the `date_2024` (original date), check Sunderland AFC fixtures / Stadium of Light events for that date, and confirm frame proximity to the stadium (54.9146, -1.3882).

- [ ] **Step 1: Create the Sunderland deep dive script**

Key queries:
1. Get the `date_2024` for frame 1234860534 on its peak day
2. Get the full hourly profile for that frame on the peak date
3. Get the same hourly profile for the two adjacent frames (1234860069, 1234860070)
4. Get frame coordinates and calculate distance to Stadium of Light
5. List ALL spike dates (index > 3.0) for these three frames with their `date_2024` values

```sql
-- Get original date and full hourly profile for peak day
SELECT date_2024, date_2025, hour, average_index, median_index
FROM mobile_volume_index
WHERE frameid = 1234860534
ORDER BY average_index DESC
LIMIT 1;

-- All spike dates for the three Sunderland frames
SELECT m.frameid, m.date_2024, m.date_2025, TO_CHAR(m.date_2024, 'Dy') AS day_2024,
       COUNT(*) AS spike_hours, ROUND(MAX(m.average_index)::numeric, 2) AS peak_index
FROM mobile_volume_index m
WHERE m.frameid IN (1234860534, 1234860069, 1234860070)
  AND m.average_index > 3.0
GROUP BY m.frameid, m.date_2024, m.date_2025
ORDER BY m.date_2024;
```

- [ ] **Step 2: Run the script**

```bash
uv run python scripts/research_sunderland_deep_dive.py > docs/Research/venue-verification/02-sunderland-smoking-gun.md
```

- [ ] **Step 3: Web search for Sunderland fixtures**

Once we have the `date_2024` values, search for:
- Sunderland AFC home fixtures on those dates
- Stadium of Light concert/event listings for those dates
- Note: Sunderland were in the Championship in 2023/24 and promoted to Premier League for 2024/25

---

### Task 3: Stretford / Old Trafford Pattern Verification

**Files:**
- Create: `scripts/research_stretford_pattern.py`
- Output: `docs/Research/venue-verification/03-stretford-old-trafford.md`

**Context:** 9 frames near Old Trafford spike on 28 separate days. We need to determine what percentage of those 28 days correspond to Manchester United home fixtures.

- [ ] **Step 1: Create the Stretford pattern script**

Key queries:
```sql
-- All spike dates for Stretford frames
SELECT DISTINCT m.date_2025, m.date_2024,
       TO_CHAR(m.date_2024, 'Dy') AS day_name,
       TO_CHAR(m.date_2024, 'DD Mon YYYY') AS date_formatted,
       COUNT(DISTINCT m.frameid) AS frames,
       ROUND(AVG(m.average_index)::numeric, 2) AS avg_index,
       ROUND(MAX(m.average_index)::numeric, 2) AS max_index
FROM mobile_volume_index m
JOIN route_frame_details r ON m.frameid = r.frameid
WHERE r.town = 'Stretford' AND m.average_index > 3.0
GROUP BY m.date_2025, m.date_2024
ORDER BY m.date_2024;

-- Frame coordinates for distance calculation
SELECT DISTINCT frameid, latitude, longitude, address, postcode
FROM route_frame_details
WHERE town = 'Stretford';
```

Also calculate distance from each frame to Old Trafford (53.4631, -2.2913).

- [ ] **Step 2: Run the script**

```bash
uv run python scripts/research_stretford_pattern.py > docs/Research/venue-verification/03-stretford-old-trafford.md
```

- [ ] **Step 3: Cross-reference with Man Utd 2023/24 fixtures**

Web search for Manchester United home fixtures 2023/24 season (Premier League + FA Cup + League Cup + Europa League/Champions League). Calculate match percentage: `matched_dates / 28 * 100`.

Target: >80% match = very strong evidence.

---

### Task 4: Glasgow North Cluster Verification

**Files:**
- Create: `scripts/research_glasgow_cluster.py`
- Output: `docs/Research/venue-verification/04-glasgow-cluster.md`

**Context:** 6+ frames at 18x index at 23:00 on 12–13 July 2025. Could be Celtic Park or Ibrox match/event, or a summer concert.

- [ ] **Step 1: Create Glasgow cluster script**

Key queries:
1. Get `date_2024` for the Glasgow spike dates
2. Full hourly profiles for all spiking Glasgow North frames on those dates
3. Frame coordinates — distance to Celtic Park (55.8497, -4.2055) and Ibrox (55.8532, -4.3092)
4. All other spike dates for these frames (to see if there's a pattern beyond just one weekend)

- [ ] **Step 2: Run and capture output**

- [ ] **Step 3: Web search for Glasgow events on the original 2024 dates**

Check: Celtic/Rangers fixtures, TRNSMT festival, summer concerts at Hampden/Celtic Park/Ibrox.

---

## Chunk 2: Broader Pattern Verification

### Task 5: Overnight Flat Pattern Investigation

**Files:**
- Create: `scripts/research_overnight_pattern.py`
- Output: `docs/Research/venue-verification/05-overnight-pattern.md`

**Context:** 420 frames show consistent 3.5x index between 0–4am. Need to determine if these are near nightlife districts, transport hubs, or a data artefact.

- [ ] **Step 1: Create overnight pattern script**

The brief provides the exact SQL query. Run it and additionally:
1. Count how many overnight-only spikers are in each town
2. Get POI (point of interest) data from `route_frame_details` for these frames
3. Check if `environment_name` gives clues (e.g., "City Centre", "Transport")
4. Compare average index at 0–4am vs 8–10am vs 18–22pm for these frames

```sql
-- From the brief: frames that spike overnight but NOT during match hours
WITH overnight_spikers AS (
    SELECT frameid FROM mobile_volume_index
    WHERE average_index > 3.0 AND hour BETWEEN 0 AND 4
    GROUP BY frameid HAVING COUNT(*) > 10
),
evening_spikers AS (
    SELECT frameid FROM mobile_volume_index
    WHERE average_index > 3.0 AND hour BETWEEN 18 AND 22
    GROUP BY frameid HAVING COUNT(*) > 5
)
SELECT DISTINCT r.frameid, r.town, r.latitude, r.longitude,
       r.poi, r.environment_name, r.address
FROM overnight_spikers o
JOIN route_frame_details r ON o.frameid = r.frameid
WHERE o.frameid NOT IN (SELECT frameid FROM evening_spikers)
ORDER BY r.town;
```

- [ ] **Step 2: Run and capture**

- [ ] **Step 3: Classify results**

Group the overnight frames into categories:
- City centre / nightlife area
- Transport hub (railway station, airport)
- Residential (possible artefact)
- Other

---

### Task 6: Top Spike Dates Cross-Reference

**Files:**
- Create: `scripts/research_top_spike_dates.py`
- Output: `docs/Research/venue-verification/06-top-spike-dates.md`

**Context:** Get the top 30 spike dates across all frames, map to `date_2024`, and cross-reference against known events.

- [ ] **Step 1: Create spike dates script**

From the brief:
```sql
SELECT DISTINCT date_2025, date_2024,
       TO_CHAR(date_2024, 'Dy') AS day_name,
       COUNT(*) AS spike_count,
       COUNT(DISTINCT frameid) AS frames
FROM mobile_volume_index
WHERE average_index > 3.0
GROUP BY date_2025, date_2024
ORDER BY spike_count DESC
LIMIT 30;
```

Additionally, for each top date, show which towns the spikes are concentrated in.

- [ ] **Step 2: Run and capture**

- [ ] **Step 3: Cross-reference dates**

For each date, check:
- Premier League matchday (Saturday 15:00 / Sunday various)
- EFL Championship matches
- Bank holidays (26 Aug 2024 = Summer Bank Holiday)
- International fixtures (Twickenham, Wembley)
- Major concerts/festivals

---

### Task 7: Full Venue Distance Matrix

**Files:**
- Create: `scripts/research_venue_distance_matrix.py`
- Output: `docs/Research/venue-verification/07-venue-distance-matrix.md`

**Context:** Build a complete matrix: for each of the 22 venues, find all frames within 1km and report their spike characteristics.

- [ ] **Step 1: Create distance matrix script**

For each venue:
1. Find all frames within 1km using haversine
2. For matched frames, query spike statistics from `mobile_volume_index`
3. Report: frame count, spike days, average peak index, spike day-of-week distribution

This confirms or denies whether each venue has nearby advertising frames that spike on event days.

- [ ] **Step 2: Run and capture**

- [ ] **Step 3: Identify venues WITHOUT nearby spiking frames**

Some venues may have no OOH advertising frames nearby — document these gaps.

---

## Chunk 3: Consolidation

### Task 8: Consolidated Findings Report

**Files:**
- Create: `docs/Research/venue-verification/00-SUMMARY.md`

**Context:** Bring together all 7 investigations into a single summary with confidence ratings.

- [ ] **Step 1: Create summary document**

Structure:
```markdown
# Mobile Index Venue Verification — Summary

## Methodology
## Confidence Ratings
## Venue-by-Venue Results (table with distance, match%, confidence)
## Key Findings
## Anomalies and Open Questions
## Recommendations
```

- [ ] **Step 2: Assign confidence ratings**

| Rating | Criteria |
|--------|----------|
| Confirmed | Frame <500m from venue AND >80% spike dates match fixtures |
| Likely | Frame <1km from venue AND >50% date match |
| Plausible | Frame <2km OR partial date match |
| Unconfirmed | No geographic or temporal correlation |
| Alternative | Evidence points to non-sporting explanation (nightlife, transport) |

- [ ] **Step 3: Review and polish**

Ensure all cross-referenced dates are documented with sources.

---

## Execution Notes

**Database:** All queries run against local PostgreSQL via `get_db_connection(use_primary=False)`.

**Web searches:** Tasks 2, 3, 4, and 6 require web searches to verify fixtures. Use 2023/24 season schedules since the source data uses 2024 dates mapped to 2025.

**Parallelism:** Tasks 1–4 are independent and can run as parallel subagents. Tasks 5–6 are independent of each other but can also run in parallel. Task 7 depends on Task 1's output for validation. Task 8 depends on all others.

**Existing scripts:** `scripts/research_event_peaks.py` and `scripts/research_overall_impact.py` provide the established pattern for research scripts (import path setup, `run_query()` helper, `get_db_connection()`). Follow the same structure.

**Output folder:** All research outputs go to `docs/Research/venue-verification/` in the docs repo (`Route-Playout-Econometrics_POC-claude-docs`).
