# Day-Cumulative Reach Cache - Now Available

**Date**: 2025-11-24
**From**: Pipeline Team
**To**: POC Team

---

## Summary

The day-cumulative reach cache has been populated and is ready for use. This data shows how campaign reach builds up day-by-day from campaign start.

---

## Table: `cache_campaign_reach_day_cumulative`

### Current Statistics

| Metric | Value |
|--------|-------|
| **Total records** | 10,819 |
| **Campaigns covered** | 830 |
| **Day range** | 1-64 days |
| **Table size** | 2.78 MB |
| **Backfill completed** | 2025-11-24 00:00 |

### Schema

```sql
CREATE TABLE cache_campaign_reach_day_cumulative (
    id                   SERIAL PRIMARY KEY,
    campaign_id          VARCHAR(255) NOT NULL,
    buyer_id             VARCHAR(255) NOT NULL,
    date                 DATE NOT NULL,
    day_number           INTEGER NOT NULL,      -- Day 1, 2, 3... from campaign start
    campaign_start_date  DATE NOT NULL,
    reach                NUMERIC(15,3) NOT NULL DEFAULT 0,
    grp                  NUMERIC(10,3) NOT NULL DEFAULT 0,
    frequency            NUMERIC(10,3) NOT NULL DEFAULT 0,
    total_impacts        NUMERIC(15,3) NOT NULL DEFAULT 0,
    frame_count          INTEGER NOT NULL DEFAULT 0,
    route_release_id     INTEGER NOT NULL,
    is_approximate       BOOLEAN NOT NULL DEFAULT false,
    approximation_method VARCHAR(100),
    cached_at            TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(campaign_id, date)
);
```

### Key Indexes

- `idx_reach_day_cumulative_campaign` - (campaign_id, date)
- `idx_reach_day_cumulative_buyer` - (buyer_id, campaign_id)
- `idx_reach_day_cumulative_approximate` - (is_approximate) WHERE is_approximate = true

---

## How It Works

Each row represents the **cumulative reach from day 1 to day N** for a campaign.

### Example: Campaign 18512 (7-day campaign)

| date | day_number | reach | grp | frequency |
|------|------------|-------|-----|-----------|
| 2025-10-07 | 1 | 0.954 | 0.007 | 3.825 |
| 2025-10-08 | 2 | 670.956 | 2.314 | 1.918 |
| 2025-10-09 | 3 | 1,184.497 | 4.419 | 2.074 |
| 2025-10-10 | 4 | 1,703.938 | 6.406 | 2.090 |
| 2025-10-11 | 5 | 2,122.035 | 7.724 | 2.023 |
| 2025-10-12 | 6 | 2,392.771 | 8.659 | 2.012 |
| 2025-10-13 | 7 | 2,484.424 | 9.878 | 2.210 |

**Interpretation**:
- Day 1: Almost no reach (campaign just started)
- Day 7: Final cumulative reach = 2,484 (matches `cache_campaign_reach_full`)

---

## Common Queries

### Get cumulative reach curve for a campaign

```sql
SELECT
    day_number,
    date,
    reach,
    grp,
    frequency
FROM cache_campaign_reach_day_cumulative
WHERE campaign_id = '18512'
ORDER BY day_number;
```

### Get all campaigns with their final day reach

```sql
SELECT
    campaign_id,
    buyer_id,
    MAX(day_number) as total_days,
    MAX(reach) as final_reach,
    MAX(grp) as final_grp
FROM cache_campaign_reach_day_cumulative
GROUP BY campaign_id, buyer_id
ORDER BY final_reach DESC;
```

### Get reach build-up percentage by day

```sql
WITH final_reach AS (
    SELECT campaign_id, MAX(reach) as total_reach
    FROM cache_campaign_reach_day_cumulative
    GROUP BY campaign_id
)
SELECT
    c.campaign_id,
    c.day_number,
    c.reach,
    ROUND(c.reach / f.total_reach * 100, 1) as pct_of_final
FROM cache_campaign_reach_day_cumulative c
JOIN final_reach f ON c.campaign_id = f.campaign_id
WHERE c.campaign_id = '18512'
ORDER BY c.day_number;
```

---

## Use Cases for POC UI

### 1. Reach Build-Up Chart
Show how reach accumulates day-by-day during a campaign.

### 2. Reach Velocity Analysis
Calculate how quickly a campaign reaches X% of its final audience:
- Days to 50% reach
- Days to 80% reach
- Days to 90% reach

### 3. Campaign Efficiency Comparison
Compare reach build-up curves across similar campaigns.

### 4. Forecast Remaining Reach
For in-flight campaigns, project final reach based on current trajectory.

---

## Relationship to Other Tables

| Table | Granularity | Use |
|-------|-------------|-----|
| `cache_campaign_reach_day_cumulative` | Cumulative by day | **Reach build-up curves** |
| `cache_campaign_reach_day` | Individual days | Daily reach (non-cumulative) |
| `cache_campaign_reach_week` | Individual weeks | Weekly reach |
| `cache_campaign_reach_full` | Campaign total | Final campaign reach |

---

## Backfill Summary

The backfill completed on 2025-11-24 with:

| Status | Count |
|--------|-------|
| ✅ Successfully cached | 9,317 |
| ❌ API errors | 15 |
| ⏭️ Skipped (no valid frames) | 186 |
| ⚠️ Large campaigns (>50k refs) | 2,409 |
| **Total time** | ~5.3 hours |

---

## Limitations

1. **Campaigns with >50k slot references** may have `is_approximate = true`
2. **ATLAS campaigns** with unregistered frames may have gaps
3. **Very recent campaigns** (last 24h) may not be cached yet

---

## Questions?

Contact Pipeline Team

