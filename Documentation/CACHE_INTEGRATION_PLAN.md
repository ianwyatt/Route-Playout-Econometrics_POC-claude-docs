# Cache Integration Plan - Route Playout POC

**Created**: 2025-11-14
**Status**: 📋 Ready to Execute
**Estimated Duration**: 16-23 hours (2-3 days)

---

## 🎯 Objective

Integrate pipeline team's 252.7M cached records into POC application to achieve:
- **1,000-6,000x query speedup** (5-30s → <5ms)
- **99%+ reduction in Route API calls** for cached campaigns
- **Access to 7 demographic segments** (all pre-cached)
- **Proper frame validation** (prevent Route API errors)
- **Correct handling of large campaigns** (>10k frames)

---

## 📊 Current State Assessment

### What We Have ✅

**Infrastructure:**
- Database connection with MS-01 switcher (`USE_MS01_DATABASE`)
- Route API client with TTL cache (`src/api/route_client.py`)
- Database helper modules (`src/db/ms01_helpers.py`, `src/db/streamlit_queries.py`)
- Two Streamlit apps (`app_demo.py`, `app_api_real.py`)

**Pipeline Cache (MS-01):**
- 252.7M demographic records (`cache_route_impacts_15min_by_demo`)
- 11,363 campaign reach records (`cache_campaign_reach_day/week/full`)
- 17,406 brand reach records (`cache_campaign_brand_reach`)
- 826 campaigns fully cached (Aug 6 - Oct 13, 2025)
- Daily refresh at 2am UTC

### What's Missing ❌

**Critical Gaps:**
1. **Not querying PostgreSQL cache** - POC calls Route API directly
2. **No frame validation** - Will cause error 220 for invalid frames
3. **No grouping logic** - Will fail for campaigns >10k frames
4. **No impacts multiplication** - Cache stores in thousands
5. **No demographic breakdown** - Not using 7 cached segments

**Impact:**
- 99% unnecessary API calls (slow, expensive)
- Route API errors for some campaigns
- Missing demographic insights
- Suboptimal user experience

---

## 🏗️ Architecture Design

### Cache-First Pattern

```
┌─────────────────────────────────────────────────────────────┐
│                    POC Application                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                   ┌──────────────────┐
                   │  Campaign Query  │
                   └──────────────────┘
                              │
                              ▼
            ┌─────────────────────────────────┐
            │ Check PostgreSQL Cache (MS-01)  │
            │ • cache_route_impacts_15min     │
            │ • cache_campaign_reach_*        │
            │ • cache_campaign_brand_reach    │
            └─────────────────────────────────┘
                              │
                    ┌─────────┴──────────┐
                    │                    │
              Cache HIT ✅          Cache MISS ❌
                    │                    │
                    ▼                    ▼
         ┌──────────────────┐   ┌──────────────────┐
         │ Return Cached    │   │ Validate Frames  │
         │ Data (<5ms)      │   │ (/rest/framedata)│
         └──────────────────┘   └──────────────────┘
                                          │
                                          ▼
                                ┌──────────────────┐
                                │ Check Frame Count│
                                │ (10k threshold)  │
                                └──────────────────┘
                                          │
                           ┌──────────────┴──────────────┐
                           │                             │
                   ≤10,000 frames                >10,000 frames
                 (can use grouping)           (no grouping allowed)
                           │                             │
                           ▼                             ▼
                  ┌─────────────────┐        ┌─────────────────┐
                  │ Call Route API  │        │ Call Route API  │
                  │ WITH grouping   │        │ WITHOUT grouping│
                  │ (per-frame)     │        │ (aggregate)     │
                  └─────────────────┘        └─────────────────┘
                           │                             │
                           └──────────────┬──────────────┘
                                          ▼
                                ┌──────────────────┐
                                │ (Optional) Store │
                                │ in Cache         │
                                └──────────────────┘
                                          │
                                          ▼
                                ┌──────────────────┐
                                │ Return to User   │
                                └──────────────────┘
```

### Data Flow

**For Cached Campaign (80%+ of queries):**
1. User requests campaign audience data
2. POC queries `cache_route_impacts_15min_by_demo`
3. PostgreSQL returns results in <5ms
4. Impacts multiplied by 1000
5. Data displayed in UI
6. **Total time: <500ms**

