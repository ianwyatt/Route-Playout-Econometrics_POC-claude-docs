# Code Review – Deeper Rescan (Reusability, Modularity, Code Quality)

Date: 2026-02-04

## Overall Score (Full)
**6.4 / 10**

**Summary:** The codebase has a clear modular intent (components, tabs, db query facades, export utilities), but several cross-module seams are inconsistent. The biggest reusability drag is database-selection not being threaded consistently through cached loaders and export pipelines, which can yield stale or mixed-source data. There’s also repeated brand formatting logic and silent error swallowing in export data collection, both of which undermine modular reuse and predictability.

## Findings

### 1) Cached frame-audience loaders ignore DB selection
**File:** `src/ui/tabs/detailed_analysis.py`

- The cached loaders (`_load_frame_*` and counts) are keyed only by `campaign_id` (and `limit`). They don’t accept or pass the active `use_primary_database` selection.
- Result: If the user switches DBs, `st.cache_data` can serve stale results from the previous database.
- Recommendation: Add a `use_primary` parameter to these loaders, pass it from session state, and include it in the cache key.

### 2) Time series tab ignores DB selection
**File:** `src/ui/tabs/time_series.py`

- `get_available_demographics_for_campaign_sync`, `get_daily_impacts_sync`, and `get_hourly_impacts_sync` are called without `use_primary`.
- Result: DB toggle is ignored; this tab can drift from the rest of the UI.
- Recommendation: Thread `use_primary` from session state into these calls for consistent modular behavior.

### 3) Export data gathering mixes DB sources
**File:** `src/ui/utils/export/data.py`

- `gather_campaign_data` accepts `use_primary` but does not pass it to several queries (geographic, regional, environment, and frame-audience queries).
- Result: Exports can mix data from different DB sources depending on env defaults.
- Recommendation: Pass `use_primary` to every query function consistently.

### 4) Export data gathering swallows exceptions
**File:** `src/ui/utils/export/data.py`

- Broad `except Exception: pass` blocks for each dataset suppress errors silently.
- Result: Exports can be incomplete without any signal to the user or logs.
- Recommendation: Log errors or collect warnings so export failures are visible and diagnosable.

### 5) Brand formatting duplicated in multiple UI paths
**Files:** `src/ui/app.py`, `src/ui/components/campaign_browser/manual_input.py`

- Brand parsing/anonymization logic is re-implemented in multiple places instead of reusing `src/utils/formatters.format_brands` or a dedicated helper.
- Result: Formatting/anonymization rules can diverge over time; hard to reuse reliably.
- Recommendation: Centralize brand formatting in one utility and reuse everywhere.

## Notes
- The earlier cache-stats finding provided in the prompt does not appear in the current `src/ui/app.py` snapshot; no such block exists in this tree.

## Suggested Next Steps
1) Thread `use_primary` consistently through cached loaders and time-series queries.
2) Fix `gather_campaign_data` to pass `use_primary` everywhere and add logging for exceptions.
3) Centralize brand formatting/anonymization logic in a single utility.

---

## Resolution Status

**All 5 findings resolved**: 4 February 2026

| # | Finding | Status | Details |
|---|---------|--------|---------|
| 1 | Cached frame-audience loaders ignore DB selection | **FIXED** | Added `use_primary` param to 6 loaders, 3 render functions, 9 call sites |
| 2 | Time series tab ignores DB selection | **FIXED** | Added `use_primary` to 3 query calls |
| 3 | Export data gathering mixes DB sources | **FIXED** | Added `use_primary=use_primary` to 5 missing query calls |
| 4 | Export data gathering swallows exceptions | **FIXED** | Replaced 9 bare `except: pass` with `logger.warning()` calls |
| 5 | Brand formatting duplicated in multiple UI paths | **FIXED** | Extended `format_brands()` utility, replaced ~58 lines of duplication |

**Handover**: `handover/SESSION_2026-02-04_CODEX_REVIEW_FIXES.md`

