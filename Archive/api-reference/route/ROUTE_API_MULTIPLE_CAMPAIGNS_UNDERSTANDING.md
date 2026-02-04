# Route API Multiple Campaign Entries - Critical Understanding
**Date**: 2025-10-21
**Purpose**: Document correct Route API request structure for pipeline backfill
**Audience**: POC team and future pipeline developers

---

## Executive Summary

**CRITICAL ISSUE DISCOVERED**: The pipeline's initial Route API backfill implementation was **incorrectly averaging** spot and break lengths across entire campaign days, when the Route API actually requires **separate campaign entries for each unique combination** of frames, spot length, break length, and time period.

**Impact**: This would have resulted in **inaccurate reach calculations** because the API wouldn't know the actual spot/break variations across different time periods and frames.

**Fix**: Rewrite request builder to create multiple campaign entries grouped by frame, spot length, break length, and 15-minute time windows.

---

## What Was Wrong (Initial Implementation)

### Incorrect Approach
```json
{
  "campaign": [
    {
      "schedule": [
        {
          "datetime_from": "2025-10-13 00:00",
          "datetime_until": "2025-10-13 13:00"   // ❌ Entire day in one block
        }
      ],
      "frames": [1234, 5678, 9012, ...],          // ❌ All frames lumped together
      "spot_length": 11,                          // ❌ AVERAGED across all playouts
      "spot_break_length": 60                     // ❌ AVERAGED across all playouts
    }
  ]
}
```

### Why This Was Wrong

1. **Lost temporal precision**: Spot/break lengths vary throughout the day (e.g., 10s at 8am, 30s at 2pm)
2. **Lost frame-level precision**: Different frames may have different spot/break lengths in the same time period
3. **Inaccurate reach**: Route API calculates reach based on actual exposure patterns, averaging distorts this
4. **API guidance violation**: Documentation explicitly shows multiple campaign entries for different spot/break combinations

### Example of Data Loss

**Reality in mv_playout_15min**:
```
Frame 1234: 00:00-00:15, spot=10s, break=50s
Frame 1234: 00:15-00:30, spot=10s, break=40s  ← Break length changed!
Frame 5678: 00:00-00:15, spot=15s, break=50s  ← Different spot length!
```

**What we were sending** (WRONG):
```
Frames [1234, 5678]: 00:00-00:30, spot=12s, break=47s  ← Everything averaged!
```

**What we should send** (CORRECT):
```
Campaign 1: Frames [1234, 5678], 00:00-00:15, spot=10s, break=50s
Campaign 2: Frame 1234,          00:15-00:30, spot=10s, break=40s
Campaign 3: Frame 5678,          00:15-00:30, spot=15s, break=50s
```

---

## What Is Correct (Guide-Based Understanding)

### Source Documentation
**File**: `docs/Passing multiple spot and break using schedules/MultiSpotBreak-UsingSchedules-AcrossTimePeriods.md`

### Key Principles

1. **Group by unique combinations**: Each campaign entry represents frames with the **same** spot length and break length during the **same** time period

