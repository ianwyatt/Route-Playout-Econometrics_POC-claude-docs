# Session Handover: Deadlock Prevention for mv_campaign_browser

**Date**: 2025-11-22
**Session Focus**: Add deadlock prevention to materialized view refresh

---

## Summary

Based on Pipeline Team's DATABASE_HANDOVER_FOR_POC.md, implemented deadlock prevention for `mv_campaign_browser` refresh operations.

---

## Changes Made

### 1. Migration 003 Updated
**File**: `migrations/003_create_mv_campaign_browser.sql`

Added parallel worker disable before REFRESH command:
```sql
-- IMPORTANT: Disable parallel workers to prevent deadlock (see Pipeline Team handover)
-- This view WILL DEADLOCK with default parallel worker settings
SET max_parallel_workers_per_gather = 0;
SET max_parallel_workers = 0;
REFRESH MATERIALIZED VIEW mv_campaign_browser;
```

### 2. Helper Script Created
**File**: `scripts/refresh_mv_campaign_browser.sh`

New shell script for ad-hoc refreshes with:
- Automatic parallel worker disable (required to prevent deadlock)
- PGPASSWORD check
- Progress output and timing
- Summary stats after refresh

**Usage**:
```bash
PGPASSWORD="$POSTGRES_PASSWORD" ./scripts/refresh_mv_campaign_browser.sh
```

---

## Background: Why This Fix Was Needed

From Pipeline Team's handover document:

> **Views Requiring Deadlock Prevention**
> These views **WILL DEADLOCK** with default parallel worker settings:
> - `mv_playout_15min_brands`
> - `mv_campaign_browser`

The fix disables parallel workers for the duration of the refresh operation.

---

## Reference

- Pipeline Team Handover: `/Users/ianwyatt/PycharmProjects/route-playout-pipeline/Claude/POC_Handover/DATABASE_HANDOVER_FOR_POC.md`
- Section: "Materialized View Refresh Reference (2025-11-21)"

---

## Files Changed

| File | Change |
|------|--------|
| `migrations/003_create_mv_campaign_browser.sql` | Added deadlock prevention |
| `scripts/refresh_mv_campaign_browser.sh` | New helper script |

---

## Next Session

- Consider adding similar fix to `migrations/004_create_mv_campaign_browser_summary.sql` if it depends on mv_campaign_browser
- Pipeline Team handles routine refreshes - this is mainly for POC team ad-hoc use

---

**Status**: Complete