**For Uncached Campaign (20% of queries):**
1. User requests campaign audience data
2. Cache query returns empty
3. POC retrieves frames from `mv_playout_15min`
4. POC validates frames via `/rest/framedata` (prevents error 220)
5. POC checks frame count (10k threshold)
6. POC calls Route API (with or without grouping)
7. Results returned and (optionally) cached
8. Data displayed in UI
9. **Total time: 5-30s** (acceptable for cache miss)

---

## 🔧 Technical Implementation

### Module Structure

```
src/
├── db/
│   ├── __init__.py
│   ├── ms01_helpers.py         # Existing - async connection pool
│   ├── streamlit_queries.py    # Existing - sync queries
│   └── cache_queries.py        # NEW - cache-specific queries
│
├── api/
│   ├── __init__.py
│   ├── route_client.py         # UPDATE - add frame validation + cache check
│   └── space_client.py         # Existing - SPACE API client
│
├── services/
│   ├── __init__.py
│   └── campaign_service.py     # UPDATE - cache-first pattern
│
├── ui/
│   ├── app_demo.py             # UPDATE - add cache status
│   ├── app_api_real.py         # UPDATE - add demographics
│   └── components/             # UPDATE - demographic charts
│
└── utils/
    ├── __init__.py
    └── validators.py           # NEW - frame validation logic
```

### Key Functions to Implement

#### 1. Cache Queries (`src/db/cache_queries.py`)

```python
def query_demographic_cache(
    campaign_id: str,
    start_date: datetime,
    end_date: datetime,
    demographic_segments: Optional[List[str]] = None,
    use_ms01: bool = True
) -> Optional[pd.DataFrame]:
    """
    Query cached demographic data from PostgreSQL.

    Args:
        campaign_id: Campaign reference ID
        start_date: Start datetime (inclusive)
        end_date: End datetime (exclusive)
        demographic_segments: List of segments or None for all 7
        use_ms01: Use MS-01 database (default True for cache)

    Returns:
        DataFrame with columns: [time_window_start, demographic_segment, impacts]
        None if cache miss or error

    Example:
        df = query_demographic_cache('18425', '2025-10-06', '2025-10-07')
        # Returns ~672 rows (96 windows/day × 7 demographics)
    """
    # CRITICAL: Must multiply impacts by 1000!
    query = """
        SELECT
            time_window_start,
            demographic_segment,
            impacts * 1000 as impacts
        FROM cache_route_impacts_15min_by_demo
        WHERE campaign_id = %s
          AND time_window_start >= %s
          AND time_window_start < %s
    """

    if demographic_segments:
        query += " AND demographic_segment = ANY(%s)"
        params = (campaign_id, start_date, end_date, demographic_segments)
    else:
        params = (campaign_id, start_date, end_date)

    query += " ORDER BY time_window_start, demographic_segment"

    try:
        conn = get_db_connection(use_ms01=use_ms01)
        df = pd.read_sql(query, conn, params=params)
        conn.close()

        if df.empty:
            logger.info(f"Cache MISS for campaign {campaign_id}")
            return None

        logger.info(f"Cache HIT for campaign {campaign_id} - {len(df)} rows")
        return df

    except Exception as e:
        logger.warning(f"Cache query failed for campaign {campaign_id}: {e}")
        return None


def query_campaign_reach_cache(
    campaign_id: str,
    aggregation_level: str = 'day',
    use_ms01: bool = True
) -> Optional[pd.DataFrame]:
    """
    Query cached campaign reach metrics.

    Args:
        campaign_id: Campaign reference ID
        aggregation_level: 'day', 'week', or 'full'
        use_ms01: Use MS-01 database (default True)

    Returns:
        DataFrame with columns: [date, reach, grp, frequency, total_impacts, ...]
        None if cache miss
    """
    table_map = {
        'day': 'cache_campaign_reach_day',
        'week': 'cache_campaign_reach_week',
        'full': 'cache_campaign_reach_full'
    }

    table = table_map.get(aggregation_level)
    if not table:
        raise ValueError(f"Invalid aggregation_level: {aggregation_level}")

    query = f"""
        SELECT *
        FROM {table}
        WHERE campaign_id = %s
        ORDER BY date
    """

    try:
        conn = get_db_connection(use_ms01=use_ms01)
        df = pd.read_sql(query, conn, params=(campaign_id,))
        conn.close()
        return df if not df.empty else None
    except Exception as e:
        logger.warning(f"Campaign reach cache query failed: {e}")
        return None


def query_brand_reach_cache(
    campaign_id: str,
    brand_id: Optional[str] = None,
    aggregation_level: str = 'full',
    use_ms01: bool = True
) -> Optional[pd.DataFrame]:
    """
    Query cached brand-level reach metrics.

    Args:
        campaign_id: Campaign reference ID
        brand_id: Specific brand ID or None for all brands
        aggregation_level: 'day', 'week', or 'full'
        use_ms01: Use MS-01 database

    Returns:
        DataFrame with brand reach metrics
    """
    query = """
        SELECT *
        FROM cache_campaign_brand_reach
        WHERE campaign_id = %s
          AND aggregation_level = %s
    """

    params = [campaign_id, aggregation_level]

    if brand_id:
        query += " AND brand_id = %s"
        params.append(brand_id)

    query += " ORDER BY reach DESC"

    try:
        conn = get_db_connection(use_ms01=use_ms01)
        df = pd.read_sql(query, conn, params=tuple(params))
        conn.close()
        return df if not df.empty else None
    except Exception as e:
        logger.warning(f"Brand reach cache query failed: {e}")
        return None


def check_campaign_cached(campaign_id: str, use_ms01: bool = True) -> bool:
    """
    Quick check if campaign has cached data.

    Returns:
        True if campaign is in cache, False otherwise
    """
    query = """
        SELECT EXISTS(
            SELECT 1 FROM cache_route_impacts_15min_by_demo
            WHERE campaign_id = %s
            LIMIT 1
        )
    """

    try:
        conn = get_db_connection(use_ms01=use_ms01)
        cursor = conn.cursor()
        cursor.execute(query, (campaign_id,))
        exists = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return exists
    except Exception as e:
        logger.warning(f"Cache check failed: {e}")
        return False


def get_cache_statistics(use_ms01: bool = True) -> Dict[str, Any]:
    """
    Get cache statistics for monitoring.

    Returns:
        Dict with cache size, coverage, freshness
    """
    queries = {
        'total_cached_records': """
            SELECT COUNT(*) FROM cache_route_impacts_15min_by_demo
        """,
        'cached_campaigns': """
            SELECT COUNT(DISTINCT campaign_id) FROM cache_route_impacts_15min_by_demo
        """,
        'date_range': """
            SELECT
                MIN(time_window_start)::date as earliest_date,
                MAX(time_window_start)::date as latest_date
            FROM cache_route_impacts_15min_by_demo
        """,
        'last_refresh': """
            SELECT MAX(cached_at) FROM cache_route_impacts_15min_by_demo
        """
    }

    try:
        conn = get_db_connection(use_ms01=use_ms01)
        cursor = conn.cursor()

        stats = {}
        for key, query in queries.items():
            cursor.execute(query)
            result = cursor.fetchone()
            stats[key] = result[0] if result else None

        cursor.close()
        conn.close()

        return stats
    except Exception as e:
        logger.error(f"Failed to get cache statistics: {e}")
        return {}
```

#### 2. Frame Validation (`src/utils/validators.py`)

```python
import requests
from typing import List, Tuple, Dict
import logging

logger = logging.getLogger(__name__)


def validate_frames(
    frame_ids: List[int],
    route_release_id: int = 56,
    auth: Tuple[str, str] = None,
    headers: Dict[str, str] = None
) -> Tuple[List[int], List[int]]:
    """
    Validate frames exist in Route release.

    Args:
        frame_ids: List of frame IDs to validate
        route_release_id: Route release number (default R56)
        auth: (username, password) tuple for Basic Auth
        headers: HTTP headers including X-Api-Key

    Returns:
        Tuple of (valid_frames, invalid_frames)

    Example:
        valid, invalid = validate_frames([123, 456, 789], route_release_id=56)
        # Returns: ([123, 456], [789])
    """
    if not frame_ids:
        return [], []

    url = 'https://route.mediatelapi.co.uk/rest/framedata'

    payload = {
        "route_release_id": route_release_id,
        "frame_ids": frame_ids
    }

    try:
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            auth=auth,
            timeout=60
        )

        response.raise_for_status()
        data = response.json()

        # Extract valid frame IDs from response
        valid_frames = [f['frame_id'] for f in data.get('frames', [])]
        invalid_frames = [fid for fid in frame_ids if fid not in valid_frames]

        logger.info(
            f"Frame validation: {len(valid_frames)} valid, "
            f"{len(invalid_frames)} invalid out of {len(frame_ids)} total"
        )

        if invalid_frames:
            logger.warning(f"Invalid frames: {invalid_frames[:10]}...")  # Log first 10

        return valid_frames, invalid_frames

    except requests.exceptions.RequestException as e:
        logger.error(f"Frame validation API call failed: {e}")
        # On API failure, assume all frames valid (fallback)
        logger.warning("Falling back to assuming all frames valid")
        return frame_ids, []


def should_use_grouping(frame_count: int, threshold: int = 10000) -> bool:
    """
    Determine if grouping should be used based on frame count.

    Args:
        frame_count: Number of unique frames in campaign
        threshold: Maximum frames allowed with grouping (default 10,000)

    Returns:
        True if grouping is safe to use, False otherwise

    Example:
        should_use = should_use_grouping(5000)  # True
        should_use = should_use_grouping(15000)  # False
    """
    return frame_count <= threshold
```

#### 3. Updated Route Client (`src/api/route_client.py`)

```python
from src.db.cache_queries import query_demographic_cache, check_campaign_cached
from src.utils.validators import validate_frames, should_use_grouping

class RouteAPIClient:
    """Route API client with cache-first pattern and frame validation."""

    def __init__(self):
        self.base_url = "https://route.mediatelapi.co.uk"
        self.auth = self._get_auth()
        self.headers = self._get_headers()
        self.use_cache_first = os.getenv('USE_CACHE_FIRST', 'true').lower() == 'true'

        # Statistics
        self.stats = {
            'cache_hits': 0,
            'cache_misses': 0,
            'api_calls': 0,
            'validation_calls': 0
        }

    def get_campaign_audience(
        self,
        campaign_id: str,
        start_date: datetime,
        end_date: datetime,
        demographics: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Get campaign audience data with cache-first pattern.

        Args:
            campaign_id: Campaign reference ID
            start_date: Start datetime
            end_date: End datetime
            demographics: List of demographic segments or None for all

        Returns:
            DataFrame with audience data
        """
        # STEP 1: Try cache first (if enabled)
        if self.use_cache_first:
            cached_data = query_demographic_cache(
                campaign_id=campaign_id,
                start_date=start_date,
                end_date=end_date,
                demographic_segments=demographics,
                use_ms01=True
            )

            if cached_data is not None:
                self.stats['cache_hits'] += 1
                logger.info(f"✅ Cache HIT for campaign {campaign_id}")
                return cached_data

            self.stats['cache_misses'] += 1
            logger.info(f"⚠️ Cache MISS for campaign {campaign_id} - calling Route API")

        # STEP 2: Cache miss - get frames from database
        frames_df = self._get_campaign_frames(campaign_id, start_date, end_date)

        if frames_df.empty:
            raise ValueError(f"No playout data for campaign {campaign_id}")

        # STEP 3: Validate frames
        frame_ids = frames_df['frameid'].unique().tolist()
        route_release_id = self._determine_route_release(start_date)

        valid_frames, invalid_frames = validate_frames(
            frame_ids=frame_ids,
            route_release_id=route_release_id,
            auth=self.auth,
            headers=self.headers
        )

        self.stats['validation_calls'] += 1

        if not valid_frames:
            raise ValueError(
                f"No valid frames in Route R{route_release_id} for campaign {campaign_id}"
            )

        if invalid_frames:
            logger.warning(
                f"Filtering out {len(invalid_frames)} invalid frames "
                f"from campaign {campaign_id}"
            )
            frames_df = frames_df[frames_df['frameid'].isin(valid_frames)]

        # STEP 4: Check if we should use grouping
        frame_count = len(valid_frames)
        use_grouping = should_use_grouping(frame_count)

        if not use_grouping:
            logger.warning(
                f"Campaign {campaign_id} has {frame_count} frames - "
                f"using non-grouping (aggregate metrics only)"
            )

        # STEP 5: Build Route API payload
        payload = self._build_route_payload(
            frames_df=frames_df,
            route_release_id=route_release_id,
            demographics=demographics,
            use_grouping=use_grouping
        )

        # STEP 6: Call Route API
        response = self._call_route_api(payload)
        self.stats['api_calls'] += 1

        # STEP 7: Parse and return results
        results_df = self._parse_route_response(response, use_grouping)

        return results_df

    def get_stats(self) -> Dict[str, int]:
        """Get client statistics."""
        total_requests = self.stats['cache_hits'] + self.stats['cache_misses']
        cache_hit_rate = (
            self.stats['cache_hits'] / total_requests * 100
            if total_requests > 0 else 0
        )

        return {
            **self.stats,
            'cache_hit_rate_pct': round(cache_hit_rate, 2)
        }

    # ... other helper methods ...
```

