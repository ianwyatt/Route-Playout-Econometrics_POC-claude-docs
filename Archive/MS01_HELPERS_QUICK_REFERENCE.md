# MS-01 Helpers Quick Reference

**One-page reference for ms01_helpers.py functions**

## Setup

```python
from src.db import initialize_ms01_database, close_ms01_database

# Initialize (do once at app start)
await initialize_ms01_database()

# Close (do once at app shutdown)
await close_ms01_database()
```

## Route API Integration (Primary Use Case)

```python
from src.db import (
    get_campaign_for_route_api,
    get_route_release_for_date,
    build_route_api_payload
)

# 1. Get campaign data for Route API
data = await get_campaign_for_route_api('18295', '2025-08-01', '2025-09-01')
# Returns: List[Dict] with frameid, datetime_from, datetime_to, spot_count, etc.

# 2. Get Route release for the date
release = await get_route_release_for_date('2025-08-01')
# Returns: Dict with release_number ('R55'), name ('Q2 2025')

# 3. Build Route API payload
payload = build_route_api_payload(data, release['release_number'])
# Returns: Dict ready for POST to Route API
```

## Campaign Statistics

```python
from src.db import get_campaign_summary, get_campaign_by_date

# Get overall campaign stats
summary = await get_campaign_summary('18295')
# Returns: total_frames, days_active, total_playouts, start_date, end_date, etc.

# Get stats for date range
stats = await get_campaign_by_date('18295', '2025-08-01', '2025-09-01')
# Returns: frames, total_windows, total_spots, avg_spot_length
```

## Time-Series Data (for Charts)

```python
from src.db import get_hourly_activity, get_daily_summary

# Hourly breakdown
hourly = await get_hourly_activity('18295', '2025-08-01', '2025-08-02')
# Returns: List[Dict] with hour, active_windows, total_spots

# Daily breakdown
daily = await get_daily_summary('18295', '2025-08-01', '2025-09-01')
# Returns: List[Dict] with date, frames, windows, spots
```

## Brand-Level Analysis

```python
from src.db import get_campaign_by_brand, split_audience_by_brand
from datetime import datetime

# Campaign performance by brand
brands = await get_campaign_by_brand('18699', '2025-08-20', '2025-08-25')
# Returns: List[Dict] with spacebrandid, unique_frames, active_windows, total_spots

# Split Route API impacts by brand (after getting Route response)
brand_impacts = await split_audience_by_brand(
    frame_id='1234859642',
    campaign_id='18699',
    window_start=datetime(2025, 8, 23, 11, 15, 0),
    total_impacts=10000.0
)
# Returns: List[Dict] with brand_id, spots, proportion, impacts
```

## Frame Queries

```python
from src.db import is_frame_active, get_frame_campaigns

# Check if frame was active on date
active = await is_frame_active('1234567890', '2025-08-15')
# Returns: bool

# Get campaigns for a frame
campaigns = await get_frame_campaigns('1234567890', '2025-08-01', '2025-09-01')
# Returns: List[Dict] with buyercampaignref, windows, total_spots, etc.
```

## Data Status

```python
from src.db import check_data_freshness, get_date_coverage, get_all_campaigns

# Check data freshness
freshness = await check_data_freshness()
# Returns: latest_window, latest_playout, hours_old

# Check date coverage
coverage = await get_date_coverage()
# Returns: start_date, end_date, days_with_data

# List available campaigns
campaigns = await get_all_campaigns(limit=50)
# Returns: List[Dict] with buyercampaignref, total_frames, total_spots, etc.
```

## Common Patterns

### Pattern 1: Campaign Dashboard

```python
async def get_campaign_dashboard(campaign_id: str):
    """Get all data for campaign dashboard."""
    await initialize_ms01_database()

    try:
        summary = await get_campaign_summary(campaign_id)

        start = summary['start_date'].strftime('%Y-%m-%d')
        end = summary['end_date'].strftime('%Y-%m-%d')

        daily = await get_daily_summary(campaign_id, start, end)
        brands = await get_campaign_by_brand(campaign_id, start, end)

        return {
            'summary': summary,
            'daily_breakdown': daily,
            'brand_breakdown': brands
        }
    finally:
        await close_ms01_database()
```

### Pattern 2: Route API Call Preparation

```python
async def prepare_route_api_call(campaign_id: str, start_date: str, end_date: str):
    """Prepare complete Route API call."""
    await initialize_ms01_database()

    try:
        # Get playout data
        data = await get_campaign_for_route_api(campaign_id, start_date, end_date)

        # Get Route release
        release = await get_route_release_for_date(start_date)

        # Build payload
        payload = build_route_api_payload(data, release['release_number'])

        return payload
    finally:
        await close_ms01_database()
```

### Pattern 3: Brand Impact Distribution

```python
async def distribute_impacts_by_brand(
    route_api_response: Dict,
    campaign_id: str
):
    """Distribute Route API impacts across brands."""
    await initialize_ms01_database()

    try:
        results = []

        for frame in route_api_response['frames']:
            for window in frame['windows']:
                brand_split = await split_audience_by_brand(
                    frame_id=frame['frame_id'],
                    campaign_id=campaign_id,
                    window_start=window['datetime_from'],
                    total_impacts=window['impacts']
                )
                results.extend(brand_split)

        return results
    finally:
        await close_ms01_database()
```

## Error Handling

```python
from asyncpg.exceptions import PostgresError
import logging

logger = logging.getLogger(__name__)

try:
    summary = await get_campaign_summary('18295')
except PostgresError as e:
    logger.error(f"Database error: {e}")
    # Handle DB error
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    # Handle other errors
```

## Environment Variables

```bash
# Use MS-01 database (production)
USE_MS01_DATABASE=true
POSTGRES_HOST_MS01=192.168.1.34
POSTGRES_PORT_MS01=5432
POSTGRES_DATABASE_MS01=route_poc
POSTGRES_USER_MS01=postgres
POSTGRES_PASSWORD_MS01=<password>

# Use local database (development)
USE_MS01_DATABASE=false
POSTGRES_HOST_LOCAL=localhost
POSTGRES_PORT_LOCAL=5432
POSTGRES_DATABASE_LOCAL=route_poc
```

## Function Categories

**Route API (2):**
- `get_campaign_for_route_api()` - Get playout data for API
- `build_route_api_payload()` - Convert to API format

**Campaign Stats (2):**
- `get_campaign_summary()` - Overall campaign statistics
- `get_campaign_by_date()` - Date-range statistics

**Time-Series (2):**
- `get_hourly_activity()` - Hourly aggregated data
- `get_daily_summary()` - Daily aggregated data

**Route Releases (2):**
- `get_route_release_for_date()` - Get release for date
- `get_all_route_releases()` - List all releases

**Brand Analysis (2):**
- `get_campaign_by_brand()` - Campaign stats by brand
- `split_audience_by_brand()` - Distribute impacts by brand

**Frame Queries (2):**
- `is_frame_active()` - Check frame activity
- `get_frame_campaigns()` - Get campaigns for frame

**Utilities (3):**
- `check_data_freshness()` - Check data age
- `get_date_coverage()` - Check date range
- `get_all_campaigns()` - List campaigns

**Connection (2):**
- `initialize_ms01_database()` - Initialize pool
- `close_ms01_database()` - Close pool

---

**Total: 17 functions**

See `/src/db/README_MS01_HELPERS.md` for detailed documentation.
