# Route API Optimization Summary

**Date:** October 26, 2025
**Optimization Type:** Minimal Payload for Econometric Analysis
**Impact:** Faster processing, cleaner responses

---

## The Optimization

### ❌ Before (Over-requesting)
```json
{
  "route_release_id": 56,
  "route_algorithm_version": "10.2",
  "option_split_reach": true,  // ❌ Not needed for impacts only
  "demographics": [
    {"demographic_custom": "ageband>0"}
  ],
  "algorithm_figures": ["all"],  // ❌ Returns all metrics unnecessarily
  "campaign": [...]
}
```

### ✅ After (Minimal - Recommended)
```json
{
  "route_release_id": 56,
  "route_algorithm_version": "10.2",
  "demographics": [
    {"demographic_custom": "ageband>0"}
  ],
  "algorithm_figures": ["impacts"],  // ✅ Only what we need
  "campaign": [...]
}
```

---

## Why This Matters

### For Econometric Analysis
- **Primary need**: Impacts (audience data)
- **Don't need**: Reach, GRP, frequency, cover, pedestrian/vehicular split
- **Result**: Faster processing, smaller responses

### Performance Benefits
- Reduced processing time (fewer metrics to calculate)
- Smaller JSON responses (less data transfer)
- Cleaner code (no unused parameters)
- Easier to parse and store

---

## What to Request

### Impacts Only (RECOMMENDED)
```json
"algorithm_figures": ["impacts"]
```

**Use when:**
- Doing econometric analysis
- Only need audience data
- Speed is important
- Caching results

### Specific Metrics
```json
"algorithm_figures": ["impacts", "reach", "grp"]
```

**Use when:**
- Need specific additional metrics
- Know exactly what you're analyzing
- Still want good performance

### All Metrics
```json
"algorithm_figures": ["all"]
```

**Use when:**
- Exploratory analysis
- Need full dataset
- Don't know which metrics you'll need
- Performance is less critical

---

## Parameters to Omit

### option_split_reach
**Omit unless you need pedestrian/vehicular split:**
- ❌ `"option_split_reach": true` - Not needed for total impacts
- ✅ Just omit the parameter entirely

### grouping
**Omit unless you need per-frame analysis:**
- ❌ `"grouping": "frame_id"` - Slower, more data
- ✅ Omit for campaign-level totals (~2x faster)

---

## Complete Minimal Example

```json
{
  "route_release_id": 56,
  "route_algorithm_version": "10.2",
  "demographics": [
    {"demographic_custom": "ageband>0"}
  ],
  "algorithm_figures": ["impacts"],
  "campaign": [
    {
      "schedule": [
        {
          "datetime_from": "2025-10-11 12:00",
          "datetime_until": "2025-10-11 13:00"
        }
      ],
      "frames": [2000312252, 2000287546],
      "spot_length": 10,
      "spot_break_length": 50
    }
  ],
  "target_month": 1
}
```

**This minimal payload:**
- Returns only impacts
- No grouping (campaign-level only)
- No pedestrian/vehicular split
- No unnecessary parameters
- **Fastest processing time**

---

## Testing Results

All tests passed with minimal payload:
- ✅ Simple demographics (impacts only): PASSED
- ✅ Multiple demographics WITH grouping (impacts only): PASSED
- ✅ Multiple demographics WITHOUT grouping (impacts only): PASSED

**Validation**: Minimal payload works correctly with Route API custom endpoint.

---

## Implementation Guide

### For Pipeline Caching
```python
def get_campaign_impacts(campaign_data):
    """Get impacts for campaign - minimal payload for fast caching."""
    payload = {
        "route_release_id": 56,
        "route_algorithm_version": "10.2",
        "demographics": [
            {"demographic_custom": "ageband>0"}
        ],
        "algorithm_figures": ["impacts"],  # Only impacts
        "campaign": build_campaign_payload(campaign_data),
        "target_month": 1
    }
    # No grouping for 2x faster processing
    # No option_split_reach for cleaner response
    return call_route_api(payload)
```

### For Detailed Analysis
```python
def get_campaign_detailed(campaign_data):
    """Get detailed metrics with per-frame breakdown."""
    payload = {
        "route_release_id": 56,
        "route_algorithm_version": "10.2",
        "demographics": [
            {"demographic_custom": "ageband>0"}
        ],
        "algorithm_figures": ["impacts", "reach", "grp"],  # Specific metrics
        "grouping": "frame_id",  # Per-frame analysis
        "campaign": build_campaign_payload(campaign_data),
        "target_month": 1
    }
    return call_route_api(payload)
```

---

## Best Practices

### 1. Only Request What You Need
- Don't use `"all"` by default
- Specify exact metrics required
- Consider whether you need grouping

### 2. Omit Unnecessary Parameters
- No `option_split_reach` unless analyzing pedestrian vs vehicular
- No `grouping` unless comparing individual frames
- Keep payload minimal

### 3. Use Appropriate Demographics
- Start with `"ageband>0"` (all adults) for general analysis
- Add specific demographics only when needed
- Remember: More demographics = longer processing

### 4. Consider Your Use Case
- **Caching**: Minimal payload, no grouping
- **Analysis**: Add metrics and grouping as needed
- **Exploration**: Can use "all" but be aware of performance impact

---

## Documentation Updated

Updated files to reflect optimization:
- ✅ `test_route_api_demographics.py` - Now uses impacts only
- ✅ `Claude/Documentation/route_api_demographics_testing.md` - Added optimization section
- ✅ `Claude/Handover/2025-10-26_route_api_demographics_testing.md` - Updated payload examples

---

## Summary

**Key Optimization**: Only request `["impacts"]` instead of `["all"]` for econometric work.

**Benefits:**
- Faster processing
- Smaller responses
- Cleaner code
- Better performance at scale

**Validated**: All tests passing with minimal payload.

**Recommended**: Use minimal payload for pipeline caching and standard econometric analysis.

---

**Created:** October 26, 2025
**Testing Status:** ✅ Complete
**Implementation:** Ready
