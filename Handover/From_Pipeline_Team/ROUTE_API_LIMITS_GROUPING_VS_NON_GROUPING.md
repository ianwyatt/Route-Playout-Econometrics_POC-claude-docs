# Route API Limits: Grouping vs Non-Grouping Calls

**Date**: 2025-10-21
**Purpose**: Clear documentation of Route API frame limits for POC development team
**Status**: ✅ PRODUCTION GUIDANCE

---

## Executive Summary

The Route API has **TWO different frame limits** depending on whether you request per-frame breakdowns (grouping) or aggregate campaign metrics (non-grouping).

| Call Type | Grouping Parameter | Frame Limit | Use Case |
|-----------|-------------------|-------------|----------|
| **With Grouping** | `"grouping": "frame"` | **10,000 unique frames** | Per-frame audience breakdown |
| **Without Grouping** | No grouping parameter | **NO LIMIT** | Campaign-level reach/GRP/frequency |

---

## Call Type 1: WITH Grouping (Per-Frame Breakdown)

### What It Does
Returns audience metrics **broken down by frame** - you get separate reach/GRP/frequency for each frame in your campaign.

### API Request Structure
```json
{
  "route_release_id": 56,
  "route_algorithm_version": 10.2,
  "target_month": 10,
  "algorithm_figures": ["impacts", "reach", "average_frequency", "grp"],
  "demographics": [{"demographic_id": 1}],
  "grouping": "frame",  // ← THIS ENABLES PER-FRAME BREAKDOWN
  "campaign": [
    {
      "schedule": [{"datetime_from": "2025-10-08 00:00", "datetime_until": "2025-10-08 23:59"}],
      "frames": [1234567890, 1234567891, 1234567892],
      "spot_length": 6,
      "spot_break_length": 54
    }
  ]
}
```

### API Response Structure
```json
{
  "results": [
    {
      "frame_id": 1234567890,
      "figures": {
        "reach": 150,
        "gross_rating_points": 2.5,
        "average_frequency": 1.8,
        "impacts": 270
      }
    },
    {
      "frame_id": 1234567891,
      "figures": {
        "reach": 200,
        "gross_rating_points": 3.2,
        "average_frequency": 2.1,
        "impacts": 420
      }
    },
    // ... one result object PER FRAME
  ]
}
```

### ⚠️ LIMIT: **10,000 Unique Frames Maximum**

If you include `"grouping": "frame"`, you can only request data for **up to 10,000 unique frames** across all campaign entries.

**Why the limit?**
Route API needs to calculate and return individual results for each frame. 10,000+ frames would create massive response payloads and slow processing.

### When to Use
- POC needs **per-frame performance comparison** (e.g., "Which frames drove the most reach?")
- Building **frame-level reports** or heatmaps
- Analyzing **individual frame efficiency**

### Example Use Case
```
User wants to see: "Show me the top 10 performing frames in campaign 18295"
→ Use WITH grouping
→ Get per-frame metrics
→ Sort by reach DESC
→ Display top 10
```

---

## Call Type 2: WITHOUT Grouping (Aggregate Campaign Metrics)

### What It Does
Returns **aggregate campaign-level metrics** - you get a single set of reach/GRP/frequency for the entire campaign across all frames.

### API Request Structure
```json
{
  "route_release_id": 56,
  "route_algorithm_version": 10.2,
  "target_month": 10,
  "algorithm_figures": ["impacts", "reach", "average_frequency", "grp", "population"],
  "demographics": [{"demographic_id": 1}],
  // NO "grouping" parameter
  "campaign": [
    {
      "schedule": [{"datetime_from": "2025-10-08 00:00", "datetime_until": "2025-10-08 00:15"}],
      "frames": [1234567890],
      "spot_length": 6,
      "spot_break_length": 54
    },
    {
      "schedule": [{"datetime_from": "2025-10-08 00:15", "datetime_until": "2025-10-08 00:30"}],
      "frames": [1234567890, 1234567891],
      "spot_length": 6,
      "spot_break_length": 54
    },
    // ... hundreds or thousands of campaign entries
  ]
}
```

### API Response Structure
```json
{
  "results": [
    {
      "figures": {
        "reach": 1523,             // Aggregate across ALL frames
        "gross_rating_points": 12.5,
        "average_frequency": 2.8,
        "impacts": 4263,
        "population": 34123
      }
    }
  ]
}
```

**Note**: Only **ONE result object** in the response, representing the entire campaign.

