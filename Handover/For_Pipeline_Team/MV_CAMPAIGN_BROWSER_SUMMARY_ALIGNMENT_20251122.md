# Handover: mv_campaign_browser_summary Schema Alignment

**From**: Pipeline Team (route-playout-pipeline)
**To**: POC Team (Route-Playout-Econometrics_POC)
**Date**: 2025-11-22
**Status**: COMPLETE

---

## Summary

The `mv_campaign_browser_summary` view has been fixed and aligned between both repositories.

| Issue | Resolution |
|-------|------------|
| Schema mismatch (9 vs 22 columns) | **FIXED** - View now has full 22-column schema |
| POC UI error "campaigns_with_route_data does not exist" | **FIXED** - Column now exists |
| Pipeline migration out of sync | **FIXED** - New migration 012 created |

---

## What Was Done

### 1. Applied POC Migration to Database

The POC team's `migrations/004_create_mv_campaign_browser_summary.sql` was run on MS01:

```bash
PGPASSWORD='...' psql -h 192.168.1.34 -U postgres -d route_poc \
  -f /path/to/Route-Playout-Econometrics_POC/migrations/004_create_mv_campaign_browser_summary.sql
```

**Result**: View now has 22 columns as expected by the UI.

### 2. Created Pipeline Migration to Match

New migration created: `sql/migrations/012_align_mv_campaign_browser_summary_with_poc.sql`

This ensures future pipeline deployments create the correct 22-column schema.

### 3. Updated Pipeline Documentation

Updated: `docs/03-database/materialized-views.md`
- Added documentation for mv_campaign_browser (section 7)
- Added documentation for mv_campaign_browser_summary (section 8)
- Added refresh commands for campaign browser views

---

## Current Schema (22 columns)

| Column | Type | Description |
|--------|------|-------------|
| total_campaigns | bigint | Total campaign count |
| campaigns_with_route_data | bigint | Campaigns with reach/impacts data |
| total_playouts | numeric | Sum of all playouts |
| total_unique_frames | numeric | Sum of unique frames |
| earliest_playout_date | timestamp | First playout timestamp |
| latest_playout_date | timestamp | Last playout timestamp |
| total_days_with_playouts | bigint | Days with activity |
| total_reach_all_adults_sum | numeric | Sum of campaign reach |
| total_impacts_all_adults_sum | numeric | Sum of campaign impacts |
| avg_reach_all_adults | numeric | Average reach |
| avg_impacts_all_adults | numeric | Average impacts |
| avg_grp_all_adults | numeric | Average GRP |
| avg_frequency_all_adults | numeric | Average frequency |
| unique_brands_count | bigint | Count of distinct brands |
| unique_brands_list | varchar[] | Array of brand names |
| multi_brand_campaigns_count | bigint | Campaigns with multiple brands |
| unique_media_owners_count | bigint | Count of media owners |
| unique_media_owners_list | varchar[] | Array of media owner names |
| unique_buyers_count | bigint | Count of buyers |
| unique_buyers_list | varchar[] | Array of buyer names |
| route_releases_used | int[] | Array of Route release IDs |
| demographic_count | bigint | Count of cached demographics |
| refreshed_at | timestamptz | When view was last refreshed |

---

## Current Data Values

As of 2025-11-22:

| Metric | Value |
|--------|-------|
| total_campaigns | 836 |
| campaigns_with_route_data | 828 |
| total_playouts | 1,265,344,117 |
| total_unique_frames | 143,989 |
| earliest_playout_date | 2025-08-06 09:45:00 |
| latest_playout_date | 2025-10-13 13:00:00 |
| total_days_with_playouts | 69 |
| unique_brands_count | 182 |
| multi_brand_campaigns_count | 234 |
| unique_media_owners_count | 6 |
| unique_buyers_count | 1 |
| avg_reach_all_adults | 1,154.89 |
| avg_impacts_all_adults | 7,390.56 |

---

## Refresh Procedure

When refreshing after cache backfills:

```bash
# Use the dedicated script (handles deadlock prevention)
POSTGRES_PASSWORD_MS01="${DB_PASSWORD}" ./scripts/tools/refresh_mv_campaign_browser.sh
```

Or manually:

```sql
SET max_parallel_workers_per_gather = 0;
SET max_parallel_workers = 0;

REFRESH MATERIALIZED VIEW mv_campaign_browser;
REFRESH MATERIALIZED VIEW mv_campaign_browser_summary;
```

**Order matters**: mv_campaign_browser must be refreshed before mv_campaign_browser_summary.

---

## Verification

To verify the schema is correct:

```sql
\d mv_campaign_browser_summary
-- Should show 23 columns (22 data + 1 refreshed_at)

SELECT total_campaigns, campaigns_with_route_data, unique_brands_count
FROM mv_campaign_browser_summary;
-- Should return data without errors
```

---

## Files Changed (Pipeline Repo)

| File | Change |
|------|--------|
| `sql/migrations/012_align_mv_campaign_browser_summary_with_poc.sql` | NEW - Creates 22-column schema |
| `docs/03-database/materialized-views.md` | UPDATED - Added sections 7 & 8 |

---

## Related Issues Resolved

| Issue | Status |
|-------|--------|
| Weekly reach = 0 for short campaigns | FIXED (Migration 011) |
| Summary view schema mismatch | FIXED (Migration 012) |
| TAB characters in campaign IDs | FIXED (previous session) |

---

## Contact

For questions about the pipeline or view definitions, contact the Pipeline Team.

---

**Created**: 2025-11-22
**By**: Claude Code (Pipeline Team)
