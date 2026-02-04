# ABOUTME: Database helper functions for PostgreSQL queries adapted from pipeline
# ABOUTME: Provides optimised query functions for campaign data, Route API integration, and brand-level reporting

import os
import logging
from datetime import datetime, date
from typing import List, Dict, Optional, Any
from contextlib import asynccontextmanager
import asyncpg
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """
    PostgreSQL database connection manager for POC application.

    Manages connection pooling and query execution for the configured database
    containing playout data and materialised views.
    """

    def __init__(self):
        """Initialise connection pool configuration."""
        self.connection_pool = None
        self._db_config = self._get_db_config()

    def _get_db_config(self) -> Dict[str, Any]:
        """
        Get database configuration from environment variables.

        Returns:
            Dict with database connection parameters
        """
        use_primary = os.getenv("USE_PRIMARY_DATABASE", "true").lower() == "true"

        if use_primary:
            host = os.getenv("POSTGRES_HOST_PRIMARY", "")
            if not host:
                raise ValueError(
                    "POSTGRES_HOST_PRIMARY environment variable "
                    "must be set for primary database connection"
                )
            return {
                "host": host,
                "port": int(os.getenv("POSTGRES_PORT_PRIMARY", "5432")),
                "database": os.getenv("POSTGRES_DATABASE_PRIMARY", "route_poc"),
                "user": os.getenv("POSTGRES_USER_PRIMARY", "postgres"),
                "password": os.getenv("POSTGRES_PASSWORD_PRIMARY", ""),
            }
        else:
            return {
                "host": os.getenv("POSTGRES_HOST_SECONDARY", "localhost"),
                "port": int(os.getenv("POSTGRES_PORT_SECONDARY", "5432")),
                "database": os.getenv("POSTGRES_DATABASE_SECONDARY", "route_poc"),
                "user": os.getenv("POSTGRES_USER_SECONDARY", "postgres"),
                "password": os.getenv("POSTGRES_PASSWORD_SECONDARY", ""),
            }

    async def initialize_connection_pool(self):
        """Initialise async database connection pool."""
        if self.connection_pool is not None:
            logger.debug("Connection pool already initialised")
            return

        try:
            self.connection_pool = await asyncpg.create_pool(
                **self._db_config, min_size=1, max_size=10, command_timeout=60
            )
            db_host = self._db_config["host"]
            db_name = self._db_config["database"]
            logger.info(f"Database connection pool initialised ({db_host}/{db_name})")
        except Exception as e:
            logger.error(f"Failed to initialise connection pool: {e}")
            raise

    async def get_pool(self) -> asyncpg.Pool:
        """
        Get connection pool, initialising if necessary.

        Returns:
            asyncpg.Pool instance
        """
        if self.connection_pool is None:
            await self.initialize_connection_pool()
        return self.connection_pool

    async def initialize(self):
        """Initialise database connection (alias for initialize_connection_pool)."""
        await self.initialize_connection_pool()

    async def close(self):
        """Close database connection (alias for close_connection_pool)."""
        await self.close_connection_pool()

    async def close_connection_pool(self):
        """Close database connection pool."""
        if self.connection_pool:
            await self.connection_pool.close()
            self.connection_pool = None
            logger.info("Database connection pool closed")

    @asynccontextmanager
    async def acquire_connection(self):
        """
        Acquire connection from pool with context manager.

        Yields:
            asyncpg.Connection
        """
        if not self.connection_pool:
            await self.initialize_connection_pool()

        async with self.connection_pool.acquire() as connection:
            yield connection

    async def execute_query(self, query: str, params: tuple = None) -> List[Dict]:
        """
        Execute query and return results as list of dicts.

        Args:
            query: SQL query string
            params: Query parameters tuple

        Returns:
            List of dicts (column_name: value)
        """
        if not self.connection_pool:
            await self.initialize_connection_pool()

        async with self.connection_pool.acquire() as connection:
            try:
                if params:
                    rows = await connection.fetch(query, *params)
                else:
                    rows = await connection.fetch(query)

                # Convert asyncpg Records to dicts
                results = [dict(row) for row in rows]
                return results

            except Exception as e:
                logger.error(f"Query execution failed: {e}")
                logger.error(f"Query: {query[:200]}...")
                if params:
                    logger.error(f"Params: {params}")
                raise


# Global database instance
_db = DatabaseConnection()


async def initialize_database():
    """Initialise the database connection pool."""
    await _db.initialize_connection_pool()


async def close_database():
    """Close the database connection pool."""
    await _db.close_connection_pool()


# ==============================================================================
# ROUTE API DATA RETRIEVAL
# ==============================================================================


