from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.config.database import get_db
from src.schemas import PermissionResponse, PermissionCreate, PermissionUpdate, MessageResponse
from src.service import PermissionService
from src.models import User, Permission
from src.core import get_current_user, has_permission
from typing import List
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class BulkDeleteRequest(BaseModel):
    permission_ids: list[int]

@router.get("/", response_model=List[PermissionResponse])
async def get_permissions(
    skip: int = 0,
    limit: int = 100,
    search: str = None,
    category: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission("permission", "read"))
):
    """Get all permissions with optional filters (Requires permission:read permission)"""
    try:
        permissions = PermissionService.get_all_permissions(
            db, 
            skip=skip, 
            limit=limit, 
            search=search, 
            category=category
        )
        return [PermissionResponse.from_orm(permission) for permission in permissions]
    except Exception as e:
        logger.error(f"Error getting permissions: {e}")
        raise HTTPException(status_code=500, detail="Unable to retrieve permissions at this time")

@router.get("/categories", response_model=List[str])
async def get_permission_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission("permission", "read"))
):
    """Get all unique permission categories (Requires permission:read permission)"""
    try:
        categories = PermissionService.get_unique_categories(db)
        return sorted(categories)
    except Exception as e:
        logger.error(f"Error getting permission categories: {e}")
        raise HTTPException(status_code=500, detail="Unable to retrieve permission categories")

@router.get("/count", response_model=int)
async def get_permissions_count(
    search: str = None,
    category: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission("permission", "read"))
):
    """Get total count of permissions with optional filters (Requires permission:read permission)"""
    try:
        count = PermissionService.get_permission_count(db, search=search, category=category)
        return count
    except Exception as e:
        logger.error(f"Error getting permissions count: {e}")
        raise HTTPException(status_code=500, detail="Unable to retrieve permissions count")

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

@router.put("/get-one/{permission_id}", response_model=PermissionResponse)
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
        if "already exists" in str(e).lower():
            raise HTTPException(status_code=400, detail="Permission name already exists")
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

@router.post("/bulk-delete", response_model=MessageResponse)
async def bulk_delete_permissions(
    request: BulkDeleteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission("permission", "delete"))
):
    """Bulk delete permissions (Requires permission:delete permission)"""
    try:
        logger.info(f"Bulk delete request: {request.permission_ids}")

        if not request.permission_ids:
            raise HTTPException(status_code=400, detail="No permission IDs provided")

        # Check if permissions exist before attempting to delete
        existing_permissions = db.query(Permission).filter(Permission.id.in_(request.permission_ids)).all()
        existing_ids = [permission.id for permission in existing_permissions]
        logger.info(f"Existing permission IDs found: {existing_ids}")

        if not existing_ids:
            raise HTTPException(status_code=404, detail="No permissions found with the provided IDs")

        # Perform bulk delete
        deleted_count = PermissionService.bulk_delete_permissions(db, existing_ids)
        logger.info(f"Deleted count: {deleted_count}")

        if deleted_count == 0:
            raise HTTPException(status_code=500, detail="Failed to delete permissions")

        return MessageResponse(
            message=f"{deleted_count} permission(s) deleted successfully",
            success=True
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error bulk deleting permissions: {e}")
        raise HTTPException(status_code=500, detail="Unable to bulk delete permissions")

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