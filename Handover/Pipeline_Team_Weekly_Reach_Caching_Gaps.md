# Request: Weekly Reach Caching Gaps - Pipeline Team Action Required

**Date**: 2025-11-21
**From**: POC Team (UI Development)
**To**: Pipeline Team (Data Ingestion & Caching)
**Priority**: HIGH
**Status**: New Request

---

## Summary

During review of the campaign browser, we identified several data inconsistencies related to weekly reach caching. The most significant issue is that **only 257 out of 838 campaigns have weekly reach data cached**, leaving 504 campaigns (60%) with total reach but no weekly reach data.

---

## Key Statistics

| Metric | Count |
|--------|-------|
| Total Campaigns | 838 |
| With Total Reach | 631 |
| With Weekly Reach | 239 |
| **Has Total but NO Weekly** | **504** |
| Rotation Campaigns | 162 |
| Rotation WITH Weekly Reach | 106 |
| Rotation WITHOUT Weekly Reach | 56 |
| 'No Valid Frames' WITH Weekly Reach | 11 |
| Truly Uncached (no data at all) | 3 |

---

## Issues Identified

### Issue 1: Missing Weekly Reach for Most Campaigns (HIGH PRIORITY)

**Problem**: 504 campaigns have total reach but zero avg weekly reach.

**Evidence**: Campaigns with 21-29 days active (plenty of full weeks) have 0 records in `cache_campaign_reach_week`:

| campaign_id | brand | days_active | total_reach | avg_weekly_reach | weekly_cache_records |
|-------------|-------|-------------|-------------|------------------|---------------------|
| 2025-07-15:KGG7V | Brand not provided | 29 | 473.7 | 0 | 0 |
| 18037 | Lidl | 29 | 94.1 | 0 | 0 |
| 17875 | Brand not provided | 29 | 348.6 | 0 | 0 |
| 2025-07-14:BQJ2S | Habitat Retail | 28 | 1797.9 | 0 | 0 |
| 18919 | Uber Eats | 23 | 3039.4 | 0 | 0 |

**Root Cause**: Weekly reach caching process has only been run for a subset of campaigns (257 out of 838).

**Fix Required**: Run weekly reach caching for ALL campaigns with 7+ days active.

---

### Issue 2: Rotation Campaigns Missing Weekly Reach (HIGH PRIORITY)

**Problem**: 56 rotation campaigns (`frame_level_week_gaps`) have no weekly reach data.

**Why This Matters**: The user correctly pointed out that even though rotation campaigns cannot have **total campaign reach** calculated (due to >1 week gaps between frame playouts), they **CAN** have weekly reach calculated because:
- Weekly reach limits analysis to 7 days
- Within any 7-day period, the "week+ gap" limitation doesn't apply
- 106 rotation campaigns already have weekly reach - proving it works

**Evidence**: Rotation campaigns that DO have weekly reach:

| campaign_id | brand | days_active | impacts | avg_weekly_reach | cached_full_weeks |
|-------------|-------|-------------|---------|------------------|-------------------|
| 17498 | Brand not provided | 37 | 227,673 | 7,292 | 3 |
| 17950 | H&M | 22 | 170,941 | 2,953 | 3 |
| 17827 | Brand not provided | 37 | 150,005 | 5,974 | 5 |
| 18295 | Uber Eats | 45 | 103,959 | 8,335 | 6 |

**Fix Required**: Run weekly reach caching for ALL rotation campaigns (56 remaining).

---

### Issue 3: 'no_valid_frames' Label Inconsistency (MEDIUM PRIORITY)

**Problem**: 11 campaigns are marked as `no_valid_frames` BUT have avg_weekly_reach > 0.

**Evidence**:

| campaign_id | brand | total_reach | avg_weekly_reach | limitation_reason |
|-------------|-------|-------------|------------------|-------------------|
| 17341 | Brand not provided | 0 | 8,380 | no_valid_frames |
| 18895 | Brand not provided | 0 | 3,733 | no_valid_frames |
| 16884 | McDonald's | 0 | 2,938 | no_valid_frames |
| 16703 | Lipton | 0 | 2,817 | no_valid_frames |
| 17595 | Brand not provided | 0 | 2,539 | no_valid_frames |

**Explanation**: The `no_valid_frames` label applies to **full campaign reach** (which is 0), but these campaigns DO have valid weekly reach data. The UI shows this flag next to the weekly reach column, which is confusing.

