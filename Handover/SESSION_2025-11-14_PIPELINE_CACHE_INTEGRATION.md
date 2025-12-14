# Pipeline Cache Integration - Session Summary

**Date**: 2025-11-14
**Status**: 🔍 Discovery & Planning Complete
**Next Session**: Implementation Phase

---

## 🎯 Executive Summary

The pipeline team has deployed **252.7M cached records** on MS-01 production database, providing 1,000-6,000x speedup over Route API calls. This session focused on understanding the handover documentation and planning POC integration.

**Key Discovery**: Route API has TWO different frame limits (10,000 with grouping, unlimited without) - this is the #1 pitfall for developers.

**Current POC Status**:
- ✅ Database connection infrastructure exists (local vs MS-01 switcher)
- ✅ Route API client exists with TTL cache
- ❌ NOT using pipeline's 252.7M cache yet
- ❌ NO frame validation workflow (will cause errors)
- ❌ NO grouping decision logic (will fail on large campaigns)

---

## 📚 What We Learned

### Pipeline Cache System (252.7M Records)

**Three cache systems deployed:**

| Cache Table | Records | Purpose | Speed Improvement |
|-------------|---------|---------|-------------------|
| `cache_route_impacts_15min_by_demo` | 252.7M | 15-min impacts, 7 demographics | 1,000-6,000x |
| `cache_campaign_reach_day` | 11,363 | Daily reach/GRP/freq metrics | 1,000-6,000x |
| `cache_campaign_brand_reach` | 17,406 | Brand-level performance | 1,000-6,000x |

**Coverage**: 826 campaigns, Aug 6 - Oct 13 2025 (69 days), refreshed daily at 2am UTC

### Database Architecture

**MS-01 Production (192.168.1.34:5432/route_poc):**

1. **`mv_playout_15min`** (~700M rows) - PRIMARY view for Route API
   - Pre-aggregated 15-minute windows (:00, :15, :30, :45)
   - ONE row per (frameid, campaign, 15-min window)
   - 10,000x faster than raw data aggregation
   - Contains: frameid, spot_count, playout_length_seconds, break_length_seconds

2. **`mv_playout_15min_brands`** (~750M rows) - Brand tracking
   - Handles multi-brand campaigns
   - Multiple rows per window if brands change
   - Used for brand-level reporting

3. **`playout_data`** (1.28B rows) - Raw playout records
   - Millisecond precision
   - Debug/audit purposes only

4. **`route_releases`** (8 rows) - Route release metadata (R54-R61)
   - Maps dates to Route releases
   - Critical for determining which release to use

### Critical Technical Discoveries

**1. Route API Frame Limits** 🚨 #1 PITFALL

| Call Type | Grouping Param | Frame Limit | Returns |
|-----------|----------------|-------------|---------|
| **With Grouping** | `"grouping": "frame"` | ❌ **10,000 max** | Per-frame breakdown |
| **Without Grouping** | (omit parameter) | ✅ **NO LIMIT** | Aggregate metrics |

**Example Error Scenario:**
```python
# BAD - Will fail if campaign has >10k frames
payload = {
    "grouping": "frame",  # Per-frame breakdown requested
    "campaign": build_campaign_with_50k_frames()  # ❌ ERROR 221
}
```

**Solution:**
```python
# Check frame count first
frame_count = len(campaign_frames)
if frame_count > 10000:
    # Use non-grouping for aggregate metrics
    payload = {"campaign": [...]}  # No grouping param
else:
    # Safe to use grouping
    payload = {"grouping": "frame", "campaign": [...]}
```

**2. Impacts Stored in Thousands** 🚨 CRITICAL

All impact values in cache tables are **divided by 1000** for storage efficiency.

```sql
-- WRONG ❌
SELECT impacts FROM cache_route_impacts_15min_by_demo;
-- Returns: 1234 (should be 1,234,000)

-- CORRECT ✅
SELECT impacts * 1000 as actual_impacts FROM cache_route_impacts_15min_by_demo;
-- Returns: 1234000 (correct)
```