### ✅ LIMIT: **NO FRAME LIMIT**

Without grouping, Route API calculates aggregate metrics. You can include **any number of frames** across your campaign entries.

**Why no limit?**
Route only returns one aggregated result object, not per-frame breakdowns. Even a campaign with 50,000+ frames returns the same single result structure.

### When to Use
- POC needs **campaign-level KPIs** (e.g., "What was the total reach for campaign 18295 on Oct 8?")
- **Caching daily/weekly campaign metrics**
- **Quick campaign performance summaries**
- Large campaigns with hundreds or thousands of frames

### Example Use Case
```
User wants to see: "What was the total reach for campaign 18295 last week?"
→ Use WITHOUT grouping
→ Get single aggregate reach value
→ Display: "Campaign 18295 reached 15,234 people"
```

---

## Pipeline Cache Implementation

### Our Cache Strategy: Non-Grouping (No Limits!)

The pipeline's Route cache backfill uses **non-grouping calls** to populate:
- `cache_campaign_reach_day` (daily campaign metrics)
- `cache_campaign_reach_week` (weekly campaign metrics)
- `cache_campaign_reach_full` (full campaign period metrics)

**Why?**
1. ✅ **No frame limits** - can cache any campaign size
2. ✅ **Faster API calls** - single result object vs thousands
3. ✅ **Smaller response payloads** - less data transfer
4. ✅ **Matches POC use case** - users want campaign KPIs, not per-frame breakdowns

### Cache Backfill Example

```python
# Pipeline backfill script builds requests like this:
api_request = {
    "route_release_id": 56,
    "route_algorithm_version": 10.2,
    "algorithm_figures": ["impacts", "reach", "average_frequency", "grp", "population"],
    "demographics": [{"demographic_id": 1}],
    # NO GROUPING - aggregate metrics only
    "campaign": [
        # 5,000+ campaign entries for large campaigns
        # 50,000+ total frame references
        # NO PROBLEM - no frame limit!
    ],
    "target_month": 10
}

# Response:
{
    "results": [{
        "figures": {
            "reach": 15234,
            "gross_rating_points": 45.6,
            "average_frequency": 3.2,
            "impacts": 48750,
            "population": 334123
        }
    }]
}

# We cache these 4 metrics per campaign/day
```

---

## POC Development Guidance

### When POC Needs Per-Frame Breakdowns

If the POC application needs per-frame metrics (e.g., frame performance comparison dashboard):

**Option 1: Small Campaigns (< 10k frames)**
```python
# Direct API call with grouping
response = route_client.post("/rest/process/custom", {
    "grouping": "frame",
    "campaign": [...]  # Up to 10,000 unique frames
})

# Returns per-frame results
for result in response['results']:
    frame_id = result['frame_id']
    reach = result['figures']['reach']
    # Store in POC database or display
```

**Option 2: Large Campaigns (> 10k frames)**

**Split into batches:**
```python
# Campaign has 25,000 frames
frames = get_campaign_frames(campaign_id)

# Split into batches of 10,000
batches = chunk_list(frames, 10000)  # [batch1: 10k frames, batch2: 10k, batch3: 5k]

all_frame_metrics = []

for batch in batches:
    response = route_client.post("/rest/process/custom", {
        "grouping": "frame",
        "campaign": [{"frames": batch, ...}]
    })
    all_frame_metrics.extend(response['results'])

# Now you have per-frame metrics for all 25,000 frames
```

**Option 3: Use Cached Aggregate + Estimate**

For large campaigns, consider whether per-frame breakdown is necessary:
```python
# Get cached campaign total
campaign_metrics = db.query("SELECT * FROM cache_campaign_reach_day WHERE campaign_id = ?")
total_reach = campaign_metrics['reach']  # e.g., 50,000

# Estimate per-frame contribution based on spot count
frames = db.query("SELECT frameid, COUNT(*) as spots FROM mv_playout_15min WHERE campaign = ?")
total_spots = sum(f['spots'] for f in frames)

for frame in frames:
    # Proportional estimate (not exact, but fast)
    estimated_reach = total_reach * (frame['spots'] / total_spots)
```

---

## Common Pitfalls & Solutions

### ❌ Pitfall 1: Adding Grouping to Large Campaigns

```python
# BAD - This will fail if campaign has > 10k frames
request = {
    "grouping": "frame",  # ← Don't add this unless you need per-frame breakdown!
    "campaign": build_campaign_with_50k_frames()  # ❌ ERROR 221 or similar
}
```

