# Performance Optimisation Plan

**Date:** 9 March 2026
**Branch:** `feature/mobile-volume-index`
**Trigger:** Cache build for 100M row mobile index takes ~2 hours; UI queries uncached

---

## Problem Summary

Three performance bottlenecks identified:

1. **Cache build** — 6 identical 416M-row JOINs run sequentially (~15-20 min each = ~2 hours total)
2. **UI queries** — Mobile index queries are completely uncached; 3-5 DB connections per tab render
3. **Per-rerender overhead** — `mobile_index_table_exists()`, `get_campaign_header_info_sync()`, and `get_mobile_index_coverage_sync()` fire on every Streamlit widget interaction with no caching

---

## Phase 1: Immediate Wins (no DB dependency, can do now)

### 1.1 Cache per-rerender queries in `app.py`

Wrap these three calls that fire on **every** Streamlit rerender:

| Call | Location | Fix |
|------|----------|-----|
| `mobile_index_table_exists()` | `app.py:294` | `@st.cache_data(ttl=3600)` wrapper |
| `get_mobile_index_coverage_sync()` | `app.py:296` | `@st.cache_data(ttl=3600)` wrapper |
| `get_campaign_header_info_sync()` | `app.py:219` | `@st.cache_data(ttl=3600)` wrapper |

### 1.2 Cache all mobile index UI queries

**Zero** MI queries have `@st.cache_data`. Add wrappers (TTL 3600s) for:

| Function | Called in |
|----------|----------|
| `get_daily_impacts_with_mobile_index_sync` | overview, time_series, reach_grp, exec_summary |
| `get_frame_totals_with_mobile_index_sync` | overview, geographic, detailed_analysis |
| `get_weekly_impacts_with_mobile_index_sync` | reach_grp, time_series |
| `get_frame_daily_with_mobile_index_sync` | detailed_analysis |
| `get_frame_hourly_with_mobile_index_sync` | detailed_analysis |
| `get_hourly_impacts_with_mobile_index_sync` | (currently unused but available) |

### 1.3 Cache geographic tab queries

`get_frame_geographic_data_sync`, `get_regional_impacts_sync`, `get_environment_impacts_sync` fire 3-4 uncached connections on every demographic dropdown change.

### 1.4 Cache time_series demographics query

`get_available_demographics_for_campaign_sync` at `time_series.py:50` is uncached. Geographic tab already caches the same query correctly.

### 1.5 Deduplicate daily impacts in overview

`overview.py:281` calls `get_daily_impacts_sync()` directly. A cached version `load_daily_impacts()` already exists in `app.py`. Use it.

### 1.6 Reduce redundant `fill_date_gaps_with_boundary_zeros` calls

`time_series.py` calls this 5 times per render with MI enabled. Compute once for mobile data, reuse for chart and bar traces.

---

## Phase 2: Cache Build Optimisation

### 2.1 Single intermediate JOIN table

The 6 cache populate queries all run the same expensive operation:

```sql
FROM cache_route_impacts_15min_by_demo c
LEFT JOIN mobile_volume_index m
    ON c.frameid = m.frameid
    AND DATE(c.time_window_start) = m.date_2025
    AND EXTRACT(HOUR FROM c.time_window_start)::int = m.hour
WHERE c.campaign_id IN (
    SELECT DISTINCT campaign_id FROM cache_route_impacts_15min_by_demo
    WHERE frameid IN (SELECT DISTINCT frameid FROM mobile_volume_index)
)
```

**Fix:** Create a single temp table with the pre-joined, pre-extracted data:

