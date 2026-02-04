# Documentation Audit Report

**Date**: 10 December 2025
**Purpose**: Identify outdated/redundant documentation and plan updates
**Status**: Planning only - NO CODE CHANGES before demo

---

## Executive Summary

The documentation is generally good but has several issues:
1. **startstream shell function** - exists in CLAUDE.md but not prominently in main docs
2. **Mock mode references** - still present, but we no longer use mock mode
3. **Campaign examples** - docs use 16932/18295/99999, should reference board demo campaigns
4. **Missing ASCII architecture diagram** - user requested this be added
5. **app_demo.py references** - deprecated app still referenced

---

## Issue 1: startstream Shell Function

### Current State
- CLAUDE.md has the full shell function ✅
- docs/01-architecture.md mentions `startstream` commands ✅
- docs/02-ui-guide.md mentions `startstream` commands ✅
- docs/03-demo-mode.md mentions `startstream` commands ✅

### Issue
- Docs reference `startstream` but don't explain it's a **custom zsh function the user must add to ~/.zshrc**
- New users would try to run `startstream` and get "command not found"

### Recommendation
Add a clear note in docs/01-architecture.md and docs/02-ui-guide.md:
```markdown
**Note**: `startstream` is a shell function you must add to `~/.zshrc`.
See the Quick Start section in `CLAUDE.md` for the function definition.
```

Or add the full function definition to the main docs.

---

## Issue 2: Mock Mode References (Outdated)

### Files with mock mode references:
| File | Lines | Issue |
|------|-------|-------|
| docs/01-architecture.md | 153, 246 | "Mock Data Generator", "mock mode" |
| docs/02-ui-guide.md | 229 | `mock_geo_data.py` |
| docs/04-cache-integration.md | 163, 402, 419, 421 | Mock mode checks |
| docs/05-cache-troubleshooting.md | 115 | "Use mock mode for testing" |
| docs/08-geographic-visualization.md | 121 | `mock_geo_data.py` |
| docs/09-credentials.md | 51, 91-127 | Mock mode activation, fallback |

### Current Reality
- We **no longer use mock mode** - all data is real
- `DEMO_MODE` anonymises brands but uses real data
- `app_demo.py` is deprecated

### Recommendation
1. Remove or update mock mode references
2. Clarify that `mock_geo_data.py` is for geographic visualisation only (not campaign data)
3. Update docs/09-credentials.md to remove mock fallback guidance

---

## Issue 3: Campaign Examples (Outdated)

### Current examples in docs:
| Campaign | Used In | Status |
|----------|---------|--------|
| 99999 | cache-integration, troubleshooting | Fake "not found" example |
| 16932 | troubleshooting, architecture | Old test campaign |
| 18295 | troubleshooting, architecture | Large campaign example |
| 12345 | API examples | Placeholder |

### Board Demo Campaigns (Current/Real):
| Campaign | Brand | Purpose |
|----------|-------|---------|
| **16699** | Brand 3 (demo) | Feature walkthrough, standard test |
| **16879** | - | Data quality issue demo |
| **16879 & 16882** | - | Overlap demonstration |
| **18409** | Waitrose | Backup campaign |
| **16860** | Specsavers | Backup campaign |

### Recommendation
Update examples in troubleshooting docs to use:
- 16699 for standard "this works" examples
- 99999 can stay as "not found" example
- Reference board demo script for real campaign examples

---

## Issue 4: Missing ASCII Architecture Diagram

### User Request
Add an ASCII representation of code flow at the start of main docs.

### Proposed Diagram (for docs/01-architecture.md):

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        PLAYOUT ANALYTICS                                 │
│                    Route Playout Econometrics POC                        │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                           USER INTERFACE                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────┐  │
│  │ Campaign Browser │  │ Analysis Tabs   │  │ Export (CSV/Excel)      │  │
│  │ (src/ui/        │  │ (src/ui/tabs/)  │  │ (src/ui/utils/export/)  │  │
│  │  components/)   │  │                 │  │                         │  │
│  └────────┬────────┘  └────────┬────────┘  └────────────┬────────────┘  │
└───────────┼─────────────────────┼──────────────────────┼────────────────┘
            │                     │                      │
            ▼                     ▼                      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          DATA LAYER                                      │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    PostgreSQL Cache (MS-01)                      │    │
