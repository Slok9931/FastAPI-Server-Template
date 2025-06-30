from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.config.database import get_db
from src.schemas.permission import PermissionResponse, PermissionCreate, PermissionUpdate
from src.schemas.user import MessageResponse
from src.service.permission_service import PermissionService
from src.models.user import User
from src.core.permissions import get_current_user, AdminRequired
from typing import List
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", response_model=List[PermissionResponse])
async def get_permissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all permissions"""
    try:
        permissions = PermissionService.get_all_permissions(db)
        return [PermissionResponse.from_orm(permission) for permission in permissions]
    except Exception as e:
        logger.error(f"Error getting permissions: {e}")
        raise HTTPException(status_code=500, detail="Failed to get permissions")

@router.post("/", response_model=PermissionResponse)
async def create_permission(
    permission_data: PermissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(AdminRequired())
):
    """Create new permission (Admin only)"""
    try:
        new_permission = PermissionService.create_permission(db, permission_data)
        return PermissionResponse.from_orm(new_permission)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating permission: {e}")
        raise HTTPException(status_code=500, detail="Failed to create permission")

@router.get("/{permission_id}", response_model=PermissionResponse)
async def get_permission(
    permission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get permission by ID"""
    try:
        permission = PermissionService.get_permission_by_id(db, permission_id)
        if not permission:
            raise HTTPException(status_code=404, detail="Permission not found")
        return PermissionResponse.from_orm(permission)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting permission: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve permission")

@router.put("/{permission_id}", response_model=PermissionResponse)
async def update_permission(
    permission_id: int,
    permission_update: PermissionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(AdminRequired())
):
    """Update permission (Admin only)"""
    try:
        updated_permission = PermissionService.update_permission(db, permission_id, permission_update)
        if not updated_permission:
            raise HTTPException(status_code=404, detail="Permission not found")
        return PermissionResponse.from_orm(updated_permission)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating permission: {e}")
        raise HTTPException(status_code=500, detail="Failed to update permission")

@router.delete("/{permission_id}", response_model=MessageResponse)
async def delete_permission(
    permission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(AdminRequired())
):
    """Delete permission (Admin only)"""
    try:
        success = PermissionService.delete_permission(db, permission_id)
        if not success:
            raise HTTPException(status_code=404, detail="Permission not found")
        return MessageResponse(
            message=f"Permission {permission_id} deleted successfully",
            success=True
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting permission: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete permission")

@router.get("/category/{category}", response_model=List[PermissionResponse])
async def get_permissions_by_category(
    category: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get permissions by category"""
    try:
        permissions = PermissionService.get_permissions_by_category(db, category)
        return [PermissionResponse.from_orm(permission) for permission in permissions]
    except Exception as e:
        logger.error(f"Error getting permissions by category: {e}")
        raise HTTPException(status_code=500, detail="Failed to get permissions by category")