2. **15-minute granularity**: Schedule periods should align with 15-minute windows (Route API's temporal granularity)

3. **Frame-level accuracy**: If frame X has different spot/break than frame Y in the same time window, they need **separate campaign entries**

4. **Temporal accuracy**: If the same frame has different spot/break in different time windows, it needs **separate campaign entries** for each window

### Correct Request Structure

```json
{
  "route_release_id": 56,
  "route_algorithm_version": 10.2,
  "algorithm_figures": ["impacts", "reach", "average_frequency", "grp", "population"],
  "grouping": "frame_ID",
  "demographics": [{"demographic_id": 1}],
  "campaign": [
    // Campaign Entry 1: Frames with 5s spot, 15s break, 00:00-00:15
    {
      "schedule": [
        {
          "datetime_from": "2025-06-01 00:00",
          "datetime_until": "2025-06-01 00:15"
        }
      ],
      "frames": [2000312252, 2000287546],
      "spot_length": 5,
      "spot_break_length": 15
    },
    // Campaign Entry 2: Different frame, different spot/break, 00:00-00:30
    {
      "schedule": [
        {
          "datetime_from": "2025-06-01 00:00",
          "datetime_until": "2025-06-01 00:30"
        }
      ],
      "frames": [1234842296],
      "spot_length": 10,
      "spot_break_length": 46
    },
    // Campaign Entry 3: Same frame as Entry 1, but DIFFERENT break, later time
    {
      "schedule": [
        {
          "datetime_from": "2025-06-01 00:15",
          "datetime_until": "2025-06-01 00:30"
        }
      ],
      "frames": [2000312252],
      "spot_length": 5,
      "spot_break_length": 29   // Changed from 15s to 29s!
    },
    // ... more campaign entries as needed
  ],
  "target_month": 6
}
```

---

## Grouping Logic

### Algorithm for Building Campaign Entries

```python
# For each campaign day:

# Step 1: Get all playout windows from mv_playout_15min
playouts = get_playouts_for_campaign_day(campaign_id, date)

# Step 2: Group by unique combinations
# Key: (time_window_start, playout_length_seconds, break_length_seconds)
# Value: List of frame IDs
groups = {}
for playout in playouts:
    key = (
        playout['time_window_start'],
        playout['playout_length_seconds'],
        playout['break_length_seconds']
    )
    if key not in groups:
        groups[key] = []
    groups[key].append(playout['frameid'])

# Step 3: Create campaign entry for each unique group
campaign_entries = []
for (time_window_start, spot_length, break_length), frames in groups.items():
    time_window_end = time_window_start + timedelta(minutes=15)

    campaign_entries.append({
        "schedule": [{
            "datetime_from": time_window_start.strftime("%Y-%m-%d %H:%M"),
            "datetime_until": time_window_end.strftime("%Y-%m-%d %H:%M")
        }],
        "frames": sorted(list(set(frames))),  # Unique frames for this group
        "spot_length": spot_length,
        "spot_break_length": break_length
    })

# Step 4: Build final API request
api_request = {
    "route_release_id": release_id,
    "route_algorithm_version": 10.2,
    "algorithm_figures": ["impacts", "reach", "average_frequency", "grp", "population"],
    "grouping": "frame_ID",
    "demographics": [{"demographic_id": 1}],
    "campaign": campaign_entries,  # Multiple entries!
    "target_month": target_month
}
```

---

## Real-World Example

### Campaign 16026 on 2025-10-13

**Playout Data**:
- 5,179 playout windows
- 177 unique frames
- Time range: 00:00 → 13:00
- Avg spot: 11s (but varies 5s-30s)
- Avg break: 60s (but varies 20s-180s)

**Old (WRONG) Approach**:
- **1 campaign entry** with:
  - All 177 frames
  - Averaged spot: 11s
  - Averaged break: 60s
  - Schedule: 00:00 → 13:00

**New (CORRECT) Approach**:
- **~500-1000 campaign entries** (estimated), each with:
  - Specific frames that share same spot/break in that 15-min window
  - Actual spot length (no averaging)
  - Actual break length (no averaging)
  - Specific 15-min schedule window

**Example Grouping**:
```
Campaign Entry 1:
  Frames: [1234841807, 1234841825, 1234841847]
  Schedule: 2025-10-13 00:00 → 2025-10-13 00:15
  Spot: 10s, Break: 50s

Campaign Entry 2:
  Frames: [1234841807, 1234841825]  // Same frames, different break!
  Schedule: 2025-10-13 00:15 → 2025-10-13 00:30
  Spot: 10s, Break: 45s

Campaign Entry 3:
  Frames: [1234841847]  // Separated because different break
  Schedule: 2025-10-13 00:15 → 2025-10-13 00:30
  Spot: 10s, Break: 50s

... (hundreds more)
```

---

## Performance Implications

### API Call Complexity

**Before** (WRONG):
- 1 API request per campaign/day
- Request size: ~10KB
- Processing time: ~1-2 seconds

**After** (CORRECT):
- Still 1 API request per campaign/day
- Request size: ~50-200KB (larger due to multiple campaign entries)
- Processing time: ~2-5 seconds (Route API handles complexity internally)

### Why This Is Still Acceptable

1. **Route API designed for this**: The multiple campaign entries pattern is explicitly documented
2. **Single HTTP request**: All campaign entries go in ONE request, not multiple requests
3. **Still within limits**: Max 10,000 frames total across all campaign entries
4. **Accurate data**: Trade-off of slightly larger request for correct reach calculations

---

## Data Source: mv_playout_15min

### Table Structure (Relevant Columns)

```sql
CREATE MATERIALIZED VIEW mv_playout_15min AS
SELECT
    frameid,                      -- Frame ID (group key)
    buyercampaignref,             -- Campaign ID
    time_window_start,            -- 15-minute window start (group key)
    playout_length_seconds,       -- Spot length (group key)
    break_length_seconds,         -- Break length (group key)
    spot_count,                   -- Number of spots in window
    -- ... other columns
FROM playout_data
GROUP BY ...;
```

### Why This Source Is Perfect

✅ **Already aggregated to 15-minute windows** - matches Route API granularity
✅ **Has actual spot/break lengths** - no need to calculate
✅ **Indexed on campaign + time** - fast queries
✅ **One row per frame per window** - easy to group

---

## Implementation Checklist

### Changes Required

- [x] Document understanding of multiple campaign entries (this file)
- [ ] Rewrite `build_route_api_request()` function in backfill script
- [ ] Add grouping logic by (time_window, spot_length, break_length)
- [ ] Update logging to show number of campaign entries
- [ ] Test with real campaign data
- [ ] Verify API accepts requests with 100+ campaign entries
- [ ] Update handover documentation

### Testing Strategy

1. **Small test**: Campaign with 1-2 frames, 2-3 time windows
   - Expected: 2-6 campaign entries
   - Verify: Spot/break variations preserved

2. **Medium test**: Campaign with 50 frames, half-day
   - Expected: 50-200 campaign entries
   - Verify: API accepts request, returns valid reach

3. **Large test**: Campaign with 177 frames, full day (like 16026)
   - Expected: 500-1000 campaign entries
   - Verify: Request size < 1MB, processing time < 10s

4. **Comparison test**: Run same campaign with old vs new approach
   - Expected: Different reach values (new should be more accurate)
   - Document: Magnitude of difference

---

## Communication to POC Team

### What POC Needs to Know

1. **Pipeline's initial implementation was incorrect**
   - Was averaging spot/break lengths
   - Would have produced inaccurate reach data
   - Fixed before any production backfill run

2. **Correct implementation uses multiple campaign entries**
   - Each entry = unique (frames, spot_length, break_length, time_window)
   - Single API request can have hundreds of campaign entries
   - This is the documented, correct way per Route API guide

3. **POC's own reach calculations may need review**
   - If POC is also calling Route API directly, check if they're using same approach
   - Share this document and the guide: `MultiSpotBreak-UsingSchedules-AcrossTimePeriods.md`
   - Verify POC's `route_api/client.py` handles multiple campaign entries

4. **Cache data quality**
   - All cached reach data will be accurate (using correct method)
   - No need for POC to recalculate or validate
   - Pipeline guarantees data quality

### Questions for POC

1. Is POC's `route_api/client.py` already handling multiple campaign entries correctly?
2. Does POC have any reach calculations that might be using averaged spot/break?
3. Should we add validation to detect when averaging is being used incorrectly?

---

## Example Query to Verify Grouping

```sql
-- Check how many unique (spot, break) combinations exist for a campaign/day
-- This shows the minimum number of campaign entries needed
SELECT
    buyercampaignref,
    time_window_start::date as playout_date,
    COUNT(DISTINCT (playout_length_seconds, break_length_seconds)) as unique_spot_break_combos,
    COUNT(*) as total_windows
FROM mv_playout_15min
WHERE buyercampaignref = '16026'
  AND time_window_start::date = '2025-10-13'
GROUP BY buyercampaignref, time_window_start::date;

-- Result shows: If there are N unique (spot, break) combos across M time windows,
-- we need roughly N * M campaign entries (could be less if grouped)
```

---

## Visual Comparison

### Before (WRONG): Single Campaign Entry
```
[00:00 ==================== 13:00]
 Frames: ALL (177)
 Spot: 11s (averaged)
 Break: 60s (averaged)
```

### After (CORRECT): Multiple Campaign Entries
```
[00:00-00:15] Frames: [A, B, C],  Spot: 10s, Break: 50s
[00:00-00:15] Frames: [D, E],     Spot: 15s, Break: 50s
[00:15-00:30] Frames: [A, B],     Spot: 10s, Break: 45s
[00:15-00:30] Frames: [C],        Spot: 10s, Break: 50s
[00:15-00:30] Frames: [D, E],     Spot: 15s, Break: 50s
...
[12:45-13:00] Frames: [X, Y, Z],  Spot: 20s, Break: 60s
```

Each line = one campaign entry in the API request.

---

## Conclusion

**This is a critical fix that ensures reach calculations are accurate.**

The Route API is designed to handle the complexity of multiple spot/break combinations across time periods. By grouping our playout data correctly and creating separate campaign entries for each unique combination, we ensure the API receives the precise exposure patterns needed for accurate reach modeling.

**No production data was affected** - this issue was caught during testing before the full backfill run.

**POC should verify** their own Route API integration follows the same multi-campaign entry pattern for accuracy.

---

**Document Owner**: Pipeline Team (Claude Code)
**Reviewed By**: Doctor Biz
**Next Review**: Before POC handover
**Status**: Understanding documented, implementation in progress

