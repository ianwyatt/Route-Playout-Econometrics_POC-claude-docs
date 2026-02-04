# Handover: Board Demo Preparation Complete
**Date**: 2025-12-01
**Session Focus**: Framework database setup, failover testing, bug fixes

---

## Summary

This session completed all infrastructure preparation for the December 4th board demo, including setting up the Framework desktop as a failover database server, fixing critical bugs in database selection, and conducting a full failover test.

---

## Work Completed

### 1. Framework Database Server Setup (COMPLETE)

**Location**: Framework Desktop (192.168.1.76)
- **Specs**: Ryzen AI Max+ 395, 128GB RAM, Fedora
- **Storage**: Dedicated 4TB NVMe at `/data`

**Tasks Completed**:
- [x] pg_restore of route_poc database (~660GB)
- [x] Moved PostgreSQL data from OS drive (LUKS) to dedicated NVMe
- [x] Fixed SELinux contexts on `/data` and `/data/postgresql`
- [x] Fixed mount point permissions (`chmod 755`, `chown root:root`)
- [x] Updated fstab with UUID: `e914d13c-cd2d-41f4-93e6-4a8f5bd00a03`
- [x] Created `mv_frame_brand_daily` and `mv_frame_brand_hourly` MVs
- [x] Verified 836 campaigns accessible

**Connection Details**:
```
Host: 192.168.1.76
Port: 5432
Database: route_poc
User: postgres
Password: <same as MS-01, see .env>
```

### 2. Database Selection Bug Fix

**Problem**: The database dropdown in the UI defaulted to MS-01 even when `startstream local` was used.

**Root Cause**: Session state was hardcoded to `True` (MS-01) instead of reading from `USE_MS01_DATABASE` env var.

**Files Modified**:
- `src/ui/app_api_real.py` - Initialize session state from env var
- `src/ui/tabs/reach_grp.py` - Pass `use_ms01` to data loaders
- `src/ui/tabs/executive_summary.py` - Pass `use_ms01` to data loaders
- `src/ui/utils/export.py` - Pass `use_ms01` to all database queries

**Commit**: `685a1e2` - fix: respect USE_MS01_DATABASE env var for database selection

### 3. Export State Bug Fix

**Problem**: Export data persisted when switching campaigns, causing wrong data downloads.

**Solution**: Added `export_campaign_id` tracking and clear export state on campaign change.

**Commit**: `1b6d00a` - fix: clear export state when switching campaigns or going back

### 4. Documentation Updates

**Moved to `/docs` for GitHub sync**:
- `docs/Board_Presentation/FAILOVER_TEST_CHECKLIST.md`
- `docs/Board_Presentation/FRAMEWORK_DATABASE_SETUP.md`
- `docs/Board_Presentation/M1_MAX_BACKUP_SETUP.md`
- `docs/Board_Presentation/PREP_SCHEDULE.md`
- `docs/Board_Presentation/PRESENTATION_AND_DEMO_SCRIPT.md`
- `docs/Board_Presentation/BOARD_DEMO_SCRIPT_2025_12_04.md`

**Updated**:
- Correct env variable names (`POSTGRES_HOST_MS01` not `DB_HOST`)
- Removed hardcoded passwords (reference .env instead)
- Framework setup marked as COMPLETE
- MV creation documented

### 5. Failover Test Results

**Date**: 2025-12-01

| Test | Result |
|------|--------|
| M4 Max + Local DB | ✅ Pass |
| M1 Max + Framework DB | ✅ Pass |
| Database dropdown fix | ✅ Pass |
| Export features | ✅ Pass |
| Enter Campaign ID | ✅ Pass |

**Test Procedure**:
1. Shut down MS-01
2. Tested M4 Max with local database (demo mode)
3. Pulled latest code on M1 Max
4. Edited M1 Max `.env` to point to Framework (192.168.1.76)
5. Successfully loaded campaigns and tested all tabs
6. Restored M1 Max `.env` to MS-01

---

## Current State

### Demo Day Configuration

| Priority | Device | Database | Command |
|----------|--------|----------|---------|
| **Primary** | M4 Max | Local | `startstream local demo` |
| **Backup** | M1 Max | MS-01 (192.168.1.34) | `startstream demo` |
| **Failover** | M1 Max | Framework (192.168.1.76) | Edit `.env` |

### Failover Procedure

1. Wake Framework if sleeping: `wakeonlan 9c:bf:0d:00:f8:e3`
2. Edit M1 Max `.env`: `POSTGRES_HOST_MS01=192.168.1.76`
3. Run: `stopstream && startstream demo`
4. Test: Load campaign 16699

### Git Status

All changes committed and pushed to `main`:
- `f19af60` - docs: add Board_Presentation folder
- `685a1e2` - fix: respect USE_MS01_DATABASE env var

---

## Pending Tasks

### Before Board Demo (Dec 4)
- [ ] Test from Route office (tomorrow, Dec 2) - verify remote access/VPN

### After Board Demo
- [ ] Archive `app_demo.py` (see `Claude/ToDo/post_demo_cleanup_plan.md`)
- [ ] Clean up root directory (PHASE_7 docs, test files)
- [ ] Remove reference folders from project root

---

## Key Files Reference

| File | Purpose |
|------|---------|
| `docs/Board_Presentation/FAILOVER_TEST_CHECKLIST.md` | Step-by-step failover test |
| `docs/Board_Presentation/FRAMEWORK_DATABASE_SETUP.md` | Framework server setup |
| `docs/Board_Presentation/PREP_SCHEDULE.md` | Demo timeline & quick reference |
| `docs/Board_Presentation/PRESENTATION_AND_DEMO_SCRIPT.md` | Talking points |
| `Claude/ToDo/post_demo_cleanup_plan.md` | Post-demo cleanup tasks |

---

## Database Locations

| Database | Host | Status |
|----------|------|--------|
| Local (M4 Max) | localhost | Ready |
| MS-01 | 192.168.1.34 | Ready (production) |
| Framework | 192.168.1.76 | Ready (failover) |

All three have:
- route_poc database
- All materialized views including `mv_frame_brand_daily`, `mv_frame_brand_hourly`
- 836 campaigns in `mv_campaign_browser`

---

## Commands Quick Reference

```bash
# M4 Max - Primary demo
startstream local demo

# M1 Max - Backup
startstream demo

# Wake Framework
wakeonlan 9c:bf:0d:00:f8:e3

# Check database connection
psql -h <host> -U postgres -d route_poc -c "SELECT COUNT(*) FROM mv_campaign_browser;"

# Health check
curl http://localhost:8504/_stcore/health
```

---

**Author**: Claude Code
**Created**: 2025-12-01
