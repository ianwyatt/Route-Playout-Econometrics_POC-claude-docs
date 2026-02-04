# ABOUTME: [PLACEHOLDER - NOT CURRENTLY USED] Circuit breaker pattern for API call management
# ABOUTME: Retained for future feature: on-demand API calls for data not in cache (e.g. regional reach, custom demographics)

import logging
from typing import Any, Dict, Optional, Callable
from functools import wraps
import asyncio
import time

logger = logging.getLogger(__name__)

class APIFallbackHandler:
    """Manages automatic fallback from real API to mock data"""
    
    def __init__(self):
        self.failure_counts = {}
        self.last_failure_time = {}
        self.circuit_open = {}
        self.max_failures = 3
        self.reset_timeout = 60  # seconds
        
    def is_circuit_open(self, api_name: str) -> bool:
        """Check if circuit breaker is open for an API"""
        if api_name not in self.circuit_open:
            return False
            
        if self.circuit_open[api_name]:
            # Check if enough time has passed to reset
            if time.time() - self.last_failure_time.get(api_name, 0) > self.reset_timeout:
                logger.info(f"🔄 Resetting circuit breaker for {api_name}")
                self.circuit_open[api_name] = False
                self.failure_counts[api_name] = 0
                return False
        
        return self.circuit_open.get(api_name, False)
    
    def record_failure(self, api_name: str):
        """Record an API failure"""
        self.failure_counts[api_name] = self.failure_counts.get(api_name, 0) + 1
        self.last_failure_time[api_name] = time.time()
        
        if self.failure_counts[api_name] >= self.max_failures:
            logger.warning(f"⚠️ {api_name} failed {self.max_failures} times, opening circuit breaker")
            self.circuit_open[api_name] = True
    
    def record_success(self, api_name: str):
        """Record an API success"""
        if api_name in self.failure_counts:
            self.failure_counts[api_name] = 0
        if api_name in self.circuit_open:
            self.circuit_open[api_name] = False

def with_fallback(api_name: str, fallback_func: Optional[Callable] = None):
    """
    Decorator to add automatic fallback to API calls
    
    Args:
        api_name: Name of the API for tracking
        fallback_func: Optional fallback function to call on failure
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            handler = APIFallbackHandler()
            
            # Check circuit breaker
            if handler.is_circuit_open(api_name):
                logger.info(f"🔄 Circuit open for {api_name}, using fallback")
                if fallback_func:
                    return await fallback_func(*args, **kwargs)
                raise Exception(f"{api_name} circuit breaker is open")
            
            try:
                # Try the real API call
                result = await func(*args, **kwargs)
                handler.record_success(api_name)
                return result
                
            except Exception as e:
                logger.warning(f"❌ {api_name} failed: {str(e)[:100]}")
                handler.record_failure(api_name)
                
                # Use fallback if available
                if fallback_func:
                    logger.info(f"🔄 Falling back to mock data for {api_name}")
                    return await fallback_func(*args, **kwargs)
                    
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            handler = APIFallbackHandler()
            
            # Check circuit breaker
            if handler.is_circuit_open(api_name):
                logger.info(f"🔄 Circuit open for {api_name}, using fallback")
                if fallback_func:
                    return fallback_func(*args, **kwargs)
                raise Exception(f"{api_name} circuit breaker is open")
            
            try:
                # Try the real API call
                result = func(*args, **kwargs)
                handler.record_success(api_name)
                return result
                
            except Exception as e:
                logger.warning(f"❌ {api_name} failed: {str(e)[:100]}")
                handler.record_failure(api_name)
                
                # Use fallback if available
                if fallback_func:
                    logger.info(f"🔄 Falling back to mock data for {api_name}")
                    return fallback_func(*args, **kwargs)
                    
                raise
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
            
    return decorator

# Global handler instance
fallback_handler = APIFallbackHandler()

def get_api_status() -> Dict[str, Any]:
    """Get current status of all APIs"""
    return {
        "failure_counts": fallback_handler.failure_counts,
        "circuit_status": {
            api: "open" if is_open else "closed"
            for api, is_open in fallback_handler.circuit_open.items()
        },
        "last_failures": {
            api: time.time() - last_time
            for api, last_time in fallback_handler.last_failure_time.items()
        }
    }