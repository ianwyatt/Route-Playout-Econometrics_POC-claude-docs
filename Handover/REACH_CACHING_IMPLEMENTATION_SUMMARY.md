# Reach Caching Implementation - Summary

**Created**: 2025-10-20
**Status**: ✅ Core Implementation Complete
**Next Steps**: Testing, Integration, UI Updates

---

## What We Built

We've implemented a comprehensive reach, GRP, and frequency caching system for the Route Playout Econometrics POC. This system allows the application to:

1. **Calculate campaign reach** at day, week, and full campaign levels
2. **Cache results persistently** in PostgreSQL (survives restarts)
3. **Auto-fallback to API** when cache misses occur
4. **Handle large campaigns** (>10k frames) with appropriate warnings
5. **Support pipeline backfilling** for historical data

---

## Files Created/Modified

### 1. Database Schema

**File**: `migrations/001_create_cache_tables.sql` (420 lines)

**Tables Created**:
- `cache_route_impacts_15min` - Frame-level impacts (15min granularity)
- `cache_campaign_reach_day` - Daily reach/GRP/frequency
- `cache_campaign_reach_week` - Weekly aggregations
- `cache_campaign_reach_full` - Full campaign period
- `cache_campaign_brand_reach` - Brand-level (Stage 2 future)

**Helper Objects**:
- View: `cache_statistics` - Monitor cache health
- Function: `invalidate_cache_for_release(release_id)` - Clear cache by Route release
- Function: `clean_stale_cache_entries()` - Remove entries >24hrs old for recent dates

**Status**: ✅ Deployed and tested on local database

**File**: `migrations/README.md`
- Instructions for running migrations on both local and MS-01 databases
- Maintenance procedures
- Troubleshooting guide

---

### 2. Route API Client Enhancements

**File**: `src/api/route_client.py` (+349 lines)

**New Methods**:
- `get_campaign_reach()` - Calls `/rest/process/custom` for reach data
- `batch_campaign_reach()` - Handles >10k frame campaigns
- `_extract_target_month()` - Auto-extract month from dates
- `_mock_reach_response()` - Mock data for reach
- `_real_reach_api_call()` - Live API calls
- `_process_reach_api_response()` - Response processing

**Features**:
- 10k frame limit validation
- Auto target_month extraction
- Mock/fallback support for demos
- TTL caching
- Full error handling with automatic fallback

**Status**: ✅ Complete and ready to use

---

### 3. Cache Service

**File**: `src/services/cache_service.py` (730 lines)

**Core Functionality**:

**Impacts Cache** (15min granularity):
- `get_impacts_cache()` - Query 15min impacts
- `put_impacts_cache()` - Store impacts data
- `get_impacts_batch()` - Batch query for date ranges

**Reach Cache** (day/week/campaign):
- `get_reach_day_cache()` / `put_reach_day_cache()` - Daily reach
- `get_reach_week_cache()` / `put_reach_week_cache()` - Weekly reach
- `get_reach_full_cache()` / `put_reach_full_cache()` - Campaign reach

**Cache Management**:
- `invalidate_release_cache()` - Invalidate by Route release
- `clean_stale_cache()` - Remove stale entries
- `get_cache_stats()` - Hit/miss monitoring
- Auto TTL: 24hr for ongoing dates, never expire for historical (>7 days)

**Status**: ✅ Complete with full error handling

---

### 4. Reach Service

**File**: `src/services/reach_service.py` (695 lines)

**Main Methods**:

**Day-level**:
- `get_campaign_reach_day(campaign_id, date)` - Reach for single day
  - Checks cache first
  - Falls back to API if cache miss
  - Stores result in cache
  - Auto-detects Route release

**Week-level**:
- `get_campaign_reach_week(campaign_id, week_start, week_end)` - Reach for week
  - Important: Recalculates from ALL frames (reach is non-additive)
  - Consolidates schedules for efficiency

**Full Campaign**:
- `get_campaign_reach_full(campaign_id, date_from, date_to)` - Entire campaign
  - Returns error if >10k frames (Route API limit)
  - Suggests using day/week aggregation instead

**Date Range**:
- `get_campaign_reach_daterange()` - With optional daily breakdown
  - Returns total reach + daily breakdown
  - Includes warning that daily values don't sum to total (non-additive)

**Helper Methods**:
- `_build_schedules_from_playouts()` - Consolidate 15min windows
- `_zero_reach_result()` - Return zeros for edge cases
- Auto-detects Route release from date
- Integrates with `mv_playout_15min` materialized view

**Status**: ✅ Complete with comprehensive error handling

---

### 5. Pipeline Documentation

**File**: `Claude/Documentation/PIPELINE_REACH_CACHING_SPEC.md` (550 lines)

**Contents**:
- Overview of caching strategy
- Database connection details
- Backfilling strategy (daily, weekly, full campaign)
- SQL queries for identifying cacheable data
- Route API integration examples
- Route release mapping
- Error handling guidelines
- Monitoring and logging requirements
- Performance optimization tips
- Testing procedures
- Integration points with POC

**Purpose**: Complete specification for the pipeline team to implement automated backfilling

