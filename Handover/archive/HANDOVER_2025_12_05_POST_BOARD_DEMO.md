# Handover: Post Board Demo Session
**Date**: 2025-12-05
**Session Focus**: Documentation review, app functionality understanding, email drafting

---

## ⚠️ NEXT SESSION: POST-DEMO CLEANUP REQUIRED

**Priority Task**: Execute the post-demo cleanup plan

**Document**: `Claude/ToDo/post_demo_cleanup_plan.md`

### What Needs Doing:

1. **Archive app_demo.py**
   - Move `src/ui/app_demo.py` → `src/ui/archive/app_demo.py`
   - Create archive README explaining why
   - Update CLAUDE.md to remove references

2. **Root Directory Cleanup**
   - `git rm PHASE_7_TEST_RESULTS.md PHASE_7_TEST_SUMMARY.txt`
   - `git mv run_migration_003.py scripts/run_migration_003.py`
   - Delete local test files: `route_response_*.json`, `test_demographics_*.log`, `PHASE6_*.md`

3. **Optional: Remove Reference Folders**
   - `Example_Python_Project_with_ Route_API_Access/`
   - `Route releases for Playout Audiences/`
   - `Talon Econometrics References/`

### Quick Execution (Copy-Paste Ready):
```bash
# Archive app_demo.py
mkdir -p src/ui/archive
mv src/ui/app_demo.py src/ui/archive/app_demo.py

# Remove phase docs from git
git rm PHASE_7_TEST_RESULTS.md PHASE_7_TEST_SUMMARY.txt

# Move migration script
git mv run_migration_003.py scripts/run_migration_003.py

# Delete local test files
rm -f route_response_*.json test_demographics_*.log PHASE6_*.md
```

See full plan with rollback instructions: `Claude/ToDo/post_demo_cleanup_plan.md`

---

## Summary

This session focused on reviewing the app's full functionality in detail and preparing communication materials. The board demo (December 4th) has been completed. All infrastructure and failover systems were verified working in the previous session.

---

## Project Status

### Board Demo: COMPLETE ✅
- Demo delivered December 4th, 2025 (morning)
- All infrastructure tested and verified
- Failover systems ready (M1 Max + Framework database)

### Current State
The POC is fully functional with:
- 836 campaigns available for analysis
- 1.2 billion playout records matched to Route audiences
- 7 demographic segments per playout
- Full UI with 6 analysis tabs
- Excel/CSV export functionality

---

## Application Architecture

### UI Tabs (in order)

| Tab | File | Purpose |
|-----|------|---------|
| **Overview** | `src/ui/tabs/overview.py` | Campaign summary, audience metrics, delivery stats, campaign shape chart |
| **Weekly Reach** | `src/ui/tabs/reach_grp.py` | Weekly performance table, reach/impacts/GRP charts, cumulative build curves |
| **Daily & Hourly** | `src/ui/tabs/time_series.py` | Time-based analysis with demographic filter, peak metrics, heatmaps |
| **Geographic** | `src/ui/tabs/geographic.py` | Regional analysis, UK map, TV regions, towns, environment breakdown |
| **Frame Audiences** | `src/ui/tabs/detailed_analysis.py` | Frame-level data at campaign/daily/hourly granularity, CSV downloads |
| **Executive Summary** | `src/ui/tabs/executive_summary.py` | One-page overview, key metrics, Excel export |

### Key Features by Tab

**Overview**
- 5 audience metrics: Impacts, GRP, Reach, Cover, Frequency
- 4 delivery metrics: Playouts, Frames, Impacts/Frame, Impacts/Playout
- Campaign Shape chart showing daily delivery pattern

**Weekly Reach, Impacts & GRPs**
- Individual week performance table
- Weekly comparison bar charts (Reach/Impacts, GRP)
- **Cumulative Build chart** - daily granularity showing reach/impacts accumulation
- All Adults 15+ only (demographic filtering is future enhancement)

**Daily & Hourly Patterns**
- **Demographic selector** - filters all charts for selected demographic
- Campaign averages (daily, weekly)
- Peak performance metrics (peak hour, peak day)
- Daily impacts line + bar charts
- Day of week comparison
- Hourly analysis bar chart
- **Heatmap** - day × hour matrix

**Geographic**
- **Demographic selector** - filters all views
- Summary metrics: frames, impacts, TV regions, towns
- Regional impact distribution (bar chart)
- Environment distribution (pie chart)
- Interactive UK map with frame markers
- TV regions table with % of total
- Towns table with frame counts

**Frame Audiences** (The MMM Export Tab)
- **Frame Campaign Audiences** - total per frame, all 7 demographics
- **Frame Daily Audiences** - frame × day, all 7 demographics
- **Frame Hourly Audiences** - frame × hour, all 7 demographics
- Pagination (2000 row default, "Load All" button)
- CSV download for each view

