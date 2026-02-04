# Integration Guide - MS-01 Migration

**Date**: 2025-10-17
**Audience**: Developers integrating MS-01 code into POC application
**Status**: Step-by-step instructions with working examples

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Database Helper Functions](#database-helper-functions)
3. [Brand Split Service](#brand-split-service)
4. [Route Release Lookups](#route-release-lookups)
5. [Common Use Cases](#common-use-cases)
6. [Error Handling](#error-handling)

---

## Quick Start

### 1. Setup Database (One-Time)

```bash
# Ensure MS-01 or local database is accessible
# Check .env file has correct credentials

# Populate Route releases (R54-R61)
python scripts/setup_route_releases.py
```

**Expected Output**:
```
✅ Database connection pool initialized
✅ Route releases table created successfully
✅ Inserted/updated release R54 with ID 1
✅ Inserted/updated release R55 with ID 2
...
📊 Successfully loaded 8 releases
```

### 2. Test Connection

```bash
# Verify MS-01 helpers work
python examples/ms01_helpers_example.py
```

**Expected Output**:
```
=== MS-01 Database Helper Examples ===

Example 1: Get campaign for Route API
Campaign ID: 18295, Date Range: 2025-08-01 to 2025-09-01
Found 4,182 windows for Route API
First window: Frame 1234567890 at 2025-08-01 00:00:00
  10 spots, 150s playout length, 300s break length
...
```

### 3. Switch Databases

```bash
# Edit .env file
USE_MS01_DATABASE=true   # For MS-01 production
USE_MS01_DATABASE=false  # For local dev/demo

# Restart application for changes to take effect
```

---

## Database Helper Functions

### Import and Initialize

```python
import asyncio
from datetime import date
from src.db import ms01_helpers

# Initialize connection pool (once at startup)
async def startup():
    await ms01_helpers.initialize_ms01_database()
    print("✅ MS-01 database ready")

# Run at application startup
asyncio.run(startup())
```

### Use Case 1: Get Campaign Data for Route API

**Scenario**: User enters campaign ID and date range, need to call Route API

```python
from src.db.ms01_helpers import get_campaign_for_route_api, build_route_api_payload
from src.db.route_releases import get_releases_for_date_range
from datetime import date

async def process_campaign_for_route_api(campaign_id: str, start_date: str, end_date: str):
    """
    Get campaign playout data and prepare Route API payload.

    Args:
        campaign_id: Campaign ID (e.g., '18295')
        start_date: Start date (e.g., '2025-08-01')
        end_date: End date (e.g., '2025-09-01')

    Returns:
        Route API payload ready to POST
    """
    # Step 1: Get campaign data from MS-01
    campaign_data = await get_campaign_for_route_api(
        campaign_id=campaign_id,
        start_date=start_date,
        end_date=end_date
    )

    if not campaign_data:
        raise ValueError(f"No playout data found for campaign {campaign_id}")

    print(f"✅ Found {len(campaign_data)} 15-minute windows")

    # Step 2: Determine Route release(s) for date range
    releases = await get_releases_for_date_range(
        date.fromisoformat(start_date),
        date.fromisoformat(end_date)
    )

    if not releases:
        raise ValueError(f"No Route release found for dates {start_date} to {end_date}")

    # Use most recent release if multiple (typical for campaigns spanning release boundaries)
    route_release = releases[-1].release_number
    print(f"✅ Using Route release: {route_release}")

    # Step 3: Build Route API payload
    payload = build_route_api_payload(campaign_data, route_release)

    print(f"✅ Payload ready: {len(payload['frames'])} frames")

    return payload

# Usage
payload = await process_campaign_for_route_api('18295', '2025-08-01', '2025-09-01')

# Now POST to Route API
# response = requests.post('https://route.mediatelapi.co.uk/rest/process/playout', json=payload)
```

### Use Case 2: Display Campaign Summary

**Scenario**: Show campaign overview on dashboard

```python
from src.db.ms01_helpers import get_campaign_summary

async def display_campaign_dashboard(campaign_id: str):
    """Display campaign summary for dashboard."""
    summary = await get_campaign_summary(campaign_id)

    if not summary:
        print(f"❌ Campaign {campaign_id} not found")
        return

    print(f"📊 Campaign {campaign_id} Summary")
    print(f"   Frames: {summary['total_frames']}")
    print(f"   Days Active: {summary['days_active']}")
    print(f"   Total Playouts: {summary['total_playouts']:,}")
    print(f"   Date Range: {summary['start_date']} to {summary['end_date']}")
    print(f"   Avg Spot Length: {summary['avg_spot_length']}s")
    print(f"   Avg Spots/Window: {summary['avg_spots_per_window']}")

# Usage
await display_campaign_dashboard('18295')
```

**Output**:
```
📊 Campaign 18295 Summary
   Frames: 145
   Days Active: 31
   Total Playouts: 12,450
   Date Range: 2025-08-01 to 2025-08-31
   Avg Spot Length: 15.2s
   Avg Spots/Window: 2.8
```

### Use Case 3: Time-Series Chart Data

**Scenario**: Generate hourly activity chart for campaign

```python
from src.db.ms01_helpers import get_hourly_activity
import pandas as pd

async def generate_hourly_chart_data(campaign_id: str, start_date: str, end_date: str):
    """Get hourly activity data for time-series chart."""
    hourly_data = await get_hourly_activity(campaign_id, start_date, end_date)

    # Convert to pandas DataFrame for charting
    df = pd.DataFrame(hourly_data)

    # Format for chart library (e.g., Chart.js)
    chart_data = {
        'labels': [row['hour'].strftime('%Y-%m-%d %H:00') for row in hourly_data],
        'datasets': [{
            'label': 'Spots per Hour',
            'data': [row['total_spots'] for row in hourly_data]
        }]
    }

    return chart_data

# Usage
chart_data = await generate_hourly_chart_data('18295', '2025-08-01', '2025-08-07')
# Pass to frontend charting library
```

### Use Case 4: Brand-Level Reporting

**Scenario**: Show campaign breakdown by brand

```python
from src.db.ms01_helpers import get_campaign_by_brand

async def display_brand_breakdown(campaign_id: str, start_date: str, end_date: str):
    """Display campaign performance by brand."""
    brands = await get_campaign_by_brand(campaign_id, start_date, end_date)

    if not brands:
        print(f"ℹ️  Campaign {campaign_id} has no brand data (single-brand campaign)")
        return

    print(f"📊 Brand Breakdown for Campaign {campaign_id}")
    print(f"   Total Brands: {len(brands)}")
    print()

    for brand in brands:
        print(f"   Brand {brand['spacebrandid']}:")
        print(f"     Frames: {brand['unique_frames']}")
        print(f"     Windows: {brand['active_windows']}")
        print(f"     Spots: {brand['total_spots']:,}")
        print()

# Usage
await display_brand_breakdown('18699', '2025-08-20', '2025-08-25')
```

**Output**:
```
📊 Brand Breakdown for Campaign 18699
   Total Brands: 2

   Brand 21143:
     Frames: 8
     Windows: 120
     Spots: 360

   Brand 21146:
     Frames: 8
     Windows: 40
     Spots: 120
```

---

## Brand Split Service

### Initialize Service

```python
from src.services.brand_split_service import BrandSplitService

# Create service instance
brand_service = BrandSplitService(cache_ttl=3600)  # 1 hour cache

# Initialize (creates connection pool)
await brand_service.initialize()

# Always cleanup when done
await brand_service.cleanup()
```

### Use Case 5: Split Route API Response by Brand

**Scenario**: User gets Route API response, need brand-level attribution

```python
from src.services.brand_split_service import BrandSplitService

async def attribute_campaign_to_brands(route_api_response: dict):
    """
    Take Route API response and split impacts across brands.

    Args:
        route_api_response: Full Route API playout response

    Returns:
        Brand-level aggregation with impacts per brand
    """
    service = BrandSplitService()
    await service.initialize()

    try:
        # Process entire Route API response
        brand_aggregation = await service.aggregate_brand_impacts(route_api_response)

        print(f"✅ Campaign: {brand_aggregation['campaign_id']}")
        print(f"   Total Impacts: {brand_aggregation['total_impacts']:,}")
        print(f"   Windows Processed: {brand_aggregation['windows_processed']}")
        print(f"   Processing Time: {brand_aggregation['processing_time_ms']:.2f}ms")
        print()

        for brand_id, data in brand_aggregation['brands'].items():
            print(f"   Brand {brand_id}:")
            print(f"     Impacts: {data['total_impacts']:,.0f} ({data['proportion']:.1%})")
            print(f"     Windows: {data['windows']}")
            print()

        return brand_aggregation

    finally:
        await service.cleanup()

# Usage
route_response = {
    'campaign_id': '18699',
    'frames': [
        {
            'frame_id': 1234859642,
            'campaign_id': '18699',
            'windows': [
                {
                    'window_start': '2025-08-23 11:15:00',
                    'impacts': 1000000  # 1 million impacts from Route API
                },
                {
                    'window_start': '2025-08-23 11:30:00',
                    'impacts': 1200000
                }
            ]
        }
    ]
}

brand_results = await attribute_campaign_to_brands(route_response)
```

**Output**:
```
✅ Campaign: 18699
   Total Impacts: 2,200,000
   Windows Processed: 2
   Processing Time: 45.23ms

   Brand 21143:
     Impacts: 1,650,000 (75.0%)
     Windows: 2

   Brand 21146:
     Impacts: 550,000 (25.0%)
     Windows: 2
```

### Use Case 6: Single Window Brand Split

**Scenario**: Split impacts for one 15-minute window

```python
from src.services.brand_split_service import BrandSplitService
from datetime import datetime

async def split_window_by_brand(
    frame_id: int,
    campaign_id: str,
    window_start: datetime,
    total_impacts: float
):
    """Split impacts for single window across brands."""
    service = BrandSplitService()
    await service.initialize()

    try:
        brand_impacts = await service.split_audience_by_brand(
            frame_id=frame_id,
            campaign_id=campaign_id,
            window_start=window_start,
            total_impacts=total_impacts
        )

        if not brand_impacts:
            print("ℹ️  Single-brand window, no split needed")
            return {campaign_id: total_impacts}

        print(f"✅ Split {total_impacts:,} impacts across {len(brand_impacts)} brands:")
        for brand_id, impacts in brand_impacts.items():
            proportion = impacts / total_impacts if total_impacts > 0 else 0
            print(f"   Brand {brand_id}: {impacts:,.0f} ({proportion:.1%})")

        return brand_impacts

    finally:
        await service.cleanup()

# Usage
brand_impacts = await split_window_by_brand(
    frame_id=1234859642,
    campaign_id='18699',
    window_start=datetime(2025, 8, 23, 11, 15),
    total_impacts=1000000
)
```

### Use Case 7: Pre-Flight Brand Analysis

**Scenario**: Check if campaign has multiple brands before processing

```python
from src.services.brand_split_service import BrandSplitService
from datetime import date

async def analyze_campaign_brands(campaign_id: str, start_date: date, end_date: date):
    """Analyze brand structure of campaign."""
    service = BrandSplitService()
    await service.initialize()

    try:
        # Get all brands in campaign
        brands = await service.get_campaign_brands(campaign_id, start_date, end_date)

        if not brands:
            print(f"ℹ️  Campaign {campaign_id} is single-brand")
            return {'is_multi_brand': False}

        print(f"📊 Campaign {campaign_id} has {len(brands)} brands:")
        for brand in brands:
            print(f"   Brand {brand['spacebrandid']}:")
            print(f"     Total Spots: {brand['total_spots']:,}")
            print(f"     Frames: {brand['frame_count']}")
            print(f"     First Window: {brand['first_window']}")
            print(f"     Last Window: {brand['last_window']}")
            print()

        # Check for multi-brand windows (complexity indicator)
        multi_brand_windows = await service.get_multi_brand_windows(
            campaign_id, start_date, end_date
        )

        if multi_brand_windows:
            print(f"⚠️  Found {len(multi_brand_windows)} windows with multiple brands")
            print(f"   Most complex: {multi_brand_windows[0]['brand_count']} brands in one window")

        return {
            'is_multi_brand': True,
            'brand_count': len(brands),
            'multi_brand_windows': len(multi_brand_windows),
            'brands': brands
        }

    finally:
        await service.cleanup()

# Usage
analysis = await analyze_campaign_brands(
    '18699',
    date(2025, 8, 20),
    date(2025, 8, 25)
)

if analysis['is_multi_brand']:
    print(f"⚠️  Campaign requires brand split (uses {analysis['brand_count']} brands)")
else:
    print("✅ Campaign is single-brand, no split needed")
```

---

## Route Release Lookups

### Use Case 8: Determine Route Release for Campaign

**Scenario**: User queries campaign, need to know which Route release to use

```python
from src.db.route_releases import get_release_for_date, validate_release_coverage
from datetime import date

async def determine_route_release_for_campaign(start_date: str, end_date: str):
    """
    Determine which Route release(s) to use for campaign date range.

    Args:
        start_date: Campaign start (YYYY-MM-DD)
        end_date: Campaign end (YYYY-MM-DD)

    Returns:
        Dict with release info and validation
    """
    start = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)

    # Validate coverage
    coverage = await validate_release_coverage(start, end)

    if not coverage['has_coverage']:
        print(f"❌ Date range has gaps in Route release coverage:")
        print(f"   {coverage['message']}")
        for gap_start, gap_end in coverage['gaps']:
            print(f"   Gap: {gap_start} to {gap_end}")
        raise ValueError("Incomplete Route release coverage for date range")

    print(f"✅ Complete Route release coverage:")
    print(f"   {coverage['coverage_percent']}% coverage")
    print(f"   {len(coverage['releases'])} release(s) needed")
    print()

    for release in coverage['releases']:
        print(f"   {release.release_number} ({release.name}):")
        print(f"     Trading Period: {release.trading_period_start} to {release.trading_period_end}")
        print()

    return {
        'releases': coverage['releases'],
        'primary_release': coverage['releases'][-1].release_number,  # Use most recent
        'coverage_complete': True
    }

# Usage
release_info = await determine_route_release_for_campaign('2025-08-01', '2025-09-01')
print(f"Use Route release: {release_info['primary_release']}")
```

**Output**:
```
✅ Complete Route release coverage:
   100.0% coverage
   1 release(s) needed

   R55 (Q2 2025):
     Trading Period: 2025-06-30 to 2025-09-28

Use Route release: R55
```

### Use Case 9: Lookup Release for Specific Date

**Scenario**: Need release number for specific playout date

```python
from src.db.route_releases import get_release_for_date
from datetime import date

async def get_release_for_playout_date(playout_date_str: str):
    """Get Route release for specific date."""
    playout_date = date.fromisoformat(playout_date_str)

    release = await get_release_for_date(playout_date)

    if not release:
        print(f"❌ No Route release found for {playout_date}")
        print("   Date may be outside available release coverage")
        return None

    print(f"✅ Date {playout_date} uses:")
    print(f"   Release: {release.release_number}")
    print(f"   Name: {release.name}")
    print(f"   Trading Period: {release.trading_period_start} to {release.trading_period_end}")

    return release.release_number

# Usage
release_number = await get_release_for_playout_date('2025-07-15')
# Output: R55
```

### Use Case 10: List Available Releases

**Scenario**: Show dropdown of available Route releases in UI

```python
from src.db.route_releases import get_all_releases

async def get_release_options_for_ui():
    """Get list of releases for UI dropdown."""
    releases = await get_all_releases()

    # Format for dropdown
    options = []
    for release in releases:
        options.append({
            'value': release.release_number,
            'label': f"{release.release_number} - {release.name}",
            'start_date': release.trading_period_start.isoformat(),
            'end_date': release.trading_period_end.isoformat()
        })

    return options

# Usage
dropdown_options = await get_release_options_for_ui()

# Output:
# [
#     {'value': 'R54', 'label': 'R54 - Q1 2025', 'start_date': '2025-04-07', ...},
#     {'value': 'R55', 'label': 'R55 - Q2 2025', 'start_date': '2025-06-30', ...},
#     ...
# ]
```

---

## Common Use Cases

### End-to-End: Campaign Query to Route API to Brand Split

```python
from src.db.ms01_helpers import get_campaign_for_route_api, build_route_api_payload
from src.db.route_releases import get_releases_for_date_range
from src.services.brand_split_service import BrandSplitService
import requests
from datetime import date

async def process_campaign_end_to_end(campaign_id: str, start_date: str, end_date: str):
    """
    Complete workflow: Query campaign → Route API → Brand split → Export.
    """
    print(f"📊 Processing Campaign {campaign_id}")
    print(f"   Date Range: {start_date} to {end_date}")
    print()

    # Step 1: Get campaign playout data from MS-01
    print("Step 1: Fetching campaign data from MS-01...")
    campaign_data = await get_campaign_for_route_api(campaign_id, start_date, end_date)

    if not campaign_data:
        raise ValueError(f"No data found for campaign {campaign_id}")

    print(f"✅ Found {len(campaign_data)} 15-minute windows")
    print()

    # Step 2: Determine Route release
    print("Step 2: Determining Route release...")
    releases = await get_releases_for_date_range(
        date.fromisoformat(start_date),
        date.fromisoformat(end_date)
    )
    route_release = releases[-1].release_number
    print(f"✅ Using Route release: {route_release}")
    print()

    # Step 3: Build Route API payload
    print("Step 3: Building Route API payload...")
    payload = build_route_api_payload(campaign_data, route_release)
    print(f"✅ Payload ready: {len(payload['frames'])} frames")
    print()

    # Step 4: Call Route API
    print("Step 4: Calling Route API...")
    route_api_url = "https://route.mediatelapi.co.uk/rest/process/playout"
    headers = {
        'x-api-key': 'your-api-key',
        'Authorization': 'your-auth-token'
    }

    response = requests.post(route_api_url, json=payload, headers=headers, timeout=1800)

    if response.status_code != 200:
        raise ValueError(f"Route API error: {response.status_code}")

    route_response = response.json()
    print(f"✅ Route API returned impacts data")
    print()

    # Step 5: Split by brand (if multi-brand campaign)
    print("Step 5: Splitting impacts by brand...")
    brand_service = BrandSplitService()
    await brand_service.initialize()

    try:
        brand_results = await brand_service.aggregate_brand_impacts(route_response)

        print(f"✅ Brand attribution complete:")
        print(f"   Total Impacts: {brand_results['total_impacts']:,}")
        print(f"   Brands: {len(brand_results['brands'])}")
        print(f"   Processing Time: {brand_results['processing_time_ms']:.2f}ms")
        print()

        for brand_id, data in brand_results['brands'].items():
            print(f"   Brand {brand_id}:")
            print(f"     Impacts: {data['total_impacts']:,.0f} ({data['proportion']:.1%})")
            print(f"     Windows: {data['windows']}")
        print()

        return {
            'campaign_id': campaign_id,
            'route_release': route_release,
            'total_impacts': brand_results['total_impacts'],
            'brand_impacts': brand_results['brands']
        }

    finally:
        await brand_service.cleanup()

# Usage
results = await process_campaign_end_to_end('18699', '2025-08-20', '2025-08-25')

# Export results
import pandas as pd
df = pd.DataFrame([
    {
        'campaign_id': results['campaign_id'],
        'brand_id': brand_id,
        'impacts': data['total_impacts'],
        'proportion': data['proportion'],
        'windows': data['windows']
    }
    for brand_id, data in results['brand_impacts'].items()
])
df.to_csv('campaign_brand_impacts.csv', index=False)
print("✅ Results exported to campaign_brand_impacts.csv")
```

---

## Error Handling

### Database Connection Errors

```python
from src.db.ms01_helpers import initialize_ms01_database
import logging

logger = logging.getLogger(__name__)

async def safe_database_init():
    """Initialize database with error handling."""
    try:
        await initialize_ms01_database()
        logger.info("✅ Database initialized successfully")
        return True

    except ConnectionError as e:
        logger.error(f"❌ Database connection failed: {e}")
        logger.error("   Check VPN/network access to MS-01")
        logger.error("   Or set USE_MS01_DATABASE=false to use local database")
        return False

    except Exception as e:
        logger.error(f"❌ Unexpected database error: {e}")
        return False

# Usage
if not await safe_database_init():
    # Fallback to CSV mode or exit
    print("Falling back to CSV-based mode")
```

### Query Errors

```python
from src.db.ms01_helpers import get_campaign_for_route_api
import logging

logger = logging.getLogger(__name__)

async def safe_campaign_query(campaign_id: str, start_date: str, end_date: str):
    """Query campaign with error handling."""
    try:
        data = await get_campaign_for_route_api(campaign_id, start_date, end_date)

        if not data:
            logger.warning(f"No data found for campaign {campaign_id}")
            return None

        return data

    except ValueError as e:
        logger.error(f"Invalid input: {e}")
        return None

    except Exception as e:
        logger.error(f"Query failed: {e}")
        return None

# Usage
data = await safe_campaign_query('18295', '2025-08-01', '2025-09-01')
if data is None:
    print("Campaign query failed")
```

### Route Release Not Found

```python
from src.db.route_releases import get_release_for_date, ReleaseNotFoundError
from datetime import date

async def safe_release_lookup(playout_date_str: str):
    """Lookup Route release with error handling."""
    try:
        playout_date = date.fromisoformat(playout_date_str)
        release = await get_release_for_date(playout_date)

        if not release:
            raise ReleaseNotFoundError(f"No release found for {playout_date}")

        return release.release_number

    except ValueError as e:
        print(f"❌ Invalid date format: {e}")
        return None

    except ReleaseNotFoundError as e:
        print(f"❌ {e}")
        print("   Date may be outside Route release coverage")
        print("   Available releases: R54-R61 (Q1 2025 - Q4 2026)")
        return None

# Usage
release = await safe_release_lookup('2025-07-15')
if release:
    print(f"✅ Use release: {release}")
```

---

## Performance Tips

### 1. Reuse Service Instances

**Bad** (creates new pool each time):
```python
async def process_many_campaigns(campaign_ids):
    for campaign_id in campaign_ids:
        service = BrandSplitService()
        await service.initialize()
        result = await service.split_audience_by_brand(...)
        await service.cleanup()  # Destroys pool!
```

**Good** (reuses pool):
```python
async def process_many_campaigns(campaign_ids):
    service = BrandSplitService()
    await service.initialize()

    try:
        for campaign_id in campaign_ids:
            result = await service.split_audience_by_brand(...)
    finally:
        await service.cleanup()
```

### 2. Batch Queries

**Bad** (separate queries):
```python
for campaign_id in campaign_ids:
    summary = await get_campaign_summary(campaign_id)
```

**Good** (single query):
```python
# Use get_all_campaigns() then filter
all_campaigns = await get_all_campaigns(limit=1000)
campaign_dict = {c['buyercampaignref']: c for c in all_campaigns}
```

### 3. Cache Results

```python
from functools import lru_cache

@lru_cache(maxsize=100)
async def cached_release_lookup(date_str: str):
    """Cache release lookups (already cached in DB layer, but can add app-level cache)."""
    return await get_release_for_date(date.fromisoformat(date_str))
```

---

## Summary

### Key Integration Points

1. **MS-01 Helpers**: Primary interface to database
2. **Brand Split Service**: Multi-brand attribution
3. **Route Releases**: Automatic release determination
4. **Database Switching**: One env var to switch databases

### Next Steps

1. Copy code examples into your application
2. Test with your campaign IDs
3. Integrate into UI workflows
4. Add error handling for production

### Getting Help

- See `05_TESTING_VALIDATION.md` for validation scripts
- See `08_KNOWN_ISSUES.md` for common problems and solutions
- Check examples in `/examples/` and `/scripts/` directories

---

**Prepared By**: Claude Code Agent Team
**Date**: 2025-10-17
**Status**: Ready for Integration