**Status**: ✅ Ready for pipeline implementation

---

## Key Design Decisions

### 1. Reach is Non-Additive

**Problem**: You cannot sum daily reach to get weekly reach (probability-based calculation)

**Solution**:
- Store reach at multiple aggregation levels (day, week, campaign)
- Each level calculated independently from ALL frames in that period
- `get_campaign_reach_daterange()` includes warning about non-additivity
- Documentation clearly explains this limitation

### 2. 10k Frame Limit

**Problem**: Route API `/rest/process/custom` has max 10,000 frames per call

**Solution**:
- `get_campaign_reach()` validates frame count and raises error if >10k
- `batch_campaign_reach()` handles batching but warns that reach is non-additive across batches
- `get_campaign_reach_full()` returns error for large campaigns, suggests day/week aggregation
- Pipeline spec advises skipping campaigns with >10k frames

### 3. Cache TTL Strategy

**Problem**: Balance between freshness and API load

**Solution**:
- Historical data (>7 days): Never expires
- Recent data (<7 days): 24hr TTL
- Stale check performed on query (not background job)
- Pipeline backfills historical data daily
- POC populates cache on-demand for recent data

### 4. Route Release Handling

**Problem**: Route releases change quarterly, cached data becomes stale

**Solution**:
- Store `route_release_id` with every cache entry
- Cache queries include release ID check
- `invalidate_cache_for_release()` function to clear old release data
- Auto-detect release from date using `get_release_for_date()`
- Pipeline spec includes release mapping table

### 5. Database as Primary Cache

**Problem**: In-memory cache (TTL) is lost on restart

**Solution**:
- PostgreSQL as persistent cache (survives restarts)
- TTL cache in Route client for API response deduplication only
- Cache service has hit/miss monitoring
- All historical data preserved permanently

---

## Integration Points

### Existing Code That Works With This

1. **Materialized Views** (`mv_playout_15min`, `mv_playout_15min_brands`)
   - Already created by pipeline
   - Reach service queries these for playout data
   - De-duplicated data at 15min granularity

2. **Route Release Database** (`src/db/route_releases.py`)
   - `get_release_for_date()` used by reach service
   - Auto-detects correct Route release for any date
   - Validates release coverage

3. **MS-01 Database Connection** (`src/db/ms01_helpers.py`)
   - Cache service uses existing connection pooling
   - `get_campaign_for_route_api()` used by reach service
   - Already handles local/MS-01 switching via env var

4. **Brand Split Service** (`src/services/brand_split_service.py`)
   - Stage 2 integration for brand-level reach
   - Uses `mv_playout_15min_brands` view
   - Cache table ready (`cache_campaign_brand_reach`)

---

## What's NOT Included (Future Work)

### Optional In-Memory Cache Layer

**Status**: Marked as pending in TODOs

**Description**: Add an in-memory LRU cache on top of database cache for ultra-fast repeated queries

**Benefit**: <100ms response times for frequently accessed campaigns

**Complexity**: Low (use existing TTLCache from `src/utils/ttl_cache.py`)

### Unit Tests

**Status**: Pending

**Required Tests**:
- Cache service: CRUD operations, TTL logic, release validation
- Reach service: Day/week/campaign calculations, edge cases
- Route client: Custom endpoint, mock responses, error handling

**Estimate**: 3-5 test files, ~500 lines total

### Integration Tests

**Status**: Pending

**Required Tests**:
- End-to-end: Campaign query → Cache check → API call → Cache store → Retrieve
- Large campaign handling (>10k frames)
- Release switching
- Stale cache cleanup

**Estimate**: 2-3 test files, ~300 lines total

### UI Integration

**Status**: Not started

**Required Changes**:
- Update `app_api_real.py` to use `ReachService`
- Add reach/GRP/frequency displays to campaign dashboard
- Add aggregation selector (day/week/campaign)
- Show cache hit/miss stats

**Estimate**: 100-200 lines in Streamlit app

### Brand-Level Reach (Stage 2)

**Status**: Database schema ready, service code not implemented

**Remaining Work**:
- Add brand reach methods to `reach_service.py`
- Query `mv_playout_15min_brands` for brand-level playouts
- Make separate API calls per brand
- Store in `cache_campaign_brand_reach`

**Estimate**: +200 lines in reach_service.py

---

## Testing Checklist

Before production deployment, test:

- [ ] **Migration** - Run `001_create_cache_tables.sql` on MS-01
- [ ] **Cache Service** - CRUD operations on all cache tables
- [ ] **Reach Service** - Day/week/campaign reach calculations
- [ ] **Route Client** - Custom endpoint with real API credentials
- [ ] **Edge Cases**:
  - [ ] Campaign with 0 playouts
  - [ ] Campaign with >10,000 frames
  - [ ] Date outside Route release coverage
  - [ ] Stale cache entries (>24hrs for recent dates)
  - [ ] Cache hit on historical data (should never refresh)
- [ ] **Route Release Switch** - Invalidate old release, calculate with new
- [ ] **Database Switching** - Local vs MS-01 (via `USE_MS01_DATABASE` env var)
- [ ] **Pipeline Integration** - Backfill runs without errors

---

## Usage Examples

### Example 1: Get Daily Reach

```python
from src.services.reach_service import get_reach_service
from datetime import date

# Initialize service
reach_service = await get_reach_service()

# Get reach for campaign 16012 on Aug 20, 2025
result = await reach_service.get_campaign_reach_day(
    campaign_id="16012",
    date=date(2025, 8, 20)
)

print(f"Reach: {result['reach']}")
print(f"GRP: {result['grp']}")
print(f"Frequency: {result['frequency']}")
print(f"From cache: {result.get('from_cache', False)}")
```

### Example 2: Get Week Reach

```python
# Get reach for week of Aug 19-25, 2025
result = await reach_service.get_campaign_reach_week(
    campaign_id="16012",
    week_start=date(2025, 8, 19),  # Monday
    week_end=date(2025, 8, 25)     # Sunday
)

print(f"Weekly Reach: {result['reach']}")
```

### Example 3: Get Full Campaign Reach

```python
# Get reach for entire campaign
result = await reach_service.get_campaign_reach_full(
    campaign_id="16012",
    date_from=date(2025, 8, 1),
    date_to=date(2025, 8, 31)
)

if result.get('success'):
    print(f"Campaign Reach: {result['reach']}")
else:
    print(f"Error: {result.get('error')}")
```

### Example 4: Force Refresh

```python
# Force API call even if cached
result = await reach_service.get_campaign_reach_day(
    campaign_id="16012",
    date=date(2025, 8, 20),
    force_refresh=True  # Skip cache
)
```

### Example 5: Check Cache Stats

```python
stats = reach_service.get_cache_stats()
print(f"Cache hits: {stats['hits']}")
print(f"Cache misses: {stats['misses']}")
print(f"Hit rate: {stats['hit_rate_percent']}%")
```

---

## Performance Expectations

### With Cache (Historical Data)

- **Query Time**: <50ms (database lookup only)
- **API Calls**: 0
- **Cache Hit Rate**: >95% for historical campaigns

### Without Cache (Live Calculation)

- **Query Time**: 2-5 seconds (API call + database query + caching)
- **API Calls**: 1 per day/week/campaign
- **Rate Limit**: 6 calls/second (Route API limit)

### Large Campaign (>1000 frames)

- **Query Time**: 3-8 seconds (larger payload)
- **Frame Limit**: 10,000 max per call
- **Recommendation**: Use day/week aggregation instead of full campaign

---

## Maintenance Tasks

### Daily (Automated - Pipeline)

- Run backfill for yesterday's campaigns
- Process completed weeks (on Mondays)
- Process completed campaigns (end date < yesterday)
- Clean stale cache entries: `SELECT * FROM clean_stale_cache_entries();`

### Quarterly (Manual - Route Release Updates)

- Update release mapping in code
- Invalidate old release cache: `SELECT * FROM invalidate_cache_for_release(54);`
- Re-run backfill for affected dates

### Monthly (Monitoring)

- Check cache statistics: `SELECT * FROM cache_statistics;`
- Review cache table sizes
- Check for anomalies (zero reach with playouts)
- Review API error logs

---

## Known Limitations

1. **10k Frame Limit**: Campaigns with >10,000 frames cannot get full campaign reach in one call
2. **Reach Non-Additivity**: Daily reach values don't sum to weekly/campaign reach
3. **Route Release Window**: Only last 5 releases available from Route API
4. **Brand Reach**: Not implemented in Stage 1 (schema ready, code pending)
5. **In-Memory Cache**: Not implemented (all cache queries hit PostgreSQL)

---

## Questions & Next Steps

### Questions for Doctor Biz

1. **Testing Priority**: Should we write tests before UI integration, or integrate UI first?
2. **Pipeline Timeline**: When will backfill be implemented? Affects cache hit rates.
3. **Brand Reach**: Is Stage 2 (brand-level) needed soon, or can it wait?
4. **In-Memory Cache**: Worth implementing for performance, or is database fast enough?
5. **Error Logging**: Where should cache/reach errors be sent? (File, Sentry, etc.)

### Immediate Next Steps

1. **Test on MS-01**: Run migration on production database
2. **UI Integration**: Add reach service to Streamlit app
3. **End-to-End Test**: Query campaign → See reach → Verify cache
4. **Pipeline Coordination**: Share spec with pipeline team
5. **Documentation Update**: Update main README with reach functionality

---

## File Locations

All code is in: `/Users/ianwyatt/PycharmProjects/Route-Playout-Econometrics_POC`

**Database**:
- `migrations/001_create_cache_tables.sql`
- `migrations/README.md`

**Services**:
- `src/services/cache_service.py`
- `src/services/reach_service.py`

**API Clients**:
- `src/api/route_client.py` (enhanced)

**Documentation**:
- `Claude/Documentation/PIPELINE_REACH_CACHING_SPEC.md`
- `Claude/Handover/REACH_CACHING_IMPLEMENTATION_SUMMARY.md` (this file)

---

**End of Summary** - Ready for review and testing!
