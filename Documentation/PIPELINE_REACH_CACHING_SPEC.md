# Pipeline Reach Caching Specification

**Document Purpose**: Specification for the route-playout-pipeline project to implement automated reach data backfilling and caching.

**Target Repository**: `route-playout-pipeline` (separate GitHub repo)

**Last Updated**: 2025-10-20

---

## Overview

The Route Playout Econometrics POC requires pre-calculated reach, GRP, and frequency data to be cached in PostgreSQL for optimal performance. This document specifies how the pipeline should populate these cache tables.

## Database Connection

**Database**: PostgreSQL on MS-01 (192.168.1.34) - `route_poc`

**Cache Tables** (created by POC migration `001_create_cache_tables.sql`):
- `cache_route_impacts_15min` - Frame-level impacts (15min granularity)
- `cache_campaign_reach_day` - Daily reach/GRP/frequency
- `cache_campaign_reach_week` - Weekly aggregations
- `cache_campaign_reach_full` - Full campaign period
- `cache_campaign_brand_reach` - Brand-level (Stage 2 - future)

## Prerequisites

The POC has already created:
- All cache tables with proper indexes
- Materialized views: `mv_playout_15min` and `mv_playout_15min_brands`
- Helper functions: `invalidate_cache_for_release()`, `clean_stale_cache_entries()`

**Pipeline should NOT create these** - they already exist.

## Backfilling Strategy

### 1. What to Cache

**Daily Reach (Priority 1)**:
- Cache reach for completed days (>24 hours old)
- One row per campaign per day
- Table: `cache_campaign_reach_day`

**Weekly Reach (Priority 2)**:
- Cache reach for completed weeks
- Weeks defined as Monday-Sunday
- Table: `cache_campaign_reach_week`

**Full Campaign Reach (Priority 3)**:
- Cache reach for completed campaigns
- One row per campaign for entire duration
- Table: `cache_campaign_reach_full`

**DO NOT cache**:
- Today's data (ongoing, let POC calculate live)
- Data from last 7 days (TTL handled by POC)
- Impacts at 15min level (POC calculates from playouts directly)

### 2. When to Run

**Schedule**:
- Daily at 02:00 UTC (after playout data import completes)
- Process yesterday's completed campaigns
- Process completed weeks (on Mondays)
- Process completed campaigns (when campaign end date < yesterday)

**Incremental Processing**:
- Only process new/changed data
- Check `cached_at` timestamp to skip already-cached data
- Update stale entries (campaigns that got new playouts)

## Implementation Guide

### Step 1: Identify Cacheable Campaigns

```sql
-- Get campaigns with completed days that aren't cached
SELECT DISTINCT
    buyercampaignref as campaign_id,
    startdate::date as playout_date
FROM playout_data
WHERE startdate::date < CURRENT_DATE - INTERVAL '1 day'
  AND frametype = 'digital'
  AND NOT EXISTS (
      SELECT 1
      FROM cache_campaign_reach_day crd
      WHERE crd.campaign_id = buyercampaignref
        AND crd.date = startdate::date
  )
ORDER BY playout_date DESC
LIMIT 100;  -- Process in batches
```

### Step 2: Get Playout Data for Reach Calculation

For each campaign/date:

```sql
-- Get aggregated playout data from materialized view
SELECT
    frameid,
    time_window_start as datetime_from,
    time_window_start + INTERVAL '15 minutes' as datetime_to,
    spot_count,
    playout_length_seconds as playout_length,
    break_length_seconds as break_length
FROM mv_playout_15min
WHERE buyercampaignref = :campaign_id
  AND time_window_start >= :date
  AND time_window_start < :date + INTERVAL '1 day'
ORDER BY frameid, time_window_start;
```

### Step 3: Call Route API Custom Endpoint

**Endpoint**: `https://route.mediatelapi.co.uk/rest/process/custom`

**Request Format**:
```json
{
  "route_release_id": 55,
  "route_algorithm_version": "10.2",
  "algorithm_figures": ["impacts", "reach", "frequency", "grp", "population"],
  "grouping": "frame_ID",
  "demographics": ["ageband>=1"],
  "campaign": [{
    "schedule": [
      {
        "datetime_from": "2025-08-20 00:00",
        "datetime_until": "2025-08-20 23:59"
      }
    ],
    "spot_length": 10,
    "spot_break_length": 50,
    "frames": [1234723633, 2000032505, ...]
  }],
  "target_month": 8
}
```

**Key Points**:
- `frames`: List of unique frame IDs (max 10,000 per call)
- `schedule`: Consolidated time blocks (merge consecutive 15min windows)
- `spot_length`: Average across all playouts for the day
- `spot_break_length`: Average break length
- `route_release_id`: Auto-detect from date (see Route Release Mapping below)
- `target_month`: Extract from date (8 for August)

