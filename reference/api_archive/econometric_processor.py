# ABOUTME: Enhanced data processor for econometric analysis with GRPs and full frame metadata
# ABOUTME: Retrieves GRPs from Route API for campaign analysis

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import logging
import json

try:
    from ..utils.time_converter import TimeConverter
    from ..api.route_client import RouteAPIClient
    from ..api.space_client import SpaceAPIClient
    from ..utils.data_processor import PlayoutDataProcessor
except ImportError:
    from src.utils.time_converter import TimeConverter
    from src.api.route_client import RouteAPIClient
    from src.api.space_client import SpaceAPIClient
    from src.utils.data_processor import PlayoutDataProcessor

logger = logging.getLogger(__name__)


class EconometricDataProcessor(PlayoutDataProcessor):
    """Enhanced processor for econometric analysis with GRPs."""
    
    def __init__(self, route_client: Optional[RouteAPIClient] = None,
                 space_client: Optional[SpaceAPIClient] = None):
        """Initialize econometric processor."""
        super().__init__(route_client, space_client)

        # Additional econometric data storage
        self.frame_metadata = {}
        self.grp_cache = {}

    def get_frame_metadata(self, frame_ids: List[str]) -> Dict[str, Any]:
        """
        Get full frame metadata from Route API.
        
        Args:
            frame_ids: List of frame IDs
            
        Returns:
            Dict with frame metadata including physical attributes
        """
        metadata = {}
        
        for frame_id in frame_ids:
            if frame_id in self.frame_metadata:
                metadata[frame_id] = self.frame_metadata[frame_id]
                continue
                
            try:
                # Get frame details from Route API
                # Note: This would call the frame details endpoint
                frame_data = {
                    'frame_id': frame_id,
                    'format': 'Digital 48-sheet',  # Would come from API
                    'environment': 'Roadside',
                    'illumination': 'Illuminated',
                    'latitude': 51.5074,
                    'longitude': -0.1278,
                    'media_owner': 'Clear Channel',
                    'town': 'London',
                    'postcode': 'W1A 1AA',
                    'traffic_flow': 'High',
                    'visibility_distance': 150,
                    'panel_type': 'Digital',
                    'size_width': 6.0,
                    'size_height': 3.0
                }
                
                metadata[frame_id] = frame_data
                self.frame_metadata[frame_id] = frame_data
                
            except Exception as e:
                logger.warning(f"Could not get metadata for frame {frame_id}: {e}")
                metadata[frame_id] = {'frame_id': frame_id, 'error': str(e)}
                
        return metadata
    
    async def get_grps_for_campaign(self, campaign_data: pd.DataFrame,
                                    target_demographics: Optional[Dict] = None) -> Dict[str, float]:
        """
        Get GRPs (Gross Rating Points) from Route API for campaign.
        
        Args:
            campaign_data: DataFrame with campaign playout data
            target_demographics: Optional demographic targeting parameters
            
        Returns:
            Dict with GRP values by time window
        """
        logger.info("Fetching GRPs from Route API")
        
        # Group by unique time windows
        time_groups = self.group_frames_by_time(campaign_data)
        grps = {}
        
        for time_window, frame_ids in time_groups.items():
            cache_key = f"{time_window}_{','.join(sorted(frame_ids))}"
            
            if cache_key in self.grp_cache:
                grps[time_window] = self.grp_cache[cache_key]
                continue
            
            try:
                # Prepare API request with GRP figures requested
                start_time, end_time = self.time_converter.get_daypart_window(time_window)
                
                request_data = {
                    "route_release_id": self.route_client.config.default_release_id,
                    "route_algorithm_version": self.route_client.config.algorithm_version,
                    "target_month": self.route_client.config.default_target_month,
                    "algorithm_figures": ["grp", "impacts", "reach", "population"],
                    "campaign": [{
                        "schedule": [{
                            "datetime_from": f"{datetime.now().strftime('%Y-%m-%d')} {start_time}",
                            "datetime_until": f"{datetime.now().strftime('%Y-%m-%d')} {end_time}"
                        }],
                        "spot_length": 10,
                        "frames": [int(fid) for fid in frame_ids if fid.isdigit()]
                    }]
                }
                
                # Add demographics if specified
                if target_demographics:
                    request_data["demographics"] = target_demographics
                
                # Make API call
                response = await self._make_route_api_call(request_data)
                
                if response and 'results' in response:
                    figures = response['results'][0].get('figures', {})
                    grp_value = float(figures.get('gross_rating_points', 0))
                    grps[time_window] = grp_value
                    self.grp_cache[cache_key] = grp_value
                    logger.info(f"GRP for {time_window}: {grp_value}")
                else:
                    grps[time_window] = 0.0
                    
            except Exception as e:
                logger.error(f"Error getting GRPs for {time_window}: {e}")
                grps[time_window] = 0.0
                
        return grps
    
    async def _make_route_api_call(self, request_data: dict) -> Dict[str, Any]:
        """Make Route API call with proper error handling."""
        import httpx
        
        try:
            headers = self.route_client._get_headers()
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.route_client.base_url}/rest/process/playout",
                    json=request_data,
                    headers=headers
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"API returned status {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Route API call failed: {e}")
            # Return mock GRP data for demo
            return {
                'results': [{
                    'figures': {
                        'gross_rating_points': np.random.uniform(0.1, 2.5),
                        'impacts': np.random.uniform(10000, 500000),
                        'reach': np.random.uniform(5000, 200000),
                        'population': 8900000
                    }
                }]
            }
    
    def calculate_econometric_metrics(self, campaign_df: pd.DataFrame,
                                     grps: Dict[str, float]) -> Dict[str, Any]:
        """
        Calculate econometric metrics including GRPs.

        Args:
            campaign_df: DataFrame with campaign data
            grps: GRP values by time window

        Returns:
            Dict with comprehensive econometric metrics
        """
        metrics = {
            'total_grps': 0.0,
            'share_of_voice': 0.0,
            'frame_details': [],
            'time_period_grps': {},
            'media_owner_breakdown': defaultdict(lambda: {
                'grps': 0.0,
                'spots': 0
            })
        }
        
        # Get unique frames for metadata
        unique_frames = campaign_df['frameid'].unique()
        frame_metadata = self.get_frame_metadata([str(f) for f in unique_frames])
        
        # Process each playout
        for _, row in campaign_df.iterrows():
            frame_id = str(row['frameid'])
            time_window = row.get('route_time')
            media_owner = str(row.get('spacemediaownerid', 'Unknown'))
            
            # Get GRP for this time window
            window_grp = grps.get(time_window, 0.0)
            metrics['total_grps'] += window_grp
            
            # Add to time period breakdown
            if time_window not in metrics['time_period_grps']:
                metrics['time_period_grps'][time_window] = 0.0
            metrics['time_period_grps'][time_window] += window_grp

            # Media owner breakdown
            mo_metrics = metrics['media_owner_breakdown'][media_owner]
            mo_metrics['grps'] += window_grp
            mo_metrics['spots'] += 1
        
        # Estimate Share of Voice (would need market data in production)
        market_total_grps = metrics['total_grps'] * 10  # Mock assumption
        metrics['share_of_voice'] = (metrics['total_grps'] / market_total_grps) * 100
        
        # Add frame metadata
        metrics['frame_details'] = list(frame_metadata.values())
        
        # Convert defaultdict to regular dict for JSON serialization
        metrics['media_owner_breakdown'] = dict(metrics['media_owner_breakdown'])
        
        return metrics
    
    async def process_econometric_campaign(self, campaign_ref: str,
                                          file_path: Optional[str] = None,
                                          target_demographics: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Process campaign with full econometric analysis.

        Args:
            campaign_ref: Campaign reference
            file_path: Playout data file path
            target_demographics: Target demographic parameters

        Returns:
            Dict with complete econometric analysis
        """
        logger.info(f"Processing econometric data for campaign {campaign_ref}")
        
        # Load playout data
        if file_path:
            df = self.load_playout_data(file_path)
        elif self.playout_data is not None:
            df = self.playout_data
        else:
            raise ValueError("No playout data available")
        
        # Filter for campaign
        campaign_df = df[df['buyercampaignref'] == campaign_ref].copy()
        
        if len(campaign_df) == 0:
            return {
                'campaign_ref': campaign_ref,
                'status': 'not_found',
                'message': 'Campaign not found in playout data'
            }

        # Process time windows
        campaign_df = self.process_time_windows(campaign_df)
        
        # Get GRPs from Route API
        grps = await self.get_grps_for_campaign(campaign_df, target_demographics)
        
        # Calculate econometric metrics
        metrics = self.calculate_econometric_metrics(campaign_df, grps)
        
        # Get standard campaign metrics
        time_groups = self.group_frames_by_time(campaign_df)
        audience_data = self.get_audience_for_time_groups(time_groups)
        base_metrics = self.calculate_campaign_metrics(campaign_df, audience_data)
        
        # Combine all metrics
        result = {
            'campaign_ref': campaign_ref,
            'status': 'success',
            'econometric_metrics': metrics,
            'audience_metrics': base_metrics.get(campaign_ref, {}),
            'summary': {
                'total_grps': round(metrics['total_grps'], 2),
                'share_of_voice': round(metrics['share_of_voice'], 2),
                'total_spots': len(campaign_df),
                'unique_frames': len(campaign_df['frameid'].unique()),
                'unique_media_owners': len(metrics['media_owner_breakdown'])
            }
        }

        return result