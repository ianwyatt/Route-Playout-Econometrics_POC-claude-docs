# Route API Demographics Testing - Summary

**Date:** October 26, 2025
**Testing Type:** Route API Custom Endpoint with Multiple Demographics
**Result:** All Tests Passed ✅

---

## Overview

Successfully validated the Route API `/rest/process/custom` endpoint with multiple demographics, testing both with and without frame grouping. This establishes the correct syntax and parameters for retrieving audience data with demographic segmentation.

---

## Key Findings

### 1. Endpoint Discovery

**CRITICAL CORRECTION**: Must use the **CUSTOM endpoint**, not the playout endpoint.

- ❌ **Wrong**: `https://route.mediatelapi.co.uk/rest/process/playout`
- ✅ **Correct**: `https://route.mediatelapi.co.uk/rest/process/custom`

### 2. Demographics Syntax

Demographics must be an **array of objects** with `"demographic_custom"` key:

```json
"demographics": [
  {
    "demographic_custom": "social_grade=1 or social_grade=2"  // ABC1 (A+B)
  },
  {
    "demographic_custom": "ageband>0 AND social_grade<=3"  // All ages, ABC1
  }
]
```

**NOT** an array of strings: ~~`["ageband=15-34"]`~~

### 3. Algorithm Figures

Use `"all"` to get all available metrics:

```json
"algorithm_figures": ["all"]
```

Available metrics when specified individually:
- "cover", "average_frequency", "reach", "impacts", "grp", "population", "sample_size"

### 4. Optimize Algorithm Figures

**Only request metrics you need for better performance:**
- For impacts only: `"algorithm_figures": ["impacts"]`
- For multiple specific metrics: `"algorithm_figures": ["impacts", "reach", "grp"]`
- For everything: `"algorithm_figures": ["all"]`

**Best Practice**: Don't request "all" if you only need impacts. Unnecessary data slows processing.

### 5. Authentication

Requires **dual authentication**:
1. HTTP Basic Auth (username + password)
2. X-Api-Key header

```python
auth = (username, password)  # Basic auth
headers = {
    'Content-Type': 'application/json',
    'X-Api-Key': api_key  # Required!
}
```

### 6. Timeout Requirements

Large campaigns require longer timeouts:
- **Recommended**: 300 seconds (5 minutes)
- Small test campaigns: ~30-60 seconds

### 7. route_release_id Type

**Must be integer, not string**:
- ✅ `"route_release_id": 56`
- ❌ ~~`"route_release_id": "56"`~~

### 8. option_split_reach Parameter

**Only include if you need pedestrian/vehicular split:**
- For impacts only: **Omit this parameter** (not needed)
- For reach analysis: Include `"option_split_reach": true`

**Best Practice**: Don't include unnecessary parameters - keeps payload clean and processing efficient.

---

## Test Results

### Test Configuration

**Test Frames**: 2000312252, 2000287546
**Test Period**: 2025-10-11 12:00 to 13:00 (1 hour)
**Route Release**: R56 (Q3 2025)
**Demographics Tested**:
1. `social_grade=1 or social_grade=2` (ABC1: A+B)
2. `ageband>0 AND social_grade<=3` (All ages, ABC1: A+B+C1)

### Test 1: Simple Demographics (Single Frame)
- **Status**: ✅ PASSED
- **Demographic**: `ageband>0` (all ages)
- **Frames**: 1 frame (2000312252)
- **Duration**: 15 minutes
- **Result**: 200 OK

### Test 2: Multiple Demographics WITH Grouping
- **Status**: ✅ PASSED
- **Grouping**: `"grouping": "frame_id"`
- **Demographics**: 2 demographics
- **Frames**: 2 frames
- **Duration**: 1 hour
- **Processing Time**: 56 seconds
- **Results Returned**: 6 objects
  - 2 "total" (campaign-level per demographic)
  - 4 "grouping" (2 demographics × 2 frames)

### Test 3: Multiple Demographics WITHOUT Grouping
- **Status**: ✅ PASSED
- **Grouping**: None (parameter omitted)
- **Demographics**: 2 demographics
- **Frames**: 2 frames
- **Duration**: 1 hour
- **Processing Time**: 29 seconds (nearly 2x faster!)
- **Results Returned**: 2 objects
  - 2 "total" (campaign-level per demographic only)

---

## Response Structure Analysis

### WITH Grouping (`"grouping": "frame_id"`)

