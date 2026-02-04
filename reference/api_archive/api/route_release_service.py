# ABOUTME: Service class for managing Route releases with caching and date lookup
# ABOUTME: Provides high-performance access to Route release data for API calls

import logging
from datetime import datetime, date, timedelta
from typing import Optional, Dict, Any, List
import asyncio
from dataclasses import dataclass

from src.db.route_releases import RouteRelease, route_release_db, initialize_route_release_db
from src.utils.ttl_cache import TTLCache
from src.config import get_route_config

logger = logging.getLogger(__name__)


@dataclass
class ReleaseInfo:
    """Simplified release information for API usage"""
    release_number: str
    name: str
    numeric_id: int  # Extract numeric part for API calls (e.g., R54 → 54)
    trading_period_start: date
    trading_period_end: date
    
    @classmethod
    def from_route_release(cls, release: RouteRelease) -> 'ReleaseInfo':
        """Create ReleaseInfo from RouteRelease database object"""
        # Extract numeric ID from release number (e.g., "R54" → 54)
        numeric_id = int(release.release_number[1:]) if release.release_number.startswith('R') else 0
        
        return cls(
            release_number=release.release_number,
            name=release.name,
            numeric_id=numeric_id,
            trading_period_start=release.trading_period_start,
            trading_period_end=release.trading_period_end
        )


