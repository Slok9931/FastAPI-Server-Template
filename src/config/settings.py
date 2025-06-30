from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
import os

class Settings(BaseSettings):
    # Database Configuration
    database_url: str = Field(default="sqlite:///./fastapi_app.db", description="Database URL")
    database_pool_size: int = Field(default=5, description="Database connection pool size")
    database_max_overflow: int = Field(default=10, description="Database max overflow connections")
    database_pool_timeout: int = Field(default=30, description="Database pool timeout in seconds")
    database_pool_recycle: int = Field(default=3600, description="Database pool recycle time")
    
    # Security Configuration
    secret_key: str = Field(default="your-super-secret-key-change-in-production-please", description="JWT secret key")
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(default=15, description="Access token expiration in minutes")
    refresh_token_expire_days: int = Field(default=7, description="Refresh token expiration in days")
    password_hash_rounds: int = Field(default=12, description="Password hash rounds")
    password_min_length: int = Field(default=8, description="Minimum password length")
    password_require_uppercase: bool = Field(default=True, description="Require uppercase in password")
    password_require_lowercase: bool = Field(default=True, description="Require lowercase in password")
    password_require_numbers: bool = Field(default=True, description="Require numbers in password")
    password_require_special_chars: bool = Field(default=True, description="Require special chars in password")
    
    # Application Configuration
    environment: str = Field(default="development", description="Application environment")
    debug: bool = Field(default=True, description="Debug mode")
    app_name: str = Field(default="FastAPI Dynamic RBAC System", description="Application name")
    app_version: str = Field(default="2.0.0", description="Application version")
    app_description: str = Field(default="A secure FastAPI application with dynamic Role-Based Access Control", description="App description")
    
    # CORS Configuration
    allowed_origins: List[str] = Field(default=["*"], description="Allowed CORS origins")
    allowed_methods: List[str] = Field(default=["*"], description="Allowed CORS methods")
    allowed_headers: List[str] = Field(default=["*"], description="Allowed CORS headers")
    allow_credentials: bool = Field(default=True, description="Allow CORS credentials")
    
    # Rate Limiting Configuration
    rate_limit_enabled: bool = Field(default=True, description="Enable rate limiting")
    rate_limit_login_max: int = Field(default=5, description="Max login attempts")
    rate_limit_login_window: int = Field(default=900, description="Login rate limit window in seconds")
    rate_limit_register_max: int = Field(default=3, description="Max registration attempts")
    rate_limit_register_window: int = Field(default=3600, description="Registration rate limit window")
    rate_limit_api_anonymous_max: int = Field(default=100, description="Max anonymous API calls")
    rate_limit_api_anonymous_window: int = Field(default=3600, description="Anonymous API rate limit window")
    
    # Security Headers
    security_headers_enabled: bool = Field(default=True, description="Enable security headers")
    
    # User Configuration
    username_min_length: int = Field(default=3, description="Minimum username length")
    username_max_length: int = Field(default=50, description="Maximum username length")
    
    # Role Configuration
    super_admin_role: str = Field(default="super_admin", description="Super admin role name")
    default_user_role: str = Field(default="user", description="Default user role name")
    
    # Logging Configuration
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s", description="Log format")
    
    # Server Configuration (these will be ignored by Pydantic but won't cause errors)
    host: str = Field(default="0.0.0.0", description="Server host", exclude=True)
    port: int = Field(default=8000, description="Server port", exclude=True)
    workers: int = Field(default=1, description="Number of workers", exclude=True)
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore",  # This allows extra fields without raising errors
        "str_strip_whitespace": True,
        "validate_assignment": True
    }

# Create settings instance
settings = Settings()