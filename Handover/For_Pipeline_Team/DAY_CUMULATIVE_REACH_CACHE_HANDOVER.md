# Day-Cumulative Reach Cache - POC Team Handover

**From:** Pipeline Team
**Date:** 2025-11-23
**Status:** BACKFILL IN PROGRESS (ETA: late Nov 24)

## Summary

We've added a new cache table `cache_campaign_reach_day_cumulative` that provides cumulative daily reach metrics for campaigns. This enables day-by-day reach curve analysis from campaign start through each subsequent day.

## What This Provides

For each campaign, you get reach metrics for:
- Day 1 (just day 1)
- Days 1-2 (cumulative)
- Days 1-3 (cumulative)
- ... through the full campaign duration

This is different from the existing `cache_campaign_reach_week` which provides weekly snapshots.

## Table Schema

```sql
CREATE TABLE cache_campaign_reach_day_cumulative (
    campaign_id VARCHAR(255) NOT NULL,
    date DATE NOT NULL,                    -- End date of the cumulative period
    day_number INTEGER NOT NULL,           -- 1, 2, 3, etc.
    campaign_start_date DATE NOT NULL,     -- Campaign start date
    reach BIGINT,                          -- Cumulative unique audience
    grp DECIMAL(10,2),                     -- Cumulative GRP
    frequency DECIMAL(10,2),               -- Average frequency
    total_impacts BIGINT,                  -- Cumulative impacts
    frame_count INTEGER,                   -- Frames active in period
    route_release_id INTEGER,              -- Route data version
    cached_at TIMESTAMP DEFAULT NOW(),
    buyer_id VARCHAR(50),
    is_approximate BOOLEAN DEFAULT false,  -- ⚠️ IMPORTANT - see below
    approximation_method VARCHAR(100),
    PRIMARY KEY (campaign_id, date)
);
```

## IMPORTANT: Sparse Frame Coverage Flag

Some campaigns have sparse frame coverage (e.g., week-on/week-off patterns). When cumulative date ranges span gaps in frame activity, the Route API cannot deduplicate audiences and returns `reach=0`.

**How to identify these records:**
```sql
-- Records with unreliable reach values
SELECT * FROM cache_campaign_reach_day_cumulative
WHERE is_approximate = true;
```

**Guidance:**
- `is_approximate = false` → Reach value is reliable, use normally
- `is_approximate = true` → Reach is 0 due to API limitation, NOT because no one saw the ads
- GRP and impacts remain valid even when `is_approximate = true`

**For reach analysis, filter these out:**
```sql
SELECT campaign_id, day_number, reach, grp
FROM cache_campaign_reach_day_cumulative
WHERE is_approximate = false
ORDER BY campaign_id, day_number;
```

## Example Queries

### Get reach curve for a campaign
```sql
SELECT
    day_number,
    date,
    reach,
    grp,
    frequency,
    total_impacts,
    is_approximate
FROM cache_campaign_reach_day_cumulative
WHERE campaign_id = '18295'
ORDER BY day_number;
```

### Compare reach growth across campaigns
```sql
SELECT
    campaign_id,
    day_number,
    reach,
    grp,
    reach / NULLIF(grp, 0) as reach_per_grp
FROM cache_campaign_reach_day_cumulative
WHERE day_number <= 14  -- First 2 weeks
  AND is_approximate = false
ORDER BY campaign_id, day_number;
```

### Find campaigns with sparse coverage issues
```sql
SELECT
    campaign_id,
    COUNT(*) as total_days,
    SUM(CASE WHEN is_approximate THEN 1 ELSE 0 END) as approximate_days,
    MIN(day_number) FILTER (WHERE is_approximate) as first_sparse_day
FROM cache_campaign_reach_day_cumulative
GROUP BY campaign_id
HAVING SUM(CASE WHEN is_approximate THEN 1 ELSE 0 END) > 0
ORDER BY approximate_days DESC;
```

## Data Volume

| Metric | Count |
|--------|-------|
| Total campaigns | ~836 |
| Total day records | ~11,026 |
| Processing order | Longest campaigns first |

## Related Documentation

- `Claude/Documentation/ROUTE_API_REACH_ZERO_BEHAVIOR.md` - Full explanation of the reach=0 behavior
- `scripts/lib/granularity/day_cumulative.py` - Processor implementation

## Questions?

Contact Pipeline Team if you need:
- Specific campaigns prioritized
- Custom date range filtering
- Explanation of any data anomalies
