# Future Pipeline Enhancements - For POC Team Awareness

**Created**: 2025-10-17
**Status**: PLANNED (Not Yet Implemented)
**Impact on POC**: Medium (Will improve performance and reduce costs)

---

## 📋 What's Coming

The pipeline team is planning to implement **API caching** to pre-fetch and store Route API audience data and SPACE entity lookups. This will benefit the POC application significantly.

---

## 🎯 Planned Features

### 1. Route API Audience Caching ⭐

**What**: Pre-cache Route API audience data for common queries

**Current State**:
- POC makes live Route API calls for every query
- Avg response time: 2-3 seconds
- Cost: ~$9,000/month (high volume)

**Future State**:
- 80% of queries served from cache
- Avg response time: < 500ms (6x faster)
- Cost: ~$2,100/month (77% reduction)

**Timeline**: Phase 3 (6 weeks implementation, starts TBD)

**Impact on POC**:
- ✅ Much faster queries
- ✅ Lower API costs
- ✅ Offline capability (use cached data when API unavailable)
- ⚠️ May need cache invalidation API

### 2. SPACE Entity Lookup Caching

**What**: Cache SPACE API entity name lookups (media owners, buyers, agencies, brands)

**Current State**:
- POC shows IDs only (e.g., "3" instead of "Clear Channel")
- Need live SPACE API calls to decode IDs

**Future State**:
- All entity names pre-cached
- Instant lookup from database
- Human-readable names everywhere

**Timeline**: Phase 2 (3 weeks implementation, starts TBD)

**Impact on POC**:
- ✅ Display human-readable names instead of IDs
- ✅ No need for POC to call SPACE API
- ✅ Instant lookups

### 3. Smart Cache Warming

**What**: POC can trigger cache pre-loading for campaigns

**Future State**:
- "Pre-load campaign" button in POC UI
- Background job fetches all data
- Next query is instant

**Timeline**: Phase 4 (2 weeks, after Phase 3)

**Impact on POC**:
- ✅ Better UX (fast initial loads)
- ✅ User control over caching
- ⚠️ Need UI integration point

---

## 📊 New Database Tables (Coming)

### route_audience_cache

Pre-cached Route API audience data per 15-minute window.

**Schema** (planned):
```sql
CREATE TABLE route_audience_cache (
    frameid VARCHAR(50),
    buyercampaignref VARCHAR(50),
    time_window_start TIMESTAMP,
    route_release_id VARCHAR(20),
    impacts DECIMAL(15,2),
    demographics JSONB,
    cached_at TIMESTAMP,
    expires_at TIMESTAMP
);
```

**POC Usage**:
```python
# Check cache first
cached = db.query("""
    SELECT impacts, demographics
    FROM route_audience_cache
    WHERE frameid = %s
      AND time_window_start = %s
      AND route_release_id = %s
      AND expires_at > NOW()
""", (frame_id, window_start, release_id))

if cached:
    return cached  # Fast path
else:
    # Fallback to live Route API call
    return call_route_api(...)
```

### space_lookup_cache

Pre-cached SPACE entity name lookups.

**Schema** (planned):
```sql
CREATE TABLE space_lookup_cache (
    lookup_type VARCHAR(50),      -- 'mediaowner', 'buyer', 'agency', 'brand'
    lookup_id VARCHAR(100),        -- Entity ID
    lookup_name VARCHAR(255),      -- Human-readable name
    metadata JSONB,
    cached_at TIMESTAMP,
    expires_at TIMESTAMP
);
```

**POC Usage**:
```python
# Get media owner name
name = db.query("""
    SELECT lookup_name
    FROM space_lookup_cache
    WHERE lookup_type = 'mediaowner'
      AND lookup_id = %s
""", (media_owner_id,))

# Use name in UI: "Clear Channel" instead of "3"
```

---

## 🚀 Implementation Timeline

| Phase | Feature | Duration | Start Date |
|-------|---------|----------|------------|
| Phase 1 | Foundation (cache tables) | 4 weeks | TBD |
| Phase 2 | SPACE caching | 3 weeks | After Phase 1 |
| **Phase 3** | **Route caching** ⭐ | **6 weeks** | **After Phase 2** |
| Phase 4 | Smart warming | 2 weeks | After Phase 3 |
| Phase 5 | Optimization | 4 weeks | After Phase 4 |

**Total**: ~19 weeks from start

**Note**: Timeline depends on:
- API credentials approval
- Resource allocation
- POC Phase 1 completion

---

## 🔄 What POC Team Should Know

### No Breaking Changes

**Good news**: These features are **additive**, not breaking.

- ✅ Current POC queries will continue to work
- ✅ No schema changes to existing tables
- ✅ New tables are separate
- ✅ POC can adopt features gradually

### Optional Integration

**POC can choose**:
1. **Ignore cache** - Continue using live API calls (works fine)
2. **Use cache opportunistically** - Check cache first, fallback to API
3. **Full integration** - Cache-first strategy with manual warming

### When to Integrate

**Recommended timeline**:
1. **Phase 2 (SPACE caching)** - Easy win, integrate immediately
2. **Phase 3 (Route caching)** - Integrate when performance becomes issue
3. **Phase 4 (Smart warming)** - Integrate if users request faster loads

---

## 📞 Coordination Points

### 1. API Credentials

**Route API**:
- Pipeline team will get credentials
- POC can use same credentials (or separate)
- Coordinate to avoid rate limits

**SPACE API**:
- Pipeline team will get credentials
- POC may not need separate access (use cache)

### 2. Cache Strategy Discussion

**Questions for POC team**:
- What % of queries are historical (cacheable) vs real-time?
- Which campaigns are queried most frequently?
- What metrics are most common (impacts, reach, frequency)?
- Do you need cache invalidation controls?

### 3. Monitoring & Alerting

**Shared visibility**:
- Cache hit/miss rates
- API call volumes
- Error rates
- Performance metrics

---

## 📚 Full Documentation

**Detailed roadmap**: `Claude/Future_Plans/API_CACHING_ROADMAP_2025.md`

This contains:
- Complete implementation plan
- Database schemas
- Code examples
- Cost analysis
- Risk assessment
- Success criteria

**For POC team**: Read this when Phase 3 approaches

---

## 🎯 What POC Should Do Now

### Immediate (This Month)
1. ✅ **Nothing required** - Current implementation is complete
2. 📖 Be aware of future features
3. 💬 Share feedback on caching strategy

### When Phase 2 Starts (SPACE Caching)
1. 📊 Update POC to query `space_lookup_cache` for entity names
2. 🎨 Display human-readable names instead of IDs
3. 🧪 Test fallback when cache empty

### When Phase 3 Starts (Route Caching)
1. 💬 Discuss cache integration strategy
2. 📊 Decide: cache-first or API-first approach
3. 🧪 Test with cached data
4. 📈 Monitor cache hit rates

---

## 🤝 Staying in Sync

**Communication strategy**: See `Claude/POC_Handover/SYNC_STRATEGY.md`

This document describes:
- How to stay informed of pipeline updates
- Change notification process
- Shared documentation strategy
- Cross-project coordination

---

## ❓ Questions?

**Contact**: Pipeline team (ian@route.org.uk)

**Documentation**:
- Full roadmap: `Claude/Future_Plans/API_CACHING_ROADMAP_2025.md`
- Sync strategy: `Claude/POC_Handover/SYNC_STRATEGY.md`
- Current database: `Claude/POC_Handover/DATABASE_HANDOVER_FOR_POC.md`

---

**Summary**: API caching is coming, will make POC faster and cheaper, but is NOT required for POC Phase 1. Integration can be gradual and optional.

**Status**: 📋 PLANNED
**Priority**: Medium (Post-POC Phase 1)
**Next Review**: Monthly