### Step 4: Store in Cache

```sql
INSERT INTO cache_campaign_reach_day (
    campaign_id,
    date,
    reach,
    grp,
    frequency,
    total_impacts,
    frame_count,
    route_release_id,
    cached_at
) VALUES (
    :campaign_id,
    :date,
    :reach_from_api,
    :grp_from_api,
    :frequency_from_api,
    :impacts_from_api,
    :frame_count,
    :route_release_id,
    CURRENT_TIMESTAMP
)
ON CONFLICT (campaign_id, date)
DO UPDATE SET
    reach = EXCLUDED.reach,
    grp = EXCLUDED.grp,
    frequency = EXCLUDED.frequency,
    total_impacts = EXCLUDED.total_impacts,
    frame_count = EXCLUDED.frame_count,
    route_release_id = EXCLUDED.route_release_id,
    cached_at = CURRENT_TIMESTAMP;
```

## Route Release Mapping

**Critical**: Use the correct Route release for each date range.

| Release | Release Number | Trading Period Start | Trading Period End |
|---------|----------------|----------------------|-------------------|
| Q2 2025 | 55             | 2025-06-30           | 2025-09-28        |
| Q3 2025 | 56             | 2025-09-29           | 2026-01-04        |
| Q4 2025 | 57             | 2026-01-05           | 2026-03-29        |

**Logic**:
```python
def get_route_release_for_date(date):
    if date >= datetime(2026, 1, 5):
        return 57
    elif date >= datetime(2025, 9, 29):
        return 56
    elif date >= datetime(2025, 6, 30):
        return 55
    else:
        raise ValueError(f"No Route release available for {date}")
```

**Or use POC function**:
```python
from src.db import get_release_for_date
release = get_release_for_date(date)
route_release_id = release.release_number
```

## Weekly Reach Backfilling

### Identify Completed Weeks

```sql
-- Get completed weeks (Monday-Sunday) that aren't cached
WITH weeks AS (
    SELECT DISTINCT
        buyercampaignref as campaign_id,
        date_trunc('week', startdate::date) as week_start,
        date_trunc('week', startdate::date) + INTERVAL '6 days' as week_end
    FROM playout_data
    WHERE startdate::date < CURRENT_DATE - INTERVAL '7 days'
      AND frametype = 'digital'
)
SELECT
    w.campaign_id,
    w.week_start::date,
    w.week_end::date
FROM weeks w
WHERE NOT EXISTS (
    SELECT 1
    FROM cache_campaign_reach_week crw
    WHERE crw.campaign_id = w.campaign_id
      AND crw.week_start = w.week_start::date
)
ORDER BY week_start DESC
LIMIT 50;
```

### Get Week Playout Data

```sql
-- Get ALL playouts for the entire week
SELECT
    frameid,
    time_window_start as datetime_from,
    time_window_start + INTERVAL '15 minutes' as datetime_to,
    spot_count,
    playout_length_seconds,
    break_length_seconds
FROM mv_playout_15min
WHERE buyercampaignref = :campaign_id
  AND time_window_start >= :week_start
  AND time_window_start < :week_end + INTERVAL '1 day'
ORDER BY time_window_start, frameid;
```

### Call API and Store

Same process as daily, but:
- Include ALL frames and schedules for entire week
- Store in `cache_campaign_reach_week` table
- Use `week_start` and `week_end` as keys

## Full Campaign Reach Backfilling

### Identify Completed Campaigns

```sql
-- Get campaigns that have ended
WITH campaign_dates AS (
    SELECT
        buyercampaignref as campaign_id,
        MIN(startdate::date) as campaign_start,
        MAX(startdate::date) as campaign_end,
        COUNT(DISTINCT frameid) as frame_count
    FROM playout_data
    WHERE frametype = 'digital'
    GROUP BY buyercampaignref
    HAVING MAX(startdate::date) < CURRENT_DATE - INTERVAL '7 days'
)
SELECT
    cd.campaign_id,
    cd.campaign_start,
    cd.campaign_end,
    cd.frame_count
FROM campaign_dates cd
WHERE NOT EXISTS (
    SELECT 1
    FROM cache_campaign_reach_full crf
    WHERE crf.campaign_id = cd.campaign_id
      AND crf.date_from = cd.campaign_start
      AND crf.date_to = cd.campaign_end
)
  AND cd.frame_count <= 10000  -- Skip campaigns with >10k frames
ORDER BY campaign_end DESC
LIMIT 20;
```

**Important**: Skip campaigns with >10,000 frames (Route API limit).

### Get Full Campaign Data

```sql
-- Get ALL playouts for entire campaign
SELECT
    frameid,
    time_window_start as datetime_from,
    time_window_start + INTERVAL '15 minutes' as datetime_to,
    spot_count,
    playout_length_seconds,
    break_length_seconds
FROM mv_playout_15min
WHERE buyercampaignref = :campaign_id
ORDER BY time_window_start, frameid;
```

