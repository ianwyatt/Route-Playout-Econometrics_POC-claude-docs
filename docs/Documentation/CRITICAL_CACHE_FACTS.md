# Critical Cache Integration Facts - Quick Reference

**Purpose**: Essential facts to remember for cache integration
**Created**: 2025-11-14
**Use**: Reference before ANY cache-related code changes

---

## 🚨 THE BIG 6 CRITICAL FACTS

### 1. Impacts Stored in Thousands ⚠️ MUST MULTIPLY BY 1000

```sql
-- WRONG ❌
SELECT impacts FROM cache_route_impacts_15min_by_demo;
-- Returns 1234 (should be 1,234,000)

-- CORRECT ✅
SELECT impacts * 1000 as impacts FROM cache_route_impacts_15min_by_demo;
-- Returns 1234000 (correct)
```

**Why**: Storage optimization - reduces database size by 30%
**Impact if forgotten**: Metrics off by 1000x - CATASTROPHIC

### 2. Route API Frame Limits 🚨 #1 DEVELOPER PITFALL

| API Call Type | Frame Limit | Use When |
|---------------|-------------|----------|
| **WITH `"grouping": "frame"`** | ❌ **10,000 frames MAX** | Need per-frame breakdown |
| **WITHOUT grouping** | ✅ **NO LIMIT** | Need aggregate campaign metrics |

```python
# BAD - Will fail if campaign has >10k frames ❌
payload = {
    "grouping": "frame",
    "campaign": [...50,000 frames...]  # ERROR 221!
}

# GOOD - Check frame count first ✅
frame_count = len(campaign_frames)
if frame_count > 10000:
    payload = {"campaign": [...]}  # No grouping - aggregate only
else:
    payload = {"grouping": "frame", "campaign": [...]}  # Per-frame OK
```

**Why**: Route API performance limits
**Impact if forgotten**: API failures for large campaigns

### 3. Route API 10MB Payload Limit 📦 CAUSES HOURLY AGGREGATION

```python
# Route API rejects requests larger than 10MB
# Large campaigns with many frames/schedules exceed this limit

# BAD - Full campaign JSON exceeds 10MB ❌
payload = {
    "campaign": build_full_campaign(100000_playouts)  # 15MB payload!
}

# GOOD - Use hourly aggregation for large campaigns ✅
# This reduces payload size by grouping 15-min windows into hours
payload = {
    "campaign": build_hourly_aggregated_campaign(100000_playouts)  # <10MB
}

# Check table to see if campaign is too large
check_query = """
    SELECT can_cache_full, json_size_mb
    FROM campaign_cache_limitations
    WHERE campaign_id = %s
"""
```

**Why**: Route API enforces 10MB max request size
**Impact if forgotten**: API rejection, requires hourly aggregation (reach becomes approximate)
**Solution**: Use `campaign_cache_limitations` table to check; use week-cumulative cache for large campaigns

### 4. Frame Validation Required 🚨 PREVENTS ERROR 220

```python
# ALWAYS validate frames BEFORE calling Route API
valid_frames, invalid = validate_frames(frame_ids, route_release_id=56)

if not valid_frames:
    raise ValueError("No valid frames in Route release")

# Only use valid frames in API call
payload["campaign"] = build_campaign(valid_frames)  # Not all frames!
```

**Why**: Not all playout frames exist in Route releases
**Impact if forgotten**: Route API error 220, failed queries

### 5. Route API Authentication - BOTH Required 🔑

```python
# MUST include BOTH Basic Auth AND X-Api-Key header
headers = {
    'Content-Type': 'application/json',
    'X-Api-Key': os.getenv('ROUTE_API_KEY')  # Header auth
}

auth = (
    os.getenv('ROUTE_API_User_Name'),  # Basic auth
    os.getenv('ROUTE_API_Password')
)

response = requests.post(url, json=payload, headers=headers, auth=auth)
```

**Why**: Dual authentication required by Route API
**Impact if forgotten**: 401 Unauthorized errors

### 6. Time Filters MANDATORY for Performance 🚀

```python
# BAD - Scans 252.7M rows ❌
query = """
    SELECT * FROM cache_route_impacts_15min_by_demo
    WHERE campaign_id = %s
"""  # Takes 30+ seconds!

# GOOD - Uses index, fast ✅
query = """
    SELECT * FROM cache_route_impacts_15min_by_demo
    WHERE campaign_id = %s
      AND time_window_start >= %s
      AND time_window_start < %s
"""  # Takes <5ms
```

**Why**: 252.7M records - full scan is slow
**Impact if forgotten**: Slow queries (30s vs 5ms)

---

## 🎯 Cache Tables

### Primary Tables on MS-01

| Table | Records | Purpose |
|-------|---------|---------|
| `cache_route_impacts_15min_by_demo` | 252.7M | 15-min demographic impacts |
| `cache_campaign_reach_day` | 11,363 | Daily reach/GRP/freq |
| `cache_campaign_brand_reach` | 17,406 | Brand-level metrics |

### 7 Demographic Segments (All Pre-Cached)

1. `all_adults` - All adults 15+
2. `age_15_34` - Young adults
3. `age_35_54` - Middle-aged adults
4. `age_55_plus` - Older adults
5. `abc1` - Higher socio-economic
6. `c2de` - Lower socio-economic
7. `housewife` - Main household shopper

