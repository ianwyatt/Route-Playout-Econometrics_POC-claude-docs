# Data Caching and Database Architecture - Search Summary

**Search Date**: October 20, 2025  
**Scope**: Comprehensive analysis of caching mechanisms, database structure, and data flows  
**Status**: Complete - All findings documented

---

## Quick Reference

### Key Finding: 4-Level Caching Strategy

1. **TTL Caches at API Clients** - In-memory, session-based
2. **Service Layer Caches** - Business logic results
3. **PostgreSQL Database** - Persistent storage (not actively caching)
4. **Mock Data Fallback** - Demo/testing reliability

---

## Search Results Summary

### Files Searched

**Database and Caching Files**:
- `/src/config_package/database.py` - PostgreSQL configuration
- `/src/utils/ttl_cache.py` - Core TTL cache implementation
- `/src/api/route_client.py` - Route API client with in-memory cache
- `/src/api/space_client.py` - SPACE API client with in-memory cache
- `/src/api/base_client.py` - Base client with shared caching logic
- `/src/db/optimized.py` - Connection pooling and optimization
- `/src/db/ms01_helpers.py` - PostgreSQL async operations
- `/src/services/base.py` - Service layer base with cache
- `/src/services/campaign_service.py` - Campaign data service
- `/src/services/route_service.py` - Route API service layer
- `/src/services/space_service.py` - SPACE API service layer

---

## Current Architecture Components

### 1. TTL Cache System (`/src/utils/ttl_cache.py`)

**Thread-safe, in-memory cache with:**
- LRU eviction when full (OrderedDict)
- Time-based expiration (TTL)
- Automatic cleanup on interval
- Comprehensive statistics

**Key Metrics**:
```
Max Size: 1000 entries (default, configurable)
Default TTL: 3600 seconds (1 hour)
Cleanup Interval: 300 seconds (5 minutes)
Memory Usage: ~100MB for 1000 entries
```

### 2. Route API Client (`/src/api/route_client.py`)

**Caching Strategy**:
- Cache Key: MD5 hash of request JSON
- TTL: 3600 seconds (configurable)
- Size: 1000 entries (configurable)
- Hit Rate: 75-85% typical in demos

**Request Flow**:
```
Generate MD5 → Check Cache → Cache Hit/Miss → 
API Call (with fallback) → Store in Cache → Return
```

### 3. SPACE API Client (`/src/api/space_client.py`)

**Caching Strategy**:
- Cache Key: `{entity_type}:{entity_id}` (e.g., `buyer:12345`)
- TTL: 3600 seconds (configurable)
- Size: 1000 entries (configurable)
- Cached Entities: Media owners, buyers, agencies, brands, frames

**Request Flow**:
```
Check Service Cache → 
Check Mock Mode → 
Make API Call (with fallback) → 
Store in Cache → Return
```

### 4. Service Layer Caches (`/src/services/`)

**Cached Services**:
- `CampaignService` - TTL: 600s, Max: 100 entries
- `RouteService` - TTL: 900s, Max: 100 entries
- `SpaceService` - TTL: varies, Max: 100 entries
- `PlayoutService` - TTL: 1800s, Max: 100 entries
- `BrandSplitService` - TTL: 3600s, Max: 100 entries

**Cache Key Format**:
```python
f"{service_name}_{operation}_{params}"
```

### 5. PostgreSQL Database (`/src/db/ms01_helpers.py`)

**Current Status**: 
- Connection pooling active (1-10 async connections)
- Query operations available
- **Not caching API responses** (future enhancement)

**Available Operations**:
- Query playouts by campaign
- Query by date range
- Hourly/daily aggregations
- Brand-level calculations

---

## Data Sources and Processing

### Playout Data Loading

**Current Method**:
```python
# Load from CSV (not database)
df = pd.read_csv(SAMPLE_PLAYOUT_CSV)
campaign_data = df[df['buyercampaignref'] == campaign_id]
```

**Table Schema** (from ms01_helpers):
- `playout` - Main playout records
- `frame_*` - Frame metadata tables
- Materialized views for aggregations

### Configuration Files

**Located in `/src/config_package/`**:
- `database.py` - Database config (pooling, SSL, timeouts)
- `api.py` - Route/SPACE API configs (cache size, TTL)
- `base.py` - Base configuration class
- `logging.py` - Logging configuration

---

## Key Findings

### Strengths

