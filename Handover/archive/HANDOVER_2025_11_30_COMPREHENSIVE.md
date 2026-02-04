# Comprehensive Session Handover
**Date:** Sunday, November 30th, 2025
**Demo Date:** Thursday, December 4th, 2025 (morning)

---

## Executive Summary

Board demo preparation is **on track**. All documentation complete, all demo campaigns verified, data quality story confirmed. Remaining tasks are manual: M1 Max setup, practice run, final checks.

---

## Session Accomplishments

### 1. Presentation & Demo Script Created
**File:** `Claude/Board_Presentation/PRESENTATION_AND_DEMO_SCRIPT.md`

Complete script covering:
- **7 PowerPoint slides** with talking points (~10 mins)
- **6 analysis tabs** walkthrough with actions and scripts
- **Data quality demo** (campaign 16879 overlap story)
- **Backup campaigns** and troubleshooting

### 2. Prep Schedule Created
**File:** `Claude/Board_Presentation/PREP_SCHEDULE.md`

| Day | Focus | Status |
|-----|-------|--------|
| Sun Nov 30 | Documentation + Testing | ✅ COMPLETE |
| Mon Dec 1 | M1 Max backup setup | Pending |
| Tue Dec 2 | Practice run-through | Pending |
| Wed Dec 3 | Final checks | Pending |
| Thu Dec 4 | Demo day | - |

### 3. Demo Campaigns Verified

All 5 campaigns tested against database:

| Campaign | Brand | Frames | Days | Cover | Freq | Status |
|----------|-------|--------|------|-------|------|--------|
| **16699** | Channel Four | 452 | 15 | 23.4% | 4.0x | ✅ Feature demo |
| **16879** | McDonald's | 918 | 28 | 19.6% | 2.4x | ✅ Cliff drop verified |
| **16879 & 16882** | McDonald's | 98 | 20 | 7.2% | 1.9x | ✅ Ramp-up verified |
| **18409** | Waitrose | 1,126 | 14 | 17.5% | 19.1x | ✅ Backup #1 |
| **16860** | Specsavers | 642 | 15 | 25.8% | 2.7x | ✅ Backup #2 |

### 4. Data Quality Story Confirmed

The cliff drop / ramp-up correlation is rock solid:

```
Campaign 16879:
  Sep 21: 1,481 impacts (healthy)
  Sep 22: 0 impacts (cliff drop)

Campaign "16879 & 16882":
  Sep 21: 77 impacts (low)
  Sep 22: 470 impacts (6x jump!)
```

**Key talking point:** "The activity didn't stop - it just got re-labelled under a different campaign ID."

---

## Board Presentation Structure

### PowerPoint (7 slides, ~10 mins)

| Slide | Title | Key Points |
|-------|-------|------------|
| 1 | Title | Route POC Progress Update |
| 2 | Executive Summary | 11+ Billion records, 1.2B in POC, 836 campaigns |
| 3 | What We've Done | 1.28B → 416M records, 91K API calls, UI built |
| 4 | Data Challenges: Campaign IDs | 97.75% valid by volume, 26.5% invalid by ID |
| 5 | Data Challenges: Brand Attribution | 42%/22%/35% split, 57.6% can't be fully attributed |
| 6 | Data Challenges: Reach & GRPs | Flighted campaigns break reach model (~10%) |
| 7 | Thank You | Transition to demo |

### Live Demo (6 tabs, ~5-10 mins)

| Tab | Content | Key Talking Points |
|-----|---------|-------------------|
| 📊 Overview | Metrics, Campaign Shape | Impacts, GRP, Reach, Cover, Frequency |
| 📈 Weekly Reach | Weekly table, Cumulative Build | "What econometricians need" |
| ⏰ Daily & Hourly | Trends, Heatmap | Peak performance, delivery patterns |
| 🗺️ Geographic | Map, Regional charts | Frame locations, regional distribution |
| 🔬 Frame Audiences | Daily/Hourly tables | "Export for MMM integration" |
| 📑 Executive Summary | One-page view | "Screenshot for reports" |

### Data Quality Demo

1. Load campaign **16879** - show healthy delivery, then cliff drop
2. Ask: "Did the advertiser stop spending?"
3. Load **"16879 & 16882"** - show it ramps up exactly when 16879 drops
4. Punchline: "The activity didn't stop - it got re-categorised"

