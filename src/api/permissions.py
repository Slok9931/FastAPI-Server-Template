from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.config.database import get_db
from src.schemas.permission import PermissionResponse, PermissionCreate, PermissionUpdate
from src.schemas.user import MessageResponse
from src.service.permission_service import PermissionService
from src.models.user import User
from src.core.permissions import get_current_user, has_permission
from typing import List
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", response_model=List[PermissionResponse])
async def get_permissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission("permission", "read"))
):
    """Get all permissions (Requires permission:read permission)"""
    try:
        permissions = PermissionService.get_all_permissions(db)
        return [PermissionResponse.from_orm(permission) for permission in permissions]
    except Exception as e:
        logger.error(f"Error getting permissions: {e}")
        raise HTTPException(status_code=500, detail="Unable to retrieve permissions at this time")

@router.post("/", response_model=PermissionResponse)
async def create_permission(
    permission_data: PermissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission("permission", "create"))
):
    """Create new permission (Requires permission:create permission)"""
    try:
        new_permission = PermissionService.create_permission(db, permission_data)
        return PermissionResponse.from_orm(new_permission)
    except ValueError as e:
        if "already exists" in str(e).lower():
            raise HTTPException(status_code=400, detail="Permission name already exists")
        raise HTTPException(status_code=400, detail="Invalid permission information provided")
    except Exception as e:
        logger.error(f"Error creating permission: {e}")
        raise HTTPException(status_code=500, detail="Unable to create permission")

@router.get("/get-one/{permission_id}", response_model=PermissionResponse)
async def get_permission(
    permission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission("permission", "read"))
):
    """Get permission by ID (Requires permission:read permission)"""
    try:
        permission = PermissionService.get_permission_by_id(db, permission_id)
        if not permission:
            raise HTTPException(status_code=404, detail="Permission not found")
        return PermissionResponse.from_orm(permission)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting permission: {e}")
        raise HTTPException(status_code=500, detail="Unable to retrieve permission information")

@router.put("/{permission_id}", response_model=PermissionResponse)
async def update_permission(
    permission_id: int,
    permission_update: PermissionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission("permission", "update"))
):
    """Update permission (Requires permission:update permission)"""
    try:
        updated_permission = PermissionService.update_permission(db, permission_id, permission_update)
        if not updated_permission:
            raise HTTPException(status_code=404, detail="Permission not found")
        return PermissionResponse.from_orm(updated_permission)
    except ValueError as e:
        if "cannot be modified" in str(e).lower():
            raise HTTPException(status_code=400, detail="System permissions cannot be modified")
        raise HTTPException(status_code=400, detail="Invalid permission information provided")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating permission: {e}")
        raise HTTPException(status_code=500, detail="Unable to update permission")

@router.delete("/{permission_id}", response_model=MessageResponse)
async def delete_permission(
    permission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission("permission", "delete"))
):
    """Delete permission (Requires permission:delete permission)"""
    try:
        success = PermissionService.delete_permission(db, permission_id)
        if not success:
            raise HTTPException(status_code=404, detail="Permission not found")
        return MessageResponse(
            message="Permission deleted successfully",
            success=True
        )
    except ValueError as e:
        if "cannot be deleted" in str(e).lower():
            raise HTTPException(status_code=400, detail="System permissions cannot be deleted")
        if "still assigned" in str(e).lower():
            raise HTTPException(status_code=400, detail="Cannot delete permission that is assigned to roles")
        raise HTTPException(status_code=400, detail="Permission cannot be deleted")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting permission: {e}")
        raise HTTPException(status_code=500, detail="Unable to delete permission")

@router.get("/category/{category}", response_model=List[PermissionResponse])
async def get_permissions_by_category(
    category: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission("permission", "read"))
):
    """Get permissions by category (Requires permission:read permission)"""
    try:
        permissions = PermissionService.get_permissions_by_category(db, category)
        return [PermissionResponse.from_orm(permission) for permission in permissions]
    except Exception as e:
        logger.error(f"Error getting permissions by category: {e}")
        raise HTTPException(status_code=500, detail="Unable to retrieve permissions for this category")

@router.get("/my-permissions", response_model=List[str])
async def get_my_permissions(
    current_user: User = Depends(get_current_user)
):
    """Get current user's permissions (No special permission required)"""
    try:
        permissions = current_user.get_permissions()
        return sorted(list(permissions))
    except Exception as e:
        logger.error(f"Error getting user permissions: {e}")
        raise HTTPException(status_code=500, detail="Unable to retrieve your permissions")