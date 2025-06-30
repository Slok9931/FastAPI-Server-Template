import os
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()

# Check Pydantic version and import accordingly
try:
    from pydantic_settings import BaseSettings
    from pydantic import validator
except ImportError:
    # Fallback for Pydantic v1
    from pydantic import BaseSettings, validator

class Settings(BaseSettings):
    # Database Configuration
    database_url: str = "sqlite:///./fastapi_app.db"
    database_pool_size: int = 5
    database_max_overflow: int = 10
    database_pool_timeout: int = 30
    database_pool_recycle: int = 3600
    
    # Security Configuration
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    password_hash_rounds: int = 12
    password_min_length: int = 8
    password_require_uppercase: bool = True
    password_require_lowercase: bool = True
    password_require_numbers: bool = True
    password_require_special_chars: bool = True
    
    # Application Configuration
    environment: str = "development"
    debug: bool = True
    app_name: str = "FastAPI Dynamic RBAC System"
    app_version: str = "2.0.0"
    app_description: str = "A secure FastAPI application with dynamic Role-Based Access Control"
    api_prefix: str = "/api/v1"
    timezone: str = "UTC"
    
    # Logging Configuration
    log_level: str = "INFO"
    log_file_path: str = "logs/security.log"
    log_max_file_size: int = 10485760  # 10MB
    log_backup_count: int = 5
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Rate Limiting Configuration
    rate_limit_enabled: bool = True
    rate_limit_login_max: int = 5
    rate_limit_login_window: int = 900
    rate_limit_register_max: int = 3
    rate_limit_register_window: int = 3600
    rate_limit_api_anonymous_max: int = 100
    rate_limit_api_anonymous_window: int = 3600
    rate_limit_api_authenticated_max: int = 1000
    rate_limit_api_authenticated_window: int = 3600
    rate_limit_api_admin_max: int = 2000
    rate_limit_api_admin_window: int = 3600
    rate_limit_cleanup_interval: int = 300
    
    # CORS Configuration
    cors_origins: str = "http://localhost:3000"
    cors_allow_credentials: bool = True
    cors_allow_methods: str = "GET,POST,PUT,DELETE,PATCH,OPTIONS"
    cors_allow_headers: str = "Authorization,Content-Type,X-Requested-With,Accept"
    cors_expose_headers: str = "X-RateLimit-Limit,X-RateLimit-Remaining,X-RateLimit-Reset"
    
    # Security Headers Configuration
    security_headers_enabled: bool = False
    x_content_type_options: str = "nosniff"
    x_frame_options: str = "DENY"
    x_xss_protection: str = "1; mode=block"
    strict_transport_security: str = "max-age=31536000; includeSubDomains"
    content_security_policy: str = "default-src 'self'; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:;"
    referrer_policy: str = "strict-origin-when-cross-origin"
    permissions_policy: str = "geolocation=(), microphone=(), camera=()"
    
    # API Documentation Configuration
    docs_enabled: bool = True
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    openapi_url: str = "/openapi.json"
    
    # Pagination Configuration
    default_page_size: int = 20
    max_page_size: int = 1000
    default_skip: int = 0
    
    # User Configuration
    username_min_length: int = 3
    username_max_length: int = 50
    email_validation_enabled: bool = True
    user_registration_enabled: bool = True
    account_activation_required: bool = False
    
    # Role Configuration - ONLY super_admin is predefined
    super_admin_role: str = "super_admin"  # This is the only fixed role
    default_user_role: str = "user"  # Default role for new users
    
    # Session Configuration
    session_timeout_minutes: int = 60
    max_concurrent_sessions: int = 5
    
    # File Upload Configuration
    max_file_size: int = 5242880  # 5MB
    allowed_file_types: str = "jpg,jpeg,png,pdf,doc,docx"
    upload_directory: str = "uploads"
    
    # Email Configuration
    smtp_host: str = "localhost"
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_use_tls: bool = True
    email_from: str = "noreply@yourcompany.com"
    
    # Redis Configuration
    redis_url: str = "redis://localhost:6379/0"
    redis_pool_size: int = 10
    
    # Monitoring Configuration
    metrics_enabled: bool = False
    health_check_enabled: bool = True
    performance_monitoring: bool = False
    
    # Development Configuration
    auto_reload: bool = True
    workers: int = 1
    host: str = "0.0.0.0"
    port: int = 8000
    
    @validator("secret_key")
    def validate_secret_key(cls, v):
        if not v or len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v
    
    @validator("cors_origins")
    def validate_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("cors_allow_methods")
    def validate_cors_methods(cls, v):
        if isinstance(v, str):
            return [method.strip() for method in v.split(",")]
        return v
    
    @validator("cors_allow_headers")
    def validate_cors_headers(cls, v):
        if isinstance(v, str):
            return [header.strip() for header in v.split(",")]
        return v
    
    @validator("cors_expose_headers")
    def validate_cors_expose_headers(cls, v):
        if isinstance(v, str):
            return [header.strip() for header in v.split(",")]
        return v
    
    @validator("allowed_file_types")
    def validate_file_types(cls, v):
        if isinstance(v, str):
            return [ext.strip() for ext in v.split(",")]
        return v
    
    @validator("super_admin_role")
    def validate_super_admin_role(cls, v):
        if not v or v.strip() == "":
            raise ValueError("Super admin role cannot be empty")
        return v.strip()
    
    @property
    def is_development(self) -> bool:
        return self.environment.lower() == "development"
    
    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"
    
    @property
    def is_testing(self) -> bool:
        return self.environment.lower() == "testing"
    
    @property
    def admin_roles(self) -> List[str]:
        """Get roles that should have admin privileges (configurable)"""
        # Only super_admin is guaranteed to have admin rights
        admin_role_names = [self.super_admin_role]
        return admin_role_names

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

# Global settings instance
settings = Settings()