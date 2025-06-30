from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from src.config.database import get_db
from src.schemas.user import UserCreate, UserResponse, UserLogin, Token
from src.service.auth_service import AuthService
from src.core.permissions import get_current_user
from src.models.user import User
from src.middleware.rate_limiting import endpoint_rate_limit

router = APIRouter()

@router.post("/register", response_model=UserResponse)
@endpoint_rate_limit(max_requests=3, window_seconds=3600)  # Extra protection
async def register(request: Request, user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    return AuthService.register_user(db, user)

@router.post("/login", response_model=Token)
async def login(request: Request, user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user and return access token"""
    return AuthService.authenticate_and_create_token(db, user_credentials)

@router.post("/refresh", response_model=Token)
async def refresh_token(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Refresh access token"""
    return AuthService.refresh_token(db, current_user)

@router.post("/change-password")
async def change_password(
    old_password: str,
    new_password: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user password"""
    AuthService.change_password(db, current_user.id, old_password, new_password)
    return {"message": "Password changed successfully"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """Get current user's profile"""
    return current_user

@router.get("/permissions")
async def get_user_permissions(
    current_user: User = Depends(get_current_user)
):
    """Get current user's permissions"""
    from src.core.permissions import RoleChecker
    
    # Define all possible permissions
    all_permissions = [
        "create_user", "get_users", "get_user", "update_user", "delete_user",
        "manage_roles", "view_roles", "update_own_profile", "moderate_content", "view_content"
    ]
    
    user_permissions = []
    for permission in all_permissions:
        if RoleChecker.has_permission(current_user, permission):
            user_permissions.append(permission)
    
    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "roles": current_user.get_role_names(),
        "permissions": user_permissions
    }