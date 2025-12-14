# Materialized View Fix - Frame Audience Location Data

**Date**: November 29, 2025
**Applied To**: MS01 (192.168.1.34) and Local databases

## Summary

Fixed a critical bug where frame audience tables (daily/hourly) showed "Unknown, Unknown" for location data. The root cause was an incorrect join between the cache tables and `route_frame_details`.

## Problem

Frame Audiences tabs displayed:
- Location: "Unknown, Unknown"
- TV Region: "Unknown"

But Campaign Frames tab showed correct location data.

## Root Cause

The join logic was incorrect:

```sql
-- WRONG: Using id = route_release_id
LEFT JOIN route_releases rr ON rr.id = d.route_release_id
```

The issue:
- `route_releases.id` = surrogate key (1, 2, 3, 4, 5...)
- `cache_route_impacts_15min_by_demo.route_release_id` = numeric release number (55, 56)
- `route_releases.release_number` = 'R55', 'R56'

So `id=55` doesn't match any row in `route_releases` (which only has ids 1-8).

## Solution

Changed join to use `release_number`:

```sql
-- CORRECT: Match numeric release to release_number
LEFT JOIN route_releases rr ON rr.release_number = 'R' || d.route_release_id::text
LEFT JOIN route_frame_details rfd ON rr.id = rfd.release_id AND p.frameid = rfd.frameid
```

## MVs Modified

### 1. mv_cache_campaign_impacts_frame_day

Added `route_release_id` column to propagate release through aggregation:

```sql
DROP MATERIALIZED VIEW IF EXISTS mv_frame_audience_daily CASCADE;
DROP MATERIALIZED VIEW IF EXISTS mv_cache_campaign_impacts_frame_day CASCADE;

CREATE MATERIALIZED VIEW mv_cache_campaign_impacts_frame_day AS
SELECT
    campaign_id,
    frameid,
    date(time_window_start) AS date,
    demographic_segment,
    sum(impacts) AS total_impacts,
    count(*) AS interval_count,
    MAX(route_release_id) AS route_release_id  -- NEW COLUMN
FROM cache_route_impacts_15min_by_demo
GROUP BY campaign_id, frameid, date(time_window_start), demographic_segment;

CREATE INDEX idx_mv_cache_frame_day_lookup
    ON mv_cache_campaign_impacts_frame_day(campaign_id, frameid, date);
```

### 2. mv_cache_campaign_impacts_frame_1hr

Added `route_release_id` column:

```sql
DROP MATERIALIZED VIEW IF EXISTS mv_frame_audience_hourly CASCADE;
DROP MATERIALIZED VIEW IF EXISTS mv_cache_campaign_impacts_frame_1hr CASCADE;

CREATE MATERIALIZED VIEW mv_cache_campaign_impacts_frame_1hr AS
SELECT
    campaign_id,
    frameid,
    date_trunc('hour', time_window_start) AS hour_start,
    demographic_segment,
    sum(impacts) AS total_impacts,
    count(*) AS interval_count,
    MAX(route_release_id) AS route_release_id  -- NEW COLUMN
FROM cache_route_impacts_15min_by_demo
GROUP BY campaign_id, frameid, date_trunc('hour', time_window_start), demographic_segment;

CREATE INDEX idx_mv_cache_frame_1hr_lookup
    ON mv_cache_campaign_impacts_frame_1hr(campaign_id, frameid, hour_start);
```

### 3. mv_frame_audience_daily

Recreated with correct join logic:

