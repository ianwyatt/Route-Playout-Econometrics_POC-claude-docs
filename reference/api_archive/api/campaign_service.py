# ABOUTME: High-level campaign service for playout analysis
# ABOUTME: Orchestrates data retrieval and formatting for UI

import pandas as pd
import asyncio
import time
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

from src.api.route_client import RouteAPIClient
from src.api.playout_processor import PlayoutProcessor
from src.utils.time_converter import TimeConverter
from src.config import (
    get_config, get_frame_config, get_entity_config,
    get_demo_config, get_campaign_config, get_spot_config
)
from src.paths import SAMPLE_PLAYOUT_CSV
from src.db.cache_queries import query_demographic_cache

logger = logging.getLogger(__name__)

class CampaignService:
    """Service for querying and processing campaign data"""
    
    def __init__(self):
        self.route_client = RouteAPIClient()
        self.playout_processor = PlayoutProcessor()
        self.time_converter = TimeConverter()
        
        # Load configuration
        self.config = get_config()
        self.frame_config = get_frame_config()
        self.entity_config = get_entity_config()
        self.demo_config = get_demo_config()
        self.campaign_config = get_campaign_config()
        self.spot_config = get_spot_config()
        
        # Load sample playout data
        self.playout_data = self._load_playout_data()
        
    def _load_playout_data(self) -> pd.DataFrame:
        """Load sample playout data from CSV"""
        if SAMPLE_PLAYOUT_CSV.exists():
            df = pd.read_csv(SAMPLE_PLAYOUT_CSV)
            # Convert date columns
            df['startdate'] = pd.to_datetime(df['startdate'])
            df['enddate'] = pd.to_datetime(df['enddate'])
            return df
        return pd.DataFrame()
    
    async def query_campaign(
        self,
        campaign_id: str,
        aggregate_by: str = "day"
    ) -> Dict[str, Any]:
        """
        Query campaign data with audience metrics

        Args:
            campaign_id: Campaign reference ID
            aggregate_by: Aggregation level (day, hour, frame)

        Returns:
            Dict with campaign metrics and details
        """
        start_time = time.time()

        # ========================================
        # STEP 1: CHECK POSTGRESQL CACHE FIRST (Skip if in mock mode)
        # ========================================
        # Skip PostgreSQL cache if we're in mock/demo mode
        use_mock = getattr(self.config.route_api, 'use_mock', False)

        if not use_mock:
            cache_start = time.time()

            try:
                # Query PostgreSQL cache - get all available data for campaign
                # Note: start_date and end_date can be None to get full campaign date range
                cached_data = query_demographic_cache(
                    campaign_id=campaign_id,
                    start_date=None,  # Get all available dates
                    end_date=None,
                    demographic_segments=None,  # Get all 7 demographics
                    use_ms01=True  # Use MS-01 production database
                )

                if cached_data is not None and not cached_data.empty:
                    # ✅ CACHE HIT!
                    cache_time_ms = (time.time() - cache_start) * 1000
                    logger.info(
                        f"✅ PostgreSQL Cache HIT for campaign {campaign_id} "
                        f"({len(cached_data)} records, {cache_time_ms:.1f}ms)"
                    )

                    # Format cached data for UI
                    result = self._format_cached_data_for_ui(cached_data, campaign_id, aggregate_by)
                    result['from_cache'] = True
                    result['cache_type'] = 'postgresql'
                    result['response_time_ms'] = cache_time_ms
                    result['total_time'] = cache_time_ms

                    return result
                else:
                    # Cache MISS - fall through to API workflow
                    cache_time_ms = (time.time() - cache_start) * 1000
                    logger.info(
                        f"⚠️ PostgreSQL Cache MISS for campaign {campaign_id} "
                        f"({cache_time_ms:.1f}ms) - calling Route API"
                    )

            except Exception as e:
                # Cache query failed - log and fall through to API workflow
                cache_time_ms = (time.time() - cache_start) * 1000
                logger.warning(
                    f"❌ PostgreSQL Cache ERROR for campaign {campaign_id}: {e} "
                    f"({cache_time_ms:.1f}ms) - falling back to Route API"
                )

        # ========================================
        # STEP 2: FALLBACK TO EXISTING API WORKFLOW
        # ========================================
        # Check if this is a campaign that should use playout processor
        # Skip playout processor for 16012 to use our new mock data with real Route numbers
        if campaign_id in ["16013", "16014", "16015"]:
            # Use playout processor for campaigns with mock data
            try:
                # For 16015, use actual playout data from 16012
                # For 16013-16014, process normally
                processor_campaign_id = "16012" if campaign_id == "16015" else campaign_id
                result = await self.playout_processor.process_playout_campaign(processor_campaign_id)
                if result:
                    # Update campaign ID to match request
                    result['campaign_id'] = campaign_id
                    if campaign_id == "16015":
                        result['campaign_name'] = "Real APIs Demo"
                    elif campaign_id == "16013":
                        result['campaign_name'] = "Brand Campaign"
                    elif campaign_id == "16014":
                        result['campaign_name'] = "Q4 Campaign"
                    # Add timing info
                    result['api_response_time'] = (time.time() - start_time) * 1000
                    result['total_time'] = result['api_response_time']
                    return result
                else:
                    # Playout processor returned None, fall back to mock
                    print(f"Warning: Playout processor returned None for campaign {campaign_id}")
            except Exception as e:
                print(f"Error processing campaign {campaign_id} with playout processor: {e}")
                # Fall through to regular mock data generation
        
        # Filter playout data for campaign
        # Force campaign 16012 to use mock data with real frame IDs from CSV
        if campaign_id == "16012":
            # Always use mock data for 16012 to get real frame IDs from CSV
            campaign_data = self._generate_mock_campaign_data(campaign_id)
        elif self.playout_data.empty:
            # Use mock data for demo
            campaign_data = self._generate_mock_campaign_data(campaign_id)
        else:
            # Filter real data
            campaign_data = self.playout_data[
                self.playout_data['buyercampaignref'] == float(campaign_id)
            ] if campaign_id.isdigit() else pd.DataFrame()
            
            if campaign_data.empty:
                # Generate mock data if campaign not found
                campaign_data = self._generate_mock_campaign_data(campaign_id)
        
        # Process playouts
        playouts = []
        for _, row in campaign_data.iterrows():
            # Handle frame ID - could be int or string
            frame_id = row.get('frameid', self.frame_config.default_frame_id)
            if isinstance(frame_id, str) and not frame_id.isdigit():
                # Skip non-numeric frame IDs or use a default
                frame_id = self.frame_config.default_frame_id
            else:
                frame_id = int(frame_id)
                
            playout = {
                'frameid': frame_id,
                'startdate': row['startdate'],
                'enddate': row['enddate'],
                'spotlength': int(row.get('spotlength', self.spot_config.default_spot_length_ms)),
                'media_owner_id': int(row.get('spacemediaownerid', self.entity_config.default_media_owner_id)),
                'start_route': self.time_converter.format_for_route_api(
                    self.time_converter.round_to_daypart(row['startdate'])
                ),
                'end_route': self.time_converter.format_for_route_api(
                    self.time_converter.round_to_daypart(row['enddate'])
                )
            }
            playouts.append(playout)
        
        # Get audience data from Route API
        playouts_with_audience = await self.route_client.get_batch_audiences(
            playouts[:self.campaign_config.max_playouts_demo]
        )  # Limit for demo
        
        # Calculate totals
        total_impacts = sum(p['audience'].get('impacts', 0) for p in playouts_with_audience if p['audience'].get('success'))
        total_reach = sum(p['audience'].get('reach', 0) for p in playouts_with_audience if p['audience'].get('success'))
        avg_frequency = total_impacts / total_reach if total_reach > 0 else 0
        total_playouts = len(playouts_with_audience)
        
        # Aggregate data
        aggregated = self._aggregate_data(playouts_with_audience, aggregate_by)
        
        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000

        # Get proper date range from all generated data (not just processed playouts)
        full_date_range = self._get_date_range(playouts)  # Use all playouts for date range

        return {
            'success': True,
            'campaign_id': campaign_id,
            'campaign_name': f"Campaign {campaign_id}",
            'metrics': {
                'total_playouts': total_playouts,
                'total_impacts': round(total_impacts, 4),  # Total impressions
                'total_reach': round(total_reach, 2),  # Unique people
                'avg_frequency': round(avg_frequency, 1),  # Avg views per person
                'unique_frames': len(set(p['frameid'] for p in playouts)),
                'date_range': full_date_range,
                'processing_time_ms': round(processing_time, 0)
            },
            'playouts': playouts_with_audience,
            'aggregated': aggregated,
            'summary_metrics': {
                'reach': f"{int(total_reach):,}",
                'impacts': f"{total_impacts:.3f}k",
                'frequency': f"{avg_frequency:.1f}",
                'performance': f"{processing_time:.0f}ms",
                'efficiency': "3 days → 3 seconds"
            },
            # Add playout_data for UI compatibility
            'playout_data': {
                'frame_count': len(set(p['frameid'] for p in playouts)),
                'date_range': full_date_range,
                'total_spots': len(playouts),  # Total spots generated (not just processed)
            },
            # Add summary for UI
            'summary': {
                'total_impacts': total_impacts,
                'total_reach': total_reach,
                'avg_frequency': avg_frequency,
                'total_spots': total_playouts,
                'unique_frames': len(set(p['frameid'] for p in playouts)),
                'total_grps': total_impacts / 1000,  # Simplified GRP calculation
                'coverage': total_reach / 1000000 if total_reach > 0 else 0  # Coverage as percentage of population
            },
            # Cache metadata (API workflow = no cache)
            'from_cache': False,
            'cache_type': 'none',
            'response_time_ms': round(processing_time, 0),
            'total_time': round(processing_time, 0)
        }
    
    def _generate_mock_campaign_data(self, campaign_id: str) -> pd.DataFrame:
        """Generate mock campaign data for demo"""
        import random
        from src.ui.data.mock_geo_data import get_mock_campaign_geo_data
        
        # For campaign 16012, use the new geo data with real Route numbers
        if campaign_id == "16012":
            # Get the geo data with real frame information
            geo_data = get_mock_campaign_geo_data(campaign_id)
            frames = geo_data.get('frames', [])
            
            # Convert frames to playout format
            data = []
            base_date = pd.Timestamp('2025-06-01')  # Week starting June 1 (R54 trading period)
            
            for frame in frames:
                # Create multiple playouts per frame across the week
                for day in range(7):  # 7 days in the week
                    for hour in [7, 12, 17]:  # Morning, noon, evening
                        start = base_date + pd.Timedelta(days=day, hours=hour, minutes=random.randint(0, 59))
                        spot_length = 10000  # 10 seconds
                        end = start + pd.Timedelta(milliseconds=spot_length)
                        
                        data.append({
                            'frameid': frame['frame_id'],
                            'startdate': start,
                            'enddate': end,
                            'spotlength': spot_length,
                            'buyercampaignref': campaign_id,
                            'spacemediaownerid': random.choice(self.entity_config.media_owner_ids),
                            'spacebuyerid': self.entity_config.default_buyer_id,
                            'spaceagencyid': self.entity_config.default_agency_id,
                            'spacebrandid': self.entity_config.default_brand_id,
                            'daily_impacts': frame.get('daily_impacts', 0),
                            'daily_reach': frame.get('daily_reach', 0),
                            'latitude': frame.get('latitude', 0),
                            'longitude': frame.get('longitude', 0),
                            'city': frame.get('city', 'Unknown')
                        })
            
            return pd.DataFrame(data) if data else self._generate_default_mock_data(campaign_id)
        
        # For other campaigns, use the default mock generation
        return self._generate_default_mock_data(campaign_id)
    
    def _generate_default_mock_data(self, campaign_id: str) -> pd.DataFrame:
        """Generate default mock campaign data"""
        import random
        
        # Generate playouts over configured days
        num_playouts = random.randint(*self.campaign_config.mock_playouts_range)
        
        data = []
        base_date = pd.Timestamp(self.demo_config.demo_base_date)
        
        for i in range(num_playouts):
            # Random time during configured active hours
            hour = random.randint(*self.campaign_config.mock_hours_range)
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            
            start = base_date + pd.Timedelta(
                days=random.randint(0, self.campaign_config.mock_days_range - 1),
                hours=hour,
                minutes=minute,
                seconds=second
            )
            
            # Spot length from configured options
            spot_length = random.choice(self.spot_config.available_spot_lengths_ms)
            end = start + pd.Timedelta(milliseconds=spot_length)
            
            data.append({
                'frameid': self.frame_config.default_frame_id,
                'startdate': start,
                'enddate': end,
                'spotlength': spot_length,
                'buyercampaignref': campaign_id,
                'spacemediaownerid': random.choice(self.entity_config.media_owner_ids),
                'spacebuyerid': self.entity_config.default_buyer_id,
                'spaceagencyid': self.entity_config.default_agency_id,
                'spacebrandid': self.entity_config.default_brand_id
            })
        
        return pd.DataFrame(data)
    
    def _aggregate_data(self, playouts: List[Dict], aggregate_by: str) -> Dict:
        """Aggregate playout data by specified level"""
        if aggregate_by == "day":
            aggregated = {}
            for playout in playouts:
                day = playout['startdate'].strftime('%Y-%m-%d')
                if day not in aggregated:
                    aggregated[day] = {
                        'date': day,
                        'playouts': 0,
                        'impacts': 0,
                        'reach': 0
                    }
                
                aggregated[day]['playouts'] += 1
                if playout['audience'].get('success'):
                    aggregated[day]['impacts'] += playout['audience'].get('impacts', 0)
                    aggregated[day]['reach'] += playout['audience'].get('reach', 0)
            
            return list(aggregated.values())
        
        elif aggregate_by == "frame":
            aggregated = {}
            for playout in playouts:
                frame = str(playout['frameid'])
                if frame not in aggregated:
                    aggregated[frame] = {
                        'frame_id': frame,
                        'playouts': 0,
                        'impacts': 0,
                        'reach': 0
                    }
                
                aggregated[frame]['playouts'] += 1
                if playout['audience'].get('success'):
                    aggregated[frame]['impacts'] += playout['audience'].get('impacts', 0)
                    aggregated[frame]['reach'] += playout['audience'].get('reach', 0)
            
            return list(aggregated.values())
        
        return []
    
    def _get_date_range(self, playouts: List[Dict]) -> str:
        """Get date range of playouts"""
        if not playouts:
            return "No data"

        dates = [p['startdate'] for p in playouts]
        min_date = min(dates)
        max_date = max(dates)

        if min_date.date() == max_date.date():
            return min_date.strftime('%Y-%m-%d')
        else:
            days = (max_date - min_date).days + 1
            return f"{min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')} ({days} days)"

    def _format_cached_data_for_ui(
        self,
        cached_df: pd.DataFrame,
        campaign_id: str,
        aggregate_by: str
    ) -> Dict[str, Any]:
        """
        Format cached DataFrame from PostgreSQL for UI consumption.

        Args:
            cached_df: DataFrame from query_demographic_cache()
                      Columns: [time_window_start, demographic_segment, impacts]
            campaign_id: Campaign reference ID
            aggregate_by: Aggregation level ('day', 'hour', 'frame')

        Returns:
            Dict with formatted data matching existing UI expectations

        Note: Impacts are already multiplied by 1000 by query_demographic_cache()
        """
        # Extract date range from cached data
        min_date = cached_df['time_window_start'].min()
        max_date = cached_df['time_window_start'].max()
        days = (max_date - min_date).days + 1

        if min_date.date() == max_date.date():
            date_range_str = min_date.strftime('%Y-%m-%d')
        else:
            date_range_str = f"{min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')} ({days} days)"

        # Calculate total metrics (aggregate across all demographics and time windows)
        # Note: We need to sum 'all_adults' demographic only to avoid double-counting
        all_adults_data = cached_df[cached_df['demographic_segment'] == 'all_adults']

        total_impacts = all_adults_data['impacts'].sum()
        total_windows = len(all_adults_data)  # Number of 15-min time windows

        # Since we don't have reach in the cache, we'll calculate a conservative estimate
        # Frequency assumption: ~3.5 average (typical for OOH campaigns)
        estimated_frequency = 3.5
        estimated_reach = total_impacts / estimated_frequency if total_impacts > 0 else 0

        # Count unique demographics
        demographics = cached_df['demographic_segment'].unique().tolist()

        # Prepare aggregated data by day (if requested)
        aggregated = []
        if aggregate_by == "day":
            # Group by date and demographic
            cached_df['date'] = pd.to_datetime(cached_df['time_window_start']).dt.date
            daily_groups = cached_df[cached_df['demographic_segment'] == 'all_adults'].groupby('date')

            for date, group in daily_groups:
                aggregated.append({
                    'date': str(date),
                    'impacts': group['impacts'].sum(),
                    'reach': group['impacts'].sum() / estimated_frequency,  # Estimated
                    'windows': len(group)
                })

        # Return data in UI-compatible format
        return {
            'success': True,
            'campaign_id': campaign_id,
            'campaign_name': f"Campaign {campaign_id}",
            'metrics': {
                'total_playouts': total_windows,
                'total_impacts': round(total_impacts, 4),
                'total_reach': round(estimated_reach, 2),
                'avg_frequency': round(estimated_frequency, 1),
                'unique_frames': 0,  # Not available in cache (could be added later)
                'date_range': date_range_str,
                'processing_time_ms': 0  # Filled in by caller
            },
            'playouts': [],  # Not available in aggregated cache
            'aggregated': aggregated,
            'summary_metrics': {
                'reach': f"{int(estimated_reach):,}",
                'impacts': f"{total_impacts/1000:.3f}k",
                'frequency': f"{estimated_frequency:.1f}",
                'performance': "0ms",  # Filled in by caller
                'efficiency': "PostgreSQL cache"
            },
            'playout_data': {
                'frame_count': 0,  # Not available in cache
                'date_range': date_range_str,
                'total_spots': total_windows,
            },
            'summary': {
                'total_impacts': total_impacts,
                'total_reach': estimated_reach,
                'avg_frequency': estimated_frequency,
                'total_spots': total_windows,
                'unique_frames': 0,
                'total_grps': total_impacts / 1000,
                'coverage': estimated_reach / 1000000 if estimated_reach > 0 else 0
            },
            # Demographics available in cache
            'demographics': demographics,
            'demographic_data': cached_df.to_dict('records')  # Raw cache data for advanced UI
        }

    async def get_available_campaigns(self) -> List[Dict]:
        """Get list of available campaigns for demo"""
        if not self.playout_data.empty:
            campaigns = self.playout_data['buyercampaignref'].dropna().unique()
            return [
                {
                    'campaign_id': str(int(c)),
                    'name': f"Campaign {int(c)}",
                    'playouts': len(self.playout_data[self.playout_data['buyercampaignref'] == c])
                }
                for c in campaigns
            ]
        else:
            # Mock campaigns from demo config
            return self.config.get_demo_campaigns()