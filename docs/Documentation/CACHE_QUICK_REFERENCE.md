# Cache Architecture - Quick Reference Card

## 4-Level Cache Strategy

```
┌──────────────────────────────────┐
│ LEVEL 1: API Client Caches       │ In-memory TTL
│ Route: 1000 entries, 3600s TTL   │ 75-85% hit rate
│ SPACE: 1000 entries, 3600s TTL   │ 85-95% hit rate
├──────────────────────────────────┤
│ LEVEL 2: Service Layer Caches    │ In-memory TTL
│ Campaign: 600s                   │ Per-service cache
│ Route: 900s                      │ Max 100 entries
│ Space: varies                    │ Max 100 entries
├──────────────────────────────────┤
│ LEVEL 3: PostgreSQL Database     │ Connection pool
│ Async pooling: 1-10 connections  │ (Future: API cache)
│ Query optimization available     │ (Future: 7-day TTL)
├──────────────────────────────────┤
│ LEVEL 4: Mock Data Fallback      │ Automatic safety
│ Demo reliability guarantee       │ Graceful degradation
└──────────────────────────────────┘
```

---

## Cache File Locations

| Component | Location | Type |
|-----------|----------|------|
| Core Cache | `/src/utils/ttl_cache.py` | TTLCache class |
| Route API | `/src/api/route_client.py` | TTLCache instance |
| SPACE API | `/src/api/space_client.py` | TTLCache instance |
| Base Client | `/src/api/base_client.py` | TTLCache base |
| Services | `/src/services/base.py` | Dict-based cache |
| Config | `/src/config_package/api.py` | Cache settings |
| Database | `/src/db/ms01_helpers.py` | Connection pool |

---

## Quick Commands

### Check Cache Stats
```python
# Route API cache
route_client.get_cache_stats()
# Returns: {hits, misses, hit_rate, evictions, size, ...}

# SPACE API cache
space_client.get_cache_stats()

# Service cache (not directly available)
```

### Clear Caches
```python
route_client.clear_cache()
space_client.clear_cache()
```

### Check API Metrics
```python
route_client.get_metrics()
# Returns: {request_count, cache_hits, cache_hit_rate, avg_response_time}
```

---

## Configuration

### Environment Variables

```bash
# Route API Cache
ROUTE_CACHE_SIZE=1000
ROUTE_CACHE_TTL=3600

# SPACE API Cache
SPACE_CACHE_SIZE=1000
SPACE_CACHE_TTL=3600

# Database
USE_MS01_DATABASE=true
POSTGRES_MAX_POOL=10
```

### Code Configuration

```python
# Cache config in /src/config_package/api.py
route_config = RouteConfig(
    cache_size=1000,      # max entries
    cache_ttl=3600        # seconds
)

space_config = SpaceConfig(
    cache_size=1000,
    cache_ttl=3600
)

# Service cache (in each service)
campaign_service = CampaignService(cache_ttl=600)
route_service = RouteService(cache_ttl=900)
```

---

## Cache Key Formats

### Route API
```
MD5(json.dumps(request_data))
Example: "a7f3e2d1c9f4b5e8a1d2c3f4e5d6c7b8"
```

### SPACE API
```
"{entity_type}:{entity_id}"
Examples:
  "media_owner:171"
  "buyer:12345"
  "agency:5678"
  "brand:9999"
  "frame:1234567890"
```

### Service Layer
```
"{service_name}_{operation}_{params}"
Example: "campaign_16012_None_None_day"
```

---

## Cache Behavior

### On Cache Miss
```
1. Check mock mode
2. Make API call (with retry logic)
3. Store in cache
4. Return result
Time: 250-350ms (API dependent)
```

### On Cache Hit
```
1. Check expiration
2. Return cached data
3. Update hit counter
4. Move to LRU end
Time: <1ms
```

### On Cache Full
```
1. LRU eviction triggered
2. Remove least recently used
3. Add new entry
4. Update statistics
```

---

## Typical Hit Rates

| Scenario | Hit Rate | Note |
|----------|----------|------|
| Campaign lookup | 80-90% | Same campaign queries |
| Entity lookup | 85-95% | Same entities frequently |
| Frame data | 70-80% | Different frames |
| Overall | 75-85% | Typical demo scenario |

---

## Performance Impact

### Without Cache
```
Campaign 16012 (50 playouts):
- Route API calls: 50 × 250ms = 12.5s
- SPACE API calls: 10 × 100ms = 1s
- Total: ~13.5s
```

### With Cache (first request)
```
Same as without cache: ~13.5s
(All requests made, all cached)
```

### With Cache (subsequent requests)
```
Campaign 16012 (50 playouts):
- Cache hits: 42 × <1ms = <50ms
- Cache misses: 8 × 250ms = 2s
- Total: ~2-2.5s
- Speedup: 6-7x faster ✓
```

---

## Common Issues and Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| Slow requests | Cache miss | Check cache TTL, warm cache |
| Memory growth | Cache not evicting | Check LRU, monitor hits |
| Stale data | Long TTL | Reduce cache_ttl value |
| Inconsistent results | Cache timing | Use cache stats to debug |
| API failures | Fallback to mock | Check credentials, logs |

---

## Monitoring and Debugging

### Cache Statistics
```python
cache.stats()
{
    'size': 45,
    'max_size': 1000,
    'hit_rate_percent': 82.5,
    'memory_utilization': 4.5,
    'evictions': 3,
    'expired_removals': 1
}
```

### API Client Metrics
```python
client.get_metrics()
{
    'request_count': 50,
    'cache_hits': 150,
    'cache_hit_rate': 75.0,
    'avg_response_time': 0.245
}
```

### Logs to Watch
```
✅ Cache hit for {key}
⚠️  Cache miss - making API request
❌ API timeout - falling back to mock
🎭 Using mock mode
```

---

## TTLCache Instance Creation

```python
from src.utils.ttl_cache import TTLCache, CachePresets

# Custom
cache = TTLCache(
    max_size=1000,
    default_ttl=3600.0,
    cleanup_interval=300.0
)

# Preset: Small and fast
cache = CachePresets.small_fast()  # 100 entries, 300s TTL

# Preset: Demo
cache = CachePresets.medium_demo()  # 1000 entries, 3600s TTL

# Preset: Production
cache = CachePresets.large_production()  # 10k entries, 7200s TTL
```

---

## Data Flow Summary

```
USER INPUT (Campaign ID)
     ↓
Service Layer Cache (L2)
     ├─ Hit? → Return ✓
     └─ Miss? → Continue
     ↓
Route API Cache (L1) + SPACE API Cache (L1)
     ├─ Hit? → Return ✓
     └─ Miss? → Continue
     ↓
PostgreSQL Database (L3)
     ├─ Load playouts
     └─ Continue
     ↓
API Calls (Route + SPACE)
     ├─ Success? → Cache results
     ├─ Timeout/Error? → Auto-fallback to mock
     └─ Return results
     ↓
Aggregate + Enrich Data
     ↓
Store in Service Cache
     ↓
Return to UI
```

---

## Next Steps

### Monitoring
- [ ] Add cache stats endpoint to admin dashboard
- [ ] Track hit rates over time
- [ ] Alert on low cache hit rates

### Optimization
- [ ] Analyze cache miss patterns
- [ ] Pre-warm cache for common campaigns
- [ ] Tune TTL based on data patterns

### Enhancement
- [ ] Implement PostgreSQL cache tables
- [ ] Add cache invalidation endpoint
- [ ] Export metrics to monitoring system

---

**Version**: 1.0  
**Updated**: October 20, 2025  
**For Full Details**: See CURRENT_ARCHITECTURE.md and CACHE_FLOW_DIAGRAMS.md