```json
{
  "route_release_id": 56,
  "route_release_revision": 1,
  "route_algorithm_version": 10.2,
  "results": [
    {
      "description": "total",
      "demographic": "Custom (social_grade=1 or social_grade=2)",
      "granular_audience": "All Adults (1)",
      "target_month": 1,
      "figures": {
        "population": "14063.958984083",
        "sample_size": "7618",
        "impacts": "0.3152623061",
        "impacts_pedestrian": "0.0186818433",
        "impacts_vehicular": "0.2965804629",
        "gross_rating_points": "0.0022416327",
        "reach": "0.2737335987",
        "reach_pedestrian": "0.052572669",
        "reach_vehicular": "0.2236570325",
        "cover": "0.0019463481",
        "average_frequency": "1.1517121305",
        // ... more metrics
      },
      "metrics": {
        "total_frames": 2,
        "total_dynamic_frames": 2,
        "total_contacts": 25,
        "total_actual_contacts": 16,
        "total_respondents": 11,
        "total_actual_respondents": 2
      }
    },
    // ... another "total" for demographic 2
    {
      "description": "grouping",
      "demographic": "Custom (social_grade=1 or social_grade=2)",
      "granular_audience": "All Adults (1)",
      "target_month": 1,
      "frame_id": "2000312252",  // ⭐ Frame-specific result
      "figures": {
        "impacts": "0.0110651062",
        "gross_rating_points": "0.000078677",
        "reach": "n/a",  // Note: reach not available at frame level
        // ... more metrics
      },
      "metrics": {
        "total_frames": 1,
        "total_dynamic_frames": 1,
        "total_contacts": 4
      }
    }
    // ... 3 more "grouping" objects (frame 2 × demographic 1, both frames × demographic 2)
  ],
  "total_processing_time": 56,
  "processed_datetime": "2025-10-26 13:21:23"
}
```

**Key Points**:
- Returns both "total" (campaign-level) AND "grouping" (per-frame) results
- Each frame gets separate results for each demographic
- Some metrics (reach, cover) marked as "n/a" at frame level
- Total of 6 result objects for 2 demographics × 2 frames

### WITHOUT Grouping (parameter omitted)

```json
{
  "route_release_id": 56,
  "route_release_revision": 1,
  "route_algorithm_version": 10.2,
  "results": [
    {
      "description": "total",
      "demographic": "Custom (social_grade=1 or social_grade=2)",
      "granular_audience": "All Adults (1)",
      "target_month": 1,
      "figures": {
        "population": "14063.958984083",
        "impacts": "0.3152623061",
        "gross_rating_points": "0.0022416327",
        "reach": "0.2737335987",
        "cover": "0.0019463481",
        "average_frequency": "1.1517121305"
        // ... all metrics available
      },
      "metrics": {
        "total_frames": 2,
        "total_contacts": 25
      }
    }
    // ... only one more "total" object for demographic 2
  ],
  "total_processing_time": 29,
  "processed_datetime": "2025-10-26 13:21:23"
}
```

**Key Points**:
- Returns only "total" (campaign-level) results
- No per-frame breakdown
- All metrics (reach, cover, frequency) available
- **Nearly 2x faster** (29s vs 56s)
- Total of 2 result objects for 2 demographics

---

## Performance Comparison

| Aspect | WITH Grouping | WITHOUT Grouping |
|--------|--------------|------------------|
| **Processing Time** | 56 seconds | 29 seconds |
| **Speed** | Baseline | **~2x faster** |
| **Results Objects** | 6 (2 totals + 4 groupings) | 2 (totals only) |
| **Frame Details** | ✅ Per-frame metrics | ❌ Campaign-level only |
| **Reach/Cover** | ⚠️ "n/a" at frame level | ✅ Available |
| **Use Case** | Per-frame analysis | Campaign aggregation |

---

## Figures Returned (using `"all"`)

### Core Metrics
- **population** - Target population size
- **sample_size** - Survey sample size
- **impacts** - Total audience impacts (thousands)
  - impacts_pedestrian
  - impacts_vehicular
- **gross_rating_points** (GRP) - Percentage of population reached
- **reach** - Unique audience reached (thousands)
  - reach_pedestrian
  - reach_vehicular
- **cover** - Population coverage percentage
- **average_frequency** - Average exposures per person reached

### Benchmarking Metrics
- **benchmarking_factor** - Campaign vs benchmark performance
- **benchmark_reach** - Expected reach for benchmark
- **benchmark_cover** - Expected cover for benchmark
- **benchmark_cover_implied** - Implied benchmark coverage
- **probability_14d_reach** - 14-day reach probability
- **rag_status** - Red/Amber/Green status indicator

### Sample Metrics
- **total_frames** - Number of frames in campaign
- **total_dynamic_frames** - Number of digital frames
- **total_contacts** - Total survey contacts
- **total_actual_contacts** - Actual contacts used
- **total_respondents** - Total respondents
- **total_actual_respondents** - Actual respondents used

---

## Recommendations

### For Econometric Analysis (Typical Use Case)

**Minimal Payload - Fast & Efficient:**
```json
{
  "route_release_id": 56,
  "route_algorithm_version": "10.2",
  "demographics": [{"demographic_custom": "ageband>0"}],
  "algorithm_figures": ["impacts"],  // ✅ Only what you need
  "campaign": [...],
  "target_month": 1
}
```