**3. Frame Validation Required** 🚨 PREVENTS ERROR 220

Must validate frames exist in Route release BEFORE calling Route API:

```python
# Step 1: Get frames for campaign
frames = get_campaign_frames(campaign_id)

# Step 2: Validate frames exist in Route release
payload = {"route_release_id": 56, "frame_ids": frames}
response = requests.post('/rest/framedata', json=payload, headers=headers)
valid_frames = [f['frame_id'] for f in response.json()['frames']]
invalid_frames = [fid for fid in frames if fid not in valid_frames]

# Step 3: Only use valid frames in Route API call
if not valid_frames:
    raise ValueError(f"No valid frames for campaign {campaign_id} in R56")
```

**Why this matters**: Not all frames in playout data exist in Route releases. Calling Route API with invalid frames causes error 220.

**4. 7 Demographic Segments** (All Pre-Cached)

1. `all_adults` - All adults 15+
2. `age_15_34` - Young adults
3. `age_35_54` - Middle-aged adults
4. `age_55_plus` - Older adults
5. `abc1` - Higher socio-economic groups
6. `c2de` - Lower socio-economic groups
7. `housewife` - Main household shopper

**5. 15-Minute Time Windows**

Strict time boundaries: `:00`, `:15`, `:30`, `:45` past each hour

```
Spot at 12:14:59 → 12:00:00 window
Spot at 12:15:00 → 12:15:00 window
Spot at 12:15:01 → 12:15:00 window
```

**6. Route API Authentication**

Requires **BOTH** Basic Auth AND X-Api-Key header:

```python
headers = {
    'Content-Type': 'application/json',
    'X-Api-Key': os.getenv('ROUTE_API_KEY')
}
auth = (
    os.getenv('ROUTE_API_User_Name'),
    os.getenv('ROUTE_API_Password')
)
response = requests.post(url, json=payload, headers=headers, auth=auth)
```

**7. Route API Rate Limits**

- **6 calls/second per account**
- **429 error** if exceeded
- **Exponential backoff** required
- Pipeline team uses **dual accounts** for 12 calls/sec total

---

## 🏗️ Current POC Architecture

### Database Connection Infrastructure

**Already Implemented:** ✅

```python
# src/db/ms01_helpers.py - Async connection pool
use_ms01 = os.getenv('USE_MS01_DATABASE', 'true').lower() == 'true'

if use_ms01:
    # MS-01 Production (192.168.1.34)
    config = {
        'host': '192.168.1.34',
        'database': 'route_poc',
        'user': 'postgres',
        'password': os.getenv('POSTGRES_PASSWORD_MS01')
    }
else:
    # Local Mac (localhost)
    config = {
        'host': 'localhost',
        'database': 'route_poc',
        'user': 'ianwyatt',
        'password': os.getenv('POSTGRES_PASSWORD_LOCAL')
    }
```

**Files:**
- `src/db/ms01_helpers.py` - Async connection pool (asyncpg)
- `src/db/streamlit_queries.py` - Sync queries for Streamlit (psycopg2)
- `src/db/__init__.py` - Database module initialization

### Route API Client

**Already Implemented:** ✅

```python
# src/api/route_client.py
class RouteAPIClient:
    def __init__(self):
        self.cache = TTLCache(max_size=1000, default_ttl=3600)  # 1hr TTL
        self.use_mock = check_credentials()

    def call_api(self, payload):
        # In-memory TTL cache
        cache_key = self._cache_key(payload)
        if cached := self.cache.get(cache_key):
            return cached

        # Make API call
        response = self._real_api_call(payload)
        self.cache.put(cache_key, response)
        return response
```

**Issues:**
- ❌ In-memory cache only (not leveraging 252.7M PostgreSQL cache)
- ❌ No frame validation before API calls
- ❌ No grouping decision logic (frame count check)
- ❌ May not handle correct endpoint (`/rest/process/custom`)