---

## 📋 Implementation Checklist

### Phase 1: Discovery & Validation ✅
- [ ] Test MS-01 connection with cache credentials
- [ ] Verify `cache_route_impacts_15min_by_demo` exists (252.7M records)
- [ ] Run example query: `SELECT COUNT(*) FROM cache_route_impacts_15min_by_demo`
- [ ] Verify query performance (<5ms)
- [ ] Test impacts multiplication (×1000)
- [ ] Document connection details in `.env`

### Phase 2: Cache Query Module ✅
- [ ] Create `src/db/cache_queries.py`
- [ ] Implement `query_demographic_cache()`
- [ ] Implement `query_campaign_reach_cache()`
- [ ] Implement `query_brand_reach_cache()`
- [ ] Implement `check_campaign_cached()`
- [ ] Implement `get_cache_statistics()`
- [ ] Add comprehensive error handling
- [ ] Write unit tests (`tests/test_cache_queries.py`)

### Phase 3: Frame Validation ✅
- [ ] Create `src/utils/validators.py`
- [ ] Implement `validate_frames()` function
- [ ] Implement `should_use_grouping()` function
- [ ] Test with known valid frames
- [ ] Test with known invalid frames
- [ ] Test with mixed valid/invalid
- [ ] Add logging for validation results
- [ ] Write unit tests (`tests/test_validators.py`)

### Phase 4: Grouping Logic ✅
- [ ] Add frame count check to Route client
- [ ] Implement grouping decision logic (10k threshold)
- [ ] Add warning logging for large campaigns
- [ ] Test with small campaign (<10k frames)
- [ ] Test with large campaign (>10k frames)
- [ ] Verify no API errors for large campaigns
- [ ] Write unit tests

### Phase 5: Cache-First Integration ✅
- [ ] Add `USE_CACHE_FIRST` environment variable
- [ ] Update `RouteAPIClient` with cache check
- [ ] Update `campaign_service.py` with cache-first pattern
- [ ] Add cache hit/miss statistics tracking
- [ ] Add logging for cache operations
- [ ] Test with cached campaign (verify <500ms)
- [ ] Test with uncached campaign (verify API fallback)
- [ ] Write integration tests

### Phase 6: UI Updates ✅
- [ ] Add cache status indicator to Streamlit app
- [ ] Add demographic selector dropdown (7 segments)
- [ ] Create demographic comparison charts
- [ ] Update metrics cards to show all demographics
- [ ] Add cache statistics display (hit rate, response time)
- [ ] Update export to include all demographics
- [ ] Test UI with cached data
- [ ] Test UI with uncached data

### Phase 7: Testing & Validation ✅
- [ ] Test with 10 cached campaigns
- [ ] Test with 5 uncached campaigns
- [ ] Test with 3 large campaigns (>10k frames)
- [ ] Test with campaigns having invalid frames
- [ ] Performance benchmark: cache vs API
- [ ] Load test: 50 concurrent queries
- [ ] Error scenario: cache unavailable
- [ ] Error scenario: API unavailable
- [ ] Document test results

### Phase 8: Documentation ✅
- [ ] Update `docs/ARCHITECTURE.md`
- [ ] Create `docs/CACHE_INTEGRATION.md`
- [ ] Update `README.md` with cache features
- [ ] Document environment variables
- [ ] Create troubleshooting guide
- [ ] Update API documentation
- [ ] Create handover document for next session

---

## 🚀 Quick Start Commands

### Test Cache Connection

```bash
# Test MS-01 cache access
python -c "
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host='192.168.1.34',
    port=5432,
    database='route_poc',
    user='postgres',
    password=os.getenv('POSTGRES_PASSWORD_MS01')
)

cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM cache_route_impacts_15min_by_demo;')
count = cursor.fetchone()[0]
print(f'✅ Cache has {count:,} records')

cursor.close()
conn.close()
"
```

