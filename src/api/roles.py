from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.config.database import get_db
from src.schemas.role import RoleResponse, RoleCreate, RoleUpdate
from src.schemas.user import MessageResponse
from src.service.role_service import RoleService
from src.models.user import User
from src.core.permissions import get_current_user, AdminRequired
from typing import List
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", response_model=List[RoleResponse])
async def get_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all roles"""
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
    current_user: User = Depends(AdminRequired())
):
    """Create new role (Admin only)"""
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
    current_user: User = Depends(get_current_user)
):
    """Get role by ID"""
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
    current_user: User = Depends(AdminRequired())
):
    """Update role (Admin only)"""
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
    current_user: User = Depends(AdminRequired())
):
    """Delete role (Admin only)"""
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
    current_user: User = Depends(AdminRequired())
):
    """Add permission to role (Admin only)"""
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
    current_user: User = Depends(AdminRequired())
):
    """Remove permission from role (Admin only)"""
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