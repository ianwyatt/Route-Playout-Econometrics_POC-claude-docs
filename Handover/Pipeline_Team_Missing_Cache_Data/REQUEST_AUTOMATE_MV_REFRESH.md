# Request: Automate mv_campaign_browser Refresh

**Date**: 2025-11-17
**From**: POC UI Team
**To**: Pipeline Team
**Priority**: Medium
**Type**: Feature Request - Automation
**Status**: ✅ **COMPLETED** by Pipeline Team (2025-11-17)

---

## ✅ REQUEST STATUS: COMPLETED

**Implementation Date**: 2025-11-17
**Implemented By**: Pipeline Team (route-playout-pipeline)
**Implementation**: Standalone shell script (Option 2)
**Script Location**: `scripts/tools/refresh_mv_campaign_browser.sh`
**Tested Duration**: ~30 minutes for 838 campaigns (non-CONCURRENT)
**Pending**: Adding to cron schedule (after daily reach recache completes)

**Pipeline Team Response**: See `/Users/ianwyatt/PycharmProjects/route-playout-pipeline/Claude/Handover/RESPONSE_TO_POC_MISSING_CACHE_INVESTIGATION.md` (lines 302-448) for complete implementation details.

**Note**: Our initial estimate of 3.5 minutes was incorrect. Actual measured duration is **~30 minutes** on production hardware. Pipeline team opted for non-CONCURRENT refresh (runs at 2:30am when no users are online) to avoid deadlock and improve reliability.

---

## Summary

The POC's `mv_campaign_browser` materialized view should be refreshed automatically by the pipeline team's daily automation, not manually by POC team.

**Why**: The view depends entirely on pipeline-maintained cache tables, so pipeline should refresh it after cache updates complete.

**Impact**: ~30 minutes refresh time (non-CONCURRENT), runs AFTER your cache refresh is complete.

**⚠️ CRITICAL**: Must disable PostgreSQL parallel workers or refresh will hang indefinitely. See implementation details below.

---

## Current Situation

### Dependencies (All Pipeline-Owned)

`mv_campaign_browser` depends on:
- ✅ `cache_campaign_reach_full` (820 campaigns) - refreshed by pipeline
- ✅ `cache_route_impacts_15min_by_demo` (525,994 records) - refreshed by pipeline
- ✅ `mv_playout_15min` (playout stats) - refreshed by pipeline
- ✅ `mv_playout_15min_brands` (brand tracking) - refreshed by pipeline
- ✅ `cache_space_*` tables (SPACE API lookups) - refreshed by pipeline

**POC provides**: Only the materialized view definition (migration file)
**Pipeline provides**: All the data the view aggregates

### Current Process (Manual)

1. Pipeline refreshes caches at 2am UTC
2. POC team manually runs:
   ```sql
   REFRESH MATERIALIZED VIEW CONCURRENTLY mv_campaign_browser;
   ```
3. POC users see updated data

**Problem**: Manual step is easy to forget, leads to stale data in campaign browser UI.

---

## Proposed Solution

### Add to Pipeline Daily Refresh Schedule

**Current pipeline schedule:**
1. Playout data import (completes ~1-2am UTC)
2. Cache refresh at 2am UTC:
   - `cache_campaign_reach_full`
   - `cache_route_impacts_15min_by_demo`
   - Other demographic/reach caches

