from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from src.config.database import get_db
from src.schemas.user import UserResponse, UserUpdate, UserCreate
from src.models.user import User
from src.core.permissions import get_current_user, RoleChecker
from src.service.user_service import UserService

router = APIRouter()

@router.post("/", response_model=UserResponse)
def create_user(
    user: UserCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """Create a new user (Admin only)"""
    if not RoleChecker.has_permission(current_user, "create_user"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return UserService.create_user(db, user)

@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all users with pagination"""
    if not RoleChecker.has_permission(current_user, "get_users"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return UserService.get_all_users(db, skip=skip, limit=limit)

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific user"""
    if not RoleChecker.has_permission(current_user, "get_user"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Additional check: regular users can only view their own profile
    if not RoleChecker.has_any_role(current_user, ["admin", "manager"]) and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="You can only view your own profile")
    
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update user information"""
    if not RoleChecker.has_permission(current_user, "update_user"):
        # Check if user is updating their own profile
        if current_user.id == user_id and RoleChecker.has_permission(current_user, "update_own_profile"):
            # Allow user to update their own profile (but limit what they can update)
            if user_update.role_ids is not None:
                raise HTTPException(status_code=403, detail="You cannot change your own roles")
        else:
            raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Additional check: regular users can only update their own profile
    if not RoleChecker.has_any_role(current_user, ["admin", "manager"]) and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="You can only update your own profile")
    
    return UserService.update_user(db, user_id, user_update)

@router.post("/{user_id}/roles/{role_id}", response_model=UserResponse)
def add_role_to_user(
    user_id: int,
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a role to user (Admin only)"""
    if not RoleChecker.has_permission(current_user, "manage_roles"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return UserService.add_role_to_user(db, user_id, role_id)

@router.delete("/{user_id}/roles/{role_id}", response_model=UserResponse)
def remove_role_from_user(
    user_id: int,
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove a role from user (Admin only)"""
    if not RoleChecker.has_permission(current_user, "manage_roles"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return UserService.remove_role_from_user(db, user_id, role_id)

@router.delete("/{user_id}")
def delete_user(
    user_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """Delete a user (Admin only)"""
    if not RoleChecker.has_permission(current_user, "delete_user"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    UserService.delete_user(db, user_id)
    return {"message": "User deleted successfully"}

@router.get("/{user_id}/roles")
def get_user_roles(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's roles"""
    if not RoleChecker.has_permission(current_user, "get_user"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Additional check: regular users can only view their own roles
    if not RoleChecker.has_any_role(current_user, ["admin", "manager"]) and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="You can only view your own roles")
    
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"user_id": user_id, "roles": user.roles}

@router.post("/{user_id}/deactivate", response_model=UserResponse)
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Deactivate user account (Admin only)"""
    if not RoleChecker.has_permission(current_user, "update_user"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return UserService.deactivate_user(db, user_id)

@router.post("/{user_id}/activate", response_model=UserResponse)
def activate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Activate user account (Admin only)"""
    if not RoleChecker.has_permission(current_user, "update_user"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return UserService.activate_user(db, user_id)