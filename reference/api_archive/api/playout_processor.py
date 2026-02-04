#!/usr/bin/env python3
# ABOUTME: Processes playout sample data and enriches with real API data
# ABOUTME: Creates hybrid demo campaigns using actual playout structure

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import asyncio
import os
import logging

from src.api.route_client import RouteAPIClient
from src.api.space_client import SpaceAPIClient
from src.api.route_release_service import get_release_for_playout_string, get_release_for_playout_date
from src.paths import PLAYOUT_SAMPLE_DIGITAL_CSV

logger = logging.getLogger(__name__)


class PlayoutProcessor:
    """Process playout sample data with real API enrichment"""
    
    def __init__(self):
        self.route_client = RouteAPIClient()
        self.space_client = SpaceAPIClient()
        # Use centralized path from paths.py
        self.playout_path = PLAYOUT_SAMPLE_DIGITAL_CSV
        
    async def process_playout_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """
        Process a campaign from playout data with API enrichment
        
        Args:
            campaign_id: Campaign reference from playout data
            
        Returns:
            Enriched campaign data combining playout and API data
        """
        try:
            logger.info(f"🔍 PLAYOUT PROCESSOR: Processing campaign {campaign_id}")
            
            # Load playout data
            df = pd.read_csv(self.playout_path)
            logger.info(f"📊 Loaded playout CSV with {len(df)} rows")
            
            # Handle campaign ID as either string or float
            try:
                campaign_float = float(campaign_id)
                campaign_df = df[df['buyercampaignref'] == campaign_float]
                logger.debug(f"🎯 Looking for campaign {campaign_float} (as float)")
            except:
                campaign_df = df[df['buyercampaignref'] == campaign_id]
                logger.debug(f"🎯 Looking for campaign {campaign_id} (as string)")
            
            logger.info(f"📈 Found {len(campaign_df)} rows for campaign {campaign_id}")
            
            if campaign_df.empty:
                logger.warning(f"❌ No data found for campaign {campaign_id}, generating mock data")
                # Show available campaigns for debugging
                available_campaigns = df['buyercampaignref'].unique()
                logger.debug(f"   Available campaigns: {sorted(available_campaigns)[:20]}{'...' if len(available_campaigns) > 20 else ''}")
                
                # Generate mock data for campaigns 16013-16015
                if campaign_id in ['16013', '16014', '16015']:
                    return self._generate_mock_campaign_data(campaign_id)
                return None
            
            # Extract key information
            frame_ids = campaign_df['frameid'].unique().tolist()
            media_owner_ids = campaign_df['spacemediaownerid'].unique().tolist()
            buyer_ids = campaign_df['spacebuyerid'].unique().tolist()
            agency_ids = campaign_df['spaceagencyid'].unique().tolist()
            brand_id = int(campaign_df['spacebrandid'].iloc[0])
            
            logger.debug(f"🎪 EXTRACTED DATA:")
            logger.debug(f"   Frame IDs: {len(frame_ids)} unique ({frame_ids[:5]}{'...' if len(frame_ids) > 5 else ''})")
            logger.debug(f"   Media Owner IDs: {media_owner_ids}")
            logger.debug(f"   Buyer IDs: {buyer_ids}")
            logger.debug(f"   Agency IDs: {agency_ids}")
            logger.debug(f"   Brand ID: {brand_id}")
            
            # Get date range
            dates = pd.to_datetime(campaign_df['startdate'].str[:10])
            start_date = dates.min().strftime('%Y-%m-%d')
            end_date = dates.max().strftime('%Y-%m-%d')
            
            # Calculate playout metrics
            total_spots = len(campaign_df)
            total_airtime_ms = campaign_df['spotlength'].sum()
            avg_spot_length = campaign_df['spotlength'].mean()
            
            # Get real audience data from Route API (individual calls per playout)
            audience_data = await self._get_audience_data(campaign_df)
            
            # Get entity data from SPACE API
            entity_data = await self._get_entity_data(
                media_owner_ids, buyer_ids, agency_ids, brand_id
            )
            
            # Calculate enhanced metrics
            metrics = self._calculate_metrics(
                campaign_df, audience_data, total_spots
            )
            
            # Build response
            result = {
                'campaign_id': campaign_id,
                'campaign_name': f'Playout Campaign {campaign_id}',
                'data_source': 'hybrid_playout_api',
                'playout_data': {
                    'total_spots': total_spots,
                    'total_airtime_seconds': total_airtime_ms / 1000,
                    'avg_spot_length_ms': avg_spot_length,
                    'frame_count': len(frame_ids),
                    'date_range': f'{start_date} to {end_date}'
                },
                'route_release': {
                    'release_used': audience_data.get('release_used', 'unknown'),
                    'date_range': f'{start_date} to {end_date}'
                },
                'entities': entity_data,
                'metrics': metrics,
                'summary': {
                    'total_impacts': metrics.get('impacts', 0),
                    'total_reach': metrics.get('reach', 0),
                    'total_audience_spot_avg': audience_data.get('audience_spot_avg_total', 0),
                    'total_frames': len(frame_ids),
                    'total_spots': total_spots,
                    'successful_api_calls': audience_data.get('successful_api_calls', 0),
                    'failed_api_calls': audience_data.get('failed_api_calls', 0)
                },
                'time_series': self._generate_time_series(campaign_df, audience_data),
                'geographic_data': self._generate_geographic_data(frame_ids, audience_data)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing playout campaign: {e}")
            return None
    
    async def _get_audience_data(self, campaign_df: pd.DataFrame) -> Dict:
        """Get real audience data from Route API - one call per playout record"""
        try:
            total_playouts = len(campaign_df)
            logger.info(f"🎯 PLAYOUT PROCESSOR: Processing {total_playouts} individual playout records")
            
            # Get the appropriate Route release for the playout dates
            first_date = campaign_df['startdate'].iloc[0][:10]
            try:
                release_info = await get_release_for_playout_string(first_date)
                logger.info(f"📋 Using Route release: {release_info.release_number} ({release_info.name})")
                logger.debug(f"   Release ID: {release_info.numeric_id}")
                
                # Update route client with the correct release ID
                self.route_client.release_id = release_info.numeric_id
                
            except Exception as e:
                logger.warning(f"⚠️ Error getting Route release, using default: {e}")
                release_info = None
            
            # Process each playout record individually
            playout_tasks = []
            
            for idx, row in campaign_df.iterrows():
                # Parse dates and round to nearest second
                # Handle special format like "2025-08-01 00:00.09.922"
                start_str = row['startdate']
                end_str = row['enddate']
                
                # Custom parsing for the unusual format with periods
                # Format: "2025-08-01 00:00.09.922" -> "2025-08-01 00:00:09.922"
                def fix_datetime_format(dt_str):
                    # The format is "2025-08-01 00:00.09.922"
                    # Which means: YYYY-MM-DD HH:MM.SS.mmm
                    # We need: YYYY-MM-DD HH:MM:SS.mmm
                    
                    # Split on space to get date and time
                    date_part, time_part = dt_str.split(' ', 1)
                    
                    # Time part looks like: "00:00.09.922" (HH:MM.SS.mmm)
                    # We need to replace the first period after MM with a colon
                    colon_pos = time_part.find(':')
                    if colon_pos >= 0:
                        # Find first period after the colon
                        first_period_pos = time_part.find('.', colon_pos)
                        if first_period_pos >= 0:
                            # Replace first period with colon: "00:00.09.922" -> "00:00:09.922"
                            fixed_time = time_part[:first_period_pos] + ':' + time_part[first_period_pos+1:]
                            return f"{date_part} {fixed_time}"
                    
                    return dt_str
                
                start_str_fixed = fix_datetime_format(start_str)
                end_str_fixed = fix_datetime_format(end_str)
                
                start_dt = pd.to_datetime(start_str_fixed)
                end_dt = pd.to_datetime(end_str_fixed)
                
                # Round to nearest second
                start_rounded = start_dt.round('s')
                end_rounded = end_dt.round('s')
                
                # Format for Route API (YYYY-MM-DD HH:MM:SS)
                datetime_from = start_rounded.strftime('%Y-%m-%d %H:%M:%S')
                datetime_until = end_rounded.strftime('%Y-%m-%d %H:%M:%S')
                
                # Calculate spot_length in seconds
                spot_length = int((end_rounded - start_rounded).total_seconds())
                
                # Get frame_id
                frame_id = int(row['frameid'])
                
                logger.debug(f"   Playout {idx}: Frame {frame_id}, {datetime_from} to {datetime_until}, {spot_length}s")
                
                # Create API call task
                task = self.route_client.get_playout_audience(
                    frame_id=frame_id,
                    datetime_from=datetime_from,
                    datetime_until=datetime_until,
                    spot_length=spot_length,
                    release_id=release_info.numeric_id if release_info else None
                )
                playout_tasks.append(task)
            
            # Execute API calls with concurrency control (max 5 concurrent)
            logger.info(f"🚀 Executing {len(playout_tasks)} API calls with concurrency limit...")
            
            # Use a semaphore to limit concurrent API calls
            semaphore = asyncio.Semaphore(5)
            
            async def limited_api_call(task):
                async with semaphore:
                    return await task
            
            # Execute all tasks with concurrency control
            limited_tasks = [limited_api_call(task) for task in playout_tasks]
            api_results = await asyncio.gather(*limited_tasks, return_exceptions=True)
            
            # Process results and calculate totals
            total_audience = 0
            successful_calls = 0
            failed_calls = 0
            
            for idx, result in enumerate(api_results):
                if isinstance(result, Exception):
                    logger.error(f"   API call {idx+1} failed: {result}")
                    failed_calls += 1
                    continue
                    
                if result and result.get('success'):
                    audience_spot_avg = result.get('audience_spot_avg', 0)
                    total_audience += audience_spot_avg
                    successful_calls += 1
                    
                    logger.debug(f"   API call {idx+1}: audience_spot_avg = {audience_spot_avg}")
                else:
                    logger.warning(f"   API call {idx+1} returned no data or failed")
                    failed_calls += 1
            
            logger.info(f"✅ BATCH PROCESSING COMPLETE: {successful_calls}/{len(api_results)} successful, total_audience = {total_audience}")
            
            if successful_calls > 0:
                # Calculate aggregated metrics
                avg_impacts_per_playout = total_audience  # audience_spot_avg is already the average
                total_impacts = total_audience * total_playouts  # Scale by total playouts
                estimated_reach = total_impacts / 3.0 if total_impacts > 0 else 0  # Frequency ~3
                
                return {
                    'audience_spot_avg_total': total_audience,
                    'impacts': total_impacts,
                    'reach': estimated_reach,
                    'successful_api_calls': successful_calls,
                    'failed_api_calls': failed_calls,
                    'total_playout_records': total_playouts,
                    'release_used': release_info.release_number if release_info else 'default'
                }
            else:
                logger.warning(f"❌ All API calls failed, using fallback data")
                # Fallback to estimated data
                audience_data = self._estimate_audience_data(len(campaign_df['frameid'].unique()))
                audience_data.update({
                    'successful_api_calls': 0,
                    'failed_api_calls': len(api_results),
                    'total_playout_records': total_playouts,
                    'release_used': 'fallback'
                })
                return audience_data
                
        except Exception as e:
            logger.error(f"Error getting audience data: {e}")
            audience_data = self._estimate_audience_data(len(campaign_df['frameid'].unique()))
            audience_data.update({
                'successful_api_calls': 0,
                'failed_api_calls': len(campaign_df),
                'total_playout_records': len(campaign_df),
                'release_used': 'fallback'
            })
            return audience_data
    
    async def _get_entity_data(self, media_owner_ids: List, buyer_ids: List, 
                               agency_ids: List, brand_id: int) -> Dict:
        """Get entity information from SPACE API"""
        entities = {}
        
        try:
            # Get media owner info
            if media_owner_ids:
                owner = self.space_client.get_media_owner(str(media_owner_ids[0]))
                entities['media_owner'] = owner.name if owner else f"Media Owner {media_owner_ids[0]}"
            
            # Get buyer info
            if buyer_ids:
                buyer = self.space_client.get_buyer(str(buyer_ids[0]))
                entities['buyer'] = buyer.name if buyer else f"Buyer {buyer_ids[0]}"
            
            # Get agency info
            if agency_ids:
                agency = self.space_client.get_agency(str(agency_ids[0]))
                entities['agency'] = agency.name if agency else f"Agency {agency_ids[0]}"
            
            # Brand info
            entities['brand'] = f"Brand {brand_id}"
            
        except Exception as e:
            logger.error(f"Error getting entity data: {e}")
            entities = {
                'media_owner': f"Media Owner {media_owner_ids[0] if media_owner_ids else 'Unknown'}",
                'buyer': f"Buyer {buyer_ids[0] if buyer_ids else 'Unknown'}",
                'agency': f"Agency {agency_ids[0] if agency_ids else 'Unknown'}",
                'brand': f"Brand {brand_id}"
            }
        
        return entities
    
    def _calculate_metrics(self, campaign_df: pd.DataFrame, 
                          audience_data: Dict, total_spots: int) -> Dict:
        """Calculate campaign metrics using audience_spot_avg data"""
        # Base metrics from audience data (now using audience_spot_avg totals)
        base_impacts = audience_data.get('impacts', 500000)
        base_reach = audience_data.get('reach', 250000)
        audience_spot_avg_total = audience_data.get('audience_spot_avg_total', 0)
        
        logger.info(f"📊 METRICS CALCULATION:")
        logger.info(f"   Base impacts: {base_impacts}")
        logger.info(f"   Base reach: {base_reach}")
        logger.info(f"   Audience spot avg total: {audience_spot_avg_total}")
        logger.info(f"   Total spots: {total_spots}")
        
        metrics = {
            'impacts': int(base_impacts),
            'reach': int(base_reach),
            'audience_spot_avg_total': audience_spot_avg_total,
            'frequency': 0,
            'grps': 0,
            'spots': total_spots
        }

        # Calculate frequency
        if metrics['reach'] > 0:
            metrics['frequency'] = metrics['impacts'] / metrics['reach']

        # Calculate GRPs (assuming UK population ~67M)
        uk_population = 67000000
        if metrics['impacts'] > 0:
            metrics['grps'] = (metrics['impacts'] / uk_population) * 100

        logger.info(f"   Final metrics: impacts={metrics['impacts']}, reach={metrics['reach']}, frequency={metrics['frequency']:.2f}, grps={metrics['grps']:.2f}")
        
        return metrics
    
    def _estimate_audience_data(self, frame_count: int) -> Dict:
        """Estimate audience data when API is unavailable"""
        return {
            'impacts': 500000 * frame_count,
            'reach': 250000 * frame_count,
            'demographics': {
                'age_18_34': 0.35,
                'age_35_54': 0.40,
                'age_55_plus': 0.25
            }
        }
    
    def _generate_mock_campaign_data(self, campaign_id: str) -> Dict[str, Any]:
        """Generate mock campaign data for campaigns that don't exist in playout CSV"""
        logger.info(f"🎨 Generating mock data for campaign {campaign_id}")
        
        # Campaign-specific configurations
        campaign_configs = {
            '16013': {
                'name': 'Summer Brand Awareness Campaign',
                'total_spots': 850,
                'total_frames': 200,
                'impacts_multiplier': 1.8,
                'reach_multiplier': 1.5
            },
            '16014': {
                'name': 'Regional Retail Promotion',
                'total_spots': 420,
                'total_frames': 85,
                'impacts_multiplier': 0.9,
                'reach_multiplier': 0.8
            },
            '16015': {
                'name': 'National Product Launch',
                'total_spots': 1200,
                'total_frames': 300,
                'impacts_multiplier': 2.5,
                'reach_multiplier': 2.2
            }
        }
        
        config = campaign_configs.get(campaign_id, campaign_configs['16014'])
        
        # Generate base metrics
        base_impacts = 3500000 * config['impacts_multiplier']
        base_reach = 1500000 * config['reach_multiplier']
        
        # Generate time series data (30 days)
        time_series = []
        start_date = datetime(2025, 7, 1)
        daily_impacts = base_impacts / 30
        daily_reach = base_reach / 30
        
        for day in range(30):
            current_date = start_date + timedelta(days=day)
            # Add some variation
            variation = 0.8 + (0.4 * np.random.random())
            time_series.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'spots': int(config['total_spots'] / 30 * variation),
                'impacts': int(daily_impacts * variation),
                'reach': int(daily_reach * variation)
            })
        
        # Generate geographic data using mock_geo_data
        from src.ui.data.mock_geo_data import get_mock_campaign_geo_data
        geo_data = get_mock_campaign_geo_data(campaign_id)
        
        result = {
            'campaign_id': campaign_id,
            'campaign_name': config['name'],
            'data_source': 'mock_data',
            'playout_data': {
                'total_spots': config['total_spots'],
                'total_airtime_seconds': config['total_spots'] * 10,
                'avg_spot_length_ms': 10000,
                'frame_count': config['total_frames'],
                'date_range': '2025-07-01 to 2025-07-31'
            },
            'route_release': {
                'release_used': 'R55',
                'date_range': '2025-07-01 to 2025-07-31'
            },
            'entities': {
                'media_owner': 'Clear Channel UK',
                'buyer': 'GroupM',
                'agency': 'Wavemaker',
                'brand': f'Brand {campaign_id[-1]}'
            },
            'metrics': {
                'impacts': int(base_impacts),
                'reach': int(base_reach),
                'frequency': round(base_impacts / base_reach, 1),
                'grps': round((base_impacts / 67000000) * 100, 2),
                'spots': config['total_spots']
            },
            'summary': {
                'total_impacts': base_impacts,
                'total_reach': base_reach,
                'total_audience_spot_avg': base_impacts / config['total_spots'],
                'total_frames': config['total_frames'],
                'total_spots': config['total_spots'],
                'successful_api_calls': 0,
                'failed_api_calls': 0
            },
            'time_series': time_series,
            'geographic_data': geo_data['frames'][:10] if 'frames' in geo_data else []
        }
        
        return result
    
    def _generate_time_series(self, campaign_df: pd.DataFrame, 
                             audience_data: Dict) -> List[Dict]:
        """Generate time series data for visualization"""
        # Group by date - use .copy() to avoid SettingWithCopyWarning
        campaign_df = campaign_df.copy()
        campaign_df['date'] = pd.to_datetime(campaign_df['startdate'].str[:10])
        daily_spots = campaign_df.groupby('date').size()
        
        # Calculate daily metrics
        base_daily_impacts = audience_data.get('impacts', 500000) / 30  # Assume 30 days
        
        time_series = []
        for date, spots in daily_spots.items():
            time_series.append({
                'date': date.strftime('%Y-%m-%d'),
                'spots': int(spots),
                'impacts': int(base_daily_impacts * spots),
                'reach': int(base_daily_impacts * spots * 0.5)
            })
        
        return time_series
    
    def _generate_geographic_data(self, frame_ids: List, 
                                  audience_data: Dict) -> List[Dict]:
        """Generate geographic data for visualization"""
        # For now, create sample London-centric data
        geo_data = []
        
        # Use frame location (assuming London for sample)
        for frame_id in frame_ids[:10]:  # Limit to 10 for visualization
            geo_data.append({
                'frame_id': str(frame_id),
                'latitude': 51.5074 + np.random.normal(0, 0.1),  # London + variation
                'longitude': -0.1278 + np.random.normal(0, 0.1),
                'impacts': audience_data.get('impacts', 500000) / max(len(frame_ids), 1),
                'location': 'London',
                'type': 'Digital'
            })
        
        return geo_data


# Integration function for campaign service
async def process_playout_campaign(campaign_id: str) -> Dict[str, Any]:
    """Process a playout campaign with API enrichment"""
    processor = PlayoutProcessor()
    return await processor.process_playout_campaign(campaign_id)