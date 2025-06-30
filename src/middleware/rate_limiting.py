from fastapi import Request, HTTPException, status
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Optional, Tuple
import asyncio
import time
import hashlib
import logging
from src.config.settings import settings

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self, max_requests: int = 100, window_seconds: int = 3600, cleanup_interval: int = 300):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.cleanup_interval = cleanup_interval
        self.requests: Dict[str, List[float]] = defaultdict(list)
        self.blocked_ips: Dict[str, float] = {}
        self.last_cleanup = time.time()
    
    def _cleanup_old_requests(self):
        """Remove old request records to prevent memory leaks"""
        current_time = time.time()
        if current_time - self.last_cleanup < self.cleanup_interval:
            return
        
        cutoff_time = current_time - self.window_seconds
        
        # Clean up request history
        for client_id in list(self.requests.keys()):
            self.requests[client_id] = [
                req_time for req_time in self.requests[client_id]
                if req_time > cutoff_time
            ]
            if not self.requests[client_id]:
                del self.requests[client_id]
        
        # Clean up blocked IPs
        for ip in list(self.blocked_ips.keys()):
            if current_time - self.blocked_ips[ip] > self.window_seconds * 2:
                del self.blocked_ips[ip]
        
        self.last_cleanup = current_time
        logger.info(f"Rate limiter cleanup completed. Active clients: {len(self.requests)}")
    
    def _get_client_identifier(self, request: Request, user_id: Optional[int] = None) -> str:
        """Generate a unique identifier for the client"""
        # Use user ID if authenticated, otherwise use IP + User-Agent hash
        if user_id:
            return f"user:{user_id}"
        
        client_ip = self._get_real_ip(request)
        user_agent = request.headers.get("user-agent", "")
        identifier = f"{client_ip}:{hashlib.md5(user_agent.encode()).hexdigest()[:8]}"
        return identifier
    
    def _get_real_ip(self, request: Request) -> str:
        """Get the real client IP, considering proxies"""
        # Check for common proxy headers
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    def is_allowed(self, request: Request, user_id: Optional[int] = None) -> Tuple[bool, Dict]:
        """Check if request is allowed and return rate limit info"""
        self._cleanup_old_requests()
        
        client_id = self._get_client_identifier(request, user_id)
        client_ip = self._get_real_ip(request)
        current_time = time.time()
        
        # Check if IP is temporarily blocked
        if client_ip in self.blocked_ips:
            if current_time - self.blocked_ips[client_ip] < self.window_seconds:
                return False, {
                    "error": "IP temporarily blocked",
                    "retry_after": int(self.window_seconds - (current_time - self.blocked_ips[client_ip]))
                }
            else:
                del self.blocked_ips[client_ip]
        
        # Clean old requests for this client
        cutoff_time = current_time - self.window_seconds
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if req_time > cutoff_time
        ]
        
        current_requests = len(self.requests[client_id])
        
        if current_requests >= self.max_requests:
            # Block IP if too many requests
            self.blocked_ips[client_ip] = current_time
            logger.warning(f"Rate limit exceeded for {client_id} (IP: {client_ip})")
            
            return False, {
                "error": "Rate limit exceeded",
                "limit": self.max_requests,
                "window": self.window_seconds,
                "retry_after": self.window_seconds
            }
        
        # Record this request
        self.requests[client_id].append(current_time)
        
        return True, {
            "limit": self.max_requests,
            "remaining": self.max_requests - current_requests - 1,
            "reset": int(current_time + self.window_seconds),
            "window": self.window_seconds
        }