### Streamlit Applications

**Two separate apps:**

1. **`app_demo.py`** - Mock data for presentations (<1s response)
2. **`app_api_real.py`** - Real API integration with database

**Current behavior:** Likely calling Route API directly without checking PostgreSQL cache first.

---

## 🚨 Integration Gaps

### Gap 1: Not Using Pipeline Cache ❌ HIGH PRIORITY

**Current:** POC calls Route API for every query (2-30 seconds per query)

**Should be:** Check PostgreSQL cache first (sub-5ms), fallback to API on miss

**Impact:**
- 99%+ unnecessary API calls for cached campaigns
- Slow user experience (5-30s vs <5ms)
- Hitting API rate limits unnecessarily

### Gap 2: No Frame Validation ❌ HIGH PRIORITY

**Current:** POC likely sends all campaign frames to Route API without validation

**Should be:** Validate frames exist in Route release via `/rest/framedata` endpoint

**Impact:**
- Route API error 220 (invalid frames)
- Failed queries for campaigns with frames not in Route
- No handling for partially valid frame sets

### Gap 3: No Grouping Decision Logic ❌ MEDIUM PRIORITY

**Current:** POC may be adding `"grouping": "frame"` without checking frame count

**Should be:** Check frame count, only use grouping if ≤10,000 frames

**Impact:**
- Route API failures for large campaigns (>10k frames)
- No fallback strategy for large campaigns

### Gap 4: Impacts Not Multiplied ❌ LOW PRIORITY

**Current:** If/when POC queries cache, may display impacts in thousands

**Should be:** Always multiply by 1000 when querying cache tables

**Impact:**
- Incorrect metrics display (off by 1000x)
- User confusion

### Gap 5: No Demographic Breakdown ⚠️ FEATURE GAP

**Current:** POC may only show "all adults" demographic

**Should be:** Display all 7 demographic segments (already cached!)

**Impact:**
- Missing valuable demographic insights
- Not leveraging full cache capability

---

## 📋 Cache-First Integration Pattern

### Recommended Architecture

