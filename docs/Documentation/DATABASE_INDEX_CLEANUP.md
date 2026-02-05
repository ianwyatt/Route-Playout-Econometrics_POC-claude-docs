# Database Index Cleanup — POC App Optimisation

**Date**: 5 February 2026
**Database**: Local Mac (`route_poc`)
**Result**: 114 GB → 76 GB (38 GB freed, 33% reduction)

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

## Impact on DigitalOcean Deployment

The database export for DigitalOcean (`~/poc export/route_poc_export/`) was created
**before** this cleanup. A fresh export after this cleanup would be significantly smaller.

If re-exporting:
- Previous export: 7.9 GB compressed
- Expected after cleanup: ~5-6 GB compressed (estimate)

## Reproducing This Cleanup

If the indexes need to be dropped on a fresh database restore, run the SQL from
the handover document: `Claude/handover/SESSION_2026-02-05_INDEX_CLEANUP.md`

---

*Last Updated: 5 February 2026*
