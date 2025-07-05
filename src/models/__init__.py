# Import all models to ensure they are registered with SQLAlchemy
from src.models.user import User
from src.models.role import Role
from src.models.permission import Permission
from src.models.module import Module
from src.models.route import Route

# Export all models
__all__ = [
    "User",
    "Role", 
    "Permission",
    "Module",
    "Route",
]