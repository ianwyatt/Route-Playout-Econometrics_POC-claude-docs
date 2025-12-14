# Adwanted Batch Data - Post-Import Checklist

**Date:** 2025-12-09
**Purpose:** Steps to complete after receiving Adwanted bulk audience data

---

## Overview

Adwanted will deliver bulk audience data (impacts, reach, GRP, frequency) for all Talon campaigns. After import, Route must create derived views and verify data integrity before the POC UI can use it.

---

## Pre-Import: Data Route Already Has

These tables exist and are maintained by Route (NOT delivered by Adwanted):

| Table | Description |
|-------|-------------|
| `route_frames` | Frame coordinates, environment, format |
| `route_frame_details` | Frame metadata (region, town, postcode) |
| `route_releases` | Release tracking (R49-R61) |

---

## Adwanted Delivers (13 Tables)

| # | Table | Rows (Est.) | Notes |
|---|-------|-------------|-------|
| 1 | `playout_data` | 11B+ | Raw playout records |
| 2 | `cache_route_impacts_15min_by_demo` | 400M+ | Impacts per frame/window/demographic |
| 3 | `cache_campaign_reach_day` | ~50K | Daily reach metrics |
| 4 | `cache_campaign_reach_week` | ~10K | Weekly reach (individual + cumulative) |
| 5 | `cache_campaign_reach_full` | ~2K | Full campaign totals |
| 6 | `cache_campaign_reach_day_cumulative` | ~50K | Running totals by date |
| 7 | `cache_campaign_brand_reach` | ~5K | Reach by brand within campaign |
| 8 | `cache_space_media_owners` | ~100 | Media owner lookup |
| 9 | `cache_space_buyers` | ~50 | Buyer lookup |
| 10 | `cache_space_agencies` | ~100 | Agency lookup |
| 11 | `cache_space_brands` | ~500 | Brand lookup |
| 12 | `cache_demographic_universes` | ~50 | Population per demographic per release |
| 13 | `campaign_cache_limitations` | ~100 | Campaigns with limitations |

**Also requested from Adwanted (playout aggregations):**

| # | Table | Rows (Est.) | Notes |
|---|-------|-------------|-------|
| 14 | `playout_15min` | ~500M | 15-min window aggregations |
| 15 | `playout_frame_day` | ~50M | Daily playout counts per frame |
| 16 | `playout_frame_hour` | ~200M | Hourly playout counts per frame |

---

## Post-Import: Name Mapping (If Adwanted Uses Different Names)

The POC UI expects specific `mv_*` prefixed names. If Adwanted delivers tables without the prefix, create alias views:

| POC Expects | Adwanted Delivers | Action |
|-------------|-------------------|--------|
| `mv_playout_15min` | `playout_15min` | Create view alias |
| `mv_playout_15min_brands` | (derived) | Route creates from playout_15min |

```sql
-- If Adwanted delivers 'playout_15min', create alias for POC compatibility
CREATE VIEW mv_playout_15min AS SELECT * FROM playout_15min;

-- mv_playout_15min_brands is derived (adds brand name joins)
CREATE MATERIALIZED VIEW mv_playout_15min_brands AS
SELECT
    p.*,
    b.name as brand_name
FROM playout_15min p
LEFT JOIN cache_space_brands b ON p.spacebrandid::varchar = b.entity_id;
```

**Alternative:** Update POC code to use Adwanted table names directly (more work, but cleaner long-term).

---

## Post-Import: Route Creates These MVs

After importing Adwanted data, Route must create these materialised views for the POC UI:

### 1. Campaign Browser Views

```sql
-- mv_campaign_browser
-- Pre-aggregated campaign list for browser UI
-- Source: cache_campaign_reach_full + playout aggregations + entity lookups
CREATE MATERIALIZED VIEW mv_campaign_browser AS
SELECT
    campaign_id,
    -- aggregated metrics from cache tables
    -- brand/buyer/media owner names from entity lookups
    ...
```

```sql
-- mv_campaign_browser_summary
-- Header statistics for campaign browser
-- Source: mv_campaign_browser
CREATE MATERIALIZED VIEW mv_campaign_browser_summary AS
SELECT
    COUNT(*) as total_campaigns,
    ...
```

### 2. Frame Audience Views (Denormalised)

```sql
-- mv_frame_audience_daily
-- Denormalised daily frame impacts with pre-joined frame details
-- Source: cache_route_impacts_15min_by_demo + route_frames + route_frame_details
CREATE MATERIALIZED VIEW mv_frame_audience_daily AS
SELECT
    frameid,
    date,
    -- frame details (environment, format, region, etc.)
    -- aggregated impacts by demographic
    ...
```

```sql
-- mv_frame_audience_hourly
-- Denormalised hourly frame impacts with pre-joined frame details
-- Source: cache_route_impacts_15min_by_demo + route_frames + route_frame_details
CREATE MATERIALIZED VIEW mv_frame_audience_hourly AS
SELECT
    frameid,
    hour_start,
    -- frame details
    -- aggregated impacts by demographic
    ...
```

---

## Post-Import Verification Checklist

### Data Integrity

- [ ] Verify row counts match expected volumes
- [ ] Verify all 7 demographics present in impacts table
- [ ] Verify all Route releases have universe populations
- [ ] Verify campaign_id consistency across all tables
- [ ] Verify date ranges match expected trading periods

### Entity Lookups

- [ ] All `spacemediaownerid` values have lookup entries
- [ ] All `spacebuyerid` values have lookup entries
- [ ] All `spacebrandid` values have lookup entries
- [ ] All `spaceagencyid` values have lookup entries

### Frame Joins

- [ ] Test frame joins work: `route_releases.release_number = 'R' || route_release_id::text`
- [ ] Verify frames in impacts table exist in `route_frames`
- [ ] Check for orphaned frames (in impacts but not in route_frames)

### MV/View Names (POC Expects These)

Verify these exist after import and MV creation:

- [ ] `mv_playout_15min` - 15-min playout aggregations
- [ ] `mv_playout_15min_brands` - With brand name joins
- [ ] `mv_campaign_browser` - Campaign browser listing
- [ ] `mv_campaign_browser_summary` - Header statistics
- [ ] `mv_frame_audience_daily` - Denormalised daily frame data
- [ ] `mv_frame_audience_hourly` - Denormalised hourly frame data
- [ ] `mv_frame_audience_campaign` - Campaign-level frame counts

### UI Smoke Test

- [ ] Campaign browser loads and shows campaigns
- [ ] Select a known campaign (e.g., 16699)
- [ ] Overview tab shows data
- [ ] Weekly Reach/GRP tab shows data
- [ ] Daily patterns tab shows data
- [ ] Geographic tab shows map with frames
- [ ] Frame Audiences tab loads data
- [ ] Executive Summary generates

---

## MV Creation Scripts Location

Full SQL scripts for creating materialised views:
- `Claude/Documentation/Adwanted_Data_Import/mv_creation_scripts.sql`

---

## Contacts

- **Route**: Ian Wyatt (ian@route.org.uk)
- **Adwanted/MediaTel**: [TBC]

---

*Last Updated: 2025-12-09*