async def get_campaign_for_route_api(
    campaign_id: str, start_date: str, end_date: str
) -> List[Dict]:
    """
    Get aggregated playout data for Route API calls.

    This is the PRIMARY function for Route API integration.
    Returns ONE row per frame/campaign/15-minute window.

    Args:
        campaign_id: Campaign reference (e.g., '18295')
        start_date: Start date (e.g., '2025-08-01')
        end_date: End date (e.g., '2025-09-01')

    Returns:
        List of dicts with keys:
            - frameid: str
            - datetime_from: datetime
            - datetime_to: datetime
            - spot_count: int
            - playout_length: int (seconds)
            - break_length: int (seconds)

    Example:
        >>> data = await get_campaign_for_route_api('18295', '2025-08-01', '2025-09-01')
        >>> print(f"Found {len(data)} windows")
        Found 4,182 windows
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
        WHERE buyercampaignref = $1
          AND time_window_start >= $2
          AND time_window_start < $3
        ORDER BY frameid, time_window_start
    """

    return await _db.execute_query(query, (campaign_id, start_date, end_date))


def build_route_api_payload(campaign_data: List[Dict], route_release: str) -> Dict:
    """
    Convert aggregated playout data into Route API request format.

    Args:
        campaign_data: Output from get_campaign_for_route_api()
        route_release: Route release number (e.g., 'R55')

    Returns:
        Dict ready for Route API POST request

    Example:
        >>> route_data = await get_campaign_for_route_api('18295', '2025-08-01', '2025-09-02')
        >>> payload = build_route_api_payload(route_data, 'R55')
        >>> # POST payload to Route API
    """
    # Group by frame for batch processing
    frames = {}
    for record in campaign_data:
        frame_id = record["frameid"]
        if frame_id not in frames:
            frames[frame_id] = []

        frames[frame_id].append(
            {
                "datetime_from": record["datetime_from"].isoformat(),
                "datetime_to": record["datetime_to"].isoformat(),
                "spot_count": record["spot_count"],
                "playout_length": record["playout_length"],
                "break_length": record["break_length"],
            }
        )

    # Build Route API payload
    payload = {"route_release_id": route_release, "frames": []}

    for frame_id, windows in frames.items():
        payload["frames"].append({"frame_id": frame_id, "windows": windows})

    return payload


# ==============================================================================
# CAMPAIGN SUMMARY & STATISTICS
# ==============================================================================


