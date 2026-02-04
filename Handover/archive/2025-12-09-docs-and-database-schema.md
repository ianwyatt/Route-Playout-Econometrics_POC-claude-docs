# Handover: Documentation Cleanup & Database Schema

**Date:** 9 December 2025
**Branch:** `refactor/modularity-cleanup`
**Status:** Ready to commit and merge to main

---

## Session Summary

This session completed two major tasks:

1. **Documentation Cleanup** - Restructured `/docs` with numbered prefixes, moved historical docs to Claude folder, archived redundant files
2. **Database Schema Documentation** - Created comprehensive database reference for the UI (`docs/11-database-schema.md`)
3. **Pipeline Handover** - Created request for frame_details table consolidation

---

## Commits This Session

### Commit: `fe5e021`
**docs: restructure with numbered prefixes and cleanup**
- Renamed 10 docs with numbered prefixes (1-10)
- Moved Board_Presentation/ to Claude/Documentation/
- Moved pipeline-handover/ to Claude/Handover/From_Pipeline_Team/
- Archived 3 historical docs
- Created docs/README.md index

### Pending (Uncommitted)
- `docs/11-database-schema.md` - New database reference
- `docs/README.md` - Updated to include schema doc
- `Claude/Handover/For_Pipeline_Team/Frame_Details_Consolidation_20251206.md` - Pipeline request

---

## Documentation Restructure

### New /docs Structure

```
docs/
├── README.md                    # NEW - Index file
├── 1-architecture.md            # Was ARCHITECTURE.md
├── 2-ui-guide.md               # Was UI_GUIDE.md
├── 3-demo-mode.md              # Was DEMO_MODE_ANONYMISATION.md
├── 4-cache-integration.md      # Was CACHE_INTEGRATION.md
├── 5-cache-troubleshooting.md  # Was CACHE_TROUBLESHOOTING.md
├── 6-campaign-indicators.md    # Was CAMPAIGN_INDICATORS_LOGIC.md
├── 7-weekly-averages.md        # Was WEEKLY_AVERAGE_CALCULATIONS.md
├── 8-geographic-visualization.md # Was GEOGRAPHIC_VISUALIZATION_README.md
├── 9-credentials.md            # Was CREDENTIAL_SYSTEM_GUIDE.md
├── 10-git-workflow.md          # Was GIT_WORKFLOW.md
├── 11-database-schema.md       # NEW - Database reference
├── api-reference/              # Unchanged
│   ├── route/
│   ├── space/
│   └── pipeline/
└── playout/                    # Unchanged
```

### Files Moved to Claude Docs

| From | To |
|------|-----|
| `docs/pipeline-handover/` (13 files) | `Claude/Handover/From_Pipeline_Team/` |
| `docs/Board_Presentation/` (6 files) | `Claude/Documentation/Board_Presentation/` |

### Files Archived

Moved to `Claude/Documentation/Archive/`:
- `CONFIGURATION_CENTRALIZATION_SUMMARY.md` - Historical summary
- `PHASE_7_QUICK_REFERENCE.md` - Historical phase docs
- `GIT_QUICK_REFERENCE.md` - Redundant with git-workflow

### Files Removed

- `docs/references/` - Empty directory
- `docs/ROUTE_API_Mixed_Spot&Break_Schedules/` - Content moved to `api-reference/route/`

---

## Database Schema Documentation

### New File: `docs/11-database-schema.md`

Comprehensive database reference covering:

**Campaign Browser Views:**
- `mv_campaign_browser` - Pre-aggregated campaign list
- `mv_campaign_browser_summary` - Header statistics

**Audience Impact Cache:**
- `cache_route_impacts_15min_by_demo` - 15-min impacts by demographic
- 5 aggregated views (15min, 1hr, daypart, day, week)

**Campaign Reach Cache:**
- `cache_campaign_reach_day` - Daily reach
- `cache_campaign_reach_week` - Weekly reach (individual + cumulative)
- `cache_campaign_reach_full` - Full campaign totals
- `cache_campaign_reach_day_cumulative` - Cumulative build

