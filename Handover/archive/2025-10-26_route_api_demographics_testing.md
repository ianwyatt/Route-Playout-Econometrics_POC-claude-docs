# Handover: Route API Demographics Testing Complete

**Date:** October 26, 2025
**Session Focus:** Route API Custom Endpoint Testing with Multiple Demographics
**Status:** ✅ Complete - All Tests Passed

---

## What Was Accomplished

### 1. Route API Endpoint Correction
- **CRITICAL FIX**: Identified correct endpoint is `/rest/process/custom`, NOT `/rest/process/playout`
- Updated test scripts to use `ROUTE_API_LIVE_CUSTOM_URL`
- Validated dual authentication (Basic Auth + X-Api-Key)

### 2. Demographics Syntax Discovery
- Learned correct syntax: array of objects with `"demographic_custom"` key
- **Correct**: `[{"demographic_custom": "social_grade=1 or social_grade=2"}]`
- **Wrong**: `["social_grade=1 or social_grade=2"]` (array of strings)

### 3. Successful API Testing
- **Test 1**: Simple demographics (single frame) - ✅ PASSED
- **Test 2**: Multiple demographics WITH grouping - ✅ PASSED (56s processing)
- **Test 3**: Multiple demographics WITHOUT grouping - ✅ PASSED (29s processing)

### 4. Performance Analysis
- **WITHOUT grouping**: ~2x faster (29s vs 56s)
- **WITH grouping**: Per-frame breakdowns available
- **Recommendation**: Use no grouping for campaign-level totals (faster)

### 5. Documentation Created
- `Claude/Documentation/route_api_demographics_testing.md` - Complete testing summary (650+ lines)
- Response samples saved with both grouping scenarios
- Test script validated and ready for reuse

---

## Key Technical Discoveries

### Minimal Payload (RECOMMENDED for Econometric Work)
```json
{
  "route_release_id": 56,  // int not string!
  "route_algorithm_version": "10.2",
  "demographics": [
    {
      "demographic_custom": "ageband>0"  // All adults
    }
  ],
  "algorithm_figures": ["impacts"],  // ✅ Only request what you need!
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

**Why Minimal?**
- Fastest processing
- Only returns impacts (audience data)
- No unnecessary parameters like `option_split_reach`
- Clean, efficient response

### Full Payload (When You Need All Metrics)
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
  "grouping": "frame_id",  // Optional: omit for 2x faster
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

### Response Structure Differences

**WITH Grouping**:
- 6 result objects: 2 "total" + 4 "grouping" (2 demographics × 2 frames)
- Per-frame metrics available
- Some metrics (reach/cover) marked "n/a" at frame level
- Slower: 56 seconds

**WITHOUT Grouping**:
- 2 result objects: only "total" per demographic
- Campaign-level aggregation only
- All metrics available
- **Faster**: 29 seconds (~2x speedup)

---

## Files Created/Updated

### Created
- `test_route_api_demographics.py` - Test script for custom endpoint (226 lines)
- `route_response_with_grouping_20251026_132123.json` - Full response with grouping
- `route_response_no_grouping_20251026_132123.json` - Full response without grouping
- `test_demographics_custom_endpoint.log` - Test execution log
- `Claude/Documentation/route_api_demographics_testing.md` - Complete testing summary
- `Claude/Documentation/route_api_optimization_summary.md` - Optimization guide

### Updated (Pipeline Team Documentation)
- ✅ `docs/api-reference/pipeline/ROUTE_API_CACHING_GUIDE.md` - Updated to custom endpoint with optimization
- ✅ `docs/api-reference/pipeline/QUICK_START.md` - Updated minimal example with correct syntax
- ✅ `docs/api-reference/pipeline/README.md` - Added optimization notice

---

## Next Steps

### Immediate (Ready to Implement)
1. **Update Cache Pipeline**
   - Switch from playout endpoint to custom endpoint
   - Use no grouping for faster cache generation
   - Store processing times for monitoring

2. **POC UI Integration**
   - Add demographic selector dropdown
   - Implement grouping toggle (frame vs campaign level)
   - Display multiple demographic results side-by-side

### Future Enhancements
1. **Performance Testing**
   - Test with 100+ frames
   - Test with 5+ demographics
   - Benchmark processing times at scale

2. **Cache Optimization**
   - Store both grouped and non-grouped results
   - Cache individual demographics separately
   - Implement smart cache invalidation

3. **Documentation Updates**
   - Update pipeline caching guide with grouping comparison
   - Add performance benchmarks
   - Document best practices

---

## Important Notes for Next Session

### Authentication Requirements
- **Both** Basic Auth AND X-Api-Key required
- Environment variables:
  - `ROUTE_API_User_Name`
  - `ROUTE_API_Password`
  - `ROUTE_API_KEY`
- Never use playout endpoint for demographics

### Timeout Configuration
- **Recommended**: 300 seconds (5 minutes)
- Small tests: 30-60 seconds sufficient
- Large campaigns (100+ frames): May need full 5 minutes

### Demographics Syntax
- Must be objects with "demographic_custom" key
- SQL-like expressions: `"social_grade=1 or social_grade=2"`
- AND/OR operators supported
- Use numeric codes from R56 questionnaire

### Algorithm Figures Optimization
- **Only request what you need** for better performance
- For impacts only: `["impacts"]` - **RECOMMENDED for econometric work**
- For specific metrics: `["impacts", "reach", "grp"]`
- For everything: `["all"]` - slower, use sparingly

### Parameter Minimization
- **Don't include `option_split_reach`** unless you need pedestrian/vehicular split
- Keep payload minimal for fastest processing
- Only add parameters you actually need

### Grouping Decision
- **Use grouping** when: Need per-frame analysis, comparing frames
- **Skip grouping** when: Speed matters, campaign-level totals sufficient
- No grouping = ~2x faster processing

---

## Testing Validation

All three test scenarios passed successfully:

✅ **Simple Demographics** (ageband>0, single frame, 15 min)
- Response: 200 OK
- Processing: Fast
- Result: Valid response structure

✅ **Multiple Demographics WITH Grouping** (2 demographics, 2 frames, 1 hour)
- Response: 200 OK
- Processing: 56 seconds
- Result: 6 result objects (2 totals + 4 groupings)

✅ **Multiple Demographics WITHOUT Grouping** (2 demographics, 2 frames, 1 hour)
- Response: 200 OK
- Processing: 29 seconds (2x faster!)
- Result: 2 result objects (totals only)

---

## Environment Variables Confirmed Working

```bash
ROUTE_API_LIVE_URL=https://route.mediatelapi.co.uk
ROUTE_API_LIVE_CUSTOM_URL=https://route.mediatelapi.co.uk/rest/process/custom
ROUTE_API_User_Name=ianw@route.org.uk
ROUTE_API_Password=a9CgngwX
ROUTE_API_KEY=5a08fc4d-34f6-4686-9228-b5a5b059b97d
```

---

## Code Snippets for Reuse

### Making a Custom Endpoint Call
```python
import requests
from dotenv import load_dotenv
import os