---

## 🔧 Database Connection

```python
# MS-01 Production (Always use for cache)
use_ms01 = True
conn = psycopg2.connect(
    host='192.168.1.34',
    port=5432,
    database='route_poc',
    user='postgres',
    password=os.getenv('POSTGRES_PASSWORD_MS01')
)
```

**Environment Variable**: `USE_MS01_DATABASE=true`
**Credential**: `POSTGRES_PASSWORD_MS01` (request from pipeline team)

---

## 📐 15-Minute Time Windows

**Strict boundaries**: `:00`, `:15`, `:30`, `:45` past each hour

```
12:14:59 → 12:00:00 window
12:15:00 → 12:15:00 window
12:15:01 → 12:15:00 window
```

**Formula**:
```python
window_start = datetime.replace(
    minute=(datetime.minute // 15) * 15,
    second=0,
    microsecond=0
)
```

---

## 🎯 Cache-First Pattern (ONE-PAGE ALGORITHM)

```python
def get_campaign_audience(campaign_id, start_date, end_date):
    """Cache-first pattern - follow this EXACTLY."""

    # 1. CHECK CACHE FIRST ⚡
    cached = query_demographic_cache(campaign_id, start_date, end_date)
    if cached is not None:
        logger.info("✅ Cache HIT")
        return cached  # 1,000x faster!

    # 2. CACHE MISS - GET FRAMES FROM DATABASE 🌐
    logger.info("⚠️ Cache MISS - calling Route API")
    frames = get_campaign_frames(campaign_id, start_date, end_date)

    # 3. VALIDATE FRAMES (PREVENTS ERROR 220) 🔍
    valid, invalid = validate_frames(frames['frameid'].unique())
    if not valid:
        raise ValueError("No valid frames")
    frames = frames[frames['frameid'].isin(valid)]  # Filter to valid only

    # 4. CHECK FRAME COUNT (PREVENTS >10K ERROR) 📊
    frame_count = len(valid)
    use_grouping = frame_count <= 10000

    if frame_count > 10000:
        logger.warning(f"{frame_count} frames - using non-grouping")

    # 5. BUILD ROUTE API PAYLOAD 🔧
    payload = {
        "route_release_id": 56,
        "route_algorithm_version": 10.2,
        "algorithm_figures": ["impacts"],
        "demographics": [{"demographic_id": i} for i in range(1, 8)],
        "campaign": build_campaign_entries(frames)
    }

    if use_grouping:
        payload["grouping"] = "frame"

    # 6. CALL ROUTE API WITH RETRY 📞
    response = call_route_api_with_retry(payload)

    # 7. RETURN RESULTS
    return parse_response(response)
```

---

## ⚠️ Common Mistakes

### Mistake #1: Not Multiplying Impacts
```python
# WRONG ❌
df['impacts']  # Off by 1000x

# CORRECT ✅
df['impacts'] * 1000
```

### Mistake #2: Adding Grouping to Large Campaigns
```python
# WRONG ❌
payload = {"grouping": "frame", "campaign": large_campaign}  # Fails if >10k

# CORRECT ✅
if frame_count <= 10000:
    payload["grouping"] = "frame"
```

### Mistake #3: Not Validating Frames
```python
# WRONG ❌
payload["campaign"] = build_campaign(all_frames)  # Some frames invalid!

# CORRECT ✅
valid_frames, _ = validate_frames(all_frames)
payload["campaign"] = build_campaign(valid_frames)
```

### Mistake #4: Missing Time Filter
```python
# WRONG ❌
WHERE campaign_id = %s  # Scans 252M rows!

# CORRECT ✅
WHERE campaign_id = %s
  AND time_window_start >= %s
  AND time_window_start < %s
```

### Mistake #5: Single Authentication Only
```python
# WRONG ❌
headers = {'X-Api-Key': api_key}  # Missing Basic Auth!

# CORRECT ✅
headers = {'X-Api-Key': api_key}
auth = (username, password)  # BOTH required
```

---

## 📊 Performance Expectations

| Metric | Target |
|--------|--------|
| Cache query time | <5ms |
| Cache hit rate | >80% |
| API fallback time | 5-30s (acceptable) |
| Frame validation | <2s for 1000 frames |

---

## 🔗 Quick Links

**Pipeline Docs**: `/docs/pipeline-handover/`
**Database Schema**: `/docs/pipeline-handover/DATABASE_HANDOVER_FOR_POC.md`
**Python Examples**: `/docs/pipeline-handover/PYTHON_EXAMPLES.py`
**Quick Reference**: `/docs/pipeline-handover/QUICK_REFERENCE.md`
**Changelog**: `/docs/pipeline-handover/CHANGELOG_FOR_POC.md` (check weekly!)

---

## 🚦 Before Writing ANY Cache Code

**Checklist**:
- [ ] Will I multiply impacts by 1000?
- [ ] Will I include time filters in WHERE clause?
- [ ] Will I validate frames before Route API call?
- [ ] Will I check frame count before using grouping?
- [ ] Do I have both Basic Auth AND X-Api-Key?

**If you answered NO to ANY question → STOP AND FIX**

---

**Created**: 2025-11-14
**Critical**: Read this BEFORE every cache-related code change
**Update**: If you discover new critical facts, add them here immediately
