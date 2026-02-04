# Route API Caching - Troubleshooting Guide

**Purpose**: Solutions to common problems encountered when caching Route audience data

---

## Table of Contents

1. [Timeout Errors](#timeout-errors)
2. [Authentication Failures](#authentication-failures)
3. [Database Connection Issues](#database-connection-issues)
4. [Data Quality Problems](#data-quality-problems)
5. [Performance Issues](#performance-issues)
6. [Route API Errors](#route-api-errors)
7. [Cache Inconsistencies](#cache-inconsistencies)

---

## Timeout Errors

### Problem 1: Read Timeout After 30 Seconds

**Error Message**:
```
requests.exceptions.ReadTimeout: HTTPSConnectionPool(host='route.mediatelapi.co.uk',
port=443): Read timed out. (read timeout=30)
```

**Cause**: Campaign is too large (200+ frames, 2M+ playouts). Route API needs 60-180 seconds for complex calculations.

**Solution 1: Increase Timeout**
```python
# Change from default 30s to 120s
response = requests.post(
    url,
    json=payload,
    headers=headers,
    timeout=120  # Increase timeout
)
```

**Solution 2: Detect Large Campaigns and Skip**
```python
def is_large_campaign(campaign_id, date):
    """Check if campaign is too large for API."""
    query = """
        SELECT SUM(spot_count) as total_playouts
        FROM mv_playout_15min
        WHERE buyercampaignref = %s AND time_window_start::date = %s
    """
    # Execute query
    return total_playouts > 500000  # 500k+ playouts = large

# In main loop
if is_large_campaign(campaign_id, date):
    print(f"⚠️ Skipping large campaign {campaign_id}")
    continue
```

**Solution 3: Split Large Campaigns**
```python
def split_campaign_by_time_windows(campaign_id, date):
    """Split large campaign into 4-hour chunks."""
    time_ranges = [
        ("00:00", "04:00"),
        ("04:00", "08:00"),
        ("08:00", "12:00"),
        ("12:00", "16:00"),
        ("16:00", "20:00"),
        ("20:00", "23:59")
    ]

    for start, end in time_ranges:
        # Call API for each 4-hour window
        cache_time_range(campaign_id, date, start, end)
```

### Problem 2: Connection Timeout

**Error Message**:
```
requests.exceptions.ConnectTimeout: Connection timed out
```

**Cause**: Network issue or Route API server unreachable

**Solution**:
```python
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Add retry with exponential backoff
retry_strategy = Retry(
    total=3,
    backoff_factor=2,  # Wait 2s, 4s, 8s
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["POST"]
)

adapter = HTTPAdapter(max_retries=retry_strategy)
session = requests.Session()
session.mount("https://", adapter)

# Use session instead of requests
response = session.post(url, json=payload, headers=headers, timeout=120)
```

---

## Authentication Failures

### Problem 3: 401 Unauthorized

**Error Message**:
```json
{"status": "error", "message": "Unauthorized", "code": 401}
```

**Cause**: Missing or invalid API credentials

**Solution 1: Verify Environment Variables**
```bash
# Check .env file exists
ls -la .env

# Verify contents (don't commit this output!)
cat .env | grep ROUTE_API
```

**Solution 2: Test Credentials**
```python
import os
from dotenv import load_dotenv

load_dotenv()

# Print first/last 4 chars to verify without exposing
api_key = os.getenv('ROUTE_API_KEY')
auth = os.getenv('ROUTE_API_AUTH')

print(f"API Key: {api_key[:4]}...{api_key[-4:]}")
print(f"Auth: {auth[:4]}...{auth[-4:]}")
```

**Solution 3: Test Simple API Call**
```python
# Test version endpoint (simpler than playout)
response = requests.post(
    "https://route.mediatelapi.co.uk/rest/version",
    headers={
        'Authorization': os.getenv('ROUTE_API_AUTH'),
        'API-Key': os.getenv('ROUTE_API_KEY')
    }
)
print(response.status_code)  # Should be 200
print(response.json())  # Should return available releases
```

### Problem 4: 403 Forbidden

**Error Message**:
```json
{"status": "error", "message": "Forbidden", "code": 403}
```

**Cause**: API key doesn't have access to playout endpoint

**Solution**: Contact Route support to verify API key permissions
- Ensure key has "playout" endpoint access
- Check if key is active and not expired
- Verify rate limits are not exceeded

---

## Database Connection Issues

### Problem 5: Connection Refused

**Error Message**:
```
psycopg2.OperationalError: could not connect to server: Connection refused
```

**Cause**: PostgreSQL server not running or wrong host/port

**Solution 1: Verify Database is Running**
```bash
# On database server
systemctl status postgresql

# Or
pg_isready -h localhost -p 5432
```

**Solution 2: Check Firewall**
```bash
# Allow PostgreSQL port
sudo ufw allow 5432/tcp

# Or test connection
telnet your_host_here 5432
```

**Solution 3: Verify Connection String**
```python
import psycopg2

try:
    conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=int(os.getenv('POSTGRES_PORT', '5432')),
        database=os.getenv('POSTGRES_DATABASE'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD')
    )
    print("✅ Connection successful")
    conn.close()
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

### Problem 6: Too Many Connections

**Error Message**:
```
psycopg2.OperationalError: FATAL: sorry, too many clients already
```

**Cause**: Exceeded PostgreSQL max_connections

**Solution 1: Use Connection Pooling**
```python
from psycopg2 import pool

# Create pool once
db_pool = pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10,  # Limit concurrent connections
    host=os.getenv('POSTGRES_HOST'),
    database=os.getenv('POSTGRES_DATABASE'),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD')
)

# Get connection
conn = db_pool.getconn()
try:
    # Use connection
    pass
finally:
    # Always return to pool
    db_pool.putconn(conn)
```

**Solution 2: Close Connections Properly**
```python
# Always use context managers
def query_database():
    conn = psycopg2.connect(...)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT ...")
        results = cursor.fetchall()
        return results
    finally:
        conn.close()  # Always close!
```

### Problem 7: Role Does Not Exist

**Error Message**:
```
psycopg2.OperationalError: FATAL: role "postgres" does not exist
```

**Cause**: Wrong username for database

**Solution**:
```bash
# Check .env file
# Secondary uses 'ianwyatt'
# Primary uses 'postgres'

# .env should have:
POSTGRES_USER_LOCAL=ianwyatt
POSTGRES_USER_PRIMARY=postgres
```

---

## Data Quality Problems

### Problem 8: Zero Impacts for All Frames

**Observation**: All frames return `impacts: 0`

**Cause 1**: Frames not in Route release

**Solution**: Verify release mapping
```python
# Check if date falls within release period
# Q3 2025 (R56): Sep 29, 2025 - Jan 4, 2026

from datetime import datetime

date = datetime.strptime("2025-10-11", "%Y-%m-%d")
if date >= datetime(2025, 9, 29) and date <= datetime(2026, 1, 4):
    route_release = "56"
else:
    # Find correct release
    route_release = get_release_for_date(date)
```

**Cause 2**: Invalid frame IDs

**Solution**: Verify frames exist in Route
```python
def verify_frames_in_route(frames):
    """Check if frames are valid Route frame IDs."""
    # Frame IDs are typically 10 digits
    valid_frames = [f for f in frames if 1000000000 <= f <= 9999999999]
    invalid_frames = [f for f in frames if f not in valid_frames]

    if invalid_frames:
        print(f"⚠️ Invalid frames: {invalid_frames}")

    return valid_frames
```

### Problem 9: Duplicate Cache Entries

**Observation**: Multiple rows for same campaign-date

**Cause**: Primary key not enforced

**Solution**: Verify table structure
```sql
-- Check constraints
SELECT conname, contype
FROM pg_constraint
WHERE conrelid = 'cache_campaign_reach_day'::regclass;

-- Should have primary key on (campaign_id, date)
-- If missing, add it:
ALTER TABLE cache_campaign_reach_day
ADD PRIMARY KEY (campaign_id, date);
```

### Problem 10: Stale Cache Data

**Observation**: Cache showing old data

**Cause**: Cache not refreshed after new playouts

**Solution**: Implement cache invalidation
```sql
-- Delete cache older than 7 days
DELETE FROM cache_campaign_reach_day
WHERE cached_at < NOW() - INTERVAL '7 days';

-- Re-cache affected campaigns
-- (run backfill script)
```

---

## Performance Issues

### Problem 11: Slow Queries

**Observation**: Database queries taking 10+ seconds

**Cause**: Missing indexes

**Solution**: Add indexes
```sql
-- Check existing indexes
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename = 'cache_campaign_reach_day';

-- Add missing indexes
CREATE INDEX IF NOT EXISTS idx_cache_campaign_day
ON cache_campaign_reach_day(campaign_id, date);

CREATE INDEX IF NOT EXISTS idx_cache_date
ON cache_campaign_reach_day(date);

CREATE INDEX IF NOT EXISTS idx_cache_updated
ON cache_campaign_reach_day(cached_at);

-- Analyze table
ANALYZE cache_campaign_reach_day;
```

### Problem 12: High Memory Usage

**Observation**: Script using 2GB+ memory

**Cause**: Loading too much data into memory

**Solution**: Use generators and batching
```python
# Bad: Load all campaigns into memory
campaigns = list(get_all_campaigns())  # 1000 campaigns × 100KB each = 100MB

# Good: Process in batches
def process_campaigns_in_batches(batch_size=50):
    offset = 0
    while True:
        batch = get_campaigns_batch(offset, batch_size)
        if not batch:
            break

        for campaign in batch:
            cache_campaign(campaign['id'], campaign['date'])

        offset += batch_size
```

### Problem 13: Slow API Responses

**Observation**: All API calls taking 60+ seconds

**Cause**: Sending too many frames per request

**Solution**: Batch frames
```python
def batch_frames(frames, max_per_batch=500):
    """Split frames into batches of max_per_batch."""
    for i in range(0, len(frames), max_per_batch):
        yield frames[i:i + max_per_batch]

# Process large campaign in batches
all_frames = get_campaign_frames(campaign_id, date)

if len(all_frames) > 500:
    print(f"Large campaign: {len(all_frames)} frames - splitting into batches")
    for batch in batch_frames(all_frames, 500):
        # Call API for each batch
        cache_frame_batch(campaign_id, date, batch)
else:
    # Single API call
    cache_campaign(campaign_id, date)
```

---

## Route API Errors

### Problem 14: Invalid Route Release ID

**Error Message**:
```json
{"status": "error", "message": "Invalid route_release_id", "code": 400}
```

**Cause**: Using release number outside available window (last 5 releases only)

**Solution**: Query available releases first
```python
def get_available_releases():
    """Get list of available Route releases."""
    response = requests.post(
        "https://route.mediatelapi.co.uk/rest/version",
        headers={
            'Authorization': os.getenv('ROUTE_API_AUTH'),
            'API-Key': os.getenv('ROUTE_API_KEY')
        }
    )
    data = response.json()
    return [r['release_id'] for r in data.get('releases', [])]

# Check before using
available = get_available_releases()
if "56" not in available:
    print(f"⚠️ Release 56 not available. Use: {available}")
```

### Problem 15: Invalid Demographics

**Error Message**:
```json
{"status": "error", "message": "Invalid demographic filter"}
```

**Cause**: Malformed demographic string

**Solution**: Use correct format
```python
# Valid demographics:
demographics = [
    "ageband>=1",          # All ages
    "ageband=15-34",       # Age 15-34
    "social_grade=ABC1",   # ABC1 social grade
    "gender=male"          # Male only
]

# Invalid:
demographics = ["age>=15"]  # Wrong - should be "ageband=15-34"
```

### Problem 16: Request Too Large

**Error Message**:
```json
{"status": "error", "message": "Request payload too large"}
```

**Cause**: Too many frames or time windows in single request

**Solution**: Split request
```python
MAX_FRAMES = 500
MAX_WINDOWS = 96  # 1 day in 15-min windows

if len(frames) > MAX_FRAMES:
    # Split frames
    for batch in batch_frames(frames, MAX_FRAMES):
        cache_batch(campaign_id, date, batch)

if len(schedule) > MAX_WINDOWS:
    # Split time windows (e.g., by 6-hour blocks)
    for time_block in split_schedule(schedule, 24):  # 6 hours = 24 windows
        cache_time_block(campaign_id, time_block)
```

---

## Cache Inconsistencies

### Problem 17: Missing Campaign Days

**Observation**: Campaign has playouts but no cache

**Cause**: Caching script failed or skipped

**Solution**: Find and re-cache missing days
```sql
-- Find campaigns with missing cache
SELECT DISTINCT
    p.buyercampaignref,
    DATE(p.time_window_start) as playout_date
FROM mv_playout_15min p
LEFT JOIN cache_campaign_reach_day c
    ON p.buyercampaignref = c.campaign_id
    AND DATE(p.time_window_start) = c.date
WHERE p.buyercampaignref IS NOT NULL
    AND c.campaign_id IS NULL
ORDER BY playout_date DESC;

-- Re-cache missing entries
-- (run backfill script for these campaigns)
```

### Problem 18: Negative Metrics

**Observation**: `reach` or `grp` showing negative values

**Cause**: Calculation error or bad API response

**Solution**: Validate before caching
```python
def validate_metrics(reach, grp, frequency, impacts):
    """Ensure metrics are valid before caching."""
    issues = []

    if reach < 0:
        issues.append(f"Negative reach: {reach}")
    if grp < 0:
        issues.append(f"Negative GRP: {grp}")
    if frequency < 0:
        issues.append(f"Negative frequency: {frequency}")
    if impacts < 0:
        issues.append(f"Negative impacts: {impacts}")

    if issues:
        print(f"❌ Invalid metrics: {', '.join(issues)}")
        return False

    return True

# In caching function
if not validate_metrics(reach, grp, frequency, impacts):
    print(f"⚠️ Skipping cache due to invalid metrics")
    return False
```

---

## Diagnostic Commands

### Check System Status

```bash
# Database connection
pg_isready -h your_host_here -p 5432

# API endpoint
curl -X POST https://route.mediatelapi.co.uk/rest/version \
  -H "Authorization: ${ROUTE_API_AUTH}" \
  -H "API-Key: ${ROUTE_API_KEY}"

# Cache table size
psql -h your_host_here -U postgres -d route_poc -c \
  "SELECT pg_size_pretty(pg_total_relation_size('cache_campaign_reach_day'))"
```

### Cache Health Check

```sql
-- Overall cache status
SELECT
    COUNT(DISTINCT campaign_id) as campaigns_cached,
    COUNT(*) as total_entries,
    MIN(date) as earliest_date,
    MAX(date) as latest_date,
    MAX(cached_at) as last_update,
    AGE(NOW(), MAX(cached_at)) as time_since_update
FROM cache_campaign_reach_day;

-- Campaigns with issues
SELECT
    campaign_id,
    COUNT(*) as days_cached,
    AVG(reach) as avg_reach,
    AVG(grp) as avg_grp,
    AVG(frequency) as avg_frequency
FROM cache_campaign_reach_day
GROUP BY campaign_id
HAVING AVG(reach) < 0 OR AVG(grp) < 0 OR AVG(frequency) < 0;
```

### Script Debugging

```python
import logging

# Enable debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Log everything
logger.debug(f"Payload: {payload}")
logger.debug(f"Response: {response.text}")
logger.debug(f"Metrics: reach={reach}, grp={grp}, freq={frequency}")
```

---

## Getting Help

If problems persist after trying these solutions:

1. **Check Logs**: Review script output and database logs
2. **Query Database**: Use diagnostic SQL queries
3. **Test Manually**: Try a single campaign-day manually
4. **Documentation**: Re-read [ROUTE_API_CACHING_GUIDE.md](./ROUTE_API_CACHING_GUIDE.md)
5. **Contact Team**: Reach out to POC team with:
   - Error message
   - Campaign ID and date
   - Steps to reproduce
   - Relevant logs

---

**Last Updated**: October 22, 2025
**Version**: 1.0
