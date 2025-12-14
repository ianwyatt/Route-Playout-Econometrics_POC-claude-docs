# Route API Integration Guide for POC Developers

**Last Updated:** 2025-11-14
**Status:** ✅ PRODUCTION GUIDANCE
**Audience:** POC Application Developers

---

## Table of Contents

1. [Overview](#overview)
2. [🚨 CRITICAL: Frame Limits (Grouping vs Non-Grouping)](#-critical-frame-limits-grouping-vs-non-grouping)
3. [Authentication & Credentials](#authentication--credentials)
4. [Rate Limiting Strategy](#rate-limiting-strategy)
5. [Frame Validation Workflow](#frame-validation-workflow)
6. [Cache-First Integration Pattern](#cache-first-integration-pattern)
7. [Error Handling](#error-handling)
8. [Common Pitfalls & Solutions](#common-pitfalls--solutions)
9. [Working Examples](#working-examples)
10. [Quick Reference](#quick-reference)

---

## Overview

The Route API provides demographic audience metrics (reach, GRP, frequency, impacts) for outdoor advertising campaigns. This guide covers critical integration patterns learned from the pipeline team's cache implementation.

### Key Endpoints

| Endpoint | Purpose | Used For |
|----------|---------|----------|
| `/rest/framedata` | Frame validation | Check frames exist in Route release |
| `/rest/campaign_insights` | Standard demographics | 7 standard demographic segments |
| `/rest/process/custom` | Custom demographics | 792 available demographic variables |

### Demographic Segments (Standard 7)

1. `all_adults` - All adults 15+
2. `age_15_34` - Young adults
3. `age_35_54` - Middle-aged adults
4. `age_55_plus` - Older adults
5. `abc1` - Higher socio-economic groups
6. `c2de` - Lower socio-economic groups
7. `housewife` - Main household shopper

---

## 🚨 CRITICAL: Frame Limits (Grouping vs Non-Grouping)

**THIS IS THE #1 PITFALL FOR POC DEVELOPERS**

The Route API has **TWO different frame limits** depending on whether you request per-frame breakdowns or aggregate campaign metrics.

### Call Type 1: WITH Grouping (Per-Frame Breakdown)

**Use Case:** "Show me the top 10 performing frames in this campaign"

**Request:**
```json
{
  "route_release_id": 56,
  "route_algorithm_version": 10.2,
  "target_month": 10,
  "algorithm_figures": ["impacts", "reach", "average_frequency", "grp"],
  "demographics": [{"demographic_id": 1}],
  "grouping": "frame",  // ← THIS ENABLES PER-FRAME BREAKDOWN
  "campaign": [
    {
      "schedule": [{"datetime_from": "2025-10-08 00:00", "datetime_until": "2025-10-08 23:59"}],
      "frames": [1234567890, 1234567891, 1234567892],
      "spot_length": 6,
      "spot_break_length": 54
    }
  ]
}
```

**Response:**
```json
{
  "results": [
    {"frame_id": 1234567890, "figures": {"reach": 150, "grp": 2.5, "average_frequency": 1.8}},
    {"frame_id": 1234567891, "figures": {"reach": 200, "grp": 3.2, "average_frequency": 2.1}},
    {"frame_id": 1234567892, "figures": {"reach": 180, "grp": 2.8, "average_frequency": 1.9}}
  ]
}
```

**⚠️ LIMIT: Maximum 10,000 unique frames**

### Call Type 2: WITHOUT Grouping (Aggregate Campaign Metrics)

**Use Case:** "What was the total reach for this campaign?"

**Request:**
```json
{
  "route_release_id": 56,
  "route_algorithm_version": 10.2,
  "target_month": 10,
  "algorithm_figures": ["impacts", "reach", "average_frequency", "grp", "population"],
  "demographics": [{"demographic_id": 1}],
  // NO "grouping" parameter
  "campaign": [
    {
      "schedule": [{"datetime_from": "2025-10-08 00:00", "datetime_until": "2025-10-08 00:15"}],
      "frames": [1234567890],
      "spot_length": 6,
      "spot_break_length": 54
    },
    {
      "schedule": [{"datetime_from": "2025-10-08 00:15", "datetime_until": "2025-10-08 00:30"}],
      "frames": [1234567890, 1234567891],
      "spot_length": 6,
      "spot_break_length": 54
    }
    // ... hundreds or thousands more campaign entries
  ]
}
```

**Response:**
```json
{
  "results": [
    {
      "figures": {
        "reach": 1523,             // Aggregate across ALL frames
        "gross_rating_points": 12.5,
        "average_frequency": 2.8,
        "impacts": 4263,
        "population": 34123
      }
    }
  ]
}
```

**✅ LIMIT: NO FRAME LIMIT** - You can include any number of frames!

### Quick Decision Matrix

| Your Need | Use Grouping? | Frame Limit | Response |
|-----------|---------------|-------------|----------|
| Campaign-level KPIs ("Total reach?") | ❌ No | None | 1 result |
| Per-frame comparison ("Which frame performed best?") | ✅ Yes | 10,000 | 1 result per frame |
| Large campaign > 10k frames | ❌ No OR batch | 10k per batch | Multiple calls if batching |

---

## Authentication & Credentials

### Standard Authentication

```python
import requests

# Single account setup
headers = {
    'API-Key': 'your_route_api_key',
    'User-Name': 'your_username',
    'Password': 'your_password',
    'Content-Type': 'application/json'
}

response = requests.post(
    'https://api.route.com/rest/process/custom',
    headers=headers,
    json=payload
)
```

### Environment Variables (Recommended)

```python
import os
from dotenv import load_dotenv

load_dotenv()

ROUTE_API_KEY = os.getenv('ROUTE_API_KEY')
ROUTE_API_USERNAME = os.getenv('ROUTE_API_User_Name')
ROUTE_API_PASSWORD = os.getenv('ROUTE_API_Password')
```

**.env file:**
```env
ROUTE_API_KEY=your_api_key_here
ROUTE_API_User_Name=your_username
ROUTE_API_Password=your_password
```

**🔒 SECURITY:** Never commit credentials to git. Use environment variables only.

---

## Rate Limiting Strategy

### Rate Limits

- **6 calls/second per account**
- **429 error** if rate limit exceeded
- **Exponential backoff** required on errors

### Basic Rate Limiting

```python
import time
from datetime import datetime, timedelta

class RouteAPIClient:
    def __init__(self):
        self.calls_this_second = 0
        self.current_second = datetime.now().second
        self.max_calls_per_second = 6

    def call_api(self, endpoint, payload):
        # Check if we're in a new second
        current_second = datetime.now().second
        if current_second != self.current_second:
            self.calls_this_second = 0
            self.current_second = current_second

        # Wait if we've hit the limit
        if self.calls_this_second >= self.max_calls_per_second:
            time.sleep(1.0 - (datetime.now().microsecond / 1000000))
            self.calls_this_second = 0
            self.current_second = datetime.now().second

        # Make the call
        response = requests.post(endpoint, json=payload, headers=self.headers)
        self.calls_this_second += 1

        return response
```

### Exponential Backoff on Errors

```python
def call_api_with_retry(endpoint, payload, max_retries=3):
    """Call Route API with exponential backoff on 429 errors"""
    for attempt in range(max_retries):
        response = requests.post(endpoint, json=payload, headers=headers)

        if response.status_code == 200:
            return response.json()

        if response.status_code == 429:  # Rate limit exceeded
            wait_time = (2 ** attempt) + random.uniform(0, 1)  # Exponential backoff
            logger.warning(f"Rate limit hit. Waiting {wait_time:.2f}s before retry {attempt + 1}/{max_retries}")
            time.sleep(wait_time)
            continue

        # Other errors
        response.raise_for_status()

    raise Exception(f"Max retries ({max_retries}) exceeded")
```

### Advanced: Dual Account Load Balancing

**Pipeline team uses TWO accounts for 12 calls/sec total:**

```python
class DualAccountRouteClient:
    def __init__(self):
        self.account_1 = RouteAPIClient(api_key=KEY_1, username=USER_1, password=PASS_1)
        self.account_2 = RouteAPIClient(api_key=KEY_2, username=USER_2, password=PASS_2)
        self.current_account = 0

    def call_api(self, endpoint, payload):
        """Alternate between accounts for 12 calls/sec total"""
        if self.current_account == 0:
            client = self.account_1
            self.current_account = 1
        else:
            client = self.account_2
            self.current_account = 0

        return client.call_api(endpoint, payload)
```

---

## Frame Validation Workflow

**ALWAYS validate frames exist in Route release BEFORE calling campaign_insights**

### Why Validate?

- Prevents API error 220 (invalid frames)
- Route releases don't include all frames
- Frames may be decommissioned or not yet added

### Frame Validation Endpoint

```python
def validate_frames(frame_ids, route_release_id=56):
    """
    Check which frames exist in Route release

    Returns:
        valid_frames: List of frame IDs that exist in Route
        invalid_frames: List of frame IDs that don't exist
    """
    payload = {
        "route_release_id": route_release_id,
        "frame_ids": frame_ids
    }

    response = requests.post(
        'https://api.route.com/rest/framedata',
        headers=headers,
        json=payload
    )

    data = response.json()

    valid_frames = [f['frame_id'] for f in data.get('frames', [])]
    invalid_frames = [fid for fid in frame_ids if fid not in valid_frames]

    return valid_frames, invalid_frames
```

### Complete Validation Workflow

```python
def get_campaign_audience_safe(campaign_id, date, route_release_id=56):
    """
    Safe Route API call with frame validation
    """
    # Step 1: Get frames from database
    frames = db.query("""
        SELECT DISTINCT frameid
        FROM mv_playout_15min
        WHERE buyercampaignref = %s
          AND time_window_start::date = %s
    """, (campaign_id, date))

    frame_ids = [f['frameid'] for f in frames]

    # Step 2: Validate frames exist in Route release
    valid_frames, invalid_frames = validate_frames(frame_ids, route_release_id)

    if invalid_frames:
        logger.warning(f"Campaign {campaign_id} has {len(invalid_frames)} invalid frames in R{route_release_id}")
        logger.warning(f"Invalid frames: {invalid_frames[:10]}...")  # Log first 10

    if not valid_frames:
        raise ValueError(f"No valid frames found for campaign {campaign_id} in R{route_release_id}")

    # Step 3: Build Route API payload with ONLY valid frames
    payload = build_route_payload(valid_frames, campaign_id, date, route_release_id)

    # Step 4: Call Route API
    response = call_api_with_retry('/rest/process/custom', payload)

    return response
```

---

## Cache-First Integration Pattern

**ALWAYS check cache before calling Route API**

### Why Cache-First?

- **1,000-6,000x faster** than API calls
- **No rate limits** or API costs
- **99%+ campaigns** already cached (826 campaigns on MS-01)

### Complete Integration Pattern

```python
def get_campaign_demographics(campaign_id, start_date, end_date):
    """
    Recommended POC integration pattern

    Returns:
        DataFrame with demographic impacts
    """
    # Step 1: Try cache first (sub-second response)
    cached_data = query_cache(campaign_id, start_date, end_date)

    if cached_data is not None and len(cached_data) > 0:
        logger.info(f"Cache HIT for campaign {campaign_id}")
        return cached_data  # 1,000-6,000x faster!

    # Step 2: Cache miss - call Route API
    logger.info(f"Cache MISS for campaign {campaign_id} - calling Route API")

    # Get frames from database
    frames_query = """
        SELECT
            frameid,
            time_window_start,
            time_window_end,
            spot_count,
            playout_length_seconds,
            break_length_seconds
        FROM mv_playout_15min
        WHERE buyercampaignref = %s
          AND time_window_start >= %s
          AND time_window_start < %s
        ORDER BY time_window_start
    """

    frames = pd.read_sql(frames_query, db_conn, params=(campaign_id, start_date, end_date))

    if frames.empty:
        raise ValueError(f"No playout data found for campaign {campaign_id}")

    # Validate frames
    frame_ids = frames['frameid'].unique().tolist()
    valid_frames, invalid_frames = validate_frames(frame_ids)

    if not valid_frames:
        raise ValueError(f"No valid frames in Route for campaign {campaign_id}")

    # Filter to valid frames only
    frames = frames[frames['frameid'].isin(valid_frames)]

    # Build Route API payload (non-grouping for aggregate)
    payload = {
        "route_release_id": 56,
        "route_algorithm_version": 10.2,
        "target_month": start_date.month,
        "algorithm_figures": ["impacts"],  # Minimal for fastest response
        "demographics": [{"demographic_id": i} for i in range(1, 8)],  # All 7 segments
        "campaign": build_campaign_entries(frames)
    }

    # Call Route API
    api_response = call_api_with_retry('/rest/process/custom', payload)

    # Step 3: (Optional) Store in cache for future use
    store_in_cache(campaign_id, api_response)

    # Step 4: Return data in same format as cache
    return format_api_response(api_response)


def query_cache(campaign_id, start_date, end_date):
    """Query cached demographic data"""
    query = """
        SELECT
            time_window_start,
            demographic_segment,
            impacts * 1000 as impacts  -- Convert from thousands
        FROM cache_route_impacts_15min_by_demo
        WHERE campaign_id = %s
          AND time_window_start >= %s
          AND time_window_start < %s
        ORDER BY time_window_start, demographic_segment
    """

    try:
        return pd.read_sql(query, db_conn, params=(campaign_id, start_date, end_date))
    except Exception as e:
        logger.warning(f"Cache query failed: {e}")
        return None
```

---

## Error Handling

### Common Route API Errors

| Error Code | Meaning | Solution |
|------------|---------|----------|
| 220 | Invalid frame IDs | Use frame validation endpoint first |
| 429 | Rate limit exceeded | Implement exponential backoff |
| 401 | Authentication failed | Check API credentials |
| 500 | Internal server error | Retry with backoff |

### Robust Error Handling Example

```python
def call_route_api_robust(payload, max_retries=3):
    """
    Call Route API with comprehensive error handling
    """
    for attempt in range(max_retries):
        try:
            response = requests.post(
                'https://api.route.com/rest/process/custom',
                headers=headers,
                json=payload,
                timeout=60  # 60 second timeout
            )

            # Check status code
            if response.status_code == 200:
                return response.json()

            elif response.status_code == 220:
                # Invalid frames - don't retry
                error_data = response.json()
                logger.error(f"Invalid frames: {error_data}")
                raise ValueError(f"Invalid frames in Route API call: {error_data}")

            elif response.status_code == 429:
                # Rate limit - exponential backoff
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                logger.warning(f"Rate limit hit. Waiting {wait_time:.2f}s (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
                continue

            elif response.status_code == 401:
                # Auth error - don't retry
                logger.error("Authentication failed - check API credentials")
                raise ValueError("Route API authentication failed")

            elif response.status_code >= 500:
                # Server error - retry with backoff
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                logger.warning(f"Server error {response.status_code}. Retrying in {wait_time:.2f}s")
                time.sleep(wait_time)
                continue

            else:
                # Other error
                logger.error(f"Unexpected error {response.status_code}: {response.text}")
                response.raise_for_status()

        except requests.Timeout:
            logger.warning(f"Request timeout (attempt {attempt + 1}/{max_retries})")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            raise

        except requests.ConnectionError as e:
            logger.warning(f"Connection error (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            raise

    raise Exception(f"Max retries ({max_retries}) exceeded")
```

---

## Common Pitfalls & Solutions

### ❌ Pitfall 1: Adding Grouping to Large Campaigns

```python
# BAD - Will fail if campaign has > 10k frames
payload = {
    "grouping": "frame",  # ← Don't add unless you need per-frame breakdown!
    "campaign": build_campaign_with_50k_frames()  # ❌ Exceeds 10k limit
}
```

**Solution:** Only use grouping when you actually need per-frame results.

```python
# GOOD - Check frame count first
frame_count = get_campaign_frame_count(campaign_id)

if frame_count <= 10000 and need_per_frame_breakdown:
    payload["grouping"] = "frame"
else:
    # Use aggregate metrics (no frame limit)
    # Returns single result for entire campaign
    pass
```

### ❌ Pitfall 2: Not Validating Frames

```python
# BAD - Directly calling API without validation
frames = get_all_campaign_frames(campaign_id)  # May include invalid frames
payload = {"campaign": [{"frames": frames, ...}]}  # ❌ Will fail with error 220
```

**Solution:** Always validate frames first.

```python
# GOOD - Validate before calling
frames = get_all_campaign_frames(campaign_id)
valid_frames, invalid_frames = validate_frames(frames)

if invalid_frames:
    logger.warning(f"Skipping {len(invalid_frames)} invalid frames")

payload = {"campaign": [{"frames": valid_frames, ...}]}  # ✅ Only valid frames
```

### ❌ Pitfall 3: Not Using Cache-First Pattern

```python
# BAD - Always calling API
def get_campaign_data(campaign_id, date):
    return call_route_api(campaign_id, date)  # ❌ Slow, expensive, rate-limited
```

**Solution:** Check cache first.

```python
# GOOD - Cache-first pattern
def get_campaign_data(campaign_id, date):
    cached = query_cache(campaign_id, date)
    if cached:
        return cached  # ✅ 1,000x faster!
    return call_route_api(campaign_id, date)
```

### ❌ Pitfall 4: Not Handling Rate Limits

```python
# BAD - No rate limiting
for campaign in campaigns:
    result = call_route_api(campaign)  # ❌ Will hit 429 errors
```

**Solution:** Implement rate limiting and backoff.

```python
# GOOD - Rate limited with backoff
client = RouteAPIClient(max_calls_per_second=6)
for campaign in campaigns:
    result = client.call_api_with_retry(campaign)  # ✅ Handles rate limits
```

### ❌ Pitfall 5: Forgetting to Multiply Impacts by 1000

```python
# BAD - Reading cached impacts directly
query = "SELECT impacts FROM cache_route_impacts_15min_by_demo"
df = pd.read_sql(query, conn)
print(df['impacts'].sum())  # ❌ Shows 1,234 instead of 1,234,000
```

**Solution:** Always multiply cached impacts by 1000.

```python
# GOOD - Convert from thousands to actual impacts
query = "SELECT impacts * 1000 as impacts FROM cache_route_impacts_15min_by_demo"
df = pd.read_sql(query, conn)
print(df['impacts'].sum())  # ✅ Shows 1,234,000
```

---

## Working Examples

### Example 1: Simple Campaign Audience Query (Cache-First)

```python
import psycopg2
import pandas as pd

def get_campaign_audience(campaign_id, date):
    """
    Get demographic audience for campaign on specific date
    Cache-first pattern with Route API fallback
    """
    # Database connection
    conn = psycopg2.connect(
        host='192.168.1.34',
        port=5432,
        database='route_poc',
        user='postgres',
        password=os.getenv('MS01_DB_PASSWORD')
    )

    # Try cache first
    cache_query = """
        SELECT
            demographic_segment,
            SUM(impacts * 1000) as total_impacts
        FROM cache_route_impacts_15min_by_demo
        WHERE campaign_id = %s
          AND time_window_start::date = %s
        GROUP BY demographic_segment
        ORDER BY total_impacts DESC
    """

    cached_data = pd.read_sql(cache_query, conn, params=(campaign_id, date))

    if not cached_data.empty:
        print(f"✅ Cache HIT for campaign {campaign_id}")
        return cached_data

    print(f"⚠️ Cache MISS - calling Route API")

    # Fallback to Route API
    # (Implementation here - see Example 2)

    conn.close()
    return api_data

# Usage
result = get_campaign_audience('18425', '2025-10-06')
print(result)
```

### Example 2: Route API Call with Frame Validation

```python
def call_route_api_for_campaign(campaign_id, date, route_release_id=56):
    """
    Complete Route API integration with validation
    """
    import requests
    from datetime import datetime, timedelta

    # Step 1: Get frames from database
    conn = psycopg2.connect(...)

    frames_query = """
        SELECT DISTINCT
            frameid,
            spot_count,
            playout_length_seconds,
            break_length_seconds
        FROM mv_playout_15min
        WHERE buyercampaignref = %s
          AND time_window_start::date = %s
    """

    frames_df = pd.read_sql(frames_query, conn, params=(campaign_id, date))
    frame_ids = frames_df['frameid'].tolist()

    # Step 2: Validate frames
    validation_payload = {
        "route_release_id": route_release_id,
        "frame_ids": frame_ids
    }

    headers = {
        'API-Key': os.getenv('ROUTE_API_KEY'),
        'User-Name': os.getenv('ROUTE_API_User_Name'),
        'Password': os.getenv('ROUTE_API_Password'),
        'Content-Type': 'application/json'
    }

    val_response = requests.post(
        'https://api.route.com/rest/framedata',
        headers=headers,
        json=validation_payload
    )

    valid_frames = [f['frame_id'] for f in val_response.json().get('frames', [])]

    if not valid_frames:
        raise ValueError(f"No valid frames for campaign {campaign_id}")

    # Step 3: Build Route API payload (non-grouping for aggregate)
    datetime_from = f"{date} 00:00"
    datetime_until = f"{date} 23:59"

    # Get average spot/break length
    avg_spot_length = int(frames_df['playout_length_seconds'].mean())
    avg_break_length = int(frames_df['break_length_seconds'].mean())

    route_payload = {
        "route_release_id": route_release_id,
        "route_algorithm_version": 10.2,
        "target_month": int(date.split('-')[1]),
        "algorithm_figures": ["impacts", "reach", "average_frequency", "grp"],
        "demographics": [{"demographic_id": i} for i in range(1, 8)],  # All 7 segments
        "campaign": [
            {
                "schedule": [
                    {
                        "datetime_from": datetime_from,
                        "datetime_until": datetime_until
                    }
                ],
                "frames": valid_frames,
                "spot_length": avg_spot_length,
                "spot_break_length": avg_break_length
            }
        ]
    }

    # Step 4: Call Route API
    response = requests.post(
        'https://api.route.com/rest/process/custom',
        headers=headers,
        json=route_payload
    )

    response.raise_for_status()

    return response.json()

# Usage
api_data = call_route_api_for_campaign('18425', '2025-10-06')
print(f"Campaign reach: {api_data['results'][0]['figures']['reach']}")
```

### Example 3: Batch Processing with Rate Limiting

```python
def process_multiple_campaigns(campaign_ids, date):
    """
    Process multiple campaigns with rate limiting
    """
    import time

    results = {}
    calls_this_second = 0
    max_calls_per_second = 6
    current_second = time.time()

    for campaign_id in campaign_ids:
        # Rate limiting
        if time.time() - current_second >= 1.0:
            # New second - reset counter
            calls_this_second = 0
            current_second = time.time()

        if calls_this_second >= max_calls_per_second:
            # Wait for next second
            sleep_time = 1.0 - (time.time() - current_second)
            if sleep_time > 0:
                time.sleep(sleep_time)
            calls_this_second = 0
            current_second = time.time()

        # Process campaign (cache-first)
        try:
            result = get_campaign_audience(campaign_id, date)
            results[campaign_id] = result
            calls_this_second += 1
        except Exception as e:
            print(f"Error processing {campaign_id}: {e}")
            results[campaign_id] = None

    return results

# Usage
campaigns = ['18425', '18426', '18427']
batch_results = process_multiple_campaigns(campaigns, '2025-10-06')
```

---

## Quick Reference

### Cache vs API Decision Tree

```
User requests campaign audience data
    ↓
Check if campaign is in cache
    ↓
├─ YES (cache hit)
│   ↓
│   Query cache table (<5ms)
│   ↓
│   Return cached data ✅ FAST
│
└─ NO (cache miss)
    ↓
    Get frames from mv_playout_15min
    ↓
    Validate frames (/rest/framedata)
    ↓
    ├─ No valid frames → Error
    │
    └─ Has valid frames
        ↓
        Check frame count
        ↓
        ├─ Need per-frame breakdown + ≤10k frames
        │   ↓
        │   Call API WITH grouping
        │
        └─ Need aggregate metrics OR >10k frames
            ↓
            Call API WITHOUT grouping
            ↓
            (Optional) Store in cache
            ↓
            Return API data ✅ SLOWER
```

### Essential Code Snippets

**Query Cache:**
```python
query = """
    SELECT demographic_segment, SUM(impacts * 1000) as impacts
    FROM cache_route_impacts_15min_by_demo
    WHERE campaign_id = %s AND time_window_start::date = %s
    GROUP BY demographic_segment
"""
```

**Validate Frames:**
```python
payload = {"route_release_id": 56, "frame_ids": frame_list}
response = requests.post('/rest/framedata', json=payload, headers=headers)
valid_frames = [f['frame_id'] for f in response.json()['frames']]
```

**Call API (Aggregate):**
```python
payload = {
    "route_release_id": 56,
    "algorithm_figures": ["impacts", "reach", "grp", "average_frequency"],
    "demographics": [{"demographic_id": i} for i in range(1, 8)],
    "campaign": [{"frames": valid_frames, "schedule": [...], ...}],
    # NO "grouping" parameter = aggregate metrics
}
```

**Call API (Per-Frame):**
```python
payload = {
    "route_release_id": 56,
    "grouping": "frame",  # ← Per-frame breakdown
    "algorithm_figures": ["impacts", "reach", "grp", "average_frequency"],
    "demographics": [{"demographic_id": i} for i in range(1, 8)],
    "campaign": [{"frames": valid_frames[:10000], ...}],  # Max 10k frames!
}
```

---

## Related Documentation

### In This Folder (POC Database Docs)
- [README.md](./README.md) - Database handover index
- [CACHE_USAGE_GUIDE.md](./CACHE_USAGE_GUIDE.md) - Complete cache query guide
- [CONNECTION.md](./CONNECTION.md) - Database connection details
- [SCHEMA_REFERENCE.md](./SCHEMA_REFERENCE.md) - Database schema

### In Parent Folder (Route API Docs)
- [../ROUTE_API_CACHING_GUIDE.md](../ROUTE_API_CACHING_GUIDE.md) - Route API caching implementation
- [../QUICK_START.md](../QUICK_START.md) - Quick start guide
- [../TROUBLESHOOTING.md](../TROUBLESHOOTING.md) - Common issues

---

## Support & Contact

**Questions About:**
- Route API integration: See this guide
- Database caching: See [CACHE_USAGE_GUIDE.md](./CACHE_USAGE_GUIDE.md)
- Connection issues: See [CONNECTION.md](./CONNECTION.md)
- Performance: See cache-first pattern above

**Pipeline Team:** ian@route.org.uk

---

**Document Version:** 1.0
**Last Updated:** 2025-11-14
**Status:** ✅ PRODUCTION GUIDANCE
**For:** Route Playout Econometrics POC Development Team