**Solution**: Only use grouping when you actually need per-frame results.

### ❌ Pitfall 2: Assuming Non-Grouping Returns Per-Frame Data

```python
# BAD - Expecting per-frame results without grouping
response = route_client.post("/rest/process/custom", {
    # No grouping parameter
    "campaign": [...]
})

# This will FAIL - only ONE result object, not per-frame
for result in response['results']:
    frame_id = result['frame_id']  # ❌ Key doesn't exist!
```

**Solution**: Check what response structure you need first.

### ❌ Pitfall 3: Not Validating Frame Count Before Grouping Call

```python
# BAD - Blindly adding grouping without checking frame count
frames = get_campaign_frames(campaign_id)  # Returns 15,000 frames

request = {
    "grouping": "frame",
    "campaign": [{"frames": frames, ...}]  # ❌ Exceeds 10k limit
}
```

**Solution**: Always validate frame count before using grouping.

```python
# GOOD - Check first
frames = get_campaign_frames(campaign_id)

if len(frames) > 10000:
    # Use batching or non-grouping approach
    print(f"Campaign has {len(frames)} frames - too large for single grouping call")
    # Either batch or use aggregate metrics
else:
    # Safe to use grouping
    request = {"grouping": "frame", "campaign": [{"frames": frames, ...}]}
```

---

## Quick Reference Table

| Scenario | Use Grouping? | Frame Limit | Response Size |
|----------|---------------|-------------|---------------|
| Campaign-level KPI dashboard | ❌ No | None | 1 result object |
| Daily/weekly reach reports | ❌ No | None | 1 result object |
| Cache backfill (our pipeline) | ❌ No | None | 1 result object |
| "Top 10 performing frames" report | ✅ Yes | 10,000 | 1 result per frame |
| Frame performance heatmap | ✅ Yes | 10,000 | 1 result per frame |
| Small campaign (<10k frames) breakdown | ✅ Yes | 10,000 | 1 result per frame |
| Large campaign (>10k frames) breakdown | ✅ Yes (batched) | 10,000 per batch | Multiple API calls needed |

---

## Testing Commands

### Test Non-Grouping (No Limit)
```bash
# Cache a large campaign - no frame limit
python scripts/tools/backfill_route_cache.py \
  --campaign 19094 \
  --database local \
  --start-date 2025-10-06 \
  --end-date 2025-10-13

# Processes campaign with 21 frames (18 valid in R56)
# Uses non-grouping - no limit check
# Returns single aggregate reach/GRP/frequency
```

### Test Grouping (10k Limit)
```python
# Test per-frame breakdown (requires custom script or POC code)
from route_api.client import RouteAPIClient

client = RouteAPIClient()

# Small campaign - under 10k frames
response = client.post("/rest/process/custom", {
    "route_release_id": 56,
    "route_algorithm_version": 10.2,
    "grouping": "frame",  # Per-frame breakdown
    "campaign": [{
        "frames": [1234567890, 1234567891, 1234567892],  # 3 frames - OK
        "schedule": [{"datetime_from": "2025-10-08 00:00", "datetime_until": "2025-10-08 23:59"}],
        "spot_length": 6,
        "spot_break_length": 54
    }],
    "target_month": 10,
    "algorithm_figures": ["reach", "grp", "average_frequency", "impacts"],
    "demographics": [{"demographic_id": 1}]
})

# Returns 3 result objects (one per frame)
print(f"Results: {len(response['results'])}")  # 3
for result in response['results']:
    print(f"Frame {result['frame_id']}: reach={result['figures']['reach']}")
```

---

## Related Documentation

- **Route API Specification**: Contact Route team for full API docs
- **Pipeline Cache Implementation**: `scripts/tools/backfill_route_cache.py`
- **Route API Client**: `route_api/client.py`
- **Cache Table Schema**: `docs/Route_Cache_Pipeline_Handover/migrations/001_create_route_cache_tables.sql`

---

## Questions?

**For Pipeline Team**: ian@route.org.uk
**For Route API Issues**: Contact Route team
**For POC Integration**: See `Claude/POC_Handover/DATABASE_HANDOVER_FOR_POC.md`

---

**Document Version**: 1.0
**Last Updated**: 2025-10-21
**Status**: ✅ PRODUCTION GUIDANCE
**Audience**: POC Development Team
