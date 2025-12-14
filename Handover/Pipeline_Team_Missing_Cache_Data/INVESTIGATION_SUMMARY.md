# Missing Reach and Impacts Cache Data - Investigation Summary

**Date**: November 15, 2025
**Investigated By**: Claude Code (POC UI Team)
**Handover To**: Pipeline Team
**Issue**: Campaigns missing from reach and/or impacts cache tables

---

## Executive Summary

**48 out of 838 campaigns (5.7%)** are missing from the reach cache (`cache_campaign_reach_full`), and **16 campaigns (1.9%)** are missing from the impacts cache (`cache_route_impacts_15min_by_demo`).

**CRITICAL**: 52% of missing campaigns (25 out of 48) are **small/medium sized** and should have reach data. This indicates a **backfill process issue**, not API limits.

---

## Affected Campaigns Breakdown

### Missing Reach Data (48 campaigns)

| Campaign Size | Count | Likely Cause | Action Required |
|--------------|-------|--------------|-----------------|
| Small (<1M playouts) | 5 | **Backfill issue** | Investigate + fix |
| Medium (1M-10M playouts) | 20 | **Backfill issue** | Investigate + fix |
| Large (10M-50M playouts) | 21 | API limits or backfill | Review API response |
| Very Large (>50M playouts) | 2 | **API limits expected** | Document as expected |

**Total needing investigation**: 25 small/medium campaigns (52% of missing)

### Missing Impacts Data (16 campaigns)

16 campaigns are missing from `cache_route_impacts_15min_by_demo` - these need investigation as impacts cache should be more complete than reach cache.

---

## Key Findings

### 1. Campaign 18856 (User-Reported Example)
- **Status**: Missing from reach cache, has impacts data
- **Size**: 1.6M playouts, 125 frames, 14 days (Sept 29 - Oct 13, 2025)
- **Expected**: Should have reach data
- **Diagnosis**: Backfill issue

### 2. Extremely Small Campaigns Missing Reach
- Campaign 18977: Only **16 playouts**, 1 frame, 1 day (Oct 7, 2025)
- Campaign 19220: Only **28 playouts**, 2 frames, 1 day (Oct 7, 2025)
- These should be trivial for Route API to process

### 3. Temporal Pattern
**Most affected campaigns started in late September 2025**, suggesting:
- Backfill process may not be running regularly
- Backfill may have failed for recent campaigns
- Process may be behind schedule

### 4. Data Exists in Source
All investigated campaigns exist in `playout_data` table with valid records. The issue is in the caching pipeline, not the source data.

---

## Campaign Lists

See attached files:
- `campaigns_missing_reach_SMALL.csv` - Small campaigns (<1M playouts) - **PRIORITY**
- `campaigns_missing_reach_MEDIUM.csv` - Medium campaigns (1M-10M playouts) - **PRIORITY**
- `campaigns_missing_reach_LARGE.csv` - Large campaigns (10M-50M playouts)
- `campaigns_missing_reach_VERY_LARGE.csv` - Very large campaigns (>50M playouts) - expected
- `campaigns_missing_impacts.csv` - All campaigns missing impacts data

---

## Recommended Actions for Pipeline Team

### Immediate (Priority 1)
1. **Check reach backfill process status**
   - When did it last run successfully?
   - Are there errors in logs for September/October 2025 campaigns?
   - Is the process running on schedule?

2. **Investigate small campaign failures** (5 campaigns)
   - These should NEVER fail - only 16-72K playouts
   - Check Route API responses for these campaigns
   - Verify no API errors were logged

3. **Review medium campaign failures** (20 campaigns)
   - 1M-10M playouts should succeed
   - Check for API timeouts or rate limits
   - Verify campaign date ranges are within Route release windows

### Secondary (Priority 2)
4. **Review large campaign handling** (21 campaigns)
   - Determine which are genuine API limits vs backfill issues
   - Document expected behavior for very large campaigns
   - Consider batch processing strategy

5. **Investigate impacts cache gaps** (16 campaigns)
   - Why are impacts missing when playout data exists?
   - Compare to reach cache gaps - same campaigns?

### Long-term (Priority 3)
6. **Implement monitoring**
   - Alert when campaigns remain uncached after X days
   - Track backfill success rate by campaign size
   - Monitor API response times and failures

7. **Document expected behavior**
   - What campaign sizes should always succeed?
   - What are legitimate API limits?
   - What's the SLA for backfilling new campaigns?

---

## Verification Queries

See `verification_queries.sql` for SQL to:
- Check current cache coverage
- Identify campaigns needing backfill
- Verify cache freshness
- Monitor backfill progress

---

## Database Schema Context

