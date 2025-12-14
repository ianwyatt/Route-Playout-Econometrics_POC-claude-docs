# Brand Split Service Documentation

## Overview

The Brand Split Service handles the distribution of Route API audience impacts across multiple brands when campaigns have multiple brands playing out in the same 15-minute window.

**Location**: `/Users/ianwyatt/PycharmProjects/Route-Playout-Econometrics_POC/src/services/brand_split_service.py`

**Created**: October 17, 2025

## Purpose

Some campaigns run multiple brands simultaneously on the same frame within a 15-minute window. The Route API returns total impacts for the window, but we need to allocate these impacts proportionally to each brand based on their spot counts.

This service:
- Queries the `mv_playout_15min_brands` view from MS-01 database
- Calculates proportional distribution based on spot counts
- Caches results for performance
- Provides aggregation across entire campaigns

## Database Dependency

### MS-01 Database View: `mv_playout_15min_brands`

This materialized view in the MS-01 Postgres database aggregates playout data into 15-minute windows and groups by brand.

**Schema:**
```sql
CREATE MATERIALIZED VIEW mv_playout_15min_brands AS
SELECT
    frameid,
    buyercampaignref,
    spacebrandid,
    date_trunc('minute', startdate) -
        (EXTRACT(minute FROM startdate)::integer % 15) * interval '1 minute' as window_start,
    date_trunc('minute', startdate) -
        (EXTRACT(minute FROM startdate)::integer % 15) * interval '1 minute' +
        interval '15 minutes' as window_end,
    COUNT(*) as spot_count
FROM playout_data
WHERE frametype = 'digital'
GROUP BY frameid, buyercampaignref, spacebrandid, window_start, window_end
ORDER BY frameid, window_start, spacebrandid;
```

**Key Fields:**
- `frameid` - Frame identifier
- `buyercampaignref` - Campaign ID
- `spacebrandid` - Brand identifier from SPACE
- `window_start` - Start of 15-minute window
- `window_end` - End of 15-minute window
- `spot_count` - Number of spots for this brand in this window

## Core Functions

### 1. `split_audience_by_brand()`

**Purpose**: Split Route API impacts across brands for a single 15-minute window.

**Signature:**
```python
async def split_audience_by_brand(
    frame_id: int,
    campaign_id: str,
    window_start: datetime,
    total_impacts: float
) -> Dict[int, float]
```

**Parameters:**
- `frame_id` - Frame identifier (e.g., 1234860035)
- `campaign_id` - Campaign identifier (e.g., "16012")
- `window_start` - Start of 15-minute window (datetime object)
- `total_impacts` - Total impacts from Route API for this window

**Returns:**
Dictionary mapping brand_id -> proportional_impacts

**Example:**
```python
brand_impacts = await service.split_audience_by_brand(
    frame_id=1234860035,
    campaign_id="16012",
    window_start=datetime(2025, 6, 1, 0, 0, 0),
    total_impacts=1000000
)

# Result: {4950: 750000.0, 4951: 250000.0}
# Brand 4950 gets 75% (3 out of 4 spots)
# Brand 4951 gets 25% (1 out of 4 spots)
```

**Algorithm:**
1. Query `mv_playout_15min_brands` for spot counts
2. Calculate total spots: `total = sum(spot_count)`
3. For each brand: `brand_impacts = (spot_count / total) * total_impacts`
4. Cache proportions (not absolute values) for reuse

### 2. `get_brand_distribution()`

**Purpose**: Get raw brand distribution data for a specific window.

**Signature:**
```python
async def get_brand_distribution(
    frame_id: int,
    campaign_id: str,
    window_start: datetime
) -> List[Dict[str, Any]]
```

**Returns:**
```python
[
    {
        'spacebrandid': 4950,
        'spot_count': 3,
        'window_start': datetime(2025, 6, 1, 0, 0),
        'window_end': datetime(2025, 6, 1, 0, 15)
    },
    {
        'spacebrandid': 4951,
        'spot_count': 1,
        'window_start': datetime(2025, 6, 1, 0, 0),
        'window_end': datetime(2025, 6, 1, 0, 15)
    }
]
```

**Use Case**: Understanding the raw data before splitting impacts.

### 3. `get_campaign_brands()`

**Purpose**: Get all brands in a campaign with aggregated statistics.

**Signature:**
```python
async def get_campaign_brands(
    campaign_id: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> List[Dict[str, Any]]
```

