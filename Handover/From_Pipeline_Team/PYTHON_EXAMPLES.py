"""
MS-01 Database Python Examples for POC Development

Purpose: Ready-to-use Python code for querying MS-01 database
Database: MS-01 @ 192.168.1.34:5432, database 'route_poc'
Last Updated: 2025-10-17

Requirements:
    pip install psycopg2-binary python-dotenv

Environment Variables:
    MS01_DB_PASSWORD=<password>
"""

import os
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ==============================================================================
# DATABASE CONNECTION
# ==============================================================================

class MS01Database:
    """MS-01 PostgreSQL database connection manager."""

    def __init__(self):
        """Initialize connection pool."""
        self.connection_pool = psycopg2.pool.SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            host="192.168.1.34",
            port=5432,
            database="route_poc",
            user="postgres",
            password=os.getenv('MS01_DB_PASSWORD')
        )

    def get_connection(self):
        """Get connection from pool."""
        return self.connection_pool.getconn()

    def return_connection(self, conn):
        """Return connection to pool."""
        self.connection_pool.putconn(conn)

    def execute_query(self, query: str, params: tuple = None) -> List[Dict]:
        """
        Execute query and return results as list of dicts.

        Args:
            query: SQL query string
            params: Query parameters tuple

        Returns:
            List of dicts (column_name: value)
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, params)
            results = cursor.fetchall()
            cursor.close()
            return results
        finally:
            self.return_connection(conn)

# Initialize database connection
db = MS01Database()

# ==============================================================================
# ROUTE API DATA RETRIEVAL
# ==============================================================================

def get_campaign_for_route_api(
    campaign_id: str,
    start_date: str,
    end_date: str
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
        >>> data = get_campaign_for_route_api('18295', '2025-08-01', '2025-09-01')
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
        WHERE buyercampaignref = %s
          AND time_window_start >= %s
          AND time_window_start < %s
        ORDER BY frameid, time_window_start
    """

    return db.execute_query(query, (campaign_id, start_date, end_date))


def build_route_api_payload(campaign_data: List[Dict], route_release: str) -> Dict:
    """
    Convert aggregated playout data into Route API request format.

    Args:
        campaign_data: Output from get_campaign_for_route_api()
        route_release: Route release number (e.g., 'R55')

    Returns:
        Dict ready for Route API POST request

    Example:
        >>> route_data = get_campaign_for_route_api('18295', '2025-08-01', '2025-09-02')
        >>> payload = build_route_api_payload(route_data, 'R55')
        >>> # POST payload to Route API
    """
    # Group by frame for batch processing
    frames = {}
    for record in campaign_data:
        frame_id = record['frameid']
        if frame_id not in frames:
            frames[frame_id] = []

        frames[frame_id].append({
            'datetime_from': record['datetime_from'].isoformat(),
            'datetime_to': record['datetime_to'].isoformat(),
            'spot_count': record['spot_count'],
            'playout_length': record['playout_length'],
            'break_length': record['break_length']
        })

    # Build Route API payload
    payload = {
        'route_release_id': route_release,
        'frames': []
    }

    for frame_id, windows in frames.items():
        payload['frames'].append({
            'frame_id': frame_id,
            'windows': windows
        })

    return payload

# ==============================================================================
# CAMPAIGN SUMMARY & STATISTICS
# ==============================================================================