```python
def get_campaign_audience(campaign_id, start_date, end_date):
    """
    Cache-first pattern with Route API fallback.

    Returns:
        DataFrame with demographic impacts
    """
    # STEP 1: Try cache first (sub-5ms response) ⚡
    cached_data = query_demographic_cache(campaign_id, start_date, end_date)

    if cached_data is not None and len(cached_data) > 0:
        logger.info(f"✅ Cache HIT for campaign {campaign_id}")
        return format_cached_data(cached_data)  # 1,000-6,000x faster!

    # STEP 2: Cache miss - call Route API 🌐
    logger.info(f"⚠️ Cache MISS for campaign {campaign_id} - calling Route API")

    # Get frames from database
    frames = get_campaign_frames(campaign_id, start_date, end_date)

    if not frames:
        raise ValueError(f"No playout data found for campaign {campaign_id}")

    # STEP 3: Validate frames exist in Route release 🔍
    frame_ids = frames['frameid'].unique().tolist()
    valid_frames, invalid_frames = validate_frames(frame_ids, route_release_id=56)

    if not valid_frames:
        raise ValueError(f"No valid frames in Route R56 for campaign {campaign_id}")

    if invalid_frames:
        logger.warning(f"Campaign {campaign_id} has {len(invalid_frames)} invalid frames")
        # Filter to valid frames only
        frames = frames[frames['frameid'].isin(valid_frames)]

    # STEP 4: Check frame count for grouping decision 📊
    frame_count = len(valid_frames)
    use_grouping = False  # Default: aggregate metrics

    if frame_count > 10000:
        logger.warning(f"Campaign has {frame_count} frames - using non-grouping (aggregate)")
    elif need_per_frame_breakdown:
        logger.info(f"Campaign has {frame_count} frames - using grouping (per-frame)")
        use_grouping = True

    # STEP 5: Build Route API payload 🔧
    payload = {
        "route_release_id": 56,
        "route_algorithm_version": 10.2,
        "target_month": start_date.month,
        "algorithm_figures": ["impacts"],  # Minimal for speed
        "demographics": [{"demographic_id": i} for i in range(1, 8)],  # All 7 segments
        "campaign": build_campaign_entries(frames)
    }

    if use_grouping:
        payload["grouping"] = "frame"

    # STEP 6: Call Route API with retry logic 📞
    api_response = call_route_api_with_retry(payload, max_retries=3)

    # STEP 7: (Optional) Store in cache for future use 💾
    # store_in_cache(campaign_id, api_response)

    # STEP 8: Return data in consistent format
    return format_api_response(api_response)


def query_demographic_cache(campaign_id, start_date, end_date):
    """Query cached demographic data from PostgreSQL."""
    query = """
        SELECT
            time_window_start,
            demographic_segment,
            impacts * 1000 as impacts  -- ⚠️ CRITICAL: Multiply by 1000!
        FROM cache_route_impacts_15min_by_demo
        WHERE campaign_id = %s
          AND time_window_start >= %s
          AND time_window_start < %s
        ORDER BY time_window_start, demographic_segment
    """

    try:
        conn = get_db_connection(use_ms01=True)  # Always query MS-01 for cache
        df = pd.read_sql(query, conn, params=(campaign_id, start_date, end_date))
        conn.close()
        return df if not df.empty else None
    except Exception as e:
        logger.warning(f"Cache query failed: {e}")
        return None


def validate_frames(frame_ids, route_release_id=56):
    """
    Validate frames exist in Route release.

    Returns:
        tuple: (valid_frames, invalid_frames)
    """
    payload = {
        "route_release_id": route_release_id,
        "frame_ids": frame_ids
    }

    response = requests.post(
        'https://route.mediatelapi.co.uk/rest/framedata',
        headers=get_route_headers(),
        auth=get_route_auth(),
        json=payload,
        timeout=60
    )

    response.raise_for_status()
    data = response.json()

    valid_frames = [f['frame_id'] for f in data.get('frames', [])]
    invalid_frames = [fid for fid in frame_ids if fid not in valid_frames]

    return valid_frames, invalid_frames
```

---

## 🎯 Integration Plan

### Phase 1: Discovery & Validation (1-2 hours)

**Objective:** Verify cache exists and is accessible

**Tasks:**
1. Test MS-01 database connection
2. Verify cache tables exist
3. Run example queries from pipeline docs
4. Validate cached campaign count (should be 826)
5. Test query performance (should be <5ms)
6. Verify impacts multiplication (×1000)

**Acceptance Criteria:**
- ✅ Can connect to MS-01 (192.168.1.34:5432)
- ✅ Can query `cache_route_impacts_15min_by_demo` (252.7M records)
- ✅ Query returns results in <5ms
- ✅ Impacts are correctly multiplied by 1000

**Risk:** Low - read-only queries, no code changes

### Phase 2: Cache Query Functions (2-3 hours)

**Objective:** Create reusable cache query functions

**Tasks:**
1. Create `src/db/cache_queries.py` module
2. Implement `query_demographic_cache(campaign_id, dates)`
3. Implement `query_campaign_reach_cache(campaign_id, aggregation)`
4. Implement `query_brand_reach_cache(campaign_id, brand_id)`
5. Add error handling and logging
6. Add time filter validation (performance critical)
7. Write unit tests for cache queries

**Deliverables:**
- `src/db/cache_queries.py` - New module
- Unit tests in `tests/test_cache_queries.py`

**Acceptance Criteria:**
- ✅ All cache query functions work correctly
- ✅ Impacts properly multiplied by 1000
- ✅ Time filters included (performance)
- ✅ Error handling for cache misses
- ✅ Unit tests passing

**Risk:** Low-Medium - new code, isolated module

### Phase 3: Frame Validation Workflow (2-3 hours)