**Returns:**
```python
[
    {
        'spacebrandid': 4950,
        'total_spots': 250,
        'first_window': datetime(2025, 6, 1, 0, 0),
        'last_window': datetime(2025, 6, 30, 23, 45),
        'frame_count': 12
    }
]
```

**Use Case**: Campaign analysis, understanding brand mix before processing.

### 4. `aggregate_brand_impacts()`

**Purpose**: Process complete Route API response and aggregate by brand.

**Signature:**
```python
async def aggregate_brand_impacts(
    route_api_response: Dict[str, Any]
) -> Dict[str, Any]
```

**Input Format:**
```python
{
    'campaign_id': '16012',
    'frames': [
        {
            'frame_id': 1234860035,
            'campaign_id': '16012',
            'windows': [
                {
                    'window_start': '2025-06-01 00:00:00',
                    'impacts': 1000000
                },
                {
                    'window_start': '2025-06-01 00:15:00',
                    'impacts': 1200000
                }
            ]
        }
    ]
}
```

**Output Format:**
```python
{
    'campaign_id': '16012',
    'total_impacts': 10000000,
    'brands': {
        4950: {
            'total_impacts': 7500000,
            'proportion': 0.75,
            'windows': 120,
        },
        4951: {
            'total_impacts': 2500000,
            'proportion': 0.25,
            'windows': 40,
        }
    },
    'windows_processed': 160,
    'processing_time_ms': 450.2,
    'timestamp': '2025-06-10T14:30:00'
}
```

**Use Case**: End-to-end processing of Route API responses with brand attribution.

### 5. `get_multi_brand_windows()`

**Purpose**: Find windows where multiple brands exist (complexity analysis).

**Signature:**
```python
async def get_multi_brand_windows(
    campaign_id: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> List[Dict[str, Any]]
```

**Returns:**
```python
[
    {
        'frameid': 1234860035,
        'window_start': datetime(2025, 6, 1, 0, 0),
        'brand_count': 3,
        'total_spots': 8,
        'brands': [4950, 4951, 4952]
    }
]
```

**Use Case**: Identifying complex campaigns that require brand splitting.

## Configuration

### Database Configuration

The service uses the POC's standard `DatabaseConfig` from `/Users/ianwyatt/PycharmProjects/Route-Playout-Econometrics_POC/src/config/database.py`.

**Environment Variables:**
- `USE_MS01_DATABASE=true` - Use MS-01 production database (default)
- `POSTGRES_HOST_MS01=192.168.1.34` - MS-01 host
- `POSTGRES_DATABASE_MS01=route_poc` - Database name
- `POSTGRES_USER_MS01=postgres` - Database user
- `POSTGRES_PASSWORD_MS01=<password>` - Database password

### Cache Configuration

**Default TTL**: 1 hour (3600 seconds)

**Cache Strategy**:
- Brand distributions cached per window (stable data)
- Proportions cached instead of absolute values (reusable across different total_impacts)
- Campaign-level queries cached for 30 minutes

**Cache Keys**:
- `brand_split_{frame_id}_{campaign_id}_{window_start}` - Proportions
- `brand_dist_{frame_id}_{campaign_id}_{window_start}` - Raw distribution
- `campaign_brands_{campaign_id}_{start_date}_{end_date}` - Campaign brands

## Usage Examples

### Example 1: Simple Window Split

```python
import asyncio
from datetime import datetime
from src.services.brand_split_service import BrandSplitService

async def split_window():
    service = BrandSplitService()
    await service.initialize()

    try:
        brand_impacts = await service.split_audience_by_brand(
            frame_id=1234860035,
            campaign_id="16012",
            window_start=datetime(2025, 6, 1, 0, 0, 0),
            total_impacts=1000000
        )

        for brand_id, impacts in brand_impacts.items():
            print(f"Brand {brand_id}: {impacts:,.0f} impacts")

    finally:
        await service.cleanup()

asyncio.run(split_window())
```

### Example 2: Campaign Brand Analysis