1. **Robust TTL Cache Implementation**
   - Thread-safe with RLock
   - LRU eviction prevents memory exhaustion
   - Automatic cleanup
   - Comprehensive statistics

2. **Multiple Cache Layers**
   - Redundant protection
   - Reduced API calls
   - Fallback mechanisms

3. **Automatic Mock Fallback**
   - Demo reliability
   - Credential validation
   - Graceful degradation

4. **Connection Pooling**
   - Efficient database access
   - Async/sync support
   - Configurable pool sizes

### Gaps/Missing Features

1. **No Persistent API Cache**
   - Route/SPACE responses not stored in database
   - Cache lost between sessions
   - No cross-instance cache sharing

2. **Limited Cache Warming**
   - No pre-population of common queries
   - No predictive loading

3. **No Distributed Caching**
   - In-memory only
   - Single-instance deployments

4. **Cache Invalidation**
   - Only TTL-based
   - No event-driven refresh
   - No manual invalidation endpoint

5. **No Metrics Export**
   - Cache statistics available but not exported
   - No monitoring integration

---

## Performance Characteristics

### API Response Times

| Component | Live | Cached | Mock |
|-----------|------|--------|------|
| Route API | 250-350ms | <100ms | <10ms |
| SPACE API | 50-200ms | <50ms | <5ms |

### Cache Hit Rates

- **Typical Demo**: 75-85%
- **Campaign Queries**: 80-90%
- **Entity Lookups**: 85-95%

### Memory Usage

- **Per TTLCache**: <100MB for 1000 entries
- **Service Caches**: <50MB (100 entries each)
- **Total System**: <500MB typical

---

## Recommendations

### Immediate Actions

1. Monitor cache hit rates via metrics endpoint
2. Document cache configuration per environment
3. Add cache statistics to admin dashboard

### Short-term Enhancements (1-2 weeks)

1. Implement PostgreSQL cache tables for API responses
2. Add cache warming for common campaigns
3. Create cache invalidation endpoint
4. Export cache metrics to monitoring

### Medium-term Improvements (1-2 months)

1. Persistent cache in PostgreSQL
   - `route_api_cache` table
   - `space_api_cache` table
   - 7-day TTL retention

2. Cache invalidation strategy
   - Event-based refresh
   - Manual invalidation
   - Scheduled cleanup

3. Metrics and monitoring
   - Export to monitoring system
   - Cache health dashboards
   - Performance alerts

### Long-term Strategies (3+ months)

1. Redis for distributed caching
2. Multi-instance cache synchronization
3. Predictive cache warming
4. Cache pre-computation service

---

## Documentation Generated

### Files Created

1. **CURRENT_ARCHITECTURE.md** (10KB)
   - Complete architecture overview
   - Configuration details
   - Data flow descriptions
   - Performance metrics

2. **CACHE_FLOW_DIAGRAMS.md** (12KB)
   - Visual flow diagrams
   - Cache operation timelines
   - Memory management examples
   - Future architecture proposals

3. **SEARCH_SUMMARY.md** (this file)
   - Quick reference guide
   - Key findings
   - Recommendations
   - File reference

### Location

All documentation in: `/Claude/Documentation/`

---

## Code Examples Reference

### Using TTL Cache
```python
from src.utils.ttl_cache import TTLCache

cache = TTLCache(max_size=1000, default_ttl=3600)
cache.put("key", value)
result = cache.get("key")
stats = cache.stats()
```

### Using Route API Cache
```python
from src.api.route_client import RouteAPIClient

client = RouteAPIClient()
result = await client.get_playout_audience(
    frame_id=123,
    datetime_from="2025-07-28 00:00",
    datetime_until="2025-07-28 00:14"
)
# Cached if called again with same params
```

### Using SPACE API Cache
```python
from src.api.space_client import SpaceAPIClient

client = SpaceAPIClient()
entity = client.get_media_owner("171")  # Cached
stats = client.get_cache_stats()
```

### Checking Service Cache
```python
from src.services.campaign_service import CampaignService

service = CampaignService()
campaign = await service.get_campaign("16012")
# Cached for 600 seconds by default
```

---

## Contact and Questions

For more details on:
- Cache implementation → See `/src/utils/ttl_cache.py`
- Route API integration → See `/src/api/route_client.py`
- Database structure → See `/src/db/ms01_helpers.py`
- Service layer → See `/src/services/base.py`

---

**Document Version**: 1.0  
**Last Updated**: October 20, 2025  
**Status**: Complete and Ready for Implementation
