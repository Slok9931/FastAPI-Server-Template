# Main package initialization - import all major components
from src import models, schemas, service, api
from src.config.database import get_db
from src.core.permissions import get_current_user, has_permission

# Export main components
__all__ = [
    "models",
    "schemas", 
    "service",
    "api",
    "get_db",
    "get_current_user",
    "has_permission"
]