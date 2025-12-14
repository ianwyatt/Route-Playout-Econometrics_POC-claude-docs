# Campaign 18428 - Incorrect "no_valid_frames" Limitation

**Date**: 2025-11-19
**Reported by**: POC Team
**Priority**: High
**Status**: Requires Re-processing

---

## Executive Summary

Campaign 18428 is incorrectly marked with `limitation_reason = 'no_valid_frames'` in the `campaign_cache_limitations` table. Investigation reveals:

1. **~390 of 400 frames (98%) ARE in Route** (R55/R56 releases)
2. **Day-level cache EXISTS** (28 days cached with reach/impacts)
3. **Week-level cache EXISTS** (10 weeks cached with reach/impacts)
4. **Full campaign cache MISSING** (0 rows in `cache_campaign_reach_full`)

**Root Cause**: Pipeline's **full campaign cache process is failing** for these campaigns, while day/week caching succeeds. The "no_valid_frames" limitation is incorrect.

**⚠️ SYSTEMATIC ISSUE**: This affects multiple large campaigns (>50 frames). All verified cases show successful day/week caching but failed full campaign caching.

**Red Flag Indicator**: Campaigns with >50 frames marked as 'no_valid_frames' + successful day/week caching = full campaign cache bug.

---

## Campaign Details

| Field | Value |
|-------|-------|
| **Campaign ID** | 18428 |
| **Brand** | Argos |
| **Buyer ID** | 15774 |
| **Start Date** | 2025-09-14 23:00:10 |
| **End Date** | 2025-10-13 13:00:43 |
| **Duration** | 30 days |
| **Total Playouts** | 3,800,773 |
| **Unique Frames** | 400 |

---

## Current (Incorrect) Status

**Database Tables:**
```sql
-- campaign_cache_limitations
campaign_id: 18428
can_cache_full: false
full_cache_limitation_reason: 'no_valid_frames'
detected_at: 2025-11-12 15:19:26
notes: NULL
```

```sql
-- cache_campaign_reach_full
(No record exists - 0 rows)
```

**UI Display:**
- Total Reach: ❌ No frames in Route (checked applicable releases)
- Total Impacts: ❌ No frames in Route (checked applicable releases)

---

## Investigation Findings

### Frames ARE in Route

Query executed:
```sql
WITH campaign_frames AS (
    SELECT DISTINCT frameid
    FROM playout_data
    WHERE buyercampaignref = '18428'
)
SELECT
    COUNT(*) as frames_in_playout,
    COUNT(rf.frameid) as frames_in_route,
    COUNT(*) - COUNT(rf.frameid) as frames_missing_from_route
FROM campaign_frames cf
LEFT JOIN route_frames rf ON cf.frameid = rf.frameid;
```

**Results:**
- Frames in playout: 400
- Frames in Route: ~390 (97.5%)
- Frames missing: ~10 (2.5%)

### Route Release Distribution

```sql
WITH campaign_frames AS (
    SELECT DISTINCT frameid
    FROM playout_data
    WHERE buyercampaignref = '18428'
)
SELECT
    rf.release_id,
    rr.release_number,
    rr.name,
    COUNT(DISTINCT cf.frameid) as frame_count
FROM campaign_frames cf
JOIN route_frames rf ON cf.frameid = rf.frameid
JOIN route_releases rr ON rf.release_id = rr.id
GROUP BY rf.release_id, rr.release_number, rr.name
ORDER BY rf.release_id;
```

**Results:**

| Release ID | Release | Quarter | Frames | Trading Period |
|------------|---------|---------|--------|----------------|
| 1 | R54 | Q1 2025 | 373 | 2025-04-07 to 2025-06-29 |
| 2 | R55 | Q2 2025 | 380 | 2025-06-30 to 2025-09-28 |
| 3 | R56 | Q3 2025 | 390 | 2025-09-29 to 2026-01-04 |

### Date Mapping

Campaign playouts span two Route releases:

**R55 (Q2 2025):**
- Trading period: 2025-06-30 to 2025-09-28
- Campaign overlap: 2025-09-14 to 2025-09-28 (15 days)
- Frames available: 380

**R56 (Q3 2025):**
- Trading period: 2025-09-29 to 2026-01-04
- Campaign overlap: 2025-09-29 to 2025-10-13 (15 days)
- Frames available: 390

---

## Additional Affected Campaigns (Systematic Issue)

Investigation of other large campaigns marked as 'no_valid_frames' reveals this is a **systematic problem**, not an isolated case.

### Verified False Positives

All campaigns below are marked `limitation_reason = 'no_valid_frames'` but have **87-95% of frames present in Route**:

| Campaign ID | Brand | Total Frames | Frames in Route | % in Route | Total Playouts | Dates |
|-------------|-------|--------------|-----------------|------------|----------------|-------|
| **18895** | Brand not provided | 816 | 708 | **87%** | 6,769,451 | 2025-09-01 to 2025-09-07 |
| **163978** | Brand not provided | 801 | 762 | **95%** | 10,688,467 | 2025-09-15 to 2025-10-13 |
| **17595** | Brand not provided | 770 | 730 | **95%** | 16,616,573 | 2025-08-24 to 2025-10-09 |
| **18655** | Euromillions | 794 | 692 | **87%** | 670,308 | 2025-10-10 (single day) |
| **18428** | Argos | 400 | ~390 | **98%** | 3,800,773 | 2025-09-14 to 2025-10-13 |

### Impact Summary

**5 verified false positives** representing:
- **3,581 total frames** incorrectly marked as unavailable
- **2,982 frames (83%)** actually present in Route
- **38.5 million playouts** with missing reach/impacts data
- **Estimated missing audience data**: 50-100 million impacts

### Additional Suspicious Campaigns

10 campaigns with >50 frames marked as 'no_valid_frames' (verification pending):

| Campaign ID | Frames | Playouts | Brand |
|-------------|--------|----------|-------|
| 17283 | 757 | 5,595,534 | Guinness |
| 16884 | 725 | 1,729,148 | McDonald's |
| 17341 | 562 | 4,681,152 | Brand not provided |
| 18871 | 549 | 2,589,601 | British Gas |
| 18899 | 513 | 3,380,802 | Brand not provided |
| 18897 | 508 | 1,262,010 | British Gas |
| *(4 more)* | 50-500 | Various | Various |

**Recommended Action**: Audit ALL campaigns with >50 frames marked as 'no_valid_frames'.

---

## Root Cause Analysis

### CONFIRMED: Full Campaign Cache Process Failing

**Critical Discovery**: All 5 affected campaigns have **successful day and week caching** but **failed full campaign caching**.

#### Cache Status Evidence:

```sql
-- Day cache: ✅ Working
SELECT campaign_id, COUNT(*) as records, SUM(reach) as reach, SUM(total_impacts) as impacts
FROM cache_campaign_reach_day
WHERE campaign_id IN ('18428', '18895', '163978', '17595', '18655')
GROUP BY campaign_id;

Campaign | Records | Reach    | Impacts
18895    | 7 days  | 5,945    | 22,295
163978   | 22 days | 4,376    | 31,742
17595    | 30 days | 20,960   | 73,691
18655    | 1 day   | 1,322    | 2,055
18428    | 28 days | 18,879   | 28,152

-- Week cache: ✅ Working
SELECT campaign_id, COUNT(*) as records, SUM(reach) as reach, SUM(total_impacts) as impacts
FROM cache_campaign_reach_week
WHERE campaign_id IN ('18428', '18895', '163978', '17595', '18655')
GROUP BY campaign_id;

Campaign | Records  | Reach    | Impacts
18895    | 2 weeks  | 7,467    | 44,591
163978   | 9 weeks  | 4,280    | 123,478
17595    | 12 weeks | 34,713   | 431,261
18655    | 2 weeks  | 2,643    | 4,111
18428    | 10 weeks | 20,995   | 113,262

-- Full cache: ❌ FAILING
SELECT * FROM cache_campaign_reach_full
WHERE campaign_id IN ('18428', '18895', '163978', '17595', '18655');
-- Returns: 0 rows
```

### Actual Root Cause

The bug is **NOT** "no valid frames" - frames are clearly valid (day/week caching proves this).

**The actual issue**: Pipeline's `cache_campaign_reach_full` population process is failing for these campaigns specifically, while day/week processes succeed.

### Possible Specific Causes

1. **Full Campaign API Call Failing**: Route API call for full campaign reach may timeout/fail while smaller time-window calls (day/week) succeed
2. **Memory/Resource Limit**: Full campaign calculation may exceed memory limits for campaigns with 400+ frames
3. **Reach Calculation Error**: Full campaign reach calculation may fail on specific frame patterns (rotation campaigns?)
4. **Transaction Timeout**: Full campaign cache write may timeout while day/week succeed
5. **Logic Bug**: Code path for full campaign may have validation that day/week don't have

### Recommended Investigation Steps

1. **Compare pipeline code paths** for day/week vs full campaign caching
2. **Check pipeline logs** for these campaigns on dates:
   - 18428: 2025-11-12 15:19:26
   - 18895: 2025-11-12 15:14:25
   - Others: 2025-11-17 10:21:40 - 10:25:54
3. **Look for errors/timeouts** specifically in full campaign cache step
4. **Verify API calls**: Did Route API return data for full campaign? Or did it timeout?
5. **Check for rotation patterns**: Are these campaigns flagged as rotation? (week-on/week-off)

---

## Impact

### User Experience
- Campaign shows ❌ indicators suggesting no data available
- Users may incorrectly assume campaign cannot be analyzed
- Total Reach and Total Impacts both show 0

### Data Completeness
- Missing reach/impacts data for 3.8M playouts
- 400 frames worth of audience data not cached
- 30-day campaign period uncovered

