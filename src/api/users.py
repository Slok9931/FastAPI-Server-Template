from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import logging
from src.config.database import get_db
from src.schemas import (
    UserResponse, UserCreate, UserUpdate, 
    MessageResponse
)
from src.models import User
from src.service import UserService
from src.core import get_current_user, has_permission

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission("user", "read"))
):
    """Get all users (Requires user:read permission)"""
    try:
        users = UserService.get_all_users(db, skip=skip, limit=limit)
        return [UserResponse.from_orm(user) for user in users]
    except Exception as e:
        logger.error(f"Error getting users: {e}")
        raise HTTPException(status_code=500, detail="Unable to retrieve users at this time")

@router.get("/get-one/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission("user", "read"))
):
    """Get user by ID (Requires user:read permission)"""
    try:
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return UserResponse.from_orm(user)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user: {e}")
        raise HTTPException(status_code=500, detail="Unable to retrieve user information")

@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission("user", "create"))
):
    """Create new user (Requires user:create permission)"""
    try:
        new_user = UserService.create_user(db, user_data)
        return UserResponse.from_orm(new_user)
    except ValueError as e:
        if "already exists" in str(e).lower():
            raise HTTPException(status_code=400, detail="Username or email already exists")
        raise HTTPException(status_code=400, detail="Invalid user information provided")
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail="Unable to create user account")

@router.put("/get-one/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission("user", "update"))
):
    """Update user (Requires user:update permission)"""
    try:
        updated_user = UserService.update_user(db, user_id, user_update)
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")
        return UserResponse.from_orm(updated_user)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user: {e}")
        raise HTTPException(status_code=500, detail="Unable to update user information")

@router.delete("/{user_id}", response_model=MessageResponse)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission("user", "delete"))
):
    """Delete user (Requires user:delete permission)"""
    try:
        if user_id == current_user.id:
            raise HTTPException(status_code=400, detail="You cannot delete your own account")
        
        success = UserService.delete_user(db, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="User not found")
        
        return MessageResponse(
            message="User deleted successfully",
            success=True
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        raise HTTPException(status_code=500, detail="Unable to delete user account")

@router.post("/{user_id}/roles/{role_id}", response_model=MessageResponse)
async def assign_role_to_user(
    user_id: int,
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission("user", "update"))
):
    """Assign role to user (Requires user:update permission)"""
    try:
        success = UserService.assign_role_to_user(db, user_id, role_id)
        if not success:
            raise HTTPException(status_code=404, detail="User or role not found")
        return MessageResponse(
            message="Role assigned to user successfully",
            success=True
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error assigning role to user: {e}")
        raise HTTPException(status_code=500, detail="Unable to assign role to user")

@router.delete("/{user_id}/roles/{role_id}", response_model=MessageResponse)
async def remove_role_from_user(
    user_id: int,
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission("user", "update"))
):
    """Remove role from user (Requires user:update permission)"""
    try:
        success = UserService.remove_role_from_user(db, user_id, role_id)
        if not success:
            raise HTTPException(status_code=404, detail="User or role not found")
        return MessageResponse(
            message="Role removed from user successfully",
            success=True
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing role from user: {e}")
        raise HTTPException(status_code=500, detail="Unable to remove role from user")

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """Get current user's profile (No special permission required)"""
    return UserResponse.from_orm(current_user)