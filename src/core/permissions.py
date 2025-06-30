from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from src.config.database import get_db
from src.models.user import User
from src.core.security import verify_token
from src.config.settings import settings
from typing import List
import logging

logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)

async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not credentials:
        raise credentials_exception
    
    token = credentials.credentials
    payload = verify_token(token, "access")
    if payload is None:
        logger.warning(f"Failed authentication attempt from {request.client.host}")
        raise credentials_exception
    
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None or not user.is_active:
        raise credentials_exception
    
    return user

class SecurityAudit:
    """Security audit logging"""
    
    @staticmethod
    def log_permission_check(user: User, permission: str, granted: bool, resource: str = None):
        logger.info(
            f"Permission check: user={user.username}, permission={permission}, "
            f"granted={granted}, resource={resource}"
        )
    
    @staticmethod
    def log_sensitive_operation(user: User, operation: str, target: str = None):
        logger.warning(
            f"Sensitive operation: user={user.username}, operation={operation}, "
            f"target={target}"
        )

class RoleChecker:
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)):
        user_roles = current_user.get_role_names()
        has_access = any(role in self.allowed_roles for role in user_roles)
        
        if not has_access:
            SecurityAudit.log_permission_check(
                current_user, f"role_check:{self.allowed_roles}", False
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted"
            )
        
        SecurityAudit.log_permission_check(
            current_user, f"role_check:{self.allowed_roles}", True
        )
        return current_user

    @staticmethod
    def has_permission(user: User, permission: str) -> bool:
        """Check if user has specific permission through their roles"""
        granted = user.has_permission(permission)
        SecurityAudit.log_permission_check(user, permission, granted)
        return granted

    @staticmethod
    def has_any_role(user: User, required_roles: List[str]) -> bool:
        """Check if user has any of the required roles"""
        user_roles = user.get_role_names()
        return any(role in required_roles for role in user_roles)

    @staticmethod
    def has_all_roles(user: User, required_roles: List[str]) -> bool:
        """Check if user has all of the required roles"""
        user_roles = user.get_role_names()
        return all(role in user_roles for role in required_roles)
    
    @staticmethod
    def is_super_admin(user: User) -> bool:
        """Check if user is super admin (only fixed role)"""
        return settings.fixed_system_role in user.get_role_names()
    
    @staticmethod
    def has_admin_role(user: User) -> bool:
        """Check if user has any admin role (dynamically determined)"""
        user_roles = user.get_role_names()
        admin_roles = settings.admin_roles
        return any(role in admin_roles for role in user_roles)

class PermissionChecker:
    def __init__(self, required_permission: str):
        self.required_permission = required_permission

    def __call__(self, current_user: User = Depends(get_current_user)):
        if not current_user.has_permission(self.required_permission):
            SecurityAudit.log_permission_check(
                current_user, self.required_permission, False
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{self.required_permission}' required"
            )
        
        SecurityAudit.log_permission_check(
            current_user, self.required_permission, True
        )
        return current_user

# Dynamic role checkers based on settings
class SuperAdminRequired:
    """Only super_admin can access (fixed role)"""
    def __call__(self, current_user: User = Depends(get_current_user)):
        if not RoleChecker.is_super_admin(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Super admin access required"
            )
        return current_user

class AdminRequired:
    """Any admin role can access (dynamic based on settings)"""
    def __call__(self, current_user: User = Depends(get_current_user)):
        if not RoleChecker.has_admin_role(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        return current_user