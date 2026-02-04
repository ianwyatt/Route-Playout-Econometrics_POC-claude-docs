# Upcoming Tasks

## Immediate: Complete Handover Cleanup (IN PROGRESS)

**Status**: Code changes complete, awaiting Doctor Biz to:

1. Update `~/.zshrc` `startstream` function (replace `USE_MS01_DATABASE` with `USE_PRIMARY_DATABASE`)
2. Test `startstream` and `startstream demo` work correctly
3. Approve and commit changes

**Proposed Commits** (code repo — GitHub + Gitea):
1. `refactor: remove Route API fallback code, make app cache-only`
2. `refactor: remove MS01 backwards-compatible aliases and env var fallbacks`
3. `chore: clean up debug tests and update README for handover`

**Proposed Commits** (docs repo — Gitea only):
1. `docs: archive API fallback code for future reference`
2. `docs: update CLAUDE.md and session handover for cleanup`

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