**Options**:
1. **Pipeline Fix**: Change limitation_reason to `no_full_reach_frames_available` to be more specific
2. **POC Fix**: UI can hide/modify the indicator when weekly reach exists
3. **Document Only**: Note that the flag only applies to total reach, not weekly

**Recommendation**: Option 1 (rename) + Option 2 (UI update) for clarity.

---

### Issue 4: Truly Uncached Campaigns (LOW PRIORITY)

**Problem**: 3 campaigns have no data at all (no reach, no impacts, no limitation reason).

**Evidence**:

| campaign_id | brand |
|-------------|-------|
| 17340 - GRPO00034483 | Brand not provided |
| 17341 - GRPO00034318/19/GRPO00034398 | Brand not provided |
| ATLAS1617-4 | Great British Racing |

**Note**: These campaign IDs contain unusual characters (spaces, dashes, slashes). This may indicate malformed campaign references or test data.

**Fix Required**: Investigate whether these are valid campaigns or should be excluded.

---

## Requested Actions (Priority Order)

### 1. Run Weekly Reach Caching for All Campaigns

**Script**: The weekly reach caching script should be run for:
- All campaigns with `days_active >= 7` that don't have weekly reach cached
- This includes both regular campaigns AND rotation campaigns

**Query to identify campaigns needing weekly caching**:
```sql
SELECT
    mb.campaign_id,
    mb.days_active,
    mb.total_reach_all_adults,
    mb.full_cache_limitation_reason
FROM mv_campaign_browser mb
WHERE mb.days_active >= 7
  AND (mb.avg_weekly_reach_all_adults IS NULL OR mb.avg_weekly_reach_all_adults = 0)
ORDER BY mb.total_impacts_all_adults DESC;
```

**Expected Result**: ~450-500 campaigns should have weekly reach cached.

### 2. Update Limitation Reason Labels (Optional)

If feasible, consider renaming `no_valid_frames` to `no_full_reach_frames_available` to clarify that this applies to full campaign reach only, not weekly reach.

### 3. Investigate Malformed Campaign IDs

Check if campaigns with unusual IDs (containing spaces, dashes, slashes) are valid or should be excluded from reporting.

---

## Verification Queries

### After Weekly Caching is Complete:

```sql
-- Verify weekly reach coverage
SELECT
    COUNT(*) as total_campaigns,
    COUNT(*) FILTER (WHERE avg_weekly_reach_all_adults > 0) as has_weekly_reach,
    COUNT(*) FILTER (WHERE days_active >= 7 AND (avg_weekly_reach_all_adults IS NULL OR avg_weekly_reach_all_adults = 0)) as missing_weekly_but_eligible
FROM mv_campaign_browser;

-- Expected: missing_weekly_but_eligible should be close to 0
```

---

## Impact on POC

Once weekly reach caching is complete:
- Campaign browser will show more accurate avg weekly reach data
- Rotation campaigns will have meaningful reach metrics (weekly instead of 0 total)
- Users can better compare campaign performance

---

## Contact

**POC Team**: Available for clarification and testing

**Database**: `route_poc` on 192.168.1.34:5432 (ms01)

---

## Issue 5: Additional Weekly Metrics Required (MEDIUM PRIORITY)

**Date Added**: 2025-11-21

**Problem**: The POC UI needs additional weekly metrics beyond just `avg_weekly_reach`. Since rotation campaigns can only report weekly data (not total campaign data), we need the full set of weekly metrics for proper comparison.

**Requested New Columns for `cache_campaign_reach_week`**:

| Column | Description | Calculation |
|--------|-------------|-------------|
| `avg_weekly_impacts` | Average weekly impacts | AVG(impacts) from full 7-day weeks |
| `avg_weekly_grp` | Average weekly GRPs | AVG(grp) from full 7-day weeks |
| `avg_weekly_frequency` | Average weekly frequency | AVG(frequency) from full 7-day weeks |
| `avg_weekly_cover_pct` | Average weekly cover % | (avg_weekly_reach × 1000 / universe) × 100 |

**Why This Matters**:
- Rotation campaigns cannot have total reach/impacts/GRPs calculated
- Weekly metrics are the ONLY way to measure rotation campaign performance
- For fair comparison, all campaigns should show both total AND weekly metrics
- UI will group weekly columns together for easy comparison

**Implementation**:
1. Ensure `cache_campaign_reach_week` stores all required metrics (impacts, grp, frequency) per week
2. Update `mv_campaign_browser` to calculate averages from full 7-day weeks
3. POC team will update UI once data is available

**Priority**: After Issue 1 & 2 (weekly reach caching) are complete

---

**End of Request**
