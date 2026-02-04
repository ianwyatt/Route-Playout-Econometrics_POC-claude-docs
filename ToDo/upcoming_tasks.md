# Upcoming Tasks

## Immediate: Commit and Push All Codex Review Fixes

**Status**: All code changes complete (12 findings across 5 rounds), awaiting Doctor Biz approval to commit

**Score progression**: 6.4 → 7.0 → 7.2 → 7.4 → 7.6 → TBD (Round 6 pending)

**Proposed Commit** (code repo — GitHub + Gitea):
```
fix: thread use_primary consistently across entire UI, add export logging, consolidate brand formatting
```

**Manual verification needed**:
1. `startstream local` → select campaign → verify all tabs show local DB data
2. Export from any campaign → check logs for warnings (should be clean on happy path)

---

## Immediate: Codex Round 6 Review

**Status**: Prompt prepared in `code reviews/Codex_re-review_prompt_2026-02-04_round6.md`

Submit to ChatGPT Codex for final verification. All active code paths now thread `use_primary` consistently, including the export dialog (Round 5 fix).

---

## Pre-Existing Test Failures (Local DB)

Two test failures exist when running against local database — not introduced by recent changes:

1. `test_empty_demographic_segments_list` — returns all data instead of empty (test expectation issue)
2. `test_query_performance_under_100ms` — 214ms on local DB (performance threshold too tight for local)

These should be investigated and fixed separately.

---

## Future: Cumulative Build Enhancement (Pending)

**Branch**: To be created: `feature/cumulative-build-daily`

**Objective**: Replace weekly cumulative build charts with daily data for smoother, more realistic curves.

**Current State**:
- Weekly Reach tab and Exec Summary both show cumulative build charts
- Charts currently use weekly data points, creating straight-line segments between weeks
- Results in a stepped/angular appearance

**Desired State**:
- Use daily cumulative data from `cache_campaign_reach_day_cumulative` table
- Smoother curves that better represent the actual reach build over time

**Files Likely Affected**:
- `src/ui/tabs/executive_summary.py` - Reach & Impact Build chart
- `src/ui/tabs/weekly_reach.py` - Cumulative build chart
- `src/db/streamlit_queries.py` - May need new query for daily cumulative data

**Database Table**: `cache_campaign_reach_day_cumulative`

---

## Future Enhancements (from README)

- Cost and financial tracking (rate cards, CPM, cost per GRP)
- Natural language query interface
- AI-powered insights (OpenAI/Claude integration)
- Classic frame support (static/scroller)
- Multi-user support with role-based access
- Demographic filtering for Weekly Reach/GRP tab
- User authentication (Pocket ID - passkey-only OIDC)
- User areas with saved campaigns and history

---

*Last Updated: 4 February 2026*
