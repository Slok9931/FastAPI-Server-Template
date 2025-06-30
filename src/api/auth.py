from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from src.config.database import get_db
from src.schemas.user import (
    UserCreate, UserResponse, UserLogin, Token, 
    MessageResponse, RefreshTokenRequest, PasswordChangeRequest,
    UserResponseSimple, UserUpdate
)
from src.service.auth_service import AuthService
from src.service.user_service import UserService
from src.models.user import User
from src.config.settings import settings
from src.core.security import create_access_token, get_password_hash, verify_password
from src.core.permissions import get_current_user
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        new_user = AuthService.register_user(db, user)
        return UserResponse.from_orm(new_user)
    except ValueError as e:
        logger.warning(f"Registration failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")

@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user and return access token"""
    try:
        logger.info(f"Login attempt for user: {user_credentials.username}")
        
        # Authenticate user
        user = AuthService.authenticate_user(db, user_credentials.username, user_credentials.password)
        if not user:
            logger.warning(f"Authentication failed for user: {user_credentials.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.info(f"User authenticated successfully: {user.username}")
        
        # Create simple access token without refresh token for now
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": user.username, "type": "access"},
            expires_delta=access_token_expires
        )
        
        response = {
            "access_token": access_token,
            "refresh_token": None,  # Set to None for now
            "token_type": "bearer",
            "expires_in": settings.access_token_expire_minutes * 60
        }
        
        logger.info(f"Login successful for user: {user.username}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error for user {user_credentials.username}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    try:
        return UserResponse.from_orm(current_user)
    except Exception as e:
        logger.error(f"Error getting current user info: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user information")

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user information"""
    try:
        # Don't allow updating roles through this endpoint
        if hasattr(user_update, 'role_ids'):
            user_update.role_ids = None
        
        updated_user = UserService.update_user(db, current_user.id, user_update)
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        logger.info(f"User updated their profile: {current_user.username}")
        return UserResponse.from_orm(updated_user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to update profile")

@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    password_data: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change current user's password"""
    try:
        # Verify current password
        if not verify_password(password_data.current_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Update password
        current_user.hashed_password = get_password_hash(password_data.new_password)
        db.commit()
        
        logger.info(f"Password changed for user: {current_user.username}")
        return MessageResponse(
            message="Password changed successfully",
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error changing password: {e}")
        raise HTTPException(status_code=500, detail="Failed to change password")

@router.get("/profile", response_model=UserResponseSimple)
async def get_user_profile(current_user: User = Depends(get_current_user)):
    """Get simplified user profile"""
    try:
        return UserResponseSimple.from_orm(current_user)
    except Exception as e:
        logger.error(f"Error getting user profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user profile")

@router.get("/permissions")
async def get_current_user_permissions(current_user: User = Depends(get_current_user)):
    """Get current user's permissions"""
    try:
        permissions = set()
        roles = []
        
        for role in current_user.roles:
            roles.append({
                "id": role.id,
                "name": role.name,
                "description": role.description
            })
            for permission in role.permissions:
                permissions.add(permission.name)
        
        return {
            "user_id": current_user.id,
            "username": current_user.username,
            "roles": roles,
            "permissions": sorted(list(permissions))
        }
        
    except Exception as e:
        logger.error(f"Error getting user permissions: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user permissions")

@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token"""
    try:
        token_data = AuthService.refresh_access_token(refresh_data.refresh_token)
        return Token(**token_data)
    except ValueError as e:
        logger.warning(f"Token refresh failed: {e}")
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(status_code=500, detail="Token refresh failed")

@router.post("/logout", response_model=MessageResponse)
async def logout(current_user: User = Depends(get_current_user)):
    """Logout user (invalidate tokens)"""
    try:
        # In a real implementation, you would add the token to a blacklist
        logger.info(f"User logged out: {current_user.username}")
        return MessageResponse(
            message="Successfully logged out",
            success=True
        )
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(status_code=500, detail="Logout failed")

@router.post("/verify-token")
async def verify_token_endpoint(current_user: User = Depends(get_current_user)):
    """Verify if current token is valid"""
    try:
        return {
            "valid": True,
            "user_id": current_user.id,
            "username": current_user.username,
            "is_active": current_user.is_active
        }
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")