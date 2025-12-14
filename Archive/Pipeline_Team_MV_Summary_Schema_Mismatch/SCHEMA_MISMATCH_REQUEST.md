# POC Team Request: mv_campaign_browser_summary Schema Mismatch

**From**: POC Team (Route-Playout-Econometrics_POC)
**To**: Pipeline Team (route-playout-pipeline)
**Date**: 2025-11-22
**Priority**: High (UI broken)

---

## Issue

The `mv_campaign_browser_summary` view in the database has a different schema than what the POC UI expects, causing this error:

```
Error loading campaign summary statistics: column "campaigns_with_route_data" does not exist
LINE 4: campaigns_with_route_data, ^
```

---

## Current Database Schema (9 columns)

```sql
\d mv_campaign_browser_summary

           Column            |            Type
-----------------------------+-----------------------------
 total_campaigns             | bigint
 campaigns_with_reach        | bigint
 campaigns_with_weekly_reach | bigint
 total_playouts              | numeric
 total_reach                 | numeric
 total_impacts               | numeric
 earliest_campaign           | timestamp without time zone
 latest_campaign             | timestamp without time zone
 refreshed_at                | timestamp with time zone
```

---

## POC UI Required Schema (22 columns)

The POC Streamlit UI expects these columns:

```sql
-- Columns required by src/db/streamlit_queries.py
total_campaigns
campaigns_with_route_data          -- MISSING (db has: campaigns_with_reach)
total_playouts
total_unique_frames                -- MISSING
earliest_playout_date              -- MISSING (db has: earliest_campaign)
latest_playout_date                -- MISSING (db has: latest_campaign)
total_days_with_playouts           -- MISSING
total_reach_all_adults_sum         -- MISSING (db has: total_reach)
total_impacts_all_adults_sum       -- MISSING (db has: total_impacts)
avg_reach_all_adults               -- MISSING
avg_impacts_all_adults             -- MISSING
avg_grp_all_adults                 -- MISSING
avg_frequency_all_adults           -- MISSING
unique_brands_count                -- MISSING
unique_brands_list                 -- MISSING
multi_brand_campaigns_count        -- MISSING
unique_media_owners_count          -- MISSING
unique_media_owners_list           -- MISSING
unique_buyers_count                -- MISSING
unique_buyers_list                 -- MISSING
route_releases_used                -- MISSING
demographic_count                  -- MISSING
refreshed_at
```

---

## Request

Please run our migration file to recreate the view with the full schema:

```bash
# Migration file location in POC repo:
migrations/004_create_mv_campaign_browser_summary.sql

# Run command:
PGPASSWORD=$DB_PASSWORD psql -h 192.168.1.34 -U postgres -d route_poc < migrations/004_create_mv_campaign_browser_summary.sql
```

**Note**: This view depends on `mv_campaign_browser` being up-to-date first.

---

## Migration File Contents

The full migration is at: `Route-Playout-Econometrics_POC/migrations/004_create_mv_campaign_browser_summary.sql`

Key features:
- Pre-calculates summary statistics from `mv_campaign_browser`
- Provides unique lists of brands, media owners, and buyers for filter dropdowns
- Calculates aggregate metrics (avg reach, impacts, GRPs, frequency)
- Single-row view for efficient UI display

---

## Alternative: POC Team Can Run It

If preferred, confirm authorization and the POC team can run this migration directly.

---

## Impact

Until this is resolved, the Campaign Browser UI shows an error instead of the Dataset Summary section.

---

*Contact POC Team for questions*
