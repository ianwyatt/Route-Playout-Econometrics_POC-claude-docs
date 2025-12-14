# MS-01 Database Handover for Playout-Econometrics-POC

**Date**: 2025-10-17
**Purpose**: Comprehensive database structure documentation for POC application development
**Database**: MS-01 PostgreSQL (192.168.1.34:5432)
**Database Name**: route_poc
**Status**: ✅ PRODUCTION READY

---

## 🎯 Executive Summary

This document provides everything the POC application team needs to query the MS-01 production database containing **1.28 billion playout records** spanning August-October 2025.

**What you get:**
- Pre-aggregated 15-minute windows for Route API integration (~700M rows)
- Raw playout data with millisecond precision (1.28B rows)
- Brand-level tracking for multi-brand campaigns
- Route release metadata for audience calculations
- Fully indexed and production-tested

**Key takeaway**: Use `mv_playout_15min` for Route API calls. It's fast, indexed, and returns exactly what Route expects.

---

## 📋 Table of Contents

1. [Database Connection](#database-connection)
2. [Database Structure Overview](#database-structure-overview)
3. [Core Tables](#core-tables)
4. [Materialized Views for Route API](#materialized-views-for-route-api)
5. [Brand Split Architecture](#brand-split-architecture)
6. [Route Release Integration](#route-release-integration)
7. [Query Patterns & Examples](#query-patterns--examples)
8. [Performance Guidelines](#performance-guidelines)
9. [Data Refresh Schedule](#data-refresh-schedule)
10. [Troubleshooting](#troubleshooting)
11. [Quick Reference](#quick-reference)

---

## Database Connection

### Connection Details

```python
# MS-01 Production Database
DB_HOST = "192.168.1.34"
DB_PORT = 5432
DB_DATABASE = "route_poc"
DB_USER = "postgres"
# DB_PASSWORD: Contact pipeline team for credentials
```

### Python Connection Example

```python
import psycopg2
from psycopg2.extras import RealDictCursor

def get_db_connection():
    """Connect to MS-01 PostgreSQL database."""
    return psycopg2.connect(
        host="192.168.1.34",
        port=5432,
        database="route_poc",
        user="postgres",
        password=os.getenv('MS01_DB_PASSWORD'),
        cursor_factory=RealDictCursor  # Returns dicts instead of tuples
    )

# Usage
conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT * FROM mv_playout_15min LIMIT 5")
results = cursor.fetchall()
cursor.close()
conn.close()
```

### Connection Pooling (Recommended)

```python
from psycopg2 import pool

# Create connection pool (do this once at app startup)
connection_pool = psycopg2.pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    host="192.168.1.34",
    port=5432,
    database="route_poc",
    user="postgres",
    password=os.getenv('MS01_DB_PASSWORD')
)

# Get connection from pool
conn = connection_pool.getconn()
# ... use connection ...
connection_pool.putconn(conn)  # Return to pool
```

---

## Database Structure Overview

### Database Size & Scale

| Component | Count | Size |
|-----------|-------|------|
| **Total Database** | - | ~596 GB |
| **Playout Records** | 1,282,183,391 | 561 GB |
| **15-Min Aggregations** | ~700,000,000 | 200-250 GB |
| **Brand Associations** | ~750,000,000 | 110 GB |
| **Date Range** | 69 days | Aug 6 - Oct 13, 2025 |

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MS-01 DATABASE (route_poc)               │
└─────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
          ▼                   ▼                   ▼
    ┌──────────┐      ┌──────────────┐    ┌─────────────┐
    │  RAW     │      │ MATERIALIZED │    │   METADATA  │
    │  DATA    │      │    VIEWS     │    │   TABLES    │
    └──────────┘      └──────────────┘    └─────────────┘
         │                    │                   │
         │                    │                   │
    playout_data      mv_playout_15min    route_releases
    (1.28B rows)      (700M rows)        (8 releases)
         │                    │
         │            mv_playout_15min_brands
         │            (750M rows)
         │
    playout_imports
    playout_dates
```

### What Each Layer Does

**Raw Data Layer:**
- `playout_data`: Every individual ad play with millisecond precision
- `playout_imports`: Import tracking and deduplication
- `playout_dates`: Daily aggregation for quick date queries

**Aggregated Layer (USE THIS FOR POC):**
- `mv_playout_15min`: Pre-aggregated 15-minute windows for Route API
- `mv_playout_15min_brands`: Brand-level tracking for multi-brand campaigns

**Metadata Layer:**
- `route_releases`: Route API release metadata (R54-R61)
- Maps trading periods to Route release numbers

---

## Core Tables

### 1. playout_data (1.28 Billion Rows)

**Purpose**: Raw playout event records from Redshift exports

**When to use**:
- ❌ **DON'T use for Route API** (too slow, wrong format)
- ✅ Use for millisecond-precision analysis
- ✅ Use for debugging specific playout events

**Schema**:
```sql
CREATE TABLE playout_data (
    -- Primary identifier
    id                    INTEGER PRIMARY KEY,

    -- Frame and timing
    frameid               BIGINT,
    startdate             TIMESTAMP,          -- Playout start (ms precision)
    enddate               TIMESTAMP,          -- Playout end
    spotlength            INTEGER,            -- Duration in milliseconds
    shareoftime           DOUBLE PRECISION,

    -- Campaign & creative
    buyercampaignref      VARCHAR(255),       -- Campaign ID (can be NULL)
    creativeid            VARCHAR(255),
    creativename          VARCHAR(255),

    -- SPACE entity IDs
    spacemediaownerid     INTEGER,            -- Media owner
    spacebuyerid          INTEGER,            -- Buyer organization
    spaceagencyid         INTEGER,            -- Agency
    spacebrandid          INTEGER,            -- Brand

    -- Import metadata
    import_timestamp      TIMESTAMP,
    import_file           VARCHAR(255),
    import_session_id     VARCHAR(20)
);
```

**Key Fields Explained**:
- `frameid`: Digital OOH frame identifier (references SPACE frames)
- `startdate`, `enddate`: Exact playout timing (e.g., 2025-08-01 12:34:56.123)
- `spotlength`: Duration in **milliseconds** (10000 = 10 seconds)
- `buyercampaignref`: Campaign ID - **can be NULL** for house ads (~5-10% of records)
- `spacemediaownerid`: Media owner (Clear Channel, JCDecaux, etc.)
- `spacebrandid`: Advertiser brand

**Indexes**:
```sql
-- Primary key
playout_data_pkey (id)

-- Unique constraint (prevents duplicates)
playout_data_unique_key (frameid, startdate, enddate, buyercampaignref)

-- Query indexes
idx_playout_frameid (frameid)
idx_playout_campaign (buyercampaignref)
idx_playout_dates (startdate, enddate)
```

**Sample Row**:
```json
{
  "id": 584122635,
  "frameid": 1234567890,
  "startdate": "2025-09-01 12:34:56.789",
  "enddate": "2025-09-01 12:35:06.789",
  "spotlength": 10000,
  "buyercampaignref": "18295",
  "spacemediaownerid": 3,
  "spaceagencyid": 156,
  "spacebrandid": 21143,
  "import_file": "playout_202509011200-000.csv"
}
```

**Data Quality Notes**:
1. **NULL campaigns**: ~5-10% have NULL `buyercampaignref` (house ads, test content)
2. **Midnight transitions**: Filter out 23:58-00:02 periods (test data)
3. **Spot length variations**: Same campaign may use multiple durations
4. **Duplicates prevented**: Unique constraint enforced

---

### 2. playout_imports (915 Rows)

**Purpose**: Track CSV file imports with deduplication

**When to use**:
- Check import status and file coverage
- Debug missing date ranges
- Verify data freshness

**Schema**:
```sql
CREATE TABLE playout_imports (
    id               INTEGER PRIMARY KEY,
    filename         VARCHAR(255) UNIQUE,
    file_hash        VARCHAR(64),           -- SHA-256 hash
    records_imported INTEGER,
    import_timestamp TIMESTAMP,
    status           VARCHAR(50)            -- 'completed', 'failed'
);
```

**Sample Query**:
```sql
-- Check recent imports
SELECT filename, records_imported, import_timestamp
FROM playout_imports
WHERE status = 'completed'
ORDER BY import_timestamp DESC
LIMIT 10;
```

---

### 3. playout_dates (35 Rows)

**Purpose**: Daily summary table for fast date-based queries

**When to use**:
- Quick "how many records on date X" queries
- Date range validation
- Dashboard summary statistics

**Schema**:
```sql
CREATE TABLE playout_dates (
    date         DATE PRIMARY KEY,
    record_count BIGINT
);
```

**Sample Query**:
```sql
-- Get daily volume for a month
SELECT date, record_count,
       ROUND(record_count::numeric / 1000000, 2) as millions
FROM playout_dates
WHERE date >= '2025-08-01' AND date < '2025-09-01'
ORDER BY date;
```

---

### 4. route_releases (8 Rows)

**Purpose**: Map Route release numbers to trading periods

**When to use**:
- Determine which Route release to use for a given playout date
- JOIN with playout data to get release metadata

**Schema**:
```sql
CREATE TABLE route_releases (
    id                   INTEGER PRIMARY KEY,
    name                 VARCHAR(100),          -- "Q1 2025"
    release_number       VARCHAR(20) UNIQUE,    -- "R54"
    data_publication     DATE,
    trading_period_start DATE,
    trading_period_end   DATE
);
```

**All Route Releases**:
| release_number | name | trading_period_start | trading_period_end |
|----------------|------|----------------------|--------------------|
| R54 | Q1 2025 | 2025-04-07 | 2025-06-29 |
| R55 | Q2 2025 | 2025-06-30 | 2025-09-28 |
| R56 | Q3 2025 | 2025-09-29 | 2026-01-04 |
| R57 | Q4 2025 | 2026-01-05 | 2026-03-29 |
| R58 | Q1 2026 | 2026-03-30 | 2026-06-28 |
| R59 | Q2 2026 | 2026-06-29 | 2026-09-27 |
| R60 | Q3 2026 | 2026-09-28 | 2027-01-03 |
| R61 | Q4 2026 | 2027-01-04 | 2027-04-04 |

**Find Route Release for a Date**:
```sql
SELECT release_number, name
FROM route_releases
WHERE '2025-09-15'::date BETWEEN trading_period_start AND trading_period_end;
-- Returns: R55, Q2 2025
```

---

## Materialized Views for Route API

### ⭐ mv_playout_15min (PRIMARY VIEW FOR POC)

**Purpose**: Pre-aggregated 15-minute playout windows ready for Route API calls

**Why use this**:
- ✅ **10,000x faster** than aggregating raw data
- ✅ **Route API compatible** format (one row per frame/campaign/window)
- ✅ **Properly indexed** for fast queries
- ✅ **Production tested** across all spot length patterns

**Row Count**: ~700 million rows
**Size**: ~200-250 GB (data + indexes)
**Refresh**: Daily (non-blocking concurrent refresh)

#### Schema

```sql
CREATE MATERIALIZED VIEW mv_playout_15min AS
SELECT
    -- Identifiers
    frameid                     VARCHAR(50),      -- Frame ID
    buyercampaignref            VARCHAR(50),      -- Campaign ID
    time_window_start           TIMESTAMP,        -- 15-min boundary (:00, :15, :30, :45)

    -- SPACE metadata (representative values)
    spacemediaownerid           VARCHAR(50),
    spacebuyerid                VARCHAR(50),
    spaceagencyid               VARCHAR(50),
    -- NOTE: spacebrandid NOT in this view (see mv_playout_15min_brands)

    -- Aggregated metrics
    spot_count                  INTEGER,          -- Number of playouts in window
    total_playout_ms            BIGINT,           -- Sum of all spot durations

    -- Route API required fields (rounded to whole seconds)
    playout_length_seconds      INTEGER,          -- Avg spot duration (rounded)
    break_length_seconds        INTEGER,          -- Avg gap duration (rounded)
    cycle_length_seconds        INTEGER,          -- 900 / spot_count

    -- Debugging/validation
    earliest_playout            TIMESTAMP,
    latest_playout              TIMESTAMP,
    avg_playout_seconds_unrounded NUMERIC(10,3)
...
```

#### Indexes

```sql
-- UNIQUE constraint (required for concurrent refresh)
idx_mv_playout_15min_pk
    UNIQUE(frameid, time_window_start, buyercampaignref)

-- Performance indexes
idx_mv_playout_15min_campaign_time
    (buyercampaignref, time_window_start)

idx_mv_playout_15min_frame_time
    (frameid, time_window_start)

idx_mv_playout_15min_time
    (time_window_start)

idx_mv_playout_15min_mediaowner
    (spacemediaownerid)
```

#### Key Constraint

**ONE row per (frameid, campaign, 15-minute window)**

This is guaranteed by the unique constraint and is exactly what Route API expects.

#### Aggregation Formula

```python
# For n playouts in a 900-second (15-minute) window:

spot_count = COUNT(*)
playout_length_seconds = ROUND(AVG(spotlength / 1000.0))
total_content_time = spot_count × playout_length_seconds
total_break_time = 900 - total_content_time
break_length_seconds = ROUND(total_break_time / spot_count)
cycle_length_seconds = ROUND(900 / spot_count)
```

#### Sample Row

```json
{
  "frameid": "1234567890",
  "buyercampaignref": "18295",
  "time_window_start": "2025-08-01 12:00:00",
  "spacemediaownerid": "3",
  "spot_count": 150,
  "playout_length_seconds": 6,
  "break_length_seconds": 0,
  "cycle_length_seconds": 6,
  "earliest_playout": "2025-08-01 12:00:05",
  "latest_playout": "2025-08-01 12:14:59"
}
```

**Interpretation**:
- 150 spots played in this 15-minute window
- Each spot averaged 6 seconds (rounded)
- No breaks between spots (continuous playback)
- Full cycle every 6 seconds

#### Example Query

```python
def get_route_api_data(campaign_id, start_date, end_date):
    """
    Fetch aggregated playout data for Route API calls.

    Returns ONE row per frame/campaign/15-minute window.
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

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, (campaign_id, start_date, end_date))
    results = cursor.fetchall()
    cursor.close()
    conn.close()

    return results

# Usage
route_data = get_route_api_data('18295', '2025-08-01', '2025-09-01')
# Returns: ~4,000 rows (31 days × 96 windows/day × avg 1-2 frames)

# Send to Route API
for record in route_data:
    response = route_api_call(
        frameid=record['frameid'],
        datetime_from=record['datetime_from'],
        datetime_to=record['datetime_to'],
        spot_count=record['spot_count'],
        playout_length=record['playout_length_seconds'],
        break_length=record['break_length_seconds']
    )
    # Store response with impacts
```

---

## Brand Split Architecture

### The Problem

Some campaigns have **brand changes within 15-minute windows**:

```
Frame: 1234859642
Campaign: 18699
Window: 2025-08-23 11:15:00

Row 1: spacebrandid = 21143, 15 spots (11:15:40 - 11:29:50)
Row 2: spacebrandid = 21146, 15 spots (11:15:30 - 11:29:40)
```

**Why this matters**:
- Route API needs ONE row per window (doesn't care about brands)
- Reporting needs brand-level breakdown
- Can't include `spacebrandid` in GROUP BY of main view (would create duplicates)

### The Solution: Two-Table Architecture

#### Table 1: mv_playout_15min (Route API)
- **Purpose**: Route API aggregation
- **Keys**: (frameid, campaign, time_window)
- **Excludes**: spacebrandid from GROUP BY
- **Guarantee**: ONE row per window

#### Table 2: mv_playout_15min_brands (Brand Tracking)
- **Purpose**: Brand-level reporting
- **Keys**: (frameid, campaign, time_window, **spacebrandid**)
- **Allows**: Multiple rows per window (one per brand)
- **Tracks**: Spot counts per brand

### mv_playout_15min_brands Schema

```sql
CREATE MATERIALIZED VIEW mv_playout_15min_brands AS
SELECT
    frameid,
    buyercampaignref,
    time_window_start,          -- 15-min boundary
    spacebrandid,               -- Brand ID

    spots_for_brand INTEGER,            -- Spots for this brand
    earliest_playout_brand TIMESTAMP,   -- First playout for brand
    latest_playout_brand TIMESTAMP      -- Last playout for brand
...
```

### Using Both Tables Together

#### Pattern 1: Get Route API Data (Main View Only)

```python
# Just use mv_playout_15min
route_data = execute_query("""
    SELECT frameid, time_window_start, spot_count,
           playout_length_seconds, break_length_seconds
    FROM mv_playout_15min
    WHERE buyercampaignref = %s
      AND time_window_start >= %s
      AND time_window_start < %s
""", (campaign_id, start_date, end_date))
```

#### Pattern 2: Split Route Audience by Brand

```python
def split_audience_by_brand(frame_id, campaign_id, window_start, total_impacts):
    """
    Split Route API audience impacts proportionally by brand.

    Args:
        frame_id: Frame identifier
        campaign_id: Campaign reference
        window_start: 15-minute window timestamp
        total_impacts: Total impacts from Route API for this window

    Returns:
        List of dicts with brand_id and proportional impacts
    """
    query = """
        SELECT
            spacebrandid,
            spots_for_brand,
            spots_for_brand::FLOAT / SUM(spots_for_brand) OVER () as brand_proportion
        FROM mv_playout_15min_brands
        WHERE frameid = %s
          AND buyercampaignref = %s
          AND time_window_start = %s
    """

    brands = execute_query(query, (frame_id, campaign_id, window_start))

    return [{
        'brand_id': brand['spacebrandid'],
        'spots': brand['spots_for_brand'],
        'proportion': brand['brand_proportion'],
        'impacts': total_impacts * brand['brand_proportion']
    } for brand in brands]

# Example usage:
route_response = {
    'frameid': '1234859642',
    'campaign': '18699',
    'window': '2025-08-23 11:15:00',
    'impacts': 10000  # From Route API
}

brand_split = split_audience_by_brand(
    route_response['frameid'],
    route_response['campaign'],
    route_response['window'],
    route_response['impacts']
)

# Result:
# [
#   {'brand_id': '21143', 'spots': 15, 'proportion': 0.5, 'impacts': 5000},
#   {'brand_id': '21146', 'spots': 15, 'proportion': 0.5, 'impacts': 5000}
# ]
```

#### Pattern 3: Campaign Summary by Brand

```sql
-- Break down campaign performance by brand
SELECT
    b.spacebrandid,
    COUNT(DISTINCT b.frameid) as unique_frames,
    COUNT(DISTINCT b.time_window_start) as active_windows,
    SUM(b.spots_for_brand) as total_spots
FROM mv_playout_15min_brands b
WHERE b.buyercampaignref = '18295'
  AND b.time_window_start >= '2025-08-01'
  AND b.time_window_start < '2025-09-01'
GROUP BY b.spacebrandid
ORDER BY total_spots DESC;
```

---

## Route Release Integration

### Determining Route Release for Playout Dates

Route API requires the correct Route release number for each playout event. The `route_releases` table maps dates to releases.

```python
def get_route_release_for_date(playout_date):
    """
    Determine which Route release to use for a given date.

    Args:
        playout_date: Date of playout (string or datetime)

    Returns:
        Dict with release_number and name
    """
    query = """
        SELECT release_number, name
        FROM route_releases
        WHERE %s::date BETWEEN trading_period_start AND trading_period_end
    """

    result = execute_query(query, (playout_date,))

    if result:
        return {
            'release_number': result[0]['release_number'],
            'release_name': result[0]['name']
        }
    else:
        raise ValueError(f"No Route release found for date {playout_date}")

# Example
release = get_route_release_for_date('2025-09-15')
# Returns: {'release_number': 'R55', 'release_name': 'Q2 2025'}
```

### JOIN Playout Data with Route Releases

```sql
-- Get playout data with Route release metadata
SELECT
    pd.frameid,
    pd.buyercampaignref,
    pd.time_window_start,
    pd.spot_count,
    rr.release_number,
    rr.name as release_name
FROM mv_playout_15min pd
JOIN route_releases rr
    ON pd.time_window_start::date
        BETWEEN rr.trading_period_start AND rr.trading_period_end
WHERE pd.buyercampaignref = '18295'
  AND pd.time_window_start >= '2025-08-01'
  AND pd.time_window_start < '2025-09-01'
LIMIT 100;
```

---

## Query Patterns & Examples

### Pattern 1: Campaign Data for Route API ⭐ MOST COMMON

```python
def get_campaign_for_route_api(campaign_id, start_date, end_date):
    """
    Get ALL playout data for Route API call.
    Returns ONE row per frame/campaign/15-minute window.
    """
    query = """
        SELECT
            frameid,
            time_window_start as datetime_from,
            time_window_start + INTERVAL '15 minutes' as datetime_to,
            spot_count,
            playout_length_seconds as playout_length,
            break_length_seconds as break_length
        FROM mv_playout_15min
        WHERE buyercampaignref = %s
          AND time_window_start >= %s
          AND time_window_start < %s
        ORDER BY frameid, time_window_start
    """

    return execute_query(query, (campaign_id, start_date, end_date))

# Usage
route_data = get_campaign_for_route_api('18295', '2025-08-01', '2025-09-01')
```

### Pattern 2: Campaign Summary Statistics

```python
def get_campaign_summary(campaign_id):
    """Get high-level campaign stats for dashboard."""
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

# Example result:
# {
#   'total_frames': 145,
#   'days_active': 31,
#   'total_playouts': 125000,
#   'start_date': '2025-08-01 06:00:00',
#   'end_date': '2025-08-31 23:45:00',
#   'avg_spot_length': 10.2,
#   'avg_spots_per_window': 44.9
# }
```

### Pattern 3: Frame Timeline (Hourly Aggregation)

```python
def get_hourly_activity(campaign_id, start_date, end_date):
    """Get hourly totals for time-series chart."""
    query = """
        SELECT
            DATE_TRUNC('hour', time_window_start) as hour,
            COUNT(*) as active_windows,
            SUM(spot_count) as total_spots
        FROM mv_playout_15min
        WHERE buyercampaignref = %s
          AND time_window_start >= %s
          AND time_window_start < %s
        GROUP BY DATE_TRUNC('hour', time_window_start)
        ORDER BY hour
    """

    return execute_query(query, (campaign_id, start_date, end_date))

# Use for: Time-series charts, day-parting analysis
```

### Pattern 4: Check Frame Activity

```python
def is_frame_active(frame_id, date):
    """Check if a frame has any playout data on a given date."""
    query = """
        SELECT EXISTS(
            SELECT 1 FROM mv_playout_15min
            WHERE frameid = %s
              AND time_window_start >= %s
              AND time_window_start < %s + INTERVAL '1 day'
        )
    """

    result = execute_query(query, (frame_id, date, date))
    return result[0][0]
```

### Pattern 5: Multi-Campaign Comparison

```sql
-- Compare multiple campaigns side-by-side
SELECT
    buyercampaignref,
    COUNT(DISTINCT frameid) as frames,
    SUM(spot_count) as total_spots,
    ROUND(AVG(playout_length_seconds), 1) as avg_spot_sec,
    MIN(time_window_start) as start_date,
    MAX(time_window_start) as end_date
FROM mv_playout_15min
WHERE buyercampaignref IN ('18295', '18098', '17827')
  AND time_window_start >= '2025-08-01'
  AND time_window_start < '2025-09-01'
GROUP BY buyercampaignref
ORDER BY total_spots DESC;
```

---

## Performance Guidelines

### ✅ Fast Query Patterns (USE THESE)

#### 1. Filter by Campaign + Time Range
```sql
WHERE buyercampaignref = '18295'
  AND time_window_start >= '2025-08-01'
  AND time_window_start < '2025-09-01'
-- Uses: idx_mv_playout_15min_campaign_time (composite index)
```

#### 2. Filter by Frame + Time Range
```sql
WHERE frameid = '1234567890'
  AND time_window_start >= '2025-08-01'
  AND time_window_start < '2025-09-01'
-- Uses: idx_mv_playout_15min_frame_time (composite index)
```

#### 3. Specific Window Lookup
```sql
WHERE frameid = '1234567890'
  AND buyercampaignref = '18295'
  AND time_window_start = '2025-08-01 12:00:00'
-- Uses: idx_mv_playout_15min_pk (unique index, SUPER FAST)
```

### ❌ Slow Query Patterns (AVOID THESE)

#### 1. No Time Filter
```sql
-- BAD: Scans entire view (700M rows!)
WHERE buyercampaignref = '18295'

-- GOOD: Add time filter
WHERE buyercampaignref = '18295'
  AND time_window_start >= '2025-08-01'
  AND time_window_start < '2025-09-01'
```

#### 2. Function on Indexed Column
```sql
-- BAD: Can't use index
WHERE DATE(time_window_start) = '2025-08-01'

-- GOOD: Use range comparison
WHERE time_window_start >= '2025-08-01'
  AND time_window_start < '2025-08-02'
```

#### 3. OR Conditions on Different Columns
```sql
-- BAD: Can't use composite indexes
WHERE buyercampaignref = '18295' OR frameid = '1234567890'

-- GOOD: Split into two queries or use UNION
SELECT * FROM mv_playout_15min WHERE buyercampaignref = '18295'
UNION
SELECT * FROM mv_playout_15min WHERE frameid = '1234567890'
```

### Performance Checklist

- ✅ **Always include time_window_start filter**
- ✅ Use `>=` and `<` for date ranges (not BETWEEN or DATE())
- ✅ Filter by campaign OR frame (not both unless specific lookup)
- ✅ Use LIMIT for UI pagination
- ✅ Consider caching frequent queries
- ✅ Use connection pooling
- ✅ Test queries with EXPLAIN ANALYZE before deploying

### Query Performance Testing

```python
# Check if query is using indexes
def explain_query(query, params):
    """Show query execution plan."""
    explain_query = f"EXPLAIN ANALYZE {query}"
    result = execute_query(explain_query, params)
    print(result)

# Look for:
# ✅ "Index Scan" (good)
# ❌ "Seq Scan" (bad - full table scan)
```

---

## Data Refresh Schedule

### Materialized View Refresh

**Schedule**: Daily at 2am UTC (after playout data import completes)

**Method**: Concurrent refresh (non-blocking)
```sql
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_playout_15min;
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_playout_15min_brands;
```

**Duration**:
- Main view: ~25-30 minutes
- Brand view: ~20-25 minutes
- Total: ~50-60 minutes (run in parallel)

### Data Freshness

**Eventually Consistent**: The materialized views are refreshed daily, so:
- Data may be up to 24 hours old
- For real-time needs, query `playout_data` directly (slower)

**Check Last Refresh**:
```sql
SELECT
    MAX(time_window_start) as latest_window,
    MAX(latest_playout) as latest_playout_timestamp
FROM mv_playout_15min;
```

If `latest_window` is > 1 day old, refresh is needed.

---

## Troubleshooting

### Problem: Query is Slow

**Check 1**: Is time filter present?
```sql
-- Add time filter
WHERE time_window_start >= '2025-08-01'
  AND time_window_start < '2025-09-01'
```

**Check 2**: Is query using indexes?
```sql
EXPLAIN ANALYZE
SELECT * FROM mv_playout_15min WHERE ...;

-- Look for "Index Scan" (good) vs "Seq Scan" (bad)
```

**Check 3**: Too many rows returned?
```sql
-- Add LIMIT for pagination
LIMIT 1000 OFFSET 0
```

### Problem: No Data Returned

**Check 1**: Verify campaign exists
```sql
SELECT COUNT(*) FROM mv_playout_15min
WHERE buyercampaignref = '18295';
```

**Check 2**: Check date range
```sql
SELECT
    MIN(time_window_start) as earliest,
    MAX(time_window_start) as latest
FROM mv_playout_15min
WHERE buyercampaignref = '18295';
```

**Check 3**: Campaign may have NULL campaign ref
```sql
-- Check for house ads
SELECT COUNT(*) FROM playout_data
WHERE buyercampaignref IS NULL
  AND frameid = '1234567890';
```

### Problem: Unexpected Row Counts

**Check 1**: Remember 15-minute aggregation
- Raw data: 150 rows for 150 individual spots
- Aggregated: 1 row with spot_count=150

**Check 2**: Verify against source
```sql
-- Compare with raw data
SELECT
    COUNT(*) as raw_count,
    COUNT(DISTINCT (frameid, buyercampaignref,
        date_trunc('hour', startdate) +
        INTERVAL '15 minutes' * floor(extract(minute from startdate) / 15)
    )) as expected_aggregated_count
FROM playout_data
WHERE buyercampaignref = '18295';
```

---

## Quick Reference

### Connection String
```
postgresql://postgres:${POSTGRES_PASSWORD_MS01}@192.168.1.34:5432/route_poc
```

**Note**: Replace `${POSTGRES_PASSWORD_MS01}` with your actual password from `.env` file

### Primary View for POC
```sql
mv_playout_15min
```

### Key Fields for Route API
```python
{
    'frameid': str,
    'time_window_start': datetime,  # 15-min boundary
    'spot_count': int,
    'playout_length_seconds': int,
    'break_length_seconds': int
}
```

### Most Common Query Pattern
```sql
SELECT frameid, time_window_start, spot_count,
       playout_length_seconds, break_length_seconds
FROM mv_playout_15min
WHERE buyercampaignref = :campaign_id
  AND time_window_start >= :start_date
  AND time_window_start < :end_date
ORDER BY time_window_start, frameid;
```

### Route Release Lookup
```sql
SELECT release_number FROM route_releases
WHERE :playout_date BETWEEN trading_period_start AND trading_period_end;
```

### Performance Rules
1. Always filter by time_window_start
2. Use >= and < for date ranges
3. Use connection pooling
4. Test with EXPLAIN ANALYZE
5. Add LIMIT for large result sets

---

## Additional Resources

### Documentation Files

In the pipeline repository (`route-playout-pipeline`):

**Core Playout Data:**
- **Full Schema**: `Claude/Documentation/ms01_database_schema.md`
- **15-Min Aggregation**: `Claude/Documentation/15min_aggregation_implementation_20251015.md`
- **Brand Architecture**: `Claude/Documentation/brand_split_architecture_20251015.md`
- **Usage Guide**: `Claude/Documentation/mv_playout_15min_usage_guide.md`
- **Route API Spec**: `docs/Converting Variable Digital Out-of-Home Playout Data to Standardised Audience Metrics.md`

**⭐ Route API Cache System (NEW - 2025-10-24):**
- **Cache Architecture**: `Claude/POC_Handover/MULTI_LEVEL_CACHE_USAGE_GUIDE.md`
- **Cache Limitations**: `Claude/POC_Handover/CAMPAIGN_CACHE_LIMITATIONS_GUIDE.md`
- **Backfill System**: `Claude/POC_Handover/CAMPAIGN_FULL_BACKFILL_PRODUCTION_READY.md`
- **⚠️ BREAKING CHANGE**: `Claude/POC_Handover/POC_TEAM_SUMMARY_BUYER_ID_CHANGES.md` - buyer_id composite keys added

### SQL Scripts (if needed)

- **Create Views**: `sql/create_mv_playout_15min.sql`
- **Refresh Views**: `sql/refresh_mv_playout_15min.sql`

### Support

**For questions contact**:
- **Database issues**: Pipeline team (ian@route.org.uk)
- **Route API integration**: See Route API specification docs
- **Performance issues**: Check indexes, add time filters, use EXPLAIN ANALYZE

---

## Summary for POC Development

### What You Need to Know

1. **Database**: MS-01 @ 192.168.1.34:5432, database `route_poc`
2. **Primary View**: `mv_playout_15min` (~700M rows, refreshed daily)
3. **Key Fields**: frameid, time_window_start, spot_count, playout_length_seconds, break_length_seconds
4. **Always Filter**: Include `time_window_start` range in WHERE clause
5. **Route Releases**: JOIN with `route_releases` to get release_number
6. **Brand Tracking**: Use `mv_playout_15min_brands` to split audience by brand

### Typical Workflow

1. User selects campaign and date range in POC UI
2. Query `mv_playout_15min` for aggregated playout data
3. Determine Route release from `route_releases` table
4. Call Route API with aggregated data
5. Get audience response (impacts per window)
6. Optionally split impacts by brand using `mv_playout_15min_brands`
7. Display/store results

### Performance Expectations

- Campaign queries (1 month): **< 1 second**
- Campaign summary stats: **< 0.5 seconds**
- Specific window lookup: **< 0.1 seconds**
- Data freshness: **Up to 24 hours old** (refreshed daily)

---

**Status**: ✅ PRODUCTION READY

**Created**: 2025-10-17
**Last Updated**: 2025-10-24 (Added cache system documentation references)
**For**: Playout-Econometrics-POC Development Team
**By**: Route Playout Pipeline Team

**Ready to integrate into POC application!** 🚀
