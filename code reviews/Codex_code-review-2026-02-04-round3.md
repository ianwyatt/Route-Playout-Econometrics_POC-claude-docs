# Code Review – Round 3 Deep Rescan (Reusability, Modularity, Code Quality)

Date: 2026-02-04

## Overall Score
**7.2 / 10**

**Rationale:** The recent fixes substantially improved modular consistency (database selection threading, export robustness, brand formatting reuse). Remaining gaps are smaller but still meaningful: a few UI components still bypass `use_primary` or cache without it, which can yield cross‑DB inconsistencies and reduce composability.

## Verification of Round 2 Findings (Resolved)
1) **Geographic tab ignores selected DB** — **Resolved.** `use_primary` is read from session state, passed to all geographic queries, and `_get_available_demographics` now accepts `use_primary` (included in cache key).
2) **Overview campaign shape ignores selected DB** — **Resolved.** `_render_campaign_shape` now accepts `use_primary` and passes it to `get_daily_impacts_sync`.

## New Findings

### 1) Manual campaign lookup ignores selected DB
**File:** `src/ui/components/campaign_browser/manual_input.py`

- `get_campaign_from_browser_by_id_sync(campaign_id.strip())` is called without `use_primary`.
- Result: Manual ID lookup can diverge from the selected DB and show inconsistent results vs the browse tab.
- Fix: Thread `use_primary = st.session_state.get("use_primary_database", True)` into the call (and include in any cache keys if added later).

### 2) Campaign header info ignores selected DB
**File:** `src/ui/app.py`

- `get_campaign_header_info_sync(st.session_state.selected_campaign_id)` is called without `use_primary`.
- Result: Header (brand/date range) can reflect a different database than the rest of the view.
- Fix: Pass `use_primary=st.session_state.get("use_primary_database", True)`.

### 3) Executive summary chart data ignores selected DB
**File:** `src/ui/tabs/executive_summary.py`

- `_get_exec_summary_chart_data()` caches by `campaign_id` but calls `get_daily_impacts_sync`, `get_hourly_impacts_sync`, and `get_regional_impacts_sync` without `use_primary`.
- Result: Cache can serve data from the wrong DB after a switch; charts can diverge from other tabs.
- Fix: Add a `use_primary` parameter (part of cache key) and pass it through to the queries.

### 4) Campaign browser platform stats ignore selected DB
**File:** `src/ui/components/campaign_browser/summary.py`

- `get_platform_stats_sync()` is called without `use_primary`.
- Result: Dataset summary can show counts from a different DB than the one currently selected.
- Fix: Thread `use_primary` from session state.

## use_primary Consistency Across UI Layer
**Not yet fully consistent.** Most tabs now pass `use_primary`, but the following still need updates:
- `src/ui/components/campaign_browser/manual_input.py`
- `src/ui/app.py` (header info)
- `src/ui/tabs/executive_summary.py` (chart data cache)
- `src/ui/components/campaign_browser/summary.py` (platform stats)

## Fix Quality Assessment
**Just right.** The recent updates improved reusability without over‑engineering. Remaining fixes are localized and consistent with the established pattern.

## Notes
- I did not run tests. This review is based on code inspection only.

---

## Resolution Status (added post-review)

| Finding | Status | Details |
|---------|--------|---------|
| 1) Manual campaign lookup | **RESOLVED** | `use_primary` threaded into `get_campaign_from_browser_by_id_sync()` |
| 2) Campaign header info | **RESOLVED** | `use_primary` threaded into `get_campaign_header_info_sync()` |
| 3) Executive summary chart data | **RESOLVED** | `use_primary` added to `_get_exec_summary_chart_data()` signature (cache key) + 3 query calls |
| 4) Platform stats | **RESOLVED** | `use_primary` threaded into `get_platform_stats_sync()` |

All 4 findings fixed. Unit tests: 66/66 pass. Round 4 review prompt submitted.
