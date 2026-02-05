# Session Handover: Database Cleanup + DigitalOcean Deployment Path

**Date**: 5 February 2026
**Session Focus**: Remove unused indexes and tables to reduce DB size before DigitalOcean deployment

---

## Summary

Audited all 101 database indexes and 42 tables against every SQL query in the POC
Streamlit app. Dropped 64 unused indexes (38 GB) and 24 unused tables (19 GB).
The local database went from 114 GB to 57 GB — a 50% reduction. This directly
benefits the upcoming DigitalOcean deployment by reducing transfer and storage costs.

---

## Work Completed This Session

### Database Cleanup

**Before**: 114 GB database, 101 indexes, 42 tables
**After**: 57 GB database, 14 indexes, 18 tables + 1 view
**Freed**: 57 GB (50%)

#### Methodology

1. Queried `pg_stat_user_indexes` for all index sizes and usage statistics
2. Read every query function in `src/db/queries/*.py` and `src/db/route_releases.py`
3. Mapped every WHERE, JOIN, ORDER BY, GROUP BY clause to serving indexes
4. Identified duplicates, pipeline-only indexes, and completely unused indexes
5. Dropped in 4 phases, verified after each

#### What Was Dropped (4 phases)

| Phase | Target | Savings |
|-------|--------|---------|
| 1 | `cache_route_impacts_15min_by_demo` — PK + 5 indexes | ~35.7 GB |
| 2 | Unused MV indexes (frame_1hr, playout_15min frame/time, playout_brands) | ~2.5 GB |
| 3 | Duplicate + unused `route_frame*` indexes (lookup dupes, location, region, etc.) | ~232 MB |
| 4 | Small pipeline-only + redundant reach/playout indexes (38 indexes) | ~3 MB |

#### Key Decision: Fallback Index Retained

`idx_impacts_demo_campaign` on `(campaign_id, demographic_segment)` — **2.8 GB kept**.
The fallback code in `impacts.py` queries `cache_route_impacts_15min_by_demo` when
materialised views lack data. Although never triggered (0 scans), dropping it would
risk a sequential scan on 41 GB if the fallback ever fires.

#### SQL to Reproduce (for fresh restores)

```sql
-- Phase 1: cache_route_impacts_15min_by_demo (~35.7 GB)
DROP INDEX IF EXISTS idx_impacts_demo_campaign_time;
DROP INDEX IF EXISTS idx_impacts_demo_frame;
DROP INDEX IF EXISTS idx_impacts_demo_time;
DROP INDEX IF EXISTS idx_impacts_demo_buyer;
DROP INDEX IF EXISTS idx_cache_spot_break_id;
ALTER TABLE cache_route_impacts_15min_by_demo
    DROP CONSTRAINT IF EXISTS cache_route_impacts_15min_by_demo_pkey;

-- Phase 2: Unused MV indexes (~2.5 GB)
DROP INDEX IF EXISTS idx_mv_cache_campaign_impacts_frame_1hr_campaign;
DROP INDEX IF EXISTS idx_mv_playout_15min_frame;
DROP INDEX IF EXISTS idx_mv_playout_15min_time;
DROP INDEX IF EXISTS idx_mv_playout_15min_brands_campaign;
DROP INDEX IF EXISTS idx_mv_playout_15min_brands_brand;

-- Phase 3: Duplicate & unused route_frame indexes (~232 MB)
DROP INDEX IF EXISTS idx_route_frame_details_lookup;
DROP INDEX IF EXISTS idx_route_frames_lookup;
DROP INDEX IF EXISTS idx_frame_details_location;
ALTER TABLE route_frame_details DROP CONSTRAINT IF EXISTS route_frame_details_pkey;
ALTER TABLE route_frames DROP CONSTRAINT IF EXISTS route_frames_pkey;
DROP INDEX IF EXISTS idx_frame_details_region;
DROP INDEX IF EXISTS idx_frame_details_town;
DROP INDEX IF EXISTS idx_frame_details_postal_district;
DROP INDEX IF EXISTS idx_frame_details_frame_type;
DROP INDEX IF EXISTS idx_frame_details_category;
DROP INDEX IF EXISTS idx_route_frame_details_metadata;
DROP INDEX IF EXISTS idx_route_frame_details_release;
DROP INDEX IF EXISTS idx_route_frames_environment;
DROP INDEX IF EXISTS idx_route_frames_release;
DROP INDEX IF EXISTS idx_route_frames_mediaowner;

-- Phase 4: Small pipeline-only & redundant
DROP INDEX IF EXISTS idx_mv_campaign_browser_start_date;
DROP INDEX IF EXISTS idx_mv_campaign_browser_last_activity;
DROP INDEX IF EXISTS idx_route_releases_number;
DROP INDEX IF EXISTS idx_route_releases_active;
DROP INDEX IF EXISTS idx_reach_day_buyer_campaign;
DROP INDEX IF EXISTS idx_reach_day_cached;
DROP INDEX IF EXISTS idx_reach_day_release;
DROP INDEX IF EXISTS idx_reach_day_cumulative_campaign;
DROP INDEX IF EXISTS idx_reach_day_cumulative_buyer;
DROP INDEX IF EXISTS idx_reach_day_cumulative_cached;
DROP INDEX IF EXISTS idx_reach_day_cumulative_approximate;
DROP INDEX IF EXISTS idx_reach_week_buyer_campaign;
DROP INDEX IF EXISTS idx_reach_week_cached;
DROP INDEX IF EXISTS idx_reach_week_type;
DROP INDEX IF EXISTS idx_reach_week_approximate;
DROP INDEX IF EXISTS idx_reach_full_buyer_campaign;
DROP INDEX IF EXISTS idx_reach_full_cached;
DROP INDEX IF EXISTS idx_reach_full_campaign;
DROP INDEX IF EXISTS idx_cache_reach_full_approximate;
DROP INDEX IF EXISTS idx_playout_frameid;
DROP INDEX IF EXISTS idx_playout_brand;
DROP INDEX IF EXISTS idx_playout_dates;
DROP INDEX IF EXISTS idx_playout_buyer;
DROP INDEX IF EXISTS idx_playout_media_owner;
DROP INDEX IF EXISTS idx_playout_campaign;
DROP INDEX IF EXISTS idx_playout_agency;
DROP INDEX IF EXISTS idx_spot_break_lookup;
DROP INDEX IF EXISTS idx_campaign_limitations_buyer_campaign;
DROP INDEX IF EXISTS idx_campaign_limitations_uncacheable;
DROP INDEX IF EXISTS idx_demographic_universe_code;
DROP INDEX IF EXISTS idx_demographic_universe_release;
DROP INDEX IF EXISTS idx_brand_name;
DROP INDEX IF EXISTS idx_buyer_name;
DROP INDEX IF EXISTS idx_agency_name;
DROP INDEX IF EXISTS idx_media_owner_name;
DROP INDEX IF EXISTS idx_sync_log_release;
DROP INDEX IF EXISTS idx_sync_log_started;
DROP INDEX IF EXISTS idx_sync_log_status;

-- Reclaim disk space
VACUUM ANALYZE;
```

