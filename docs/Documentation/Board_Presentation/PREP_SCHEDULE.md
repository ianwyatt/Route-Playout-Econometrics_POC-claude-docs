# Board Demo Preparation Schedule
**Demo Date:** Thursday, December 4th, 2025 (morning)
**Created:** Sunday, November 30th, 2025

---

## Sunday, November 30th (Today)
**Focus: Documentation & Testing**

### Documentation Complete
- [x] Demo script created with all 6 tab walkthroughs
- [x] Presentation script aligned to 7-slide PowerPoint
- [x] Backup campaigns selected (18409 Waitrose, 16860 Specsavers)

### Testing (~1 hour) - VERIFIED
- [x] Streamlit app running (health check OK)
- [x] All 5 demo campaigns have data in mv_campaign_browser
- [x] Campaign **16699** - Channel Four, 452 frames, 15 days, 23.4% cover
- [x] Campaign **16879** - McDonald's, cliff drop Sep 21→22 confirmed
- [x] Campaign **"16879 & 16882"** - Ramps up 6x on Sep 22 (77→470)
- [x] Backup **18409** (Waitrose) - 17.5% cover, 19.1x freq (real data)
- [x] Backup **16860** (Specsavers) - 25.8% cover, 2.7x freq (real data)

**Data Quality Demo Story Verified:**
- Sep 21: 16879 = 1,481 impacts, "16879 & 16882" = 77 impacts
- Sep 22: 16879 = 0 impacts, "16879 & 16882" = 470 impacts (6x jump!)

---

## Monday, December 1st
**Focus: M1 Max Backup Setup + Framework Database Server**

### M1 Max Setup (~30-45 mins) - COMPLETE ✅
- [x] Follow `M1_MAX_BACKUP_SETUP.md`
- [x] Clone/pull repo on M1 Max
- [x] Install dependencies (`uv sync`)
- [x] Configure `.env` for MS-01 database
- [x] Add shell aliases to `~/.zshrc`
- [x] Test Streamlit starts: `startstream`
- [x] Test one campaign loads (16699)
- [x] Verify MS-01 is accessible from M1 Max

### Framework Database Server Setup - COMPLETE ✅
Follow `FRAMEWORK_DATABASE_SETUP.md`:
- [x] Partition & format `/dev/nvme0n1` as ext4
- [x] Mount at `/data`
- [x] Install PostgreSQL on Fedora
- [x] Configure data directory at `/data/postgresql`
- [x] Set postgres password (same as MS-01)
- [x] Configure pg_hba.conf for network access
- [x] Open firewall for PostgreSQL
- [x] Create database dump from M4 Max local DB
- [x] Transfer dump to Framework
- [x] Restore database on Framework
- [x] Move database to dedicated NVMe (fixed SELinux issues)
- [x] Create mv_frame_brand_daily and mv_frame_brand_hourly MVs
- [x] Test connection from M4 Max to Framework (192.168.1.76)

### Verify
- [x] M1 Max can connect to MS-01 database (192.168.1.34)
- [x] App runs on port 8504
- [x] Demo campaigns load correctly
- [x] M4 Max can connect to Framework database (192.168.1.76) as failover

### Failover Test - COMPLETE ✅
- [x] Shut down MS-01
- [x] Tested M4 Max with local database (all features working)
- [x] Tested M1 Max with Framework database (all features working)
- [x] Fixed database selection bug (dropdown now respects env var)
- [x] Restored M1 Max .env to MS-01
- [x] Restarted MS-01
- See `FAILOVER_TEST_CHECKLIST.md` for full results

---

## Tuesday, December 2nd
**Focus: Remote Access Test + Practice Run**

### Remote Access Test (from Route Office)
- [ ] Test VPN connectivity to home network
- [ ] Verify M4 Max local database accessible
- [ ] Test M1 Max → MS-01 connection
- [ ] Confirm demo campaigns load correctly