│  │  ┌───────────────────┐  ┌───────────────────────────────────┐   │    │
│  │  │ mv_campaign_      │  │ cache_route_impacts_15min_by_demo │   │    │
│  │  │ browser           │  │ (252.7M records)                  │   │    │
│  │  └───────────────────┘  └───────────────────────────────────┘   │    │
│  │  ┌───────────────────┐  ┌───────────────────────────────────┐   │    │
│  │  │ mv_frame_audience │  │ cache_campaign_reach_full         │   │    │
│  │  │ _daily/_hourly    │  │ cache_campaign_reach_day          │   │    │
│  │  └───────────────────┘  └───────────────────────────────────┘   │    │
│  └─────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
            │
            │ Cache MISS (rare)
            ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        EXTERNAL APIS (Fallback)                          │
│  ┌─────────────────────────┐  ┌─────────────────────────────────────┐   │
│  │ Route API               │  │ SPACE API                           │   │
│  │ (Audience data)         │  │ (Frame metadata, brands)            │   │
│  │ route.mediatelapi.co.uk │  │ oohspace.co.uk/api                  │   │
│  └─────────────────────────┘  └─────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘

DATA FLOW:
───────────
1. User selects campaign in Browser
2. Query PostgreSQL cache (mv_campaign_browser)
3. Load analysis data from cache tables
4. Display in 6-tab layout
5. Export to CSV/Excel on demand

PERFORMANCE:
────────────
• Cache HIT:  <100ms (typical)
• Cache MISS: 30-60s (API fallback)
• 826 campaigns, 69 days cached
```

---

## Issue 5: app_demo.py References (Deprecated)

### Files referencing deprecated app:
| File | Line | Reference |
|------|------|-----------|
| docs/01-architecture.md | 26-29 | "Legacy Demo Application (app_demo.py) - DEPRECATED" |
| docs/01-architecture.md | 382 | `streamlit run src/ui/app_demo.py` |
| docs/02-ui-guide.md | 209 | `app_demo.py # Legacy demo app (deprecated)` |

### Status
- `app_demo.py` marked as deprecated ✅
- References note it's deprecated ✅
- But old command `streamlit run src/ui/app_demo.py` still shown

### Recommendation
Remove the deprecated run command from docs/01-architecture.md line 382.
Keep the "DEPRECATED" note for historical reference.

---

## Issue 6: Outdated Date References

