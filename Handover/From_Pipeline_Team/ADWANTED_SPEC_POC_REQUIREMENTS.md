# ABOUTME: POC requirements for Adwanted batch data spec
# ABOUTME: Clarifies table relationships, playout sources, and missing tables for v7 spec

# Adwanted Batch Spec - POC Team Requirements

**Date**: 2025-12-05
**From**: POC Team
**To**: Pipeline Team
**Re**: v7 Adwanted Request Specification (`v7_adwanted_request.md`)

---

## Purpose

This document provides feedback on the v7 Adwanted batch data specification from the POC team's perspective. It clarifies:

1. Which tables the POC actually uses
2. The relationship between `route_frames` and `route_frame_details`
3. Where playout counts come from
4. Tables missing from the spec that the POC requires

---

## 1. `route_frames` vs `route_frame_details` - TECHNICAL DEBT

⚠️ **These tables are redundant and should be consolidated.**

Currently the POC uses both tables, but this is technical debt. They share the same key (`release_id`, `frameid`) and are always joined together. The only unique data in `route_frames` is `latitude` and `longitude`.

### Recommendation for Adwanted Spec

**Provide a single consolidated `route_frame_details` table** that includes lat/lon:

```sql
CREATE TABLE route_frame_details (
    release_id          INTEGER NOT NULL,
    frameid             BIGINT NOT NULL,
    -- Coordinates (currently in route_frames)
    latitude            DECIMAL(10, 8),
    longitude           DECIMAL(11, 8),
    -- Metadata
    environment_name    VARCHAR(100),
    format_name         VARCHAR(100),
    mediaowner_name     VARCHAR(200),
    mediaowner_code     VARCHAR(50),
    town                VARCHAR(100),
    barb_region_name    VARCHAR(100),
    postcode            VARCHAR(20),
    format_width        DECIMAL(10, 2),
    format_height       DECIMAL(10, 2),
    format_orientation  VARCHAR(20),
    additional_metadata JSONB,
    PRIMARY KEY (release_id, frameid)
);
```

This eliminates an unnecessary join and simplifies the data model.

See: `Claude/Documentation/TECHNICAL_DEBT_FRAME_TABLES.md` for full analysis.

---

### Current State (Technical Debt)

For reference, here's how the POC currently uses the two tables:

### route_frames (Core Identity + Coordinates)

```sql
CREATE TABLE route_frames (
    id              BIGSERIAL PRIMARY KEY,
    release_id      INTEGER NOT NULL,      -- FK to route_releases.id
    frameid         BIGINT NOT NULL,
    frame_reference VARCHAR(50),
    environmentid   INTEGER,
    formatid        INTEGER,
    mediaownerid    INTEGER,
    illumination    VARCHAR(20),           -- 'Digital' or 'Classic'
    latitude        DECIMAL(10, 8),
    longitude       DECIMAL(11, 8)
);
```

**Purpose**: Core frame lookup with geographic coordinates for mapping.

### route_frame_details (Extended Metadata)

```sql
CREATE TABLE route_frame_details (
    id                  BIGSERIAL PRIMARY KEY,
    release_id          INTEGER NOT NULL,      -- FK to route_releases.id
    frameid             BIGINT NOT NULL,
    environment_name    VARCHAR(100),
    environment_type    VARCHAR(50),
    format_name         VARCHAR(100),
    format_width        DECIMAL(10, 2),
    format_height       DECIMAL(10, 2),
    format_orientation  VARCHAR(20),
    mediaowner_name     VARCHAR(200),
    mediaowner_code     VARCHAR(50),
    postcode            VARCHAR(20),
    town                VARCHAR(100),
    barb_region_name    VARCHAR(100),          -- ⚠️ CRITICAL: TV region
    additional_metadata JSONB
);
```

**Purpose**: Human-readable names, geographic classification (town, TV region).

### How POC Joins Them

```sql
-- From src/db/streamlit_queries.py (lines 663-665)
JOIN route_frames rf ON mf.frameid = rf.frameid
JOIN route_frame_details rfd ON rf.release_id = rfd.release_id AND rf.frameid = rfd.frameid
```

### ⚠️ CRITICAL: Per-Release Data