### `cache_campaign_reach_full` ⚠️ **NOT IN PIPELINE DOCS**
- Stores **full campaign reach** (All Adults demographic) - one record per campaign
- Values stored in **thousands** (divide by 1000 for storage)
- Source: Route API reach endpoint
- **Current coverage**: 790 out of 838 campaigns (94.3%)
- **NOTE**: This is DIFFERENT from `cache_campaign_reach_day` (daily reach, 11,363 records)
- **May be newer cache table** - not documented in pipeline handover (last updated 2025-10-17)

### `cache_route_impacts_15min_by_demo`
- Stores 15-minute time window impacts by demographic
- Values stored in **thousands** (divide by 1000 for storage)
- Source: Route API playout endpoint
- **Current coverage**: 822 out of 838 campaigns (98.1%)

### `cache_campaign_reach_day` (Mentioned in Pipeline Docs)
- Stores **daily reach** breakdowns with GRP, frequency metrics
- 11,363 records (multiple records per campaign, one per day)
- This is different from `cache_campaign_reach_full` (full campaign reach)

### `mv_campaign_browser`
- Materialized view joining playout data with cache tables
- Uses **LEFT JOIN** - missing cache entries show as 0
- Refreshed after playout imports
- UI displays values × 1000 (reverses storage scaling)

---

## Contact

For questions about this investigation or UI behavior:
- POC UI repository: `Route-Playout-Econometrics_POC`
- Campaign browser: `src/ui/app_api_real.py`
- Database queries: `src/db/streamlit_queries.py`

For pipeline/caching issues:
- Pipeline repository: `route-playout-pipeline`
- Reach backfill: (pipeline team to document)
- Impacts backfill: (pipeline team to document)

---

## POC Database Dependencies - Coordination Required

### mv_campaign_browser Materialized View

The POC project has created a **materialized view** on MS-01 database that depends on pipeline-maintained tables:

**View Name**: `mv_campaign_browser`
**Location**: MS-01 database (route_poc)
**Migration**: `migrations/003_create_mv_campaign_browser.sql`
**Purpose**: Pre-aggregated campaign browser table for POC UI

### Dependencies on Pipeline Tables

| Pipeline Table | POC Usage | Status |
|----------------|-----------|--------|
| `mv_playout_15min` | Playout statistics (frames, playouts, dates) | ✅ Working |
| `mv_playout_15min_brands` | Brand information aggregation | ✅ Working |
| **`cache_campaign_reach_full`** | **Total Reach column** | ⚠️ **NOT in pipeline docs** |
| `cache_route_impacts_15min_by_demo` | Total Impacts column | ✅ Working |
| `cache_space_buyers` | Buyer name lookups | ✅ Working |
| `cache_space_brands` | Brand name lookups | ✅ Working |
| `cache_space_media_owners` | Media owner lookups | ✅ Working |

### Critical Coordination Needs

**1. Schema Change Notifications**
- If pipeline modifies cache table schemas, POC view will break
- Please notify POC team BEFORE changing:
  - Column names in cache tables
  - Data types or scaling (e.g., thousands storage)
  - Table names or migrations

**2. Refresh Schedule Coordination**
- **Pipeline refresh**: Daily at 2am UTC
- **POC refresh**: Should run AFTER pipeline refresh completes
- **Current**: POC manually refreshes `mv_campaign_browser` as needed
- **Future**: Automate POC refresh after pipeline completion

**3. Performance Monitoring**
- POC view refresh takes ~1-2 minutes for 838 campaigns
- Uses indexes on pipeline tables
- Monitor for concurrent refresh conflicts

**4. Data Quality Dependencies**
- POC campaign browser shows "-" for missing cache data
- Missing reach/impacts directly visible to users
- Backfill gaps affect POC user experience

### Unknown Table Ownership

**⚠️ CRITICAL**: `cache_campaign_reach_full` is used by POC but not documented in pipeline handover:

**Questions for Pipeline Team:**
1. Who created `cache_campaign_reach_full`?
2. Who maintains the backfill for this table?
3. Is it part of your daily refresh schedule?
4. Should it be added to your handover documentation?

**POC Assumption**: This table is maintained by pipeline team alongside `cache_campaign_reach_day` (daily reach). If this assumption is incorrect, we need to clarify ownership urgently.

### Migration File Reference

The POC materialized view is defined in:
```
/Users/ianwyatt/PycharmProjects/Route-Playout-Econometrics_POC/migrations/003_create_mv_campaign_browser.sql
```

This migration:
- LEFT JOINs to `cache_campaign_reach_full` (missing data → 0)
- LEFT JOINs to `cache_route_impacts_15min_by_demo` (missing data → 0)
- Aggregates brand information from `mv_playout_15min_brands`
- Creates indexes for campaign browser sorting

**Important**: Missing cache entries appear as zero/null in the view, displayed as "-" in POC UI.

---

**Next Steps**:
1. Pipeline team to investigate backfill process for missing campaigns
2. Pipeline team to confirm ownership of `cache_campaign_reach_full`
3. Coordinate refresh schedules to avoid conflicts
4. Add POC dependencies to pipeline documentation