**Proposed addition:**
3. **Refresh `mv_campaign_browser`** (NEW - after step 2 completes)
   - Depends on: `cache_campaign_reach_full` and `cache_route_impacts_15min_by_demo`
   - Duration: ~30 minutes for 838 campaigns (non-CONCURRENT, with parallel workers disabled)
   - **CRITICAL**: Must disable parallel workers (see implementation below)
   - Can run in parallel with daily reach cache (they don't depend on each other)

---

## ⚠️ CRITICAL: Parallel Worker Deadlock Issue

**MUST READ BEFORE IMPLEMENTING**

This materialized view refresh **WILL HANG INDEFINITELY** if run with PostgreSQL's default parallel worker settings.

### The Problem
- PostgreSQL spawns 6-7 parallel workers for this complex view
- Workers deadlock instead of cooperating
- Refresh hangs for 6+ minutes with no completion
- View is never refreshed

### The Solution
**MUST disable parallel workers** before refreshing:

```sql
SET max_parallel_workers_per_gather = 0;
SET max_parallel_workers = 0;
```

### Performance Impact
- **Without fix (broken)**: Hangs indefinitely, never completes
- **With fix (working)**: **~30 minutes** for 838 campaigns (non-CONCURRENT, production tested)

### Why It Happens
View has complex CTEs with:
- 5 CTEs with window functions and array aggregations
- Multiple LEFT JOINs across large tables (mv_playout_15min, cache tables)
- ~838 campaigns with large data sets

PostgreSQL's parallel execution causes workers to fight instead of coordinate.

**Full troubleshooting guide**: `Claude/Documentation/Troubleshooting/POSTGRESQL_PARALLEL_WORKER_DEADLOCK_FIX.md`

---

## Implementation

### Option 1: Add to Existing Python Script

Add to your cache refresh script (e.g., `scripts/tools/refresh_caches.py`):

```python
def refresh_poc_campaign_browser():
    """Refresh POC's mv_campaign_browser materialized view."""
    import psycopg2
    import os
    from datetime import datetime

    conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST_MS01', '192.168.1.34'),
        port=int(os.getenv('POSTGRES_PORT_MS01', '5432')),
        database=os.getenv('POSTGRES_DATABASE_MS01', 'route_poc'),
        user=os.getenv('POSTGRES_USER_MS01', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD_MS01', '')
    )

    conn.autocommit = True
    cursor = conn.cursor()

    start_time = datetime.now()
    print(f"[{start_time}] Refreshing mv_campaign_browser...")

    # CRITICAL: Disable parallel workers to avoid deadlock (see POSTGRESQL_PARALLEL_WORKER_DEADLOCK_FIX.md)
    cursor.execute("SET max_parallel_workers_per_gather = 0")
    cursor.execute("SET max_parallel_workers = 0")
    print("  ✓ Disabled parallel workers (prevents deadlock)")

    # Use CONCURRENTLY to allow queries during refresh
    cursor.execute("REFRESH MATERIALIZED VIEW CONCURRENTLY mv_campaign_browser")

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    # Get campaign count
    cursor.execute("SELECT COUNT(*) FROM mv_campaign_browser")
    count = cursor.fetchone()[0]

    print(f"[{end_time}] ✓ Refreshed mv_campaign_browser: {count} campaigns in {duration:.1f}s")

    cursor.close()
    conn.close()

# Add to your refresh workflow:
# 1. refresh_demographics_cache()
# 2. refresh_campaign_reach_full()
# 3. refresh_poc_campaign_browser()  # NEW
# 4. refresh_daily_reach_cache()  # Can run in parallel
```

### Option 2: Standalone SQL Script ✅ **IMPLEMENTED**

**Pipeline team chose this option** - Script created at `scripts/tools/refresh_mv_campaign_browser.sh` in route-playout-pipeline repository.

**Original proposal** (actual implementation may vary slightly):

Create `scripts/refresh_mv_campaign_browser.sh`:

```bash
#!/bin/bash
# Refresh POC's mv_campaign_browser materialized view
# Run after cache_campaign_reach_full and cache_route_impacts_15min_by_demo are refreshed
# CRITICAL: Must disable parallel workers to avoid deadlock (see POSTGRESQL_PARALLEL_WORKER_DEADLOCK_FIX.md)

PGHOST="${POSTGRES_HOST_MS01:-192.168.1.34}"
PGPORT="${POSTGRES_PORT_MS01:-5432}"
PGDATABASE="${POSTGRES_DATABASE_MS01:-route_poc}"
PGUSER="${POSTGRES_USER_MS01:-postgres}"
PGPASSWORD="${POSTGRES_PASSWORD_MS01}"

export PGHOST PGPORT PGDATABASE PGUSER PGPASSWORD

echo "[$(date)] Starting mv_campaign_browser refresh..."
START=$(date +%s)

# CRITICAL: Use heredoc to set parallel workers to 0 before refresh
psql <<'SQL'
-- Disable parallel workers to prevent deadlock
SET max_parallel_workers_per_gather = 0;
SET max_parallel_workers = 0;

-- Now refresh the view
-- NOTE: Pipeline team used non-CONCURRENT (runs at 2:30am when no users online)
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_campaign_browser;
SQL

END=$(date +%s)
DURATION=$((END - START))

COUNT=$(psql -t -c "SELECT COUNT(*) FROM mv_campaign_browser;")

echo "[$(date)] ✓ Refreshed mv_campaign_browser: $COUNT campaigns in ${DURATION}s"
```

Then add to your cron or scheduler:
```bash
# After cache refresh completes at ~2:30am
30 2 * * * /path/to/scripts/refresh_mv_campaign_browser.sh >> /var/log/pipeline/mv_refresh.log 2>&1
```

---

## Performance Considerations

### Refresh Duration
- **Measured**: **~30 minutes** for 838 campaigns (non-CONCURRENT, with parallel workers disabled)
- **Variable**: Will vary based on campaign count and database load
- **Locking**: Uses non-CONCURRENT refresh (runs at 2:30am when no users online)
- **WARNING**: Without disabling parallel workers, refresh will hang indefinitely (never completes)
- **Note**: Pipeline team chose non-CONCURRENT for reliability; CONCURRENT would deadlock even with parallel workers disabled

### Resource Usage
- CPU: Moderate (aggregations and JOINs)
- Memory: Low (view is pre-indexed)
- Disk I/O: Moderate (reading cache tables, writing view)
- Lock: None (CONCURRENTLY avoids exclusive locks)

### Concurrent Execution
Can run in parallel with:
- ✅ Daily reach cache refresh (no dependencies)
- ✅ POC UI queries (CONCURRENTLY allows this)

Must run AFTER:
- ❌ `cache_campaign_reach_full` refresh
- ❌ `cache_route_impacts_15min_by_demo` refresh

---

## Verification

After adding to automation, verify:

```sql
-- Check view has been refreshed recently
SELECT
    refreshed_at,
    COUNT(*) as campaign_count,
    MAX(last_activity) as most_recent_campaign_activity
FROM mv_campaign_browser
GROUP BY refreshed_at
ORDER BY refreshed_at DESC
LIMIT 1;

-- Expected: refreshed_at within last 24 hours
```

**Success criteria**:
- View refreshes daily without manual intervention
- `refreshed_at` timestamp updates daily
- Campaign count matches expectations (~838 campaigns)
- No errors in pipeline logs

---

## Rollback Plan

If refresh causes issues:

1. **Remove from automation schedule**
2. **POC team reverts to manual refresh**
3. **Investigate performance issue**
4. **Re-enable after fix**

View can always be manually refreshed (don't forget parallel worker fix):
```sql
-- Manual refresh (must include parallel worker fix)
SET max_parallel_workers_per_gather = 0;
SET max_parallel_workers = 0;
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_campaign_browser;
```

---

## Benefits

**For Pipeline Team:**
- ✅ Full ownership of data pipeline end-to-end
- ✅ POC view stays in sync with cache refreshes automatically
- ✅ No coordination needed with POC team for refresh timing
- ✅ Consistent data across all systems

**For POC Team:**
- ✅ Always have fresh data in campaign browser
- ✅ No manual refresh required
- ✅ Reduced operational burden
- ✅ Automatic updates when pipeline fixes data issues

**For Users:**
- ✅ Campaign browser always shows latest data
- ✅ No stale reach/impacts values
- ✅ Consistent experience

---

## Migration File Reference

The view definition is in POC repository:
```
/Users/ianwyatt/PycharmProjects/Route-Playout-Econometrics_POC/migrations/003_create_mv_campaign_browser.sql
```

**View characteristics:**
- Creates indexes for sorting/filtering
- Uses LEFT JOINs (missing cache data → 0)
- Stores `refreshed_at` timestamp for monitoring
- No schema changes required to automate refresh

---

## Questions?

**POC Team Contact:**
- Repository: `Route-Playout-Econometrics_POC`
- Migration: `migrations/003_create_mv_campaign_browser.sql`
- Handover: `Claude/Handover/Pipeline_Team_Missing_Cache_Data/`

**Pipeline Team Contact:**
- Repository: `route-playout-pipeline`
- Cache refresh: `scripts/tools/backfill_route_cache.py`
- Contact: Ian Wyatt (ian@route.org.uk)

---

## Timeline

**Requested**: 2025-11-17
**Priority**: Medium (not urgent, but improves data freshness)
**Status**: ✅ **COMPLETED** 2025-11-17
**Actual effort**: ~2 hours (script creation and testing)
**Implementation**: Standalone shell script at `scripts/tools/refresh_mv_campaign_browser.sh`
**Tested duration**: ~30 minutes for 838 campaigns
**Pending**: Adding to cron schedule (after daily reach recache completes)

---

**Thank you for implementing this automation request!** The POC campaign browser will now always show the freshest data without manual intervention once cron scheduling is complete.
