# Database Cleanup — POC App Optimisation

**Date**: 5 February 2026
**Database**: Local Mac (`route_poc`)
**Result**: 114 GB → 57 GB (57 GB freed, 50% reduction)

| Phase | Action | Savings |
|-------|--------|---------|
| Index cleanup | Dropped 64 unused indexes | 38 GB (114 → 76 GB) |
| Table cleanup | Dropped 24 unused tables | 19 GB (76 → 57 GB) |

---

## Background

The database accumulated indexes from the pipeline phase that are not used by the
read-only Streamlit POC app. A systematic audit cross-referenced every SQL query in
`src/db/` against all 101 database indexes to identify what could be safely removed.

## Methodology

1. Queried `pg_stat_user_indexes` for all index sizes and scan counts
2. Read every query function in `src/db/queries/` and `src/db/route_releases.py`
3. Mapped each `WHERE`, `JOIN`, `ORDER BY`, and `GROUP BY` clause to the indexes that serve it
4. Identified duplicates (e.g., non-unique index duplicating a unique constraint)
5. Classified indexes as KEEP, BORDERLINE, or DROP

## What Was Removed

### Phase 1: `cache_route_impacts_15min_by_demo` (~35.7 GB)

This single table had 38 GB of indexes (93% of all index space). The app only uses
it as a fallback when materialised views lack data, filtering by `(campaign_id, demographic_segment)`.

| Index Dropped | Size | Reason |
|---------------|------|--------|
| Primary key `(frameid, time_window_start, demographic_segment, campaign_id)` | 21 GB | App never queries by this column order |
| `idx_impacts_demo_campaign_time` | 3,074 MB | Redundant — `idx_impacts_demo_campaign` covers the fallback |
| `idx_impacts_demo_frame` | 2,852 MB | App never filters this table by frameid |
| `idx_impacts_demo_time` | 2,828 MB | App never filters by time alone |
| `idx_impacts_demo_buyer` | 2,809 MB | App never filters by buyer_id |
| `idx_cache_spot_break_id` | 2,748 MB | Pipeline-only (spot_break_id) |

**Kept**: `idx_impacts_demo_campaign` on `(campaign_id, demographic_segment)` — 2.8 GB.
This serves the fallback queries in `impacts.py:43-44` and `impacts.py:111-112`.

### Phase 2: Unused Materialised View Indexes (~2.5 GB)

| Index Dropped | Table | Size | Reason |
|---------------|-------|------|--------|
| `idx_mv_cache_campaign_impacts_frame_1hr_campaign` | mv_cache_campaign_impacts_frame_1hr | 693 MB | App never queries this table |
| `idx_mv_playout_15min_frame` | mv_playout_15min | 449 MB | App filters by campaign, not frame |
| `idx_mv_playout_15min_time` | mv_playout_15min | 445 MB | App never filters by time |
| `idx_mv_playout_15min_brands_campaign` | mv_playout_15min_brands | 444 MB | App never queries this table |
| `idx_mv_playout_15min_brands_brand` | mv_playout_15min_brands | 443 MB | App never queries this table |

### Phase 3: Duplicate & Unused `route_frame*` Indexes (~232 MB)

| Index Dropped | Size | Reason |
|---------------|------|--------|
| `idx_route_frame_details_lookup` | 35 MB | Exact duplicate of `unique_frame_detail_per_release` |
| `idx_route_frames_lookup` | 35 MB | Exact duplicate of `unique_frame_per_release` |
| `idx_frame_details_location` | 37 MB | App joins by (release_id, frameid), not location |
| `route_frame_details_pkey` (id) | 25 MB | Surrogate key — app uses (release_id, frameid) |
| `route_frames_pkey` (id) | 25 MB | Surrogate key — app uses frameid |
| Various column indexes (region, town, postal_district, frame_type, category, environment, release, mediaowner, metadata) | ~75 MB | App never filters by these columns |

