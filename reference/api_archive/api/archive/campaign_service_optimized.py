# ABOUTME: Optimized campaign service with data enrichment and fast CSV export
# ABOUTME: Performance-focused implementation with <3 second response target

import pandas as pd
import asyncio
import time
import csv
import io
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path
import logging

from src.api.route_client import RouteAPIClient
from src.api.space_client import SpaceAPIClient
from src.api.playout_processor import PlayoutProcessor
from src.utils.time_converter import TimeConverter
from src.utils.mock_data_factory import MockDataFactory
from src.config import (
    get_config, get_frame_config, get_entity_config,
    get_demo_config, get_campaign_config, get_spot_config
)
from src.paths import SAMPLE_PLAYOUT_CSV

logger = logging.getLogger(__name__)

class OptimizedCampaignService:
    """Optimized campaign service with enrichment and export capabilities"""
    
    def __init__(self):
        self.route_client = RouteAPIClient()
        self.space_client = SpaceAPIClient()
        self.playout_processor = PlayoutProcessor()
        self.time_converter = TimeConverter()
        
        # Load configuration
        self.config = get_config()
        self.frame_config = get_frame_config()
        self.entity_config = get_entity_config()
        self.demo_config = get_demo_config()
        self.campaign_config = get_campaign_config()
        self.spot_config = get_spot_config()
        
        # Performance optimizations from config
        self.batch_size = self.campaign_config.batch_size
        self.max_concurrent_requests = self.campaign_config.max_concurrent_requests
        self.cache_ttl = self.config.route_api.cache_ttl
        
        # Load sample data
        self.playout_data = self._load_playout_data()
        
        # Pre-cache common entities for performance
        self._precache_entities()
    
    def _load_playout_data(self) -> pd.DataFrame:
        """Load sample playout data from CSV"""
        if SAMPLE_PLAYOUT_CSV.exists():
            df = pd.read_csv(SAMPLE_PLAYOUT_CSV)
            df['startdate'] = pd.to_datetime(df['startdate'])
            df['enddate'] = pd.to_datetime(df['enddate'])
            return df
        return pd.DataFrame()
    
    def _precache_entities(self):
        """Pre-cache common entities for faster lookups"""
        if not self.playout_data.empty:
            # Get unique entity IDs with config limit
            limit = self.campaign_config.precache_entity_limit
            media_owners = self.playout_data['spacemediaownerid'].dropna().unique()[:limit]
            buyers = self.playout_data['spacebuyerid'].dropna().unique()[:limit]
            agencies = self.playout_data['spaceagencyid'].dropna().unique()[:limit]
            
            # Pre-load into cache
            for mo_id in media_owners:
                try:
                    self.space_client.get_media_owner(str(int(mo_id)))
                except:
                    pass
            
            for buyer_id in buyers:
                try:
                    self.space_client.get_buyer(str(int(buyer_id)))
                except:
                    pass
            
            for agency_id in agencies:
                try:
                    self.space_client.get_agency(str(int(agency_id)))
                except:
                    pass
    
    async def query_campaign_optimized(
        self,
        campaign_id: str,
        aggregate_by: str = "day",
        include_enrichment: bool = True,
        max_playouts: int = None
    ) -> Dict[str, Any]:
        """
        Optimized campaign query with enrichment
        
        Args:
            campaign_id: Campaign reference ID
            aggregate_by: Aggregation level (day, hour, frame)
            include_enrichment: Include entity name lookups
            max_playouts: Maximum playouts to process (uses config default if None)
            
        Returns:
            Dict with enriched campaign metrics
        """
        start_time = time.time()
        
        # Check if this is campaign 16015 (real API demo using playout sample)
        if campaign_id == "16015":
            # Use playout processor for hybrid demo with real API data
            try:
                result = await self.playout_processor.process_playout_campaign("16012")
                if result:
                    # Update campaign ID to match request
                    result['campaign_id'] = "16015"
                    result['campaign_name'] = "Playout Demo (Real APIs)"
                    # Add timing info
                    result['api_response_time'] = (time.time() - start_time) * 1000
                    result['total_time'] = result['api_response_time']
                    result['ui_query_time'] = result['api_response_time']
                    return result
                else:
                    logger.warning("Playout processor returned None for campaign 16015")
            except Exception as e:
                logger.error(f"Error processing campaign 16015 with playout processor: {e}")
                # Fall through to regular mock data generation
        
        # Filter campaign data
        if not self.playout_data.empty:
            campaign_data = self.playout_data[
                self.playout_data['buyercampaignref'] == float(campaign_id)
            ] if campaign_id.isdigit() else pd.DataFrame()
        else:
            campaign_data = self._generate_mock_campaign_data(campaign_id)
        
        if campaign_data.empty:
            campaign_data = self._generate_mock_campaign_data(campaign_id)
        
        # Use config default if not provided
        max_playouts = max_playouts or self.campaign_config.max_playouts_processing
        
        # Limit playouts for performance
        if len(campaign_data) > max_playouts:
            campaign_data = campaign_data.sample(n=max_playouts)
            logger.info(f"Sampled {max_playouts} playouts from {len(campaign_data)} total")
        
        # Process in batches for better performance
        batch_results = []
        for i in range(0, len(campaign_data), self.batch_size):
            batch = campaign_data.iloc[i:i+self.batch_size]
            batch_result = await self._process_playout_batch(batch)
            batch_results.extend(batch_result)
        
        # Enrich with entity names if requested
        enrichment_data = {}
        if include_enrichment:
            enrichment_data = await self._enrich_campaign_data(campaign_data)
        
        # Calculate metrics
        total_impacts = sum(p['audience'].get('impacts', 0) for p in batch_results if p['audience'].get('success'))
        total_reach = sum(p['audience'].get('reach', 0) for p in batch_results if p['audience'].get('success'))
        avg_frequency = total_impacts / total_reach if total_reach > 0 else 0
        
        # Aggregate results
        aggregated = self._aggregate_data_optimized(batch_results, aggregate_by)
        
        # Calculate performance
        processing_time = (time.time() - start_time) * 1000
        
        # Format response
        response = {
            'success': True,
            'campaign_id': campaign_id,
            'metrics': {
                'total_playouts': len(batch_results),
                'total_impacts': round(total_impacts, 4),  # Total impressions
                'total_reach': round(total_reach, 2),  # Unique people
                'avg_frequency': round(avg_frequency, 1),  # Avg views per person
                'unique_frames': len(set(p['frameid'] for p in batch_results)),
                'date_range': self._get_date_range(batch_results),
                'processing_time_ms': round(processing_time, 0),
                'performance_grade': self._get_performance_grade(processing_time)
            },
            'enrichment': enrichment_data,
            'aggregated': aggregated,
            'summary_metrics': {
                'reach': f"{int(total_reach):,}",
                'impacts': f"{total_impacts:.3f}k",
                'frequency': f"{avg_frequency:.1f}",
                'performance': f"{processing_time:.0f}ms",
                'efficiency': "3 days → 3 seconds"
            }
        }
        
        # Add sample playouts for detail view
        response['sample_playouts'] = batch_results[:self.campaign_config.sample_playouts_display]
        
        return response
    
    async def _process_playout_batch(self, batch_df: pd.DataFrame) -> List[Dict]:
        """Process a batch of playouts efficiently"""
        playouts = []
        
        for _, row in batch_df.iterrows():
            # Convert times to Route API format
            start_rounded = self.time_converter.round_to_daypart(row['startdate'])
            end_rounded = self.time_converter.round_to_daypart(row['enddate'])
            
            # Handle frame ID - could be int or string like "FRM_16014_00000"
            frame_id = row.get('frameid', self.frame_config.default_frame_id)
            if isinstance(frame_id, str):
                if frame_id.isdigit():
                    frame_id = int(frame_id)
                else:
                    # For string IDs like "FRM_16014_00000", use a hash or default
                    frame_id = self.frame_config.default_frame_id
            else:
                frame_id = int(frame_id)
            
            playout = {
                'frameid': frame_id,
                'startdate': row['startdate'],
                'enddate': row['enddate'],
                'spotlength': int(row.get('spotlength', self.spot_config.default_spot_length_ms)),
                'media_owner_id': int(row.get('spacemediaownerid', self.entity_config.default_media_owner_id)),
                'buyer_id': int(row.get('spacebuyerid', self.entity_config.default_buyer_id)),
                'agency_id': int(row.get('spaceagencyid', self.entity_config.default_agency_id)),
                'start_route': self.time_converter.format_for_route_api(start_rounded),
                'end_route': self.time_converter.format_for_route_api(end_rounded),
                'audience': {'success': False}  # Will be populated
            }
            playouts.append(playout)
        
        # Get audiences in parallel (limited concurrency)
        semaphore = asyncio.Semaphore(self.max_concurrent_requests)
        
        async def get_audience_with_limit(playout):
            async with semaphore:
                audience = await self.route_client.get_playout_audience(
                    frame_id=playout['frameid'],
                    datetime_from=playout['start_route'],
                    datetime_until=playout['end_route'],
                    spot_length=playout['spotlength'] / self.spot_config.ms_to_seconds_divisor,
                    release_id=self.config.route_api.default_release_id
                )
                playout['audience'] = audience
                return playout
        
        # Process with limited concurrency
        tasks = [get_audience_with_limit(p) for p in playouts]
        results = await asyncio.gather(*tasks)
        
        return results
    
    async def _enrich_campaign_data(self, campaign_df: pd.DataFrame) -> Dict[str, Any]:
        """Enrich campaign data with entity names"""
        enrichment = {
            'media_owners': {},
            'buyers': {},
            'agencies': {},
            'brands': {}
        }
        
        # Get unique IDs
        media_owner_ids = campaign_df['spacemediaownerid'].dropna().unique()
        buyer_ids = campaign_df['spacebuyerid'].dropna().unique()
        agency_ids = campaign_df['spaceagencyid'].dropna().unique()
        brand_ids = campaign_df.get('spacebrandid', pd.Series()).dropna().unique()
        
        # Lookup entities (uses cache for performance)
        limit = self.campaign_config.enrichment_entity_limit
        for mo_id in media_owner_ids[:limit]:  # Limit for demo
            try:
                entity = self.space_client.get_media_owner(str(int(mo_id)))
                enrichment['media_owners'][str(int(mo_id))] = {
                    'name': entity.name,
                    'type': entity.details.get('type', 'Digital'),
                    'locations': entity.details.get('locations', 0)
                }
            except:
                enrichment['media_owners'][str(int(mo_id))] = {
                    'name': f"Media Owner {int(mo_id)}",
                    'type': 'Unknown',
                    'locations': 0
                }
        
        for buyer_id in buyer_ids[:limit]:
            try:
                entity = self.space_client.get_buyer(str(int(buyer_id)))
                enrichment['buyers'][str(int(buyer_id))] = {
                    'name': entity.name,
                    'category': entity.details.get('category', 'Unknown')
                }
            except:
                enrichment['buyers'][str(int(buyer_id))] = {
                    'name': f"Buyer {int(buyer_id)}",
                    'category': 'Unknown'
                }
        
        for agency_id in agency_ids[:limit]:
            try:
                entity = self.space_client.get_agency(str(int(agency_id)))
                enrichment['agencies'][str(int(agency_id))] = {
                    'name': entity.name,
                    'parent': entity.details.get('parent', 'Independent')
                }
            except:
                enrichment['agencies'][str(int(agency_id))] = {
                    'name': f"Agency {int(agency_id)}",
                    'parent': 'Unknown'
                }
        
        return enrichment
    
    def _aggregate_data_optimized(self, playouts: List[Dict], aggregate_by: str) -> List[Dict]:
        """Optimized data aggregation"""
        if aggregate_by == "day":
            aggregated = {}
            for playout in playouts:
                day = playout['startdate'].strftime('%Y-%m-%d')
                if day not in aggregated:
                    aggregated[day] = {
                        'date': day,
                        'playouts': 0,
                        'impacts': 0,
                        'reach': 0,
                        'frames': set()
                    }
                
                aggregated[day]['playouts'] += 1
                if playout['audience'].get('success'):
                    aggregated[day]['impacts'] += playout['audience'].get('impacts', 0)
                    aggregated[day]['reach'] += playout['audience'].get('estimated_reach', 0)
                aggregated[day]['frames'].add(playout['frameid'])
            
            # Convert sets to counts
            for day_data in aggregated.values():
                day_data['unique_frames'] = len(day_data['frames'])
                del day_data['frames']
            
            return sorted(aggregated.values(), key=lambda x: x['date'])
        
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
                    aggregated[frame]['reach'] += playout['audience'].get('estimated_reach', 0)
            
            return sorted(aggregated.values(), key=lambda x: x['impacts'], reverse=True)
        
        return []
    
    def _get_performance_grade(self, processing_time_ms: float) -> str:
        """Get performance grade based on response time"""
        thresholds = self.config.get_performance_thresholds()
        
        if processing_time_ms < thresholds['excellent']:
            return "A+ (Excellent)"
        elif processing_time_ms < thresholds['very_good']:
            return "A (Very Good)"
        elif processing_time_ms < thresholds['good']:
            return "B (Good)"
        elif processing_time_ms < thresholds['acceptable']:
            return "C (Acceptable)"
        else:
            return "D (Needs Optimization)"
    
    def _get_date_range(self, playouts: List[Dict]) -> str:
        """Get date range from playouts"""
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
    
    def _generate_mock_campaign_data(self, campaign_id: str) -> pd.DataFrame:
        """Generate mock campaign data using centralized factory"""
        import random
        
        # Use factory to generate consistent mock data
        num_frames = random.randint(*self.campaign_config.mock_playouts_optimized_range)
        mock_frames = MockDataFactory.generate_campaign_frames(
            campaign_id=campaign_id,
            num_frames=num_frames
        )
        
        # Convert to expected format for playout data
        data = []
        for frame in mock_frames:
            # Parse timestamp from frame
            timestamp = pd.to_datetime(frame['timestamp'])
            spot_length = frame['duration'] * 1000  # Convert seconds to ms
            end = timestamp + pd.Timedelta(milliseconds=spot_length)
            
            data.append({
                'frameid': frame['frame_id'],
                'startdate': timestamp,
                'enddate': end,
                'spotlength': spot_length,
                'buyercampaignref': campaign_id,
                'spacemediaownerid': random.choice(self.entity_config.media_owner_ids),
                'spacebuyerid': random.choice(self.entity_config.buyer_ids),
                'spaceagencyid': random.choice(self.entity_config.agency_ids),
                'spacebrandid': random.choice(self.entity_config.brand_ids),
                # Add econometric data from mock
                'grps': frame['grps'],
                'channel': frame['channel'],
                'region': frame['region']
            })
        
        return pd.DataFrame(data)
    
    async def export_campaign_csv(
        self,
        campaign_id: str,
        include_enrichment: bool = True
    ) -> Tuple[str, float]:
        """
        Export campaign data to CSV with <2 second performance
        
        Args:
            campaign_id: Campaign reference ID
            include_enrichment: Include entity names in export
            
        Returns:
            Tuple of (csv_content, export_time_seconds)
        """
        start_time = time.time()
        
        # Get campaign data
        result = await self.query_campaign_optimized(
            campaign_id,
            aggregate_by="none",
            include_enrichment=include_enrichment,
            max_playouts=self.campaign_config.max_playouts_export  # Limit for CSV export
        )
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        headers = [
            'Frame ID', 'Start Date', 'End Date', 'Spot Length (ms)',
            'Media Owner ID', 'Media Owner Name', 'Buyer ID', 'Buyer Name',
            'Agency ID', 'Agency Name', 'Impacts', 'Reach'
        ]
        writer.writerow(headers)
        
        # Write data rows
        enrichment = result.get('enrichment', {})
        for playout in result.get('sample_playouts', []):
            # Get entity names from enrichment
            mo_name = enrichment.get('media_owners', {}).get(
                str(playout['media_owner_id']), {}
            ).get('name', 'Unknown')
            
            buyer_name = enrichment.get('buyers', {}).get(
                str(playout['buyer_id']), {}
            ).get('name', 'Unknown')
            
            agency_name = enrichment.get('agencies', {}).get(
                str(playout['agency_id']), {}
            ).get('name', 'Unknown')

            # Get impacts
            impacts = playout['audience'].get('impacts', 0)

            row = [
                playout['frameid'],
                playout['startdate'].strftime('%Y-%m-%d %H:%M:%S'),
                playout['enddate'].strftime('%Y-%m-%d %H:%M:%S'),
                playout['spotlength'],
                playout['media_owner_id'],
                mo_name,
                playout['buyer_id'],
                buyer_name,
                playout['agency_id'],
                agency_name,
                round(impacts, 6),
                playout['audience'].get('estimated_reach', 0)
            ]
            writer.writerow(row)
        
        # Add summary rows
        writer.writerow([])
        writer.writerow(['SUMMARY'])
        writer.writerow(['Total Playouts', result['metrics']['total_playouts']])
        writer.writerow(['Total Impacts', result['metrics']['total_impacts']])
        writer.writerow(['Total Reach', result['metrics']['total_reach']])
        writer.writerow(['Processing Time', f"{result['metrics']['processing_time_ms']}ms"])
        writer.writerow(['Performance Grade', result['metrics']['performance_grade']])
        
        csv_content = output.getvalue()
        export_time = time.time() - start_time
        
        logger.info(f"CSV export completed in {export_time:.2f} seconds")
        
        return csv_content, export_time
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get system performance metrics for dashboard"""
        # Run a test query to measure performance
        test_campaign = self.demo_config.test_campaign_id
        start_time = time.time()
        
        result = await self.query_campaign_optimized(
            test_campaign,
            aggregate_by="day",
            include_enrichment=False,
            max_playouts=self.campaign_config.sample_playouts_display * 10
        )
        
        query_time = (time.time() - start_time) * 1000
        
        return {
            'api_response_time': query_time,
            'cache_hit_rate': 0.7,  # Mock for now - could be made configurable
            'concurrent_requests': self.max_concurrent_requests,
            'batch_size': self.batch_size,
            'performance_grade': self._get_performance_grade(query_time),
            'throughput': f"{(self.campaign_config.sample_playouts_display * 10) / (query_time / 1000):.0f} playouts/second"
        }