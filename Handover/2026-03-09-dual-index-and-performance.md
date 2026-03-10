# Handover: Dual Mobile Index & Performance Optimisation

**Date:** 9 March 2026
**Branch:** `feature/mobile-volume-index`
**Status:** Import complete, cache build running (final table), UI caching implemented

---

## What Was Done This Session

### 1. Dual Mobile Index (Average + Median)

The analyst provided a v2 materialised view (`cristina.oa_frames_hourly_index_v2`) with two index types:
- **`average_index`** — mean footfall / annual OA average (same concept as v1's `a_index`)
- **`median_index`** — median footfall / annual OA average (more robust to outliers)

**Schema changes:**
- `mobile_volume_index` table: `index_value` column replaced with `average_index` + `median_index`
- All 7 cache tables: added `median_indexed_*` columns alongside existing `indexed_impacts`
- Cache populate queries: compute both `SUM(impacts * average_index)` and `SUM(impacts * median_index)`

**Import script (`scripts/import_mobile_index_from_db.py`):**
- Updated to query `cristina.oa_frames_hourly_index_v2` (130M rows, 19,933 frames)
- Pulls both `average_index` and `median_index`
- Created `frame_id` index on the v2 MV on the analyst's database
- Import completed: 99,870,680 rows in 67 minutes

**UI — dual toggles:**
- Two independent checkboxes in `app.py`: "Average-Indexed Impacts" / "Median-Indexed Impacts"
- Session state keys: `mi_average_toggle`, `mi_median_toggle`
- `global_mobile_index_toggle` remains as backwards-compat OR of both
- All 6 tabs updated to show either, both, or neither index type
- Colour scheme: average = orange `#F18F01` (dashed), median = purple `#8E44AD` (dotted)

**Files modified for dual index:**
- `scripts/import_mobile_index.py` — DDL, cache populate queries, CSV parser
- `scripts/import_mobile_index_from_db.py` — v2 source, both columns
- `src/db/queries/mobile_index.py` — all 6 query functions return both columns
- `src/ui/app.py` — dual toggle checkboxes
- `src/ui/tabs/overview.py` — dual metrics, dual chart traces
- `src/ui/tabs/reach_grp.py` — dual table columns, dual chart bars
- `src/ui/tabs/time_series.py` — dual metrics, dual chart traces, dual bars
- `src/ui/tabs/geographic.py` — dual lookups, dual metrics, dual table columns
- `src/ui/tabs/detailed_analysis.py` — dual table columns
- `src/ui/tabs/executive_summary.py` — dual delivery card rows, dual chart traces

### 2. Performance Optimisation (Phase 1)

**Problem:** Every Streamlit rerender fired 16-20 uncached DB connections. Mobile index queries had zero caching.

**Cached wrappers added to `app.py`:**

| Wrapper | Raw function | TTL |
|---------|-------------|-----|
| `load_mobile_index_exists` | `mobile_index_table_exists` | 1 hour |
| `load_mobile_index_coverage` | `get_mobile_index_coverage_sync` | 1 hour |
| `load_campaign_header` | `get_campaign_header_info_sync` | 1 hour |
| `load_mi_daily` | `get_daily_impacts_with_mobile_index_sync` | 1 hour |
| `load_mi_weekly` | `get_weekly_impacts_with_mobile_index_sync` | 1 hour |
| `load_mi_hourly` | `get_hourly_impacts_with_mobile_index_sync` | 1 hour |
| `load_mi_frame_totals` | `get_frame_totals_with_mobile_index_sync` | 1 hour |
| `load_mi_frame_daily` | `get_frame_daily_with_mobile_index_sync` | 1 hour |
| `load_mi_frame_hourly` | `get_frame_hourly_with_mobile_index_sync` | 1 hour |
| `load_frame_geographic_data` | `get_frame_geographic_data_sync` | 10 min |
| `load_regional_impacts` | `get_regional_impacts_sync` | 10 min |
| `load_environment_impacts` | `get_environment_impacts_sync` | 10 min |
| `load_available_demographics` | `get_available_demographics_for_campaign_sync` | 10 min |

**All tabs updated** to use cached wrappers via lazy imports (deferred import pattern to avoid circular imports with `app.py`).

**Result:** DB connections per widget interaction reduced from ~16-20 to 0 after first load.

### 3. Optimised Cache Build (ready but not yet tested)

The old cache build repeats the same expensive 416M-row JOIN six times (~15-20 min each = ~2 hours total).

**New approach in `build_cache()`:**
1. Create a single temp table `_mi_join_base` with the pre-joined, pre-extracted data
2. Index the temp table
3. Each cache table aggregates from the temp table (no JOIN, no subquery)
4. Drop temp table

**Expected improvement:** ~2 hours → ~30-40 minutes.

The code is in `CACHE_POPULATE_QUERIES_FROM_BASE` dict and the rewritten `build_cache()` function in `scripts/import_mobile_index.py`. It will be used on the next cache rebuild.

---

## Current State

### Cache Build
- **6 of 7 tables complete** — `cache_mi_coverage` still running (slow due to old-style full-table JOIN)
- When it finishes, the app should work with real analyst data and both index toggles
- Next rebuild will use the optimised temp table approach

### Cache Table Row Counts (this build)

| Table | Rows |
|-------|------|
| `cache_mi_daily` | 67,025 |
| `cache_mi_weekly` | 14,189 |
| `cache_mi_hourly` | 504,728 |
| `cache_mi_frame_daily` | 7,382,697 |
| `cache_mi_frame_hourly` | 104,665,855 |
| `cache_mi_frame_totals` | 915,383 |
| `cache_mi_coverage` | (building) |

### Raw Data

| Table | Rows |
|-------|------|
| `mobile_volume_index` | 99,870,680 |

### Source (analyst DB)

| MV | Rows | Frames | Date Range |
|----|------|--------|------------|
| `cristina.oa_frames_hourly_index_v2` | 130,121,387 | 19,933 | 2024-04-01 to 2024-12-31 |

---

## What's Left To Do

### Immediate (this session or next)
1. Wait for `cache_mi_coverage` to finish
2. Test the app with both toggles in browser
3. Verify the `get_frame_hourly_with_mobile_index_sync` query still used directly in `detailed_analysis.py` — may need cached wrapper

### Performance Plan (documented in `Claude/Plans/2026-03-09-performance-optimisation.md`)
- **Phase 2:** Test the optimised cache build (temp table approach) — run `--cache-only`
- **Phase 3:** Connection pooling, missing indexes, fix demographic count scan, refactor frame audience query

### Branch
- Not yet committed — significant changes across many files
- Should commit after cache build completes and app is verified working

---

## Key Files Modified

```
scripts/import_mobile_index.py          — DDL, cache queries, optimised build
scripts/import_mobile_index_from_db.py  — v2 source, dual columns
src/db/queries/mobile_index.py          — all queries return both index types
src/ui/app.py                           — dual toggles, cached wrappers
src/ui/tabs/overview.py                 — dual index support, cached queries
src/ui/tabs/reach_grp.py               — dual index support, cached queries
src/ui/tabs/time_series.py             — dual index support, cached queries, reduced fill_gaps calls
src/ui/tabs/geographic.py              — dual index support, cached queries
src/ui/tabs/detailed_analysis.py       — dual index support, cached queries
src/ui/tabs/executive_summary.py       — dual index support, cached queries
Claude/Plans/2026-03-09-performance-optimisation.md — full optimisation plan
```