---

## Files Created This Session

### Board Presentation Folder (`Claude/Board_Presentation/`)
| File | Purpose |
|------|---------|
| `PRESENTATION_AND_DEMO_SCRIPT.md` | Full presentation + demo script |
| `PREP_SCHEDULE.md` | Daily prep checklist through Dec 4 |
| `BOARD_DEMO_SCRIPT_2025_12_04.md` | Campaign details, API limitations |
| `M1_MAX_BACKUP_SETUP.md` | Backup device setup guide |

### Updated Files
| File | Changes |
|------|---------|
| `Claude/ToDo/upcoming_tasks.md` | Marked demo prep tasks complete |
| `Claude/Handover/HANDOVER_2025_11_30_BOARD_PREP.md` | Updated with tab walkthrough status |

---

## Technical Context

### App Status
- **Streamlit:** Running on port 8504
- **Health check:** `curl http://localhost:8504/_stcore/health` → OK

### Recommended Demo Setup (Updated)
| Priority | Device | Database | Command |
|----------|--------|----------|---------|
| **Primary** | M4 Max | Local (658GB) | `startstream local demo` |
| **Backup** | M1 Max | MS-01 | `startstream demo` |

**Why Local?** Faster response, no network dependency, all demo campaigns verified.

### Key Commands
```bash
# Primary (M4 Max with local DB - RECOMMENDED)
startstream local demo

# Backup (M1 Max with MS-01)
startstream demo

# Health check
curl http://localhost:8504/_stcore/health
```

### Background MV Tasks - ALL COMPLETE ✅
- `bc0d19`: mv_cache_campaign_impacts_frame_day rebuilt (7.4M rows)
- `14d824`: mv_cache_campaign_impacts_frame_1hr rebuilt on MS-01 (104.7M rows)
- `6ca340`: mv_cache_campaign_impacts_frame_1hr rebuilt on local (104.7M rows)

---

## Remaining Manual Tasks

### Monday, December 1st - M1 Max Setup (~30-45 mins)
1. Clone/pull repo on M1 Max
2. `uv sync` to install dependencies
3. Configure `.env` for MS-01 database
4. Add shell aliases to `~/.zshrc`
5. Test: `startstream` then load campaign 16699
6. Verify MS-01 accessible from M1 Max

### Tuesday, December 2nd - Practice Run (~20 mins)
1. Run through full presentation + demo
2. Time it (target: 15-20 mins total)
3. Note any awkward transitions
4. Decide which tabs to skip if running long

### Wednesday, December 3rd - Final Checks (~15 mins)
1. `git pull` on both machines
2. Verify MS-01 accessible
3. Charge M1 Max fully
4. Have demo script ready (print or second screen)

### Thursday, December 4th - Demo Day
1. Start Streamlit 30 mins before
2. Quick test: load campaign 16699
3. Have M1 Max ready as backup
4. Go time!

---

## If Something Goes Wrong

| Problem | Solution |
|---------|----------|
| Campaign won't load | Try backup: 18409 (Waitrose) or 16860 (Specsavers) |
| App crashes | `stopstream && startstream` |
| Database unavailable | Switch to M1 Max |
| M1 Max fails too | PowerPoint only, explain what demo would show |

---

## Key File Locations

| File | Path |
|------|------|
| Demo script | `Claude/Board_Presentation/PRESENTATION_AND_DEMO_SCRIPT.md` |
| Prep schedule | `Claude/Board_Presentation/PREP_SCHEDULE.md` |
| M1 Max setup | `Claude/Board_Presentation/M1_MAX_BACKUP_SETUP.md` |
| PowerPoint | `/Users/ianwyatt/Route Dropbox/Ian Wyatt/01-Projects/Route-Playout-Econometrics-POC/Board Presentation/20251126/Route - Playout POC Update - Board Version - 20251127.pptx` |

---

## Quick Start for Next Session

```bash
# Check app status
curl http://localhost:8504/_stcore/health

# If not running
stopstream && startstream

# Test a campaign
# Open http://localhost:8504 and load campaign 16699
```

---

*Handover prepared by: Claude Code*
*Session date: Sunday, November 30th, 2025*
*Demo date: Thursday, December 4th, 2025 (morning)*
