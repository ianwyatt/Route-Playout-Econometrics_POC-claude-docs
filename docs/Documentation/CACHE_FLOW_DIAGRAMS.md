# Cache and Data Flow Diagrams

## 1. Route API Cache Flow

```
USER QUERY (Campaign ID)
        ↓
CampaignService.query_campaign()
        ↓
PlayoutProcessor.process_playout_campaign()
        ↓
Load Playouts from CSV/DB
        ↓
GroupBy 15-minute Dayparts
        ↓
RouteAPIClient.get_batch_audiences() ← Loop through playouts
        ↓
ForEach Playout:
    ├─→ Create request_data (JSON)
    │   ├─ route_release_id
    │   ├─ frame_id
    │   ├─ datetime_from/until
    │   └─ spot_length
    │
    ├─→ Generate Cache Key (MD5 of JSON)
    │
    ├─→ CHECK CACHE
    │   ├─ Cache Hit? → Return cached response
    │   └─ Cache Miss? → Continue
    │
    ├─→ CHECK MOCK MODE
    │   ├─ If use_mock=True → _mock_response()
    │   └─ If use_mock=False → Continue
    │
    ├─→ MAKE API CALL
    │   ├─ POST /rest/process/playout
    │   ├─ Timeout? → Auto-fallback to mock
    │   ├─ Auth failure? → Auto-fallback to mock
    │   └─ Success? → Parse response
    │
    ├─→ STORE IN CACHE
    │   ├─ Key: MD5 hash
    │   ├─ Value: API response
    │   ├─ TTL: 3600 seconds (default)
    │   └─ If cache full? → LRU eviction
    │
    └─→ Return: {impacts, reach, frequency, GRPs, ...}
        ↓
Aggregate all playouts
        ↓
Return to UI
```

### Cache Miss Scenario (First Request)
```
Request Data:
{
    "route_release_id": 55,
    "route_algorithm_version": 10.2,
    "campaign": [{
        "schedule": [{"datetime_from": "2025-07-28 00:00", "datetime_until": "2025-07-28 00:14"}],
        "spot_length": 10,
        "frames": [1234723633]
    }]
}
            ↓
MD5 Hash: a7f3e2d1c9f4b5e8...
            ↓
Cache Check: Not Found
            ↓
Mock Check: Not in mock mode
            ↓
API Call: POST route.mediatelapi.co.uk/rest/process/playout
            ↓
Response: {
    "success": true,
    "impacts": 245.6,
    "reach": 82,
    "frequency": 3.0,
    "gross_rating_points": 0.00276,
    ...
}
            ↓
Store in TTLCache
            ↓
Mark: {'from_cache': False, 'processing_time': 245ms}
```

### Cache Hit Scenario (Repeated Request)
```
Request Data (Same as before)
            ↓
MD5 Hash: a7f3e2d1c9f4b5e8...
            ↓
Cache Check: FOUND!
            ↓
Check Expiration:
    - Cached: Oct 20 14:30:00
    - Now: Oct 20 14:50:00
    - Expires: Oct 20 15:30:00
    - Status: VALID ✓
            ↓
Return: {
    "impacts": 245.6,
    "reach": 82,
    "frequency": 3.0,
    "gross_rating_points": 0.00276,
    "from_cache": true,
    "processing_time": 0ms
}
            ↓
Mark Cache Hit: hits++
```

---

## 2. SPACE API Cache Flow

```
CampaignService Processing Playouts
        ↓
For each playout, need:
    • Buyer name (from spacebuyerid)
    • Agency name (from spaceagencyid)
    • Brand name (from spacebrandid)
    • Media owner name (from spacemediaownerid)
        ↓
SpaceAPIClient.get_buyer(buyer_id) ← For each unique buyer
        ↓
CHECK CACHE
├─ Key: "buyer:12345"
├─ Found and not expired? → Return SpaceEntity
└─ Not found? → Continue
        ↓
CHECK MOCK MODE
├─ If use_mock=True → Return mock entity
└─ If use_mock=False → Continue
        ↓
MAKE API CALL
├─ GET /buyers/12345
├─ Auth with basic auth (username, password)
├─ Timeout? → Auto-fallback to mock
├─ 401 Auth failed? → Auto-fallback to mock
├─ 404 Not found? → Return mock (unknown)
└─ 200 Success? → Parse JSON
        ↓
STORE IN CACHE
├─ Key: "buyer:12345"
├─ Value: SpaceEntity object
├─ TTL: 3600 seconds (default)
└─ If cache full? → LRU eviction
        ↓
Return: SpaceEntity(
    id='12345',
    name='Creative Agency Ltd',
    type='buyer',
    details={...},
    last_updated=datetime.now()
)
        ↓
Use in Campaign Data
```

