# Codex Re-Review Prompt — Round 3

**Date**: 4 February 2026
**Context**: Second follow-up. Original score 6.4/10 (5 findings). First re-review scored 7.0/10 (all 5 fixed, 2 new findings). Both new findings now fixed. Requesting final review.

---

## Prompt to Submit to Codex

```
You have now reviewed this codebase twice:

- Round 1 (score 6.4/10): 5 findings — all fixed
- Round 2 (score 7.0/10): 2 new findings — both now fixed

The two Round 2 findings were:

1. Geographic tab ignores selected DB — `geographic.py` called 4 query functions without `use_primary`
2. Overview tab `_render_campaign_shape()` called `get_daily_impacts_sync` without `use_primary`

Both are now fixed. Please review the two changed files below, then perform a fresh deep review of the full codebase focused on reusability, modularity, and code quality. Score on the same 1-10 scale.

## Files changed since Round 2:

### src/ui/tabs/geographic.py
- Added `use_primary = st.session_state.get("use_primary_database", True)` after campaign_id read
- Passed `use_primary=use_primary` to `get_frame_geographic_data_sync()`, `get_regional_impacts_sync()`, `get_environment_impacts_sync()`
- Updated cached `_get_available_demographics()` to accept `use_primary: bool = None` parameter (adds it to cache key) and pass it to `get_available_demographics_for_campaign_sync()`

### src/ui/tabs/overview.py
- Added `use_primary = st.session_state.get("use_primary_database", True)` in `_render_mv_path()` before calling `_render_campaign_shape()`
- Updated `_render_campaign_shape()` signature to accept `use_primary: bool = True`
- Passed `use_primary=use_primary` to `get_daily_impacts_sync()`

## Full list of files changed across all 3 rounds (for context):

| File | What changed |
|------|-------------|
| `src/ui/tabs/detailed_analysis.py` | use_primary threaded through 6 cached loaders + 3 render functions |
| `src/ui/tabs/time_series.py` | use_primary threaded through 3 query calls |
| `src/ui/tabs/geographic.py` | use_primary threaded through 4 query calls + cached demographics |
| `src/ui/tabs/overview.py` | use_primary threaded through _render_campaign_shape |
| `src/ui/utils/export/data.py` | use_primary threaded through 5 calls + logging added to 9 exception handlers |
| `src/utils/formatters.py` | format_brands() extended with parse_string and max_display params |
| `src/ui/app.py` | ~40 lines inline brand logic replaced with format_brands() call |
| `src/ui/components/campaign_browser/manual_input.py` | ~18 lines inline brand logic replaced with format_brands() call |

## Architecture notes:
- Streamlit app, cache-only (no live API calls)
- Database selection stored in `st.session_state["use_primary_database"]`
- All query functions in `src/db/queries/` accept `use_primary: bool = None`
- The pattern `use_primary = st.session_state.get("use_primary_database", True)` is now consistent across all tabs

## Tabs that already had correct use_primary threading before these fixes:
- `src/ui/tabs/reach_grp.py` — original reference implementation
- `src/ui/components/campaign_browser/browse_tab.py` — correct throughout

## Test results:
- 66/66 unit tests pass
- 21/21 validator tests pass
- All module imports clean

## Please provide:
1. Updated score (same 1-10 scale)
2. Verification that both Round 2 findings are resolved
3. Any new findings or remaining issues
4. Whether use_primary is now consistently threaded across the entire UI layer

## Output instructions:
Save your review as: `code reviews/Codex_code-review-2026-02-04-round3.md`
in the docs repo at: `~/PycharmProjects/Route-Playout-Econometrics_POC-claude-docs/`
```

---

*Created: 4 February 2026*