Both tables store data **per Route release**. A frame exists in multiple releases (typically 2-3) with potentially different metadata. When querying frame details, you MUST use the correct release.

**Example**: Campaign spans R55 and R56. Playouts in September use R55 frame details; playouts in October use R56 frame details.

The join logic must match the release used for audience calculation:

```sql
-- CORRECT: Match release from cache to frame details
LEFT JOIN route_releases rr ON rr.release_number = 'R' || cache.route_release_id::text
LEFT JOIN route_frame_details rfd ON rr.id = rfd.release_id AND frame.frameid = rfd.frameid
```

See: `docs/pipeline-handover/MV_FRAME_AUDIENCE_FIX_2025-11-29.md` for detailed explanation.

---

## 2. Where Playout Counts Come From

The v7 spec has `playout_data` but is missing the **aggregation layer** that produces playout counts.

### Data Flow

```
playout_data (raw - 1 row per playout event)
    ↓ aggregate to 15-minute windows
mv_playout_15min (1 row per frame × 15-min window)
    ↓ aggregate to daily
mv_playout_frame_day (1 row per frame × day)
    ↓ aggregate to hourly
mv_playout_frame_hour (1 row per frame × hour)
```

### Missing Table 1: mv_playout_15min

This is the primary aggregation table. **Source of `spot_count`**.

```sql
CREATE MATERIALIZED VIEW mv_playout_15min AS
SELECT
    frameid                       BIGINT,
    buyercampaignref              TEXT,           -- campaign_id
    time_window_start             TIMESTAMP,      -- 15-min boundary
    spacemediaownerid             INTEGER,
    spacebuyerid                  INTEGER,
    spaceagencyid                 INTEGER,
    spacebrandid                  INTEGER,
    spot_count                    BIGINT,         -- ⭐ NUMBER OF PLAYOUTS
    total_playout_ms              BIGINT,
    playout_length_seconds        INTEGER,        -- spot length
    break_length_seconds          INTEGER,        -- derived break length
    cycle_length_seconds          INTEGER,
    earliest_playout              TIMESTAMP,
    latest_playout                TIMESTAMP,
    avg_playout_seconds_unrounded NUMERIC
FROM playout_data
GROUP BY frameid, buyercampaignref,
         date_trunc('hour', startdate) +
         INTERVAL '15 min' * FLOOR(EXTRACT(MINUTE FROM startdate) / 15),
         spacemediaownerid, spacebuyerid, spaceagencyid, spacebrandid;

-- Indexes (critical for performance)
CREATE UNIQUE INDEX idx_mv_playout_15min_pk
    ON mv_playout_15min(frameid, time_window_start, buyercampaignref);
CREATE INDEX idx_mv_playout_15min_campaign_time
    ON mv_playout_15min(buyercampaignref, time_window_start);
CREATE INDEX idx_mv_playout_15min_frame_time
    ON mv_playout_15min(frameid, time_window_start);
CREATE INDEX idx_mv_playout_15min_brand
    ON mv_playout_15min(spacebrandid);
CREATE INDEX idx_mv_playout_15min_mediaowner
    ON mv_playout_15min(spacemediaownerid);
```

**POC Usage**: Campaign browser summary, total playouts calculation.

### Missing Table 2: mv_playout_frame_day

Daily playout aggregation per frame. **Source of daily `playout_count`**.

```sql
CREATE MATERIALIZED VIEW mv_playout_frame_day AS
SELECT
    campaign_id    TEXT,
    frameid        BIGINT,
    date           DATE,
    playout_count  NUMERIC,        -- ⭐ SUM(spot_count) for the day
    interval_count BIGINT,         -- number of 15-min intervals
    first_playout  TIMESTAMP,
    last_playout   TIMESTAMP
FROM mv_playout_15min
GROUP BY buyercampaignref, frameid, DATE(time_window_start);

-- Indexes
CREATE INDEX idx_mv_playout_frame_day_campaign
    ON mv_playout_frame_day(campaign_id);
CREATE INDEX idx_mv_playout_frame_day_composite
    ON mv_playout_frame_day(campaign_id, frameid, date);
CREATE INDEX idx_mv_playout_frame_day_frame_date
    ON mv_playout_frame_day(frameid, date);
```

