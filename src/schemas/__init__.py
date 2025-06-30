"""
Schema module initialization and model resolution.
This file resolves forward references to avoid circular imports.
"""

# Import all schema classes for easy access
from src.schemas.user import (
    UserBase, UserCreate, UserUpdate, UserLogin, 
    UserResponse, UserResponseSimple, UserInDB,
    Token, TokenData, RefreshTokenRequest, 
    PasswordChangeRequest, MessageResponse
)

from src.schemas.role import (
    RoleBase, RoleCreate, RoleUpdate, RoleResponse, RoleSimple
)

from src.schemas.permission import (
    PermissionBase, PermissionCreate, PermissionUpdate, PermissionResponse
)

def rebuild_models():
    """Rebuild all models to resolve forward references."""
    try:
        # Rebuild models that have forward references
        UserResponse.model_rebuild()
        RoleResponse.model_rebuild()
        print("✅ Schema models rebuilt successfully")
    except Exception as e:
        print(f"❌ Error rebuilding models: {e}")
        raise

# Export all schemas
__all__ = [
    # User schemas
    "UserBase", "UserCreate", "UserUpdate", "UserLogin",
    "UserResponse", "UserResponseSimple", "UserInDB",
    "Token", "TokenData", "RefreshTokenRequest",
    "PasswordChangeRequest", "MessageResponse",
    
    # Role schemas
    "RoleBase", "RoleCreate", "RoleUpdate", "RoleResponse", "RoleSimple",
    
    # Permission schemas
    "PermissionBase", "PermissionCreate", "PermissionUpdate", "PermissionResponse"
]

# Automatically rebuild models when this module is imported
rebuild_models()