#### Phase 5: Unused Table Cleanup (~19.5 GB)

After index cleanup, a second audit identified 24 tables never referenced in app code.
All `mv_*` tables were converted from materialised views to regular tables during the
January 2026 export prep, so source-table dependencies no longer apply.

```sql
-- Large unused tables (> 1 GB)
DROP TABLE IF EXISTS mv_cache_campaign_impacts_frame_1hr CASCADE;  -- 9,031 MB
DROP TABLE IF EXISTS mv_playout_15min_brands CASCADE;              -- 5,425 MB
DROP TABLE IF EXISTS mv_playout_60min CASCADE;                     -- 1,797 MB
DROP TABLE IF EXISTS mv_playout_frame_hour CASCADE;                -- 1,104 MB
DROP TABLE IF EXISTS mv_playout_120min CASCADE;                    -- 1,004 MB

-- Medium unused tables
DROP TABLE IF EXISTS mv_cache_campaign_impacts_frame_day CASCADE;  -- 634 MB
DROP TABLE IF EXISTS mv_cache_campaign_impacts_15min CASCADE;      -- 429 MB
DROP TABLE IF EXISTS mv_playout_frame_day CASCADE;                 -- 96 MB
DROP TABLE IF EXISTS mv_cache_campaign_impacts_daypart CASCADE;    -- 20 MB
DROP TABLE IF EXISTS mv_cache_campaign_impacts_week CASCADE;       -- 1.2 MB
DROP TABLE IF EXISTS cache_campaign_reach_day CASCADE;             -- 1.3 MB
DROP TABLE IF EXISTS mv_playout_dates CASCADE;                     -- 40 KB

-- Small pipeline-only tables
DROP TABLE IF EXISTS playout_data CASCADE;
DROP TABLE IF EXISTS playout_imports CASCADE;
DROP TABLE IF EXISTS playout_dates CASCADE;
DROP TABLE IF EXISTS spot_break_combinations CASCADE;
DROP TABLE IF EXISTS campaign_cache_limitations CASCADE;
DROP TABLE IF EXISTS cache_statistics CASCADE;
DROP TABLE IF EXISTS cache_demographic_universes CASCADE;
DROP TABLE IF EXISTS cache_space_brands CASCADE;
DROP TABLE IF EXISTS cache_space_buyers CASCADE;
DROP TABLE IF EXISTS cache_space_agencies CASCADE;
DROP TABLE IF EXISTS cache_space_media_owners CASCADE;
DROP TABLE IF EXISTS route_frame_cache_sync_log CASCADE;

VACUUM ANALYZE;
```

**Cascade drops** (automatic, all pipeline-only):
- FK `cache_route_impacts_15min_by_demo_spot_break_id_fkey` (from `spot_break_combinations`)
- Views `v_uncacheable_campaigns`, `v_limitation_health` (from `campaign_cache_limitations`)
- View `cache_space_statistics` (from `cache_space_*`)

### Documentation