**Benefits:**
- Fastest processing time
- Only returns impacts (audience data)
- No unnecessary metrics
- Clean, minimal response
- **Recommended for pipeline caching**

### Use Grouping When:
- Need per-frame analysis
- Analyzing individual frame performance
- Comparing frames within campaign
- Building detailed frame-level reports
- OK with longer processing times

### Use No Grouping When:
- Only need campaign-level totals
- Speed is priority (~2x faster)
- Exporting aggregated campaign metrics
- Large campaigns with many frames
- Need reach/cover/frequency (available at campaign level)

### Request Only Needed Metrics:
- **Impacts only**: `["impacts"]` - Fastest
- **Impacts + reach**: `["impacts", "reach"]` - Targeted
- **Everything**: `["all"]` - Slowest, use sparingly

---

## Test Files Created

| File | Purpose | Size |
|------|---------|------|
| `test_route_api_demographics.py` | Test script for custom endpoint | 226 lines |
| `route_response_with_grouping_*.json` | Full API response with grouping | 210 lines |
| `route_response_no_grouping_*.json` | Full API response without grouping | 75 lines |
| `test_demographics_custom_endpoint.log` | Test execution log | Full output |

---

## Correct Payload Examples

### Minimal Payload (Impacts Only)
**Recommended for econometric analysis - only request what you need:**

```json
{
  "route_release_id": 56,
  "route_algorithm_version": "10.2",
  "demographics": [
    {
      "demographic_custom": "ageband>0"
    }
  ],
  "algorithm_figures": ["impacts"],  // Only request impacts - faster!
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

### Full Payload (All Metrics)
**Use when you need reach, GRP, frequency, etc.:**

```json
{
  "route_release_id": 56,
  "route_algorithm_version": "10.2",
  "option_split_reach": true,  // Only if you need pedestrian/vehicular split
  "demographics": [
    {
      "demographic_custom": "social_grade=1 or social_grade=2"
    },
    {
      "demographic_custom": "ageband>0 AND social_grade<=3"
    }
  ],
  "algorithm_figures": ["all"],  // All metrics
  "grouping": "frame_id",  // Optional: omit for campaign-level only
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

---

## Common Errors Fixed

### Error 1: Wrong Endpoint
```
❌ Error: "Unrecognized field 'option_split_reach'"
Cause: Using /rest/process/playout instead of /rest/process/custom
Fix: Use ROUTE_API_LIVE_CUSTOM_URL
```

### Error 2: Missing X-Api-Key
```
❌ Error 215: "HTTP header is missing 'X-Api-Key' or its incomplete!"
Cause: Only using Basic Auth
Fix: Add X-Api-Key header in addition to Basic Auth
```

### Error 3: String vs Int for release_id
```
❌ Inconsistent: Some docs show "56", others show 56
Fix: Use integer: "route_release_id": 56
```

---

## Integration Points

### Pipeline Caching
- Use **without grouping** for faster cache generation
- Cache campaign-level totals per demographic
- Store processing time for performance tracking

### POC Application
- Use **with grouping** for frame-level analysis
- Display per-frame metrics in UI
- Allow user to toggle grouping based on needs

### Exports
- Campaign reports: no grouping (faster)
- Frame analysis: with grouping (detailed)
- Include processing time in metadata

---

## Next Steps

1. **Cache Integration**
   - Update cache pipeline to use custom endpoint
   - Store both grouped and non-grouped results
   - Track processing times for performance monitoring

2. **POC Integration**
   - Add demographic selector to UI
   - Implement grouping toggle
   - Display multiple demographic results

3. **Documentation Updates**
   - Update ROUTE_API_CACHING_GUIDE.md with grouping comparison
   - Add performance benchmarks
   - Document best practices for grouping selection

4. **Testing**
   - Test with larger campaigns (100+ frames)
   - Test with more demographics (5+)
   - Measure processing time at scale

---

## Conclusion

Successfully validated Route API custom endpoint with multiple demographics. Key learnings:

✅ Custom endpoint required (not playout)
✅ Demographics syntax: array of objects with "demographic_custom" key
✅ Dual authentication required (Basic Auth + X-Api-Key)
✅ Grouping optional: use for per-frame analysis, omit for 2x faster campaign totals
✅ **Only request metrics you need**: Use `["impacts"]` for econometric work, not `["all"]`
✅ **Omit unnecessary parameters**: Don't include `option_split_reach` if only getting impacts
✅ 5-minute timeout recommended for large campaigns

**Best Practice for Econometric Analysis:**
Use minimal payload with only impacts - fastest processing, cleanest response.

All tests passed with both grouping scenarios validated and documented.

---

**Created:** October 26, 2025
**Testing Framework**: Python 3.11 + requests
**Endpoint**: `/rest/process/custom`
**Route Release**: R56 (Q3 2025)
**Status**: Complete ✅