### Call API and Store

Store in `cache_campaign_reach_full` with `date_from` and `date_to`.

## Error Handling

### API Rate Limiting

Route API has a 6 calls/second limit.

**Implementation**:
```python
import asyncio

# Process in batches with rate limiting
async def process_with_rate_limit(campaigns, max_per_second=6):
    for i, campaign in enumerate(campaigns):
        if i > 0 and i % max_per_second == 0:
            await asyncio.sleep(1)  # Rate limit
        await process_campaign(campaign)
```

### Failed API Calls

- Log failures but continue processing
- Retry failed campaigns on next run
- Don't cache zero/null results from API errors

### Data Quality Checks

Before caching:
- Verify `reach > 0` for campaigns with playouts
- Verify `frequency = impacts / reach` (within 1% tolerance)
- Verify `grp > 0` for campaigns with audience
- Log anomalies but still cache (for manual review)

## Monitoring and Logging

### What to Log

**Info Level**:
- Number of campaigns processed
- Cache hit rate (if checking before calling API)
- Total API calls made
- Processing duration

**Warning Level**:
- API errors/timeouts
- Campaigns with zero reach but playouts exist
- Campaigns with >10k frames (skipped)

**Error Level**:
- Database connection failures
- Invalid Route release for date
- API authentication failures

### Example Log Output

```
2025-10-20 02:05:12 INFO  Starting daily reach cache backfill
2025-10-20 02:05:15 INFO  Found 47 campaigns with uncached daily reach
2025-10-20 02:06:42 INFO  Processed 47 campaigns, made 152 API calls
2025-10-20 02:06:42 INFO  Cache stats: 145 new entries, 7 updated
2025-10-20 02:06:42 INFO  Completed in 90.2 seconds
```

## Maintenance

### Daily Cleanup

Run the helper function to remove stale cache for ongoing campaigns:

```sql
SELECT * FROM clean_stale_cache_entries();
```

This removes:
- Cache entries >24hrs old for dates within last 7 days
- Does NOT remove historical data (>7 days old)

### Route Release Updates

When a new Route release is published:

1. Update release mapping in code
2. Invalidate old release cache if needed:
   ```sql
   SELECT * FROM invalidate_cache_for_release(54);
   ```
3. Re-run backfill for affected dates

## Performance Optimization

### Batch Processing

- Process 100 campaigns per run (configurable)
- Use connection pooling (10-20 connections)
- Run multiple date ranges in parallel (with rate limiting)

### Database Optimization

- Refresh materialized views before backfill:
  ```sql
  REFRESH MATERIALIZED VIEW CONCURRENTLY mv_playout_15min;
  ```
- Use prepared statements for inserts
- Batch inserts where possible (VALUES clause with multiple rows)

### API Optimization

- Consolidate consecutive 15min schedules into larger blocks
- De-duplicate frame lists
- Cache Route API responses in-memory during session (avoid duplicate calls)

## Testing

### Test with Single Campaign

```python
# Test backfill for campaign 16012 on 2025-08-20
campaign_id = "16012"
date = datetime(2025, 8, 20).date()

# 1. Check if already cached
cached = await cache_service.get_reach_day_cache(campaign_id, date, route_release_id=55)

if not cached:
    # 2. Get playout data
    playouts = await get_campaign_for_route_api(campaign_id, date, date)

    # 3. Call Route API
    reach_data = await route_client.get_campaign_reach(...)

    # 4. Store in cache
    await cache_service.put_reach_day_cache(...)

    print(f"Cached: {reach_data}")
else:
    print(f"Already cached: {cached}")
```

### Verify Cache

```sql
-- Check daily cache
SELECT * FROM cache_campaign_reach_day
WHERE campaign_id = '16012'
ORDER BY date DESC
LIMIT 10;

-- Check statistics
SELECT * FROM cache_statistics;
```

## Integration with POC

The POC will:
- Query cache first before calling API
- Fall back to live API if cache miss
- Populate cache with live results
- Use TTL rules (24hr for recent, never expire for historical)

The pipeline should:
- Backfill historical data (>24hrs old)
- Run daily to keep cache current
- Handle edge cases (large campaigns, missing releases)
- Monitor cache health

## Questions / Clarifications

If unclear, refer to:
- POC code: `/Users/ianwyatt/PycharmProjects/Route-Playout-Econometrics_POC`
- Cache service: `src/services/cache_service.py`
- Reach service: `src/services/reach_service.py`
- Route client: `src/api/route_client.py`
- Migration SQL: `migrations/001_create_cache_tables.sql`

**Contact**: Doctor Biz (ian@route.org.uk)

---

**End of Specification**
