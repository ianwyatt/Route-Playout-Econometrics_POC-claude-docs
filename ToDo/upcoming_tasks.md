# Upcoming Tasks

## Completed: Codex Code Review Fixes (6 Rounds)

All 12 actionable findings addressed across 6 rounds. Score progression: 6.4 → 7.8/10. Two commits pushed:
1. `fix: thread use_primary consistently across entire UI, add export logging, consolidate brand formatting`
2. `refactor: remove unused imports, dead code, and redundant comments`

---

## Completed: Documentation Archival

- 50+ pre-2026 handover files archived to `handover/archive/`
- 11 completed todo files archived to `todo/archive/`
- 12 outdated docs archived to `docs/Documentation/Archive/`
- Adwanted sharing guide created at `docs/SHARING_GUIDE_ADWANTED.md`

---

## Pending: Manual Verification

1. `startstream local` → select campaign → verify all tabs show local DB data
2. Export from any campaign → check logs for warnings (should be clean on happy path)

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

## Future: Share with Adwanted

See `docs/SHARING_GUIDE_ADWANTED.md` for full instructions on:
- Adding Adwanted as GitHub collaborator
- Database export/restore options
- Environment setup and running the app

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
