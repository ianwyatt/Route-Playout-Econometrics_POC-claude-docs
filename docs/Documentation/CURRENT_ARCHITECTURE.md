# Current Data Caching and Database Architecture

**Document Created**: October 20, 2025
**Status**: Snapshot of current implementation

## Executive Summary

The Route Playout Econometrics POC implements a **layered caching strategy** with in-memory TTL caches at the API client level and potential PostgreSQL integration for persistent data. The system uses **two primary API clients** (Route and SPACE) with automatic mock fallback for demo reliability.

## Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     UI LAYER (Streamlit)                        │
├─────────────────────────────────────────────────────────────────┤
│  ▼
├─────────────────────────────────────────────────────────────────┐
│              SERVICE LAYER (Business Logic)                     │
│  • CampaignService - High-level campaign operations             │
│  • RouteService - Route API orchestration                       │
│  • SpaceService - SPACE API orchestration                       │
│  • PlayoutService - Playout data processing                     │
│  • BrandSplitService - Brand-level calculations                 │
├─────────────────────────────────────────────────────────────────┤
│  ▼
├─────────────────────────────────────────────────────────────────┐
│              API CLIENT LAYER (External APIs)                   │
│  • RouteAPIClient (TTL Cache - 3600s default)                   │
│  • SpaceAPIClient (TTL Cache - 3600s default)                   │
│  • Base client with shared retry/fallback logic                 │
├─────────────────────────────────────────────────────────────────┤
│  ▼
├─────────────────────────────────────────────────────────────────┐
│          DATABASE LAYER (PostgreSQL - MS-01 or Local)           │
│  • MS01DatabaseConnection - Async connection pooling            │
│  • QueryOptimizer - Batch queries and optimization              │
│  • ConnectionPool - asyncpg and psycopg2 pooling                │
└─────────────────────────────────────────────────────────────────┘
```

## Caching Architecture

### Level 1: API Client In-Memory Caches

**Purpose**: Prevent redundant API calls during a session

#### RouteAPIClient Cache
- **File**: `/src/api/route_client.py`
- **Cache Implementation**: `TTLCache` (in-memory)
- **Size**: Configurable via `route_config.cache_size` (default: 1000 entries)
- **TTL**: Configurable via `route_config.cache_ttl` (default: 3600 seconds)
- **Key Format**: MD5 hash of request JSON data
- **Cache Strategy**:
  ```python
  cache_key = self._cache_key(request_data)  # MD5 of JSON
  cached = self.cache.get(cache_key)         # Check cache
  if cached:
      cached['from_cache'] = True
      return cached
  # Otherwise make API call
  response = await self._real_api_call_with_fallback(request_data)
  self.cache.put(cache_key, response)        # Cache result
  ```

#### SpaceAPIClient Cache
- **File**: `/src/api/space_client.py`
- **Cache Implementation**: `TTLCache` (in-memory)
- **Size**: Configurable via `space_config.cache_size` (default: 1000 entries)
- **TTL**: Configurable via `space_config.cache_ttl` (default: 3600 seconds)
- **Key Format**: `{entity_type}:{entity_id}` (e.g., `media_owner:171`)
- **Cached Entity Types**:
  - Media owners: `media_owner:{id}` → cached as `SpaceEntity`
  - Buyers: `buyer:{id}` → cached as `SpaceEntity`
  - Agencies: `agency:{id}` → cached as `SpaceEntity`
  - Brands: `brand:{id}` → cached as `SpaceEntity`
  - Frames: `frame:{id}` → cached as dict

#### TTLCache Implementation
- **File**: `/src/utils/ttl_cache.py`
- **Features**:
  - Thread-safe with `RLock`
  - LRU eviction when full (OrderedDict)
  - Time-based expiration
  - Automatic cleanup on configurable interval (default: 300 seconds)
  - Comprehensive statistics (hits, misses, evictions, expired removals)
- **Configuration**:
  ```python
  cache = TTLCache(
      max_size=1000,           # Max entries before LRU eviction
      default_ttl=3600.0,      # 1 hour TTL
      cleanup_interval=300.0   # Cleanup every 5 minutes
  )
  ```

### Level 2: Service Layer Cache

**Purpose**: Cache processed business logic results

**File**: `/src/services/base.py`

Each service inherits `BaseService` with:
- In-memory dictionary cache: `self._cache`
- Cache entries: `CacheEntry(data, ttl, expires_at)`
- TTL configurable per service (default: 300-3600 seconds)
- Cache methods:
  ```python
  self.set_cache(key, value, ttl)
  cached = self.get_from_cache(key)
  ```

**Services Using Cache**:
- `CampaignService` (cache_ttl=600s) - Campaign query results
- `RouteService` (cache_ttl=900s) - Playout audience data
- `SpaceService` - Entity lookup results
- `PlayoutService` (cache_ttl=1800s) - Playout processing results
- `BrandSplitService` (cache_ttl=3600s) - Brand proportion calculations

### Level 3: PostgreSQL Database (Persistent Cache)

**Current Status**: Database layer exists but not actively caching API responses

#### Database Connection
- **File**: `/src/db/ms01_helpers.py`
- **Type**: Async connection pooling with `asyncpg`
- **Configuration**:
  ```python
  min_connections: 1
  max_connections: 10
  command_timeout: 60s
  ```

#### Available Database Operations
- Query campaign playouts from `playout` table
- Join with frame data
- Brand-level aggregations
- Date-based filtering
- Hourly and daily summaries

#### Database Tables (Inferred from Queries)
- `playout` - Playout records with frame_id, campaign_id, times, spot lengths
- `route_cache` (potential) - Cached Route API responses
- `space_cache` (potential) - Cached SPACE API responses
- Materialized views for aggregations

### Level 4: Mock Data Fallback

**Purpose**: Ensure demo/testing reliability

**Fallback Logic**:
1. API Request Made
2. If timeout/error → Automatic fallback to mock data
3. Mock data generated with realistic parameters
4. Marked with `demo_fallback: True` or `demo_mode: True`

**Implementation**:
- RouteAPIClient: `_generate_fallback_audience_data()` - Uses frame_id for seed
- SpaceAPIClient: `_get_mock_entity_data()` - Returns from mock entity config
- BaseAPIClient: `_get_mock_fallback()` - Abstract method

## Configuration Management

### Cache Configuration
- **File**: `/src/config_package/api.py`
- **Route Config**:
  ```python
  cache_size: 1000
  cache_ttl: 3600  # 1 hour
  default_spot_length: 10  # seconds
  ```

- **Space Config**:
  ```python
  cache_size: 1000
  cache_ttl: 3600  # 1 hour
  demo_timeout: 5.0  # seconds
  ```

### Database Configuration
- **File**: `/src/config_package/database.py`
- **Query Cache**:
  ```python
  query_cache_enabled: True
  query_cache_ttl: 300.0  # 5 minutes
  query_cache_size: 100
  ```

- **Connection Pool**:
  ```python
  min_pool_size: 2
  max_pool_size: 10
  pool_timeout: 30.0
  idle_timeout: 600.0  # 10 minutes
  ```

## Data Sources and Flow

### Route API Data Flow

1. **UI Entry**: User enters campaign ID in Streamlit app
2. **Campaign Service**: `query_campaign(campaign_id)`
3. **Playout Processor**: Loads playouts from CSV or database
4. **Route Client (Batch)**: Groups playouts into 15-min dayparts
5. **Route Client (Cache)**: Check cache for each frame/timeframe
6. **Route API Call**: If cache miss → POST to `/rest/process/playout`
7. **Cache Store**: Cache response with MD5 key
8. **Return**: With audience metrics (impacts, reach, frequency, GRPs)

### SPACE API Data Flow

1. **Campaign Service**: Processing playouts
2. **Enrichment**: Need entity names (buyer, agency, brand, media owner)
3. **Space Client (Lookup)**: Check cache for entity
4. **Space API Call**: If cache miss → GET `/media-owners/{id}` etc
5. **Cache Store**: Cache entity data
6. **Return**: Entity name/details

### Database Query Flow

**Current Pattern**: Load playouts from CSV, not database
```python
# In CampaignService._load_playout_data()
self.playout_data = pd.read_csv(SAMPLE_PLAYOUT_CSV)
# Filter by campaign_id
campaign_data = self.playout_data[
    self.playout_data['buyercampaignref'] == float(campaign_id)
]
```

**Potential Database Pattern** (not yet implemented):
```python
# Query playout data from PostgreSQL
SELECT * FROM playout 
WHERE buyercampaignref = $1 
AND startdate >= $2 AND startdate <= $3
ORDER BY startdate
```

## Current Cache Metrics and Monitoring

### Cache Statistics Available

#### TTLCache Stats
```python
cache.stats() returns:
{
    'size': 42,                    # Current entries
    'max_size': 1000,             # Max capacity
    'expired_entries': 0,         # Expired but not cleaned
    'memory_utilization': 4.2,    # Percentage
    'hits': 150,                  # Cache hits
    'misses': 25,                 # Cache misses
    'hit_rate_percent': 85.7,     # Hit rate
    'evictions': 5,               # LRU evictions
    'expired_removals': 2,        # Cleanup removals
    'default_ttl_seconds': 3600,
    'cleanup_interval_seconds': 300,
    'last_cleanup': 1697829600.0,
    'time_since_last_cleanup': 45.2
}
```

#### API Client Metrics
```python
route_client.get_metrics() returns:
{
    'api_name': 'Route API',
    'request_count': 50,
    'cache_hits': 150,
    'cache_hit_rate': 75.0,       # Of total requests
    'avg_response_time': 0.245,   # seconds
    'total_response_time': 12.25
}
```

## Credential and Mock Mode Handling

### Automatic Mock Activation
- **File**: `/src/utils/credentials.py`
- **Logic**:
  ```python
  if credentials_missing or credentials_invalid:
      force_mock_mode = True
  ```

- **Route Client Initialization**:
  ```python
  self.use_mock = credentials_force_mock or self.config.use_mock
  if self.use_mock:
      logger.info("🎭 Route API using mock mode")
  else:
      logger.info("✅ Route API credentials validated - live mode available")
  ```

## Missing/Future Implementations

### Database Caching (Planned)
1. **Route API Cache Table**: Store API responses indexed by request hash
2. **SPACE API Cache Table**: Cache entity lookups with 30-day TTL
3. **Query Optimization**: Use database cache for historical data
4. **Cache Invalidation**: TTL-based cleanup or manual refresh

### Improvements Needed
1. **Database Integration**: Persist Route/SPACE cache to PostgreSQL
2. **Cache Warming**: Pre-populate cache on startup for common queries
3. **Distributed Caching**: Redis for multi-instance deployments
4. **Cache Invalidation Strategy**: How/when to refresh stale data
5. **Metrics Export**: Send cache stats to monitoring systems

## Key Files Reference

| File | Purpose | Cache Type |
|------|---------|-----------|
| `/src/utils/ttl_cache.py` | TTL cache implementation | In-memory, TTL-based |
| `/src/api/route_client.py` | Route API client with cache | TTLCache (1000 entries, 1hr TTL) |
| `/src/api/space_client.py` | SPACE API client with cache | TTLCache (1000 entries, 1hr TTL) |
| `/src/api/base_client.py` | Base client with retry/cache | TTLCache base |
| `/src/services/base.py` | Service layer base with cache | Dict-based, TTL-managed |
| `/src/services/campaign_service.py` | Campaign query service | Service layer cache |
| `/src/services/route_service.py` | Route orchestration service | Service layer cache |
| `/src/services/space_service.py` | SPACE orchestration service | Service layer cache |
| `/src/db/ms01_helpers.py` | PostgreSQL async operations | Connection pooling |
| `/src/db/optimized.py` | DB optimization utilities | Connection pool stats |
| `/src/config_package/database.py` | Database configuration | Config (no caching) |
| `/src/config_package/api.py` | API configuration | Config (no caching) |

## Performance Characteristics

### Current Performance
- **Route API**: ~250-350ms per request (live), <100ms (cached/mock)
- **SPACE API**: ~50-200ms per lookup (live), <50ms (cached/mock)
- **Cache Hit Rate**: 75-85% typical in demo scenarios
- **Memory Usage**: Minimal (<100MB for 1000 cache entries)

### Bottlenecks
1. **Network I/O**: Real API calls are slowest component
2. **Batch Processing**: 15-min daypart grouping can be large
3. **No Database Cache**: Repeated queries to PostgreSQL for same campaigns
4. **Service Layer Cache**: Not shared across requests (per-instance only)

## Recommendations

### Short Term
1. Monitor cache hit rates and TTL effectiveness
2. Add cache warming for frequently-accessed campaigns
3. Implement database-backed cache for Route API responses

### Medium Term
1. Persistent cache in PostgreSQL for API responses
2. Cache invalidation strategy (time-based or event-based)
3. Metrics export to monitoring dashboard

### Long Term
1. Redis for distributed caching across instances
2. Cache pre-computation for known scenarios
3. Predictive cache warming based on user patterns

---

**Last Updated**: October 20, 2025
**Next Review**: After database integration implementation