**Objective:** Implement frame validation before Route API calls

**Tasks:**
1. Create `validate_frames()` function
2. Add to Route API client
3. Implement invalid frame filtering
4. Add logging for validation results
5. Handle edge case: all frames invalid
6. Add retry logic for validation failures
7. Write unit tests

**Deliverables:**
- Updated `src/api/route_client.py`
- Unit tests in `tests/test_frame_validation.py`

**Acceptance Criteria:**
- ✅ Frames validated before every API call
- ✅ Invalid frames filtered out
- ✅ Proper error handling (all frames invalid)
- ✅ Logging shows valid/invalid counts
- ✅ Unit tests passing

**Risk:** Medium - modifies existing Route API client

### Phase 4: Grouping Decision Logic (2 hours)

**Objective:** Add frame count validation and grouping logic

**Tasks:**
1. Add frame count check before API calls
2. Implement grouping decision logic
3. Add batching support for campaigns >10k frames (optional)
4. Update Route API client
5. Add configuration for grouping threshold (10000)
6. Write unit tests

**Deliverables:**
- Updated `src/api/route_client.py`
- Unit tests in `tests/test_grouping_logic.py`

**Acceptance Criteria:**
- ✅ Frame count checked before grouping
- ✅ Grouping only used if ≤10k frames
- ✅ Warning logged for large campaigns
- ✅ No API failures from exceeding frame limit
- ✅ Unit tests passing

**Risk:** Low - logic addition, no breaking changes

### Phase 5: Cache-First Integration (3-4 hours)

**Objective:** Update POC to check cache before calling API

**Tasks:**
1. Update `src/services/campaign_service.py` with cache-first pattern
2. Update `src/api/route_client.py` to check PostgreSQL cache
3. Add cache hit/miss logging
4. Add fallback to Route API on cache miss
5. Update Streamlit apps to show cache status
6. Add cache statistics to UI (hit rate, response time)
7. Write integration tests

**Deliverables:**
- Updated `src/services/campaign_service.py`
- Updated `src/api/route_client.py`
- Updated `src/ui/app_api_real.py`
- Integration tests in `tests/integration/test_cache_integration.py`

**Acceptance Criteria:**
- ✅ Cache checked first for all queries
- ✅ Fallback to API on cache miss
- ✅ Cache hit rate displayed in UI
- ✅ Performance improvement visible (5-30s → <5ms)
- ✅ Integration tests passing

**Risk:** Medium-High - affects core query flow

### Phase 6: Demographic Breakdown UI (2-3 hours)

**Objective:** Display all 7 demographic segments in UI

**Tasks:**
1. Add demographic selector dropdown to UI
2. Display all 7 segments in results table
3. Add demographic comparison charts
4. Update export to include all demographics
5. Add demographic filtering
6. Write UI tests (Streamlit)

**Deliverables:**
- Updated `src/ui/app_api_real.py`
- Updated `src/ui/components/` (metrics cards, tables)
- UI screenshots for documentation

**Acceptance Criteria:**
- ✅ All 7 demographics visible in UI
- ✅ User can select which demographics to display
- ✅ Comparison charts work correctly
- ✅ Export includes demographic breakdown
- ✅ UI tests passing

**Risk:** Low - UI changes only, no data logic

### Phase 7: Testing & Validation (3-4 hours)

**Objective:** Comprehensive testing of cache integration

**Tasks:**
1. Test with cached campaigns (should be fast)
2. Test with uncached campaigns (should fallback to API)
3. Test with large campaigns (>10k frames, no grouping)
4. Test with invalid frames (validation filtering)
5. Performance benchmarking (cache vs API)
6. Load testing (multiple concurrent queries)
7. Error scenario testing (cache down, API down)
8. Write test report

**Deliverables:**
- Test results document
- Performance benchmark report
- Integration test suite passing

**Acceptance Criteria:**
- ✅ Cache hit rate >80% for common queries
- ✅ Query time <500ms for cached data
- ✅ Query time 5-30s for uncached (API) data
- ✅ No errors for large campaigns
- ✅ Proper fallback when cache unavailable
- ✅ All integration tests passing

**Risk:** Low - testing only

### Phase 8: Documentation & Handover (1-2 hours)

**Objective:** Document cache integration for team

**Tasks:**
1. Update `docs/ARCHITECTURE.md` with cache integration
2. Create `docs/CACHE_INTEGRATION.md` guide
3. Update `README.md` with new capabilities
4. Document environment variables needed
5. Create troubleshooting guide
6. Update handover docs for next session

**Deliverables:**
- Updated documentation
- Troubleshooting guide
- Handover document for next session

**Acceptance Criteria:**
- ✅ Documentation complete and accurate
- ✅ Team can understand cache integration
- ✅ Troubleshooting scenarios documented

**Risk:** Low - documentation only

---

## 📊 Estimated Timeline

| Phase | Duration | Risk Level | Priority |
|-------|----------|------------|----------|
| Phase 1: Discovery & Validation | 1-2 hours | Low | HIGH |
| Phase 2: Cache Query Functions | 2-3 hours | Low-Medium | HIGH |
| Phase 3: Frame Validation | 2-3 hours | Medium | HIGH |
| Phase 4: Grouping Logic | 2 hours | Low | MEDIUM |
| Phase 5: Cache-First Integration | 3-4 hours | Medium-High | HIGH |
| Phase 6: Demographic UI | 2-3 hours | Low | MEDIUM |
| Phase 7: Testing & Validation | 3-4 hours | Low | HIGH |
| Phase 8: Documentation | 1-2 hours | Low | MEDIUM |

**Total Estimated Time:** 16-23 hours (2-3 days of focused work)

**Critical Path:** Phases 1 → 2 → 3 → 5 → 7 (must be done in order)

**Parallel Work:** Phases 4 and 6 can be done alongside Phase 5

---

## ⚠️ Risks & Mitigation

### Risk 1: Database Credentials Not Available

**Impact:** Cannot access MS-01 cache (HIGH)

**Mitigation:**
- Request `MS01_DB_PASSWORD` from pipeline team immediately
- Test local database as fallback
- Ensure `USE_MS01_DATABASE` switcher works

**Contingency:**
- Use local database with sample data
- Continue development with mock cache responses

### Risk 2: Breaking Existing Functionality

**Impact:** POC stops working during integration (HIGH)

**Mitigation:**
- Implement cache-first as **optional feature** initially
- Add feature flag: `USE_CACHE_FIRST=false` (default off)
- Test thoroughly with existing campaigns
- Keep fallback to direct API calls

**Contingency:**
- Quick rollback via feature flag
- Maintain old code path intact

### Risk 3: Cache Query Performance Issues

**Impact:** Queries slower than expected (MEDIUM)

**Mitigation:**
- Always include time filters in WHERE clause
- Use proper indexes (already exist)
- Test with EXPLAIN ANALYZE first
- Monitor query execution plans

**Contingency:**
- Optimize query structure
- Add additional indexes if needed
- Contact pipeline team for help

### Risk 4: Demographic Data Not in Expected Format

**Impact:** UI display issues (LOW-MEDIUM)

**Mitigation:**
- Review pipeline cache schema carefully
- Test with sample data first
- Add data validation in query functions
- Handle missing demographics gracefully

**Contingency:**
- Add data transformation layer
- Fallback to "all adults" only

### Risk 5: Frame Validation Adds Latency

**Impact:** Queries slower with validation (LOW)

**Mitigation:**
- Cache validation results (frames don't change frequently)
- Validate once per campaign, not per query
- Add validation result caching (1hr TTL)

**Contingency:**
- Make validation optional via config
- Skip validation for cached campaigns

### Risk 6: Large Campaign Handling Complexity

**Impact:** Campaigns >10k frames not handled (LOW)

**Mitigation:**
- Implement non-grouping approach first
- Add batching only if per-frame breakdown needed
- Document limitations clearly

**Contingency:**
- Show error message for >10k frame per-frame requests
- Offer aggregate metrics only

---

## 🎯 Success Criteria

### Performance Metrics

- **Cache Hit Rate**: >80% for common campaigns
- **Cache Query Time**: <5ms for cached data
- **API Fallback Time**: 5-30s for uncached data (acceptable)
- **Frame Validation**: <2s for validation of 1000 frames
- **Overall User Query Time**: <500ms for 80% of queries

### Functional Requirements

- ✅ Cache-first pattern implemented
- ✅ Frame validation prevents error 220
- ✅ Grouping logic prevents >10k frame errors
- ✅ All 7 demographics accessible
- ✅ Impacts correctly multiplied by 1000
- ✅ Fallback to API works seamlessly
- ✅ Cache hit/miss visible in logs/UI

### Quality Requirements

- ✅ All unit tests passing (>80% coverage)
- ✅ Integration tests passing
- ✅ No breaking changes to existing functionality
- ✅ Backward compatibility maintained
- ✅ Error handling comprehensive
- ✅ Logging informative

### Documentation Requirements

- ✅ Architecture docs updated
- ✅ Cache integration guide created
- ✅ Troubleshooting guide available
- ✅ Code comments clear
- ✅ Team can maintain code

---

## 📞 Key Contacts & Resources

### Pipeline Team
- **Contact**: ian@route.org.uk
- **Database**: MS-01 @ 192.168.1.34:5432/route_poc
- **Credentials**: Request `MS01_DB_PASSWORD`

### Documentation
- **Pipeline Handover**: `/docs/pipeline-handover/`
- **Database Reference**: `/docs/pipeline-handover/DATABASE_HANDOVER_FOR_POC.md`
- **API Integration**: `/docs/pipeline-handover/API_INTEGRATION_GUIDE.md`
- **Cache Usage**: `/docs/pipeline-handover/CACHE_USAGE_GUIDE.md`
- **Python Examples**: `/docs/pipeline-handover/PYTHON_EXAMPLES.py`
- **Quick Reference**: `/docs/pipeline-handover/QUICK_REFERENCE.md`

### Weekly Checks
- **Changelog**: `/docs/pipeline-handover/CHANGELOG_FOR_POC.md` (check every Monday)

---

## 🚀 Next Session Action Items

**Priority 1 (Start Immediately):**
1. Test MS-01 cache connection
2. Run example queries from QUICK_REFERENCE.md
3. Verify 252.7M records exist
4. Benchmark query performance

**Priority 2 (Day 1):**
1. Create `src/db/cache_queries.py`
2. Implement demographic cache query function
3. Test with real campaign data
4. Verify impacts multiplication

**Priority 3 (Day 1-2):**
1. Implement frame validation workflow
2. Add to Route API client
3. Test with invalid frames
4. Add logging

**Priority 4 (Day 2):**
1. Implement cache-first pattern
2. Update campaign service
3. Test with cached vs uncached campaigns
4. Measure performance improvement

---

## 📝 Questions for Next Session

1. Do we have `MS01_DB_PASSWORD` credential?
2. Should we implement batching for >10k frame campaigns?
3. Do we need per-frame breakdown or are aggregate metrics sufficient?
4. Should cache-first be default or opt-in feature flag?
5. What's acceptable fallback time for uncached campaigns (currently 5-30s)?
6. Should we display cache hit/miss to users or only in logs?
7. Do we need demographic selector UI or show all 7 by default?

---

**Status**: 📋 Planning Complete
**Confidence**: High - clear plan, well-defined scope
**Blockers**: None (pending MS01_DB_PASSWORD credential)
**Ready to Proceed**: ✅ YES

---

**Created**: 2025-11-14
**Session Duration**: 2 hours (discovery & planning)
**Next Session**: Implementation Phase 1-3
