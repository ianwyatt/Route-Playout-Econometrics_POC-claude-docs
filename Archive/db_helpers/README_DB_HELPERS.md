# Database Helper Functions

## Overview

The `db_helpers.py` module provides database query functions adapted from the Route Playout Pipeline for use in the POC application. These functions query the PostgreSQL database and are designed for campaign analysis and brand-level reporting.

## Key Features

- **Async-First Design**: All queries use asyncpg for optimal performance
- **Connection Pooling**: Efficient connection management via asyncpg connection pools
- **Environment-Aware**: Automatically switches between primary and secondary databases based on `USE_PRIMARY_DATABASE` env var

## Database Configuration

The module automatically configures database connections based on environment variables:

```python
# Primary Database
USE_PRIMARY_DATABASE=true
POSTGRES_HOST_PRIMARY=your_host_here
POSTGRES_PORT_PRIMARY=5432
POSTGRES_DATABASE_PRIMARY=route_poc
POSTGRES_USER_PRIMARY=postgres
POSTGRES_PASSWORD_PRIMARY=<password>

# Secondary Database (Development/Testing)
USE_PRIMARY_DATABASE=false
POSTGRES_HOST_SECONDARY=localhost
POSTGRES_PORT_SECONDARY=5432
POSTGRES_DATABASE_SECONDARY=route_poc
POSTGRES_USER_SECONDARY=postgres
POSTGRES_PASSWORD_SECONDARY=<password>
```

## Core Functions

### Route API Integration

#### `get_campaign_for_route_api(campaign_id, start_date, end_date)`
**Primary function for Route API data preparation.**

Returns aggregated playout data with one row per frame/campaign/15-minute window.

```python
from src.db import get_campaign_for_route_api, initialize_database

await initialize_database()

# Get campaign data ready for Route API
data = await get_campaign_for_route_api(
    campaign_id='18295',
    start_date='2025-08-01',
    end_date='2025-09-01'
)

# Returns: List[Dict] with keys:
# - frameid: str
# - datetime_from: datetime
# - datetime_to: datetime
# - spot_count: int
# - playout_length: int (seconds)
# - break_length: int (seconds)
```

#### `build_route_api_payload(campaign_data, route_release)`
Convert playout data into Route API request format.

```python
from src.db import build_route_api_payload

# Build payload for Route API POST
payload = build_route_api_payload(data, 'R55')

# Returns: Dict with structure:
# {
#     'route_release_id': 'R55',
#     'frames': [
#         {
#             'frame_id': '1234567890',
#             'windows': [
#                 {
#                     'datetime_from': '2025-08-01T00:00:00',
#                     'datetime_to': '2025-08-01T00:15:00',
#                     'spot_count': 5,
#                     'playout_length': 50,
#                     'break_length': 300
#                 },
#                 ...
#             ]
#         },
#         ...
#     ]
# }
```

### Campaign Summary & Statistics

#### `get_campaign_summary(campaign_id)`
Get high-level campaign statistics for dashboard display.

```python
from src.db import get_campaign_summary

summary = await get_campaign_summary('18295')

# Returns: Dict with keys:
# - total_frames: int
# - days_active: int
# - total_playouts: int
# - start_date: datetime
# - end_date: datetime
# - avg_spot_length: float
# - avg_spots_per_window: float
```

#### `get_campaign_by_date(campaign_id, start_date, end_date)`
Get campaign summary for a specific date range.

```python
summary = await get_campaign_by_date(
    '18295', '2025-08-01', '2025-09-01'
)

# Returns: Dict with keys:
# - frames: int
# - total_windows: int
# - total_spots: int
# - avg_spot_length: float
```

### Time-Series Data

#### `get_hourly_activity(campaign_id, start_date, end_date)`
Get hourly aggregated activity for time-series charts.

```python
from src.db import get_hourly_activity

activity = await get_hourly_activity(
    '18295', '2025-08-01', '2025-08-02'
)

# Returns: List[Dict] with keys:
# - hour: datetime (truncated to hour)
# - active_windows: int
# - total_spots: int
```

#### `get_daily_summary(campaign_id, start_date, end_date)`
Get daily summary for calendar view or daily breakdown chart.

```python
daily = await get_daily_summary(
    '18295', '2025-08-01', '2025-09-01'
)

# Returns: List[Dict] with keys:
# - date: date
# - frames: int
# - windows: int
# - spots: int
```

### Route Release Integration

#### `get_route_release_for_date(playout_date)`
Determine which Route release to use for a given date.

```python
from src.db import get_route_release_for_date

release = await get_route_release_for_date('2025-09-15')

# Returns: Dict with keys:
# - release_number: str (e.g., 'R55')
# - name: str (e.g., 'Q2 2025')
```

#### `get_all_route_releases()`
Get all Route releases with their trading periods.

```python
releases = await get_all_route_releases()

# Returns: List[Dict] with keys:
# - release_number: str
# - name: str
# - trading_period_start: date
# - trading_period_end: date
```

### Brand-Level Reporting

#### `get_campaign_by_brand(campaign_id, start_date, end_date)`
Break down campaign performance by brand.

```python
from src.db import get_campaign_by_brand

brands = await get_campaign_by_brand(
    '18699', '2025-08-20', '2025-08-25'
)

# Returns: List[Dict] with keys:
# - spacebrandid: str
# - unique_frames: int
# - active_windows: int
# - total_spots: int
```

#### `split_audience_by_brand(frame_id, campaign_id, window_start, total_impacts)`
**Use AFTER Route API call to distribute impacts across brands.**