```python
async def analyze_campaign():
    service = BrandSplitService()
    await service.initialize()

    try:
        # Get all brands
        brands = await service.get_campaign_brands(
            campaign_id="16012",
            start_date=date(2025, 6, 1),
            end_date=date(2025, 6, 30)
        )

        print(f"Campaign has {len(brands)} brands:")
        for brand in brands:
            print(f"  Brand {brand['spacebrandid']}: {brand['total_spots']} spots")

        # Find complex windows
        multi_brand = await service.get_multi_brand_windows(
            campaign_id="16012"
        )

        print(f"\n{len(multi_brand)} windows have multiple brands")

    finally:
        await service.cleanup()

asyncio.run(analyze_campaign())
```

### Example 3: Process Full Route API Response

```python
async def process_route_response():
    service = BrandSplitService()
    await service.initialize()

    try:
        # Assume route_response came from Route API
        route_response = {
            'campaign_id': '16012',
            'frames': [...]  # Full response from Route API
        }

        # Aggregate by brand
        result = await service.aggregate_brand_impacts(route_response)

        print(f"Total impacts: {result['total_impacts']:,}")
        print(f"Processing time: {result['processing_time_ms']:.2f}ms")

        for brand_id, data in result['brands'].items():
            print(f"\nBrand {brand_id}:")
            print(f"  Impacts: {data['total_impacts']:,.0f} ({data['proportion']:.1%})")
            print(f"  Windows: {data['windows']}")

    finally:
        await service.cleanup()

asyncio.run(process_route_response())
```

### Example 4: Integration with Route API Service

```python
from src.services.route_service import RouteService
from src.services.brand_split_service import BrandSplitService

async def get_campaign_with_brands():
    route_service = RouteService()
    brand_service = BrandSplitService()

    await route_service.initialize()
    await brand_service.initialize()

    try:
        # Get Route API data
        route_response = await route_service.get_campaign_playout(
            campaign_id="16012"
        )

        # Split by brands
        brand_results = await brand_service.aggregate_brand_impacts(
            route_response
        )

        return brand_results

    finally:
        await route_service.cleanup()
        await brand_service.cleanup()

asyncio.run(get_campaign_with_brands())
```

## Error Handling

### No Data Found

If no brand data exists for a window:
```python
brand_impacts = await service.split_audience_by_brand(...)
# Returns: {}

# Check result:
if not brand_impacts:
    print("No brand data - window may be empty or not in database")
```

### Database Connection Errors

```python
try:
    await service.initialize()
except Exception as e:
    print(f"Database connection failed: {e}")
    # Check:
    # 1. MS-01 database is accessible
    # 2. VPN is connected
    # 3. Credentials in .env are correct
```

### View Does Not Exist

```python
health = await service.health_check()
if not health.get('view_exists'):
    print("mv_playout_15min_brands view not found")
    # Need to create the view in MS-01 database
```

## Performance Considerations

### Caching

**Cache Hit**: ~0.1ms
**Database Query**: ~5-20ms (depending on network)

The service aggressively caches:
- Brand distributions (1 hour TTL)
- Proportions (reusable across different impact values)
- Campaign-level aggregations (30 minutes TTL)

### Batch Processing

When processing many windows:
```python
# Good: Single service instance, reuse connections
service = BrandSplitService()
await service.initialize()

for window in windows:
    await service.split_audience_by_brand(...)  # Reuses connection and cache

await service.cleanup()

# Bad: Creating new service for each window
for window in windows:
    service = BrandSplitService()  # Don't do this!
    await service.initialize()
    await service.split_audience_by_brand(...)
    await service.cleanup()
```

### Connection Pooling

Default pool: 2-10 connections
Configure via:
```python
from src.config.database import DatabaseConfig

db_config = DatabaseConfig()
db_config.postgres.min_pool_size = 5
db_config.postgres.max_pool_size = 20

service = BrandSplitService(db_config=db_config)
```

## Testing

### Run Test Suite

```bash
cd /Users/ianwyatt/PycharmProjects/Route-Playout-Econometrics_POC
python src/services/test_brand_split.py
```

**Tests Include:**
1. Health check and database connectivity
2. Get brand distribution for window
3. Split audience across brands
4. Get campaign brands summary
5. Find multi-brand windows
6. Aggregate full Route API response
7. Cache performance verification

### Test Requirements

- MS-01 database must be accessible
- VPN connection to MS-01 required
- `mv_playout_15min_brands` view must exist
- Campaign 16012 data should be present (or adjust test campaign ID)

## Integration Points

### 1. Route API Service Integration