### Files with old dates:
| File | Current Date | Issue |
|------|--------------|-------|
| CLAUDE.md | November 27, 2025 | Should be December 2025 |
| docs/03-demo-mode.md | November 28, 2025 | Could update |
| Claude/Documentation/Board_Presentation/* | Various Nov dates | Historical, OK to keep |

### Recommendation
Update CLAUDE.md date to December 2025 after any changes.

---

## Issue 7: Outdated Phase 7 Performance Numbers

### Current Claims in Docs
| File | Claim |
|------|-------|
| docs/01-architecture.md:346-350 | "Phase 7 Testing" - Campaign 16932: 1.7-3.6s, Campaign 18295: 29-58s |
| docs/04-cache-integration.md:83-85 | Small campaigns 1.7-3.6s, Large campaigns 29-58s |
| docs/04-cache-integration.md:697 | Large campaign 29s |

### Why This Is Outdated
These numbers are from **October 2025** (Phase 7) before we added:
- `mv_frame_audience_daily` (denormalised, 3.8ms query time)
- `mv_frame_audience_hourly` (denormalised, ~4ms query time)
- SQL LIMIT pagination (2000 rows initial load)
- Streamlit caching (@st.cache_data)

### Current Reality (December 2025)
With the denormalised MVs:
- **Campaign browser**: <100ms
- **Initial frame audiences load**: <100ms (2000 rows)
- **Full frame audiences**: <5s daily, <30s hourly
- **Tab switching**: Instant (cached)

### Files to Update
| File | Lines | Update Needed |
|------|-------|---------------|
| docs/01-architecture.md | 346-365 | Remove "Phase 7" label, update times |
| docs/04-cache-integration.md | 83-85, 607-697 | Update benchmark section |

### Suggested Updated Performance Table

```markdown
### Current Performance (December 2025)

| Operation | Response Time | Notes |
|-----------|---------------|-------|
| Campaign browser | <100ms | mv_campaign_browser |
| Campaign summary | <100ms | Cached in session |
| Frame Audiences (initial) | <100ms | 2000 row LIMIT |
| Frame Audiences (full daily) | <5s | mv_frame_audience_daily |
| Frame Audiences (full hourly) | <30s | mv_frame_audience_hourly |
| Tab switching | Instant | @st.cache_data |
| API fallback (rare) | 30-60s | Uncached campaigns only |
```

---

## Documentation Structure Issues

### Current Redundancy
- Claude/Documentation/ has 50+ files, many historical
- Board_Presentation/ has 5 files specific to Dec 4th demo
- Some overlap between docs/ and Claude/Documentation/

### Recommendation
1. Keep docs/ as the canonical documentation
2. Archive older Claude/Documentation/ files to Claude/Archive/
3. Board_Presentation/ can stay for reference but note demo has passed

---

## Files to Archive (Post-Demo)

| File/Folder | Reason |
|-------------|--------|
| Claude/Documentation/SESSION_SUMMARY_2025_09_10.md | 3 months old |
| Claude/Documentation/MS01_MIGRATION_*.md | Migration complete |
| Claude/Documentation/BOARD_DEMO_UI_MIGRATION_2025_10_20.md | Complete |
| Claude/Documentation/CLEANUP_2025_10_17_SCRIPTS_TESTS.md | Complete |
| Claude/Documentation/COST_REMOVAL_2025_10_18.md | Complete |
| Claude/Documentation/README_AND_DOCS_CLEANUP_2025_10_18.md | Complete |
| Various dated files from October | Historical |

---

## Action Items (Post-Demo)

### Priority 1: Core Doc Updates
- [ ] Add ASCII architecture diagram to docs/01-architecture.md
- [ ] Add note about startstream being a zsh function
- [ ] Update campaign examples to use 16699/16879
- [ ] Remove deprecated `streamlit run app_demo.py` command
- [ ] **Update Phase 7 performance numbers** - current times are much faster!

### Priority 2: Mock Mode Cleanup
- [ ] Remove/update mock mode references in docs/04-cache-integration.md
- [ ] Update docs/05-cache-troubleshooting.md mock mode guidance
- [ ] Update docs/09-credentials.md mock fallback section

### Priority 3: Housekeeping
- [ ] Update CLAUDE.md date
- [ ] Archive old Claude/Documentation/ files
- [ ] Review and consolidate duplicate content

---

## Recommended New Documentation Structure

```
docs/
├── README.md                    # Index (current)
├── 00-quick-start.md           # NEW: How to run, shell functions
├── 01-architecture.md          # With ASCII diagram at top
├── 02-ui-guide.md              # User guide
├── 03-demo-mode.md             # Brand anonymisation
├── 04-cache-integration.md     # Remove mock references
├── 05-cache-troubleshooting.md # Update examples
├── 06-campaign-indicators.md   # Keep
├── 07-weekly-averages.md       # Keep
├── 08-geographic-visualization.md # Keep
├── 09-credentials.md           # Remove mock fallback
├── 10-git-workflow.md          # Keep
├── 11-database-schema.md       # Keep
└── api-reference/              # Keep as-is
```

---

*This is a planning document. No changes to be made before the demo on 11 December 2025.*
