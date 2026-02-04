# Route API Caching Guide for Pipeline Teams

**Version:** 1.1
**Last Updated:** October 26, 2025
**Audience:** Pipeline developers, data engineers

---

## Table of Contents

1. [Overview](#overview)
2. [Route API Playout Endpoint](#route-api-playout-endpoint)
   - [Custom Demographics and Questionnaire Endpoint](#custom-demographics-and-questionnaire-endpoint)
3. [Database Schema](#database-schema)
4. [Implementation Guide](#implementation-guide)
5. [Error Handling](#error-handling)
6. [Performance Optimization](#performance-optimization)
7. [Monitoring and Maintenance](#monitoring-and-maintenance)

---

## Overview

This guide provides comprehensive documentation for caching Route API audience data to PostgreSQL for the Route Playout Econometrics POC.

### Purpose

- **Reduce API calls**: Cache frequently accessed audience data
- **Improve performance**: Instant retrieval from database vs 30-120s API calls
- **Cost efficiency**: Minimize API usage charges
- **Data availability**: Historical data beyond Route's 5-release window

### Data Flow

```
Playout Records (mv_playout_15min)
    ↓
Route API Playout Endpoint
    ↓
Cache Tables (cache_campaign_reach_day)
    ↓
POC Application (Streamlit UI)
```

---

## Route API Custom Endpoint

### Endpoint Details

**URL**: `https://route.mediatelapi.co.uk/rest/process/custom`
**Method**: `POST`
**Content-Type**: `application/json`
**Authentication**: HTTP Basic Auth + X-Api-Key Header

⚠️ **IMPORTANT**: Use the **custom** endpoint, not the playout endpoint. The custom endpoint supports multiple demographics and advanced filtering.

### Authentication

**Dual authentication required:**
1. HTTP Basic Authentication (username + password)
2. X-Api-Key header

Store credentials in `.env` file (never commit to git):

```bash
ROUTE_API_User_Name=your_username
ROUTE_API_Password=your_password
ROUTE_API_KEY=your_api_key_here
ROUTE_API_LIVE_CUSTOM_URL=https://route.mediatelapi.co.uk/rest/process/custom
```

Python usage:

```python
import os
import requests
from dotenv import load_dotenv

load_dotenv()

url = os.getenv('ROUTE_API_LIVE_CUSTOM_URL')
auth = (
    os.getenv('ROUTE_API_User_Name'),
    os.getenv('ROUTE_API_Password')
)
headers = {
    'Content-Type': 'application/json',
    'X-Api-Key': os.getenv('ROUTE_API_KEY')
}

response = requests.post(url, json=payload, headers=headers, auth=auth, timeout=300)
```

### Request Format

#### Minimal Request (RECOMMENDED for Caching)

**For fastest processing and efficient caching, use this minimal payload:**

```json
{
  "route_release_id": 56,
  "route_algorithm_version": "10.2",
  "demographics": [
    {
      "demographic_custom": "ageband>0"
    }
  ],
  "algorithm_figures": ["impacts"],
  "campaign": [{
    "schedule": [{
      "datetime_from": "2025-10-11 00:00",
      "datetime_until": "2025-10-11 23:45"
    }],
    "spot_length": 10,
    "spot_break_length": 50,
    "frames": [1234567890, 2345678901, 3456789012]
  }],
  "target_month": 1
}
```

**Why this is optimal:**
- ✅ **Impacts only**: Fastest processing (only returns audience data)
- ✅ **No grouping**: ~2x faster for campaign-level caching
- ✅ **Minimal demographics**: Simple "all adults" filter
- ✅ **No unnecessary parameters**: Clean payload
- ✅ **Integer route_release_id**: Correct API format

#### Key Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `route_release_id` | **Integer** | Yes | Route release number (e.g., `56` for Q3 2025) - **must be int, not string** |
| `route_algorithm_version` | String | Yes | Algorithm version (always `"10.2"`) |
| `demographics` | Array of Objects | Yes | Demographic filters - **must be objects**: `[{"demographic_custom": "ageband>0"}]` |
| `algorithm_figures` | Array | Yes | Metrics to return: `["impacts"]` for fastest processing |
| `grouping` | String | **No** | **Omit for caching** (adds ~2x processing time). Only use for per-frame analysis |
| `option_split_reach` | Boolean | **No** | **Omit unless** you need pedestrian/vehicular split |
| `campaign.schedule` | Array | Yes | Time windows (15-minute intervals recommended) |
| `campaign.spot_length` | Integer | Yes | Average spot length in seconds |
| `campaign.spot_break_length` | Integer | Yes | Average break length in seconds |
| `campaign.frames` | Array | Yes | Frame IDs to query (max ~500 per request) |
| `target_month` | Integer | Yes | Always `1` for playout data |

#### Multiple Demographics (Optional)

If you need to segment by demographics (e.g., ABC1 vs C2DE), use multiple demographic objects:

```json
{
  "route_release_id": 56,
  "route_algorithm_version": "10.2",
  "demographics": [
    {
      "demographic_custom": "social_grade=1 or social_grade=2"
    },
    {
      "demographic_custom": "social_grade>=3"
    }
  ],
  "algorithm_figures": ["impacts"],
  "campaign": [...],
  "target_month": 1
}
```

**Note**: Each demographic creates a separate result set. More demographics = longer processing time.

### Response Format

#### Success Response

```json
{
  "status": "success",
  "data": {
    "frames": [
      {
        "frame_id": 1234567890,
        "impacts": 1234.56,
        "datetime_from": "2025-10-11 00:00:00",
        "datetime_until": "2025-10-11 00:15:00"
      },
      {
        "frame_id": 2345678901,
        "impacts": 2345.67,
        "datetime_from": "2025-10-11 00:00:00",
        "datetime_until": "2025-10-11 00:15:00"
      }
    ]
  }
}
```

#### Error Response

```json
{
  "status": "error",
  "message": "Invalid route_release_id",
  "code": 400
}
```

### Time Format Conversion

**Playout format**: `2025-10-11T00:00:09.922` (ISO 8601)
**Route API format**: `2025-10-11 00:00` (space-separated)

Python conversion:

```python
from datetime import datetime

# Playout timestamp to Route API format
playout_time = "2025-10-11T00:00:09.922"
dt = datetime.fromisoformat(playout_time)
route_time = dt.strftime("%Y-%m-%d %H:%M")
# Result: "2025-10-11 00:00"
```

### Route Release Mapping

Route releases are quarterly trading periods. **Only the last 5 releases are available via API.**

| Release | Number | Trading Period | Available Until |
|---------|--------|----------------|-----------------|
| Q3 2025 | R56 | Sep 29, 2025 - Jan 4, 2026 | ~Q3 2026 |
| Q2 2025 | R55 | Jun 30, 2025 - Sep 28, 2025 | ~Q2 2026 |
| Q1 2025 | R54 | Apr 7, 2025 - Jun 29, 2025 | ~Q1 2026 |
| Q4 2024 | R53 | Jan 5, 2025 - Mar 29, 2025 | ~Q4 2025 |
| Q3 2024 | R52 | Sep 30, 2024 - Jan 4, 2025 | ~Q3 2025 |

**Query available releases**:

```bash
curl -X POST https://route.mediatelapi.co.uk/rest/version \
  -H "Authorization: ${ROUTE_API_AUTH}" \
  -H "API-Key: ${ROUTE_API_KEY}"
```

### Custom Demographics and Questionnaire Endpoint

#### Questionnaire Variables Endpoint

**URL**: `https://route.mediatelapi.co.uk/rest/codebook/questionnaire`
**Method**: `POST`
**Purpose**: Retrieve available demographic variables for building custom audience targets

This endpoint returns all available questionnaire variables that can be used in the `demographics` parameter of the playout endpoint. Use this to discover what demographic filters are available beyond the basic age and gender options.

**📋 R56 Reference**: See **[R56_QUESTIONNAIRE_REFERENCE.md](./R56_QUESTIONNAIRE_REFERENCE.md)** for the complete R56 (Q3 2025) questionnaire response with all 792 available variables.

**Request Example**:

```bash
curl -X POST https://route.mediatelapi.co.uk/rest/codebook/questionnaire \
  -H "Authorization: ${ROUTE_API_AUTH}" \
  -H "API-Key: ${ROUTE_API_KEY}" \
  -H "Content-Type: application/json"
```

**Python Example**:

```python
import requests
import os
from dotenv import load_dotenv

load_dotenv()

def get_questionnaire_variables():
    """Get all available demographic variables from Route API."""
    url = f"{os.getenv('ROUTE_API_URL')}/rest/codebook/questionnaire"

    headers = {
        'Authorization': os.getenv('ROUTE_API_AUTH'),
        'Content-Type': 'application/json',
        'API-Key': os.getenv('ROUTE_API_KEY')
    }

    response = requests.post(url, headers=headers)
    response.raise_for_status()

    return response.json()

# Get available variables
variables = get_questionnaire_variables()

# Print variable categories
for category in variables.get('variables', []):
    print(f"Category: {category['name']}")
    print(f"  Variables: {', '.join([v['code'] for v in category['items']])}")
```

**Response Structure**:

The endpoint returns available demographic variables organized by category:

```json
{
  "variables": [
    {
      "name": "Age",
      "items": [
        {"code": "ageband", "description": "Age bands", "values": ["15-34", "35-54", "55+"]},
        {"code": "age", "description": "Specific age", "values": ["15", "16", "17", ...]}
      ]
    },
    {
      "name": "Demographics",
      "items": [
        {"code": "social_grade", "description": "Social grade", "values": ["ABC1", "C2DE"]},
        {"code": "gender", "description": "Gender", "values": ["male", "female"]},
        {"code": "working_status", "description": "Working status", "values": ["working", "not_working"]}
      ]
    },
    {
      "name": "Geography",
      "items": [
        {"code": "tv_region", "description": "TV region", "values": ["London", "Yorkshire", ...]},
        {"code": "conurbation", "description": "Conurbation", "values": ["Greater London", ...]}
      ]
    }
  ]
}
```

#### Building Custom Demographic Filters

Use questionnaire variables to create custom demographic filters for the playout endpoint:

**Basic Demographics**:

```python
# All ages (default)
demographics = ["ageband>=1"]

# Specific age band
demographics = ["ageband=15-34"]

# Multiple age bands
demographics = ["ageband=15-34", "ageband=35-54"]

# Social grade ABC1
demographics = ["social_grade=ABC1"]

# Male only
demographics = ["gender=male"]
```

**Complex Targeting**:

```python
# Young, working ABC1 males
demographics = [
    "ageband=15-34",
    "social_grade=ABC1",
    "gender=male",
    "working_status=working"
]

# Seniors in specific region
demographics = [
    "ageband=55+",
    "tv_region=London"
]

# Multiple demographic segments (OR logic)
demographics = [
    "ageband=15-34",
    "ageband=35-54"
]
```

**Usage in Playout Request**:

```python
def build_custom_demographic_request(frames, schedule, demographics):
    """Build Route API request with custom demographics."""
    payload = {
        "route_release_id": "56",
        "route_algorithm_version": "10.2",
        "algorithm_figures": ["impacts"],
        "grouping": "frame_ID",
        "demographics": demographics,  # Custom demographic filters
        "campaign": [{
            "schedule": schedule,
            "spot_length": 10,
            "spot_break_length": 50,
            "frames": frames
        }],
        "target_month": 1
    }
    return payload

# Example: Target working ABC1 adults 25-44
demographics = [
    "ageband=25-44",
    "social_grade=ABC1",
    "working_status=working"
]

payload = build_custom_demographic_request(
    frames=[1234567890, 2345678901],
    schedule=[{"datetime_from": "2025-10-11 00:00", "datetime_until": "2025-10-11 23:59"}],
    demographics=demographics
)

# Call API
response = call_route_api(payload)
```

#### Caching Custom Demographics

When caching data with custom demographics, store the demographic filter used:

```sql
-- Extended cache table for custom demographics
CREATE TABLE cache_campaign_reach_day_custom (
    campaign_id VARCHAR NOT NULL,
    date DATE NOT NULL,
    demographic_filter TEXT,              -- JSON array of demographics used
    reach NUMERIC,
    grp NUMERIC,
    frequency NUMERIC,
    total_impacts NUMERIC,
    frame_count INTEGER,
    route_release_id INTEGER,
    cached_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (campaign_id, date, demographic_filter)
);
```

**Caching Example**:

```python
import json

def cache_custom_demographic_data(campaign_id, date, demographics, api_response, route_release_id):
    """Cache campaign data with custom demographic filter."""

    # Store demographics as JSON string
    demographic_filter = json.dumps(demographics)

    query = """
        INSERT INTO cache_campaign_reach_day_custom (
            campaign_id, date, demographic_filter,
            reach, grp, frequency, total_impacts,
            frame_count, route_release_id
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (campaign_id, date, demographic_filter)
        DO UPDATE SET
            reach = EXCLUDED.reach,
            grp = EXCLUDED.grp,
            frequency = EXCLUDED.frequency,
            total_impacts = EXCLUDED.total_impacts,
            frame_count = EXCLUDED.frame_count,
            cached_at = CURRENT_TIMESTAMP
    """

    # Execute query
    # ...
```

#### Common Demographic Combinations

**Standard Demographics**:
- `["ageband>=1"]` - All ages (default)
- `["ageband=15-34"]` - Young adults
- `["ageband=35-54"]` - Middle-aged adults
- `["ageband=55+"]` - Seniors
- `["social_grade=ABC1"]` - ABC1 social grade
- `["social_grade=C2DE"]` - C2DE social grade

**Campaign-Specific Targets**:
- Young professionals: `["ageband=25-44", "social_grade=ABC1", "working_status=working"]`
- Families: `["ageband=35-54", "household_composition=with_children"]`
- Affluent seniors: `["ageband=55+", "social_grade=ABC1"]`
- Urban youth: `["ageband=15-34", "conurbation=Greater London"]`

**Important Notes**:
- Variables must match exactly as returned by questionnaire endpoint
- Multiple values for same variable use OR logic
- Different variables use AND logic
- Test demographic filters with small sample before full cache run
- Not all combinations may have sufficient sample size

---

## Database Schema

### Cache Tables

#### `cache_campaign_reach_day`

Primary table for daily campaign audience metrics.

```sql
CREATE TABLE cache_campaign_reach_day (
    campaign_id VARCHAR NOT NULL,           -- Campaign reference (buyercampaignref)
    date DATE NOT NULL,                     -- Specific day
    reach NUMERIC,                          -- Audience reached (000s)
    grp NUMERIC,                            -- Gross Rating Points
    frequency NUMERIC,                      -- Average frequency (views per person)
    total_impacts NUMERIC,                  -- Total impressions (000s)
    frame_count INTEGER,                    -- Number of frames used
    route_release_id INTEGER,               -- Route release number (e.g., 56)
    cached_at TIMESTAMP DEFAULT NOW(),     -- Cache timestamp
    PRIMARY KEY (campaign_id, date)
);

-- Index for fast lookups
CREATE INDEX idx_cache_campaign_day ON cache_campaign_reach_day(campaign_id, date);
CREATE INDEX idx_cache_date ON cache_campaign_reach_day(date);
CREATE INDEX idx_cache_updated ON cache_campaign_reach_day(cached_at);
```

#### `cache_route_impacts_15min`

Detailed 15-minute interval impacts for granular analysis.

```sql
CREATE TABLE cache_route_impacts_15min (
    frameid BIGINT NOT NULL,
    time_window_start TIMESTAMP NOT NULL,
    time_window_end TIMESTAMP NOT NULL,
    impacts NUMERIC,                        -- Route audience (000s)
    route_release_id INTEGER,
    cached_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (frameid, time_window_start)
);

CREATE INDEX idx_impacts_15min_frame ON cache_route_impacts_15min(frameid);
CREATE INDEX idx_impacts_15min_time ON cache_route_impacts_15min(time_window_start);
```

### SPACE API Cache Tables

Used for entity lookups (media owners, buyers, brands).

```sql
-- Media owners
CREATE TABLE cache_space_media_owners (
    spacemediaownerid INTEGER PRIMARY KEY,
    name VARCHAR,
    cached_at TIMESTAMP DEFAULT NOW()
);

-- Buyers
CREATE TABLE cache_space_buyers (
    spacebuyerid INTEGER PRIMARY KEY,
    name VARCHAR,
    cached_at TIMESTAMP DEFAULT NOW()
);

-- Brands
CREATE TABLE cache_space_brands (
    spacebrandid INTEGER PRIMARY KEY,
    name VARCHAR,
    cached_at TIMESTAMP DEFAULT NOW()
);

-- Agencies
CREATE TABLE cache_space_agencies (
    spaceagencyid INTEGER PRIMARY KEY,
    name VARCHAR,
    cached_at TIMESTAMP DEFAULT NOW()
);
```

---

## Implementation Guide

### Step 1: Query Playout Data

Get playouts from materialized view (fast, doesn't hit main 596GB table):

```python
import psycopg2
from psycopg2.extras import RealDictCursor

def get_campaign_playouts(campaign_id: str, date: str):
    """
    Get playout data for a campaign on a specific date.

    Args:
        campaign_id: Campaign reference (e.g., "15884")
        date: Date string (e.g., "2025-10-11")

    Returns:
        List of playout records
    """
    conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST'),
        database=os.getenv('POSTGRES_DATABASE'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD')
    )

    query = """
        SELECT
            frameid,
            time_window_start,
            time_window_start + INTERVAL '15 minutes' as time_window_end,
            spot_count,
            playout_length_seconds,
            break_length_seconds
        FROM mv_playout_15min
        WHERE TRIM(buyercampaignref) = %s
            AND time_window_start::date = %s
        ORDER BY frameid, time_window_start
    """

    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(query, (campaign_id, date))
        results = cursor.fetchall()

    conn.close()
    return results
```

### Step 2: Build Route API Request

Group frames by time window and build request payload:

```python
from datetime import datetime
from typing import List, Dict

def build_route_request(playouts: List[Dict], route_release_id: str = "56"):
    """
    Build Route API request from playout data.

    Args:
        playouts: List of playout records from database
        route_release_id: Route release number

    Returns:
        Request payload for Route API
    """
    # Group by time window
    time_windows = {}

    for playout in playouts:
        window_key = playout['time_window_start']

        if window_key not in time_windows:
            time_windows[window_key] = {
                'frames': set(),
                'spot_length_total': 0,
                'break_length_total': 0,
                'count': 0
            }

        time_windows[window_key]['frames'].add(playout['frameid'])
        time_windows[window_key]['spot_length_total'] += playout['playout_length_seconds']
        time_windows[window_key]['break_length_total'] += playout['break_length_seconds']
        time_windows[window_key]['count'] += 1

    # Build schedule
    schedule = []
    for window_start, data in sorted(time_windows.items()):
        window_end = window_start + timedelta(minutes=15)

        schedule.append({
            "datetime_from": window_start.strftime("%Y-%m-%d %H:%M"),
            "datetime_until": window_end.strftime("%Y-%m-%d %H:%M")
        })

    # Calculate averages
    total_frames = len(set(f for w in time_windows.values() for f in w['frames']))
    avg_spot_length = sum(w['spot_length_total'] for w in time_windows.values()) / sum(w['count'] for w in time_windows.values())
    avg_break_length = sum(w['break_length_total'] for w in time_windows.values()) / sum(w['count'] for w in time_windows.values())

    # All unique frames for the day
    all_frames = list(set(p['frameid'] for p in playouts))

    payload = {
        "route_release_id": route_release_id,
        "route_algorithm_version": "10.2",
        "algorithm_figures": ["impacts"],
        "grouping": "frame_ID",
        "demographics": ["ageband>=1"],  # All ages
        "campaign": [{
            "schedule": schedule,
            "spot_length": int(avg_spot_length),
            "spot_break_length": int(avg_break_length),
            "frames": all_frames
        }],
        "target_month": 1
    }

    return payload
```

### Step 3: Call Route API

Make the API call with proper timeout and error handling:

```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def call_route_api(payload: Dict, timeout: int = 120):
    """
    Call Route API with retry logic.

    Args:
        payload: Request payload
        timeout: Request timeout in seconds (default 120)

    Returns:
        API response data or None if failed
    """
    # Setup retry strategy
    retry_strategy = Retry(
        total=3,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["POST"],
        backoff_factor=2  # Wait 2s, 4s, 8s
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)
    session = requests.Session()
    session.mount("https://", adapter)

    headers = {
        'Authorization': os.getenv('ROUTE_API_AUTH'),
        'Content-Type': 'application/json',
        'API-Key': os.getenv('ROUTE_API_KEY')
    }

    url = f"{os.getenv('ROUTE_API_URL')}/rest/process/playout"

    try:
        response = session.post(
            url,
            json=payload,
            headers=headers,
            timeout=timeout
        )
        response.raise_for_status()
        return response.json()

    except requests.exceptions.Timeout:
        print(f"⏱️ Timeout after {timeout}s")
        return None

    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e.response.status_code} - {e.response.text}")
        return None

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None
```

### Step 4: Cache Results

Store the results in PostgreSQL:

```python
def cache_campaign_day(campaign_id: str, date: str, api_response: Dict, route_release_id: int):
    """
    Cache campaign audience data for a specific day.

    Args:
        campaign_id: Campaign reference
        date: Date string
        api_response: Response from Route API
        route_release_id: Route release number
    """
    # Calculate daily metrics from API response
    total_impacts = sum(frame.get('impacts', 0) for frame in api_response.get('data', {}).get('frames', []))
    unique_frames = len(set(frame['frame_id'] for frame in api_response.get('data', {}).get('frames', [])))

    # These would come from Route API response (simplified here)
    reach = total_impacts / 2.5  # Placeholder - get actual reach from API
    grp = reach / 55000  # Placeholder - calculate from population
    frequency = total_impacts / reach if reach > 0 else 0

    conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST'),
        database=os.getenv('POSTGRES_DATABASE'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD')
    )

    query = """
        INSERT INTO cache_campaign_reach_day (
            campaign_id,
            date,
            reach,
            grp,
            frequency,
            total_impacts,
            frame_count,
            route_release_id,
            cached_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
        ON CONFLICT (campaign_id, date)
        DO UPDATE SET
            reach = EXCLUDED.reach,
            grp = EXCLUDED.grp,
            frequency = EXCLUDED.frequency,
            total_impacts = EXCLUDED.total_impacts,
            frame_count = EXCLUDED.frame_count,
            route_release_id = EXCLUDED.route_release_id,
            cached_at = CURRENT_TIMESTAMP
    """

    with conn.cursor() as cursor:
        cursor.execute(query, (
            campaign_id,
            date,
            reach,
            grp,
            frequency,
            total_impacts,
            unique_frames,
            route_release_id
        ))
        conn.commit()

    conn.close()
    print(f"✅ Cached: reach={reach:.0f}, grp={grp:.2f}, freq={frequency:.2f}")
```

### Step 5: Complete Workflow

Put it all together:

```python
def cache_campaign(campaign_id: str, date: str, route_release_id: str = "56"):
    """
    Complete workflow to cache a campaign's audience data for a specific day.

    Args:
        campaign_id: Campaign reference
        date: Date string (YYYY-MM-DD)
        route_release_id: Route release number
    """
    print(f"Processing campaign {campaign_id} on {date}")

    # Step 1: Get playout data
    playouts = get_campaign_playouts(campaign_id, date)
    if not playouts:
        print(f"⚠️ No playouts found for {campaign_id} on {date}")
        return False

    print(f"Found {len(playouts)} playout records")

    # Step 2: Build API request
    payload = build_route_request(playouts, route_release_id)
    print(f"Built request with {len(payload['campaign'][0]['frames'])} frames")

    # Step 3: Call Route API
    response = call_route_api(payload, timeout=120)
    if not response:
        print(f"❌ API call failed for {campaign_id} on {date}")
        return False

    # Step 4: Cache results
    cache_campaign_day(campaign_id, date, response, int(route_release_id))
    print(f"✅ Successfully cached {campaign_id} on {date}")
    return True
```

---

## Error Handling

### Common Errors and Solutions

#### 1. Timeout Errors

**Error**:
```
requests.exceptions.ReadTimeout: Read timed out. (read timeout=30)
```

**Cause**: Large campaigns (200+ frames, 2M+ playouts) take 60-120 seconds

**Solution**:
```python
# Increase timeout
response = session.post(url, json=payload, timeout=120)

# Or detect large campaigns and skip/batch
if len(frames) > 500:
    # Split into multiple requests
    pass
```

#### 2. Invalid Route Release

**Error**:
```json
{"status": "error", "message": "Invalid route_release_id"}
```

**Cause**: Using a release number outside the available window

**Solution**:
```python
# Query available releases first
def get_available_releases():
    response = requests.post(
        f"{ROUTE_API_URL}/rest/version",
        headers=headers
    )
    return response.json()['releases']

# Map date to appropriate release
def get_release_for_date(date):
    # Q3 2025 (R56): Sep 29, 2025 - Jan 4, 2026
    # Q2 2025 (R55): Jun 30, 2025 - Sep 28, 2025
    # etc.
    pass
```

#### 3. Frame Not in Route Release

**Error**: No error, but some frames return zero impacts

**Cause**: Frame not available in specified Route release

**Solution**:
```python
# Assign zero impacts for frames not in release
for frame_id in requested_frames:
    if frame_id not in response_frames:
        # Store with impacts=0
        cache_frame_impacts(frame_id, 0, note="Not in Route release")
```

#### 4. Database Connection Pool Exhausted

**Error**:
```
OperationalError: connection pool exhausted
```

**Cause**: Too many concurrent database connections

**Solution**:
```python
# Use connection pooling
from psycopg2 import pool

connection_pool = pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    host=os.getenv('POSTGRES_HOST'),
    database=os.getenv('POSTGRES_DATABASE'),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD')
)

# Get connection from pool
conn = connection_pool.getconn()
try:
    # Use connection
    pass
finally:
    # Return to pool
    connection_pool.putconn(conn)
```

---

## Performance Optimization

### 0. API Request Optimization (MOST IMPORTANT) ⭐

**Optimize your Route API requests for maximum performance:**

#### Use Minimal Payloads

✅ **DO**: Request only what you need
```json
{
  "route_release_id": 56,
  "route_algorithm_version": "10.2",
  "demographics": [{"demographic_custom": "ageband>0"}],
  "algorithm_figures": ["impacts"],  // ✅ Only impacts
  "campaign": [...]
}
```

❌ **DON'T**: Request all metrics unnecessarily
```json
{
  "route_release_id": 56,
  "option_split_reach": true,  // ❌ Unnecessary for impacts only
  "demographics": [{"demographic_custom": "ageband>0"}],
  "algorithm_figures": ["all"],  // ❌ Slower processing
  "grouping": "frame_id",  // ❌ Not needed for caching
  "campaign": [...]
}
```

#### Grouping Performance Impact

**Without grouping** (campaign-level):
- Processing time: ~30 seconds
- Returns: Campaign totals only
- **Recommended for caching**

**With grouping** (`"grouping": "frame_id"`):
- Processing time: ~60 seconds (~2x slower)
- Returns: Per-frame breakdown + campaign totals
- Use only when per-frame analysis required

#### Algorithm Figures Optimization

| Request | Processing Speed | Use Case |
|---------|------------------|----------|
| `["impacts"]` | Fastest | **Econometric caching (recommended)** |
| `["impacts", "reach", "grp"]` | Medium | Specific metrics needed |
| `["all"]` | Slowest | Exploratory analysis only |

**Best Practice**: For pipeline caching, always use `["impacts"]` only.

### 1. Batch Processing

Process multiple days per campaign before switching campaigns:

```python
# Good: Complete campaign 15884 first
cache_campaign("15884", "2025-10-11")
cache_campaign("15884", "2025-10-12")
cache_campaign("15884", "2025-10-13")
# Then move to next campaign
cache_campaign("15661", "2025-10-11")

# Bad: Switch campaigns frequently
cache_campaign("15884", "2025-10-11")
cache_campaign("15661", "2025-10-11")  # Context switch
cache_campaign("15884", "2025-10-12")  # Context switch
```

### 2. Parallel Workers

Run multiple workers processing different campaign ranges:

```bash
# Terminal 1: Process campaigns 1-330
python backfill_cache.py --start-campaign 1 --end-campaign 330

# Terminal 2: Process campaigns 331-660
python backfill_cache.py --start-campaign 331 --end-campaign 660

# Terminal 3: Process campaigns 661-990
python backfill_cache.py --start-campaign 661 --end-campaign 990
```

**Important**: Respect Route API rate limits (typically 6 calls/second)

### 3. Prioritize Recent Campaigns

Cache most recent campaigns first:

```sql
-- Get campaigns ordered by most recent activity
SELECT
    buyercampaignref,
    MAX(time_window_start) as last_activity
FROM mv_playout_15min
WHERE buyercampaignref IS NOT NULL
GROUP BY buyercampaignref
ORDER BY last_activity DESC;
```

### 4. Skip Already Cached

Check cache before making API calls:

```python
def is_cached(campaign_id: str, date: str) -> bool:
    """Check if campaign-day is already cached."""
    query = """
        SELECT 1 FROM cache_campaign_reach_day
        WHERE campaign_id = %s AND date = %s
    """
    # Execute query
    return result is not None

# In main loop
if is_cached(campaign_id, date):
    print(f"⏩ Skipping {campaign_id} on {date} - already cached")
    continue
```

### 5. Connection Pooling

Use connection pools for database operations:

```python
# Initialize once
db_pool = psycopg2.pool.ThreadedConnectionPool(
    minconn=5,
    maxconn=20,
    host=os.getenv('POSTGRES_HOST'),
    database=os.getenv('POSTGRES_DATABASE'),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD')
)

# Reuse connections
def get_connection():
    return db_pool.getconn()

def return_connection(conn):
    db_pool.putconn(conn)
```

### 6. Estimated Completion Time

Track progress and estimate completion:

```python
from tqdm import tqdm
import time

campaigns = get_campaigns_to_cache()
start_time = time.time()

for i, campaign in enumerate(tqdm(campaigns)):
    cache_campaign(campaign['id'], campaign['date'])

    # Estimate remaining time
    if i > 0 and i % 10 == 0:
        elapsed = time.time() - start_time
        avg_time_per_campaign = elapsed / i
        remaining = len(campaigns) - i
        eta_seconds = remaining * avg_time_per_campaign
        eta_hours = eta_seconds / 3600
        print(f"📊 ETA: {eta_hours:.1f} hours")
```

---

## Monitoring and Maintenance

### Cache Health Metrics

Query cache coverage and freshness:

```sql
-- Total cache coverage
SELECT
    COUNT(DISTINCT campaign_id) as cached_campaigns,
    COUNT(*) as total_entries,
    MIN(date) as earliest_date,
    MAX(date) as latest_date,
    MAX(cached_at) as last_update
FROM cache_campaign_reach_day;

-- Cache age distribution
SELECT
    DATE(cached_at) as cache_date,
    COUNT(*) as entries_cached
FROM cache_campaign_reach_day
GROUP BY DATE(cached_at)
ORDER BY cache_date DESC;

-- Campaigns missing cache
SELECT
    p.buyercampaignref,
    COUNT(DISTINCT DATE(p.time_window_start)) as days_active,
    COUNT(DISTINCT c.date) as days_cached,
    COUNT(DISTINCT DATE(p.time_window_start)) - COUNT(DISTINCT c.date) as days_missing
FROM mv_playout_15min p
LEFT JOIN cache_campaign_reach_day c ON p.buyercampaignref = c.campaign_id
WHERE p.buyercampaignref IS NOT NULL
GROUP BY p.buyercampaignref
HAVING COUNT(DISTINCT DATE(p.time_window_start)) > COUNT(DISTINCT c.date)
ORDER BY days_missing DESC;
```

### Cache Invalidation

Refresh stale cache entries:

```sql
-- Find entries older than 7 days
SELECT
    campaign_id,
    date,
    cached_at,
    AGE(NOW(), cached_at) as cache_age
FROM cache_campaign_reach_day
WHERE cached_at < NOW() - INTERVAL '7 days'
ORDER BY cached_at;

-- Delete and refresh
DELETE FROM cache_campaign_reach_day
WHERE campaign_id = '15884' AND date = '2025-10-11';
-- Then re-cache with fresh API call
```

### Progress Tracking

Create a progress table:

```sql
CREATE TABLE cache_progress (
    campaign_id VARCHAR,
    total_days INTEGER,
    cached_days INTEGER,
    last_cached_date DATE,
    status VARCHAR,  -- 'in_progress', 'completed', 'failed'
    last_updated TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (campaign_id)
);

-- Update progress
UPDATE cache_progress
SET cached_days = cached_days + 1,
    last_cached_date = '2025-10-11',
    status = CASE WHEN cached_days + 1 = total_days THEN 'completed' ELSE 'in_progress' END,
    last_updated = NOW()
WHERE campaign_id = '15884';
```

### Logging Best Practices

```python
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'cache_log_{datetime.now():%Y%m%d}.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Use in code
logger.info(f"Processing campaign {campaign_id} on {date}")
logger.warning(f"Timeout on campaign {campaign_id} - retrying")
logger.error(f"Failed to cache {campaign_id}: {error}")
logger.debug(f"API response: {response}")
```

---

## Quick Reference

### Complete Example Script

```python
#!/usr/bin/env python3
"""
Route API caching script for pipeline teams.
Caches campaign audience data from Route API to PostgreSQL.
"""

import os
import sys
import psycopg2
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

def cache_campaign(campaign_id, date, route_release_id="56"):
    """Cache a single campaign-day."""
    # 1. Get playouts
    playouts = get_campaign_playouts(campaign_id, date)
    if not playouts:
        return False

    # 2. Build request
    payload = build_route_request(playouts, route_release_id)

    # 3. Call API
    response = call_route_api(payload, timeout=120)
    if not response:
        return False

    # 4. Cache results
    cache_campaign_day(campaign_id, date, response, route_release_id)
    return True

if __name__ == "__main__":
    campaigns = get_campaigns_to_cache()

    for campaign in tqdm(campaigns):
        success = cache_campaign(
            campaign['id'],
            campaign['date'],
            campaign['release']
        )

        if success:
            print(f"✅ {campaign['id']} on {campaign['date']}")
        else:
            print(f"❌ {campaign['id']} on {campaign['date']}")
```

### Environment Variables Required

```bash
# Route API
ROUTE_API_KEY=your_api_key
ROUTE_API_AUTH=your_auth_header
ROUTE_API_URL=https://route.mediatelapi.co.uk

# Database
POSTGRES_HOST=your_host_here
POSTGRES_PORT=5432
POSTGRES_DATABASE=route_poc
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
```

### Useful SQL Queries

```sql
-- Check cache status
SELECT * FROM cache_campaign_reach_day WHERE campaign_id = '15884';

-- Count cached campaigns
SELECT COUNT(DISTINCT campaign_id) FROM cache_campaign_reach_day;

-- Find gaps
SELECT DISTINCT buyercampaignref
FROM mv_playout_15min
WHERE buyercampaignref NOT IN (
    SELECT DISTINCT campaign_id FROM cache_campaign_reach_day
);

-- Recent activity
SELECT * FROM cache_campaign_reach_day
WHERE cached_at > NOW() - INTERVAL '1 hour'
ORDER BY cached_at DESC;
```

---

## Support

For questions or issues:

1. **Documentation**: Check `docs/api-reference/route/` for Route API docs
2. **Schema**: See `docs/playout/` for playout data formats
3. **Database**: Check `cache_campaign_reach_day` table structure
4. **Logs**: Review script logs in `logs/cache_*.log`

---

**Last Updated:** October 22, 2025
**Version:** 1.0
**Maintainer:** Route POC Team
