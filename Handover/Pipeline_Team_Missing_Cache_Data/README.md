# Pipeline Team Handover - Missing Cache Data Investigation

**Created**: November 15, 2025
**Purpose**: Handover package for pipeline team to investigate missing reach and impacts cache data

---

## Contents

1. **INVESTIGATION_SUMMARY.md** - Full investigation findings and recommendations
2. **REQUEST_AUTOMATE_MV_REFRESH.md** - Request to automate mv_campaign_browser refresh
3. **verification_queries.sql** - SQL queries to verify cache coverage and monitor progress
4. **campaigns_missing_reach_SMALL.csv** - 5 small campaigns missing reach (PRIORITY)
5. **campaigns_missing_reach_MEDIUM.csv** - 20 medium campaigns missing reach (PRIORITY)
6. **campaigns_missing_reach_LARGE.csv** - 21 large campaigns missing reach
7. **campaigns_missing_reach_VERY_LARGE.csv** - 2 very large campaigns (expected API limits)
8. **campaigns_missing_impacts.csv** - 16 campaigns missing impacts data

---

## Quick Summary

**Problem**: 48 campaigns (5.7%) missing from reach cache, 16 (1.9%) missing from impacts cache

**Critical Finding**: 52% of missing campaigns are small/medium sized and should have been cached successfully - this indicates a backfill process issue.

**User Impact**: Campaign browser displays "-" or zero values for Total Reach/Total Impacts on affected campaigns.

**Recommended Actions**:
1. ✅ **DONE**: Pipeline team fixed datetime_until bug and recached all data (Nov 16-17)
2. ✅ **DONE**: Pipeline team implemented `mv_campaign_browser` refresh automation (Nov 17) - see REQUEST_AUTOMATE_MV_REFRESH.md
3. **TODO**: Verify all 48 campaigns now have reach data after daily reach recache completes (Nov 18 AM expected)

**Pipeline Response**: See `/Users/ianwyatt/PycharmProjects/route-playout-pipeline/Claude/Handover/RESPONSE_TO_POC_MISSING_CACHE_INVESTIGATION.md` for complete details on bug fix and automation implementation.

---

## Files Explained

### Priority Files (Start Here)
- **campaigns_missing_reach_SMALL.csv**: 5 campaigns, 16-72K playouts - should NEVER fail
- **campaigns_missing_reach_MEDIUM.csv**: 20 campaigns, 1M-10M playouts - should succeed

These 25 campaigns are the priority - they should have been cached successfully.

### Secondary Files
- **campaigns_missing_reach_LARGE.csv**: May be API limits or backfill issues - needs investigation
- **campaigns_missing_reach_VERY_LARGE.csv**: Expected API limits (>50M playouts)
- **campaigns_missing_impacts.csv**: Impacts cache gaps (separate issue)

---

## Next Steps

1. **Read** `INVESTIGATION_SUMMARY.md` for full context
2. **Run** queries from `verification_queries.sql` to verify current state
3. **Review** priority CSV files (small + medium campaigns)
4. **Investigate** backfill process for September-October 2025 campaigns
5. **Report** findings back to POC UI team

---

## Contact

Questions about this handover? Check:
- Investigation summary for detailed findings
- Verification queries for current state
- POC UI repository for campaign browser code

---

**Status**: Ready for pipeline team investigation
