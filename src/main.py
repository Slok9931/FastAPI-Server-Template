from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from src.api import auth, users, roles, permissions
from src.config.database import engine, Base
from src.models import user, role, permission, user_role, role_permission
from src.middleware.security_headers import SecurityHeadersMiddleware
from src.middleware.rate_limiting import rate_limit_middleware
from src.config.settings import settings
import time
import logging
import os
from logging.handlers import RotatingFileHandler

# Enhanced logging configuration from environment
log_level = getattr(logging, settings.log_level.upper())

# Create logs directory if it doesn't exist
os.makedirs(os.path.dirname(settings.log_file_path), exist_ok=True)

# Configure logging with rotation
handlers = [logging.StreamHandler()]

if settings.log_file_path:
    file_handler = RotatingFileHandler(
        settings.log_file_path,
        maxBytes=settings.log_max_file_size,
        backupCount=settings.log_backup_count
    )
    handlers.append(file_handler)

logging.basicConfig(
    level=log_level,
    format=settings.log_format,
    handlers=handlers
)

logger = logging.getLogger(__name__)

# FastAPI application with environment configuration
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=settings.app_description,
    docs_url=settings.docs_url if settings.docs_enabled else None,  # Remove production check
    redoc_url=settings.redoc_url if settings.docs_enabled else None,  # Remove production check
    openapi_url=settings.openapi_url if settings.docs_enabled else None,
    debug=settings.debug
)

# Security middleware
if settings.security_headers_enabled:
    app.add_middleware(SecurityHeadersMiddleware)

# CORS middleware with environment configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
    expose_headers=settings.cors_expose_headers
)

# Rate limiting middleware
if settings.rate_limit_enabled:
    app.middleware("http")(rate_limit_middleware)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    logger.info(
        f"Request: {request.method} {request.url.path} "
        f"- Client: {request.client.host if request.client else 'unknown'} "
        f"- User-Agent: {request.headers.get('user-agent', 'unknown')[:50]}"
    )
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(
        f"Response: {response.status_code} "
        f"- Time: {process_time:.3f}s "
        f"- Path: {request.url.path}"
    )
    
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Include routers with API prefix if configured
api_prefix = settings.api_prefix if settings.api_prefix != "/" else ""

app.include_router(auth.router, prefix=f"{api_prefix}/auth", tags=["Authentication"])
app.include_router(users.router, prefix=f"{api_prefix}/users", tags=["User Management"])
app.include_router(roles.router, prefix=f"{api_prefix}/roles", tags=["Role Management"])
app.include_router(permissions.router, prefix=f"{api_prefix}/permissions", tags=["Permission Management"])

@app.on_event("startup")
async def startup():
    logger.info(f"Application starting up in {settings.environment} environment...")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Rate limiting: {'enabled' if settings.rate_limit_enabled else 'disabled'}")
    logger.info(f"API documentation: {'enabled' if settings.docs_enabled else 'disabled'}")
    
    # Database initialization with retry logic
    max_retries = 5
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables created successfully")
            break
        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(f"Failed to create tables (attempt {attempt + 1}/{max_retries}): {e}")
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error(f"Failed to create database tables after {max_retries} attempts: {e}")
                raise e
    
    logger.info(f"{settings.app_name} v{settings.app_version} started successfully!")

@app.on_event("shutdown")
async def shutdown():
    logger.info("Application shutting down...")

@app.get("/", tags=["System"])
async def root():
    return {
        "message": f"Welcome to {settings.app_name}!",
        "version": settings.app_version,
        "environment": settings.environment,
        "docs": settings.docs_url if settings.docs_enabled and not settings.is_production else None,
        "api_prefix": settings.api_prefix
    }

@app.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "timestamp": time.time()
    }

@app.get("/config", tags=["System"])
async def get_config():
    """Get current configuration (non-sensitive values only)"""
    return {
        "app_name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "debug": settings.debug,
        "rate_limiting_enabled": settings.rate_limit_enabled,
        "docs_enabled": settings.docs_enabled,
        "api_prefix": settings.api_prefix,
        "default_page_size": settings.default_page_size,
        "max_page_size": settings.max_page_size,
        "access_token_expire_minutes": settings.access_token_expire_minutes,
        "user_registration_enabled": settings.user_registration_enabled
    }

if settings.rate_limit_enabled:
    @app.get("/rate-limit-status", tags=["System"])
    async def rate_limit_status(request: Request):
        """Check current rate limit status"""
        from src.middleware.rate_limiting import advanced_limiter
        
        allowed, info = advanced_limiter.check_rate_limit(request)
        
        return {
            "allowed": allowed,
            "rate_limit_info": info,
            "client_ip": request.client.host if request.client else "unknown"
        }