When processing Route API playout responses:
```python
# Route service returns impacts per window
route_impacts = await route_service.get_playout(...)

# Brand service splits across brands
brand_impacts = await brand_service.split_audience_by_brand(
    frame_id=frame_id,
    campaign_id=campaign_id,
    window_start=window_start,
    total_impacts=route_impacts['impacts']
)
```

### 2. Export Integration

When exporting campaign data:
```python
# Add brand-level detail to exports
route_data = await route_service.get_campaign(...)
brand_data = await brand_service.aggregate_brand_impacts(route_data)

# Export with brand attribution
export_data = {
    'campaign_summary': route_data,
    'brand_breakdown': brand_data['brands']
}
```

### 3. UI Integration

Display brand splits in the UI:
```python
# In Streamlit/Gradio UI
brand_data = await brand_service.get_campaign_brands(campaign_id)

st.write(f"Campaign has {len(brand_data)} brands")
for brand in brand_data:
    st.write(f"Brand {brand['spacebrandid']}: {brand['total_spots']} spots")
```

## Troubleshooting

### Issue: Empty Results

**Symptom**: `split_audience_by_brand()` returns `{}`

**Possible Causes:**
1. mv_playout_15min_brands view is empty
2. Frame/campaign/window combination doesn't exist
3. Wrong database selected (local vs MS-01)

**Solutions:**
```python
# Check health
health = await service.health_check()
print(health)

# Verify database
db_info = service.db_config.get_active_database_info()
print(db_info)

# Query view directly
distribution = await service.get_brand_distribution(...)
print(f"Found {len(distribution)} brands")
```

### Issue: Slow Performance

**Symptom**: Queries take > 100ms

**Possible Causes:**
1. Cache not being used
2. Network latency to MS-01
3. View needs indexing

**Solutions:**
```python
# Check cache stats
print(f"Cache entries: {len(service._cache)}")

# Clear cache if stale
service.clear_cache()

# Verify cache is working
# First call: ~20ms, Second call: <1ms
```

### Issue: Connection Timeout

**Symptom**: `asyncpg.exceptions.ConnectionError`

**Possible Causes:**
1. MS-01 server unreachable
2. VPN not connected
3. Wrong credentials

**Solutions:**
```bash
# Test connectivity
ping 192.168.1.34

# Check VPN
# Connect to Route VPN

# Verify credentials in .env
cat .env | grep POSTGRES
```

## Future Enhancements

### Planned Features

1. **Brand Name Enrichment**
   - Integrate with SPACE API to get brand names
   - Cache brand metadata

2. **Historical Trends**
   - Track brand proportions over time
   - Identify brand mix changes

3. **Performance Metrics**
   - Track split accuracy
   - Monitor cache hit rates
   - Database query profiling

4. **Batch Processing**
   - Optimize for bulk campaign processing
   - Parallel window processing

5. **Export Formats**
   - CSV export with brand splits
   - Excel with brand sheets
   - Parquet for data science

## Related Documentation

- `/Claude/Documentation/APPLICATION_PORTS_GUIDE.md` - Application overview
- `/Claude/Handover/MASTER_HANDOVER_CURRENT.md` - Project status
- `/src/config/database.py` - Database configuration
- `/src/services/base.py` - Base service patterns

## Maintenance

### Regular Tasks

1. **Monitor View Refresh**
   - mv_playout_15min_brands should be refreshed daily
   - Check refresh status in MS-01

2. **Cache Management**
   - Cache clears automatically on TTL expiry
   - Manual clear if data updated: `service.clear_cache()`

3. **Performance Monitoring**
   - Track query times via logging
   - Check health_check() regularly

### Database Maintenance

```sql
-- Refresh materialized view (run on MS-01)
REFRESH MATERIALIZED VIEW mv_playout_15min_brands;

-- Check view size
SELECT pg_size_pretty(pg_total_relation_size('mv_playout_15min_brands'));

-- Check last refresh (if tracking column exists)
SELECT MAX(window_end) FROM mv_playout_15min_brands;
```

## Support

**Location**: `/Users/ianwyatt/PycharmProjects/Route-Playout-Econometrics_POC/src/services/brand_split_service.py`

**Database**: MS-01 (192.168.1.34) `route_poc` database

**Key View**: `mv_playout_15min_brands`

**Tests**: `/Users/ianwyatt/PycharmProjects/Route-Playout-Econometrics_POC/src/services/test_brand_split.py`

---

*Documentation created: October 17, 2025*
*Last updated: October 17, 2025*