- `Claude/docs/Documentation/DATABASE_INDEX_CLEANUP.md` — Full analysis with methodology, what was dropped/kept, and rationale

---

## Database State

**Local Mac (Secondary):**
- Size: 57 GB (was 114 GB)
- 18 tables + 1 view remaining (all used by app)
- 14 indexes remaining (~3.5 GB)
- VACUUM ANALYZE completed
- All app functionality preserved

**MS-01 (Primary):** Unchanged — indexes and tables not yet cleaned

**Previous backup**: `~/Desktop/route_poc_adwanted_20260204.dump` (7.9 GB, pre-cleanup)

---

## Continuing From Previous Session: DigitalOcean Deployment

### Context

The Adwanted developer handover is complete (tag `v2.0-adwanted-handover` at `eb5a7c8`).
The next priority is deploying to DigitalOcean for external access.

### Impact of Cleanup on Deployment

The existing database export at `~/poc export/route_poc_export/` (7.9 GB) was created
**before** this cleanup. Options:

1. **Re-export after cleanup** (recommended) — will be much smaller (~3-4 GB estimated),
   faster to transfer, won't waste storage on dropped indexes/tables on DO
2. **Use existing export** — restore then run the full cleanup SQL above. Wastes
   temporary disk space during restore but achieves the same end state.

### DigitalOcean Deployment Task List

**Database (~$61/month)**
- [ ] Create DigitalOcean account / login
- [ ] Provision Managed PostgreSQL (London, Basic 4 GB, 60 GB storage)
- [ ] Re-export database from local Mac (post-cleanup) OR use existing export
- [ ] Transfer export file to DO
- [ ] Restore database with pg_restore
- [ ] If using old export: run index cleanup SQL
- [ ] Create read-only app user
- [ ] Verify data integrity

**App Droplet (~$6/month)**
- [ ] Provision Droplet (London, Basic 1 GB)
- [ ] SSH hardening (key-only, non-standard port, Fail2ban)
- [ ] Install Python 3.11+, UV, git
- [ ] Clone repo and install dependencies
- [ ] Configure .env for cloud database

**Reverse Proxy & Security**
- [ ] Install Caddy reverse proxy
- [ ] HTTPS with Let's Encrypt
- [ ] PocketID authentication (passkey-only)
- [ ] GB geo-blocking
- [ ] Security headers, rate limiting

**Estimated cost:** ~$67/month

### Key Reference Files

| File | Purpose |
|------|---------|
| `Claude/handover/2026-01-14-digitalocean-database-export.md` | Export details, restore commands |
| `Claude/todo/upcoming_tasks.md` | Task checklist |
| `Claude/docs/Documentation/SELF_HOSTED_DEPLOYMENT_GUIDE.md` | Pangolin/PocketID guide |
| `Claude/docs/Documentation/DATABASE_INDEX_CLEANUP.md` | Index cleanup documentation |
| `Claude/docs/Documentation/GITHUB_PRIVATE_REPO_ACCESS.md` | Fine-grained token auth |
| `~/poc export/route_poc_export/` | Database export (pre-cleanup, 7.9 GB) |

### VM Test Results (from previous session)

Ubuntu 24.04 fresh install verified:
- PostgreSQL 17, Python 3.12, uv
- Fine-grained tokens require `x-access-token` as username
- Ubuntu PostgreSQL needs password for TCP connections
- All app tabs functional after restore

### Start Prompt for DigitalOcean Session

```
Continue deploying Route Playout Econometrics POC to DigitalOcean.

Previous work:
- Database fully cleaned: 114 GB → 57 GB (dropped 64 indexes + 24 tables)
- Old export at ~/poc export/route_poc_export/ (7.9 GB, pre-cleanup)
- Re-export recommended for smaller transfer (~3-4 GB estimated)
- MVs converted to tables for pg_dump compatibility
- VM installation tested successfully on Ubuntu 24.04

Next steps:
1. Re-export database post-cleanup
2. Provision DO Managed PostgreSQL (London, Basic 4 GB)
3. Restore database
4. Provision Droplet for Streamlit app
5. Deploy with PocketID auth and GB geo-blocking

See handover: Claude/handover/SESSION_2026-02-05_INDEX_CLEANUP.md
Full cleanup SQL: in the handover above
```

---

## Pre-Existing Issues (unchanged)

### Test Failures (Local DB)

1. `test_empty_demographic_segments_list` — returns all data instead of empty
2. `test_query_performance_under_100ms` — 214ms on local DB

Not blocking; investigate separately.

### Primary DB (MS-01)

Indexes and tables have NOT been cleaned on the primary database. If needed, run
the full cleanup SQL from the "SQL to Reproduce" and "Phase 5" sections above.

---

## Future Enhancements (backlog)

- Cumulative build with daily data (smoother charts)
- Cost and financial tracking
- Natural language query interface
- AI-powered insights
- Classic frame support
- Multi-user support with role-based access
- Demographic filtering for Weekly Reach/GRP tab
- User areas with saved campaigns

---

*Handover prepared: 5 February 2026*
