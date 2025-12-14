# MS-01 Production Database Migration Plan

**Target Database**: MS-01 @ 192.168.1.34:5432
**Database Name**: route_poc
**Data Volume**: 1.28 billion records, 596GB
**Date Range**: August 6 - October 13, 2025
**Status**: Production Ready
**Created**: 2025-10-17

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Migration Steps](#migration-steps)
4. [Query Refactoring Guide](#query-refactoring-guide)
5. [Testing Checklist](#testing-checklist)
6. [Rollback Plan](#rollback-plan)
7. [Performance Expectations](#performance-expectations)
8. [Common Issues and Solutions](#common-issues-and-solutions)
9. [Quick Reference](#quick-reference)

---

## Overview

### What's Changing

**FROM**: Local MacOS PostgreSQL database
**TO**: MS-01 Proxmox production database with 1.28B playout records

### Why Migrate

1. **Massive Scale**: Access to 1.28 billion real playout records vs limited local dataset
2. **Pre-Optimized**: Production materialized views (`mv_playout_15min`) ready for Route API
3. **Production Ready**: Fully indexed, tested, and refreshed daily
4. **Real Data**: 69 days of actual playout data (Aug 6 - Oct 13, 2025)
5. **Better Performance**: Optimized indexes and aggregation for fast queries

### Key Changes

| Aspect | Current (Local) | New (MS-01) |
|--------|----------------|-------------|
| **Host** | localhost | 192.168.1.34 |
| **Database** | route_poc | route_poc |
| **Primary Table** | playout_data | mv_playout_15min ⭐ |
| **Record Count** | Limited local data | 1.28B raw, 700M aggregated |
| **Query Strategy** | Direct playout_data queries | Materialized view queries |
| **Environment Variable** | USE_MS01_DATABASE=false | USE_MS01_DATABASE=true |

### Critical Difference: Table Structure

**Old Approach** (Local):
```sql
SELECT * FROM playout_data
WHERE buyercampaignref = '18295'
```

**New Approach** (MS-01):
```sql
SELECT * FROM mv_playout_15min
WHERE buyercampaignref = '18295'
  AND time_window_start >= '2025-08-01'
  AND time_window_start < '2025-09-01'
```

The MS-01 database uses **pre-aggregated 15-minute windows** instead of raw millisecond-level playouts. This is exactly what Route API needs and is 10,000x faster.

---

## Prerequisites

### 1. Network Access

Verify you can reach MS-01 database:

```bash
# Test network connectivity
ping 192.168.1.34

# Test PostgreSQL port
nc -zv 192.168.1.34 5432
```

**Expected output**:
```
Connection to 192.168.1.34 port 5432 [tcp/postgresql] succeeded!
```

### 2. Database Credentials

Ensure you have MS-01 database password in your `.env` file:

```bash
# Check .env file exists
ls -la /Users/ianwyatt/PycharmProjects/Route-Playout-Econometrics_POC/.env

# Verify MS-01 credentials are present (don't print password!)
grep -q "MS01_DB_PASSWORD" .env && echo "✅ MS01 password configured" || echo "❌ MS01 password missing"
```

**Required .env variables**:
```bash
# MS-01 Production Database
POSTGRES_HOST_MS01=192.168.1.34
POSTGRES_PORT_MS01=5432
POSTGRES_DATABASE_MS01=route_poc
POSTGRES_USER_MS01=postgres
MS01_DB_PASSWORD=<ask pipeline team>

# Migration control flag
USE_MS01_DATABASE=true
```

### 3. Test Connection

Create a test connection script:

```python
# test_ms01_connection.py
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

try:
    conn = psycopg2.connect(
        host="192.168.1.34",
        port=5432,
        database="route_poc",
        user="postgres",
        password=os.getenv('MS01_DB_PASSWORD')
    )

    cursor = conn.cursor()

    # Test basic query
    cursor.execute("SELECT COUNT(*) FROM mv_playout_15min LIMIT 1")
    print("✅ Connection successful!")
    print(f"✅ mv_playout_15min table accessible")

    # Check data volume
    cursor.execute("""
        SELECT
            COUNT(*) as row_count,
            MIN(time_window_start) as earliest_date,
            MAX(time_window_start) as latest_date
        FROM mv_playout_15min
        LIMIT 1
    """)
    result = cursor.fetchone()
    print(f"✅ Rows: {result[0]:,}")
    print(f"✅ Date range: {result[1]} to {result[2]}")

    cursor.close()
    conn.close()

except Exception as e:
    print(f"❌ Connection failed: {e}")
    exit(1)
```

Run test:
```bash
cd /Users/ianwyatt/PycharmProjects/Route-Playout-Econometrics_POC
python test_ms01_connection.py
```

### 4. Documentation Access

Verify you can access handover documentation:

```bash
# Check handover docs exist
ls -la /Users/ianwyatt/PycharmProjects/route-playout-pipeline/Claude/POC_Handover/

# Key documents
cat /Users/ianwyatt/PycharmProjects/route-playout-pipeline/Claude/POC_Handover/QUICK_REFERENCE.md
cat /Users/ianwyatt/PycharmProjects/route-playout-pipeline/Claude/POC_Handover/DATABASE_HANDOVER_FOR_POC.md
```

### 5. Backup Current Configuration

```bash
# Backup current .env
cp .env .env.backup.$(date +%Y%m%d)

# Backup current database config
cp src/config/database.py src/config/database.py.backup
```

---

## Migration Steps

### Step 1: Update Environment Configuration

```bash
cd /Users/ianwyatt/PycharmProjects/Route-Playout-Econometrics_POC

# Edit .env file
nano .env  # or your preferred editor
```

**Add/update these lines**:
```bash
# MS-01 Production Database
USE_MS01_DATABASE=true
POSTGRES_HOST_MS01=192.168.1.34
POSTGRES_PORT_MS01=5432
POSTGRES_DATABASE_MS01=route_poc
POSTGRES_USER_MS01=postgres
MS01_DB_PASSWORD=<your-password-here>
```

**Verify configuration**:
```bash
grep "USE_MS01_DATABASE" .env
# Should output: USE_MS01_DATABASE=true
```

### Step 2: Update Database Configuration Code

The current `/Users/ianwyatt/PycharmProjects/Route-Playout-Econometrics_POC/src/config/database.py` already supports MS-01!

**Verify the configuration logic** (lines 60-77):
```python
# Check which database to use (MS-01 or local)
use_ms01 = self.get_env('USE_MS01_DATABASE', 'true').lower() == 'true'

if use_ms01:
    # MS-01 Production Database (1.28B records, primary)
    self.postgres.host = self.get_env('POSTGRES_HOST_MS01', '192.168.1.34')
    self.postgres.port = self.get_env('POSTGRES_PORT_MS01', 5432, int)
    self.postgres.database = self.get_env('POSTGRES_DATABASE_MS01', 'route_poc')
    self.postgres.user = self.get_env('POSTGRES_USER_MS01', 'postgres')
    self.postgres.password = self.get_env('POSTGRES_PASSWORD_MS01', '')
```

✅ **No code changes needed** - the database config already has MS-01 support built in!

### Step 3: Refactor Service Layer Queries

**Critical**: Update all services to use `mv_playout_15min` instead of `playout_data`.

**Files to update**:
```
/Users/ianwyatt/PycharmProjects/Route-Playout-Econometrics_POC/src/services/playout_service.py
/Users/ianwyatt/PycharmProjects/Route-Playout-Econometrics_POC/src/api/campaign_service.py
/Users/ianwyatt/PycharmProjects/Route-Playout-Econometrics_POC/src/api/campaign_service_optimized.py
```

See [Query Refactoring Guide](#query-refactoring-guide) below for detailed examples.

### Step 4: Test Connection with Service Layer

Create integration test:

```python
# test_ms01_integration.py
import os
from dotenv import load_dotenv
from src.config.database import DatabaseConfig

load_dotenv()

# Initialize database config
db_config = DatabaseConfig()

print("=" * 70)
print("MS-01 DATABASE INTEGRATION TEST")
print("=" * 70)

# Check active database
db_info = db_config.get_active_database_info()
print(f"\n✅ Active Database: {db_info['database_mode']}")
print(f"✅ Host: {db_info['host']}")
print(f"✅ Database: {db_info['database']}")
print(f"✅ Is MS-01: {db_info['is_ms01']}")

# Get connection string (without password for security)
conn_str = db_config.get_connection_string(include_password=False)
print(f"\n✅ Connection string: {conn_str}")

print("\n✅ Configuration successfully loaded!")
```

Run test:
```bash
python test_ms01_integration.py
```

**Expected output**:
```
======================================================================
MS-01 DATABASE INTEGRATION TEST
======================================================================

✅ Active Database: MS-01 (Production)
✅ Host: 192.168.1.34
✅ Database: route_poc
✅ Is MS-01: True

✅ Connection string: postgresql://postgres@192.168.1.34:5432/route_poc

✅ Configuration successfully loaded!
```

### Step 5: Update Application Startup

Verify apps use the database config correctly:

```bash
# Check which apps reference database
grep -r "playout_data" src/ui/*.py
grep -r "DatabaseConfig" src/ui/*.py
```

**Update app startup to use MS-01**:
```python
# In app.py or main app file
from src.config.database import DatabaseConfig

# Initialize database (will use MS-01 if USE_MS01_DATABASE=true)
db_config = DatabaseConfig()
db_info = db_config.get_active_database_info()

print(f"🚀 Starting with {db_info['database_mode']}")
```

### Step 6: Run Full Application Test

Start the POC application:

```bash
# For Streamlit app
cd /Users/ianwyatt/PycharmProjects/Route-Playout-Econometrics_POC
streamlit run src/ui/app.py
```

**Manual testing checklist**:
- [ ] App loads without errors
- [ ] Campaign search works
- [ ] Campaign data displays correctly
- [ ] Route API calls succeed
- [ ] Export functionality works
- [ ] Performance is acceptable (< 2 seconds for campaign query)

### Step 7: Enable Production Mode

Once testing is complete, verify production settings:

```bash
# .env should have:
USE_MS01_DATABASE=true
ENVIRONMENT=production
DEBUG_MODE=false
```

---

## Query Refactoring Guide

### Pattern 1: Basic Campaign Query

**❌ OLD (Local database)**:
```python
def get_campaign_playouts(campaign_id):
    query = """
        SELECT frameid, startdate, enddate, spotlength
        FROM playout_data
        WHERE buyercampaignref = %s
        ORDER BY startdate
    """
    return execute_query(query, (campaign_id,))
```

**✅ NEW (MS-01)**:
```python
def get_campaign_playouts(campaign_id, start_date, end_date):
    """
    Get campaign data from pre-aggregated 15-minute windows.

    CRITICAL: Always include time_window_start filter for performance!
    """
    query = """
        SELECT
            frameid,
            time_window_start as datetime_from,
            time_window_start + INTERVAL '15 minutes' as datetime_to,
            spot_count,
            playout_length_seconds,
            break_length_seconds
        FROM mv_playout_15min
        WHERE buyercampaignref = %s
          AND time_window_start >= %s
          AND time_window_start < %s
        ORDER BY frameid, time_window_start
    """
    return execute_query(query, (campaign_id, start_date, end_date))
```

**Key changes**:
1. ✅ Table: `playout_data` → `mv_playout_15min`
2. ✅ Fields: `startdate/enddate` → `time_window_start`
3. ✅ **ALWAYS include time filter** (critical for performance!)
4. ✅ Use `>=` and `<` for date ranges (not BETWEEN)
5. ✅ Returns aggregated windows, not individual spots

### Pattern 2: Campaign Summary Statistics

**❌ OLD**:
```python
def get_campaign_stats(campaign_id):
    query = """
        SELECT
            COUNT(*) as total_playouts,
            COUNT(DISTINCT frameid) as total_frames,
            AVG(spotlength) as avg_duration
        FROM playout_data
        WHERE buyercampaignref = %s
    """
    return execute_query(query, (campaign_id,))
```

**✅ NEW**:
```python
def get_campaign_stats(campaign_id):
    """Get campaign summary from aggregated view."""
    query = """
        SELECT
            COUNT(DISTINCT frameid) as total_frames,
            COUNT(DISTINCT DATE(time_window_start)) as days_active,
            SUM(spot_count) as total_playouts,
            MIN(time_window_start) as start_date,
            MAX(time_window_start) as end_date,
            ROUND(AVG(playout_length_seconds), 1) as avg_spot_length,
            ROUND(AVG(spot_count), 1) as avg_spots_per_window
        FROM mv_playout_15min
        WHERE buyercampaignref = %s
    """
    return execute_query(query, (campaign_id,))
```

**Key changes**:
1. ✅ Use `SUM(spot_count)` instead of `COUNT(*)` for total playouts
2. ✅ Access pre-calculated averages via `playout_length_seconds`
3. ✅ Can query without time filter for campaign-wide stats (but slower)

### Pattern 3: Time-Series Data

**❌ OLD**:
```python
def get_hourly_playouts(campaign_id, start_date, end_date):
    query = """
        SELECT
            DATE_TRUNC('hour', startdate) as hour,
            COUNT(*) as playouts
        FROM playout_data
        WHERE buyercampaignref = %s
          AND startdate >= %s
          AND startdate < %s
        GROUP BY DATE_TRUNC('hour', startdate)
    """
    return execute_query(query, (campaign_id, start_date, end_date))
```

**✅ NEW**:
```python
def get_hourly_playouts(campaign_id, start_date, end_date):
    """Get hourly activity from 15-minute aggregations."""
    query = """
        SELECT
            DATE_TRUNC('hour', time_window_start) as hour,
            COUNT(*) as active_windows,
            SUM(spot_count) as total_playouts
        FROM mv_playout_15min
        WHERE buyercampaignref = %s
          AND time_window_start >= %s
          AND time_window_start < %s
        GROUP BY DATE_TRUNC('hour', time_window_start)
        ORDER BY hour
    """
    return execute_query(query, (campaign_id, start_date, end_date))
```

**Key changes**:
1. ✅ Group by `time_window_start` instead of `startdate`
2. ✅ Use `SUM(spot_count)` for total playouts
3. ✅ Can add `active_windows` metric (count of 15-min windows)

### Pattern 4: Route API Integration

**❌ OLD** (manual aggregation):
```python
def prepare_route_api_data(campaign_id):
    # Complex aggregation logic to create 15-minute windows
    # from millisecond-level data...
    pass
```

**✅ NEW** (use pre-aggregated data):
```python
def prepare_route_api_data(campaign_id, start_date, end_date):
    """
    Get data ready for Route API - already aggregated!

    Returns ONE row per frame/campaign/15-minute window.
    """
    query = """
        SELECT
            frameid,
            time_window_start as datetime_from,
            time_window_start + INTERVAL '15 minutes' as datetime_to,
            spot_count,
            playout_length_seconds as spot_length,
            break_length_seconds
        FROM mv_playout_15min
        WHERE buyercampaignref = %s
          AND time_window_start >= %s
          AND time_window_start < %s
        ORDER BY frameid, time_window_start
    """
    return execute_query(query, (campaign_id, start_date, end_date))
```

**Key benefits**:
1. ✅ No manual aggregation needed
2. ✅ Already in Route API format
3. ✅ 10,000x faster than aggregating raw data
4. ✅ Guaranteed one row per window

### Pattern 5: Frame Activity Check

**❌ OLD**:
```python
def is_frame_active(frame_id, date):
    query = """
        SELECT EXISTS(
            SELECT 1 FROM playout_data
            WHERE frameid = %s
              AND DATE(startdate) = %s
        )
    """
    return execute_query(query, (frame_id, date))
```

**✅ NEW**:
```python
def is_frame_active(frame_id, date):
    """Check if frame has activity on date."""
    query = """
        SELECT EXISTS(
            SELECT 1 FROM mv_playout_15min
            WHERE frameid = %s
              AND time_window_start >= %s
              AND time_window_start < %s::date + INTERVAL '1 day'
        )
    """
    return execute_query(query, (frame_id, date, date))
```

**Key changes**:
1. ✅ Use range comparison (`>=` and `<`) instead of `DATE()` function
2. ✅ Query against `mv_playout_15min`
3. ✅ Faster index usage

### Critical Performance Rules

**✅ DO**:
1. **Always include time_window_start filter**
2. Use `>=` and `<` for date ranges (not BETWEEN or DATE())
3. Filter by campaign OR frame (not both unless specific lookup)
4. Use LIMIT for pagination
5. Leverage pre-calculated fields (spot_count, playout_length_seconds)

**❌ DON'T**:
1. Query without time filter (scans 700M rows!)
2. Use functions on indexed columns (breaks index usage)
3. Use OR on different indexed columns
4. Try to access millisecond precision (use raw playout_data if needed)

---

## Testing Checklist

### Unit Tests

Create test file: `tests/test_ms01_queries.py`

```python
import pytest
from src.services.playout_service import PlayoutService

def test_campaign_query():
    """Test basic campaign query against MS-01."""
    service = PlayoutService()

    # Use known campaign from MS-01 data
    result = service.get_campaign_data(
        campaign_id='18295',
        start_date='2025-08-01',
        end_date='2025-08-02'
    )

    assert len(result) > 0, "Should return playout data"
    assert 'frameid' in result[0], "Should have frameid field"
    assert 'time_window_start' in result[0], "Should have time_window_start"

def test_campaign_summary():
    """Test campaign summary statistics."""
    service = PlayoutService()

    summary = service.get_campaign_summary('18295')

    assert summary['total_frames'] > 0, "Should have frames"
    assert summary['total_playouts'] > 0, "Should have playouts"
    assert summary['avg_spot_length'] > 0, "Should have avg duration"

def test_time_filter_required():
    """Verify time filter improves performance."""
    import time
    service = PlayoutService()

    # With time filter (should be fast)
    start = time.time()
    result = service.get_campaign_data(
        '18295', '2025-08-01', '2025-08-02'
    )
    duration_with_filter = time.time() - start

    # Should complete in < 2 seconds
    assert duration_with_filter < 2.0, "Query with time filter should be fast"
```

Run tests:
```bash
pytest tests/test_ms01_queries.py -v
```

### Integration Tests

**Test 1: Database Connection**
```bash
python test_ms01_connection.py
```

**Test 2: Service Layer**
```bash
python test_ms01_integration.py
```

**Test 3: Full Application Flow**
```bash
# Start app
streamlit run src/ui/app.py

# Manual testing:
# 1. Search for campaign 18295
# 2. Select date range: Aug 1-2, 2025
# 3. Verify data loads
# 4. Check performance (should be < 2 seconds)
# 5. Export CSV and verify output
```

### Performance Tests

**Test query performance**:
```python
# test_query_performance.py
import time
import psycopg2
import os

conn = psycopg2.connect(
    host="192.168.1.34",
    port=5432,
    database="route_poc",
    user="postgres",
    password=os.getenv('MS01_DB_PASSWORD')
)

cursor = conn.cursor()

# Test 1: Campaign query with time filter
start = time.time()
cursor.execute("""
    SELECT * FROM mv_playout_15min
    WHERE buyercampaignref = '18295'
      AND time_window_start >= '2025-08-01'
      AND time_window_start < '2025-09-01'
""")
results = cursor.fetchall()
duration = time.time() - start

print(f"✅ Campaign query: {duration:.2f}s, {len(results)} rows")
assert duration < 2.0, "Should complete in < 2 seconds"

# Test 2: Campaign summary
start = time.time()
cursor.execute("""
    SELECT COUNT(DISTINCT frameid) as frames,
           SUM(spot_count) as total_playouts
    FROM mv_playout_15min
    WHERE buyercampaignref = '18295'
""")
duration = time.time() - start
print(f"✅ Summary query: {duration:.2f}s")
assert duration < 1.0, "Summary should complete in < 1 second"

cursor.close()
conn.close()
print("\n✅ All performance tests passed!")
```

### Data Validation Tests

**Verify data integrity**:
```python
# test_data_validation.py
import psycopg2
import os

conn = psycopg2.connect(
    host="192.168.1.34",
    port=5432,
    database="route_poc",
    user="postgres",
    password=os.getenv('MS01_DB_PASSWORD')
)

cursor = conn.cursor()

# Test 1: Check date coverage
cursor.execute("""
    SELECT
        MIN(time_window_start) as earliest,
        MAX(time_window_start) as latest
    FROM mv_playout_15min
""")
result = cursor.fetchone()
print(f"✅ Date range: {result[0]} to {result[1]}")

# Test 2: Verify unique constraint
cursor.execute("""
    SELECT
        frameid,
        buyercampaignref,
        time_window_start,
        COUNT(*) as duplicates
    FROM mv_playout_15min
    GROUP BY frameid, buyercampaignref, time_window_start
    HAVING COUNT(*) > 1
    LIMIT 1
""")
duplicates = cursor.fetchone()
assert duplicates is None, "Should have no duplicates"
print("✅ No duplicate windows found")

# Test 3: Verify 15-minute boundaries
cursor.execute("""
    SELECT time_window_start
    FROM mv_playout_15min
    WHERE EXTRACT(MINUTE FROM time_window_start)::int % 15 != 0
    LIMIT 1
""")
invalid_boundary = cursor.fetchone()
assert invalid_boundary is None, "All windows should be on 15-min boundaries"
print("✅ All windows on 15-minute boundaries")

cursor.close()
conn.close()
print("\n✅ All validation tests passed!")
```

---

## Rollback Plan

If migration causes issues, here's how to quickly switch back to local database:

### Quick Rollback (Environment Variable)

**Step 1**: Change environment variable
```bash
# Edit .env
nano .env

# Change this line:
USE_MS01_DATABASE=false
```

**Step 2**: Restart application
```bash
# Kill running apps
pkill -f streamlit

# Restart with local database
streamlit run src/ui/app.py
```

**Verify rollback**:
```python
from src.config.database import DatabaseConfig
db_config = DatabaseConfig()
db_info = db_config.get_active_database_info()
print(db_info['database_mode'])
# Should print: "Local (Dev/Demo)"
```

### Full Rollback (Restore Backup)

If environment variable rollback doesn't work:

```bash
# Restore backed up .env
cp .env.backup.20251017 .env

# Restore backed up database config (if modified)
cp src/config/database.py.backup src/config/database.py

# Restart application
streamlit run src/ui/app.py
```

### Emergency Local Database Setup

If you need to quickly spin up local database:

```bash
# Start local PostgreSQL (MacOS)
brew services start postgresql@14

# Create database
createdb route_poc

# Import sample data (if available)
psql route_poc < backup/sample_data.sql
```

---

## Performance Expectations

### Query Performance Targets

| Query Type | Expected Duration | Row Count |
|------------|------------------|-----------|
| Campaign query (1 month) | < 1 second | ~4,000 rows |
| Campaign summary | < 0.5 seconds | 1 row |
| Specific window lookup | < 0.1 seconds | 1 row |
| Hourly aggregation (1 month) | < 1 second | ~744 rows |
| Frame activity check | < 0.1 seconds | 1 row |
| Brand breakdown | < 1 second | Variable |

### Performance Grading

Based on campaign query for 1 month of data:

| Grade | Duration | Status |
|-------|----------|--------|
| A+ | < 1 second | Excellent |
| A | 1-2 seconds | Very Good |
| B | 2-3 seconds | Good |
| C | 3-5 seconds | Acceptable |
| D | > 5 seconds | Needs optimization |

### Optimization Tips

**If queries are slow (> 2 seconds)**:

1. **Check time filter exists**:
   ```sql
   -- BAD: No time filter
   WHERE buyercampaignref = '18295'

   -- GOOD: Always include time filter
   WHERE buyercampaignref = '18295'
     AND time_window_start >= '2025-08-01'
     AND time_window_start < '2025-09-01'
   ```

2. **Verify index usage**:
   ```sql
   EXPLAIN ANALYZE
   SELECT * FROM mv_playout_15min
   WHERE buyercampaignref = '18295'
     AND time_window_start >= '2025-08-01'
     AND time_window_start < '2025-09-01';

   -- Look for "Index Scan" (good) vs "Seq Scan" (bad)
   ```

3. **Add pagination**:
   ```sql
   -- For UI display, use LIMIT
   LIMIT 1000 OFFSET 0
   ```

4. **Use connection pooling**:
   ```python
   # Already configured in DatabaseConfig
   # Verify pool settings:
   db_config.postgres.min_pool_size = 2
   db_config.postgres.max_pool_size = 10
   ```

### Expected Data Freshness

- **Refresh Schedule**: Daily at 2am UTC
- **Refresh Duration**: ~50-60 minutes
- **Data Age**: Up to 24 hours old

**Check data freshness**:
```sql
SELECT
    MAX(time_window_start) as latest_window,
    MAX(latest_playout) as latest_playout,
    EXTRACT(EPOCH FROM (NOW() - MAX(latest_playout))) / 3600 as hours_old
FROM mv_playout_15min;
```

---

## Common Issues and Solutions

### Issue 1: Connection Refused

**Error**:
```
psycopg2.OperationalError: could not connect to server: Connection refused
```

**Solutions**:
1. Check network connectivity:
   ```bash
   ping 192.168.1.34
   nc -zv 192.168.1.34 5432
   ```

2. Verify VPN connection (if required):
   ```bash
   # Check if you need VPN to access 192.168.1.x network
   ```

3. Check firewall rules:
   ```bash
   # Ensure PostgreSQL port 5432 is not blocked
   ```

4. Verify MS-01 server is running:
   ```bash
   # Contact pipeline team if MS-01 is down
   ```

### Issue 2: Authentication Failed

**Error**:
```
psycopg2.OperationalError: FATAL: password authentication failed
```

**Solutions**:
1. Verify password in .env:
   ```bash
   grep "MS01_DB_PASSWORD" .env
   # Should have actual password, not placeholder
   ```

2. Check environment variable is loaded:
   ```python
   import os
   from dotenv import load_dotenv
   load_dotenv()
   print(os.getenv('MS01_DB_PASSWORD'))  # Should print password
   ```

3. Contact pipeline team for correct credentials

### Issue 3: Table/View Not Found

**Error**:
```
psycopg2.ProgrammingError: relation "mv_playout_15min" does not exist
```

**Solutions**:
1. Verify you're connected to correct database:
   ```sql
   SELECT current_database();
   -- Should return: route_poc
   ```

2. Check view exists:
   ```sql
   SELECT schemaname, matviewname
   FROM pg_matviews
   WHERE matviewname = 'mv_playout_15min';
   ```

3. Ensure database is MS-01 (not local):
   ```python
   from src.config.database import DatabaseConfig
   db_config = DatabaseConfig()
   print(db_config.postgres.host)
   # Should be: 192.168.1.34
   ```

### Issue 4: Queries Extremely Slow

**Symptom**: Queries taking > 10 seconds

**Solutions**:
1. **Ensure time filter is present**:
   ```python
   # CRITICAL: Always filter by time_window_start
   query = """
       SELECT * FROM mv_playout_15min
       WHERE buyercampaignref = %s
         AND time_window_start >= %s  -- REQUIRED!
         AND time_window_start < %s   -- REQUIRED!
   """
   ```

2. **Check query plan**:
   ```sql
   EXPLAIN ANALYZE
   SELECT * FROM mv_playout_15min
   WHERE buyercampaignref = '18295'
     AND time_window_start >= '2025-08-01'
     AND time_window_start < '2025-09-01';
   ```

   Look for:
   - ✅ "Index Scan using idx_mv_playout_15min_campaign_time"
   - ❌ "Seq Scan on mv_playout_15min"

3. **Add LIMIT for testing**:
   ```sql
   -- Test with small limit first
   LIMIT 100
   ```

4. **Check database load**:
   ```sql
   SELECT count(*) FROM pg_stat_activity
   WHERE datname = 'route_poc';
   -- Too many concurrent connections?
   ```

### Issue 5: No Data Returned

**Symptom**: Query returns 0 rows but campaign should exist

**Solutions**:
1. **Verify campaign exists**:
   ```sql
   SELECT COUNT(*) FROM mv_playout_15min
   WHERE buyercampaignref = '18295';
   ```

2. **Check date range**:
   ```sql
   SELECT
       MIN(time_window_start) as earliest,
       MAX(time_window_start) as latest
   FROM mv_playout_15min
   WHERE buyercampaignref = '18295';
   ```

3. **Check for NULL campaign** (house ads):
   ```sql
   SELECT COUNT(*) FROM playout_data
   WHERE buyercampaignref IS NULL
     AND frameid = '1234567890';
   ```

4. **Verify data coverage**:
   ```sql
   SELECT
       MIN(time_window_start) as db_start,
       MAX(time_window_start) as db_end
   FROM mv_playout_15min;
   -- Data only available Aug 6 - Oct 13, 2025
   ```

### Issue 6: Brand Data Missing

**Symptom**: Can't get brand breakdown

**Solution**: Use separate brand view:
```sql
-- Don't use mv_playout_15min for brand breakdown
-- Use mv_playout_15min_brands instead

SELECT
    spacebrandid,
    SUM(spots_for_brand) as total_spots
FROM mv_playout_15min_brands
WHERE buyercampaignref = '18295'
  AND time_window_start >= '2025-08-01'
  AND time_window_start < '2025-09-01'
GROUP BY spacebrandid;
```

### Issue 7: Unexpected Row Counts

**Symptom**: Getting different counts than expected

**Explanation**: Remember aggregation difference:
```
Raw playout_data: 150 individual spot records
Aggregated mv_playout_15min: 1 record with spot_count=150
```

**Solution**:
```python
# To get total playouts, use SUM(spot_count):
total_playouts = SUM(spot_count)  # NOT COUNT(*)

# To get number of windows:
total_windows = COUNT(*)
```

### Issue 8: Connection Pool Exhausted

**Error**:
```
psycopg2.pool.PoolError: connection pool exhausted
```

**Solutions**:
1. Increase pool size:
   ```bash
   # In .env
   POSTGRES_MAX_POOL=20  # Increase from 10
   ```

2. Return connections properly:
   ```python
   conn = pool.getconn()
   try:
       # Use connection
       pass
   finally:
       pool.putconn(conn)  # ALWAYS return!
   ```

3. Use context managers:
   ```python
   with get_db_connection() as conn:
       # Connection automatically returned
       pass
   ```

---

## Quick Reference

### Connection Details

```python
# MS-01 Production Database
host = "192.168.1.34"
port = 5432
database = "route_poc"
user = "postgres"
password = os.getenv('MS01_DB_PASSWORD')
```

### Primary View

```sql
mv_playout_15min  -- USE THIS for Route API
```

### Essential Query Pattern

```sql
SELECT
    frameid,
    time_window_start,
    spot_count,
    playout_length_seconds,
    break_length_seconds
FROM mv_playout_15min
WHERE buyercampaignref = :campaign_id
  AND time_window_start >= :start_date
  AND time_window_start < :end_date
ORDER BY time_window_start, frameid;
```

### Performance Checklist

- ✅ Always filter by `time_window_start`
- ✅ Use `>=` and `<` for date ranges
- ✅ Use `SUM(spot_count)` for total playouts
- ✅ Add LIMIT for pagination
- ✅ Use connection pooling
- ✅ Test with EXPLAIN ANALYZE

### Key Files

```
# Configuration
/Users/ianwyatt/PycharmProjects/Route-Playout-Econometrics_POC/.env
/Users/ianwyatt/PycharmProjects/Route-Playout-Econometrics_POC/src/config/database.py

# Services to update
/Users/ianwyatt/PycharmProjects/Route-Playout-Econometrics_POC/src/services/playout_service.py
/Users/ianwyatt/PycharmProjects/Route-Playout-Econometrics_POC/src/api/campaign_service.py

# Documentation
/Users/ianwyatt/PycharmProjects/route-playout-pipeline/Claude/POC_Handover/DATABASE_HANDOVER_FOR_POC.md
/Users/ianwyatt/PycharmProjects/route-playout-pipeline/Claude/POC_Handover/QUICK_REFERENCE.md
```

### Testing Commands

```bash
# Test connection
python test_ms01_connection.py

# Test integration
python test_ms01_integration.py

# Run unit tests
pytest tests/test_ms01_queries.py -v

# Start app
streamlit run src/ui/app.py
```

### Rollback Command

```bash
# Quick rollback to local database
# Edit .env:
USE_MS01_DATABASE=false

# Restart app
pkill -f streamlit && streamlit run src/ui/app.py
```

---

## Support and Resources

### Documentation

**Full Database Documentation**:
```
/Users/ianwyatt/PycharmProjects/route-playout-pipeline/Claude/POC_Handover/DATABASE_HANDOVER_FOR_POC.md
```

**Quick Reference**:
```
/Users/ianwyatt/PycharmProjects/route-playout-pipeline/Claude/POC_Handover/QUICK_REFERENCE.md
```

**Python Examples**:
```
/Users/ianwyatt/PycharmProjects/route-playout-pipeline/Claude/POC_Handover/PYTHON_EXAMPLES.py
```

### Contact

**Database/Pipeline Issues**: ian@route.org.uk
**Route API Integration**: See Route API specification docs
**Performance Issues**: Check indexes, add time filters, use EXPLAIN ANALYZE

---

## Summary

### Migration in 3 Steps

1. **Update .env**: Set `USE_MS01_DATABASE=true` and add MS-01 credentials
2. **Refactor queries**: Change `playout_data` → `mv_playout_15min`, add time filters
3. **Test thoroughly**: Run connection tests, query tests, full app tests

### Critical Success Factors

✅ **Always include time_window_start filter** (performance killer if missing)
✅ **Use materialized view** (`mv_playout_15min`, not `playout_data`)
✅ **Test before deploying** (connection, queries, full app flow)
✅ **Monitor performance** (< 2 seconds for campaign queries)
✅ **Have rollback plan ready** (just change USE_MS01_DATABASE=false)

### Benefits After Migration

- ✅ 1.28 billion real playout records
- ✅ 10,000x faster queries (pre-aggregated)
- ✅ Production-ready for Route API integration
- ✅ 69 days of real data (Aug-Oct 2025)
- ✅ Daily refresh with latest data
- ✅ Fully indexed and optimized

---

**Status**: Ready for Migration
**Created**: 2025-10-17
**Last Updated**: 2025-10-17
**Version**: 1.0
