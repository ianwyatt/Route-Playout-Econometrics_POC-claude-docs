# Codex Re-Review Prompt — Round 5 (Final)

**Date**: 4 February 2026
**Context**: Fourth follow-up. Score progression: 6.4 → 7.0 → 7.2 → 7.4. All actionable findings fixed. This round challenges the Round 4 findings and requests a final assessment.

---

## Prompt to Submit to Codex

```
You have now reviewed this codebase four times:

- Round 1 (score 6.4/10): 5 findings — all fixed
- Round 2 (score 7.0/10): 2 new findings — both fixed
- Round 3 (score 7.2/10): 4 new findings — all fixed
- Round 4 (score 7.4/10): 3 new findings — see response below

No code changes were made for Round 4 because we believe all 3 findings are non-actionable. Here is our reasoning:

### Round 4 Finding 1: "Campaign header loader still bypasses use_primary in one place"
**Our response: Not reproducible.** You mentioned "older archive/legacy paths" and "selected_campaign_row population in browse vs manual" but did not cite a specific file or line number. In the active codebase:
- `selected_campaign_row` is populated by `browse_tab.py` (already had correct `use_primary` threading before any of our fixes — you confirmed this yourself in Round 3)
- `selected_campaign_row` is also populated by `manual_input.py` (now passes `use_primary` to `get_campaign_from_browser_by_id_sync()` — fixed in Round 3)
- There is no other active code path that populates `selected_campaign_row`

If you can identify a specific file and line number where this is still an issue, please do so. Otherwise this finding should be closed.

### Round 4 Finding 2: "Executive summary cache key does not include demographic (if added later)"
**Our response: Acknowledged as not a bug.** You explicitly stated "Not a current bug, but a likely future coupling issue." The executive summary hardcodes `"all_adults"` — there is no demographic selector on that tab. We don't add forward-compatibility parameters for features that don't exist. If demographics become configurable on that tab in future, the cache key will be updated at that time.

### Round 4 Finding 3: "Legacy export path still ignores use_primary"
**Our response: Archive/dead code.** The file `src/ui/archive/export_legacy.py` is in the `archive/` directory, which contains a README explicitly stating: "This file is retained for reference only. Do not use for new development." Nothing in the active codebase imports from `src/ui/archive/`. Updating dead archived code would be unnecessary churn.

## What we're asking for:

1. Do you accept our reasoning on the 3 Round 4 findings? If not, cite specific file paths and line numbers for any you believe are still genuine issues.

2. Please perform one final fresh deep review of the **active** codebase (excluding `src/ui/archive/`) focused on:
   - Reusability, modularity, and code quality
   - Any remaining `use_primary` gaps in active code
   - Any other code quality issues you haven't previously flagged

3. Provide a final score on the same 1-10 scale.

## Architecture notes (unchanged):
- Streamlit app, cache-only (no live API calls)
- Database selection stored in `st.session_state["use_primary_database"]`
- All query functions in `src/db/queries/` accept `use_primary: bool = None`
- The pattern `use_primary = st.session_state.get("use_primary_database", True)` is now consistent across all active tabs and components

## Tabs/components with confirmed correct use_primary threading:
- `src/ui/tabs/reach_grp.py` — original reference implementation
- `src/ui/tabs/detailed_analysis.py` — 6 cached loaders + 3 render functions (Round 1)
- `src/ui/tabs/time_series.py` — 3 query calls (Round 1)
- `src/ui/tabs/geographic.py` — 4 query calls + cached demographics (Round 2)
- `src/ui/tabs/overview.py` — campaign shape renderer (Round 2)
- `src/ui/tabs/executive_summary.py` — cached chart data + 3 query calls (Round 3)
- `src/ui/utils/export/data.py` — 5 query calls (Round 1)
- `src/ui/app.py` — header info, brand formatting, all cached loaders (Rounds 1 + 3)
- `src/ui/components/campaign_browser/browse_tab.py` — correct throughout (pre-existing)
- `src/ui/components/campaign_browser/manual_input.py` — campaign lookup (Round 3)
- `src/ui/components/campaign_browser/summary.py` — platform stats (Round 3)

## Test results:
- 66/66 unit tests pass
- 21/21 validator tests pass
- All module imports clean

## Output instructions:
Save your review as: `code reviews/Codex_code-review-2026-02-04-round5.md`
in the docs repo at: `~/PycharmProjects/Route-Playout-Econometrics_POC-claude-docs/`
```

---

*Created: 4 February 2026*
