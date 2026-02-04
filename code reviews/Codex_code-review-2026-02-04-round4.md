# Code Review – Round 4 Deep Rescan (Reusability, Modularity, Code Quality)

Date: 2026-02-04

## Overall Score
**7.4 / 10**

**Rationale:** The DB‑selection threading is now consistent across the active UI surface, exports are safer, and brand formatting has been centralized. Remaining issues are mostly structural/quality: a few cache keys still don’t include DB selection, and some UI utilities bypass `use_primary` in less‑used paths. These are smaller but still relevant to modular correctness.

## Verification of Round 3 Findings (Resolved)
1) **Manual campaign lookup ignores selected DB** — **Resolved.** `use_primary` is now read from session state and passed into `get_campaign_from_browser_by_id_sync`.
2) **Campaign header info ignores selected DB** — **Resolved.** `get_campaign_header_info_sync` now receives `use_primary`.
3) **Executive summary cached chart data ignores selected DB** — **Resolved.** `_get_exec_summary_chart_data` now accepts `use_primary` (part of cache key) and passes it through to all 3 queries.
4) **Campaign browser platform stats ignore selected DB** — **Resolved.** `get_platform_stats_sync` now receives `use_primary` from session state.

## New Findings

### 1) Campaign header loader still bypasses `use_primary` in one place
**File:** `src/ui/app.py`

- `get_campaign_header_info_sync(st.session_state.selected_campaign_id, use_primary=use_primary)` is fixed, but other header‑adjacent data paths (e.g., `selected_campaign_row` population in browse vs manual) still rely on env default for older archive/legacy paths.
- Impact: Lower risk in current mainline, but the UI can still drift if older codepaths are used (e.g., legacy exports).
- Recommendation: Consider aligning or clearly isolating legacy paths to avoid mixed DB assumptions.

### 2) Executive summary chart cache key does not include demographic (if added later)
**File:** `src/ui/tabs/executive_summary.py`

- The cache key now includes `use_primary`, but if demographics become configurable later, the cache key will need to include `demographic` to avoid reuse bugs.
- Impact: Not a current bug, but a likely future coupling issue.
- Recommendation: Document this in the function docstring or structure it to accept a `demographic` parameter for forward‑compatibility.

### 3) Legacy export path still ignores `use_primary`
**File:** `src/ui/archive/export_legacy.py`

- The archive export still uses older `use_ms01`/defaults and doesn’t follow `use_primary` threading.
- Impact: Only affects legacy/export paths, but violates modular consistency and reusability if that code is used.
- Recommendation: Either update legacy exports to the new pattern or clearly mark them as deprecated.

## use_primary Consistency Across UI Layer
**Yes for all active UI components.** The main tabs and campaign browser now thread `use_primary` correctly. Remaining inconsistencies are limited to legacy/archive paths.

## Additional Code Quality Observations
- **Positive:** The `format_brands()` utility now absorbs parsing/truncation logic, reducing duplication and improving reuse.
- **Positive:** Export data gathering now logs failures, which makes degradation observable.
- **Minor:** Some cached loaders still accept `use_primary` but do not explicitly document it in their docstrings; not a bug but reduces clarity.

## Fix Quality Assessment
**Just right.** The recent changes are focused, consistent with existing patterns, and avoid over‑engineering.

## Notes
- I did not run tests. This review is based on code inspection only.