def get_campaign_summary(campaign_id: str) -> Dict:
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

    Example:
        >>> summary = get_campaign_summary('18295')
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
        WHERE buyercampaignref = %s
    """

    results = db.execute_query(query, (campaign_id,))
    return results[0] if results else None


def get_campaign_by_date(campaign_id: str, start_date: str, end_date: str) -> Dict:
    """
    Get campaign summary for a specific date range.

    Args:
        campaign_id: Campaign reference
        start_date: Start date
        end_date: End date

    Returns:
        Dict with date-range summary

    Example:
        >>> summary = get_campaign_by_date('18295', '2025-08-01', '2025-09-01')
    """
    query = """
        SELECT
            COUNT(DISTINCT frameid) as frames,
            COUNT(DISTINCT time_window_start) as total_windows,
            SUM(spot_count) as total_spots,
            ROUND(AVG(playout_length_seconds), 1) as avg_spot_length
        FROM mv_playout_15min
        WHERE buyercampaignref = %s
          AND time_window_start >= %s
          AND time_window_start < %s
    """

    results = db.execute_query(query, (campaign_id, start_date, end_date))
    return results[0] if results else None

# ==============================================================================
# TIME-SERIES DATA FOR CHARTS
# ==============================================================================

def get_hourly_activity(
    campaign_id: str,
    start_date: str,
    end_date: str
) -> List[Dict]:
    """
    Get hourly aggregated activity for time-series charts.

    Args:
        campaign_id: Campaign reference
        start_date: Start date
        end_date: End date

    Returns:
        List of dicts with:
            - hour: datetime
            - active_windows: int
            - total_spots: int

    Example:
        >>> activity = get_hourly_activity('18295', '2025-08-01', '2025-08-02')
        >>> # Use for time-series chart
    """
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

    return db.execute_query(query, (campaign_id, start_date, end_date))


def get_daily_summary(
    campaign_id: str,
    start_date: str,
    end_date: str
) -> List[Dict]:
    """
    Get daily summary for calendar view or daily breakdown chart.

    Args:
        campaign_id: Campaign reference
        start_date: Start date
        end_date: End date

    Returns:
        List of dicts with daily metrics

    Example:
        >>> daily = get_daily_summary('18295', '2025-08-01', '2025-09-01')
    """
    query = """
        SELECT
            DATE(time_window_start) as date,
            COUNT(DISTINCT frameid) as frames,
            COUNT(*) as windows,
            SUM(spot_count) as spots
        FROM mv_playout_15min
        WHERE buyercampaignref = %s
          AND time_window_start >= %s
          AND time_window_start < %s
        GROUP BY DATE(time_window_start)
        ORDER BY date
    """

    return db.execute_query(query, (campaign_id, start_date, end_date))

# ==============================================================================
# ROUTE RELEASE INTEGRATION
# ==============================================================================

def get_route_release_for_date(playout_date: str) -> Optional[Dict]:
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
        >>> release = get_route_release_for_date('2025-09-15')
        >>> print(release['release_number'])
        R55
    """
    query = """
        SELECT release_number, name
        FROM route_releases
        WHERE %s::date BETWEEN trading_period_start AND trading_period_end
    """

    results = db.execute_query(query, (playout_date,))
    return results[0] if results else None


def get_all_route_releases() -> List[Dict]:
    """
    Get all Route releases with their trading periods.

    Returns:
        List of dicts with release metadata

    Example:
        >>> releases = get_all_route_releases()
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

    return db.execute_query(query)

# ==============================================================================
# BRAND-LEVEL REPORTING
# ==============================================================================

def get_campaign_by_brand(
    campaign_id: str,
    start_date: str,
    end_date: str
) -> List[Dict]:
    """
    Break down campaign performance by brand.

    Args:
        campaign_id: Campaign reference
        start_date: Start date
        end_date: End date

    Returns:
        List of dicts with brand-level metrics:
            - spacebrandid: str
            - unique_frames: int
            - active_windows: int
            - total_spots: int

    Example:
        >>> brands = get_campaign_by_brand('18699', '2025-08-20', '2025-08-25')
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
        WHERE buyercampaignref = %s
          AND time_window_start >= %s
          AND time_window_start < %s
        GROUP BY spacebrandid
        ORDER BY total_spots DESC
    """

    return db.execute_query(query, (campaign_id, start_date, end_date))


def split_audience_by_brand(
    frame_id: str,
    campaign_id: str,
    window_start: datetime,
    total_impacts: float
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
        >>> brand_split = split_audience_by_brand(
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
        WHERE frameid = %s
          AND buyercampaignref = %s
          AND time_window_start = %s
    """

    brands = db.execute_query(query, (frame_id, campaign_id, window_start))

    return [{
        'brand_id': brand['spacebrandid'],
        'spots': brand['spots_for_brand'],
        'proportion': brand['brand_proportion'],
        'impacts': total_impacts * brand['brand_proportion']
    } for brand in brands]

# ==============================================================================
# FRAME-LEVEL QUERIES
# ==============================================================================

def is_frame_active(frame_id: str, date: str) -> bool:
    """
    Check if a frame has any playout data on a given date.

    Args:
        frame_id: Frame identifier
        date: Date to check (YYYY-MM-DD)

    Returns:
        True if frame was active, False otherwise

    Example:
        >>> active = is_frame_active('1234567890', '2025-08-15')
        >>> print(f"Frame active: {active}")
    """
    query = """
        SELECT EXISTS(
            SELECT 1 FROM mv_playout_15min
            WHERE frameid = %s
              AND time_window_start >= %s
              AND time_window_start < %s::date + INTERVAL '1 day'
        )
    """

    result = db.execute_query(query, (frame_id, date, date))
    return result[0]['exists'] if result else False


