# Route Release Helper Functions - Quick Reference

## Overview

The `/Users/ianwyatt/PycharmProjects/Route-Playout-Econometrics_POC/src/db/route_releases.py` module provides helper functions for Route release lookups using the `route_releases` table in the MS-01 database.

## Key Features

- ✅ Automatic release detection for playout dates
- ✅ Date range coverage validation
- ✅ Built-in caching (24-hour TTL)
- ✅ Both async and sync versions
- ✅ Comprehensive error handling
- ✅ Database config integration

## New Helper Functions

### 1. Get Release for Specific Date

**Async:**
```python
from src.db.route_releases import get_release_for_date
from datetime import date

release = await get_release_for_date(date(2025, 7, 15))
print(f"Release: {release.release_number}")
# Output: Release: R55
```

**Sync:**
```python
from src.db.route_releases import get_route_release_for_date_sync
from datetime import date

release = get_route_release_for_date_sync(date(2025, 7, 15))
print(f"Release: {release.release_number}")
```

### 2. Get Releases for Date Range

**Async:**
```python
from src.db.route_releases import get_releases_for_date_range
from datetime import date

releases = await get_releases_for_date_range(
    date(2025, 7, 1),
    date(2025, 12, 31)
)
for r in releases:
    print(f"{r.release_number}: {r.trading_period_start} - {r.trading_period_end}")
```

**Sync:**
```python
from src.db.route_releases import get_route_release_for_date_range_sync

releases = get_route_release_for_date_range_sync(
    date(2025, 7, 1),
    date(2025, 12, 31)
)
```

### 3. Get All Available Releases

**Async:**
```python
from src.db.route_releases import get_all_releases

all_releases = await get_all_releases()
print(f"Total releases: {len(all_releases)}")
```

**Sync:**
```python
from src.db.route_releases import get_all_route_releases_sync

all_releases = get_all_route_releases_sync()
```

### 4. Get Current Active Release

**Async:**
```python
from src.db.route_releases import get_current_release

current = await get_current_release()
print(f"Current: {current.release_number}")
```

**Sync:**
```python
from src.db.route_releases import get_current_route_release_sync

current = get_current_route_release_sync()
```

### 5. Validate Release Coverage

**Async:**
```python
from src.db.route_releases import validate_release_coverage
from datetime import date

result = await validate_release_coverage(
    date(2025, 7, 1),
    date(2025, 12, 31)
)

if result['has_coverage']:
    print(f"✅ {result['message']}")
    print(f"Coverage: {result['coverage_percent']}%")
else:
    print(f"⚠️  {result['message']}")
    for gap_start, gap_end in result['gaps']:
        print(f"Gap: {gap_start} to {gap_end}")
```

**Sync:**
```python
from src.db.route_releases import validate_release_coverage_sync

result = validate_release_coverage_sync(
    date(2025, 7, 1),
    date(2025, 12, 31)
)
```

## Cache Management

### Get Cache Statistics

```python
from src.db.route_releases import route_release_db

stats = route_release_db.get_cache_stats()
print(f"Hit rate: {stats['hit_rate_percent']}%")
print(f"Size: {stats['size']}/{stats['max_size']}")
```

### Clear Cache

```python
route_release_db.clear_cache()
```

## Practical Use Cases

### Use Case 1: Campaign Date Validation

```python
from src.db.route_releases import validate_release_coverage_sync
from datetime import date

campaign_start = date(2025, 7, 1)
campaign_end = date(2025, 7, 31)

result = validate_release_coverage_sync(campaign_start, campaign_end)

if not result['has_coverage']:
    raise ValueError(f"Campaign dates have gaps: {result['message']}")

# Proceed with campaign processing
```

### Use Case 2: Determine Release for Playout

```python
from src.db.route_releases import get_route_release_for_date_sync
from datetime import date

playout_date = date(2025, 7, 15)
release = get_route_release_for_date_sync(playout_date)

if release:
    # Use release.release_number for Route API call
    release_id = int(release.release_number.replace('R', ''))
    print(f"Use release ID {release_id} for Route API")
else:
    raise ValueError(f"No release found for {playout_date}")
```

### Use Case 3: Check Data Availability

```python
from src.db.route_releases import validate_release_coverage_sync
from datetime import date

model_start = date(2025, 6, 1)
model_end = date(2025, 12, 31)

result = validate_release_coverage_sync(model_start, model_end)

print(f"Data coverage: {result['coverage_percent']}%")
print(f"Covered days: {result['covered_days']}/{result['total_days']}")

if result['coverage_percent'] < 95:
    print("⚠️  Warning: Incomplete data coverage for econometric model")
```

## Error Handling

### ReleaseNotFoundError

```python
from src.db.route_releases import (
    get_route_release_for_date_sync,
    ReleaseNotFoundError
)

try:
    release = get_route_release_for_date_sync(date(2020, 1, 1))
    if not release:
        raise ReleaseNotFoundError("No release for old date")
except ReleaseNotFoundError as e:
    print(f"Error: {e}")
```

### ReleaseCoverageError

```python
from src.db.route_releases import (
    validate_release_coverage_sync,
    ReleaseCoverageError
)

result = validate_release_coverage_sync(start_date, end_date)
if not result['has_coverage']:
    raise ReleaseCoverageError(result['message'])
```

## Configuration

The module automatically uses database configuration from:
1. `src.config.database.DatabaseConfig` (preferred)
2. Environment variables (fallback):
   - `POSTGRES_HOST`, `POSTGRES_PORT`
   - `POSTGRES_DATABASE`, `POSTGRES_USER`, `POSTGRES_PASSWORD`

## Database Schema

The `route_releases` table schema:

```sql
CREATE TABLE route_releases (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    release_number VARCHAR(20) NOT NULL UNIQUE,
    data_publication DATE NOT NULL,
    trading_period_start DATE NOT NULL,
    trading_period_end DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for fast lookups
CREATE INDEX idx_route_releases_trading_period 
ON route_releases (trading_period_start, trading_period_end);

CREATE INDEX idx_route_releases_number 
ON route_releases (release_number);
```

## Caching Behavior

- **TTL**: 24 hours (releases rarely change)
- **Size**: 100 entries
- **Cleanup**: Every hour
- **Strategy**: LRU eviction when full
- **Cached Queries**:
  - Release by date
  - Release by date range
  - All releases

## Performance

- First query: Database hit (~50-100ms)
- Cached queries: <1ms
- Date range queries: Optimized with SQL indexes
- Coverage validation: Single query + in-memory processing

## Testing

Run the demo script:

```bash
python scripts/demo_route_release_helpers.py
```

Run comprehensive tests:

```bash
python scripts/test_route_releases.py
```

## Files Modified

- `/Users/ianwyatt/PycharmProjects/Route-Playout-Econometrics_POC/src/db/route_releases.py` - Enhanced with new functions
- `/Users/ianwyatt/PycharmProjects/Route-Playout-Econometrics_POC/scripts/demo_route_release_helpers.py` - New demo script

## Related Documentation

- Route Release Table Setup: See `scripts/setup_route_releases.py`
- Route API Integration: See `Claude/Documentation/APPLICATION_PORTS_GUIDE.md`
- Database Configuration: See `src/config/database.py`

## Summary

The Route release helper functions provide a simple, cached, and reliable way to:

1. ✅ Determine which Route release to use for playout dates
2. ✅ Validate date ranges have complete coverage
3. ✅ Get all available releases for UI/reporting
4. ✅ Handle both async and sync contexts
5. ✅ Minimize database load with intelligent caching

Perfect for integration with the Route API playout endpoint for econometric analysis.
