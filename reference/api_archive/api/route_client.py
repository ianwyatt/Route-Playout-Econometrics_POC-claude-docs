# ABOUTME: Route API client with caching and mock mode support
# ABOUTME: Provides audience data from MediaTel Route API

import httpx
import json
import os
import asyncio
import random
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
import hashlib
import logging
from src.utils.ttl_cache import TTLCache
from src.utils.error_handlers import (
    DemoErrorHandler,
    RetryHandler,
    demo_safe_api_call,
    log_api_metrics,
    ErrorType
)
from src.config import get_route_config, get_frame_config
from src.utils.credentials import get_route_credentials, is_mock_mode_active
from src.utils.validators import validate_frames, should_use_grouping

load_dotenv()
logger = logging.getLogger(__name__)

class RouteAPIClient:
    """Client for MediaTel Route API with caching and mock mode"""
    
    def __init__(self):
        # Load configuration
        self.config = get_route_config()
        
        # Get validated credentials with automatic mock mode activation
        self.api_key, self.auth_header, credentials_force_mock = get_route_credentials()
        
        # API settings from config
        self.base_url = self.config.base_url
        self.timeout = self.config.timeout
        self.demo_timeout = self.config.demo_timeout
        self.mock_delay = self.config.mock_response_delay
        
        # Determine mock mode - use credential-based decision or config override
        self.use_mock = credentials_force_mock or self.config.use_mock or is_mock_mode_active()
        
        # TTL cache for production safety - prevents memory exhaustion during demos
        self.cache = TTLCache(max_size=self.config.cache_size, default_ttl=self.config.cache_ttl)
        
        # Log credential status for admin monitoring (without exposing values)
        if self.use_mock:
            if credentials_force_mock:
                logger.info("🎭 Route API using mock mode due to credential validation")
            else:
                logger.info("🎭 Route API using mock mode by configuration")
        else:
            logger.info("✅ Route API credentials validated - live mode available")
        
    def _get_headers(self) -> Dict[str, str]:
        """Get API headers with authentication - demo safe"""
        if not self.api_key or not self.auth_header:
            # This should not happen due to credential validation, but safety first
            logger.warning("Missing credentials in _get_headers - this should not happen")
            return {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
        
        return {
            "x-api-key": self.api_key,
            "Authorization": self.auth_header,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def _cache_key(self, request_data: dict) -> str:
        """Generate cache key from request data"""
        json_str = json.dumps(request_data, sort_keys=True)
        return hashlib.md5(json_str.encode()).hexdigest()
    
    def _generate_fallback_audience_data(
        self, 
        frame_id: int, 
        spot_length: int, 
        **kwargs
    ) -> Dict[str, Any]:
        """Generate realistic fallback data for demo"""
        # Generate consistent but varied data based on frame_id
        random.seed(frame_id)
        
        # For realistic numbers, use per-playout impacts (total campaign / playouts)
        # Target ~260,000 total impacts for campaign 16012 with 1050 playouts
        base_impacts_per_playout = random.uniform(200, 300)  # ~250 avg per playout
        ped_ratio = random.uniform(*self.config.pedestrian_ratio_range)
        
        impacts = base_impacts_per_playout * (spot_length / self.config.default_spot_length)
        impacts_ped = impacts * ped_ratio
        impacts_veh = impacts * (1 - ped_ratio)
        
        # Realistic frequency range from config
        frequency = random.uniform(*self.config.frequency_range)
        reach = impacts / frequency if impacts > 0 else 0
        
        # Calculate GRPs (impacts / population * 100)
        population = 8900000  # Greater London population
        grps = (impacts / population) * 100
        
        return {
            'impacts': round(impacts, 6),
            'impacts_pedestrian': round(impacts_ped, 6), 
            'impacts_vehicular': round(impacts_veh, 6),
            'playouts_total': self.config.playouts_total,
            'audience_spot_avg': round(impacts / self.config.playouts_total, 8),
            'reach': round(reach, 2),
            'frequency': round(frequency, 1),
            'gross_rating_points': round(grps, 6),
            'population': population,
            'processing_time': random.randint(*self.config.processing_time_range)
        }
    
    @log_api_metrics
    async def get_playout_audience(
        self,
        frame_id: int,
        datetime_from: str,
        datetime_until: str,
        spot_length: int = None,
        release_id: int = None,
        target_month: int = None,
        include_grps: bool = False
    ) -> Dict[str, Any]:
        """
        Get audience data for a frame playout
        
        Args:
            frame_id: Route frame ID
            datetime_from: Start time (YYYY-MM-DD HH:MM)
            datetime_until: End time (YYYY-MM-DD HH:MM)
            spot_length: Spot length in seconds (uses config default if None)
            release_id: Route release ID (uses config default if None)
            target_month: Target month (uses config default if None)
            include_grps: Include GRPs in the response
            
        Returns:
            Dict with audience metrics
        """
        # Use config defaults if not provided
        spot_length = spot_length or self.config.default_spot_length
        release_id = release_id or self.config.default_release_id
        target_month = target_month or self.config.default_target_month
        
        # Ensure datetime_until is after datetime_from (Route API requires a range)
        # If they're the same, add 14 minutes to create a 15-minute daypart
        if datetime_from == datetime_until:
            from datetime import datetime, timedelta
            dt_from = datetime.strptime(datetime_from, "%Y-%m-%d %H:%M")
            dt_until = dt_from + timedelta(minutes=14, seconds=59)
            datetime_until = dt_until.strftime("%Y-%m-%d %H:%M")  # Route API expects HH:MM format
        
        # Prepare request
        request_data = {
            "route_release_id": release_id,
            "route_algorithm_version": self.config.algorithm_version,
            "target_month": target_month,
            "campaign": [{
                "schedule": [{
                    "datetime_from": datetime_from,
                    "datetime_until": datetime_until
                }],
                "spot_length": spot_length,
                "spot_break_length": 0,
                "frames": [frame_id]
            }]
        }
        
        # Add algorithm figures if GRPs requested
        if include_grps:
            request_data["algorithm_figures"] = ["grp", "impacts", "reach", "population"]
        
        # Check cache
        cache_key = self._cache_key(request_data)
        cached = self.cache.get(cache_key)
        if cached is not None:
            cached['from_cache'] = True
            cached['processing_time'] = 0
            return cached
        
        # Mock mode or fallback for demo reliability
        if self.use_mock:
            response = await self._mock_response(frame_id, spot_length)
        else:
            response = await self._real_api_call_with_fallback(request_data, frame_id, spot_length)
        
        # Cache successful responses
        if response and response.get('success'):
            self.cache.put(cache_key, response)
        
        return response

    async def get_campaign_reach(
        self,
        frames: List[int],
        schedules: List[Dict[str, str]],
        spot_length: int = None,
        break_length: int = None,
        release_id: int = None,
        target_month: int = None,
        demographics: List[str] = None
    ) -> Dict[str, Any]:
        """
        Get reach, GRP, and frequency data for a campaign using /rest/process/custom endpoint

        This endpoint returns campaign-level reach (unique audience), which is non-additive
        and must be calculated fresh for each aggregation period.

        Args:
            frames: List of Route frame IDs (max 10,000 per call)
            schedules: List of schedule dicts with datetime_from and datetime_until
            spot_length: Average spot length in seconds (uses config default if None)
            break_length: Average break length in seconds (uses config default if None)
            release_id: Route release ID (uses config default if None)
            target_month: Target month (auto-extracted from schedules if None)
            demographics: List of demographic filters (e.g., ["ageband>=1"])

        Returns:
            Dict with reach, GRP, frequency, and impacts metrics

        Raises:
            ValueError: If frames list exceeds 10,000 (use batching)
        """
        # Validate frame count
        if len(frames) > 10000:
            raise ValueError(
                f"Frame count ({len(frames)}) exceeds Route API limit of 10,000. "
                "Use batch_campaign_reach() for large campaigns."
            )

        # Use config defaults if not provided
        spot_length = spot_length or self.config.default_spot_length
        break_length = break_length or (self.config.default_spot_length * 5)  # Default 5x spot length
        release_id = release_id or self.config.default_release_id

        # Validate frames exist in Route release (prevents API error 220)
        if not self.use_mock:
            # Get auth credentials for validation
            auth = (
                os.getenv('ROUTE_API_User_Name'),
                os.getenv('ROUTE_API_Password')
            )
            headers = self._get_headers()

            # Validate frames exist in Route release
            valid_frames, invalid_frames = validate_frames(
                frame_ids=frames,
                route_release_id=release_id,
                auth=auth,
                headers=headers
            )

            # Handle all-frames-invalid edge case
            if not valid_frames:
                raise ValueError(
                    f"No valid frames in Route release R{release_id}. "
                    f"All {len(frames)} frames are invalid."
                )

            # Log warning if some frames filtered
            if invalid_frames:
                logger.warning(
                    f"Filtered {len(invalid_frames)} invalid frames. "
                    f"Proceeding with {len(valid_frames)} valid frames."
                )
                # Use only valid frames
                frames = valid_frames

        # Determine if grouping should be used (prevents API error 221)
        use_grouping = should_use_grouping(len(frames))

        if not use_grouping:
            logger.warning(
                f"Campaign has {len(frames)} frames - disabling grouping "
                f"(Route API limit: 10,000 frames with grouping)"
            )

        # Auto-extract target_month from schedules if not provided
        if target_month is None and schedules:
            target_month = self._extract_target_month(schedules[0]['datetime_from'])
        else:
            target_month = target_month or self.config.default_target_month

        # Default demographics if not provided
        if demographics is None:
            demographics = ["ageband>=1"]  # All ages 15+

        # Prepare request
        request_data = {
            "route_release_id": release_id,
            "route_algorithm_version": self.config.algorithm_version,
            "algorithm_figures": ["impacts", "reach", "frequency", "grp", "population"],
            "demographics": demographics,
            "campaign": [{
                "schedule": schedules,
                "spot_length": spot_length,
                "spot_break_length": break_length,
                "frames": frames
            }],
            "target_month": target_month
        }

        # Conditionally add grouping parameter
        if use_grouping:
            request_data["grouping"] = "frame_ID"

        # Check cache
        cache_key = self._cache_key(request_data)
        cached = self.cache.get(cache_key)
        if cached is not None:
            cached['from_cache'] = True
            cached['processing_time'] = 0
            logger.debug(f"✅ Cache hit for reach calculation ({len(frames)} frames)")
            return cached

        # Mock mode or fallback for demo reliability
        if self.use_mock:
            response = await self._mock_reach_response(len(frames), schedules)
        else:
            response = await self._real_reach_api_call(request_data, len(frames))

        # Cache successful responses
        if response and response.get('success'):
            self.cache.put(cache_key, response)

        return response

    async def batch_campaign_reach(
        self,
        frames: List[int],
        schedules: List[Dict[str, str]],
        spot_length: int = None,
        break_length: int = None,
        release_id: int = None,
        target_month: int = None,
        demographics: List[str] = None,
        batch_size: int = 10000
    ) -> Dict[str, Any]:
        """
        Get reach for campaigns with >10,000 frames by batching

        NOTE: This will make multiple API calls and aggregate results.
        Reach is non-additive, so this returns reach per batch, not total reach.
        Use this for getting frame-level data, not campaign-level reach.

        Args:
            frames: List of Route frame IDs (can exceed 10,000)
            schedules: List of schedule dicts
            spot_length: Spot length in seconds
            break_length: Break length in seconds
            release_id: Route release ID
            target_month: Target month
            demographics: Demographic filters
            batch_size: Frames per batch (default 10,000)

        Returns:
            Dict with aggregated results and batch info
        """
        if len(frames) <= batch_size:
            # No batching needed
            return await self.get_campaign_reach(
                frames=frames,
                schedules=schedules,
                spot_length=spot_length,
                break_length=break_length,
                release_id=release_id,
                target_month=target_month,
                demographics=demographics
            )

        # Split into batches
        batches = [frames[i:i + batch_size] for i in range(0, len(frames), batch_size)]
        logger.info(f"🔄 Batching {len(frames)} frames into {len(batches)} batches of {batch_size}")

        # Process batches
        tasks = []
        for batch_frames in batches:
            task = self.get_campaign_reach(
                frames=batch_frames,
                schedules=schedules,
                spot_length=spot_length,
                break_length=break_length,
                release_id=release_id,
                target_month=target_month,
                demographics=demographics
            )
            tasks.append(task)

        batch_results = await asyncio.gather(*tasks)

        # Aggregate impacts (additive)
        total_impacts = sum(r.get('impacts', 0) for r in batch_results if r.get('success'))

        # WARNING: Cannot simply add reach - this is probability-based
        # Return batch results for caller to handle appropriately
        return {
            'success': True,
            'impacts': total_impacts,
            'batches': len(batches),
            'batch_results': batch_results,
            'warning': 'Reach is non-additive across batches. Use batch_results for accurate reach calculation.'
        }

    def _extract_target_month(self, datetime_str: str) -> int:
        """
        Extract target month from datetime string

        Args:
            datetime_str: Datetime in format "YYYY-MM-DD HH:MM"

        Returns:
            Month as integer (1-12)
        """
        try:
            dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
            return dt.month
        except (ValueError, AttributeError):
            logger.warning(f"Could not extract month from '{datetime_str}', using default")
            return self.config.default_target_month

    async def _mock_reach_response(
        self,
        frame_count: int,
        schedules: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Generate realistic mock response for reach endpoint"""
        await asyncio.sleep(self.mock_delay)

        # Calculate schedule duration
        total_hours = 0
        for schedule in schedules:
            try:
                dt_from = datetime.strptime(schedule['datetime_from'], "%Y-%m-%d %H:%M")
                dt_until = datetime.strptime(schedule['datetime_until'], "%Y-%m-%d %H:%M")
                total_hours += (dt_until - dt_from).total_seconds() / 3600
            except (ValueError, KeyError):
                total_hours += 24  # Default to 24 hours

        # Generate realistic metrics based on frame count and duration
        # Impacts scale with frames and duration
        base_impacts_per_frame_hour = random.uniform(200, 500)
        total_impacts = base_impacts_per_frame_hour * frame_count * total_hours

        # Reach is based on unique audience (non-linear scaling)
        # More frames = higher reach, but with diminishing returns
        import math
        reach_factor = 1 - math.exp(-frame_count / 100)  # Exponential approach to saturation
        base_reach = total_impacts * reach_factor * random.uniform(0.3, 0.5)

        # Frequency = impacts / reach
        frequency = total_impacts / base_reach if base_reach > 0 else 0

        # GRP = (Reach / Population) * 100
        # Assume UK 15+ population ~52 million
        population = 52000  # in thousands
        grp = (base_reach / population) * 100 if population > 0 else 0

        return {
            'success': True,
            'demo_mode': True,
            'impacts': round(total_impacts, 3),
            'reach': round(base_reach, 3),
            'frequency': round(frequency, 3),
            'grp': round(grp, 3),
            'population': population,
            'frame_count': frame_count,
            'schedule_count': len(schedules),
            'processing_time': self.mock_delay * 1000
        }

    async def _real_reach_api_call(
        self,
        request_data: dict,
        frame_count: int
    ) -> Dict[str, Any]:
        """Make real API call to /rest/process/custom endpoint with fallback"""

        try:
            # Use demo timeout for board safety
            timeout = httpx.Timeout(self.demo_timeout, connect=5.0)

            # Custom endpoint URL
            api_url = os.getenv('ROUTE_API_LIVE_CUSTOM_URL', f"{self.base_url}/rest/process/custom")
            headers = self._get_headers()

            logger.debug("🚀 ROUTE REACH API REQUEST:")
            logger.debug(f"   URL: {api_url}")
            logger.debug(f"   Frame count: {frame_count}")
            logger.debug(f"   Request Body: {json.dumps(request_data, indent=2)}")

            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    api_url,
                    json=request_data,
                    headers=headers
                )

                logger.debug("📥 ROUTE REACH API RESPONSE:")
                logger.debug(f"   Status Code: {response.status_code}")

                return await self._process_reach_api_response(response, frame_count)

        except httpx.TimeoutException as e:
            logger.warning(f"Route reach API timeout ({self.demo_timeout}s), falling back to mock data")
            return await self._mock_reach_response(frame_count, request_data['campaign'][0]['schedule'])

        except httpx.HTTPStatusError as e:
            status_code = e.response.status_code
            logger.warning(f"Route reach API HTTP error {status_code}, falling back to mock data")
            return await self._mock_reach_response(frame_count, request_data['campaign'][0]['schedule'])

        except Exception as e:
            logger.error(f"Unexpected Route reach API error: {type(e).__name__}")
            return await self._mock_reach_response(frame_count, request_data['campaign'][0]['schedule'])

    async def _process_reach_api_response(
        self,
        response: httpx.Response,
        frame_count: int
    ) -> Dict[str, Any]:
        """Process Route API custom endpoint response"""
        start_time = time.time()

        try:
            elapsed = (time.time() - start_time) * 1000

            if response.status_code == 200:
                data = response.json()

                logger.debug("🔍 PROCESSING REACH API RESPONSE:")
                logger.debug(f"   Raw JSON: {json.dumps(data, indent=2)}")

                # Extract metrics from results
                results = data.get('results', [])

                if results:
                    # For reach calculations, we want campaign-level metrics
                    # These are typically in the first result
                    figures = results[0].get('figures', {})

                    processed_result = {
                        'success': True,
                        'impacts': float(figures.get('impacts', 0)),
                        'reach': float(figures.get('reach', 0)),
                        'frequency': float(figures.get('frequency', 0)),
                        'grp': float(figures.get('grp', 0)),
                        'population': float(figures.get('population', 0)),
                        'frame_count': frame_count,
                        'processing_time': elapsed,
                        'raw_response': data
                    }

                    logger.debug(f"✅ PROCESSED REACH RESULT: {json.dumps(processed_result, indent=2, default=str)}")
                    return processed_result
                else:
                    logger.warning("⚠️  No results in reach API response - returning zero metrics")
                    return {
                        'success': True,
                        'impacts': 0,
                        'reach': 0,
                        'frequency': 0,
                        'grp': 0,
                        'population': 0,
                        'frame_count': frame_count,
                        'processing_time': elapsed,
                        'message': 'No audience data available'
                    }

            # Non-200 status codes
            elif response.status_code == 401:
                raise httpx.HTTPStatusError(
                    "Authentication failed",
                    request=response.request,
                    response=response
                )
            else:
                raise httpx.HTTPStatusError(
                    f"HTTP {response.status_code}",
                    request=response.request,
                    response=response
                )

        except (ValueError, KeyError, TypeError) as e:
            logger.error(f"Invalid reach API response format: {e}")
            raise ValueError(f"Invalid response format: {e}")

    async def _real_api_call_with_fallback(
        self, 
        request_data: dict, 
        frame_id: int, 
        spot_length: int
    ) -> Dict[str, Any]:
        """Make real API call with automatic fallback for demo safety"""
        
        try:
            # Use demo timeout for board safety
            timeout = httpx.Timeout(self.demo_timeout, connect=5.0)
            
            # Detailed API request logging (debug mode)
            # Use the live playout endpoint
            api_url = os.getenv('ROUTE_API_LIVE_PLAYOUT_URL', f"{self.base_url}/rest/process/playout")
            headers = self._get_headers()
            
            logger.debug("🚀 ROUTE API REQUEST:")
            logger.debug(f"   URL: {api_url}")
            logger.debug(f"   Headers: {json.dumps({k: v if k != 'x-api-key' and k != 'Authorization' else '***REDACTED***' for k, v in headers.items()}, indent=2)}")
            logger.debug(f"   Request Body: {json.dumps(request_data, indent=2)}")
            
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    api_url,
                    json=request_data,
                    headers=headers
                )
                
                # Log response details before processing (debug mode)
                logger.debug("📥 ROUTE API RESPONSE:")
                logger.debug(f"   Status Code: {response.status_code}")
                logger.debug(f"   Response Headers: {dict(response.headers)}")
                
                try:
                    response_text = response.text
                    logger.debug(f"   Response Body: {response_text}")
                except Exception as e:
                    logger.warning(f"   Could not log response body: {e}")
                
                return await self._process_api_response(response)
                
        except httpx.TimeoutException as e:
            logger.warning(f"Route API timeout ({self.demo_timeout}s), falling back to mock data")
            # Automatic fallback to mock for demo
            return await self._mock_response(frame_id, spot_length, fallback_reason="API timeout")
            
        except httpx.HTTPStatusError as e:
            status_code = e.response.status_code
            if status_code == 401:
                logger.warning("Route API authentication failed - credentials may be invalid")
                # Don't expose credential details in logs
                return await self._mock_response(frame_id, spot_length, fallback_reason="Authentication failed")
            else:
                logger.warning(f"Route API HTTP error {status_code}, falling back to mock data")
                return await self._mock_response(frame_id, spot_length, fallback_reason=f"HTTP {status_code}")
            
        except httpx.ConnectError as e:
            logger.warning(f"Route API connection failed, falling back to mock data")
            return await self._mock_response(frame_id, spot_length, fallback_reason="Connection failed")
            
        except Exception as e:
            # Never expose credential information in error messages
            logger.error(f"Unexpected Route API error: {type(e).__name__}")
            return await self._mock_response(frame_id, spot_length, fallback_reason="Unexpected error")
    
    async def _process_api_response(self, response: httpx.Response) -> Dict[str, Any]:
        """Process Route API response with proper error handling"""
        start_time = time.time()
        
        try:
            elapsed = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                
                logger.debug("🔍 PROCESSING API RESPONSE:")
                logger.debug(f"   Raw JSON: {json.dumps(data, indent=2)}")
                
                # Extract key metrics
                results = data.get('results', [])
                logger.debug(f"   Results array length: {len(results)}")
                
                if results:
                    figures = results[0].get('figures', {})
                    logger.debug(f"   Figures from first result: {json.dumps(figures, indent=2)}")
                    
                    impacts = float(figures.get('impacts', 0))
                    # Reach calculation with API data
                    estimated_reach = impacts / 3.0 if impacts > 0 else 0
                    
                    processed_result = {
                        'success': True,
                        'impacts': impacts,
                        'impacts_pedestrian': float(figures.get('impacts_pedestrian', 0)),
                        'impacts_vehicular': float(figures.get('impacts_vehicular', 0)),
                        'playouts_total': int(figures.get('playouts_total', 0)),
                        'audience_spot_avg': float(figures.get('audience_spot_avg', 0)),
                        'reach': estimated_reach,
                        'frequency': 3.0,
                        'gross_rating_points': float(figures.get('gross_rating_points', 0)),
                        'population': float(figures.get('population', 0)),
                        'processing_time': elapsed,
                        'raw_response': data
                    }
                    
                    logger.debug(f"✅ PROCESSED RESULT: {json.dumps(processed_result, indent=2, default=str)}")
                    return processed_result
                else:
                    logger.warning("⚠️  No results in API response - returning zero metrics")
                    no_results_response = {
                        'success': True,
                        'impacts': 0,
                        'reach': 0,
                        'frequency': 0,
                        'processing_time': elapsed,
                        'message': 'No audience data for this frame'
                    }
                    logger.debug(f"📊 NO RESULTS RESPONSE: {json.dumps(no_results_response, indent=2)}")
                    return no_results_response
            
            # Non-200 status codes
            elif response.status_code == 401:
                raise httpx.HTTPStatusError(
                    "Authentication failed", 
                    request=response.request, 
                    response=response
                )
            elif response.status_code == 429:
                raise httpx.HTTPStatusError(
                    "Rate limit exceeded", 
                    request=response.request, 
                    response=response
                )
            elif response.status_code >= 500:
                raise httpx.HTTPStatusError(
                    "Server error", 
                    request=response.request, 
                    response=response
                )
            else:
                raise httpx.HTTPStatusError(
                    f"HTTP {response.status_code}", 
                    request=response.request, 
                    response=response
                )
                
        except (ValueError, KeyError, TypeError) as e:
            logger.error(f"Invalid API response format: {e}")
            raise ValueError(f"Invalid response format: {e}")
    
    async def _mock_response(
        self, 
        frame_id: int, 
        spot_length: int, 
        fallback_reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate mock response for demo with optional fallback indicator"""
        await asyncio.sleep(self.mock_delay)
        
        # Use fallback data generator for consistency
        mock_data = self._generate_fallback_audience_data(frame_id, spot_length)
        mock_data.update({
            'success': True,
            'demo_mode': True
        })
        
        # Add fallback reason if this was automatic fallback
        if fallback_reason:
            mock_data['fallback_reason'] = fallback_reason
            logger.info(f"Auto-fallback to mock data: {fallback_reason}")
        
        return mock_data
    
    async def get_batch_audiences(
        self,
        playouts: List[Dict],
        release_id: int = None
    ) -> List[Dict]:
        """
        Get audiences for multiple playouts (batch processing)
        
        Args:
            playouts: List of playout dicts with frame_id, start, end
            release_id: Route release ID
            
        Returns:
            List of audience results
        """
        logger.debug(f"🚀 BATCH PROCESSING: Starting batch of {len(playouts)} playouts")
        
        tasks = []
        for i, playout in enumerate(playouts):
            frame_id = playout['frameid']
            start_date = playout['start_route']
            end_date = playout['end_route']
            spot_length = playout.get('spotlength', self.config.default_spot_length * 1000) / 1000  # Convert ms to seconds
            
            logger.debug(f"   Task {i+1}: Frame {frame_id}, {start_date} to {end_date}, {spot_length}s")
            
            task = self.get_playout_audience(
                frame_id=frame_id,
                datetime_from=start_date,
                datetime_until=end_date,
                spot_length=spot_length,
                release_id=release_id or self.config.default_release_id
            )
            tasks.append(task)
        
        logger.debug(f"⏳ BATCH PROCESSING: Executing {len(tasks)} API calls...")
        results = await asyncio.gather(*tasks)
        
        # Combine with playout data and add batch processing info
        for playout, result in zip(playouts, results):
            playout['audience'] = result  # Use 'audience' key to match campaign_service expectations
        
        # Log batch processing summary for monitoring
        successful = sum(1 for r in results if r.get('success', False))
        logger.info(f"✅ BATCH PROCESSING: {successful}/{len(results)} successful")
        
        # Log detailed results for debugging
        for i, (playout, result) in enumerate(zip(playouts, results)):
            frame_id = playout['frameid']
            impacts = result.get('impacts', 0) if result else 0
            logger.debug(f"   Result {i+1}: Frame {frame_id} -> {impacts} impacts")
        
        return playouts
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test API connectivity with detailed board-safe results"""
        if self.use_mock:
            return {
                'connected': True,
                'mode': 'demo',
                'response_time': 5,
                'message': 'Demo mode active'
            }
        
        start_time = time.time()
        
        try:
            timeout = httpx.Timeout(5.0, connect=2.0)  # Quick test for demo
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    f"{self.base_url}/rest/version",
                    headers=self._get_headers(),
                    json={}
                )
                
                elapsed = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    return {
                        'connected': True,
                        'mode': 'live',
                        'response_time': round(elapsed, 1),
                        'message': 'API connected successfully'
                    }
                else:
                    return {
                        'connected': False,
                        'mode': 'fallback',
                        'response_time': round(elapsed, 1),
                        'message': 'Demo data will be used'
                    }
                    
        except Exception as e:
            elapsed = (time.time() - start_time) * 1000
            logger.warning(f"Route API connection test failed: {e}")
            
            return {
                'connected': False,
                'mode': 'fallback',
                'response_time': round(elapsed, 1),
                'message': 'Demo data will be used'
            }
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics for monitoring"""
        return self.cache.stats()
    
    def clear_cache(self) -> None:
        """Clear the cache manually"""
        self.cache.clear()