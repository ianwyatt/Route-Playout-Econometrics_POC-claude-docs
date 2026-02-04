# Code Review – Round 5 Deep Rescan (Active Codebase)

Date: 2026-02-04

## Overall Score
**7.6 / 10**

**Rationale:** The UI layer now threads `use_primary` consistently through active data paths, exports are more robust, and brand formatting is centralized. Remaining issues are minor and mostly about reducing env‑coupling in export helpers and improving structural clarity.

## Round 4 Findings – Resolution Check
All four Round 4 findings are resolved in active code:
1) **Manual campaign lookup ignores selected DB** — fixed.
2) **Campaign header info ignores selected DB** — fixed.
3) **Executive summary cached chart data ignores selected DB** — fixed (cache key now includes `use_primary`).
4) **Platform stats ignore selected DB** — fixed.

## New Findings (Active Codebase Only)

### 1) Export dialog doesn’t pass `use_primary`
**File:** `src/ui/utils/export_dialog.py`

- `create_excel_export()` is called without `use_primary`, so it falls back to env defaults.
- Impact: If environment and session diverge, exports could come from the wrong DB. This is a reusability/modularity issue because it relies on implicit state.
- Fix: Read `use_primary = st.session_state.get("use_primary_database", True)` and pass it into `create_excel_export`.

## use_primary Coverage Across UI Layer
**Yes, for active UI query paths.** All tabs/components thread `use_primary` correctly. The only remaining gap is the export dialog’s reliance on env defaults (not a direct query, but still a data path).

## Other Code Quality Observations (Non‑use_primary)
- **Positive:** Centralized `format_brands()` usage reduces duplication and makes anonymization consistent.
- **Positive:** Export data gathering now logs failures, improving observability.
- **Minor:** Inline HTML/CSS blocks in `app.py` could be moved to shared style helpers for better modularity, but this is cosmetic.

## Notes
- I did not run tests. This review is based on code inspection only.

---

## Resolution Status (added post-review)

| Finding | Status | Details |
|---------|--------|---------|
| 1) Export dialog doesn't pass `use_primary` | **RESOLVED** | `use_primary` threaded from session state into `create_excel_export()` call |

Round 6 review prompt submitted.