def get_frame_campaigns(
    frame_id: str,
    start_date: str,
    end_date: str
) -> List[Dict]:
    """
    Get all campaigns that played on a specific frame in date range.

    Args:
        frame_id: Frame identifier
        start_date: Start date
        end_date: End date

    Returns:
        List of dicts with campaign summaries

    Example:
        >>> campaigns = get_frame_campaigns('1234567890', '2025-08-01', '2025-09-01')
    """
    query = """
        SELECT
            buyercampaignref,
            COUNT(*) as windows,
            SUM(spot_count) as total_spots,
            MIN(time_window_start) as first_window,
            MAX(time_window_start) as last_window
        FROM mv_playout_15min
        WHERE frameid = %s
          AND time_window_start >= %s
          AND time_window_start < %s
        GROUP BY buyercampaignref
        ORDER BY total_spots DESC
    """

    return db.execute_query(query, (frame_id, start_date, end_date))

# ==============================================================================
# UTILITY FUNCTIONS
# ==============================================================================

def check_data_freshness() -> Dict:
    """
    Check when data was last refreshed.

    Returns:
        Dict with:
            - latest_window: datetime
            - latest_playout: datetime
            - hours_old: float

    Example:
        >>> freshness = check_data_freshness()
        >>> print(f"Data is {freshness['hours_old']:.1f} hours old")
    """
    query = """
        SELECT
            MAX(time_window_start) as latest_window,
            MAX(latest_playout) as latest_playout
        FROM mv_playout_15min
    """

    result = db.execute_query(query)[0]

    hours_old = (datetime.now() - result['latest_playout']).total_seconds() / 3600

    return {
        'latest_window': result['latest_window'],
        'latest_playout': result['latest_playout'],
        'hours_old': hours_old
    }


def get_date_coverage() -> Dict:
    """
    Get date range and coverage of playout data.

    Returns:
        Dict with date coverage info

    Example:
        >>> coverage = get_date_coverage()
        >>> print(f"Coverage: {coverage['start_date']} to {coverage['end_date']}")
    """
    query = """
        SELECT
            MIN(DATE(time_window_start)) as start_date,
            MAX(DATE(time_window_start)) as end_date,
            COUNT(DISTINCT DATE(time_window_start)) as days_with_data
        FROM mv_playout_15min
    """

    return db.execute_query(query)[0]

# ==============================================================================
# EXAMPLE USAGE
# ==============================================================================

if __name__ == "__main__":
    """
    Example usage of the database functions.
    """

    # 1. Get campaign data for Route API
    print("=" * 70)
    print("1. GETTING CAMPAIGN DATA FOR ROUTE API")
    print("=" * 70)

    campaign_data = get_campaign_for_route_api(
        campaign_id='18295',
        start_date='2025-08-01',
        end_date='2025-08-02'
    )

    print(f"Found {len(campaign_data)} windows")
    print(f"First window: {campaign_data[0]}")

    # 2. Get Route release for date range
    print("\n" + "=" * 70)
    print("2. DETERMINING ROUTE RELEASE")
    print("=" * 70)

    release = get_route_release_for_date('2025-08-01')
    print(f"Route Release: {release['release_number']} ({release['name']})")

    # 3. Build Route API payload
    print("\n" + "=" * 70)
    print("3. BUILDING ROUTE API PAYLOAD")
    print("=" * 70)

    payload = build_route_api_payload(campaign_data, release['release_number'])
    print(f"Payload has {len(payload['frames'])} frames")
    print(f"Total windows: {sum(len(f['windows']) for f in payload['frames'])}")

    # 4. Get campaign summary
    print("\n" + "=" * 70)
    print("4. CAMPAIGN SUMMARY")
    print("=" * 70)

    summary = get_campaign_summary('18295')
    print(f"Total frames: {summary['total_frames']}")
    print(f"Days active: {summary['days_active']}")
    print(f"Total playouts: {summary['total_playouts']:,}")
    print(f"Avg spot length: {summary['avg_spot_length']}s")

    # 5. Check data freshness
    print("\n" + "=" * 70)
    print("5. DATA FRESHNESS CHECK")
    print("=" * 70)

    freshness = check_data_freshness()
    print(f"Latest data: {freshness['latest_playout']}")
    print(f"Age: {freshness['hours_old']:.1f} hours old")

    # 6. Get date coverage
    print("\n" + "=" * 70)
    print("6. DATE COVERAGE")
    print("=" * 70)

    coverage = get_date_coverage()
    print(f"Start date: {coverage['start_date']}")
    print(f"End date: {coverage['end_date']}")
    print(f"Days with data: {coverage['days_with_data']}")

    print("\n✅ All examples completed successfully!")
