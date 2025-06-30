from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from src.models.permission import Permission
from src.schemas.permission import PermissionCreate, PermissionResponse, PermissionUpdate
from src.config.database import get_db
from src.core.permissions import get_current_user, RoleChecker
from src.models.user import User
from src.service.permission_service import PermissionService

router = APIRouter()

@router.post("/", response_model=PermissionResponse)
def create_permission(
    permission: PermissionCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new permission (Super Admin only)"""
    if not current_user.has_permission("manage_permissions"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return PermissionService.create_permission(db, permission)

@router.get("/", response_model=List[PermissionResponse])
def get_permissions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all permissions with pagination and optional category filter"""
    if not current_user.has_permission("view_permissions"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return PermissionService.get_all_permissions(db, skip=skip, limit=limit, category=category)

@router.get("/categories")
def get_permission_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all permission categories"""
    if not current_user.has_permission("view_permissions"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    categories = PermissionService.get_permission_categories(db)
    return {"categories": categories}

@router.get("/{permission_id}", response_model=PermissionResponse)
def get_permission(
    permission_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific permission"""
    if not current_user.has_permission("view_permissions"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    permission = PermissionService.get_permission_by_id(db, permission_id)
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    return permission

@router.put("/{permission_id}", response_model=PermissionResponse)
def update_permission(
    permission_id: int, 
    permission_update: PermissionUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update permission information (Super Admin only)"""
    if not current_user.has_permission("manage_permissions"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return PermissionService.update_permission(db, permission_id, permission_update)

@router.delete("/{permission_id}")
def delete_permission(
    permission_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a permission (Super Admin only)"""
    if not current_user.has_permission("manage_permissions"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    PermissionService.delete_permission(db, permission_id)
    return {"message": "Permission deleted successfully"}