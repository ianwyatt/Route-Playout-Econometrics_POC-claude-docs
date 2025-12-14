# Pipeline Team Handover: Frame Audience MVs

**Date**: 2025-11-29 (Updated)
**Created By**: Claude Code / Ian Wyatt
**Database**: route_poc (MS-01: 192.168.1.34)

---

## Summary

Four materialized views have been created to dramatically improve performance of frame audience queries in the POC UI:

**Playout Aggregation MVs:**
- `mv_playout_frame_day` - Daily playout aggregation
- `mv_playout_frame_hour` - Hourly playout aggregation

**Denormalized Audience MVs (NEW):**
- `mv_frame_audience_daily` - Pre-joined daily frame audience data (3.2M rows)
- `mv_frame_audience_hourly` - Pre-joined hourly frame audience data (46M rows)

## Problem Solved

The frame audience queries were scanning `mv_playout_15min` (67M rows, 14GB) which caused:
- 2+ second query times for large campaigns
- Sequential scans due to large result sets
- Disk spills during sorting

## Solution

Pre-aggregate playout data by campaign/frame/day and campaign/frame/hour:

| Table | Rows | Size | Reduction |
|-------|------|------|-----------|
| mv_playout_15min (source) | 67,000,591 | 14 GB | - |
| mv_playout_frame_day (new) | 1,178,728 | ~50 MB | 57x smaller |
| mv_playout_frame_hour (new) | 16,855,687 | ~700 MB | 4x smaller |

**Performance improvement**: 2,174ms → 8ms (271x faster for daily queries)

---

## MV Definitions

### mv_playout_frame_day (Daily)

```sql
CREATE MATERIALIZED VIEW mv_playout_frame_day AS
SELECT
    buyercampaignref as campaign_id,
    frameid,
    DATE(time_window_start) as date,
    SUM(spot_count) as playout_count,
    COUNT(*) as interval_count,
    MIN(time_window_start) as first_playout,
    MAX(time_window_start) as last_playout
FROM mv_playout_15min
GROUP BY buyercampaignref, frameid, DATE(time_window_start);

-- Indexes
CREATE INDEX idx_mv_playout_frame_day_campaign ON mv_playout_frame_day(campaign_id);
CREATE INDEX idx_mv_playout_frame_day_composite ON mv_playout_frame_day(campaign_id, frameid, date);
CREATE INDEX idx_mv_playout_frame_day_frame_date ON mv_playout_frame_day(frameid, date);
```

### mv_playout_frame_hour (Hourly)

```sql
CREATE MATERIALIZED VIEW mv_playout_frame_hour AS
SELECT
    buyercampaignref as campaign_id,
    frameid,
    date_trunc('hour', time_window_start) as hour_start,
    SUM(spot_count) as playout_count,
    COUNT(*) as interval_count
FROM mv_playout_15min
GROUP BY buyercampaignref, frameid, date_trunc('hour', time_window_start);

-- Indexes
CREATE INDEX idx_mv_playout_frame_hour_campaign ON mv_playout_frame_hour(campaign_id);
CREATE INDEX idx_mv_playout_frame_hour_composite ON mv_playout_frame_hour(campaign_id, frameid, hour_start);
```

---

## Pipeline Integration Required

### Refresh Schedule

Both MVs need to be refreshed when `mv_playout_15min` is updated. Add to the pipeline:

```sql
REFRESH MATERIALIZED VIEW mv_playout_frame_day;
REFRESH MATERIALIZED VIEW mv_playout_frame_hour;
```

### Recommended Refresh Strategy

**Option A: After mv_playout_15min refresh**
```sql
-- In pipeline after mv_playout_15min is refreshed
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_playout_frame_day;
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_playout_frame_hour;
```

Note: CONCURRENTLY requires unique indexes. If needed, add:
```sql
CREATE UNIQUE INDEX idx_mv_playout_frame_day_unique
ON mv_playout_frame_day(campaign_id, frameid, date);

CREATE UNIQUE INDEX idx_mv_playout_frame_hour_unique
ON mv_playout_frame_hour(campaign_id, frameid, hour_start);
```

**Option B: Scheduled refresh**
- Daily refresh during off-peak hours
- Acceptable if slight data lag is tolerable

### Estimated Refresh Time

Based on current data volume:
- mv_playout_frame_day: ~2-3 minutes
- mv_playout_frame_hour: ~5-8 minutes

---

## Columns

