# ABOUTME: Data processing utility for Route Playout Econometrics POC
# ABOUTME: Loads playout CSV data, processes campaigns, and calculates aggregated metrics

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import logging

try:
    from ..utils.time_converter import TimeConverter
    from ..api.route_client import RouteAPIClient
    from ..api.space_client import SpaceAPIClient
except ImportError:
    from src.utils.time_converter import TimeConverter
    from src.api.route_client import RouteAPIClient
    from src.api.space_client import SpaceAPIClient

logger = logging.getLogger(__name__)


class PlayoutDataProcessor:
    """Processes playout data for Route audience analysis."""
    
    def __init__(self, route_client: Optional[RouteAPIClient] = None, 
                 space_client: Optional[SpaceAPIClient] = None):
        """
        Initialize data processor.
        
        Args:
            route_client: Route API client (creates new if not provided)
            space_client: SPACE API client (creates new if not provided)
        """
        self.route_client = route_client or RouteAPIClient()
        self.space_client = space_client or SpaceAPIClient()
        self.time_converter = TimeConverter()
        self.logger = logging.getLogger(__name__)
        
        # Cache for processed data
        self.playout_data = None
        self.processed_campaigns = {}
    
    def load_playout_data(self, file_path: str) -> pd.DataFrame:
        """
        Load playout data from CSV file.
        
        Args:
            file_path: Path to playout CSV file
            
        Returns:
            DataFrame with playout data
        """
        try:
            self.logger.info(f"Loading playout data from {file_path}")
            
            # Load CSV with proper column handling
            df = pd.read_csv(file_path)
            
            # Validate required columns
            required_columns = [
                'frameid', 'startdate', 'startutcoffset', 'enddate', 'endutcoffset',
                'spotlength', 'spacemediaownerid', 'spacebuyerid', 'spaceagencyid',
                'buyercampaignref', 'creativeid'
            ]
            
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")
            
            # Convert data types
            df['frameid'] = df['frameid'].astype(str)
            df['spacemediaownerid'] = df['spacemediaownerid'].astype(str)
            df['spacebuyerid'] = df['spacebuyerid'].astype(str)
            df['spaceagencyid'] = df['spaceagencyid'].astype(str)
            df['spotlength'] = pd.to_numeric(df['spotlength'], errors='coerce')
            
            # Handle missing values
            df['buyercampaignref'] = df['buyercampaignref'].fillna('Unknown')
            df['creativeid'] = df['creativeid'].fillna('Unknown')
            
            self.playout_data = df
            self.logger.info(f"Loaded {len(df)} playout records")
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error loading playout data: {e}")
            raise
    
    def process_time_windows(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process playout times into Route API time windows.
        
        Args:
            df: DataFrame with playout data
            
        Returns:
            DataFrame with added time window columns
        """
        self.logger.info("Processing time windows")
        
        processed_times = []
        for _, row in df.iterrows():
            try:
                route_time, proportion = self.time_converter.process_playout_spot(
                    row['startdate'],
                    row['enddate'], 
                    row['startutcoffset'],
                    row['endutcoffset'],
                    row['spotlength']
                )
                
                processed_times.append({
                    'route_time': route_time,
                    'audience_proportion': proportion
                })
                
            except Exception as e:
                self.logger.warning(f"Error processing time for row: {e}")
                processed_times.append({
                    'route_time': None,
                    'audience_proportion': 0.0
                })
        
        # Add processed columns
        time_df = pd.DataFrame(processed_times)
        result_df = pd.concat([df, time_df], axis=1)
        
        # Remove rows with invalid times
        result_df = result_df.dropna(subset=['route_time'])
        
        self.logger.info(f"Processed {len(result_df)} valid time windows")
        return result_df
    
    def group_frames_by_time(self, df: pd.DataFrame) -> Dict[str, List[str]]:
        """
        Group frame IDs by time windows for efficient API calls.
        
        Args:
            df: DataFrame with processed time data
            
        Returns:
            Dict mapping time windows to frame ID lists
        """
        self.logger.info("Grouping frames by time windows")
        
        time_groups = defaultdict(set)
        
        for _, row in df.iterrows():
            if pd.notna(row['route_time']):
                time_groups[row['route_time']].add(str(row['frameid']))
        
        # Convert sets to lists
        result = {time_window: list(frame_ids) for time_window, frame_ids in time_groups.items()}
        
        self.logger.info(f"Created {len(result)} time window groups")
        return result
    
    def get_audience_for_time_groups(self, time_groups: Dict[str, List[str]]) -> Dict[str, Any]:
        """
        Get Route API audience data for time groups.
        
        Args:
            time_groups: Dict mapping time windows to frame IDs
            
        Returns:
            Dict with audience data for each time window
        """
        self.logger.info(f"Getting audience data for {len(time_groups)} time groups")
        
        audience_data = {}
        total_requests = 0
        total_response_time = 0
        
        for time_window, frame_ids in time_groups.items():
            try:
                # Create time window string for API
                start_time, end_time = self.time_converter.get_daypart_window(time_window)
                api_time_window = f"{start_time} to {end_time}"
                
                # Get audience data
                response = self.route_client.get_playout_audience(frame_ids, api_time_window)
                
                audience_data[time_window] = {
                    'audience_count': response.audience_count,
                    'frame_ids': response.frame_ids,
                    'demographics': response.demographics,
                    'response_time_ms': response.response_time_ms,
                    'cached': response.cached
                }
                
                total_requests += 1
                total_response_time += response.response_time_ms
                
            except Exception as e:
                self.logger.error(f"Error getting audience for {time_window}: {e}")
                audience_data[time_window] = {
                    'audience_count': 0,
                    'frame_ids': frame_ids,
                    'demographics': {},
                    'response_time_ms': 0,
                    'cached': False,
                    'error': str(e)
                }
        
        avg_response_time = total_response_time / total_requests if total_requests > 0 else 0
        self.logger.info(f"Completed {total_requests} API requests, avg response time: {avg_response_time:.1f}ms")
        
        return audience_data
    
    def calculate_campaign_metrics(self, df: pd.DataFrame, audience_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate aggregated metrics for campaigns.
        
        Args:
            df: DataFrame with playout data
            audience_data: Audience data from Route API
            
        Returns:
            Dict with campaign metrics
        """
        self.logger.info("Calculating campaign metrics")
        
        campaign_metrics = defaultdict(lambda: {
            'total_audience': 0,
            'total_spots': 0,
            'unique_frames': set(),
            'media_owners': set(),
            'buyers': set(),
            'agencies': set(),
            'time_windows': set(),
            'total_duration_ms': 0,
            'avg_spot_length': 0
        })
        
        # Process each playout record
        for _, row in df.iterrows():
            campaign_ref = row.get('buyercampaignref', 'Unknown')
            time_window = row.get('route_time')
            
            if time_window and time_window in audience_data:
                # Calculate proportional audience for this spot
                audience_count = audience_data[time_window]['audience_count']
                proportional_audience = audience_count * row.get('audience_proportion', 1.0)
                
                metrics = campaign_metrics[campaign_ref]
                metrics['total_audience'] += proportional_audience
                metrics['total_spots'] += 1
                metrics['unique_frames'].add(str(row['frameid']))
                metrics['media_owners'].add(str(row['spacemediaownerid']))
                metrics['buyers'].add(str(row['spacebuyerid']))
                metrics['agencies'].add(str(row['spaceagencyid']))
                metrics['time_windows'].add(time_window)
                metrics['total_duration_ms'] += row.get('spotlength', 0)
        
        # Convert sets to counts and calculate averages
        final_metrics = {}
        for campaign_ref, metrics in campaign_metrics.items():
            final_metrics[campaign_ref] = {
                'total_audience': int(metrics['total_audience']),
                'total_spots': metrics['total_spots'],
                'unique_frames': len(metrics['unique_frames']),
                'unique_media_owners': len(metrics['media_owners']),
                'unique_buyers': len(metrics['buyers']),
                'unique_agencies': len(metrics['agencies']),
                'unique_time_windows': len(metrics['time_windows']),
                'total_duration_ms': metrics['total_duration_ms'],
                'avg_spot_length': metrics['total_duration_ms'] / metrics['total_spots'] if metrics['total_spots'] > 0 else 0,
                'frame_ids': list(metrics['unique_frames']),
                'media_owner_ids': list(metrics['media_owners']),
                'buyer_ids': list(metrics['buyers']),
                'agency_ids': list(metrics['agencies'])
            }
        
        self.logger.info(f"Calculated metrics for {len(final_metrics)} campaigns")
        return final_metrics
    
    def aggregate_by_media_owner(self, df: pd.DataFrame, audience_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aggregate metrics by media owner.
        
        Args:
            df: DataFrame with playout data
            audience_data: Audience data from Route API
            
        Returns:
            Dict with media owner aggregated metrics
        """
        self.logger.info("Aggregating by media owner")
        
        media_owner_metrics = defaultdict(lambda: {
            'total_audience': 0,
            'total_spots': 0,
            'unique_frames': set(),
            'campaigns': set(),
            'buyers': set()
        })
        
        for _, row in df.iterrows():
            media_owner_id = str(row['spacemediaownerid'])
            time_window = row.get('route_time')
            
            if time_window and time_window in audience_data:
                audience_count = audience_data[time_window]['audience_count']
                proportional_audience = audience_count * row.get('audience_proportion', 1.0)
                
                metrics = media_owner_metrics[media_owner_id]
                metrics['total_audience'] += proportional_audience
                metrics['total_spots'] += 1
                metrics['unique_frames'].add(str(row['frameid']))
                metrics['campaigns'].add(row.get('buyercampaignref', 'Unknown'))
                metrics['buyers'].add(str(row['spacebuyerid']))
        
        # Convert to final format
        final_metrics = {}
        for media_owner_id, metrics in media_owner_metrics.items():
            final_metrics[media_owner_id] = {
                'total_audience': int(metrics['total_audience']),
                'total_spots': metrics['total_spots'],
                'unique_frames': len(metrics['unique_frames']),
                'unique_campaigns': len(metrics['campaigns']),
                'unique_buyers': len(metrics['buyers'])
            }
        
        return final_metrics
    
    def process_campaign_query(self, campaign_ref: str, file_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a specific campaign query with full enrichment.
        
        Args:
            campaign_ref: Campaign reference to query
            file_path: Path to playout data (uses cached if not provided)
            
        Returns:
            Dict with enriched campaign data
        """
        if campaign_ref in self.processed_campaigns:
            self.logger.info(f"Returning cached results for campaign {campaign_ref}")
            return self.processed_campaigns[campaign_ref]
        
        # Load data if needed
        if file_path:
            df = self.load_playout_data(file_path)
        elif self.playout_data is not None:
            df = self.playout_data
        else:
            raise ValueError("No playout data available - provide file_path or load data first")
        
        # Filter for campaign
        campaign_df = df[df['buyercampaignref'] == campaign_ref].copy()
        
        if len(campaign_df) == 0:
            return {
                'campaign_ref': campaign_ref,
                'status': 'not_found',
                'total_spots': 0,
                'total_audience': 0
            }
        
        self.logger.info(f"Processing campaign {campaign_ref} with {len(campaign_df)} spots")
        
        # Process time windows
        campaign_df = self.process_time_windows(campaign_df)
        
        # Group by time
        time_groups = self.group_frames_by_time(campaign_df)
        
        # Get audience data
        audience_data = self.get_audience_for_time_groups(time_groups)
        
        # Calculate metrics
        campaign_metrics = self.calculate_campaign_metrics(campaign_df, audience_data)
        
        # Get enriched lookups
        enriched_data = self._enrich_campaign_data(campaign_df, campaign_metrics.get(campaign_ref, {}))
        
        result = {
            'campaign_ref': campaign_ref,
            'status': 'success',
            **enriched_data,
            'processing_stats': {
                'total_api_calls': len(time_groups),
                'time_windows_processed': len(audience_data),
                'spots_processed': len(campaign_df)
            }
        }
        
        # Cache result
        self.processed_campaigns[campaign_ref] = result
        
        return result
    
    def _enrich_campaign_data(self, df: pd.DataFrame, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich campaign data with SPACE API lookups."""
        enriched = metrics.copy()
        
        # Get unique entity IDs
        media_owner_ids = df['spacemediaownerid'].unique()
        buyer_ids = df['spacebuyerid'].unique()
        agency_ids = df['spaceagencyid'].unique()
        
        # Perform batch lookups
        enriched['media_owners'] = {}
        enriched['buyers'] = {}
        enriched['agencies'] = {}
        
        for mo_id in media_owner_ids:
            try:
                entity = self.space_client.get_media_owner(str(mo_id))
                enriched['media_owners'][str(mo_id)] = {
                    'name': entity.name,
                    'details': entity.details
                }
            except Exception as e:
                self.logger.warning(f"Failed to lookup media owner {mo_id}: {e}")
        
        for buyer_id in buyer_ids:
            try:
                entity = self.space_client.get_buyer(str(buyer_id))
                enriched['buyers'][str(buyer_id)] = {
                    'name': entity.name,
                    'details': entity.details
                }
            except Exception as e:
                self.logger.warning(f"Failed to lookup buyer {buyer_id}: {e}")
        
        for agency_id in agency_ids:
            try:
                entity = self.space_client.get_agency(str(agency_id))
                enriched['agencies'][str(agency_id)] = {
                    'name': entity.name,
                    'details': entity.details
                }
            except Exception as e:
                self.logger.warning(f"Failed to lookup agency {agency_id}: {e}")
        
        return enriched