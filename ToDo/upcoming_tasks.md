# Upcoming Tasks

## 1. Cumulative Build Enhancement (Pending)

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

## 2. Performance Investigation (COMPLETED & MERGED)

**Branch**: `feature/performance-investigation` → merged to main

**Status**: COMPLETED - Merged to main on 2025-11-29

**Summary of Work Done**:
1. Created `mv_playout_frame_day` MV (1.2M rows vs 67M source) - 271x faster
2. Created `mv_playout_frame_hour` MV (17M rows vs 67M source) - 4x reduction
3. Created `mv_frame_audience_daily` (3.2M rows) - 9x faster queries
4. Created `mv_frame_audience_hourly` (46M rows) - Pre-joined hourly data
5. Added SQL LIMIT to queries (2000 row default) for faster initial load
6. Added `@st.cache_data(ttl=3600)` to all frame audience loaders
7. Reordered tabs: Campaign → Daily → Hourly (smallest first)
8. Added custom CSV/Excel download buttons for full dataset export
9. Synced all MVs and indexes to local database

**Documentation**:
- `docs/ARCHITECTURE.md` - Performance optimization section added
- `Claude/Handover/Pipeline/mv_playout_frame_day_handover.md`
- `Claude/Handover/2025-11-29_performance_optimization_handover.md`

---

## 3. UI Polish for Board Demo (COMPLETED)

**Status**: COMPLETED - Merged to main on 2025-11-30

**Summary of Work Done**:
1. Tab state preservation - Replaced `st.tabs` with `st.segmented_control`
2. Button styling - Frosted glass effect with cyan accent for primary buttons
3. Route logo integration - Added to main header and campaign analysis header
4. Global CSS - Moved styling to be applied consistently across app

**Commits**:
- `97dda27` - style: add frosted glass button and teal tab selector styling
- `e253705` - refactor: make primary button styling global for consistency
- `079e0f8` - feat: add Route company logo to header and analysis page

**Files Modified**:
- `src/ui/components/campaign_browser.py` - Header and button styling
- `src/ui/app_api_real.py` - Campaign analysis header logo
- `src/ui/assets/Route Logo White-01.png` - New logo asset

**Documentation**:
- `docs/UI_GUIDE.md` - Updated with Visual Design section
- `Claude/Handover/HANDOVER_2025_11_30_UI_STYLING_AND_LOGO.md`

---

## 4. Board Demo Preparation (IN PROGRESS)

**Demo Date**: December 4th, 2025 (morning)

**Status**: IN PROGRESS - M1 Max setup complete, Framework database restore in progress

**Demo Campaigns**:
- **16699** - Feature walkthrough (Channel Four, 452 frames, 15 days)
- **16879** - Data quality issue demo (McDonald's, 918 frames, 28 days)
- **16879 & 16882** - Overlap demonstration (combined campaign)
- **18409** - Backup primary (Waitrose, 1,126 frames, 14 days, 17.5% cover)
- **16860** - Backup secondary (Specsavers, 642 frames, 15 days, 25.8% cover)

**Key Demo Story - Campaign Overlap Issue**:
- Campaign 16879 impacts drop off ~Sep 21-22
- Campaign "16879 & 16882" ramps up exactly when 16879 drops
- Perfect example of econometrician's spend attribution nightmare
- Shows value of tool for data quality investigation

**Outstanding Tasks**:
- [x] Select backup campaign - **18409 (Waitrose)** selected (LNER had API limitation issue)
- [x] Create full presentation script aligned to 7-slide PowerPoint
- [x] Write detailed demo walkthrough for all 6 analysis tabs
- [x] Test all campaigns in UI (verified in database)
- [x] Set up M1 Max as backup device
- [ ] Complete Framework database setup (see section 5 below)
- [ ] Practice demo run-through

**Documentation** (all in `Claude/Board_Presentation/`):
- `PRESENTATION_AND_DEMO_SCRIPT.md` - Full presentation + demo script
- `BOARD_DEMO_SCRIPT_2025_12_04.md` - Demo campaign details & API limitations
- `M1_MAX_BACKUP_SETUP.md` - Backup device setup guide
- `FRAMEWORK_DATABASE_SETUP.md` - Framework backup database server guide
- `PREP_SCHEDULE.md` - Daily prep schedule through Dec 4

**PowerPoint Reference**:
`/Users/ianwyatt/Route Dropbox/Ian Wyatt/01-Projects/Route-Playout-Econometrics-POC/Board Presentation/20251126/Route - Playout POC Update - Board Version - 20251127.pptx`

---

## 5. Framework Database Server Setup (IN PROGRESS)

**Purpose**: Backup PostgreSQL server for M1 Max if MS-01 is unavailable

**Framework Specs**:
- Device: Framework Desktop
- OS: Fedora
- CPU: Ryzen AI Max+ 395
- RAM: 128GB
- Storage: 2x Samsung 990 PRO 4TB NVMe
- Network IP: 192.168.1.76

**Demo Day Redundancy**:
| Priority | Demo Machine | Database | IP |
|----------|--------------|----------|-----|
| Primary | M4 Max | Local PostgreSQL | localhost |
| Backup | M1 Max | MS-01 | 192.168.1.34 |
| Failover | M1 Max | Framework | 192.168.1.76 |

**Completed Steps**:
- [x] Partition `/dev/nvme0n1` as ext4
- [x] Install PostgreSQL on Fedora
- [x] Configure `postgresql.conf` for network access (`listen_addresses = '*'`)
- [x] Configure `pg_hba.conf` for network access (192.168.1.0/24 scram-sha-256)
- [x] Set postgres password (same as MS-01)
- [x] Create `route_poc` database
- [x] Open firewall for PostgreSQL
- [x] Fix SELinux context for `/data/postgresql`
- [x] Test connection from M4 Max to Framework
- [x] Create database dump from M4 Max local DB (50.3GB)
- [x] Transfer dump to Framework via rsync

**In Progress**:
- [ ] **pg_restore running** - Currently indexing `playout_data` table
  - Started: 15:38 GMT
  - Progress: Creating indexes on playout_data table
  - Currently at: idx_playout_* indexes (parallel -j 8)

**Remaining Steps After Restore**:
- [ ] Wait for pg_restore to complete
- [ ] Move PostgreSQL data from OS drive to dedicated NVMe (restore went to wrong mount)
  - Stop PostgreSQL
  - Unmount `/run/media/ianwyatt/data`
  - Fix fstab: mount `/dev/nvme0n1p1` at `/data`
  - Move `/data/postgresql` to correct location
  - Fix SELinux context
  - Start PostgreSQL
- [ ] Test connection from M1 Max to Framework (192.168.1.76)
- [ ] Verify demo campaigns load correctly

**Storage Issue Discovered**:
- The `/data` mount went to OS drive (Btrfs LUKS) instead of dedicated NVMe
- Auto-mount put NVMe at `/run/media/ianwyatt/data` instead
- Restore is using ~800GB on encrypted OS drive
- Will move data to dedicated NVMe after restore completes

**Documentation**:
- `Claude/Board_Presentation/FRAMEWORK_DATABASE_SETUP.md` - Full setup guide

---

*Last Updated: 2025-12-01*