| Column | Type | Description |
|--------|------|-------------|
| campaign_id | text | Campaign reference (buyercampaignref) |
| frameid | bigint | Frame ID |
| date | date | Playout date |
| playout_count | bigint | Sum of spot_count for that frame-day |
| interval_count | bigint | Number of 15-min intervals with playouts |
| first_playout | timestamp | First playout time that day |
| last_playout | timestamp | Last playout time that day |

---

## Dependencies

- **Source**: `mv_playout_15min`
- **Used by**: POC UI frame audience queries (`src/db/streamlit_queries.py`)

---

## Verification Queries

```sql
-- Check MV exists and row count
SELECT COUNT(*) FROM mv_playout_frame_day;

-- Check data matches source for a campaign
SELECT
    (SELECT COUNT(*) FROM mv_playout_frame_day WHERE campaign_id = '18295') as mv_rows,
    (SELECT COUNT(DISTINCT (frameid, DATE(time_window_start)))
     FROM mv_playout_15min WHERE buyercampaignref = '18295') as source_rows;

-- Check refresh is needed (compare timestamps)
SELECT
    (SELECT MAX(last_playout) FROM mv_playout_frame_day) as mv_latest,
    (SELECT MAX(time_window_start) FROM mv_playout_15min) as source_latest;
```

---

## Denormalized Audience MVs (NEW)

These MVs pre-join all required tables for frame audience queries, eliminating joins at query time.

### mv_frame_audience_daily

Pre-joined daily frame audience data with demographics and location.

```sql
CREATE MATERIALIZED VIEW mv_frame_audience_daily AS
WITH frame_daily_demographics AS (
    SELECT campaign_id, frameid, date,
        MAX(CASE WHEN demographic_segment = 'all_adults' THEN total_impacts ELSE 0 END) as impacts_all_adults,
        MAX(CASE WHEN demographic_segment = 'abc1' THEN total_impacts ELSE 0 END) as impacts_abc1,
        -- ... other demographics
        MAX(interval_count) as interval_count
    FROM mv_cache_campaign_impacts_frame_day
    GROUP BY campaign_id, frameid, date
)
SELECT
    p.campaign_id, p.frameid, p.date, p.playout_count,
    d.impacts_all_adults, d.impacts_abc1, ... (all demographics),
    rfd.town, rfd.barb_region_name as tv_region,
    rr.release_number as route_release
FROM mv_playout_frame_day p
LEFT JOIN frame_daily_demographics d ON ...
LEFT JOIN route_frames rf ON p.frameid = rf.frameid
LEFT JOIN route_releases rr ON rf.release_id = rr.id
LEFT JOIN route_frame_details rfd ON rf.release_id = rfd.release_id AND rf.frameid = rfd.frameid;

-- Indexes
CREATE INDEX idx_mv_frame_audience_daily_campaign ON mv_frame_audience_daily(campaign_id);
CREATE INDEX idx_mv_frame_audience_daily_composite ON mv_frame_audience_daily(campaign_id, date DESC, impacts_all_adults DESC);
```

**Performance**: 3.8ms vs 33ms (9x faster)

### mv_frame_audience_hourly

Pre-joined hourly frame audience data with demographics and location.

```sql
CREATE MATERIALIZED VIEW mv_frame_audience_hourly AS
-- Same structure as daily but with hour_start instead of date
-- 46M rows

-- Indexes
CREATE INDEX idx_mv_frame_audience_hourly_campaign ON mv_frame_audience_hourly(campaign_id);
CREATE INDEX idx_mv_frame_audience_hourly_composite ON mv_frame_audience_hourly(campaign_id, hour_start DESC, impacts_all_adults DESC);
```

### Refresh Schedule for New MVs

These MVs depend on the underlying MVs. Refresh in order:

```sql
-- After source data is updated:
REFRESH MATERIALIZED VIEW mv_playout_frame_day;
REFRESH MATERIALIZED VIEW mv_playout_frame_hour;
REFRESH MATERIALIZED VIEW mv_cache_campaign_impacts_frame_day;
REFRESH MATERIALIZED VIEW mv_cache_campaign_impacts_frame_1hr;

-- Then refresh denormalized MVs:
REFRESH MATERIALIZED VIEW mv_frame_audience_daily;
REFRESH MATERIALIZED VIEW mv_frame_audience_hourly;
```

**Estimated refresh times:**
- mv_frame_audience_daily: ~2-3 minutes
- mv_frame_audience_hourly: ~10-15 minutes

---

## Contact

For questions about how this MV is used in the POC, contact Ian Wyatt.
