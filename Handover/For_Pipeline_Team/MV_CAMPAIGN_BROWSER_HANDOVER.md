# POC Team Handover: mv_campaign_browser Materialized View

**From**: POC Team (Route-Playout-Econometrics_POC)
**To**: Pipeline Team (route-playout-pipeline)
**Date**: 2025-11-22
**Version**: 1.0

---

## Overview

The POC Team has created a materialized view `mv_campaign_browser` that powers the Campaign Browser UI in the Streamlit application. This document explains:
- What the view does
- What tables it depends on
- How to refresh it safely
- What data it exposes

---

## Purpose

`mv_campaign_browser` is a pre-aggregated view that combines:
- Playout statistics (from `mv_playout_15min` and `mv_playout_15min_brands`)
- Brand information (from `cache_space_brands`)
- Media Owner information (from `cache_space_media_owners`)
- Buyer information (from `cache_space_buyers`)
- Audience metrics (from `cache_campaign_reach_full`)
- Weekly reach averages (from `cache_campaign_reach_week`)
- Campaign limitations (from `campaign_cache_limitations`)
- Demographic universes for Cover % (from `cache_demographic_universes`)

The view enables **sub-second queries** for the campaign browser UI by pre-joining and pre-aggregating all campaign data.

---

## Schema

### Columns

| Column | Type | Description |
|--------|------|-------------|
| `campaign_id` | varchar | Campaign reference (buyercampaignref) |
| `total_frames` | bigint | Count of unique frames used |
| `total_playouts` | bigint | Total playout count |
| `start_date` | timestamp | First playout date |
| `end_date` | timestamp | Last playout date |
| `days_active` | bigint | Count of distinct days with playouts |
| `avg_spot_length` | numeric | Average spot length in seconds |
| `primary_brand` | varchar | Most common brand by spot count |
| `brand_count` | integer | Number of distinct brands |
| `brand_names` | varchar[] | Array of all brand names |
| `primary_media_owner` | varchar | First media owner chronologically |
| `media_owner_count` | integer | Number of distinct media owners |
| `media_owner_names` | varchar[] | Array of all media owner names |
| `total_reach_all_adults` | numeric | Full campaign reach (All Adults) - in thousands |
| `total_impacts_all_adults` | numeric | Full campaign impacts (All Adults) - in thousands |
| `total_grp_all_adults` | numeric | Full campaign GRPs (All Adults) |
| `frequency_all_adults` | numeric | Average frequency (All Adults) |
| `avg_weekly_reach_all_adults` | numeric | Average reach from full 7-day weeks |
| `full_week_count` | bigint | Number of complete weeks |
| `cover_pct_all_adults` | numeric | Cover % = (Reach / Universe) * 100 |
| `route_release_id` | varchar | Route release used for metrics |
| `is_approximate_reach` | boolean | Whether reach is approximated |
| `reach_approximation_method` | varchar | Method used for approximation |
| `can_cache_full` | boolean | Whether full campaign can be cached |
| `full_cache_limitation_reason` | varchar | Reason for cache limitation |
| `limitation_notes` | text | Additional notes on limitations |
| `buyer_id` | bigint | Buyer entity ID |
| `buyer_name` | varchar | Buyer name |
| `campaign_duration` | interval | End date minus start date |
| `last_activity` | timestamp | Most recent playout timestamp |
| `refreshed_at` | timestamp | When view was last refreshed |

### Indexes

```sql
-- Primary lookup
idx_mv_campaign_browser_campaign_id (campaign_id)

-- Sorting indexes
idx_mv_campaign_browser_last_activity (last_activity DESC)
idx_mv_campaign_browser_total_playouts (total_playouts DESC)
idx_mv_campaign_browser_total_frames (total_frames DESC)
idx_mv_campaign_browser_start_date (start_date DESC)
idx_mv_campaign_browser_total_reach (total_reach_all_adults DESC)
idx_mv_campaign_browser_total_impacts (total_impacts_all_adults DESC)

-- Filtering indexes
idx_mv_campaign_browser_primary_brand (primary_brand)

-- Array search indexes (GIN)
idx_mv_campaign_browser_brand_names (brand_names)
idx_mv_campaign_browser_media_owner_names (media_owner_names)
```

---

## Dependencies

### Required Tables (Pipeline Team Manages)

