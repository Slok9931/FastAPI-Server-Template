from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.config.database import get_db
from src.schemas.user import UserResponse, UserUpdate, UserCreate, MessageResponse
from src.service.user_service import UserService
from src.models.user import User
from src.core.permissions import get_current_user, AdminRequired
from typing import List
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(AdminRequired())
):
    """Get all users (Admin only)"""
    try:
        users = UserService.get_all_users(db, skip=skip, limit=limit)
        return [UserResponse.from_orm(user) for user in users]
    except Exception as e:
        logger.error(f"Error getting users: {e}")
        raise HTTPException(status_code=500, detail="Failed to get users")

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(AdminRequired())
):
    """Get user by ID (Admin only)"""
    try:
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return UserResponse.from_orm(user)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user")

@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(AdminRequired())
):
    """Create new user (Admin only)"""
    try:
        new_user = UserService.create_user(db, user_data)
        return UserResponse.from_orm(new_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail="Failed to create user")

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(AdminRequired())
):
    """Update user (Admin only)"""
    try:
        updated_user = UserService.update_user(db, user_id, user_update)
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")
        return UserResponse.from_orm(updated_user)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user: {e}")
        raise HTTPException(status_code=500, detail="Failed to update user")

@router.delete("/{user_id}", response_model=MessageResponse)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(AdminRequired())
):
    """Delete user (Admin only)"""
    try:
        if user_id == current_user.id:
            raise HTTPException(status_code=400, detail="Cannot delete yourself")
        
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
        raise HTTPException(status_code=500, detail="Failed to delete user")

@router.post("/{user_id}/roles/{role_id}", response_model=MessageResponse)
async def assign_role_to_user(
    user_id: int,
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(AdminRequired())
):
    """Assign role to user (Admin only)"""
    try:
        success = UserService.assign_role_to_user(db, user_id, role_id)
        if not success:
            raise HTTPException(status_code=404, detail="User or role not found")
        return MessageResponse(
            message=f"Role {role_id} assigned to user {user_id}",
            success=True
        )
    except Exception as e:
        logger.error(f"Error assigning role to user: {e}")
        raise HTTPException(status_code=500, detail="Failed to assign role to user")

@router.delete("/{user_id}/roles/{role_id}", response_model=MessageResponse)
async def remove_role_from_user(
    user_id: int,
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(AdminRequired())
):
    """Remove role from user (Admin only)"""
    try:
        success = UserService.remove_role_from_user(db, user_id, role_id)
        if not success:
            raise HTTPException(status_code=404, detail="User or role not found")
        return MessageResponse(
            message=f"Role {role_id} removed from user {user_id}",
            success=True
        )
    except Exception as e:
        logger.error(f"Error removing role from user: {e}")
        raise HTTPException(status_code=500, detail="Failed to remove role from user")