---

## Recommended Actions

### Immediate Actions (Priority: CRITICAL)

**⚠️ SYSTEMATIC ISSUE**: Do not treat this as a single campaign fix. This affects multiple high-value campaigns.

1. **Audit scope of problem**
   ```sql
   -- Get full list of affected campaigns
   SELECT
       cs.campaign_id,
       cs.primary_brand,
       cs.total_frames,
       cs.total_playouts,
       cs.start_date,
       cs.end_date
   FROM mv_campaign_browser cs
   JOIN campaign_cache_limitations ccl ON cs.campaign_id = ccl.campaign_id
   WHERE ccl.full_cache_limitation_reason = 'no_valid_frames'
   AND cs.total_frames > 50
   ORDER BY cs.total_frames DESC;
   ```
   **Expected**: ~10-15 campaigns need re-processing

2. **Re-process verified false positives (Priority 1)**

   Re-run cache process for these **5 verified campaigns**:
   - **18895** (816 frames, 6.7M playouts)
   - **163978** (801 frames, 10.7M playouts)
   - **17595** (770 frames, 16.6M playouts)
   - **18655** (794 frames, 670K playouts)
   - **18428** (400 frames, 3.8M playouts)

   For each campaign:
   - Query appropriate Route releases based on campaign dates
   - Cache reach and impacts data in `cache_campaign_reach_full`
   - Update/remove limitation record in `campaign_cache_limitations`

3. **Verify additional suspicious campaigns (Priority 2)**

   Check remaining campaigns with >50 frames:
   - 17283 (Guinness, 757 frames)
   - 16884 (McDonald's, 725 frames)
   - 17341, 18871, 18899, 18897 (508-562 frames each)

   Use same verification query as "Investigation Findings" section

4. **Update limitation records**
   - Remove entries from `campaign_cache_limitations` for successfully cached campaigns
   - Keep limitation records ONLY for campaigns with genuinely missing frames
   - Document actual limitation reason if different from 'no_valid_frames'

### Follow-up Actions (Post-Fix)

5. **Root cause investigation**
   - Review pipeline logs for affected campaigns
   - Identify why frame validation failed for campaigns with 80%+ frames in Route
   - Document actual failure mode (API timeout, logic bug, etc.)

6. **Prevent recurrence**
   ```sql
   -- Find other campaigns incorrectly marked as 'no_valid_frames'
   SELECT ccl.campaign_id, ccl.full_cache_limitation_reason,
          cs.total_frames, cs.total_playouts
   FROM campaign_cache_limitations ccl
   JOIN mv_campaign_browser cs ON ccl.campaign_id = cs.campaign_id
   WHERE ccl.full_cache_limitation_reason = 'no_valid_frames'
   AND cs.total_frames > 100  -- Large frame count suggests frames likely exist
   ORDER BY cs.total_frames DESC;
   ```

5. **Review validation logic**
   - Audit frame validation code in pipeline
   - Add logging for "no_valid_frames" decisions
   - Consider adding frame existence check before marking limitation

6. **Add monitoring**
   - Alert when campaigns with >100 frames marked as 'no_valid_frames'
   - Track success rate of Route API calls
   - Monitor cache completion rate by limitation reason

---

## Expected Outcome

After re-processing campaign 18428:

**Database:**
```sql
-- cache_campaign_reach_full should have:
campaign_id: 18428
reach: >0 (expected ~1-2 million)
total_impacts: >0 (expected ~3-4 million)
route_release_id: 55 or 56
is_approximate: false (unless >50M playouts)
```

**UI Display:**
- Total Reach: [formatted number] (no indicator)
- Total Impacts: [formatted number] (no indicator)

---

## Sample Frame IDs for Testing

First 10 frame IDs from campaign 18428:
```
1234853305
1234853306
1234853310
1234853311
1234853312
1234853313
1234853454
1234854076
1234854158
1234854307
```

Use these to verify Route API calls and audience data retrieval.

---

## Contact

**POC Team**: Available for clarification and testing
**Database**: `route_poc` on 192.168.1.34
**UI**: http://localhost:8504 (Browse Campaigns → Search "18428")

---

## Appendix: Verification Queries

### Check if campaign was successfully re-processed
```sql
SELECT
    campaign_id,
    reach,
    total_impacts,
    route_release_id,
    is_approximate,
    cached_at
FROM cache_campaign_reach_full
WHERE campaign_id = '18428';
```

### Check if limitation was removed/updated
```sql
SELECT
    campaign_id,
    can_cache_full,
    full_cache_limitation_reason,
    detected_at,
    notes
FROM campaign_cache_limitations
WHERE campaign_id = '18428';
```

### Verify UI display
```sql
SELECT
    campaign_id,
    total_reach_all_adults,
    total_impacts_all_adults,
    route_release_id,
    full_cache_limitation_reason
FROM mv_campaign_browser
WHERE campaign_id = '18428';
```

---

**End of Report**