### Phase 4: Small Pipeline-Only & Redundant (~3 MB)

38 small indexes on pipeline-only tables (`cache_campaign_reach_day`, `playout_data`,
`playout_imports`, `spot_break_combinations`, `campaign_cache_limitations`,
`cache_statistics`, `cache_demographic_universes`, `cache_space_*`,
`route_frame_cache_sync_log`) and redundant duplicates on reach tables.

## Indexes Retained (37 remaining)

### Actively Used by App

| Index | Table | Size | Query Pattern |
|-------|-------|------|---------------|
| `idx_impacts_demo_campaign` | cache_route_impacts_15min_by_demo | 2,812 MB | Fallback WHERE (campaign_id, demographic_segment) |
| `idx_mv_playout_15min_campaign` | mv_playout_15min | 443 MB | WHERE buyercampaignref |
| `idx_mv_frame_audience_hourly_campaign` | mv_frame_audience_hourly | 112 MB | WHERE campaign_id |
| `unique_frame_detail_per_release` | route_frame_details | 35 MB | JOIN (release_id, frameid) |
| `unique_frame_per_release` | route_frames | 35 MB | JOIN (release_id, frameid) |
| `idx_route_frames_frameid` | route_frames | 18 MB | JOIN ON frameid |
| `idx_route_frame_details_frameid` | route_frame_details | 18 MB | JOIN ON frameid |
| `idx_mv_frame_audience_daily_campaign` | mv_frame_audience_daily | 8 MB | WHERE campaign_id |
| `cache_campaign_reach_day_cumulative_..._date_key` | cache_campaign_reach_day_cumulative | 368 KB | UNIQUE covers WHERE campaign_id |
| `idx_reach_week_campaign` | cache_campaign_reach_week | 96 KB | WHERE campaign_id |
| `idx_mv_campaign_browser_campaign_id` | mv_campaign_browser | 40 KB | WHERE campaign_id |
| `route_releases_pkey` | route_releases | 16 KB | JOIN ON id |
| `route_releases_release_number_key` | route_releases | 16 KB | WHERE release_number + UPSERT |
| `idx_route_releases_trading_period` | route_releases | 16 KB | WHERE trading_period range |

### Retained as Table Constraints (small, not worth removing)

Primary keys and unique constraints on small pipeline tables (< 400 KB each).
These preserve data integrity and cost negligible space.

## Phase 5: Unused Table Cleanup (~19.5 GB)

After removing indexes, a second audit identified 24 tables never referenced in
any app code (`src/`), tests, or runtime configuration. All `mv_*` tables had been
converted from materialised views to regular tables during the DigitalOcean export
prep (January 2026), so source-table dependencies (e.g., `mv_playout_15min_brands`
feeding `mv_campaign_browser`) no longer apply.

References were found only in migration SQL (historical), `refresh_local_mvs.sh`
(dead — no matviews remain), and export scripts (not runtime).

### Large Tables Dropped (> 1 GB)

| Table | Size | What it was |
|-------|------|-------------|
| `mv_cache_campaign_impacts_frame_1hr` | 9,031 MB | Frame-level hourly impacts — app uses `_1hr` and `_frame` separately |
| `mv_playout_15min_brands` | 5,425 MB | Playout data with brand IDs — app uses `mv_frame_brand_daily/hourly` |
| `mv_playout_60min` | 1,797 MB | 60-min playout aggregation — unused |
| `mv_playout_frame_hour` | 1,104 MB | Frame-hour playout aggregation — unused |
| `mv_playout_120min` | 1,004 MB | 120-min playout aggregation — unused |

### Medium Tables Dropped

