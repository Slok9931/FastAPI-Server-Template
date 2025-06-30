from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from src.config.settings import settings

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to all responses"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        if settings.security_headers_enabled:
            # Add security headers
            response.headers["X-Content-Type-Options"] = settings.x_content_type_options
            response.headers["X-Frame-Options"] = settings.x_frame_options
            response.headers["X-XSS-Protection"] = settings.x_xss_protection
            response.headers["Strict-Transport-Security"] = settings.strict_transport_security
            response.headers["Content-Security-Policy"] = settings.content_security_policy
            response.headers["Referrer-Policy"] = settings.referrer_policy
            response.headers["Permissions-Policy"] = settings.permissions_policy
            
            # Remove server header for security
            if "server" in response.headers:
                del response.headers["server"]
        
        return response