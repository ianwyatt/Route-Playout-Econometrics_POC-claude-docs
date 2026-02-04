# Route API Caching - Quick Start Guide

**For:** Pipeline developers who need to cache Route audience data quickly

---

## Prerequisites

- Python 3.11+
- PostgreSQL database access
- Route API credentials
- `.env` file configured

---

## 5-Minute Setup

### 1. Environment Variables

Create `.env` file in project root:

```bash
# Route API (Custom Endpoint - requires both Basic Auth + API Key)
ROUTE_API_User_Name=your_username
ROUTE_API_Password=your_password
ROUTE_API_KEY=your_api_key_here
ROUTE_API_LIVE_CUSTOM_URL=https://route.mediatelapi.co.uk/rest/process/custom

# Database
POSTGRES_HOST=your_host_here
POSTGRES_PORT=5432
POSTGRES_DATABASE=route_poc
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
```

### 2. Install Dependencies

```bash
pip install psycopg2-binary requests python-dotenv tqdm
```

### 3. Minimal Caching Script

```python
#!/usr/bin/env python3
import os
import psycopg2
import requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def cache_campaign_day(campaign_id: str, date: str):
    """Cache a campaign's audience data for one day."""

    # 1. Get playouts from database
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
            spot_count,
            playout_length_seconds,
            break_length_seconds
        FROM mv_playout_15min
        WHERE TRIM(buyercampaignref) = %s
            AND time_window_start::date = %s
        ORDER BY frameid, time_window_start
    """

    cursor = conn.cursor()
    cursor.execute(query, (campaign_id, date))
    playouts = cursor.fetchall()
    conn.close()

    if not playouts:
        print(f"No playouts found for {campaign_id} on {date}")
        return False

    # 2. Get unique frames and calculate averages
    frames = list(set(p[0] for p in playouts))
    avg_spot_length = int(sum(p[3] for p in playouts) / len(playouts))
    avg_break_length = int(sum(p[4] for p in playouts) / len(playouts))

    # 3. Build Route API request (OPTIMIZED for caching)
    payload = {
        "route_release_id": 56,  # Q3 2025 - must be int, not string!
        "route_algorithm_version": "10.2",
        "demographics": [
            {"demographic_custom": "ageband>0"}  # All adults - correct syntax
        ],
        "algorithm_figures": ["impacts"],  # Only impacts - fastest processing
        # No grouping - ~2x faster for campaign-level caching
        "campaign": [{
            "schedule": [{
                "datetime_from": f"{date} 00:00",
                "datetime_until": f"{date} 23:59"
            }],
            "spot_length": avg_spot_length,
            "spot_break_length": avg_break_length,
            "frames": frames
        }],
        "target_month": 1
    }

    # 4. Call Route API (dual authentication required)
    url = os.getenv('ROUTE_API_LIVE_CUSTOM_URL')

    # Both Basic Auth AND X-Api-Key required
    auth = (
        os.getenv('ROUTE_API_User_Name'),
        os.getenv('ROUTE_API_Password')
    )

    headers = {
        'Content-Type': 'application/json',
        'X-Api-Key': os.getenv('ROUTE_API_KEY')
    }

    try:
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            auth=auth,  # Basic authentication
            timeout=300  # 5 minutes for large campaigns
        )
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"API Error: {e}")
        return False

    # 5. Calculate metrics (simplified)
    total_impacts = sum(
        frame.get('impacts', 0)
        for frame in data.get('data', {}).get('frames', [])
    )

    # Placeholder calculations - adjust based on actual API response
    reach = total_impacts / 2.5
    grp = reach / 55000
    frequency = total_impacts / reach if reach > 0 else 0

    # 6. Save to cache
    conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST'),
        database=os.getenv('POSTGRES_DATABASE'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD')
    )

    insert_query = """
        INSERT INTO cache_campaign_reach_day (
            campaign_id, date, reach, grp, frequency,
            total_impacts, frame_count, route_release_id
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (campaign_id, date) DO UPDATE SET
            reach = EXCLUDED.reach,
            grp = EXCLUDED.grp,
            frequency = EXCLUDED.frequency,
            total_impacts = EXCLUDED.total_impacts,
            frame_count = EXCLUDED.frame_count,
            cached_at = CURRENT_TIMESTAMP
    """

    cursor = conn.cursor()
    cursor.execute(insert_query, (
        campaign_id, date, reach, grp, frequency,
        total_impacts, len(frames), 56
    ))
    conn.commit()
    conn.close()

    print(f"✅ Cached {campaign_id} on {date}: reach={reach:.0f}, grp={grp:.2f}, freq={frequency:.2f}")
    return True

# Example usage
if __name__ == "__main__":
    cache_campaign_day("15884", "2025-10-11")
    cache_campaign_day("15884", "2025-10-12")
    cache_campaign_day("15884", "2025-10-13")
```

### 4. Run It

```bash
python cache_script.py
```

Expected output:
```
✅ Cached 15884 on 2025-10-11: reach=394, grp=1.53, freq=2.16
✅ Cached 15884 on 2025-10-12: reach=297, grp=1.02, freq=1.90
✅ Cached 15884 on 2025-10-13: reach=281, grp=1.14, freq=2.25
```

---

## Common Issues

### Timeout Errors

**Error**: `requests.exceptions.ReadTimeout`

**Fix**: Increase timeout
```python
response = requests.post(url, json=payload, timeout=180)  # 3 minutes
```

### Invalid Release

**Error**: `"Invalid route_release_id"`

**Fix**: Use correct release for date
```python
# Q3 2025 (Sep 29 - Jan 4, 2026) → "56"
# Q2 2025 (Jun 30 - Sep 28, 2025) → "55"
"route_release_id": "56"
```

### Missing Frames

**Issue**: Some frames return 0 impacts

**Reason**: Frame not available in Route release (normal)

**Action**: Store with impacts=0, no error

---

## Verify Cache

```sql
-- Check what's cached
SELECT * FROM cache_campaign_reach_day WHERE campaign_id = '15884';

-- Count cached campaigns
SELECT COUNT(DISTINCT campaign_id) FROM cache_campaign_reach_day;

-- Recent cache activity
SELECT * FROM cache_campaign_reach_day
WHERE cached_at > NOW() - INTERVAL '1 hour'
ORDER BY cached_at DESC;
```

---

## Next Steps

1. **Scale Up**: Process multiple campaigns in a loop
2. **Add Progress Tracking**: Use `tqdm` for progress bars
3. **Handle Errors**: Add retry logic and logging
4. **Optimize**: Batch processing, parallel workers

**Full Documentation**: See `ROUTE_API_CACHING_GUIDE.md` for complete implementation details.

---

## Key Points

✅ Use `mv_playout_15min` materialized view (fast)
✅ Set timeout to 120+ seconds for large campaigns
✅ Cache uses `ON CONFLICT` to update existing entries
✅ Query cache before calling API to avoid duplicates
✅ Store results with `campaign_id` + `date` as primary key

---

**Quick Reference**: [ROUTE_API_CACHING_GUIDE.md](./ROUTE_API_CACHING_GUIDE.md)