**Frame Data:**
- `route_frames` - Core frame data + coordinates
- `route_frame_details` - Extended metadata
- `route_releases` - Release tracking

**Entity Lookups:**
- `cache_space_brands`, `cache_space_media_owners`, `cache_space_buyers`, `cache_space_agencies`

**Supporting Tables:**
- `campaign_cache_limitations` - Uncacheable campaign tracking
- `cache_demographic_universes` - Population bases for GRP

**Playout Aggregation:**
- `mv_playout_15min` - Source aggregation
- `mv_playout_frame_day` - Daily frame playouts
- `mv_playout_frame_hour` - Hourly frame playouts

---

## Pipeline Team Request

### Frame Details Consolidation

Created `Claude/Handover/For_Pipeline_Team/Frame_Details_Consolidation_20251206.md`

**Issue:** `route_frames` and `route_frame_details` are always joined together. The only unique data in `route_frames` is latitude/longitude.

**Request:** Add lat/lon columns to `route_frame_details`, then POC will update queries to use single table.

**Migration Steps:**
1. `ALTER TABLE route_frame_details ADD COLUMN latitude, longitude`
2. `UPDATE route_frame_details SET lat/lon FROM route_frames`
3. Add coordinate index
4. Notify POC team
5. (Future) Drop redundant `route_frames` table

**Priority:** Medium - technical debt cleanup, no urgency

---

## Branch Status

### Commits on `refactor/modularity-cleanup`

| Hash | Description |
|------|-------------|
| `fe5e021` | docs: restructure with numbered prefixes and cleanup |
| `0bb4922` | docs: update ARCHITECTURE.md for modularity refactor |
| `089a7be` | refactor: modularise large files and archive dead code |
| `e69e8c2` | refactor: consolidate config systems into single config.py |
| `8d6e0d2` | refactor: modularity cleanup and code deduplication |

### Uncommitted Changes

```
docs/11-database-schema.md      # New database reference
docs/README.md                  # Updated index
```

Note: Claude/ folder changes are gitignored (local working docs).

---

## Next Steps

### Immediate
1. **Commit** the database schema doc and README update
2. **Push** to branch
3. **Merge** to main when ready

### Commit Command
```bash
git add docs/11-database-schema.md docs/README.md
git commit -m "docs: add database schema reference

- Create docs/11-database-schema.md with comprehensive DB reference
- Document all tables, views, and relationships used by UI
- Update docs/README.md index to include new doc

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
Co-Authored-By: ian@route.org.uk"
```

### Merge to Main
```bash
git checkout main
git merge refactor/modularity-cleanup
git push origin main
git push zimacube main
```

---

## Related Files

### Created This Session
- `docs/11-database-schema.md` - Database reference
- `docs/README.md` - Docs index
- `Claude/Handover/For_Pipeline_Team/Frame_Details_Consolidation_20251206.md` - Pipeline request

### Modified This Session
- `docs/README.md` - Added schema doc to index

### From Previous Session (Modularity Refactor)
- `src/config.py` - Added DatabaseConfig, get_database_config()
- `src/db/queries/` - New package (8 modules)
- `src/ui/components/campaign_browser/` - New package (8 modules)
- `src/ui/utils/export/` - New package (5 modules)
- `src/archive/` - Dead code archived

---

## Quick Reference

### Running the App
```bash
startstream        # MS-01 database
startstream demo   # Demo mode (brands anonymised)
startstream local  # Local database
```

### Key Documentation
- Architecture: `docs/1-architecture.md`
- UI Guide: `docs/2-ui-guide.md`
- Database Schema: `docs/11-database-schema.md`
- Cache System: `docs/4-cache-integration.md`

### Pipeline Requests Pending
- Frame details consolidation (medium priority)

---

**Session completed by:** Claude (Opus 4.5)
**Reviewed by:** Doctor Biz
