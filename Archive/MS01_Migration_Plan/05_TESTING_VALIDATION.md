# Testing & Validation - MS-01 Migration

**Date**: 2025-10-17
**Purpose**: Comprehensive testing procedures and validation scripts
**Status**: Ready to execute

---

## Table of Contents

1. [Pre-Deployment Testing](#pre-deployment-testing)
2. [MS-01 Connection Testing](#ms-01-connection-testing)
3. [Function Validation](#function-validation)
4. [Performance Benchmarks](#performance-benchmarks)
5. [Integration Testing](#integration-testing)
6. [Troubleshooting Tests](#troubleshooting-tests)

---

## Pre-Deployment Testing

### Checklist

Before deploying MS-01 integration, verify:

- [ ] VPN/network access to MS-01 (192.168.1.34) established
- [ ] MS-01 database credentials correct in `.env`
- [ ] Route releases table populated (R54-R61)
- [ ] Database views exist: `mv_playout_15min`, `mv_playout_15min_brands`
- [ ] Python dependencies installed (`asyncpg`, `pandas`, etc.)
- [ ] Local database available as fallback (if needed)

---

## MS-01 Connection Testing

### Test 1: Basic Connection

**Purpose**: Verify can connect to MS-01 database

**Script**: Run this in Python REPL or create test file

```python
import asyncio
import os

# Ensure MS-01 is selected
os.environ['USE_MS01_DATABASE'] = 'true'

from src.config.database import DatabaseConfig

async def test_connection():
    """Test basic MS-01 connection."""
    config = DatabaseConfig()

    print("=== MS-01 Connection Test ===")
    print()

    # Check active database
    db_info = config.get_active_database_info()
    print(f"Active Database: {db_info['database_mode']}")
    print(f"Host: {db_info['host']}")
    print(f"Database: {db_info['database']}")
    print(f"Description: {db_info['description']}")
    print()

    # Test connection
    import asyncpg

    try:
        conn = await asyncpg.connect(
            host=config.postgres.host,
            port=config.postgres.port,
            database=config.postgres.database,
            user=config.postgres.user,
            password=config.postgres.password,
            timeout=10
        )

        # Test query
        result = await conn.fetchval("SELECT 1")
        await conn.close()

        if result == 1:
            print("✅ MS-01 Connection Successful")
            return True
        else:
            print("❌ Connection test failed (unexpected result)")
            return False

    except asyncpg.exceptions.PostgresError as e:
        print(f"❌ PostgreSQL Error: {e}")
        print()
        print("Possible causes:")
        print("  - Incorrect credentials in .env")
        print("  - Database does not exist")
        print("  - User lacks permissions")
        return False

    except TimeoutError:
        print("❌ Connection Timeout")
        print()
        print("Possible causes:")
        print("  - Not connected to VPN")
        print("  - Firewall blocking port 5432")
        print("  - MS-01 server offline")
        print("  - Incorrect IP address (should be 192.168.1.34)")
        return False

    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False

# Run test
asyncio.run(test_connection())
```

**Expected Output** (Success):
```
=== MS-01 Connection Test ===

Active Database: MS-01 (Production)
Host: 192.168.1.34
Database: route_poc
Description: MS-01 Proxmox with 1.28B records

✅ MS-01 Connection Successful
```

**Expected Output** (Failure - VPN not connected):
```
❌ Connection Timeout

Possible causes:
  - Not connected to VPN
  - Firewall blocking port 5432
  - MS-01 server offline
  - Incorrect IP address (should be 192.168.1.34)
```

### Test 2: Check Database Views

**Purpose**: Verify required materialized views exist

```python
import asyncio
from src.db.ms01_helpers import initialize_ms01_database, _ms01_db

async def test_views():
    """Check if required views exist."""
    print("=== Database Views Test ===")
    print()

    await initialize_ms01_database()

    query = """
        SELECT table_name
        FROM information_schema.views
        WHERE table_schema = 'public'
          AND table_name IN ('mv_playout_15min', 'mv_playout_15min_brands')
        ORDER BY table_name;
    """

    try:
        results = await _ms01_db.execute_query(query)

        required_views = {'mv_playout_15min', 'mv_playout_15min_brands'}
        found_views = {row['table_name'] for row in results}

        print(f"Required views: {required_views}")
        print(f"Found views: {found_views}")
        print()

        missing = required_views - found_views

        if not missing:
            print("✅ All required views exist")
            return True
        else:
            print(f"❌ Missing views: {missing}")
            print()
            print("Action Required:")
            print("  Contact pipeline team to create materialized views")
            print("  SQL scripts should be in pipeline repository")
            return False

    except Exception as e:
        print(f"❌ Error checking views: {e}")
        return False

# Run test
asyncio.run(test_views())
```

### Test 3: Check Route Releases Table

**Purpose**: Verify route_releases table exists and is populated

```bash
# Run the setup script
python scripts/setup_route_releases.py

# Then run test script
python scripts/test_route_releases.py
```

**Expected Output**:
```
=== Route Release Database Tests ===

Test 1: Initialize Database
✅ Database initialized

Test 2: Insert Releases
✅ Inserted release R54 (Q1 2025)
✅ Inserted release R55 (Q2 2025)
✅ Inserted release R56 (Q3 2025)
✅ Inserted release R57 (Q4 2025)
✅ Inserted release R58 (Q1 2026)
✅ Inserted release R59 (Q2 2026)
✅ Inserted release R60 (Q3 2026)
✅ Inserted release R61 (Q4 2026)

Test 3: Get Release by Date
✅ Date 2025-07-15 → Release R55
✅ Date 2025-08-01 → Release R55
✅ Date 2025-10-01 → Release R56

... (continued)

=== All Tests Passed ===
```

---

## Function Validation

### Test 4: MS-01 Helper Functions

**Script**: `/Users/ianwyatt/PycharmProjects/Route-Playout-Econometrics_POC/examples/ms01_helpers_example.py`

```bash
python examples/ms01_helpers_example.py
```

**What It Tests**:
1. Campaign data for Route API (get_campaign_for_route_api)
2. Campaign summary (get_campaign_summary)
3. Date-filtered summary (get_campaign_by_date)
4. Hourly activity (get_hourly_activity)
5. Daily summary (get_daily_summary)
6. Route release lookup (get_route_release_for_date)
7. All Route releases (get_all_route_releases)
8. Brand-level reporting (get_campaign_by_brand)
9. Brand impact split (split_audience_by_brand)
10. Frame activity check (is_frame_active)
11. Frame campaigns (get_frame_campaigns)
12. Data freshness (check_data_freshness)
13. Date coverage (get_date_coverage)
14. All campaigns list (get_all_campaigns)

**Expected Output** (Sample):
```
=== MS-01 Database Helper Examples ===

Example 1: Get campaign for Route API
Campaign ID: 18295, Date Range: 2025-08-01 to 2025-09-01
Found 4,182 windows for Route API
First window: Frame 1234567890 at 2025-08-01 00:00:00
  10 spots, 150s playout length, 300s break length

Example 2: Get campaign summary
Campaign ID: 18295
Total Frames: 145
Days Active: 31
Total Playouts: 12,450
Date Range: 2025-08-01 to 2025-08-31
Avg Spot Length: 15.2s
Avg Spots/Window: 2.8

... (continued for all 14 examples)
```

**Validation Criteria**:
- All functions execute without errors
- Returned data matches expected types
- Non-empty results for test campaign IDs
- Query times <5 seconds per function

### Test 5: Brand Split Service

**Script**: `/Users/ianwyatt/PycharmProjects/Route-Playout-Econometrics_POC/src/services/test_brand_split.py`

```bash
python src/services/test_brand_split.py
```

**What It Tests**:
1. Service initialization
2. Brand distribution lookup
3. Single window brand split
4. Campaign brand list
5. Multi-brand window detection
6. Route API response aggregation
7. Health check

**Expected Output**:
```
=== Brand Split Service Tests ===

Test 1: Service Initialization
✅ Service initialized
✅ Connection pool active

Test 2: Brand Distribution Lookup
Campaign: 18699, Window: 2025-08-23 11:15:00
✅ Found 2 brands:
  Brand 21143: 3 spots
  Brand 21146: 1 spot

Test 3: Single Window Split
Total impacts: 1,000,000
✅ Split across brands:
  Brand 21143: 750,000 (75.0%)
  Brand 21146: 250,000 (25.0%)
✅ Sum validation: 1,000,000 (100.0%)

Test 4: Campaign Brands
Campaign: 18699
✅ Found 2 brands:
  Brand 21143: 360 spots on 8 frames
  Brand 21146: 120 spots on 8 frames

Test 5: Multi-Brand Windows
✅ Found 160 multi-brand windows
  Most complex: 2 brands in one window

Test 6: Aggregate Route API Response
✅ Processed 2 windows in 45.23ms
  Total impacts: 2,200,000
  Brand 21143: 1,650,000 (75.0%)
  Brand 21146: 550,000 (25.0%)

Test 7: Health Check
✅ Service healthy
  Database: connected
  View exists: True
  Cache entries: 5

=== All Tests Passed ===
```

**Validation Criteria**:
- All tests pass without errors
- Brand split sums equal total impacts (100%)
- Processing time <100ms for aggregation
- Health check shows "connected"

### Test 6: Route Release Functions

**Script**: `/Users/ianwyatt/PycharmProjects/Route-Playout-Econometrics_POC/scripts/test_route_releases.py`

```bash
python scripts/test_route_releases.py
```

**What It Tests**:
1. Database initialization
2. Table creation
3. Release insertion (R54-R61)
4. Get release by date
5. Get release by number
6. Get current release
7. Get all releases
8. Date range queries
9. Coverage validation (with gaps)
10. Coverage validation (complete)
11. Cache hit/miss statistics

**Validation Criteria**:
- All 8 releases inserted successfully
- Date lookups return correct release
- Coverage validation detects gaps
- Cache hit rate >70% after warmup

---

## Performance Benchmarks

### Test 7: Query Performance

**Purpose**: Validate query times meet performance targets

```python
import asyncio
import time
from src.db.ms01_helpers import *

async def benchmark_queries():
    """Benchmark all query functions."""
    print("=== Query Performance Benchmarks ===")
    print()

    await initialize_ms01_database()

    benchmarks = []

    # Test 1: Campaign Route API data (target: <1 sec)
    start = time.time()
    data = await get_campaign_for_route_api('18295', '2025-08-01', '2025-09-01')
    elapsed = time.time() - start
    benchmarks.append(('Campaign Route API data', len(data), elapsed, 1.0))
    print(f"Campaign Route API data: {elapsed:.3f}s ({len(data)} windows)")

    # Test 2: Campaign summary (target: <0.5 sec)
    start = time.time()
    summary = await get_campaign_summary('18295')
    elapsed = time.time() - start
    benchmarks.append(('Campaign summary', 1, elapsed, 0.5))
    print(f"Campaign summary: {elapsed:.3f}s")

    # Test 3: Hourly activity (target: <1 sec)
    start = time.time()
    hourly = await get_hourly_activity('18295', '2025-08-01', '2025-08-07')
    elapsed = time.time() - start
    benchmarks.append(('Hourly activity', len(hourly), elapsed, 1.0))
    print(f"Hourly activity: {elapsed:.3f}s ({len(hourly)} hours)")

    # Test 4: Daily summary (target: <1 sec)
    start = time.time()
    daily = await get_daily_summary('18295', '2025-08-01', '2025-09-01')
    elapsed = time.time() - start
    benchmarks.append(('Daily summary', len(daily), elapsed, 1.0))
    print(f"Daily summary: {elapsed:.3f}s ({len(daily)} days)")

    # Test 5: Brand-level data (target: <0.5 sec)
    start = time.time()
    brands = await get_campaign_by_brand('18699', '2025-08-20', '2025-08-25')
    elapsed = time.time() - start
    benchmarks.append(('Brand breakdown', len(brands), elapsed, 0.5))
    print(f"Brand breakdown: {elapsed:.3f}s ({len(brands)} brands)")

    # Test 6: Route release lookup (target: <0.1 sec, cached)
    from src.db.route_releases import get_release_for_date
    from datetime import date

    start = time.time()
    release = await get_release_for_date(date(2025, 7, 15))
    elapsed = time.time() - start
    benchmarks.append(('Release lookup (cold)', 1, elapsed, 0.1))
    print(f"Release lookup (cold): {elapsed:.3f}s")

    start = time.time()
    release = await get_release_for_date(date(2025, 7, 15))
    elapsed = time.time() - start
    benchmarks.append(('Release lookup (cached)', 1, elapsed, 0.01))
    print(f"Release lookup (cached): {elapsed:.3f}s")

    print()
    print("=== Performance Summary ===")
    print()

    passed = 0
    failed = 0

    for name, count, elapsed, target in benchmarks:
        status = "✅" if elapsed <= target else "❌"
        if elapsed <= target:
            passed += 1
        else:
            failed += 1
        print(f"{status} {name}: {elapsed:.3f}s (target: {target}s)")

    print()
    print(f"Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("✅ All performance benchmarks met")
    else:
        print("⚠️  Some benchmarks failed - review query optimization")

# Run benchmarks
asyncio.run(benchmark_queries())
```

**Expected Performance Targets**:
| Query | Target | Acceptable | Slow |
|-------|--------|------------|------|
| Campaign Route API data | <1s | <3s | >5s |
| Campaign summary | <0.5s | <1s | >2s |
| Hourly activity | <1s | <2s | >5s |
| Daily summary | <1s | <2s | >5s |
| Brand breakdown | <0.5s | <1s | >2s |
| Release lookup (cold) | <0.1s | <0.3s | >0.5s |
| Release lookup (cached) | <0.01s | <0.05s | >0.1s |

### Test 8: Brand Split Performance

```python
import asyncio
import time
from datetime import datetime
from src.services.brand_split_service import BrandSplitService

async def benchmark_brand_split():
    """Benchmark brand split operations."""
    print("=== Brand Split Performance Benchmarks ===")
    print()

    service = BrandSplitService()
    await service.initialize()

    try:
        # Test 1: Single window split (target: <25ms)
        start = time.time()
        brand_impacts = await service.split_audience_by_brand(
            frame_id=1234859642,
            campaign_id='18699',
            window_start=datetime(2025, 8, 23, 11, 15),
            total_impacts=1000000
        )
        elapsed = (time.time() - start) * 1000  # Convert to ms
        print(f"Single window split: {elapsed:.2f}ms (target: <25ms)")

        if elapsed < 25:
            print("✅ Performance excellent")
        elif elapsed < 100:
            print("⚠️  Performance acceptable but could be optimized")
        else:
            print("❌ Performance poor - investigate query optimization")

        print()

        # Test 2: Campaign brand lookup (target: <100ms)
        from datetime import date

        start = time.time()
        brands = await service.get_campaign_brands(
            campaign_id='18699',
            start_date=date(2025, 8, 20),
            end_date=date(2025, 8, 25)
        )
        elapsed = (time.time() - start) * 1000
        print(f"Campaign brands: {elapsed:.2f}ms (target: <100ms)")

        if elapsed < 100:
            print("✅ Performance excellent")
        elif elapsed < 500:
            print("⚠️  Performance acceptable")
        else:
            print("❌ Performance poor")

        print()

        # Test 3: Aggregate 160 windows (target: <500ms)
        # Simulate Route API response with 160 windows
        route_response = {
            'campaign_id': '18699',
            'frames': []
        }

        # Create test data
        for i in range(160):
            if i % 10 == 0:
                route_response['frames'].append({
                    'frame_id': 1234859642,
                    'campaign_id': '18699',
                    'windows': []
                })

            window_start = f'2025-08-23 {i // 4:02d}:{(i % 4) * 15:02d}:00'
            route_response['frames'][-1]['windows'].append({
                'window_start': window_start,
                'impacts': 1000000
            })

        start = time.time()
        result = await service.aggregate_brand_impacts(route_response)
        elapsed = (time.time() - start) * 1000
        print(f"Aggregate 160 windows: {elapsed:.2f}ms (target: <500ms)")
        print(f"  Processing rate: {160 / (elapsed / 1000):.0f} windows/sec")

        if elapsed < 500:
            print("✅ Performance excellent")
        elif elapsed < 2000:
            print("⚠️  Performance acceptable")
        else:
            print("❌ Performance poor")

        # Cache statistics
        print()
        print("Cache Statistics:")
        print(f"  Cache entries: {len(service._cache)}")
        # Note: BaseService doesn't expose cache stats directly, but we can check size

    finally:
        await service.cleanup()

# Run benchmarks
asyncio.run(benchmark_brand_split())
```

---

## Integration Testing

### Test 9: End-to-End Campaign Processing

**Purpose**: Test complete workflow from query to export

```python
import asyncio
from src.db.ms01_helpers import get_campaign_for_route_api, build_route_api_payload
from src.db.route_releases import get_releases_for_date_range
from datetime import date

async def test_end_to_end():
    """Test end-to-end campaign processing workflow."""
    print("=== End-to-End Integration Test ===")
    print()

    campaign_id = '18295'
    start_date = '2025-08-01'
    end_date = '2025-08-31'

    print(f"Testing campaign: {campaign_id}")
    print(f"Date range: {start_date} to {end_date}")
    print()

    # Step 1: Query campaign data
    print("Step 1: Query campaign data...")
    try:
        campaign_data = await get_campaign_for_route_api(campaign_id, start_date, end_date)

        if not campaign_data:
            print("❌ No campaign data found")
            return False

        print(f"✅ Found {len(campaign_data)} windows")
    except Exception as e:
        print(f"❌ Query failed: {e}")
        return False

    # Step 2: Determine Route release
    print()
    print("Step 2: Determine Route release...")
    try:
        releases = await get_releases_for_date_range(
            date.fromisoformat(start_date),
            date.fromisoformat(end_date)
        )

        if not releases:
            print("❌ No Route release found")
            return False

        route_release = releases[-1].release_number
        print(f"✅ Using Route release: {route_release}")
    except Exception as e:
        print(f"❌ Release lookup failed: {e}")
        return False

    # Step 3: Build Route API payload
    print()
    print("Step 3: Build Route API payload...")
    try:
        payload = build_route_api_payload(campaign_data, route_release)

        if 'frames' not in payload:
            print("❌ Invalid payload structure")
            return False

        print(f"✅ Payload ready: {len(payload['frames'])} frames")

        # Validate payload structure
        assert 'route_release_id' in payload
        assert payload['route_release_id'] == route_release
        assert len(payload['frames']) > 0

        frame = payload['frames'][0]
        assert 'frame_id' in frame
        assert 'windows' in frame
        assert len(frame['windows']) > 0

        window = frame['windows'][0]
        assert 'datetime_from' in window
        assert 'datetime_to' in window
        assert 'spot_count' in window
        assert 'playout_length' in window
        assert 'break_length' in window

        print("✅ Payload structure validated")

    except Exception as e:
        print(f"❌ Payload build failed: {e}")
        return False

    print()
    print("✅ End-to-end test passed")
    return True

# Run test
success = asyncio.run(test_end_to_end())
exit(0 if success else 1)
```

### Test 10: Database Switching

**Purpose**: Verify seamless database switching works

```bash
# Test script: test_database_switching.sh

#!/bin/bash

echo "=== Database Switching Test ==="
echo

# Test MS-01
echo "Test 1: MS-01 Database"
export USE_MS01_DATABASE=true
python -c "
import asyncio
from src.config.database import DatabaseConfig

async def test():
    config = DatabaseConfig()
    info = config.get_active_database_info()
    print(f\"Active: {info['database_mode']}\")
    print(f\"Host: {info['host']}\")
    assert info['is_ms01'] == True, 'Should be MS-01'
    print('✅ MS-01 selected correctly')

asyncio.run(test())
"

echo

# Test Local
echo "Test 2: Local Database"
export USE_MS01_DATABASE=false
python -c "
import asyncio
from src.config.database import DatabaseConfig

async def test():
    config = DatabaseConfig()
    info = config.get_active_database_info()
    print(f\"Active: {info['database_mode']}\")
    print(f\"Host: {info['host']}\")
    assert info['is_local'] == True, 'Should be local'
    print('✅ Local selected correctly')

asyncio.run(test())
"

echo
echo "✅ Database switching test passed"
```

---

## Troubleshooting Tests

### Test 11: Network Connectivity

```bash
# Test MS-01 network access
ping -c 3 192.168.1.34

# Test PostgreSQL port
nc -zv 192.168.1.34 5432

# Test with psql (if installed)
PGPASSWORD="$POSTGRES_PASSWORD_PRIMARY" psql -h 192.168.1.34 -U postgres -d route_poc -c "SELECT 1"
```

### Test 12: View Data Quality

```python
import asyncio
from src.db.ms01_helpers import check_data_freshness, get_date_coverage

async def test_data_quality():
    """Check data freshness and coverage."""
    print("=== Data Quality Test ===")
    print()

    # Check freshness
    freshness = await check_data_freshness()
    print(f"Data Freshness:")
    print(f"  Latest window: {freshness['latest_window']}")
    print(f"  Latest playout: {freshness['latest_playout']}")
    print(f"  Hours old: {freshness['hours_old']:.1f}h")
    print()

    if freshness['hours_old'] < 48:
        print("✅ Data is fresh (<48 hours old)")
    else:
        print("⚠️  Data is stale (>48 hours old)")
        print("   Check pipeline refresh schedule")

    print()

    # Check coverage
    coverage = await get_date_coverage()
    print(f"Data Coverage:")
    print(f"  Start date: {coverage['start_date']}")
    print(f"  End date: {coverage['end_date']}")
    print(f"  Days with data: {coverage['days_with_data']}")
    print()

    expected_days = (coverage['end_date'] - coverage['start_date']).days + 1
    coverage_percent = (coverage['days_with_data'] / expected_days) * 100

    print(f"Coverage: {coverage_percent:.1f}%")

    if coverage_percent > 95:
        print("✅ Good coverage (>95%)")
    elif coverage_percent > 80:
        print("⚠️  Acceptable coverage (80-95%)")
    else:
        print("❌ Poor coverage (<80%)")

asyncio.run(test_data_quality())
```

---

## Validation Summary

### Quick Validation Checklist

Run these commands in order:

```bash
# 1. Connection test
python -c "import asyncio; from src.db.ms01_helpers import initialize_ms01_database; asyncio.run(initialize_ms01_database())"

# 2. Setup Route releases
python scripts/setup_route_releases.py

# 3. Test MS-01 helpers
python examples/ms01_helpers_example.py

# 4. Test brand split
python src/services/test_brand_split.py

# 5. Test route releases
python scripts/test_route_releases.py

# If all pass:
echo "✅ All validation tests passed - Ready for production"
```

### Expected Timeline

| Test Suite | Duration | When to Run |
|------------|----------|-------------|
| Connection tests | 1-2 min | Once at setup |
| Function validation | 5-10 min | After code deploy |
| Performance benchmarks | 2-3 min | Weekly / after optimization |
| Integration tests | 3-5 min | Before production deploy |
| Troubleshooting tests | 1-2 min | When issues arise |

---

## Success Criteria

### Required for Production

- ✅ MS-01 connection successful
- ✅ All database views exist
- ✅ Route releases table populated (R54-R61)
- ✅ All 17 helper functions return data
- ✅ Brand split sums equal 100%
- ✅ Query performance meets targets (<5s per query)
- ✅ End-to-end test passes

### Nice to Have

- ✅ Cache hit rate >70%
- ✅ Data freshness <24 hours
- ✅ Data coverage >95%
- ✅ All performance benchmarks met
- ✅ Database switching works

---

**Prepared By**: Claude Code Agent Team
**Date**: 2025-10-17
**Status**: Ready for Testing