```sql
CREATE TEMP TABLE mi_join_base AS
SELECT
    c.frameid, c.campaign_id, c.demographic_segment, c.impacts,
    DATE(c.time_window_start) AS date,
    EXTRACT(DOW FROM c.time_window_start)::int AS day_of_week,
    EXTRACT(HOUR FROM c.time_window_start)::int AS hour,
    EXTRACT(ISOYEAR FROM c.time_window_start)::int AS iso_year,
    EXTRACT(WEEK FROM c.time_window_start)::int AS iso_week,
    DATE_TRUNC('week', c.time_window_start)::date AS week_start,
    COALESCE(m.average_index, 1.0) AS average_index,
    COALESCE(m.median_index, 1.0) AS median_index
FROM cache_route_impacts_15min_by_demo c
LEFT JOIN mobile_volume_index m
    ON c.frameid = m.frameid
    AND DATE(c.time_window_start) = m.date_2025
    AND EXTRACT(HOUR FROM c.time_window_start)::int = m.hour
WHERE c.campaign_id IN (
    SELECT DISTINCT campaign_id FROM cache_route_impacts_15min_by_demo
    WHERE frameid IN (SELECT DISTINCT frameid FROM mobile_volume_index)
);
```

Then each cache table is a simple `GROUP BY` aggregation — no JOIN, no subquery.

**Expected improvement:** ~2 hours -> ~30-40 minutes (1 expensive JOIN + 6 cheap aggregations).

### 2.2 Index the temp table

After creating `mi_join_base`, add indexes for the aggregation queries:

```sql
CREATE INDEX idx_mi_base_campaign_demo ON mi_join_base (campaign_id, demographic_segment);
CREATE INDEX idx_mi_base_frame ON mi_join_base (frameid, campaign_id, demographic_segment);
```

### 2.3 Make the source JOIN sargable (future)

The `DATE()` and `EXTRACT(HOUR ...)` function wrappers prevent index use. Options:
- Functional index on `cache_route_impacts_15min_by_demo`:
  `CREATE INDEX idx_impacts_date_hour ON cache_route_impacts_15min_by_demo (frameid, DATE(time_window_start), EXTRACT(HOUR FROM time_window_start)::int)`
- Or add materialised `playout_date` and `playout_hour` columns

---

## Phase 3: Connection and Query Optimisation

### 3.1 Connection pooling

Replace per-call `psycopg2.connect()` with `psycopg2.pool.SimpleConnectionPool(1, 5)` in `connection.py`. Eliminates TCP handshake overhead on the 3-5 connections per tab render.

### 3.2 Verify/add missing indexes

| Table | Index to verify/add |
|-------|-------------------|
| `mv_cache_campaign_impacts_day` | `(campaign_id, demographic_segment)` |
| `mv_cache_campaign_impacts_1hr` | `(campaign_id, demographic_segment)` |
| `cache_campaign_reach_day_cumulative` | `(campaign_id)` |
| `mv_frame_audience_daily` | `(campaign_id)` |
| `mv_frame_audience_hourly` | `(campaign_id)` |

### 3.3 Fix `get_demographic_count_sync`

Currently does `COUNT(DISTINCT demographic_segment)` on 416M rows. Replace with query against `mv_cache_campaign_impacts_frame` (tiny table) or hardcode with long TTL.

### 3.4 Refactor `get_frame_audience_table_sync`

Currently reads `mv_playout_15min` (8.6 GB) via CTE for date ranges. Could use `mv_frame_audience_daily` instead.

---

## What We Can Do Right Now (while cache builds)

All Phase 1 items are pure Python/Streamlit changes — no DB dependency:

1. Add `@st.cache_data` wrappers for MI queries in `app.py`
2. Cache `mobile_index_table_exists`, `get_mobile_index_coverage_sync`, `get_campaign_header_info_sync`
3. Cache geographic queries
4. Cache demographics query in time_series
5. Deduplicate daily impacts in overview
6. Reduce `fill_date_gaps_with_boundary_zeros` calls in time_series
7. Write the optimised `build_cache` with temp table approach (ready to test after current build)

---

## Connection Count Summary (current vs after Phase 1)

| Tab | Current (MI on) | After Phase 1 |
|-----|----------------|---------------|
| App-level (every rerender) | 2-3 | 0 (cached) |
| Overview | 3 | 0 (cached) |
| Reach & GRP | 2 | 0 (cached) |
| Daily & Hourly | 5 | 0 (cached) |
| Geographic | 4 | 0 (cached) |
| Frame Audiences | 1-2 | 0 (cached) |
| Executive Summary | 1 | 0 (cached) |
| **Total per interaction** | **16-20** | **0** (first load only) |

---

*Phase 1 should take ~1-2 hours to implement and will make the app feel instant.*
