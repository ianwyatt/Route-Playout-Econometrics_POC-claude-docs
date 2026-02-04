# Codex Re-Review Prompt

**Date**: 4 February 2026
**Context**: Follow-up to deep code review scored 6.4/10 (5 findings). All 5 findings have been fixed. Requesting a fresh review to validate fixes and identify any remaining issues.

---

## Prompt to Submit to Codex

```
You previously reviewed this codebase and scored it 6.4/10, identifying 5 findings:

1. Cached frame-audience loaders in detailed_analysis.py ignore DB selection (use_primary not threaded)
2. Time series tab ignores DB selection (use_primary not passed to queries)
3. Export data gathering mixes DB sources (use_primary not passed to 5 of 9 queries)
4. Export data gathering swallows exceptions (9 bare except:pass blocks)
5. Brand formatting duplicated in app.py and manual_input.py instead of reusing format_brands()

All 5 have been fixed. Please review the following files to verify the fixes and perform a fresh deep review focused on reusability, modularity, and code quality. Score the codebase again on the same 1-10 scale.

## Files to review (changed files):

### src/ui/tabs/detailed_analysis.py
- Finding 1 fix: Added `use_primary: bool = None` to all 6 cached loaders (_load_frame_daily_data, _load_frame_hourly_data, _load_frame_campaign_data, _get_daily_count, _get_hourly_count, _get_campaign_count). Session state read at top of render function. Passed through to all 3 render sub-functions and 9 call sites. The use_primary parameter becomes part of the @st.cache_data cache key automatically.

### src/ui/tabs/time_series.py
- Finding 2 fix: Added use_primary read from session state. Passed to get_available_demographics_for_campaign_sync, get_daily_impacts_sync, and get_hourly_impacts_sync.

### src/ui/utils/export/data.py
- Finding 3 fix: Added use_primary=use_primary to 5 previously missing query calls (geographic, regional, environment, frame daily, frame hourly).
- Finding 4 fix: Added import logging + logger. Replaced all 9 bare `except Exception: pass` with `logger.warning("Failed to gather %s for campaign %s: %s", dataset_name, campaign_id, e)`. Graceful degradation preserved.

### src/utils/formatters.py
- Finding 5 fix: Extended format_brands() with two optional parameters:
  - `parse_string: bool = False` — accepts string input, parses PostgreSQL array format via ast.literal_eval with fallback
  - `max_display: Optional[int] = None` — truncates to first N brands with "+M more" suffix
  - Fixed placeholder matching from exact string match to case-insensitive check ("not provided" in b.lower())

### src/ui/app.py
- Finding 5 fix: Replaced ~40 lines of inline brand parsing/sorting/anonymisation (lines 264-304) with single call: `format_brands(campaign_info["brand_names"], parse_string=True)`

### src/ui/components/campaign_browser/manual_input.py
- Finding 5 fix: Replaced ~18 lines of inline brand formatting (lines 55-73) with single call: `format_brands(campaign_data.get("brand_names", []), max_display=3)`. Removed unused anonymise_brand and is_demo_mode imports.

## Additional context for review:

### Files NOT changed but worth reviewing for consistency:
- src/ui/tabs/overview.py — does it thread use_primary correctly?
- src/ui/tabs/geographic.py — does it thread use_primary correctly?
- src/ui/tabs/reach_grp.py — this was the reference implementation for the pattern
- src/ui/components/campaign_browser/browse_tab.py — uses format_brands correctly (confirmed)

### Architecture notes:
- This is a Streamlit app (cache-only, no live API calls)
- Database selection is stored in st.session_state["use_primary_database"]
- All query functions in src/db/queries/ accept `use_primary: bool = None`
- The pattern from reach_grp.py (line 31) was replicated: `use_primary = st.session_state.get("use_primary_database", True)`

### Test results after fixes:
- 66/66 unit tests pass (including all TestFormatBrands tests)
- 21/21 validator tests pass
- 22/24 DB-dependent tests pass (2 pre-existing failures unrelated to changes)

Please provide:
1. Updated score (same 1-10 scale)
2. Verification that all 5 original findings are resolved
3. Any new findings or remaining issues
4. Assessment of the fix quality (over-engineering? under-engineering? just right?)
```

---

## How to Use This Prompt

1. Open ChatGPT with the Codex agent
2. Attach or provide the 6 changed files listed above
3. Optionally attach the additional files for consistency review
4. Paste the prompt above
5. Save the response alongside the original review in `code reviews/`

---

*Created: 4 February 2026*
