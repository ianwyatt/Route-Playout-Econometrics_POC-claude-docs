# ABOUTME: [PLACEHOLDER - NOT CURRENTLY USED] Reach calculation service with Route API integration
# ABOUTME: Retained for future feature: on-demand API calls for data not in cache (e.g. regional reach, custom demographics)

import logging
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any
from src.api.route_client import RouteAPIClient
from src.services.cache_service import CacheService, get_cache_service
from src.db import get_campaign_for_route_api, get_release_for_date

logger = logging.getLogger(__name__)


class ReachService:
    """
    Service for calculating reach, GRP, and frequency metrics

    Integrates:
    - PostgreSQL cache (persistent across sessions)
    - Route API custom endpoint (for reach calculations)
    - Materialized views (for playout aggregation)

    Supports multiple aggregation levels:
    - Day: Reach for a single day
    - Week: Reach for a week (Monday-Sunday)
    - Campaign: Reach for entire campaign period
    """

    def __init__(self):
        """Initialize reach service"""
        self.route_client = RouteAPIClient()
        self.cache: Optional[CacheService] = None
        self._initialized = False

    async def initialize(self):
        """Initialize database cache connection"""
        if not self._initialized:
            self.cache = await get_cache_service()
            self._initialized = True
            logger.info("Reach service initialized")

    async def close(self):
        """Close connections"""
        # Cache service is global, don't close it here
        self._initialized = False
        logger.info("Reach service closed")

    # =========================================================================
    # Day-level Reach
    # =========================================================================

    async def get_campaign_reach_day(
        self,
        campaign_id: str,
        date: date,
        route_release_id: Optional[int] = None,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Get reach, GRP, and frequency for a campaign on a specific day

        Args:
            campaign_id: Campaign reference
            date: Date to calculate reach for
            route_release_id: Route release ID (auto-detected if None)
            force_refresh: Force API call even if cached

        Returns:
            Dict with reach, GRP, frequency, impacts
        """
        if not self._initialized:
            await self.initialize()

        # Auto-detect route release if not provided
        if route_release_id is None:
            release = await get_release_for_date(date)
            if release is None:
                logger.error(f"No Route release found for date {date}")
                return {
                    'success': False,
                    'error': f'No Route release available for {date}',
                    'reach': 0,
                    'grp': 0,
                    'frequency': 0,
                    'total_impacts': 0
                }
            route_release_id = release.release_number

        # Check cache first (unless force refresh)
        if not force_refresh:
            cached = await self.cache.get_reach_day_cache(
                campaign_id=campaign_id,
                date=date,
                route_release_id=route_release_id
            )
            if cached:
                logger.info(f"✅ Using cached reach for campaign {campaign_id} on {date}")
                return cached

        # Cache miss - calculate from API
        logger.info(f"📡 Calculating reach for campaign {campaign_id} on {date}")

        # Get playout data for this day from materialized view
        # Note: end_date is EXCLUSIVE in the query (uses <, not <=)
        playouts = await get_campaign_for_route_api(
            campaign_id=campaign_id,
            start_date=date,
            end_date=date + timedelta(days=1)  # Exclusive end date
        )

        if not playouts:
            logger.warning(f"No playout data for campaign {campaign_id} on {date}")
            # Cache zero result
            await self.cache.put_reach_day_cache(
                campaign_id=campaign_id,
                date=date,
                reach=0,
                grp=0,
                frequency=0,
                total_impacts=0,
                frame_count=0,
                route_release_id=route_release_id
            )
            return {
                'success': True,
                'reach': 0,
                'grp': 0,
                'frequency': 0,
                'total_impacts': 0,
                'frame_count': 0,
                'message': 'No playouts for this date'
            }

        # Extract unique frames and build schedules
        frames = list(set(p['frameid'] for p in playouts))

        # Group by time windows to build schedules
        schedules = self._build_schedules_from_playouts(playouts)

        # Calculate average spot and break lengths (rounded to nearest second)
        avg_spot_length = round(sum(p['playout_length'] for p in playouts) / len(playouts))
        avg_break_length = round(sum(p['break_length'] for p in playouts) / len(playouts))

        # Call Route API custom endpoint
        try:
            result = await self.route_client.get_campaign_reach(
                frames=frames,
                schedules=schedules,
                spot_length=avg_spot_length,
                break_length=avg_break_length,
                release_id=route_release_id
            )

            if result.get('success'):
                # Cache the result
                await self.cache.put_reach_day_cache(
                    campaign_id=campaign_id,
                    date=date,
                    reach=result.get('reach', 0),
                    grp=result.get('grp', 0),
                    frequency=result.get('frequency', 0),
                    total_impacts=result.get('impacts', 0),
                    frame_count=len(frames),
                    route_release_id=route_release_id
                )

                logger.info(
                    f"✅ Calculated reach for {campaign_id} on {date}: "
                    f"Reach={result.get('reach', 0)}, GRP={result.get('grp', 0)}"
                )

                return result
            else:
                logger.error(f"Route API call failed for {campaign_id} on {date}")
                return {
                    'success': False,
                    'error': 'Route API call failed',
                    'reach': 0,
                    'grp': 0,
                    'frequency': 0,
                    'total_impacts': 0
                }

        except Exception as e:
            logger.error(f"Error calculating reach: {e}")
            return {
                'success': False,
                'error': str(e),
                'reach': 0,
                'grp': 0,
                'frequency': 0,
                'total_impacts': 0
            }

    # =========================================================================
    # Week-level Reach
    # =========================================================================

    async def get_campaign_reach_week(
        self,
        campaign_id: str,
        week_start: date,
        week_end: date,
        route_release_id: Optional[int] = None,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Get reach, GRP, and frequency for a campaign for a week

        NOTE: Reach is non-additive. We cannot sum daily reach to get weekly reach.
        Must recalculate with all frames across the entire week.

        Args:
            campaign_id: Campaign reference
            week_start: Start of week (typically Monday)
            week_end: End of week (typically Sunday)
            route_release_id: Route release ID (auto-detected if None)
            force_refresh: Force API call even if cached

        Returns:
            Dict with reach, GRP, frequency, impacts for the week
        """
        if not self._initialized:
            await self.initialize()

        # Auto-detect route release
        if route_release_id is None:
            release = await get_release_for_date(week_start)
            if release is None:
                logger.error(f"No Route release found for week starting {week_start}")
                return self._zero_reach_result('No Route release available')
            route_release_id = release.release_number

        # Check cache
        if not force_refresh:
            cached = await self.cache.get_reach_week_cache(
                campaign_id=campaign_id,
                week_start=week_start,
                week_end=week_end,
                route_release_id=route_release_id
            )
            if cached:
                logger.info(f"✅ Using cached week reach for campaign {campaign_id}")
                return cached

        # Cache miss - calculate from API
        logger.info(f"📡 Calculating week reach for campaign {campaign_id} ({week_start} to {week_end})")

        # Get ALL playouts for the entire week
        # Note: end_date is EXCLUSIVE, so add 1 day to include week_end
        playouts = await get_campaign_for_route_api(
            campaign_id=campaign_id,
            start_date=week_start,
            end_date=week_end + timedelta(days=1)  # Exclusive end date
        )

        if not playouts:
            logger.warning(f"No playout data for campaign {campaign_id} for week {week_start}")
            result = self._zero_reach_result('No playouts for this week')
            # Cache zero result
            await self.cache.put_reach_week_cache(
                campaign_id=campaign_id,
                week_start=week_start,
                week_end=week_end,
                reach=0,
                grp=0,
                frequency=0,
                total_impacts=0,
                frame_count=0,
                route_release_id=route_release_id
            )
            return result

        # Build API request
        frames = list(set(p['frameid'] for p in playouts))
        schedules = self._build_schedules_from_playouts(playouts)
        avg_spot_length = round(sum(p['playout_length'] for p in playouts) / len(playouts))
        avg_break_length = round(sum(p['break_length'] for p in playouts) / len(playouts))

        # Call Route API
        try:
            result = await self.route_client.get_campaign_reach(
                frames=frames,
                schedules=schedules,
                spot_length=avg_spot_length,
                break_length=avg_break_length,
                release_id=route_release_id
            )

            if result.get('success'):
                # Cache the result
                await self.cache.put_reach_week_cache(
                    campaign_id=campaign_id,
                    week_start=week_start,
                    week_end=week_end,
                    reach=result.get('reach', 0),
                    grp=result.get('grp', 0),
                    frequency=result.get('frequency', 0),
                    total_impacts=result.get('impacts', 0),
                    frame_count=len(frames),
                    route_release_id=route_release_id
                )

                logger.info(f"✅ Calculated week reach for {campaign_id}: Reach={result.get('reach', 0)}")
                return result
            else:
                return self._zero_reach_result('Route API call failed')

        except Exception as e:
            logger.error(f"Error calculating week reach: {e}")
            return self._zero_reach_result(str(e))

    # =========================================================================
    # Full Campaign Reach
    # =========================================================================

    async def get_campaign_reach_full(
        self,
        campaign_id: str,
        date_from: date,
        date_to: date,
        route_release_id: Optional[int] = None,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Get reach, GRP, and frequency for entire campaign period

        Args:
            campaign_id: Campaign reference
            date_from: Campaign start date
            date_to: Campaign end date
            route_release_id: Route release ID (auto-detected if None)
            force_refresh: Force API call even if cached

        Returns:
            Dict with reach, GRP, frequency, impacts for full campaign
        """
        if not self._initialized:
            await self.initialize()

        # Auto-detect route release
        if route_release_id is None:
            release = await get_release_for_date(date_from)
            if release is None:
                logger.error(f"No Route release found for campaign starting {date_from}")
                return self._zero_reach_result('No Route release available')
            route_release_id = release.release_number

        # Check cache
        if not force_refresh:
            cached = await self.cache.get_reach_full_cache(
                campaign_id=campaign_id,
                date_from=date_from,
                date_to=date_to,
                route_release_id=route_release_id
            )
            if cached:
                logger.info(f"✅ Using cached full campaign reach for {campaign_id}")
                return cached

        # Cache miss - calculate from API
        logger.info(f"📡 Calculating full campaign reach for {campaign_id} ({date_from} to {date_to})")

        # Get ALL playouts for entire campaign
        # Note: end_date is EXCLUSIVE, so add 1 day to include date_to
        playouts = await get_campaign_for_route_api(
            campaign_id=campaign_id,
            start_date=date_from,
            end_date=date_to + timedelta(days=1)  # Exclusive end date
        )

        if not playouts:
            logger.warning(f"No playout data for campaign {campaign_id}")
            result = self._zero_reach_result('No playouts for this campaign')
            # Cache zero result
            await self.cache.put_reach_full_cache(
                campaign_id=campaign_id,
                date_from=date_from,
                date_to=date_to,
                reach=0,
                grp=0,
                frequency=0,
                total_impacts=0,
                frame_count=0,
                route_release_id=route_release_id
            )
            return result

        # Build API request
        frames = list(set(p['frameid'] for p in playouts))

        # Check if we need batching (>10k frames)
        if len(frames) > 10000:
            logger.warning(f"Large campaign with {len(frames)} frames - using batching")
            # For >10k frames, we can't get accurate reach in one call
            # Return warning and suggest using date-based aggregation
            return {
                'success': False,
                'error': 'Campaign exceeds 10,000 frame limit',
                'frame_count': len(frames),
                'recommendation': 'Use day or week aggregation instead',
                'reach': 0,
                'grp': 0,
                'frequency': 0,
                'total_impacts': 0
            }

        schedules = self._build_schedules_from_playouts(playouts)
        avg_spot_length = round(sum(p['playout_length'] for p in playouts) / len(playouts))
        avg_break_length = round(sum(p['break_length'] for p in playouts) / len(playouts))

        # Call Route API
        try:
            result = await self.route_client.get_campaign_reach(
                frames=frames,
                schedules=schedules,
                spot_length=avg_spot_length,
                break_length=avg_break_length,
                release_id=route_release_id
            )

            if result.get('success'):
                # Cache the result
                await self.cache.put_reach_full_cache(
                    campaign_id=campaign_id,
                    date_from=date_from,
                    date_to=date_to,
                    reach=result.get('reach', 0),
                    grp=result.get('grp', 0),
                    frequency=result.get('frequency', 0),
                    total_impacts=result.get('impacts', 0),
                    frame_count=len(frames),
                    route_release_id=route_release_id
                )

                logger.info(f"✅ Calculated full campaign reach for {campaign_id}: Reach={result.get('reach', 0)}")
                return result
            else:
                return self._zero_reach_result('Route API call failed')

        except Exception as e:
            logger.error(f"Error calculating full campaign reach: {e}")
            return self._zero_reach_result(str(e))

    # =========================================================================
    # Multi-day Aggregation
    # =========================================================================

    async def get_campaign_reach_daterange(
        self,
        campaign_id: str,
        date_from: date,
        date_to: date,
        route_release_id: Optional[int] = None,
        return_daily: bool = False
    ) -> Dict[str, Any]:
        """
        Get reach across a date range with daily breakdown option

        Args:
            campaign_id: Campaign reference
            date_from: Start date
            date_to: End date
            route_release_id: Route release ID
            return_daily: If True, return daily breakdown in addition to total

        Returns:
            Dict with total reach and optional daily breakdown
        """
        # For date ranges, we use the full campaign method
        # which calculates reach across all frames in the period
        total_reach = await self.get_campaign_reach_full(
            campaign_id=campaign_id,
            date_from=date_from,
            date_to=date_to,
            route_release_id=route_release_id
        )

        if not return_daily:
            return total_reach

        # Also get daily breakdown
        daily_breakdown = []
        current_date = date_from
        while current_date <= date_to:
            day_reach = await self.get_campaign_reach_day(
                campaign_id=campaign_id,
                date=current_date,
                route_release_id=route_release_id
            )
            daily_breakdown.append({
                'date': current_date.isoformat(),
                'reach': day_reach.get('reach', 0),
                'grp': day_reach.get('grp', 0),
                'frequency': day_reach.get('frequency', 0),
                'impacts': day_reach.get('total_impacts', 0)
            })
            current_date += timedelta(days=1)

        return {
            'success': True,
            'campaign_id': campaign_id,
            'date_from': date_from.isoformat(),
            'date_to': date_to.isoformat(),
            'total': total_reach,
            'daily': daily_breakdown,
            'note': 'Daily reach values do NOT sum to total reach (reach is non-additive)'
        }

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _build_schedules_from_playouts(self, playouts: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        Build Route API schedule format from playout data

        Consolidates 15-minute windows into larger time blocks for efficiency

        Args:
            playouts: List of playout dicts with datetime_from and datetime_to

        Returns:
            List of schedule dicts for Route API (with datetime strings in "YYYY-MM-DD HH:MM" format)
        """
        if not playouts:
            return []

        # Group consecutive time windows
        # Sort by start time
        sorted_playouts = sorted(playouts, key=lambda p: p['datetime_from'])

        schedules = []
        current_start = sorted_playouts[0]['datetime_from']
        current_end = sorted_playouts[0]['datetime_to']

        for playout in sorted_playouts[1:]:
            # If this playout starts where the last one ended, merge them
            if playout['datetime_from'] == current_end:
                current_end = playout['datetime_to']
            else:
                # Gap detected - save current schedule and start new one
                schedules.append({
                    'datetime_from': self._format_datetime_for_route(current_start),
                    'datetime_until': self._format_datetime_for_route(current_end)
                })
                current_start = playout['datetime_from']
                current_end = playout['datetime_to']

        # Add final schedule
        schedules.append({
            'datetime_from': self._format_datetime_for_route(current_start),
            'datetime_until': self._format_datetime_for_route(current_end)
        })

        logger.debug(f"Built {len(schedules)} schedule blocks from {len(playouts)} playouts")
        return schedules

    def _format_datetime_for_route(self, dt: Any) -> str:
        """
        Format datetime for Route API

        Handles both datetime objects and strings, converting to Route API format: "YYYY-MM-DD HH:MM"

        Args:
            dt: datetime object or string

        Returns:
            Formatted datetime string
        """
        if isinstance(dt, str):
            # Already a string - try to parse and reformat
            try:
                parsed = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
                return parsed.strftime("%Y-%m-%d %H:%M")
            except ValueError:
                # Try alternative format
                try:
                    parsed = datetime.strptime(dt, "%Y-%m-%d %H:%M")
                    return dt  # Already in correct format
                except ValueError:
                    logger.warning(f"Unexpected datetime string format: {dt}")
                    return dt
        else:
            # datetime object - convert to Route API format
            return dt.strftime("%Y-%m-%d %H:%M")

    def _zero_reach_result(self, message: str = '') -> Dict[str, Any]:
        """Return a zero reach result with optional message"""
        return {
            'success': True,
            'reach': 0,
            'grp': 0,
            'frequency': 0,
            'total_impacts': 0,
            'frame_count': 0,
            'message': message
        }

    # =========================================================================
    # Cache Statistics
    # =========================================================================

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if self.cache:
            return self.cache.get_cache_stats()
        return {'error': 'Cache not initialized'}

    async def clear_campaign_cache(self, campaign_id: str) -> int:
        """
        Clear all cached reach data for a specific campaign

        Args:
            campaign_id: Campaign to clear cache for

        Returns:
            Number of entries cleared
        """
        # This would require additional SQL queries to delete by campaign_id
        # For now, return not implemented
        logger.warning(f"clear_campaign_cache not yet implemented for {campaign_id}")
        return 0


# Global service instance
_reach_service: Optional[ReachService] = None


async def get_reach_service() -> ReachService:
    """Get or create global reach service instance"""
    global _reach_service
    if _reach_service is None:
        _reach_service = ReachService()
        await _reach_service.initialize()
    return _reach_service


async def close_reach_service():
    """Close global reach service instance"""
    global _reach_service
    if _reach_service is not None:
        await _reach_service.close()
        _reach_service = None
