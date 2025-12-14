# Pipeline Team Handover: Campaign Cache Limitations Fix

**Date:** 2025-11-26
**From:** Pipeline Team
**To:** POC UI Team
**Priority:** Action Required

---

## Summary

The `campaign_cache_limitations` table is now **self-healing**. You can trust the flags in this table - they will always accurately reflect whether a campaign can be cached.

**Action Required:** Remove any UI workarounds that check actual cached data instead of trusting the limitation flags.

---

## What Was the Problem?

Previously, 24 campaigns (13% of flagged campaigns) had stale limitation flags:
- Flags said `can_cache_full = false` with reasons like `no_valid_frames`
- But actual cached data showed these campaigns HAD valid reach/impacts
- This happened because the backfill code set flags on failure but never cleared them on success

---

## What Was Fixed

### Root Cause Fix (backfill_route_cache.py)

Added `_clear_campaign_limitation()` method that automatically clears stale flags when:
- Any caching operation succeeds (day, week, full, day-cumulative)
- Called immediately after successful API response and database insert

This means:
- Retries with `--recache` automatically clear old flags on success
- New Route releases that add frames will self-heal
- No manual intervention needed

### One-Time Data Fix

Applied SQL fix to both Local Mac and MS-01 databases:
- Created backup: `campaign_cache_limitations_backup_20241126`
- Cleared incorrect flags for 24 campaigns
- Verified: **0 remaining mismatches** on both databases

---

## Action Required: Remove UI Workaround

If the POC UI has code that does something like this:

```python
# DON'T DO THIS - checking actual data instead of trusting flags
if limitation_flag == 'no_valid_frames':
    # Check if there's actually cached data anyway
    actual_data = query_cache_table(campaign_id)
    if actual_data.reach > 0:
        # Ignore the flag, show data anyway
        ...
```

**Please remove this workaround.**

The correct approach is now:

```python
# DO THIS - trust the flags
if can_cache_full == False:
    show_limitation_message(limitation_reason)
else:
    show_cached_data()
```

---

## Why Remove the Workaround?

**"Fail visible, not fail silent"**

If limitation flags ever become stale again, it indicates a bug in the pipeline code. We want to see that bug, not mask it with UI workarounds.

- Workarounds hide bugs from detection
- Hidden bugs don't get fixed
- They accumulate and cause bigger problems later

By trusting the flags and removing workarounds, any future pipeline bugs will be immediately visible in the UI, prompting investigation and proper fixes.

---

## Technical Details

### Table: campaign_cache_limitations

| Column | Description |
|--------|-------------|
| `buyer_id` | Buyer ID (spacebuyerid) |
| `campaign_id` | Campaign ID (buyercampaignref) |
| `can_cache_full` | TRUE = can be cached, FALSE = has limitations |
| `full_cache_limitation_reason` | NULL, `no_valid_frames`, `frame_level_week_gaps`, or `json_exceeds_10mb` |

### When Limitations Are Set

- `no_valid_frames` - Campaign has no frames in current Route release
- `frame_level_week_gaps` - Rotation pattern detected (7+ day gaps)
- `json_exceeds_10mb` - API payload too large

### When Limitations Are Cleared

- Automatically when ANY granularity caching succeeds
- No manual intervention needed

---

## Verification

You can verify the fix is working with this query:

```sql
-- Should return 0 rows if everything is working correctly
SELECT
    ccl.campaign_id,
    ccl.full_cache_limitation_reason as flag,
    cb.total_reach_all_adults as reach
FROM campaign_cache_limitations ccl
JOIN mv_campaign_browser cb ON ccl.campaign_id = cb.campaign_id
WHERE (
    (ccl.full_cache_limitation_reason = 'no_valid_frames'
     AND (cb.total_reach_all_adults > 0 OR cb.total_impacts_all_adults > 0))
    OR
    (ccl.full_cache_limitation_reason = 'frame_level_week_gaps'
     AND cb.total_reach_all_adults > 0)
);
```

**Expected result:** 0 rows

If you ever see rows returned, contact the Pipeline Team - it indicates a bug in `backfill_route_cache.py`.

---

## Documentation

Full troubleshooting guide available at:
- `route-playout-pipeline/docs/08-troubleshooting/campaign-cache-limitations.md`

---

## Contact

Questions? Reach out to the Pipeline Team.

**Last Updated:** 2025-11-26
