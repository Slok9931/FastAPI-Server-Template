from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from src.config.database import get_db
from src.core.security import verify_token
from src.models.user import User
from src.service.user_service import UserService
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Security scheme for Bearer token
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    try:
        # Verify token
        token_data = verify_token(credentials.credentials)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get username from token
        username = token_data.get("sub")
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get user from database
        user = UserService.get_user_by_username(db, username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is disabled",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting current user: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )

def has_permission(resource: str, action: str):
    """
    Check if current user has permission for a specific resource and action.
    
    Args:
        resource (str): The resource name (e.g., 'user', 'role', 'permission')
        action (str): The action ('read', 'create', 'update', 'delete')
    
    Returns:
        User: The current user if they have permission
        
    Raises:
        HTTPException: If user doesn't have permission
    """
    def permission_dependency(current_user: User = Depends(get_current_user)):
        # Construct permission name
        permission_name = f"{resource}:{action}"
        
        # Check if user has the required permission
        if not current_user.has_permission(permission_name):
            logger.warning(
                f"Permission denied - User: {current_user.username}, "
                f"Required: {permission_name}, "
                f"User permissions: {list(current_user.get_permissions())}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission_name}' required for this action"
            )
        
        logger.info(f"Permission granted - User: {current_user.username}, Permission: {permission_name}")
        return current_user
    
    return permission_dependency

def require_permission(permission_name: str):
    """Legacy function - use has_permission instead"""
    def permission_dependency(current_user: User = Depends(get_current_user)):
        if not current_user.has_permission(permission_name):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission_name}' required"
            )
        return current_user
    return permission_dependency

def require_role(role_name: str):
    """Decorator to require specific role"""
    def role_dependency(current_user: User = Depends(get_current_user)):
        if not current_user.has_role(role_name):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{role_name}' required"
            )
        return current_user
    return role_dependency

class AdminRequired:
    """Legacy class - use has_permission instead"""
    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        if not (current_user.has_role("admin") or current_user.has_role("super_admin")):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin privileges required"
            )
        return current_user

class SuperAdminRequired:
    """Dependency class for super admin-only endpoints"""
    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        if not current_user.has_role("super_admin"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Super admin privileges required"
            )
        return current_user

def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current user if authenticated, otherwise return None"""
    if not credentials:
        return None
    
    try:
        return get_current_user(credentials, db)
    except HTTPException:
        return None