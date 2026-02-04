# Session Handover: Board Demo Preparation
**Date:** 2025-11-30
**Session Focus:** Board demo preparation for December 4th

---

## Summary of Work Completed

### 1. Demo Script Created
**File**: `Claude/Documentation/BOARD_DEMO_SCRIPT_2025_12_04.md`

Contains:
- Full walkthrough script for feature demo (campaign 16699)
- Data quality issue demo script (campaigns 16879 / 16879 & 16882)
- Talking points and narrative
- Pre-demo checklist

### 2. M1 Max Backup Setup Documented
**File**: `Claude/Documentation/M1_MAX_BACKUP_SETUP.md`

Contains:
- Setup checklist for M1 Max
- Environment configuration
- Terminal aliases
- Troubleshooting guide

### 3. Campaign Overlap Issue Documented

**The Key Discovery:**
- Campaign `16879` and combined campaign `16879 & 16882` have correlated timing
- When 16879 impacts drop off (~Sep 21-22), `16879 & 16882` ramps up
- This is the econometrician's nightmare - can't determine if spend stopped or just got re-categorised

**Visual Evidence:**
- Screenshots captured showing both campaign shapes
- Clear cliff-drop in 16879 coinciding with ramp-up in combined campaign

---

## Demo Campaign Summary

| Campaign | Purpose | Brand | Frames | Days |
|----------|---------|-------|--------|------|
| **16699** | Feature walkthrough | Channel Four | 452 | 15 |
| **16879** | Data quality issue | McDonald's | 918 | 28 |
| **16879 & 16882** | Overlap demo | McDonald's | 98 | 20 |
| **18409** | Backup (primary) | Waitrose | 1,126 | 14 |
| **16860** | Backup (secondary) | Specsavers | 642 | 15 |

### Backup Campaigns Selected (Verified with Real Reach Data)
1. **18409 (Waitrose)** ✅ - 17.5% cover, 19.1x freq
2. **16860 (Specsavers)** ✅ - 25.8% cover, 2.7x freq

### API Limitation Issues (Campaigns to Avoid)
The following campaigns trigger Route API limitations (Reach shows 0):
- **17902** - LNER (40,005 frame×days)
- **18279** - Starbucks (19,712 frame×days)
- **17543** - National Lottery (19,260 frame×days)

Worth mentioning briefly in board presentation as a known limitation we're working through.

---

## Technical Context

### Background MV Tasks Completed
All completed successfully earlier in session:
- `bc0d19`: mv_cache_campaign_impacts_frame_day rebuilt (7.4M rows)
- `14d824`: mv_cache_campaign_impacts_frame_1hr rebuilt (104.6M rows) on MS-01
- `6ca340`: mv_cache_campaign_impacts_frame_1hr rebuilt (104.6M rows) on local

### MV Impact Data Discrepancy
Note: `mv_campaign_browser` shows lower impact totals than the UI. This is a known discrepancy - the UI is displaying correct data from the source tables. May need MV refresh investigation post-demo.

---

## Files Created/Modified

### New Documentation
- `Claude/Documentation/BOARD_DEMO_SCRIPT_2025_12_04.md` - Demo script
- `Claude/Documentation/M1_MAX_BACKUP_SETUP.md` - Backup device setup

### This Session's Commits
- Earlier commits for UI styling (documented in previous handover)
- No new commits this portion of session (documentation only)

---

## Outstanding Tasks for Board Demo

### Must Complete Before Dec 4th
1. [x] **Select backup campaign** - 18409 (Waitrose) selected ✅
2. [ ] **Test all demo campaigns** - 16699, 16879, "16879 & 16882" in UI
3. [ ] **Set up M1 Max** - Follow `M1_MAX_BACKUP_SETUP.md`
4. [x] **Review PowerPoint** - Demo script aligned to 7-slide presentation ✅
5. [ ] **Practice demo** - Run through script at least once

### Documentation Complete
- [x] Full presentation script for all 7 slides
- [x] Detailed demo walkthrough for all 6 analysis tabs
- [x] Data quality demo script (campaign 16879 overlap)

### Night Before (Dec 3rd)
1. [ ] Pull latest code on both machines
2. [ ] Verify MS-01 accessible from both
3. [ ] Test all campaigns load
4. [ ] Charge M1 Max fully

### Morning Of (Dec 4th)
1. [ ] Start Streamlit on primary Mac
2. [ ] Have M1 Max ready as backup
3. [ ] Have demo script accessible (print or second screen)

---

## Quick Start for Next Session

```bash
# Start Streamlit
USE_MS01_DATABASE=true streamlit run src/ui/app_api_real.py --server.port 8504

# Or use aliases
stopstream && startstream
```

### Key Files
- Demo script: `Claude/Documentation/BOARD_DEMO_SCRIPT_2025_12_04.md`
- M1 Max setup: `Claude/Documentation/M1_MAX_BACKUP_SETUP.md`
- PowerPoint: `/Users/ianwyatt/Route Dropbox/Ian Wyatt/01-Projects/Route-Playout-Econometrics-POC/Board Presentation/20251126/Route - Playout POC Update - Board Version - 20251127.pptx`

---

## Campaign 16879 Overlap - Key Talking Points

> "Here's campaign 16879 - notice the healthy delivery through mid-September, then watch what happens around the 21st..."
>
> "The impacts fall off a cliff. Did the advertiser stop spending?"
>
> "Now look at '16879 & 16882' - it ramps up exactly when 16879 drops off."
>
> "For an econometrician, this is a nightmare. The activity didn't stop - it just got re-labelled."
>
> "This is why we need this tool - to surface these issues before they corrupt econometric models."

---

*Handover prepared by: Claude Code*
*Date: 2025-11-30*
*Demo Date: December 4th, 2025 (morning)*
