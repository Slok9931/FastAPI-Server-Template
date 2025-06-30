from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import time

# Import models to register them with SQLAlchemy
from src.models import User, Role, Permission, user_roles, role_permissions

from src.api.auth import router as auth_router
from src.api.users import router as users_router
from src.api.roles import router as roles_router
from src.api.permissions import router as permissions_router
from src.config.database import engine, get_db
from src.config.settings import settings
from src.core.init_db import init_database
from src.middleware.rate_limiting import rate_limit_middleware
from sqlalchemy.orm import Session

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format=settings.log_format
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("🚀 FastAPI Dynamic RBAC System starting up...")
    logger.info(f"Application starting up in {settings.environment} environment...")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Rate limiting: {'enabled' if settings.rate_limit_enabled else 'disabled'}")
    logger.info(f"API documentation: {'enabled' if settings.debug else 'disabled'}")
    
    try:
        # Initialize database
        await init_database()
        logger.info("✅ Database connection successful")
        
        # Create tables
        from src.config.database import Base
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
        logger.info(f"FastAPI Dynamic RBAC System v{settings.app_version} started successfully!")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Application shutting down...")

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=settings.app_description,
    debug=settings.debug,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=settings.allow_credentials,
    allow_methods=settings.allowed_methods,
    allow_headers=settings.allowed_headers,
)

# Add rate limiting middleware
if settings.rate_limit_enabled:
    app.middleware("http")(rate_limit_middleware)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log request
    logger.info(
        f"Request: {request.method} {request.url.path} - "
        f"Client: {request.client.host if request.client else 'unknown'} - "
        f"User-Agent: {request.headers.get('user-agent', 'unknown')[:100]}"
    )
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Log response
        logger.info(
            f"Response: {response.status_code} - "
            f"Time: {process_time:.3f}s - "
            f"Path: {request.url.path}"
        )
        
        return response
        
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"Request failed: {request.method} {request.url.path} - "
            f"Error: {str(e)} - Time: {process_time:.3f}s"
        )
        raise

# Include routers
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users_router, prefix="/api/v1/users", tags=["Users"])
app.include_router(roles_router, prefix="/api/v1/roles", tags=["Roles"])
app.include_router(permissions_router, prefix="/api/v1/permissions", tags=["Permissions"])

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.app_version,
        "environment": settings.environment,
        "debug": settings.debug
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.app_name} v{settings.app_version}",
        "docs": "/docs" if settings.debug else "Documentation disabled in production",
        "health": "/health",
        "environment": settings.environment
    }

# Global exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "path": request.url.path,
            "method": request.method
        }
    )

# Global exception handler for unexpected errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error" if not settings.debug else str(exc),
            "status_code": 500,
            "path": request.url.path,
            "method": request.method
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )