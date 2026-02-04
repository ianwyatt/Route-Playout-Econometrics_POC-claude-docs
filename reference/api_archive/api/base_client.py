# ABOUTME: Base API client with shared functionality for all API clients
# ABOUTME: Reduces code duplication across Route and SPACE API clients

import requests
import logging
import time
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
import base64

from src.utils.ttl_cache import TTLCache
from src.utils.error_handlers import handle_api_error
from src.config import get_config


logger = logging.getLogger(__name__)


class BaseAPIClient(ABC):
    """
    Base class for all API clients with shared functionality.
    
    Features:
    - Automatic retry logic with exponential backoff
    - Caching with TTL
    - Error handling and logging
    - Authentication header management
    - Mock data fallback for demos
    """
    
    def __init__(self, api_name: str, cache_size: int = 1000, cache_ttl: float = 3600):
        """
        Initialize base API client.
        
        Args:
            api_name: Name of the API for logging
            cache_size: Maximum cache entries
            cache_ttl: Cache TTL in seconds
        """
        self.api_name = api_name
        self.config = get_config()
        self.cache = TTLCache(max_size=cache_size, default_ttl=cache_ttl)
        self.session = requests.Session()
        self._setup_session()
        
        # Performance metrics
        self.request_count = 0
        self.cache_hits = 0
        self.total_response_time = 0
    
    @abstractmethod
    def _setup_session(self):
        """Setup session with API-specific configuration"""
        pass
    
    @abstractmethod
    def _get_base_url(self) -> str:
        """Get the base URL for the API"""
        pass
    
    @abstractmethod
    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for the API"""
        pass
    
    def _make_request(
        self,
        endpoint: str,
        method: str = "GET",
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        use_cache: bool = True,
        cache_key: Optional[str] = None,
        retry_count: int = 3,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """
        Make an API request with retry logic and caching.
        
        Args:
            endpoint: API endpoint path
            method: HTTP method
            params: Query parameters
            data: Request body data
            use_cache: Whether to use caching
            cache_key: Custom cache key
            retry_count: Number of retries
            timeout: Request timeout in seconds
            
        Returns:
            API response data
        """
        # Generate cache key if not provided
        if not cache_key and use_cache:
            cache_key = self._generate_cache_key(endpoint, params)
        
        # Check cache for GET requests
        if method == "GET" and use_cache and cache_key:
            cached = self.cache.get(cache_key)
            if cached is not None:
                self.cache_hits += 1
                logger.debug(f"{self.api_name} cache hit for {cache_key}")
                return cached
        
        # Prepare request
        url = f"{self._get_base_url()}{endpoint}"
        headers = self._get_auth_headers()
        
        # Retry logic with exponential backoff
        last_error = None
        for attempt in range(retry_count):
            try:
                start_time = time.time()
                
                response = self.session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    json=data,
                    timeout=timeout
                )
                
                # Track metrics
                response_time = time.time() - start_time
                self.request_count += 1
                self.total_response_time += response_time
                
                # Check response status
                if response.status_code == 200:
                    result = response.json()
                    
                    # Cache successful GET responses
                    if method == "GET" and use_cache and cache_key:
                        self.cache.put(cache_key, result)
                    
                    logger.debug(f"{self.api_name} request successful: {endpoint} ({response_time:.2f}s)")
                    return result
                
                elif response.status_code == 429:  # Rate limited
                    retry_after = int(response.headers.get('Retry-After', 2 ** attempt))
                    logger.warning(f"{self.api_name} rate limited, retrying after {retry_after}s")
                    time.sleep(retry_after)
                    continue
                
                elif response.status_code >= 500:  # Server error
                    logger.warning(f"{self.api_name} server error {response.status_code}, attempt {attempt + 1}/{retry_count}")
                    if attempt < retry_count - 1:
                        time.sleep(2 ** attempt)  # Exponential backoff
                        continue
                    else:
                        raise Exception(f"Server error: {response.status_code}")
                
                else:  # Client error
                    error_msg = f"{self.api_name} request failed: {response.status_code}"
                    logger.error(f"{error_msg}: {response.text[:200]}")
                    raise Exception(error_msg)
                    
            except requests.exceptions.Timeout:
                last_error = f"Request timeout after {timeout}s"
                logger.warning(f"{self.api_name} timeout on attempt {attempt + 1}/{retry_count}")
                if attempt < retry_count - 1:
                    time.sleep(2 ** attempt)
                    continue
                    
            except requests.exceptions.ConnectionError as e:
                last_error = f"Connection error: {str(e)}"
                logger.warning(f"{self.api_name} connection error on attempt {attempt + 1}/{retry_count}")
                if attempt < retry_count - 1:
                    time.sleep(2 ** attempt)
                    continue
                    
            except Exception as e:
                last_error = str(e)
                logger.error(f"{self.api_name} unexpected error: {e}")
                break
        
        # All retries failed
        error_msg = last_error or f"Failed after {retry_count} attempts"
        logger.error(f"{self.api_name} request failed: {error_msg}")
        
        # Return mock data if available
        return self._get_mock_fallback(endpoint, params)
    
    def _generate_cache_key(self, endpoint: str, params: Optional[Dict] = None) -> str:
        """Generate a cache key from endpoint and parameters"""
        if params:
            param_str = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
            return f"{self.api_name}:{endpoint}?{param_str}"
        return f"{self.api_name}:{endpoint}"
    
    @abstractmethod
    def _get_mock_fallback(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Get mock data fallback for failed requests"""
        pass
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for this client"""
        avg_response_time = (
            self.total_response_time / self.request_count 
            if self.request_count > 0 else 0
        )
        
        cache_hit_rate = (
            self.cache_hits / (self.request_count + self.cache_hits) * 100
            if (self.request_count + self.cache_hits) > 0 else 0
        )
        
        return {
            'api_name': self.api_name,
            'request_count': self.request_count,
            'cache_hits': self.cache_hits,
            'cache_hit_rate': round(cache_hit_rate, 2),
            'avg_response_time': round(avg_response_time, 3),
            'total_response_time': round(self.total_response_time, 2)
        }
    
    def clear_cache(self):
        """Clear the cache for this client"""
        self.cache.clear()
        logger.info(f"{self.api_name} cache cleared")
    
    def __repr__(self) -> str:
        """String representation of the client"""
        metrics = self.get_metrics()
        return (
            f"{self.__class__.__name__}("
            f"requests={metrics['request_count']}, "
            f"cache_hit_rate={metrics['cache_hit_rate']}%)"
        )