```python
from src.db import split_audience_by_brand
from datetime import datetime

# After getting 10,000 impacts from Route API
brand_split = await split_audience_by_brand(
    frame_id='1234859642',
    campaign_id='18699',
    window_start=datetime(2025, 8, 23, 11, 15, 0),
    total_impacts=10000.0
)

# Returns: List[Dict] with keys:
# - brand_id: str
# - spots: int
# - proportion: float
# - impacts: float (total_impacts * proportion)
```

### Frame-Level Queries

#### `is_frame_active(frame_id, date_str)`
Check if a frame has playout data on a given date.

```python
active = await is_frame_active('1234567890', '2025-08-15')
# Returns: bool
```

#### `get_frame_campaigns(frame_id, start_date, end_date)`
Get all campaigns that played on a specific frame.

```python
campaigns = await get_frame_campaigns(
    '1234567890', '2025-08-01', '2025-09-01'
)

# Returns: List[Dict] with keys:
# - buyercampaignref: str
# - windows: int
# - total_spots: int
# - first_window: datetime
# - last_window: datetime
```

### Utility Functions

#### `check_data_freshness()`
Check when data was last refreshed.

```python
freshness = await check_data_freshness()

# Returns: Dict with keys:
# - latest_window: datetime
# - latest_playout: datetime
# - hours_old: float
```

#### `get_date_coverage()`
Get date range and coverage of playout data.

```python
coverage = await get_date_coverage()

# Returns: Dict with keys:
# - start_date: date
# - end_date: date
# - days_with_data: int
```

#### `get_all_campaigns(limit=100)`
Get list of all available campaigns.

```python
campaigns = await get_all_campaigns(limit=50)

# Returns: List[Dict] with keys:
# - buyercampaignref: str
# - total_frames: int
# - total_spots: int
# - start_date: datetime
# - end_date: datetime
```

## Connection Management

### Initialize Database

Always initialize the database connection pool before using any query functions:

```python
from src.db import initialize_database

await initialize_database()
```

### Close Database

Close the connection pool when done (e.g., at application shutdown):

```python
from src.db import close_database

await close_database()
```

## Complete Usage Example

See `/examples/db_helpers_example.py` for a complete working example:

```python
import asyncio
from src.db import (
    initialize_database,
    close_database,
    get_campaign_summary,
    get_campaign_for_route_api,
    get_route_release_for_date,
    build_route_api_payload
)

async def main():
    # Initialize
    await initialize_database()

    try:
        # Get campaign summary
        summary = await get_campaign_summary('18295')
        print(f"Campaign has {summary['total_frames']} frames")

        # Get data for Route API
        data = await get_campaign_for_route_api(
            '18295', '2025-08-01', '2025-09-01'
        )

        # Get Route release
        release = await get_route_release_for_date('2025-08-01')

        # Build API payload
        payload = build_route_api_payload(data, release['release_number'])

    finally:
        # Cleanup
        await close_database()

if __name__ == "__main__":
    asyncio.run(main())
```

## Database Schema Requirements

The following materialized views must exist in the database:

### `mv_playout_15min`
Aggregated playout data at 15-minute intervals.

Required columns:
- `frameid`: Frame identifier
- `buyercampaignref`: Campaign reference
- `time_window_start`: Start of 15-minute window
- `spot_count`: Number of spots in window
- `playout_length_seconds`: Total playout duration
- `break_length_seconds`: Total break duration
- `latest_playout`: Timestamp of latest playout

### `mv_playout_15min_brands`
Brand-level playout data at 15-minute intervals.

Required columns:
- `frameid`: Frame identifier
- `buyercampaignref`: Campaign reference
- `spacebrandid`: Brand identifier
- `time_window_start`: Start of 15-minute window
- `spots_for_brand`: Number of spots for this brand

### `route_releases`
Route release metadata.

Required columns:
- `release_number`: Release identifier (e.g., 'R55')
- `name`: Release name (e.g., 'Q2 2025')
- `trading_period_start`: Trading period start date
- `trading_period_end`: Trading period end date

## Performance Considerations

1. **Connection Pooling**: The module uses asyncpg connection pooling (1-10 connections)
2. **Query Optimization**: All queries use parameterized queries for PostgreSQL query plan caching
3. **Materialized Views**: Queries target pre-aggregated materialized views for optimal performance
4. **Async Operations**: All I/O operations are async for maximum concurrency

## Error Handling

All functions propagate database errors. Recommended error handling:

```python
from asyncpg.exceptions import PostgresError

try:
    summary = await get_campaign_summary('18295')
except PostgresError as e:
    logger.error(f"Database error: {e}")
    # Handle error appropriately
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    # Handle error appropriately
```

## Integration with POC

The db_helpers module integrates seamlessly with existing POC components:

- **Config System**: Uses POC's environment variable configuration
- **Database Module**: Exported via `src.db.__init__` for easy imports
- **Logging**: Uses POC's standard logging configuration
- **Error Handling**: Compatible with POC's error handling patterns

## Migration from Pipeline

Key changes from the original pipeline code:

1. **Environment Integration**: Uses POC's environment variable structure
2. **Connection Management**: Uses POC's database connection patterns
3. **Logging**: Uses POC's logging configuration
4. **Error Handling**: Adapted to POC's error handling approach
5. **Import Paths**: Updated for POC package structure

## Testing

Run the example file to test all functions:

```bash
python examples/db_helpers_example.py
```

Expected output:
- Campaign summary statistics
- Route API payload generation
- Hourly activity charts
- Brand-level impact distribution
- Data freshness check
- Available campaigns list

## Future Enhancements

Potential improvements for production:

1. **Query Caching**: Add TTL caching for frequently accessed queries
2. **Batch Operations**: Add batch query support for multiple campaigns
3. **Performance Monitoring**: Add query timing and performance metrics
4. **Connection Retries**: Add automatic retry logic for transient failures
5. **Read Replicas**: Support read replica routing for heavy queries