**Executive Summary**
- Media Metrics card: GRP, Reach, Cover, Frequency
- Delivery table, Peak Performance table
- Reach & Impact Build chart
- Daily Impacts, Day of Week, Regional breakdown
- **One-click Excel export** - multi-sheet workbook

### Demographics Available
1. All Adults (15+)
2. ABC1
3. C2DE
4. Age 15-34
5. Age 35+
6. Main Shopper
7. Households with Children

---

## Database Infrastructure

| Database | Host | Purpose |
|----------|------|---------|
| **Local (M4 Max)** | localhost | Primary for demo |
| **MS-01** | 192.168.1.34 | Production server |
| **Framework** | 192.168.1.76 | Failover backup |

All three databases contain:
- `route_poc` database
- All materialized views including `mv_frame_brand_daily`, `mv_frame_brand_hourly`
- 836 campaigns in `mv_campaign_browser`

### Key Materialized Views
- `mv_campaign_browser` - Campaign list with summary metrics
- `mv_cache_campaign_impacts_frame` - Frame-level impacts by demographic
- `mv_frame_audience_daily` - Denormalised frame × day data
- `mv_frame_audience_hourly` - Denormalised frame × hour data
- `mv_frame_brand_daily` - Frame × day with brand info
- `mv_frame_brand_hourly` - Frame × hour with brand info

---

## Commands Reference

```bash
# Start app (various configurations)
startstream              # MS-01 database, normal mode
startstream demo         # MS-01 database, demo mode (brands anonymised)
startstream local        # Local database, normal mode
startstream local demo   # Local database, demo mode

# Stop Streamlit
stopstream

# Wake Framework for failover
wakeonlan 9c:bf:0d:00:f8:e3

# Health check
curl http://localhost:8504/_stcore/health

# Database connection test
psql -h <host> -U postgres -d route_poc -c "SELECT COUNT(*) FROM mv_campaign_browser;"
```

---

## Key Files Reference

### Documentation
| File | Purpose |
|------|---------|
| `docs/ARCHITECTURE.md` | Technical architecture overview |
| `docs/UI_GUIDE.md` | UI component documentation |
| `docs/Board_Presentation/PRESENTATION_AND_DEMO_SCRIPT.md` | Demo talking points |
| `docs/Board_Presentation/PREP_SCHEDULE.md` | Demo timeline & quick reference |
| `docs/Board_Presentation/FAILOVER_TEST_CHECKLIST.md` | Failover testing procedure |

### Configuration
| File | Purpose |
|------|---------|
| `.env` | Database credentials, API keys (gitignored) |
| `src/ui/config/demographics.py` | Demographic display names and sort order |
| `src/ui/config/anonymisation.py` | Brand anonymisation for demo mode |

### Data Layer
| File | Purpose |
|------|---------|
| `src/db/streamlit_queries.py` | All database query functions |
| `src/ui/utils/export.py` | Excel/CSV export logic |

---

## Pending Tasks

### ⚠️ IMMEDIATE: Post-Demo Cleanup
**Full instructions**: `Claude/ToDo/post_demo_cleanup_plan.md`

| Task | Status | Notes |
|------|--------|-------|
| Archive `app_demo.py` | ❌ Pending | Move to `src/ui/archive/` |
| Remove PHASE_7 docs | ❌ Pending | `git rm` tracked files |
| Move migration script | ❌ Pending | `git mv` to `scripts/` |
| Delete local test files | ❌ Pending | JSON, log, PHASE6 md files |
| Update CLAUDE.md | ❌ Pending | Remove app_demo.py references |
| Remove reference folders | ❓ Optional | External project references |

### Future Enhancements (Not Urgent)
- Demographic filtering for Weekly Reach/GRP tab (requires Route API backfill)
- Classic frame support (static/scroller)
- Natural language query interface
- Cost and financial tracking

---

## Session History

### Previous Sessions
- **2025-12-01**: Framework database setup, failover testing, database selection bug fixes
- **2025-11-30**: Demo script creation, backup campaign selection, documentation

### This Session (2025-12-05)
- Reviewed full app functionality in detail
- Read all tab implementation files to understand features
- Prepared email summary for econometrician outreach
- Created this handover document

---

## Git Status

Branch: `main`

Recent commits:
- `ac3025f` - style: polish Enter Campaign ID tab UI and fix brand anonymisation
- `079e0f8` - feat: add Route company logo to header and analysis page
- `e253705` - refactor: make primary button styling global for consistency

No uncommitted changes at session start (only `docs/UI_GUIDE.md` modified).

---

**Author**: Claude Code
**Created**: 2025-12-05
