from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from src.config.settings import settings
import time
import logging
from collections import defaultdict
from typing import Dict, Tuple
import asyncio
import functools

logger = logging.getLogger(__name__)

class RateLimitStore:
    """In-memory rate limit store"""
    
    def __init__(self):
        self.requests: Dict[str, list] = defaultdict(list)
        self.last_cleanup = time.time()
    
    def is_rate_limited(self, key: str, max_requests: int, window_seconds: int) -> bool:
        """Check if key is rate limited"""
        now = time.time()
        window_start = now - window_seconds
        
        # Clean old requests periodically
        if now - self.last_cleanup > 300:  # Cleanup every 5 minutes
            self._cleanup_old_requests(window_start)
            self.last_cleanup = now
        
        # Get requests in current window
        if key not in self.requests:
            self.requests[key] = []
        
        # Remove old requests
        self.requests[key] = [req_time for req_time in self.requests[key] if req_time > window_start]
        
        # Check if rate limited
        if len(self.requests[key]) >= max_requests:
            return True
        
        # Add current request
        self.requests[key].append(now)
        return False
    
    def _cleanup_old_requests(self, cutoff_time: float):
        """Remove old requests to prevent memory leaks"""
        for key in list(self.requests.keys()):
            self.requests[key] = [req_time for req_time in self.requests[key] if req_time > cutoff_time]
            if not self.requests[key]:
                del self.requests[key]

# Global rate limit store
rate_limit_store = RateLimitStore()

async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware"""
    if not settings.rate_limit_enabled:
        return await call_next(request)
    
    # Get client IP
    client_ip = request.client.host if request.client else "unknown"
    
    # Rate limit based on endpoint
    path = request.url.path
    method = request.method
    
    # Different limits for different endpoints
    rate_limits = {
        "POST /api/v1/auth/login": (5, 900),  # 5 requests per 15 minutes
        "POST /api/v1/auth/register": (3, 3600),  # 3 requests per hour
    }
    
    # Default API limits
    default_limits = (100, 3600)  # 100 requests per hour for other endpoints
    
    # Get rate limit for this endpoint
    endpoint_key = f"{method} {path}"
    max_requests, window_seconds = rate_limits.get(endpoint_key, default_limits)
    
    # Create rate limit key
    rate_limit_key = f"{client_ip}:{endpoint_key}"
    
    # Check rate limit
    if rate_limit_store.is_rate_limited(rate_limit_key, max_requests, window_seconds):
        logger.warning(f"Rate limit exceeded for {client_ip} on {endpoint_key}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Max {max_requests} requests per {window_seconds} seconds.",
            headers={"Retry-After": str(window_seconds)}
        )
    
    response = await call_next(request)
    
    # Add rate limit headers
    response.headers["X-RateLimit-Limit"] = str(max_requests)
    response.headers["X-RateLimit-Window"] = str(window_seconds)
    
    return response

def endpoint_rate_limit(max_requests: int, window_seconds: int):
    """Decorator for endpoint-specific rate limiting (documentation only - actual limiting is in middleware)"""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # The actual rate limiting is handled by the middleware
            # This decorator is just for documentation and potential future use
            return await func(*args, **kwargs)
        
        # Store rate limit info for potential middleware use
        wrapper._rate_limit_max = max_requests
        wrapper._rate_limit_window = window_seconds
        
        return wrapper
    return decorator