### Run Example Query

```bash
# Query cached campaign
python -c "
from src.db.cache_queries import query_demographic_cache
import pandas as pd

df = query_demographic_cache(
    campaign_id='18425',
    start_date='2025-10-06',
    end_date='2025-10-07'
)

if df is not None:
    print(f'✅ Retrieved {len(df)} cached records')
    print(df.head())
else:
    print('❌ Campaign not in cache')
"
```

### Validate Frames

```bash
# Test frame validation
python -c "
from src.utils.validators import validate_frames
import os

valid, invalid = validate_frames(
    frame_ids=[1234567890, 9999999999],
    route_release_id=56
)

print(f'Valid: {len(valid)}, Invalid: {len(invalid)}')
"
```

---

## 📊 Success Metrics

### Performance Targets

| Metric | Target | Current (Before) | Expected (After) |
|--------|--------|------------------|------------------|
| Avg query time (cached) | <500ms | 5-30s | <500ms | ✅
| Avg query time (uncached) | 5-30s | 5-30s | 5-30s | ✅
| Cache hit rate | >80% | 0% | >80% | ✅
| API calls per 100 queries | <20 | 100 | <20 | ✅
| Frame validation time | <2s | N/A | <2s | ✅
| Failed queries (error 220) | 0 | Variable | 0 | ✅

### Quality Targets

- ✅ All unit tests passing (>80% coverage)
- ✅ All integration tests passing
- ✅ Zero breaking changes to existing functionality
- ✅ Backward compatibility maintained
- ✅ Comprehensive error handling
- ✅ Informative logging at all levels

---

## ⚠️ Risk Management

### High Risk Items

1. **Breaking Existing POC Functionality**
   - Mitigation: Feature flag `USE_CACHE_FIRST=false` (default off initially)
   - Rollback: Quick disable via environment variable

2. **Cache Query Performance Issues**
   - Mitigation: Always include time filters, test with EXPLAIN ANALYZE
   - Contingency: Optimize queries, add indexes, contact pipeline team

3. **Missing Credentials (MS01_DB_PASSWORD)**
   - Mitigation: Request immediately from pipeline team
   - Contingency: Develop with local database, sample data

### Medium Risk Items

4. **Frame Validation Latency**
   - Mitigation: Cache validation results (1hr TTL)
   - Contingency: Make validation optional via config

5. **Demographic Data Format Issues**
   - Mitigation: Extensive testing with sample data first
   - Contingency: Add data transformation layer

### Low Risk Items

6. **Large Campaign Complexity**
   - Mitigation: Start with non-grouping only
   - Contingency: Document limitations, add batching later

---

## 📅 Timeline

### Day 1 (6-8 hours)
- **Morning**: Phase 1 + Phase 2 (cache queries)
- **Afternoon**: Phase 3 (frame validation)
- **End of day**: Working cache query module with frame validation

### Day 2 (6-8 hours)
- **Morning**: Phase 4 (grouping logic) + Phase 5 (cache-first integration)
- **Afternoon**: Phase 6 (UI updates)
- **End of day**: Fully integrated cache-first POC

### Day 3 (4-7 hours)
- **Morning**: Phase 7 (comprehensive testing)
- **Afternoon**: Phase 8 (documentation)
- **End of day**: Production-ready cache integration

**Total**: 16-23 hours over 2-3 days

---

## 🎯 Next Steps

**Immediate (Today):**
1. Request `MS01_DB_PASSWORD` from pipeline team
2. Test MS-01 cache connection
3. Run example queries from pipeline docs
4. Verify 252.7M records exist

**Tomorrow (Day 1):**
1. Create `src/db/cache_queries.py`
2. Implement cache query functions
3. Test with real campaign data
4. Implement frame validation

**Day 2-3:**
1. Integrate cache-first pattern
2. Update UI with demographics
3. Comprehensive testing
4. Documentation

---

**Status**: 📋 Ready to Execute
**Confidence Level**: High (clear plan, well-defined scope)
**Blockers**: MS01_DB_PASSWORD credential (requested)
**Estimated Completion**: 2-3 days focused work

---

**Document Owner**: Claude Code / Ian Wyatt
**Last Updated**: 2025-11-14
**Next Review**: After Phase 5 completion