class RouteReleaseService:
    """High-performance service for Route release management"""
    
    def __init__(self, cache_size: int = 100, cache_ttl: float = 3600.0):
        """
        Initialize Route release service
        
        Args:
            cache_size: Maximum number of cached entries
            cache_ttl: Time-to-live for cached entries in seconds (default: 1 hour)
        """
        self.cache = TTLCache(max_size=cache_size, default_ttl=cache_ttl)
        self.config = get_route_config()
        self._initialized = False
        self._initialization_lock = asyncio.Lock()
        
        # Statistics
        self.stats = {
            'cache_hits': 0,
            'cache_misses': 0,
            'database_queries': 0,
            'fallback_uses': 0
        }
    
    async def initialize(self):
        """Initialize the service and database connection"""
        async with self._initialization_lock:
            if self._initialized:
                return
            
            try:
                await initialize_route_release_db()
                self._initialized = True
                logger.info("✅ Route release service initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Route release service: {e}")
                raise
    
    async def get_release_for_date(self, playout_date: date) -> ReleaseInfo:
        """
        Get the appropriate Route release for a playout date
        
        Args:
            playout_date: The date to lookup the release for
            
        Returns:
            ReleaseInfo with release details for API usage
        """
        if not self._initialized:
            await self.initialize()
        
        # Check cache first
        cache_key = f"date_{playout_date.isoformat()}"
        cached_result = self.cache.get(cache_key)
        
        if cached_result:
            self.stats['cache_hits'] += 1
            logger.debug(f"🎯 Cache hit for date {playout_date} → {cached_result.release_number}")
            return cached_result
        
        self.stats['cache_misses'] += 1
        
        try:
            # Query database
            self.stats['database_queries'] += 1
            release = await route_release_db.get_release_by_date(playout_date)
            
            if release:
                release_info = ReleaseInfo.from_route_release(release)
                
                # Cache the result
                self.cache.set(cache_key, release_info)
                
                logger.debug(f"📊 Database lookup for date {playout_date} → {release_info.release_number}")
                return release_info
            else:
                # No release found, use fallback
                logger.warning(f"⚠️ No release found for date {playout_date}, using fallback")
                return await self._get_fallback_release(playout_date)
                
        except Exception as e:
            logger.error(f"❌ Database error getting release for date {playout_date}: {e}")
            return await self._get_fallback_release(playout_date)
    
    async def get_release_by_number(self, release_number: str) -> Optional[ReleaseInfo]:
        """
        Get a Route release by its release number
        
        Args:
            release_number: Release number (e.g., "R54")
            
        Returns:
            ReleaseInfo if found, None otherwise
        """
        if not self._initialized:
            await self.initialize()
        
        # Check cache first
        cache_key = f"number_{release_number}"
        cached_result = self.cache.get(cache_key)
        
        if cached_result:
            self.stats['cache_hits'] += 1
            return cached_result
        
        self.stats['cache_misses'] += 1
        
        try:
            # Query database
            self.stats['database_queries'] += 1
            release = await route_release_db.get_release_by_number(release_number)
            
            if release:
                release_info = ReleaseInfo.from_route_release(release)
                
                # Cache the result
                self.cache.set(cache_key, release_info)
                
                return release_info
            
            return None
                
        except Exception as e:
            logger.error(f"❌ Database error getting release {release_number}: {e}")
            return None
    
    async def get_current_release(self) -> ReleaseInfo:
        """
        Get the current Route release based on today's date
        
        Returns:
            ReleaseInfo for current trading period
        """
        today = date.today()
        return await self.get_release_for_date(today)
    
    async def get_release_for_datetime(self, playout_datetime: datetime) -> ReleaseInfo:
        """
        Get the appropriate Route release for a datetime
        
        Args:
            playout_datetime: The datetime to lookup the release for
            
        Returns:
            ReleaseInfo with release details
        """
        playout_date = playout_datetime.date()
        return await self.get_release_for_date(playout_date)
    
    async def get_release_for_playout_string(self, playout_date_str: str) -> ReleaseInfo:
        """
        Get the appropriate Route release for a playout date string
        
        Args:
            playout_date_str: Date string in format YYYY-MM-DD or DD/MM/YYYY
            
        Returns:
            ReleaseInfo with release details
        """
        try:
            # Try different date formats
            if '-' in playout_date_str:
                playout_date = datetime.strptime(playout_date_str[:10], '%Y-%m-%d').date()
            elif '/' in playout_date_str:
                playout_date = datetime.strptime(playout_date_str[:10], '%d/%m/%Y').date()
            else:
                raise ValueError(f"Unknown date format: {playout_date_str}")
            
            return await self.get_release_for_date(playout_date)
            
        except Exception as e:
            logger.error(f"❌ Error parsing date string '{playout_date_str}': {e}")
            return await self._get_fallback_release(date.today())
    
    async def _get_fallback_release(self, playout_date: date) -> ReleaseInfo:
        """
        Get fallback release when database lookup fails
        
        Args:
            playout_date: Date for context
            
        Returns:
            ReleaseInfo with fallback data
        """
        self.stats['fallback_uses'] += 1
        
        # Use default release from config
        default_release_id = self.config.default_release_id
        
        # Create fallback release info
        fallback_release = ReleaseInfo(
            release_number=f"R{default_release_id}",
            name=f"Fallback Release R{default_release_id}",
            numeric_id=default_release_id,
            trading_period_start=playout_date - timedelta(days=90),  # 3 months before
            trading_period_end=playout_date + timedelta(days=90)     # 3 months after
        )
        
        logger.warning(f"🔄 Using fallback release R{default_release_id} for date {playout_date}")
        return fallback_release
    
    async def preload_releases(self, start_date: date, end_date: date):
        """
        Preload releases for a date range into cache
        
        Args:
            start_date: Start of date range
            end_date: End of date range
        """
        if not self._initialized:
            await self.initialize()
        
        logger.info(f"📥 Preloading releases for date range {start_date} to {end_date}")
        
        current_date = start_date
        preloaded_count = 0
        
        while current_date <= end_date:
            try:
                await self.get_release_for_date(current_date)
                preloaded_count += 1
                current_date += timedelta(days=7)  # Sample weekly
            except Exception as e:
                logger.warning(f"⚠️ Error preloading release for {current_date}: {e}")
                current_date += timedelta(days=7)
        
        logger.info(f"✅ Preloaded {preloaded_count} release lookups")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache and service statistics"""
        cache_stats = self.cache.get_stats()
        
        total_requests = self.stats['cache_hits'] + self.stats['cache_misses']
        hit_rate = (self.stats['cache_hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'cache_stats': cache_stats,
            'service_stats': self.stats,
            'hit_rate_percent': round(hit_rate, 2),
            'total_requests': total_requests
        }
    
    def clear_cache(self):
        """Clear the release cache"""
        self.cache.clear()
        logger.info("🗑️ Route release cache cleared")
    
    async def refresh_cache_for_date(self, playout_date: date):
        """Force refresh cache for a specific date"""
        cache_key = f"date_{playout_date.isoformat()}"
        self.cache.delete(cache_key)
        await self.get_release_for_date(playout_date)
        logger.debug(f"🔄 Refreshed cache for date {playout_date}")


# Global service instance
route_release_service = RouteReleaseService()


# Convenience functions for easy usage
async def get_release_for_playout_date(playout_date: date) -> ReleaseInfo:
    """Get Route release for a playout date"""
    return await route_release_service.get_release_for_date(playout_date)


async def get_release_for_playout_datetime(playout_datetime: datetime) -> ReleaseInfo:
    """Get Route release for a playout datetime"""
    return await route_release_service.get_release_for_datetime(playout_datetime)


async def get_release_for_playout_string(playout_date_str: str) -> ReleaseInfo:
    """Get Route release for a playout date string"""
    return await route_release_service.get_release_for_playout_string(playout_date_str)


async def get_current_route_release() -> ReleaseInfo:
    """Get current Route release"""
    return await route_release_service.get_current_release()


def get_release_service_stats() -> Dict[str, Any]:
    """Get service statistics"""
    return route_release_service.get_cache_stats()