| Table | Purpose |
|-------|---------|
| `mv_playout_15min` | 15-minute aggregated playout data |
| `mv_playout_15min_brands` | Brand-level playout aggregations |
| `cache_space_brands` | SPACE API brand lookups |
| `cache_space_media_owners` | SPACE API media owner lookups |
| `cache_space_buyers` | SPACE API buyer lookups |
| `cache_campaign_reach_full` | Full campaign reach/impacts (authoritative) |
| `cache_campaign_reach_week` | Weekly reach data (for fallback) |
| `campaign_cache_limitations` | Cache limitation reasons |
| `cache_demographic_universes` | Universe populations for Cover % |

### Child View

| View | Purpose |
|------|---------|
| `mv_campaign_browser_summary` | Single-row summary statistics for UI header |

---

## Refresh Instructions

### CRITICAL: Deadlock Prevention Required

This view **WILL DEADLOCK** with default PostgreSQL parallel worker settings.

**Always disable parallel workers before refresh:**

```sql
-- REQUIRED: Disable parallel workers to prevent deadlock
SET max_parallel_workers_per_gather = 0;
SET max_parallel_workers = 0;

-- Then refresh
REFRESH MATERIALIZED VIEW mv_campaign_browser;

-- Also refresh the summary view (no deadlock risk)
REFRESH MATERIALIZED VIEW mv_campaign_browser_summary;
```

### Refresh Order

1. First refresh `mv_campaign_browser` (with parallel workers disabled)
2. Then refresh `mv_campaign_browser_summary` (depends on mv_campaign_browser)

### Helper Script

POC Team has a helper script at:
```
Route-Playout-Econometrics_POC/scripts/refresh_mv_campaign_browser.sh
```

Usage:
```bash
PGPASSWORD=$YOUR_DB_PASSWORD ./scripts/refresh_mv_campaign_browser.sh
```

### Expected Refresh Time

- `mv_campaign_browser`: ~2-5 minutes (depending on data volume)
- `mv_campaign_browser_summary`: <1 second

---

## Data Notes

### Audience Metrics Units

- **Reach**: Stored in **thousands** (multiply by 1000 for absolute values)
- **Impacts**: Stored in **thousands** (multiply by 1000 for absolute values)
- **GRPs**: Stored as percentage points
- **Frequency**: Average OTS (opportunities to see)
- **Cover %**: Percentage of population reached (calculated from Reach/Universe)

### Brand Handling

- `primary_brand`: Most frequent brand by spot count
- `brand_names`: All brands as an array
- If no brand data: `primary_brand = 'Unknown'`, `brand_names = ARRAY[]`

### Media Owner Handling

- `primary_media_owner`: First media owner chronologically
- `media_owner_names`: All media owners as an array
- If no media owner data: `primary_media_owner = 'Unknown'`, `media_owner_names = ARRAY[]`

### Weekly Reach Calculation

**UPDATED 2025-11-22**: The view now uses **max available days** instead of requiring `days = 7`.

- Uses the maximum cached days for each campaign (e.g., days=1 for 1-day campaigns, days=7 for 7+ day campaigns)
- This ensures ALL campaigns with weekly cache data show their reach, regardless of campaign duration
- Uses `reach_type = 'individual'` (not cumulative)

**Migration**: `011_fix_mv_campaign_browser_weekly_reach.sql` was applied to fix this.

**Previous behavior (incorrect)**: Required `days = 7`, which excluded ~246 campaigns that ran <7 days.

### Cover % Calculation

```sql
Cover % = (Reach * 1000 / Universe) * 100
```
- Uses demographic universe from `cache_demographic_universes`
- Demographic code: `ageband>=1` (All Adults)
- Returns NULL if universe is 0 or missing

---

## Migration Files

The view is created by these migrations in the POC repository:

| File | Purpose |
|------|---------|
| `migrations/003_create_mv_campaign_browser.sql` | Main campaign browser view |
| `migrations/004_create_mv_campaign_browser_summary.sql` | Summary statistics view |

---

## Recommended Refresh Schedule

| Timing | Refresh |
|--------|---------|
| After playout data import | Yes |
| After SPACE API cache updates | Yes |
| After cache_campaign_reach_full updates | Yes |
| After cache_demographic_universes updates | Yes |
| Daily maintenance window | Recommended |

---

## Contact

For questions about this view, contact the POC Team.

---

*Document created: 2025-11-22*