### Practice Demo (~20 mins)
- [ ] Print or have demo script accessible
- [ ] Run through full demo once:
  1. Load campaign 16699
  2. Walk through all 6 tabs with talking points
  3. Back to browser
  4. Load 16879 (data quality demo)
  5. Show the cliff drop
  6. Load "16879 & 16882" (overlap)
  7. Show correlation

### Timing Check
- Presentation: ~10 mins (7 slides)
- Demo: ~5-10 mins
- **Total: ~15-20 mins**

### Refine
- [ ] Note any awkward transitions
- [ ] Identify tabs to skip if running long (Geographic? Frame Audiences?)
- [ ] Decide: do full tab walkthrough or just highlights?

---

## Wednesday, December 3rd (Evening)
**Focus: Final Checks**

### Code Sync
- [ ] `git pull` on primary Mac
- [ ] `git pull` on M1 Max backup

### Database Check
- [ ] Verify MS-01 (192.168.1.34) is accessible
- [ ] Quick test: load one campaign on primary

### Hardware
- [ ] Charge M1 Max fully
- [ ] Check primary Mac battery/power
- [ ] Test HDMI/display adapter if presenting on external screen

### Prepare
- [ ] Have demo script open (print or second screen)
- [ ] Have PowerPoint ready
- [ ] Know the URL: http://localhost:8504

---

## Thursday, December 4th (Morning of Demo)
**Focus: Go Time**

### 30 mins before
- [ ] Start Streamlit: `stopstream && startstream`
- [ ] Quick test: load campaign 16699, verify it works
- [ ] Have M1 Max ready as backup (not running, just ready)
- [ ] Open demo script
- [ ] Open PowerPoint

### If Something Goes Wrong
1. **Campaign won't load:** Try backup (18409 or 16860)
2. **App crashes:** `stopstream && startstream`
3. **Database unavailable:** Switch to M1 Max
4. **MS-01 and local both down:** Wake Framework (`wakeonlan 9c:bf:0d:00:f8:e3`), edit `.env` to use 192.168.1.76
5. **Everything fails:** Show PowerPoint only, explain demo would show X

---

## Quick Reference

### Demo Campaigns
| Campaign | Purpose | What to Show |
|----------|---------|--------------|
| 16699 | Feature walkthrough | All 6 tabs |
| 16879 | Data quality issue | Campaign shape cliff drop |
| 16879 & 16882 | Overlap demo | Ramp-up correlation |
| 18409 | Backup (Waitrose) | Full metrics, real reach |
| 16860 | Backup (Specsavers) | Full metrics, real reach |

### Recommended Setup for Demo Day
| Priority | Device | Database | Command |
|----------|--------|----------|---------|
| **Primary** | M4 Max | Local | `startstream local demo` |
| **Backup** | M1 Max | MS-01 | `startstream demo` |
| **Failover** | M1 Max | Framework | Edit `.env` → `POSTGRES_HOST_MS01=192.168.1.76` |

**Why Local?** Faster response, no network dependency, tested and verified.

**Framework Failover**: If MS-01 goes down, edit M1 Max `.env` to use Framework (192.168.1.76).

### Key Commands
```bash
# Primary (M4 Max with local DB - RECOMMENDED)
startstream local demo

# Backup (M1 Max with MS-01)
startstream demo

# Wake Framework if needed (for failover)
wakeonlan 9c:bf:0d:00:f8:e3

# Health check
curl http://localhost:8504/_stcore/health
```

### Key Files
- Demo script: `Claude/Board_Presentation/PRESENTATION_AND_DEMO_SCRIPT.md`
- M1 Max setup: `Claude/Board_Presentation/M1_MAX_BACKUP_SETUP.md`
- Framework setup: `Claude/Board_Presentation/FRAMEWORK_DATABASE_SETUP.md`
- PowerPoint: `/Users/ianwyatt/Route Dropbox/.../Route - Playout POC Update - Board Version - 20251127.pptx`

---

*Last Updated: 2025-12-01*