**POC Usage**: Frame Audiences daily tab, daily playout counts.

### Missing Table 3: mv_playout_frame_hour

Hourly playout aggregation per frame. **Source of hourly `playout_count`**.

```sql
CREATE MATERIALIZED VIEW mv_playout_frame_hour AS
SELECT
    campaign_id    TEXT,
    frameid        BIGINT,
    hour_start     TIMESTAMP,      -- truncated to hour
    playout_count  NUMERIC,        -- ⭐ SUM(spot_count) for the hour
    interval_count BIGINT          -- number of 15-min intervals (max 4)
FROM mv_playout_15min
GROUP BY buyercampaignref, frameid, DATE_TRUNC('hour', time_window_start);

-- Indexes
CREATE INDEX idx_mv_playout_frame_hour_campaign
    ON mv_playout_frame_hour(campaign_id);
CREATE INDEX idx_mv_playout_frame_hour_composite
    ON mv_playout_frame_hour(campaign_id, frameid, hour_start);
```

**POC Usage**: Frame Audiences hourly tab, hourly playout counts.

---

## 3. Tables in Spec - POC Usage Status

| # | Table | POC Uses? | Notes |
|---|-------|-----------|-------|
| 1 | `playout_data` | ✅ Yes | Raw source (via MVs) |
| 2 | `playout_dates` | ❌ No | Not currently used |
| 3 | `route_releases` | ✅ Yes | Release lookup for frame joins |
| 4 | `spot_break_combinations` | ❌ No | POC uses inline spot/break from mv_playout_15min |
| 5 | `cache_demographic_universes` | ✅ Yes | GRP calculation |
| 6 | `cache_space_media_owners` | ✅ Yes | Media owner names |
| 7 | `cache_space_buyers` | ✅ Yes | Buyer names |
| 8 | `cache_space_agencies` | ✅ Yes | Agency names |
| 9 | `cache_space_brands` | ✅ Yes | Brand names |
| 10 | `route_frames` | ✅ Yes | Lat/lon for maps |
| 11 | `route_frame_details` | ✅ Yes | Town, TV region, environment |
| 12 | `cache_route_impacts_15min_by_demo` | ✅ Yes | **Primary audience data** |
| 13 | `cache_campaign_reach_day` | ✅ Yes | Daily reach metrics |
| 14 | `cache_campaign_reach_week` | ✅ Yes | Weekly reach table |
| 15 | `cache_campaign_reach_full` | ✅ Yes | Full campaign metrics |
| 16 | `cache_campaign_reach_day_cumulative` | ✅ Yes | Cumulative build charts |
| 17 | `cache_campaign_brand_reach` | ⚠️ Future | Not yet implemented in POC |
| 18 | `campaign_cache_limitations` | ✅ Yes | On/off campaign handling |

---

## 4. Updated Table Count

### Adwanted Delivers: 13 tables
### Route Provides: 2 tables
### Route Creates: 3+ MVs

| Category | Owner | Count | Tables |
|----------|-------|-------|--------|
| Source Data | Adwanted | 1 | playout_data |
| Reference | Adwanted | 1 | cache_demographic_universes |
| SPACE Lookups | Adwanted | 4 | cache_space_agencies, cache_space_brands, cache_space_buyers, cache_space_media_owners |
| Audience Data | Adwanted | 6 | cache_route_impacts_15min_by_demo, cache_campaign_reach_day, cache_campaign_reach_week, cache_campaign_reach_full, cache_campaign_reach_day_cumulative, cache_campaign_brand_reach |
| Limitations | Adwanted | 1 | campaign_cache_limitations |
| **Frame Data** | **Route** | **1** | **route_frame_details** (consolidated with lat/lon) |
| **Reference** | **Route** | **1** | **route_releases** |
| Playout Aggregation | Route (creates) | 3 | mv_playout_15min, mv_playout_frame_day, mv_playout_frame_hour |

### Removed from Adwanted Spec
- `route_frames` - Consolidated into `route_frame_details`
- `route_releases` - Route provides this
- `playout_dates` - Not used by POC
- `spot_break_combinations` - POC uses inline values from mv_playout_15min

---