```sql
CREATE MATERIALIZED VIEW mv_frame_audience_daily AS
WITH frame_daily_demographics AS (
    SELECT
        campaign_id, frameid, date,
        MAX(CASE WHEN demographic_segment = 'all_adults' THEN total_impacts ELSE 0 END) AS impacts_all_adults,
        MAX(CASE WHEN demographic_segment = 'abc1' THEN total_impacts ELSE 0 END) AS impacts_abc1,
        MAX(CASE WHEN demographic_segment = 'c2de' THEN total_impacts ELSE 0 END) AS impacts_c2de,
        MAX(CASE WHEN demographic_segment = 'age_15_34' THEN total_impacts ELSE 0 END) AS impacts_age_15_34,
        MAX(CASE WHEN demographic_segment = 'age_35_plus' THEN total_impacts ELSE 0 END) AS impacts_age_35_plus,
        MAX(CASE WHEN demographic_segment = 'main_shopper' THEN total_impacts ELSE 0 END) AS impacts_main_shopper,
        MAX(CASE WHEN demographic_segment = 'children_hh' THEN total_impacts ELSE 0 END) AS impacts_children_hh,
        MAX(interval_count) AS interval_count,
        MAX(route_release_id) AS route_release_id
    FROM mv_cache_campaign_impacts_frame_day
    GROUP BY campaign_id, frameid, date
)
SELECT
    p.campaign_id, p.frameid, p.date, p.playout_count,
    COALESCE(d.impacts_all_adults, 0) AS impacts_all_adults,
    COALESCE(d.impacts_abc1, 0) AS impacts_abc1,
    COALESCE(d.impacts_c2de, 0) AS impacts_c2de,
    COALESCE(d.impacts_age_15_34, 0) AS impacts_age_15_34,
    COALESCE(d.impacts_age_35_plus, 0) AS impacts_age_35_plus,
    COALESCE(d.impacts_main_shopper, 0) AS impacts_main_shopper,
    COALESCE(d.impacts_children_hh, 0) AS impacts_children_hh,
    COALESCE(d.interval_count, 0) AS interval_count,
    COALESCE(rfd.town, 'Unknown') AS town,
    COALESCE(rfd.barb_region_name, 'Unknown') AS tv_region,
    rr.release_number AS route_release
FROM mv_playout_frame_day p
LEFT JOIN frame_daily_demographics d
    ON p.campaign_id = d.campaign_id::text AND p.frameid = d.frameid AND p.date = d.date
LEFT JOIN route_releases rr
    ON rr.release_number = 'R' || d.route_release_id::text  -- CORRECT JOIN
LEFT JOIN route_frame_details rfd
    ON rr.id = rfd.release_id AND p.frameid = rfd.frameid;

CREATE INDEX idx_mv_frame_audience_daily_campaign ON mv_frame_audience_daily(campaign_id);
CREATE INDEX idx_mv_frame_audience_daily_lookup ON mv_frame_audience_daily(campaign_id, frameid, date);
```

### 4. mv_frame_audience_hourly

Same pattern as daily:

```sql
CREATE MATERIALIZED VIEW mv_frame_audience_hourly AS
WITH frame_hourly_demographics AS (
    SELECT
        campaign_id, frameid, hour_start,
        MAX(CASE WHEN demographic_segment = 'all_adults' THEN total_impacts ELSE 0 END) AS impacts_all_adults,
        -- ... other demographics ...
        MAX(route_release_id) AS route_release_id
    FROM mv_cache_campaign_impacts_frame_1hr
    GROUP BY campaign_id, frameid, hour_start
)
SELECT
    p.campaign_id, p.frameid, p.hour_start, p.playout_count,
    -- ... impact columns ...
    COALESCE(rfd.town, 'Unknown') AS town,
    COALESCE(rfd.barb_region_name, 'Unknown') AS tv_region,
    rr.release_number AS route_release
FROM mv_playout_frame_hour p
LEFT JOIN frame_hourly_demographics d
    ON p.campaign_id = d.campaign_id::text AND p.frameid = d.frameid AND p.hour_start = d.hour_start
LEFT JOIN route_releases rr
    ON rr.release_number = 'R' || d.route_release_id::text  -- CORRECT JOIN
LEFT JOIN route_frame_details rfd
    ON rr.id = rfd.release_id AND p.frameid = rfd.frameid;

CREATE INDEX idx_mv_frame_audience_hourly_campaign ON mv_frame_audience_hourly(campaign_id);
CREATE INDEX idx_mv_frame_audience_hourly_lookup ON mv_frame_audience_hourly(campaign_id, frameid, hour_start);
```

## Important Data Model Note

### Why This Matters

A campaign may span multiple Route releases (typically 2, sometimes 3). Each release covers ~3 months:

| Release | Period |
|---------|--------|
| R55 | Jun 30 - Sep 28, 2025 |
| R56 | Sep 29 - Jan 4, 2026 |

When audience impacts are calculated for a playout, they're tied to a specific release. The frame's location data must be retrieved from `route_frame_details` using that **same release**.

**Incorrect**: Using any release or the latest release for the frame
**Correct**: Using the release stored in `route_release_id` from the cache

## Verification

After fix:
```sql
SELECT frameid, date, town, tv_region, route_release
FROM mv_frame_audience_daily
WHERE campaign_id = '16699'
LIMIT 5;

-- Results:
--   frameid   |    date    |     town      |    tv_region    | route_release
-- ------------+------------+---------------+-----------------+---------------
--  1234854967 | 2025-08-25 | Milton Keynes | East Of England | R55
--  1234854967 | 2025-08-26 | Milton Keynes | East Of England | R55
```

Row counts (campaign 16699):
- Daily: 6,364 rows (0 duplicates)
- Hourly: 120,011 rows (0 duplicates)

## Refresh Schedule

These MVs should be refreshed when the underlying cache data is updated. They depend on:
- `cache_route_impacts_15min_by_demo` (source data)
- `mv_playout_frame_day` / `mv_playout_frame_hour` (playout aggregation)
- `route_releases` (release lookup)
- `route_frame_details` (frame location data)

---
*For questions, contact the POC team.*