async def get_campaign_summary(campaign_id: str) -> Optional[Dict]:
    """
    Get high-level campaign statistics for dashboard display.

    Args:
        campaign_id: Campaign reference

    Returns:
        Dict with campaign summary:
            - total_frames: int
            - days_active: int
            - total_playouts: int
            - start_date: datetime
            - end_date: datetime
            - avg_spot_length: float
            - avg_spots_per_window: float
        or None if no data found

    Example:
        >>> summary = await get_campaign_summary('18295')
        >>> print(f"Campaign ran on {summary['total_frames']} frames")
        Campaign ran on 145 frames
    """
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
        WHERE buyercampaignref = $1
    """

    results = await _db.execute_query(query, (campaign_id,))
    return results[0] if results else None


async def get_campaign_by_date(
    campaign_id: str, start_date: str, end_date: str
) -> Optional[Dict]:
    """
    Get campaign summary for a specific date range.

    Args:
        campaign_id: Campaign reference
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)

    Returns:
        Dict with date-range summary or None if no data

    Example:
        >>> summary = await get_campaign_by_date('18295', '2025-08-01', '2025-09-01')
    """
    query = """
        SELECT
            COUNT(DISTINCT frameid) as frames,
            COUNT(DISTINCT time_window_start) as total_windows,
            SUM(spot_count) as total_spots,
            ROUND(AVG(playout_length_seconds), 1) as avg_spot_length
        FROM mv_playout_15min
        WHERE buyercampaignref = $1
          AND time_window_start >= $2
          AND time_window_start < $3
    """

    results = await _db.execute_query(query, (campaign_id, start_date, end_date))
    return results[0] if results else None


# ==============================================================================
# TIME-SERIES DATA FOR CHARTS
# ==============================================================================


async def get_hourly_activity(
    campaign_id: str, start_date: str, end_date: str
) -> List[Dict]:
    """
    Get hourly aggregated activity for time-series charts.

    Args:
        campaign_id: Campaign reference
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)

    Returns:
        List of dicts with:
            - hour: datetime
            - active_windows: int
            - total_spots: int

    Example:
        >>> activity = await get_hourly_activity('18295', '2025-08-01', '2025-08-02')
        >>> # Use for time-series chart
    """
    query = """
        SELECT
            DATE_TRUNC('hour', time_window_start) as hour,
            COUNT(*) as active_windows,
            SUM(spot_count) as total_spots
        FROM mv_playout_15min
        WHERE buyercampaignref = $1
          AND time_window_start >= $2
          AND time_window_start < $3
        GROUP BY DATE_TRUNC('hour', time_window_start)
        ORDER BY hour
    """

    return await _db.execute_query(query, (campaign_id, start_date, end_date))


async def get_daily_summary(
    campaign_id: str, start_date: str, end_date: str
) -> List[Dict]:
    """
    Get daily summary for calendar view or daily breakdown chart.

    Args:
        campaign_id: Campaign reference
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)

    Returns:
        List of dicts with daily metrics

    Example:
        >>> daily = await get_daily_summary('18295', '2025-08-01', '2025-09-01')
    """
    query = """
        SELECT
            DATE(time_window_start) as date,
            COUNT(DISTINCT frameid) as frames,
            COUNT(*) as windows,
            SUM(spot_count) as spots
        FROM mv_playout_15min
        WHERE buyercampaignref = $1
          AND time_window_start >= $2
          AND time_window_start < $3
        GROUP BY DATE(time_window_start)
        ORDER BY date
    """

    return await _db.execute_query(query, (campaign_id, start_date, end_date))


# ==============================================================================
# ROUTE RELEASE INTEGRATION
# ==============================================================================


async def get_route_release_for_date(playout_date: str) -> Optional[Dict]:
    """
    Determine which Route release to use for a given date.

    Args:
        playout_date: Date of playout (YYYY-MM-DD)

    Returns:
        Dict with:
            - release_number: str (e.g., 'R55')
            - name: str (e.g., 'Q2 2025')
        or None if no release found

    Example:
        >>> release = await get_route_release_for_date('2025-09-15')
        >>> print(release['release_number'])
        R55
    """
    query = """
        SELECT release_number, name
        FROM route_releases
        WHERE $1::date BETWEEN trading_period_start AND trading_period_end
    """

    results = await _db.execute_query(query, (playout_date,))
    return results[0] if results else None


async def get_all_route_releases() -> List[Dict]:
    """
    Get all Route releases with their trading periods.

    Returns:
        List of dicts with release metadata

    Example:
        >>> releases = await get_all_route_releases()
        >>> for r in releases:
        ...     print(f"{r['release_number']}: {r['name']}")
        R54: Q1 2025
        R55: Q2 2025
        ...
    """
    query = """
        SELECT
            release_number,
            name,
            trading_period_start,
            trading_period_end
        FROM route_releases
        ORDER BY trading_period_start
    """

    return await _db.execute_query(query)


# ==============================================================================
# BRAND-LEVEL REPORTING
# ==============================================================================


async def get_campaign_by_brand(
    campaign_id: str, start_date: str, end_date: str
) -> List[Dict]:
    """
    Break down campaign performance by brand.

    Args:
        campaign_id: Campaign reference
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)

    Returns:
        List of dicts with brand-level metrics:
            - spacebrandid: str
            - unique_frames: int
            - active_windows: int
            - total_spots: int

    Example:
        >>> brands = await get_campaign_by_brand('18699', '2025-08-20', '2025-08-25')
        >>> for brand in brands:
        ...     print(f"Brand {brand['spacebrandid']}: {brand['total_spots']} spots")
    """
    query = """
        SELECT
            spacebrandid,
            COUNT(DISTINCT frameid) as unique_frames,
            COUNT(DISTINCT time_window_start) as active_windows,
            SUM(spots_for_brand) as total_spots
        FROM mv_playout_15min_brands
        WHERE buyercampaignref = $1
          AND time_window_start >= $2
          AND time_window_start < $3
        GROUP BY spacebrandid
        ORDER BY total_spots DESC
    """

    return await _db.execute_query(query, (campaign_id, start_date, end_date))


async def split_audience_by_brand(
    frame_id: str, campaign_id: str, window_start: datetime, total_impacts: float
) -> List[Dict]:
    """
    Split Route API audience impacts proportionally by brand.

    Use this AFTER getting Route API response to distribute impacts
    across brands based on their spot distribution.

    Args:
        frame_id: Frame identifier
        campaign_id: Campaign reference
        window_start: 15-minute window timestamp
        total_impacts: Total impacts from Route API for this window

    Returns:
        List of dicts with:
            - brand_id: str
            - spots: int
            - proportion: float
            - impacts: float

    Example:
        >>> # After Route API call returns 10,000 impacts
        >>> brand_split = await split_audience_by_brand(
        ...     '1234859642', '18699', '2025-08-23 11:15:00', 10000
        ... )
        >>> for brand in brand_split:
        ...     print(f"Brand {brand['brand_id']}: {brand['impacts']} impacts")
        Brand 21143: 5000.0 impacts
        Brand 21146: 5000.0 impacts
    """
    query = """
        SELECT
            spacebrandid,
            spots_for_brand,
            spots_for_brand::FLOAT / SUM(spots_for_brand) OVER () as brand_proportion
        FROM mv_playout_15min_brands
        WHERE frameid = $1
          AND buyercampaignref = $2
          AND time_window_start = $3
    """

    brands = await _db.execute_query(query, (frame_id, campaign_id, window_start))

    return [
        {
            "brand_id": brand["spacebrandid"],
            "spots": brand["spots_for_brand"],
            "proportion": brand["brand_proportion"],
            "impacts": total_impacts * brand["brand_proportion"],
        }
        for brand in brands
    ]


# ==============================================================================
# FRAME-LEVEL QUERIES
# ==============================================================================


async def is_frame_active(frame_id: str, date_str: str) -> bool:
    """
    Check if a frame has any playout data on a given date.

    Args:
        frame_id: Frame identifier
        date_str: Date to check (YYYY-MM-DD)

    Returns:
        True if frame was active, False otherwise

    Example:
        >>> active = await is_frame_active('1234567890', '2025-08-15')
        >>> print(f"Frame active: {active}")
    """
    query = """
        SELECT EXISTS(
            SELECT 1 FROM mv_playout_15min
            WHERE frameid = $1
              AND time_window_start >= $2
              AND time_window_start < $2::date + INTERVAL '1 day'
        )
    """

    result = await _db.execute_query(query, (frame_id, date_str))
    return result[0]["exists"] if result else False


async def get_frame_campaigns(
    frame_id: str, start_date: str, end_date: str
) -> List[Dict]:
    """
    Get all campaigns that played on a specific frame in date range.

    Args:
        frame_id: Frame identifier
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)

    Returns:
        List of dicts with campaign summaries

    Example:
        >>> campaigns = await get_frame_campaigns('1234567890', '2025-08-01', '2025-09-01')
    """
    query = """
        SELECT
            buyercampaignref,
            COUNT(*) as windows,
            SUM(spot_count) as total_spots,
            MIN(time_window_start) as first_window,
            MAX(time_window_start) as last_window
        FROM mv_playout_15min
        WHERE frameid = $1
          AND time_window_start >= $2
          AND time_window_start < $3
        GROUP BY buyercampaignref
        ORDER BY total_spots DESC
    """

    return await _db.execute_query(query, (frame_id, start_date, end_date))


# ==============================================================================
# UTILITY FUNCTIONS
# ==============================================================================


async def check_data_freshness() -> Dict:
    """
    Check when data was last refreshed.

    Returns:
        Dict with:
            - latest_window: datetime
            - latest_playout: datetime
            - hours_old: float

    Example:
        >>> freshness = await check_data_freshness()
        >>> print(f"Data is {freshness['hours_old']:.1f} hours old")
    """
    query = """
        SELECT
            MAX(time_window_start) as latest_window,
            MAX(latest_playout) as latest_playout
        FROM mv_playout_15min
    """

    result = (await _db.execute_query(query))[0]

    hours_old = (datetime.now() - result["latest_playout"]).total_seconds() / 3600

    return {
        "latest_window": result["latest_window"],
        "latest_playout": result["latest_playout"],
        "hours_old": hours_old,
    }


async def get_date_coverage() -> Dict:
    """
    Get date range and coverage of playout data.

    Returns:
        Dict with date coverage info

    Example:
        >>> coverage = await get_date_coverage()
        >>> print(f"Coverage: {coverage['start_date']} to {coverage['end_date']}")
    """
    query = """
        SELECT
            MIN(DATE(time_window_start)) as start_date,
            MAX(DATE(time_window_start)) as end_date,
            COUNT(DISTINCT DATE(time_window_start)) as days_with_data
        FROM mv_playout_15min
    """

    return (await _db.execute_query(query))[0]


async def get_all_campaigns(limit: int = 100) -> List[Dict]:
    """
    Get list of all available campaigns in the database.

    Args:
        limit: Maximum number of campaigns to return

    Returns:
        List of dicts with campaign information

    Example:
        >>> campaigns = await get_all_campaigns(limit=50)
        >>> for campaign in campaigns:
        ...     print(f"{campaign['buyercampaignref']}: {campaign['total_spots']} spots")
    """
    query = """
        SELECT
            buyercampaignref,
            COUNT(DISTINCT frameid) as total_frames,
            SUM(spot_count) as total_spots,
            MIN(time_window_start) as start_date,
            MAX(time_window_start) as end_date
        FROM mv_playout_15min
        GROUP BY buyercampaignref
        ORDER BY MAX(time_window_start) DESC
        LIMIT $1
    """

    return await _db.execute_query(query, (limit,))