### Batch Lookup Example
```
Lookups Needed:
[
    {'type': 'media_owner', 'id': '171'},  ← Clear Channel
    {'type': 'buyer', 'id': '12345'},
    {'type': 'agency', 'id': '5678'},
    {'type': 'brand', 'id': '9999'}
]
        ↓
FOR each lookup:
    lookup_key = "media_owner:171"
    ├─ CHECK CACHE → Hit or Miss
    ├─ If Miss → API Call or Mock
    ├─ STORE IN CACHE
    └─ Add to results
        ↓
Results = {
    'media_owner:171': SpaceEntity(...),
    'buyer:12345': SpaceEntity(...),
    'agency:5678': SpaceEntity(...),
    'brand:9999': SpaceEntity(...)
}
```

---

## 3. Service Layer Cache Flow

```
UI: User Requests Campaign Data
        ↓
CampaignService.get_campaign(campaign_id)
        ↓
Generate Cache Key:
    f"campaign_{campaign_id}_{start_date}_{end_date}_{aggregate_by}"
        ↓
CHECK SERVICE CACHE
├─ cached = self.get_from_cache(cache_key)
├─ If valid (not expired)?
│  └─ Return cached result ✓ (Cache Hit)
└─ If expired or missing? → Continue
        ↓
PROCESS CAMPAIGN
├─ Load playouts from CSV
├─ Call Route API (with cache)
├─ Call SPACE API (with cache)
├─ Aggregate data
└─ Return processed result
        ↓
STORE IN SERVICE CACHE
├─ self.set_cache(cache_key, result)
├─ TTL: 600 seconds (CampaignService default)
├─ Max entries: 100 (per service)
└─ Eviction: LRU when full
        ↓
Return to UI
```

### Multi-Level Cache Interaction
```
REQUEST: get_campaign("16012")
        ↓
LEVEL 1: Service Cache
    ├─ Check: "campaign_16012_None_None_day"
    └─ Miss: Continue to Level 2
        ↓
LEVEL 2: Route API Client Cache (for each playout)
    ├─ Check: "a7f3e2d1c9f4b5e8..." (MD5)
    └─ Hit/Miss: Fetch or Call API
        ↓
LEVEL 3: SPACE API Client Cache (for each entity)
    ├─ Check: "buyer:12345"
    └─ Hit/Miss: Fetch or Call API
        ↓
LEVEL 4: PostgreSQL Database
    ├─ Query: SELECT * FROM playout WHERE campaign_id = 16012
    └─ Return: Raw playout records
        ↓
AGGREGATE ALL LEVELS
        ↓
STORE: Result in Service Cache (LEVEL 1)
        ↓
RETURN: Fully enriched campaign data to UI
```

---

## 4. TTLCache Internal Structure

```
TTLCache Instance:
{
    _cache: OrderedDict([
        ('key1', CacheEntry(value=data1, expires_at=T1, access_count=5)),
        ('key2', CacheEntry(value=data2, expires_at=T2, access_count=2)),
        ('key3', CacheEntry(value=data3, expires_at=T3, access_count=8)),
        ...
    ]),
    _max_size: 1000,
    _default_ttl: 3600.0,
    _cleanup_interval: 300.0,
    
    STATISTICS:
    _hits: 150
    _misses: 25
    _evictions: 5
    _expired_removals: 2
    _last_cleanup: 1697829600.0
}
```

### Cache Operation Timeline
```
TIME    EVENT                           STATE
─────────────────────────────────────────────────────
14:00   Cache initialize               size=0
14:01   PUT key1 (TTL=3600)           size=1, expires=15:01
14:02   PUT key2 (TTL=3600)           size=2, expires=15:02
14:03   GET key1 ✓                    hit++, move_to_end(key1)
14:04   PUT key3 (TTL=3600)           size=3, expires=15:04
14:05   Cleanup check                 size=3 (none expired)
        (next cleanup: 14:10)
14:06   PUT key4 (TTL=3600)           size=4, expires=15:06
15:01   GET key1                      EXPIRED, removed
        expired_removals++, size=3
15:02   GET key2 ✓                    hit++, still valid
15:03   PUT key5 → size would be 5    LRU evict key3
        (key3 least recently accessed) size=4
15:10   Manual cleanup_expired()       expired_removals+=2, size=2
```

---

## 5. Database Integration (Future)

```
POTENTIAL FUTURE ARCHITECTURE:

UI Request
    ↓
Service Layer
    ↓
┌─────────────────────────────────────────┐
│ Check PostgreSQL Cache                  │
│ SELECT * FROM route_api_cache           │
│ WHERE request_hash = MD5(request_data)  │
│ AND expires_at > NOW()                  │
└─────────────────────────────────────────┘
    ├─ Found and valid? → Return (DB Cache Hit)
    └─ Not found? → Continue
        ↓
API Client In-Memory Cache
    ├─ Found and valid? → Return (Memory Cache Hit)
    └─ Not found? → Continue
        ↓
Make API Call
    ├─ Success? → Continue
    └─ Timeout/Error? → Fallback to Mock
        ↓
STORE IN BOTH CACHES:
├─ In-Memory Cache (TTL 1 hour)
└─ PostgreSQL route_api_cache (TTL 7 days)
    │
    └─ INSERT INTO route_api_cache (
        request_hash,
        request_data,
        response_data,
        cached_at,
        expires_at
    ) VALUES (...)
        ↓
Return to UI
```

### Cache Table Schema (Proposed)
```
route_api_cache:
├─ id: SERIAL PRIMARY KEY
├─ request_hash: VARCHAR(32) UNIQUE  ← MD5 of request
├─ request_data: JSONB               ← Full request JSON
├─ response_data: JSONB              ← Full response JSON
├─ cached_at: TIMESTAMP              ← When cached
├─ expires_at: TIMESTAMP             ← TTL expiration
└─ INDEX: (request_hash, expires_at)

space_api_cache:
├─ id: SERIAL PRIMARY KEY
├─ entity_type: VARCHAR(20)          ← 'buyer', 'agency', etc.
├─ entity_id: VARCHAR(100)
├─ entity_data: JSONB                ← Full entity JSON
├─ cached_at: TIMESTAMP
├─ expires_at: TIMESTAMP
└─ UNIQUE INDEX: (entity_type, entity_id)
```

---

## 6. Cache Hit/Miss Decision Tree

```
                        REQUEST
                           ↓
                    Cache Enabled?
                      /        \
                    NO          YES
                    ↓            ↓
                MAKE API      Cache Key
                CALL          Generated?
                              /     \
                            NO      YES
                            ↓        ↓
                         MAKE    LOOKUP
                         API     CACHE
                              /    │    \
                         MISS  EXPIRED  HIT
                          ↓      ↓      ↓
                        MAKE   MAKE   RETURN
                        API    API    CACHED
                        ↓      ↓      ↓
                      STORE  STORE  COUNT
                      IN    IN     HITS++
                      CACHE CACHE
                        ↓      ↓
                      ├────────┘
                           ↓
                      RETURN TO
                      CALLER
                           ↓
                      COUNT
                      REQUESTS++
```

---

## 7. Memory Management (LRU Eviction)

```
Cache at Capacity (1000 entries):
┌─────────────────────────────────────────┐
│ MOST RECENTLY USED                      │
│                                         │
│ key_N (access_count=50, last_accessed=T_now)
│ key_M (access_count=45, last_accessed=T_now-5s)
│ ...                                     │
│ key_2 (access_count=2, last_accessed=T_old)
│ key_1 (access_count=1, last_accessed=T_oldest)
│                                         │
│ LEAST RECENTLY USED ← Next to evict     │
└─────────────────────────────────────────┘

NEW REQUEST: PUT key_Z
    ├─ Size Check: 1000 >= 1000? YES
    ├─ Evict LRU: Remove key_1
    ├─ Update Stats: evictions++
    ├─ Add new: key_Z at end (most recent)
    └─ Size: Still 1000
```

---

**Last Updated**: October 20, 2025
**Purpose**: Visual reference for cache and data flow architecture
