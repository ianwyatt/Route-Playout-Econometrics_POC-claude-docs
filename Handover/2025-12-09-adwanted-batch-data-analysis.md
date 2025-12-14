# Session Handover - 2025-12-09

**Session Focus:** Adwanted Batch Data Analysis and Documentation
**Branch:** refactor/modularity-cleanup

---

## Summary

Analysed the Adwanted batch data specification against POC UI requirements to identify gaps, pitfalls, and post-import actions needed. Created comprehensive documentation for both the POC team (post-import checklist) and pipeline team (spec updates and alias view creation).

---

## Context

Adwanted/MediaTel will bulk-produce audience data (impacts, reach, GRP, frequency) for all Talon campaigns (~14 months of playout data, 11B+ records). This replaces the current approach where Route's pipeline calls the Route API directly.

**Key Documents Reviewed:**
- `/Users/ianwyatt/PycharmProjects/route-playout-pipeline/Claude/Documentation/Adwanted_Batch_Request/ADWANTED_REQUEST_FINAL.md` - The spec sent to Adwanted (13 tables)
- `docs/11-database-schema.md` - POC database reference
- `src/db/queries/*.py` - All query files to identify table dependencies

---

## Key Findings

### 1. Tables Adwanted Delivers (Match POC Needs)

These tables are correctly specified and match what POC uses:
- `cache_route_impacts_15min_by_demo` (~416M rows)
- `cache_campaign_reach_day`
- `cache_campaign_reach_week`
- `cache_campaign_reach_full`
- `cache_campaign_reach_day_cumulative`
- `cache_space_brands/buyers/agencies/media_owners`
- `cache_demographic_universes`

### 2. Tables Route Already Has (NOT from Adwanted)

- `route_frames` - Frame coordinates/metadata
- `route_frame_details` - Frame environment/format/region
- `route_releases` - Release tracking (R49-R61)

### 3. Playout Aggregation Tables (Added to Spec)

Recommended Adwanted create these (11B raw records too heavy for Route to aggregate):

| Table | Purpose |
|-------|---------|
| `playout_15min` | 15-min window aggregations |
| `playout_frame_day` | Daily playout counts per frame |
| `playout_frame_hour` | Hourly playout counts per frame |

**Naming Decision:** Adwanted delivers WITHOUT `mv_` prefix. Pipeline team creates alias views after import.

### 4. MVs Route Must Create After Import

These are derived from Adwanted data + Route frame data:
- `mv_campaign_browser` - Campaign browser listing
- `mv_campaign_browser_summary` - Header statistics
- `mv_frame_audience_daily` - Denormalised daily frame data
- `mv_frame_audience_hourly` - Denormalised hourly frame data
- `mv_frame_audience_campaign` - Campaign-level counts
- `mv_playout_15min_brands` - Playout with brand name joins

### 5. campaign_cache_limitations Schema Change

**Current Adwanted spec has:** `is_on_off_campaign`, `gap_days`, `active_periods`, `limitation_reason`

**Simplified to:**
- `limitation_type`: 'flighted_campaign' or 'no_route_frames'
- `limitation_reason`: Human-readable explanation

Removed JSON size limitation (Adwanted maintains the API, no payload size constraints).

### 6. Demographics

**No POC changes needed.** The POC already uses friendly codes (`all_adults`, `abc1`, etc.) which match what Adwanted will deliver in `cache_route_impacts_15min_by_demo.demographic_segment`.

Current `cache_demographic_universes` table is incomplete (only has ageband) but will be populated correctly by Adwanted with all 7 demographics per release.

---

## Documents Created

### 1. Post-Import Checklist (POC Team)

**Location:** `Claude/Documentation/Adwanted_Data_Import/POST_IMPORT_CHECKLIST.md`

**Contents:**
- Pre-import: Data Route already has
- Adwanted delivers: 16 tables (13 original + 3 playout aggregations)
- Name mapping: Alias views if Adwanted uses different names
- Post-import: MVs Route must create
- Verification checklist: Data integrity, entity lookups, frame joins
- MV/View names: All 7 views POC expects
- UI smoke test: Step-by-step verification

### 2. Pipeline Team Handover (Adwanted Spec Updates)

**Location:** `Claude/Handover/For_Pipeline_Team/Adwanted_Spec_Updates_20251209.md`

**Contents:**
1. Add playout aggregation tables (14-16) to spec
2. Update campaign_cache_limitations schema
3. Naming convention: No `mv_` prefix from Adwanted
4. **Action Required:** Create alias views after import:
   ```sql
   CREATE VIEW mv_playout_15min AS SELECT * FROM playout_15min;
   CREATE VIEW mv_playout_frame_day AS SELECT * FROM playout_frame_day;
   CREATE VIEW mv_playout_frame_hour AS SELECT * FROM playout_frame_hour;
   ```
5. Tables correctly specified (no changes needed)

---

## POC UI Table Dependencies

Full list of tables/views the POC queries (from code search):

| Table/View | Used By |
|------------|---------|
| `mv_campaign_browser` | Campaign browser |
| `mv_campaign_browser_summary` | Browser header stats |
| `cache_campaign_reach_day` | Daily reach metrics |
| `cache_campaign_reach_week` | Weekly reach/GRP tab |
| `cache_campaign_reach_full` | Executive summary |
| `cache_campaign_reach_day_cumulative` | Cumulative charts |
| `cache_route_impacts_15min_by_demo` | Demographics, impacts |
| `mv_frame_audience_daily` | Frame Audiences daily tab |
| `mv_frame_audience_hourly` | Frame Audiences hourly tab |
| `mv_playout_15min` | campaigns.py, frame_audience.py |
| `mv_playout_15min_brands` | brand_split_service.py |
| `route_frames` | Geographic maps |
| `route_frame_details` | Frame metadata, regions |
| `route_releases` | Release joins |
| `cache_space_brands` | Brand name lookups |
| `cache_space_buyers` | Buyer name lookups |
| `cache_space_media_owners` | Media owner lookups |
| `cache_space_agencies` | Agency name lookups |
| `cache_demographic_universes` | GRP calculations |

---

## Previous Session Context

This session continued from a modularity refactor that:
- Consolidated config files
- Archived dead code to `src/archive/`
- Modularised large files into packages
- Cleaned up /docs with numbered prefixes (1-11)
- Created `docs/11-database-schema.md`
- Updated README.md with correct project structure

---

## Files Modified This Session

| File | Action |
|------|--------|
| `Claude/Documentation/Adwanted_Data_Import/POST_IMPORT_CHECKLIST.md` | Created |
| `Claude/Handover/For_Pipeline_Team/Adwanted_Spec_Updates_20251209.md` | Created |
| `Claude/Handover/2025-12-09-adwanted-batch-data-analysis.md` | Created (this file) |

---

## No Commits Made

Documentation only - no code changes requiring commit.

---

## Next Steps

1. **Pipeline Team:** Review `Adwanted_Spec_Updates_20251209.md` and update `ADWANTED_REQUEST_FINAL.md`
2. **After Adwanted Delivery:** Follow `POST_IMPORT_CHECKLIST.md` for import and verification
3. **POC:** No code changes needed - ready to receive Adwanted data

---

*Created: 2025-12-09*
