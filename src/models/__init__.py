# Import all models to ensure they are registered with SQLAlchemy
from src.models.associations import user_roles, role_permissions
from src.models.user import User
from src.models.role import Role
from src.models.permission import Permission

# Export all models
__all__ = [
    "User",
    "Role", 
    "Permission",
    "user_roles",
    "role_permissions"
]