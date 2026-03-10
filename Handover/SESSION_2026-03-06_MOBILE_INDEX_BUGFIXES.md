# Session Handover: Mobile Volume Index Bug Fixes

**Date:** 6 March 2026
**Session Focus:** Fix bugs found during browser testing of mobile index overlay across all 6 tabs

---

## What Was Done

### Bugs Fixed (all on branch `feature/mobile-volume-index`)

| Bug | Tab | Root Cause | Fix |
|-----|-----|------------|-----|
| GROUP BY alias error in cache build | `import_mobile_index.py` | `day_of_week` and `hour` aliases used in GROUP BY instead of full expressions | Replaced with `EXTRACT(DOW FROM ...)::int` and `EXTRACT(HOUR FROM ...)::int` |
| 1.6 TB WAL disk explosion | `import_mobile_index.py` | Bulk inserts (52M rows) without checkpoints | Added `CHECKPOINT` after each cache table build |
| Coverage query 3+ hours | `import_mobile_index.py` | LEFT JOIN + COUNT DISTINCT against 44 GB table | Replaced with fast query against `cache_mi_frame_totals` |
| Weekly tab empty indexed values | `reach_grp.py` | Matching by sequential `week_number` vs ISO `iso_week` | Changed to date range overlap matching with 1-day tolerance |
| Weekly tab tiny values (0, 34, 35) | `reach_grp.py` | Cache stores values in 000s, code divided by 1000 again | Removed `/1000` |
| Weekly tab missing Week 5 | `reach_grp.py` | Reach weeks start Sunday, ISO weeks start Monday | 1-day tolerance in date overlap matching |
| Weekly chart colour clash | `reach_grp.py` | Orange indexed bars identical to orange GRP bars | Changed indexed to green `#27AE60` |
| Frame Campaign tiny values (2.103 vs 2,005) | `detailed_analysis.py` | `/1000` double-division | Removed `/1000` |
| Frame Daily tiny values (0.006 vs 4.465) | `detailed_analysis.py` | `/1000` double-division | Removed `/1000` |
| Frame Hourly all zeros | `detailed_analysis.py` | `/1000` double-division (values became sub-0.001) | Removed `/1000` |

### Commit

```
79629ee fix: mobile index cache tables, GROUP BY bugs, /1000 double-division across all tabs
```

10 files changed, 941 insertions(+), 205 deletions(-)

---

## Current State

- Branch: `feature/mobile-volume-index` — 9 commits ahead of main
- All 6 tabs tested and working with mobile index enabled
- Cache tables populated and functional
- No uncommitted changes in source code

### Key Lesson: Cache Values Are Already in 000s

The `cache_route_impacts_15min_by_demo` source table stores impacts in 000s. The cache tables (`cache_mi_*`) aggregate these values with `SUM()`, preserving the 000s unit. The UI display code must NOT divide by 1000 again — just format and display directly.

### Key Lesson: PostgreSQL WAL Management

Bulk inserts generate massive WAL files. The `cache_mi_frame_hourly` table (52M rows) generated ~1.6 TB of temporary WAL. Always run `CHECKPOINT` between large table builds. This is now documented in `.claude/CLAUDE.md`.

---

## What's Next

1. **Load real analyst CSV data** when available:
   ```bash
   uv run python scripts/import_mobile_index.py /path/to/analyst_data.csv
   ```
2. **Run full test suite** before merge: `uv run pytest tests/ -v`
3. **Review and merge** `feature/mobile-volume-index` to `main`
4. **DigitalOcean deployment** — next priority after merge

---

## Key Files

| File | Purpose |
|------|---------|
| `scripts/import_mobile_index.py` | CSV import + cache table build (7 tables with CHECKPOINT) |
| `src/db/queries/mobile_index.py` | 8 query functions reading from cache tables |
| `src/ui/tabs/reach_grp.py` | Weekly table + chart with date overlap matching |
| `src/ui/tabs/detailed_analysis.py` | 3 frame sub-tabs with indexed columns (no /1000) |
| `Claude/docs/Documentation/MOBILE_VOLUME_INDEX.md` | Full documentation |

---

*Last Updated: 6 March 2026*