## 5. Priority for POC Functionality

### Critical - Adwanted Must Deliver

| Table | Why Critical |
|-------|--------------|
| `playout_data` | Source of all playout records |
| `cache_route_impacts_15min_by_demo` | Primary audience data |
| `cache_space_brands` | Brand names for display |
| `cache_space_media_owners` | Media owner names |
| `cache_space_buyers` | Buyer names |

### Critical - Route Must Provide

| Table | Why Critical |
|-------|--------------|
| `route_frame_details` | Frame coordinates, town, TV region |
| `route_releases` | Release lookup for joins |

### Critical - Route Creates

| MV | Why Critical |
|----|--------------|
| `mv_playout_15min` | Playout aggregation with spot_count |

### Important (Full Feature Set)

| Owner | Table | Purpose |
|-------|-------|---------|
| Route creates | `mv_playout_frame_day` | Daily playout counts |
| Route creates | `mv_playout_frame_hour` | Hourly playout counts |
| Adwanted | `cache_campaign_reach_full` | Campaign totals |
| Adwanted | `cache_campaign_reach_day` | Daily reach |
| Adwanted | `cache_campaign_reach_week` | Weekly reach table |
| Adwanted | `cache_campaign_reach_day_cumulative` | Cumulative charts |
| Adwanted | `cache_demographic_universes` | GRP calculation |
| Adwanted | `campaign_cache_limitations` | On/off campaign handling |

### Optional (Future Features)

| Owner | Table | Purpose |
|-------|-------|---------|
| Adwanted | `cache_campaign_brand_reach` | Brand-level reach (not yet implemented) |
| Adwanted | `cache_space_agencies` | Agency names (displayed but not critical) |

---

## 6. Spec Clarification: barb_region_name

The spec lists `route_frame_details.region` but POC uses **`barb_region_name`** for TV region.

```sql
-- POC query (streamlit_queries.py:659)
rfd.barb_region_name as tv_region
```

Ensure the column name matches: `barb_region_name` not just `region`.

---

## 7. Division of Work - CONFIRMED

**Adwanted provides playout + audience data. Route provides frame data.**

Frame details are Route's data - no need for a middleman. This simplifies Adwanted's job and keeps Route in control of their own data.

| Adwanted Delivers | Route Provides | Route Creates |
|-------------------|----------------|---------------|
| `playout_data` | `route_frame_details` (consolidated, with lat/lon) | `mv_playout_15min` |
| `cache_route_impacts_15min_by_demo` | `route_releases` | `mv_playout_frame_day` |
| `cache_campaign_reach_day` | | `mv_playout_frame_hour` |
| `cache_campaign_reach_week` | | All indexes |
| `cache_campaign_reach_full` | | Denormalised MVs |
| `cache_campaign_reach_day_cumulative` | | |
| `cache_campaign_brand_reach` | | |
| `cache_space_agencies` | | |
| `cache_space_brands` | | |
| `cache_space_buyers` | | |
| `cache_space_media_owners` | | |
| `cache_demographic_universes` | | |
| `campaign_cache_limitations` | | |

### Why This Split Makes Sense

1. **Frame data is Route's data** - Comes from Route API, Route controls the source
2. **Frame data is static per release** - Populate once per release, done
3. **Reduces Adwanted's scope** - They focus on playouts + audience calculations
4. **Less coordination risk** - Route controls their own data quality

### Coordination Required

**Route must supply Adwanted with `route_releases` data upfront** so they can:
- Determine which release to use for each playout date
- Calculate audiences using the correct release
- Store `route_release_id` in cache tables

| Release | Trading Period Start | Trading Period End |
|---------|---------------------|-------------------|
| R54 | 2025-04-07 | 2025-06-29 |
| R55 | 2025-06-30 | 2025-09-28 |
| R56 | 2025-09-29 | 2026-01-04 |
| R57 | 2026-01-05 | 2026-03-29 |

**Action**: Route to provide `route_releases` table to Adwanted before processing begins.

---

## Contact

**POC Team**: Route Playout Econometrics POC
**Document**: `docs/pipeline-handover/ADWANTED_SPEC_POC_REQUIREMENTS.md`

---

*Version 1.0 | 2025-12-05*