| Table | Size | What it was |
|-------|------|-------------|
| `mv_cache_campaign_impacts_frame_day` | 634 MB | Frame-day impacts — unused |
| `mv_cache_campaign_impacts_15min` | 429 MB | 15-min impacts — unused |
| `mv_playout_frame_day` | 96 MB | Frame-day playouts — unused |
| `mv_cache_campaign_impacts_daypart` | 20 MB | Daypart impacts — unused |
| `cache_campaign_reach_day` | 1.3 MB | Daily reach (app uses `_day_cumulative`) |
| `mv_cache_campaign_impacts_week` | 1.2 MB | Weekly impacts — unused |
| `mv_playout_dates` | 40 KB | Date list — unused |

### Small Pipeline-Only Tables Dropped

| Table | What it was |
|-------|-------------|
| `playout_data` | Empty (truncated) |
| `playout_imports` | Pipeline import tracking |
| `playout_dates` | Pipeline date tracking |
| `spot_break_combinations` | Pipeline spot break lookup |
| `campaign_cache_limitations` | Pipeline — data pre-joined into mv_campaign_browser |
| `cache_statistics` | Pipeline cache tracking |
| `cache_demographic_universes` | Pipeline reference |
| `cache_space_brands` | Pipeline SPACE API cache |
| `cache_space_buyers` | Pipeline SPACE API cache |
| `cache_space_agencies` | Pipeline SPACE API cache |
| `cache_space_media_owners` | Pipeline SPACE API cache |
| `route_frame_cache_sync_log` | Pipeline sync log |

### Cascade Drops (automatic)

Dropping `spot_break_combinations` removed FK `cache_route_impacts_15min_by_demo_spot_break_id_fkey`.
Dropping `campaign_cache_limitations` removed views `v_uncacheable_campaigns` and `v_limitation_health`.
Dropping `cache_space_*` removed view `cache_space_statistics`.
None of these were used by the app.

## Final Database State

18 tables + 1 view remaining (all used by the app):

| Table | Size | Purpose |
|-------|------|---------|
| `cache_route_impacts_15min_by_demo` | 44 GB | Fallback for impacts queries |
| `mv_playout_15min` | 8,642 MB | Campaign summary + frame audience table |
| `mv_frame_audience_hourly` | 2,635 MB | Frame audience hourly tab |
| `mv_frame_brand_hourly` | 1,523 MB | Brand JOIN for hourly tab |
| `route_frame_details` | 415 MB | Region/environment/town JOINs |
| `mv_frame_audience_daily` | 186 MB | Frame audience daily tab |
| `route_frames` | 164 MB | Lat/lng, frameid JOINs |
| `mv_frame_brand_daily` | 105 MB | Brand JOIN for daily tab |
| `mv_cache_campaign_impacts_1hr` | 98 MB | Hourly heatmap |
| `mv_cache_campaign_impacts_frame` | 81 MB | Geographic + environment + regional |
| `mv_cache_campaign_impacts_day` | 5.5 MB | Daily time series |
| `cache_campaign_reach_day_cumulative` | 1.9 MB | Daily cumulative reach |
| `cache_campaign_reach_week` | 760 KB | Weekly reach |
| `mv_campaign_browser` | 456 KB | Campaign browser listing |
| `cache_campaign_reach_full` | 240 KB | Full campaign reach |
| `mv_campaign_browser_summary` | 96 KB | Browser summary stats |
| `route_releases` | 88 KB | Release date lookups |
| `mv_platform_stats` | 40 KB | Platform stats display |
| `v_demographic_segment_count` | (view) | Demographic segment count |

## Impact on DigitalOcean Deployment

The database export for DigitalOcean (`~/poc export/route_poc_export/`) was created
**before** this cleanup. A fresh export after this cleanup would be significantly smaller.

- Previous export: 7.9 GB compressed (pre-cleanup)
- Expected after full cleanup: ~3-4 GB compressed (estimate)

## Reproducing This Cleanup

If the cleanup needs to be run on a fresh database restore, use the SQL from
the handover document: `Claude/handover/SESSION_2026-02-05_INDEX_CLEANUP.md`

---

*Last Updated: 5 February 2026*
