from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.config.database import get_db
from src.schemas import RoleResponse, RoleCreate, RoleUpdate, MessageResponse
from src.service import RoleService
from src.models import User
from src.core import has_permission
from typing import List
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", response_model=List[RoleResponse])
async def get_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission("role", "read"))
):
    """Get all roles (Requires role:read permission)"""
    try:
        roles = RoleService.get_all_roles(db)
        return [RoleResponse.from_orm(role) for role in roles]
    except Exception as e:
        logger.error(f"Error getting roles: {e}")
        raise HTTPException(status_code=500, detail="Failed to get roles")

@router.post("/", response_model=RoleResponse)
async def create_role(
    role_data: RoleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission("role", "create"))
):
    """Create new role (Requires role:create permission)"""
    try:
        new_role = RoleService.create_role(db, role_data)
        return RoleResponse.from_orm(new_role)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating role: {e}")
        raise HTTPException(status_code=500, detail="Failed to create role")

@router.get("/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission("role", "read"))
):
    """Get role by ID (Requires role:read permission)"""
    try:
        role = RoleService.get_role_by_id(db, role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        return RoleResponse.from_orm(role)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting role: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve role")

@router.put("/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: int,
    role_update: RoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission("role", "update"))
):
    """Update role (Requires role:update permission)"""
    try:
        updated_role = RoleService.update_role(db, role_id, role_update)
        if not updated_role:
            raise HTTPException(status_code=404, detail="Role not found")
        return RoleResponse.from_orm(updated_role)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating role: {e}")
        raise HTTPException(status_code=500, detail="Failed to update role")

@router.delete("/{role_id}", response_model=MessageResponse)
async def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission("role", "delete"))
):
    """Delete role (Requires role:delete permission)"""
    try:
        success = RoleService.delete_role(db, role_id)
        if not success:
            raise HTTPException(status_code=404, detail="Role not found")
        return MessageResponse(
            message=f"Role {role_id} deleted successfully",
            success=True
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting role: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete role")

@router.post("/{role_id}/permissions/{permission_id}", response_model=MessageResponse)
async def add_permission_to_role(
    role_id: int,
    permission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission("role", "update"))
):
    """Add permission to role (Requires role:update permission)"""
    try:
        success = RoleService.add_permission_to_role(db, role_id, permission_id)
        if not success:
            raise HTTPException(status_code=404, detail="Role or permission not found")
        return MessageResponse(
            message=f"Permission {permission_id} added to role {role_id}",
            success=True
        )
    except Exception as e:
        logger.error(f"Error adding permission to role: {e}")
        raise HTTPException(status_code=500, detail="Failed to add permission to role")

@router.delete("/{role_id}/permissions/{permission_id}", response_model=MessageResponse)
async def remove_permission_from_role(
    role_id: int,
    permission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission("role", "update"))
):
    """Remove permission from role (Requires role:update permission)"""
    try:
        success = RoleService.remove_permission_from_role(db, role_id, permission_id)
        if not success:
            raise HTTPException(status_code=404, detail="Role or permission not found")
        return MessageResponse(
            message=f"Permission {permission_id} removed from role {role_id}",
            success=True
        )
    except Exception as e:
        logger.error(f"Error removing permission from role: {e}")
        raise HTTPException(status_code=500, detail="Failed to remove permission from role")