class AdvancedRateLimiter:
    """Advanced rate limiter with NO hardcoded roles - uses environment configuration"""
    
    def __init__(self):
        if not settings.rate_limit_enabled:
            # Disable rate limiting by setting very high limits
            self.limiters = {
                "auth_login": RateLimiter(max_requests=999999, window_seconds=1),
                "auth_register": RateLimiter(max_requests=999999, window_seconds=1),
                "auth_refresh": RateLimiter(max_requests=999999, window_seconds=1),
                "api_anonymous": RateLimiter(max_requests=999999, window_seconds=1),
                "api_authenticated": RateLimiter(max_requests=999999, window_seconds=1),
                "api_admin": RateLimiter(max_requests=999999, window_seconds=1),
                "file_upload": RateLimiter(max_requests=999999, window_seconds=1),
            }
        else:
            # Use configured limits from environment
            self.limiters = {
                "auth_login": RateLimiter(
                    max_requests=settings.rate_limit_login_max, 
                    window_seconds=settings.rate_limit_login_window,
                    cleanup_interval=settings.rate_limit_cleanup_interval
                ),
                "auth_register": RateLimiter(
                    max_requests=settings.rate_limit_register_max, 
                    window_seconds=settings.rate_limit_register_window,
                    cleanup_interval=settings.rate_limit_cleanup_interval
                ),
                "auth_refresh": RateLimiter(
                    max_requests=10, 
                    window_seconds=300,
                    cleanup_interval=settings.rate_limit_cleanup_interval
                ),
                "api_anonymous": RateLimiter(
                    max_requests=settings.rate_limit_api_anonymous_max, 
                    window_seconds=settings.rate_limit_api_anonymous_window,
                    cleanup_interval=settings.rate_limit_cleanup_interval
                ),
                "api_authenticated": RateLimiter(
                    max_requests=settings.rate_limit_api_authenticated_max, 
                    window_seconds=settings.rate_limit_api_authenticated_window,
                    cleanup_interval=settings.rate_limit_cleanup_interval
                ),
                "api_admin": RateLimiter(
                    max_requests=settings.rate_limit_api_admin_max, 
                    window_seconds=settings.rate_limit_api_admin_window,
                    cleanup_interval=settings.rate_limit_cleanup_interval
                ),
                "file_upload": RateLimiter(
                    max_requests=20, 
                    window_seconds=3600,
                    cleanup_interval=settings.rate_limit_cleanup_interval
                ),
            }
    
    def get_limiter_key(self, request: Request, user_roles: List[str] = None) -> str:
        """Determine which rate limiter to use based on endpoint and user - NO hardcoded roles"""
        path = request.url.path
        
        # Authentication endpoints
        if path.startswith("/auth/login"):
            return "auth_login"
        elif path.startswith("/auth/register"):
            return "auth_register"
        elif path.startswith("/auth/refresh"):
            return "auth_refresh"
        elif path.startswith("/upload"):
            return "file_upload"
        
        # API endpoints based on user role - DYNAMIC ADMIN DETECTION
        if user_roles:
            # Check if user has any admin roles (dynamically determined)
            admin_roles = settings.admin_roles
            if any(role in admin_roles for role in user_roles):
                return "api_admin"
            else:
                return "api_authenticated"
        
        return "api_anonymous"
    
    def check_rate_limit(self, request: Request, user_id: Optional[int] = None, 
                        user_roles: List[str] = None) -> Tuple[bool, Dict]:
        """Check rate limit for the request"""
        limiter_key = self.get_limiter_key(request, user_roles)
        limiter = self.limiters[limiter_key]
        
        allowed, info = limiter.is_allowed(request, user_id)
        info["limiter_type"] = limiter_key
        
        return allowed, info

# Global advanced rate limiter instance
advanced_limiter = AdvancedRateLimiter()

async def rate_limit_middleware(request: Request, call_next):
    """Enhanced rate limiting middleware with user context - NO hardcoded roles"""
    
    # Skip rate limiting for health checks and docs
    if request.url.path in ["/health", settings.docs_url, settings.redoc_url, settings.openapi_url]:
        return await call_next(request)
    
    # Skip if rate limiting is disabled
    if not settings.rate_limit_enabled:
        return await call_next(request)
    
    user_id = None
    user_roles = []
    
    # Try to get user context from token if present
    try:
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            from src.core.security import verify_token
            from src.config.database import SessionLocal
            from src.models.user import User
            
            token = auth_header.split(" ")[1]
            payload = verify_token(token, "access")
            
            if payload:
                username = payload.get("sub")
                if username:
                    db = SessionLocal()
                    try:
                        user = db.query(User).filter(User.username == username).first()
                        if user and user.is_active:
                            user_id = user.id
                            user_roles = user.get_role_names()
                    finally:
                        db.close()
    except Exception as e:
        logger.debug(f"Error getting user context for rate limiting: {e}")
    
    # Check rate limit
    allowed, rate_info = advanced_limiter.check_rate_limit(request, user_id, user_roles)
    
    if not allowed:
        logger.warning(
            f"Rate limit exceeded: {request.client.host} "
            f"- {request.method} {request.url.path} "
            f"- User: {user_id or 'anonymous'} "
            f"- Type: {rate_info.get('limiter_type')}"
        )
        
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "Rate limit exceeded",
                "message": rate_info.get("error", "Too many requests"),
                "retry_after": rate_info.get("retry_after", 3600),
                "limit": rate_info.get("limit"),
                "window_seconds": rate_info.get("window")
            },
            headers={
                "X-RateLimit-Limit": str(rate_info.get("limit", 0)),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(rate_info.get("reset", 0)),
                "Retry-After": str(rate_info.get("retry_after", 3600))
            }
        )
    
    # Add rate limit headers to response
    response = await call_next(request)
    
    response.headers["X-RateLimit-Limit"] = str(rate_info.get("limit", 0))
    response.headers["X-RateLimit-Remaining"] = str(rate_info.get("remaining", 0))
    response.headers["X-RateLimit-Reset"] = str(rate_info.get("reset", 0))
    response.headers["X-RateLimit-Window"] = str(rate_info.get("window", 0))
    
    return response

# Decorator for additional endpoint-specific rate limiting
def endpoint_rate_limit(max_requests: int, window_seconds: int):
    """Decorator for additional endpoint-specific rate limiting"""
    limiter = RateLimiter(max_requests, window_seconds)
    
    def decorator(func):
        async def wrapper(request: Request, *args, **kwargs):
            allowed, info = limiter.is_allowed(request)
            if not allowed:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Endpoint rate limit exceeded. Try again in {info.get('retry_after', 0)} seconds."
                )
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator