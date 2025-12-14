# Post-Demo Cleanup Plan

**Status**: ⚠️ READY TO EXECUTE - Board demo completed December 4th, 2025

**Next Session Priority**: Execute this cleanup plan

This document covers all cleanup tasks to be executed after the board demo.

---

# Part 1: Archive app_demo.py

## Background

The `src/ui/app_demo.py` file is a legacy demo application that uses mock data. It has been superseded by the demo mode feature in `app_api_real.py`, which provides the same brand anonymisation functionality but with real data.

### Current State
- `app_demo.py`: Uses mock data, no database connection
- `app_api_real.py` with `DEMO_MODE=true`: Uses real cached data, anonymises brands only

### Why Archive?
1. **Redundant**: Demo mode in main app provides same presentation-safe output
2. **Maintenance burden**: Two apps to maintain instead of one
3. **Confusion risk**: Users might run wrong app
4. **Real data is better**: Demo mode shows actual campaign performance, just with anonymised brands

---

## Archival Steps (Post-Demo)

### Step 1: Verify Demo Mode Works
```bash
# Test demo mode thoroughly
startstream demo
# Load multiple campaigns, check all tabs, verify brand anonymisation
```

### Step 2: Update Documentation
- [x] `docs/UI_GUIDE.md` - Mark app_demo.py as deprecated (DONE 2025-12-01)
- [x] `docs/ARCHITECTURE.md` - Mark app_demo.py as deprecated (DONE 2025-12-01)
- [x] `README.md` - Updated with correct architecture (DONE 2025-12-01)
- [ ] `CLAUDE.md` - Remove references to app_demo.py

### Step 3: Move File to Archive
```bash
# Create archive directory if needed
mkdir -p src/ui/archive

# Move the file
mv src/ui/app_demo.py src/ui/archive/app_demo.py

# Add note explaining why archived
cat > src/ui/archive/README.md << 'EOF'
# Archived UI Files

## app_demo.py (Archived 2025-12-XX)

**Reason**: Superseded by demo mode in app_api_real.py

The demo mode (`DEMO_MODE=true`) provides the same brand anonymisation
functionality but uses real cached data instead of mock data.

**To run demo mode:**
```bash
startstream demo
# or
USE_MS01_DATABASE=true DEMO_MODE=true streamlit run src/ui/app_api_real.py --server.port 8504
```

This file is retained for reference only. Do not use for new development.
EOF
```

### Step 4: Update Imports (if any)
Search for any imports of app_demo and update:
```bash
grep -r "app_demo" src/
grep -r "app_demo" tests/
```

### Step 5: Commit Changes
```bash
git add -A
git commit -m "chore: archive app_demo.py (superseded by demo mode)

- Move app_demo.py to src/ui/archive/
- Demo mode in app_api_real.py provides same functionality with real data
- Update documentation to reflect single-app architecture

🤖 Generated with Claude Code

Co-Authored-By: Claude <noreply@anthropic.com>
Co-Authored-By: ian@route.org.uk"
```

---

## Rollback Plan

If issues are discovered after archiving:

```bash
# Restore from archive
mv src/ui/archive/app_demo.py src/ui/app_demo.py

# Or restore from git
git checkout HEAD~1 -- src/ui/app_demo.py
```

---

# Part 2: Root Directory Cleanup

## Files Tracked in Git (to remove)

### Phase Documentation
These temporary phase docs are no longer needed:
```bash
git rm PHASE_7_TEST_RESULTS.md
git rm PHASE_7_TEST_SUMMARY.txt
```

### Migration Script
Move to proper location:
```bash
git mv run_migration_003.py scripts/run_migration_003.py
```

## Local Files (not in git, delete manually)

### Route API Test Outputs
```bash
rm route_response_no_grouping_*.json
rm route_response_with_grouping_*.json
```

### Test Log Files
```bash
rm test_demographics_*.log
```

### Phase 6 Documentation (gitignored)
```bash
rm PHASE6_DEMOGRAPHIC_UI_SUMMARY.md
rm PHASE6_TESTING_GUIDE.md
rm PHASE6_UI_LAYOUT.md
```

## Reference Folders (consider removing)

These are gitignored but clutter the project root. Consider moving to external location:
- `Example_Python_Project_with_ Route_API_Access/`
- `Route releases for Playout Audiences/`
- `Talon Econometrics References/`

## Commit Root Cleanup
```bash
git add -A
git commit -m "chore: clean up root directory

- Remove obsolete PHASE_7 test documentation
- Move run_migration_003.py to scripts/

🤖 Generated with Claude Code

Co-Authored-By: Claude <noreply@anthropic.com>
Co-Authored-By: ian@route.org.uk"
```

---

# Part 3: Combined Cleanup Commit (Alternative)

If doing all cleanup at once:
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

# Commit everything
git add -A
git commit -m "chore: post-demo cleanup

- Archive app_demo.py (superseded by demo mode)
- Remove obsolete PHASE_7 test documentation
- Move run_migration_003.py to scripts/
- Clean up local test outputs

🤖 Generated with Claude Code

Co-Authored-By: Claude <noreply@anthropic.com>
Co-Authored-By: ian@route.org.uk"
```

---

## Timeline

| Date | Action |
|------|--------|
| Dec 4, 2025 | Board demo (DO NOT CHANGE CODE) |
| Dec 5+, 2025 | Safe to execute all cleanup |

---

# Part 4: Framework Database Storage Fix - COMPLETED ✅

~~The pg_restore completed but data landed on the OS drive instead of the dedicated NVMe.~~

**RESOLVED 2025-12-01**: PostgreSQL data successfully moved to dedicated NVMe at `/data`.

### Final Configuration
- **Mount**: `/dev/nvme0n1p1` at `/data`
- **UUID**: `e914d13c-cd2d-41f4-93e6-4a8f5bd00a03`
- **SELinux**: `postgresql_db_t` context on `/data` and `/data/postgresql`
- **MVs Created**: `mv_frame_brand_daily` and `mv_frame_brand_hourly`
- **Test**: Verified 836 campaigns accessible from M4 Max

---

## Checklist

### Code Cleanup
- [ ] Part 1: Archive app_demo.py
- [ ] Part 2: Root directory cleanup
- [ ] Update CLAUDE.md (remove app_demo.py references)
- [ ] Remove reference folders (optional)

### Framework Database - COMPLETE ✅
- [x] Move PostgreSQL data from OS drive to dedicated NVMe (DONE 2025-12-01)
- [x] Fix fstab mount at /data with UUID=e914d13c-cd2d-41f4-93e6-4a8f5bd00a03 (DONE 2025-12-01)
- [x] Fix SELinux context on /data and /data/postgresql (DONE 2025-12-01)
- [x] Create missing MVs (mv_frame_brand_daily, mv_frame_brand_hourly) (DONE 2025-12-01)
- [x] Test connection from M4 Max to Framework (192.168.1.76) (DONE 2025-12-01)
- [x] Verify 836 campaigns in mv_campaign_browser (DONE 2025-12-01)

### Framework MV Creation SQL
```sql
-- Run on Framework after restore/move is complete
-- These MVs may be missing from the dump

CREATE MATERIALIZED VIEW IF NOT EXISTS mv_frame_brand_daily AS
SELECT pb.buyercampaignref AS campaign_id,
    pb.frameid,
    date(pb.time_window_start) AS date,
    string_agg(DISTINCT sb.name::text, ', '::text ORDER BY (sb.name::text)) AS brand_names,
    count(DISTINCT pb.spacebrandid) AS brand_count,
    sum(pb.spots_for_brand) AS total_spots
FROM mv_playout_15min_brands pb
LEFT JOIN cache_space_brands sb ON pb.spacebrandid::text = sb.entity_id::text
GROUP BY pb.buyercampaignref, pb.frameid, (date(pb.time_window_start));

CREATE INDEX IF NOT EXISTS idx_mv_frame_brand_daily_campaign ON mv_frame_brand_daily(campaign_id);

CREATE MATERIALIZED VIEW IF NOT EXISTS mv_frame_brand_hourly AS
SELECT pb.buyercampaignref AS campaign_id,
    pb.frameid,
    date_trunc('hour'::text, pb.time_window_start) AS hour_start,
    string_agg(DISTINCT sb.name::text, ', '::text ORDER BY (sb.name::text)) AS brand_names,
    count(DISTINCT pb.spacebrandid) AS brand_count,
    sum(pb.spots_for_brand) AS total_spots
FROM mv_playout_15min_brands pb
LEFT JOIN cache_space_brands sb ON pb.spacebrandid::text = sb.entity_id::text
GROUP BY pb.buyercampaignref, pb.frameid, (date_trunc('hour'::text, pb.time_window_start));

CREATE INDEX IF NOT EXISTS idx_mv_frame_brand_hourly_campaign ON mv_frame_brand_hourly(campaign_id);
```

### Documentation Already Done
- [x] Update UI_GUIDE.md (2025-12-01)
- [x] Update ARCHITECTURE.md (2025-12-01)
- [x] Update README.md (2025-12-01)
- [x] Create this cleanup plan (2025-12-01)

---

**Created**: 2025-12-01
**Updated**: 2025-12-01 (Framework setup complete)
**Author**: Claude Code
