# Code Review – Deep Rescan (Reusability, Modularity, Code Quality)

Date: 2026-02-04

## Overall Score
**7.0 / 10**

**Rationale:** The recent fixes improve consistency and reusability, especially around database selection, exports, and brand formatting. Remaining gaps are mostly in a couple of tabs still ignoring the selected DB context, which can yield inconsistent UI state and cached results.

## Verification of Prior Findings (Resolved)
1) **Detailed Analysis cached loaders ignore DB selection** — Fixed. Loaders now accept `use_primary` and pass it to all queries; `use_primary` is part of the cache key.
2) **Time Series tab ignores DB selection** — Fixed. `use_primary` is read from session state and passed to demographics/daily/hourly queries.
3) **Export data mixes DB sources** — Fixed. `use_primary` is now passed to geographic/regional/environment/frame daily/hourly queries.
4) **Export data swallows exceptions** — Fixed. Exceptions now log warnings with campaign context.
5) **Brand formatting duplicated** — Fixed. Brand parsing/anonymisation consolidated via `format_brands()` and reused in the header and manual input.

## New Findings

### 1) Geographic tab ignores selected DB
**Files:** `src/ui/tabs/geographic.py`

- The geographic tab calls `get_frame_geographic_data_sync`, `get_regional_impacts_sync`, `get_environment_impacts_sync`, and `_get_available_demographics()` without `use_primary`.
- Result: DB selection can be inconsistent with other tabs, and cached demographics may not match the selected DB.
- Fix: Thread `use_primary = st.session_state.get("use_primary_database", True)` into the calls and add it to `_get_available_demographics` and its cache key.

### 2) Overview tab campaign shape ignores selected DB
**Files:** `src/ui/tabs/overview.py`

- `_render_campaign_shape()` calls `get_daily_impacts_sync(campaign_id)` without passing `use_primary`.
- Result: Overview charts can show data from the wrong database after a DB switch.
- Fix: Read `use_primary` from session state and pass it through.

## Fix Quality Assessment
**Just right.** Changes are localized, improve reuse, and keep API contracts simple. `format_brands()` gained minimal, pragmatic options (`parse_string`, `max_display`) without over‑engineering.

## Notes
- I did not run tests. This review is based on code inspection only.