load_dotenv()

url = os.getenv('ROUTE_API_LIVE_CUSTOM_URL')
auth = (
    os.getenv('ROUTE_API_User_Name'),
    os.getenv('ROUTE_API_Password')
)
headers = {
    'Content-Type': 'application/json',
    'X-Api-Key': os.getenv('ROUTE_API_KEY')
}

payload = {
    "route_release_id": 56,
    "route_algorithm_version": "10.2",
    "demographics": [
        {"demographic_custom": "ageband>0"}
    ],
    "algorithm_figures": ["all"],
    "campaign": [...],
    "target_month": 1
}

response = requests.post(
    url,
    json=payload,
    headers=headers,
    auth=auth,
    timeout=300
)
```

### Processing Response
```python
if response.status_code == 200:
    data = response.json()

    # Extract totals
    totals = [r for r in data['results'] if r['description'] == 'total']

    # Extract groupings (if present)
    groupings = [r for r in data['results'] if r['description'] == 'grouping']

    # Get metrics
    for result in totals:
        demographic = result['demographic']
        impacts = result['figures']['impacts']
        reach = result['figures']['reach']
        grp = result['figures']['gross_rating_points']
        print(f"{demographic}: Impacts={impacts}, Reach={reach}, GRP={grp}")
```

---

## Questions for Next Session

1. **Should we update the cache pipeline to use custom endpoint now?**
   - Would provide more flexibility with demographics
   - Slightly different response structure to handle

2. **Which metrics are most important for econometricians?**
   - impacts (audience)
   - GRP (gross rating points)
   - reach
   - frequency
   - All of the above?

3. **Do we need per-frame analysis in the POC UI?**
   - If yes: use grouping (slower but detailed)
   - If no: skip grouping (2x faster, campaign totals only)

4. **Should we cache multiple demographics or just "all adults"?**
   - Multiple: More flexible, more storage
   - Single: Faster, simpler

---

## Summary

Successfully validated Route API custom endpoint with multiple demographics. All tests passed. Key correction: Must use `/rest/process/custom` endpoint, not playout endpoint. Discovered ~2x performance improvement when omitting grouping parameter for campaign-level aggregations.

Ready to integrate into cache pipeline and POC UI. All documentation complete and test scripts validated.

**Status**: ✅ Ready for Integration

---

**Created:** October 26, 2025 13:30
**Next Session Priority:** Integrate custom endpoint into cache pipeline
**Blockers:** None
**Confidence:** High - All tests passing
