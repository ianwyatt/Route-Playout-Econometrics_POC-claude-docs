# ABOUTME: SPACE API client for Route Playout Econometrics POC
# ABOUTME: Handles lookups for media owners, buyers, agencies with caching and mock fallback

import os
import json
import time
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging
from src.utils.ttl_cache import TTLCache
from src.utils.error_handlers import (
    DemoErrorHandler,
    demo_safe_api_call,
    log_api_metrics,
    ErrorType
)
from src.config import get_space_config, get_entity_config
from src.utils.credentials import get_space_credentials, is_mock_mode_active

logger = logging.getLogger(__name__)


@dataclass
class SpaceEntity:
    """Represents a SPACE API entity (media owner, buyer, agency, etc.)."""
    id: str
    name: str
    type: str
    details: Dict[str, Any]
    last_updated: datetime




class SpaceAPIClient:
    """Client for SPACE API with basic auth and caching."""
    
    def __init__(self, username: Optional[str] = None, password: Optional[str] = None,
                 use_mock: Optional[bool] = None):
        """
        Initialize SPACE API client with secure credential management.
        
        Args:
            username: SPACE API username (uses credential manager if not provided)
            password: SPACE API password (uses credential manager if not provided) 
            use_mock: Use mock data (uses credential validation result if not provided)
        """
        # Load configuration
        self.space_config = get_space_config()
        self.entity_config = get_entity_config()
        
        # Get validated credentials or use provided ones
        if username is not None and password is not None:
            # Use provided credentials (for testing)
            self.username = username
            self.password = password
            credentials_force_mock = False
        else:
            # Use credential manager for validation and automatic mock mode
            self.username, self.password, credentials_force_mock = get_space_credentials()
        
        # API settings from config
        self.base_url = self.space_config.base_url
        self.timeout = self.space_config.timeout
        self.demo_timeout = self.space_config.demo_timeout
        
        # Determine mock mode - use credential-based decision or config/parameter override
        if use_mock is not None:
            self.use_mock = use_mock
        else:
            self.use_mock = credentials_force_mock or self.space_config.use_mock or is_mock_mode_active()
        
        # TTL cache for production safety - prevents memory exhaustion during demos
        self.cache = TTLCache(max_size=self.space_config.cache_size, default_ttl=self.space_config.cache_ttl)
        self.logger = logging.getLogger(__name__)
        
        # Mock data for fallback from configuration
        self.mock_data = self.entity_config.mock_entities
        
        # Log credential status for admin monitoring (without exposing values)
        if self.use_mock:
            if credentials_force_mock:
                self.logger.info("🎭 SPACE API using mock mode due to credential validation")
            else:
                self.logger.info("🎭 SPACE API using mock mode by configuration")
        else:
            self.logger.info("✅ SPACE API credentials validated - live mode available")
    
    def _get_auth(self) -> tuple:
        """Get basic auth tuple - demo safe"""
        if not self.username or not self.password:
            # This should not happen due to credential validation, but safety first
            self.logger.warning("Missing credentials in _get_auth - this should not happen")
            return ("", "")
        return (self.username, self.password)
    
    def _make_request_with_fallback(
        self,
        endpoint: str,
        entity_type: str,
        entity_id: str,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Make API request with automatic fallback for demo safety.

        Args:
            endpoint: API endpoint
            entity_type: Type of entity being requested
            entity_id: ID of the entity
            params: Query parameters

        Returns:
            API response data or mock fallback
        """
        url = f"{self.base_url}{endpoint}"

        try:
            # Use demo timeout for safety
            response = requests.get(
                url,
                params=params,
                auth=self._get_auth(),
                timeout=self.demo_timeout,
                headers={'User-Agent': 'Route-Playout-Econometrics-POC/1.0'}
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                self.logger.warning(f"SPACE API authentication failed for {entity_type} {entity_id} - credentials may be invalid")
                # Don't expose credential details in logs
                return self._get_mock_entity_data(entity_type, entity_id)
            elif response.status_code == 404:
                self.logger.info(f"SPACE API entity not found: {entity_type} {entity_id}, using mock data")
                return self._get_mock_entity_data(entity_type, entity_id)
            elif response.status_code == 429:
                self.logger.warning(f"SPACE API rate limited for {entity_type} {entity_id}, using mock data")
                return self._get_mock_entity_data(entity_type, entity_id)
            else:
                self.logger.warning(f"SPACE API HTTP {response.status_code} for {entity_type} {entity_id}, using mock data")
                return self._get_mock_entity_data(entity_type, entity_id)
                
        except requests.exceptions.Timeout:
            self.logger.warning(f"SPACE API timeout ({self.demo_timeout}s) for {entity_type} {entity_id}, using mock data")
            return self._get_mock_entity_data(entity_type, entity_id)
            
        except requests.exceptions.ConnectionError:
            self.logger.warning(f"SPACE API connection failed for {entity_type} {entity_id}, using mock data")
            return self._get_mock_entity_data(entity_type, entity_id)
            
        except requests.exceptions.RequestException as e:
            self.logger.warning(f"SPACE API request failed for {entity_type} {entity_id}: {e}, using mock data")
            return self._get_mock_entity_data(entity_type, entity_id)
            
        except Exception as e:
            self.logger.error(f"Unexpected SPACE API error for {entity_type} {entity_id}: {e}, using mock data")
            return self._get_mock_entity_data(entity_type, entity_id)
    
    def _get_mock_entity_data(self, entity_type: str, entity_id: str) -> Dict[str, Any]:
        """Get mock entity data as dict for fallback processing"""
        mock_delay = float(os.getenv('MOCK_RESPONSE_DELAY', '0.1'))
        time.sleep(mock_delay)
        
        type_map = {
            'media_owner': 'media_owners',
            'buyer': 'buyers', 
            'agency': 'agencies',
            'brand': 'brands'
        }
        
        mock_type = type_map.get(entity_type)
        if mock_type and entity_id in self.mock_data[mock_type]:
            data = self.mock_data[mock_type][entity_id].copy()
            data['id'] = entity_id
            return data
        
        # Return unknown entity data if not found
        return {
            'id': entity_id,
            'name': f"Unknown {entity_type.title()} ({entity_id})",
            'status': 'unknown',
            'demo_fallback': True
        }
    
    def _get_mock_entity(self, entity_type: str, entity_id: str) -> Optional[SpaceEntity]:
        """Get mock entity data."""
        mock_delay = float(os.getenv('MOCK_RESPONSE_DELAY', '0.1'))
        time.sleep(mock_delay)
        
        type_map = {
            'media_owner': 'media_owners',
            'buyer': 'buyers', 
            'agency': 'agencies',
            'brand': 'brands'
        }
        
        mock_type = type_map.get(entity_type)
        if mock_type and entity_id in self.mock_data[mock_type]:
            data = self.mock_data[mock_type][entity_id]
            return SpaceEntity(
                id=entity_id,
                name=data['name'],
                type=entity_type,
                details=data,
                last_updated=datetime.now()
            )
        
        # Return unknown entity if not found in mock data
        return SpaceEntity(
            id=entity_id,
            name=f"Unknown {entity_type.title()} ({entity_id})",
            type=entity_type,
            details={'status': 'unknown'},
            last_updated=datetime.now()
        )
    
    def get_media_owner(self, media_owner_id: str) -> SpaceEntity:
        """
        Get media owner details with automatic fallback for demo safety.

        Args:
            media_owner_id: Media owner ID

        Returns:
            SpaceEntity with media owner details
        """
        # Check cache first
        cache_key = f"media_owner:{media_owner_id}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached
        
        try:
            if self.use_mock:
                entity = self._get_mock_entity('media_owner', media_owner_id)
            else:
                response = self._make_request_with_fallback(
                    f"/media-owners/{media_owner_id}", 
                    'media_owner', 
                    media_owner_id
                )
                entity = SpaceEntity(
                    id=media_owner_id,
                    name=response.get('name', f'Media Owner {media_owner_id}'),
                    type='media_owner',
                    details=response,
                    last_updated=datetime.now()
                )
            
            # Always cache for demo performance
            self.cache.put(cache_key, entity)
            return entity

        except Exception as e:
            self.logger.error(f"Critical error getting media owner {media_owner_id}: {e}")
            # Final fallback - always return something for demo
            return self._get_mock_entity('media_owner', media_owner_id)
    
    def get_buyer(self, buyer_id: str) -> SpaceEntity:
        """
        Get buyer details with automatic fallback for demo safety.
        
        Args:
            buyer_id: Buyer ID
            
        Returns:
            SpaceEntity with buyer details
        """
        cache_key = f"buyer:{buyer_id}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached
        
        try:
            if self.use_mock:
                entity = self._get_mock_entity('buyer', buyer_id)
            else:
                response = self._make_request_with_fallback(
                    f"/buyers/{buyer_id}", 
                    'buyer', 
                    buyer_id
                )
                entity = SpaceEntity(
                    id=buyer_id,
                    name=response.get('name', f'Buyer {buyer_id}'),
                    type='buyer',
                    details=response,
                    last_updated=datetime.now()
                )
            
            self.cache.put(cache_key, entity)
            return entity
            
        except Exception as e:
            self.logger.error(f"Critical error getting buyer {buyer_id}: {e}")
            return self._get_mock_entity('buyer', buyer_id)
    
    def get_agency(self, agency_id: str) -> SpaceEntity:
        """
        Get agency details with automatic fallback for demo safety.
        
        Args:
            agency_id: Agency ID
            
        Returns:
            SpaceEntity with agency details
        """
        cache_key = f"agency:{agency_id}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached
        
        try:
            if self.use_mock:
                entity = self._get_mock_entity('agency', agency_id)
            else:
                response = self._make_request_with_fallback(
                    f"/agencies/{agency_id}", 
                    'agency', 
                    agency_id
                )
                entity = SpaceEntity(
                    id=agency_id,
                    name=response.get('name', f'Agency {agency_id}'),
                    type='agency',
                    details=response,
                    last_updated=datetime.now()
                )
            
            self.cache.put(cache_key, entity)
            return entity
            
        except Exception as e:
            self.logger.error(f"Critical error getting agency {agency_id}: {e}")
            return self._get_mock_entity('agency', agency_id)
    
    def get_brand(self, brand_id: str) -> SpaceEntity:
        """
        Get brand details with automatic fallback for demo safety.
        
        Args:
            brand_id: Brand ID
            
        Returns:
            SpaceEntity with brand details
        """
        cache_key = f"brand:{brand_id}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached
        
        try:
            if self.use_mock:
                entity = self._get_mock_entity('brand', brand_id)
            else:
                response = self._make_request_with_fallback(
                    f"/brands/{brand_id}", 
                    'brand', 
                    brand_id
                )
                entity = SpaceEntity(
                    id=brand_id,
                    name=response.get('name', f'Brand {brand_id}'),
                    type='brand',
                    details=response,
                    last_updated=datetime.now()
                )
            
            self.cache.put(cache_key, entity)
            return entity
            
        except Exception as e:
            self.logger.error(f"Critical error getting brand {brand_id}: {e}")
            return self._get_mock_entity('brand', brand_id)
    
    def get_frame(self, frame_id: str) -> Dict[str, Any]:
        """
        Get frame details including media owner from SPACE API.
        
        Args:
            frame_id: Frame ID
            
        Returns:
            Dict with frame details including media owner
        """
        cache_key = f"frame:{frame_id}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached
        
        try:
            if self.use_mock:
                # Return mock frame data
                return {
                    'FrameID': frame_id,
                    'MediaOwnerID': '171',  # Default to Clear Channel for mock
                    'MediaOwnerDescription': 'Clear Channel',
                    'LocationDescription': f'Mock Location {frame_id}',
                    'demo_fallback': True
                }
            
            # Make API request with frame ID parameter
            response = requests.get(
                f"{self.base_url}/frame",
                params={'id': frame_id},
                auth=self._get_auth(),
                timeout=self.demo_timeout,
                headers={'User-Agent': 'Route-Playout-Econometrics-POC/1.0'}
            )
            
            if response.status_code == 200:
                data = response.json()
                # Extract frame data from response
                if data and 'data' in data and len(data['data']) > 0:
                    frame_data = data['data'][0]
                    self.cache.put(cache_key, frame_data)
                    return frame_data
                else:
                    # Frame not found
                    self.logger.warning(f"Frame {frame_id} not found in SPACE API")
                    return {
                        'FrameID': frame_id,
                        'MediaOwnerID': 'unknown',
                        'MediaOwnerDescription': f'Unknown Media Owner',
                        'demo_fallback': True
                    }
            else:
                self.logger.warning(f"SPACE API HTTP {response.status_code} for frame {frame_id}")
                return {
                    'FrameID': frame_id,
                    'MediaOwnerID': 'unknown',
                    'MediaOwnerDescription': f'Unknown Media Owner',
                    'demo_fallback': True
                }
                
        except Exception as e:
            self.logger.error(f"Error getting frame {frame_id}: {e}")
            return {
                'FrameID': frame_id,
                'MediaOwnerID': 'unknown',
                'MediaOwnerDescription': f'Unknown Media Owner',
                'demo_fallback': True
            }
    
    def batch_lookup(self, lookups: List[Dict[str, str]]) -> Dict[str, SpaceEntity]:
        """
        Perform batch lookups with demo safety - never fails completely.
        
        Args:
            lookups: List of dicts with 'type' and 'id' keys
            
        Returns:
            Dict mapping lookup keys to SpaceEntity objects
        """
        results = {}
        successful = 0
        
        for lookup in lookups:
            entity_type = lookup['type']
            entity_id = lookup['id']
            key = f"{entity_type}:{entity_id}"
            
            try:
                if entity_type == 'media_owner':
                    results[key] = self.get_media_owner(entity_id)
                    successful += 1
                elif entity_type == 'buyer':
                    results[key] = self.get_buyer(entity_id)
                    successful += 1
                elif entity_type == 'agency':
                    results[key] = self.get_agency(entity_id)
                    successful += 1
                elif entity_type == 'brand':
                    results[key] = self.get_brand(entity_id)
                    successful += 1
                else:
                    self.logger.warning(f"Unknown entity type: {entity_type}")
                    # Create fallback entity for unknown types
                    results[key] = SpaceEntity(
                        id=entity_id,
                        name=f"Unknown {entity_type} ({entity_id})",
                        type=entity_type,
                        details={'status': 'unknown'},
                        last_updated=datetime.now()
                    )
                    
            except Exception as e:
                self.logger.error(f"Failed to lookup {key}: {e}")
                # Always provide fallback for demo
                results[key] = self._get_mock_entity(entity_type, entity_id)
        
        self.logger.info(f"Batch lookup: {successful}/{len(lookups)} successful")
        return results
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return self.cache.stats()
    
    def clear_cache(self):
        """Clear lookup cache."""
        self.cache.clear()
    
    def health_check(self) -> Dict[str, Any]:
        """Check SPACE API availability with demo safety."""
        if self.use_mock:
            return {
                'available': True,
                'mode': 'demo',
                'response_time': 5,
                'message': 'Demo mode active'
            }
        
        start_time = time.time()
        
        try:
            # Quick health check with known entity
            entity = self.get_media_owner("171")  # Clear Channel
            elapsed = (time.time() - start_time) * 1000
            
            return {
                'available': True,
                'mode': 'live' if not hasattr(entity.details, 'demo_fallback') else 'fallback',
                'response_time': round(elapsed, 1),
                'message': 'API connected successfully' if entity.details.get('demo_fallback') != True else 'Using demo data'
            }
            
        except Exception as e:
            elapsed = (time.time() - start_time) * 1000
            self.logger.warning(f"SPACE API health check failed: {e}")
            
            return {
                'available': False,
                'mode': 'fallback',
                'response_time': round(elapsed, 1),
                'message': 'Demo data will be used'
            }


# Convenience functions
def lookup_media_owner(media_owner_id: str) -> str:
    """Quick lookup of media owner name with demo safety."""
    try:
        client = SpaceAPIClient()
        entity = client.get_media_owner(media_owner_id)
        return entity.name
    except Exception as e:
        logger.error(f"Failed to lookup media owner {media_owner_id}: {e}")
        return f"Media Owner {media_owner_id}"


def lookup_buyer(buyer_id: str) -> str:
    """Quick lookup of buyer name with demo safety."""
    try:
        client = SpaceAPIClient()
        entity = client.get_buyer(buyer_id)
        return entity.name
    except Exception as e:
        logger.error(f"Failed to lookup buyer {buyer_id}: {e}")
        return f"Buyer {buyer_id}"