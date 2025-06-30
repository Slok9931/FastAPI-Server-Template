from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from src.models.role import Role
from src.schemas.role import RoleCreate, RoleResponse, RoleUpdate, RoleResponseSimple
from src.config.database import get_db
from src.core.permissions import get_current_user
from src.models.user import User
from src.service.role_service import RoleService
from src.config.settings import settings

router = APIRouter()

@router.post("/", response_model=RoleResponse)
def create_role(
    role: RoleCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new role with minimal permissions (others added via API)"""
    if not current_user.has_permission("manage_roles"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return RoleService.create_role(db, role)

@router.post("/create-minimal", response_model=RoleResponse)
def create_minimal_role(
    role_name: str,
    description: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a role with only minimal permissions (get_user, update_own_profile, view_content)"""
    if not current_user.has_permission("manage_roles"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Prevent creating super admin role
    if role_name == settings.super_admin_role:
        raise HTTPException(status_code=400, detail="Cannot create super admin role through this endpoint")
    
    role = RoleService.create_role_if_not_exists(db, role_name, description)
    return role

@router.get("/", response_model=List[RoleResponseSimple])
def get_roles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all roles with pagination (without users details)"""
    if not current_user.has_permission("view_roles"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return RoleService.get_all_roles(db, skip=skip, limit=limit)

@router.get("/{role_id}", response_model=RoleResponse)
def get_role(
    role_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific role (with users details)"""
    if not current_user.has_permission("view_roles"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    role = RoleService.get_role_by_id(db, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role

@router.put("/{role_id}", response_model=RoleResponse)
def update_role(
    role_id: int, 
    role_update: RoleUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update role information"""
    if not current_user.has_permission("manage_roles"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return RoleService.update_role(db, role_id, role_update)

@router.delete("/{role_id}")
def delete_role(
    role_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a role"""
    if not current_user.has_permission("manage_roles"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    RoleService.delete_role(db, role_id)
    return {"message": "Role deleted successfully"}

# ========== PERMISSION MANAGEMENT ENDPOINTS ==========

@router.post("/{role_id}/permissions/{permission_id}", response_model=RoleResponse)
def add_permission_to_role(
    role_id: int,
    permission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a single permission to role"""
    if not current_user.has_permission("manage_roles"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return RoleService.add_permission_to_role(db, role_id, permission_id)

@router.delete("/{role_id}/permissions/{permission_id}", response_model=RoleResponse)
def remove_permission_from_role(
    role_id: int,
    permission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove a permission from role"""
    if not current_user.has_permission("manage_roles"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return RoleService.remove_permission_from_role(db, role_id, permission_id)

@router.post("/{role_id}/permissions/bulk", response_model=RoleResponse)
def add_multiple_permissions_to_role(
    role_id: int,
    permission_ids: List[int],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add multiple permissions to role at once"""
    if not current_user.has_permission("manage_roles"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return RoleService.bulk_add_permissions_to_role(db, role_id, permission_ids)

@router.put("/{role_id}/permissions", response_model=RoleResponse)
def set_role_permissions(
    role_id: int,
    permission_ids: List[int],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Set exact permissions for role (replaces all existing permissions except minimal ones)"""
    if not current_user.has_permission("manage_roles"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return RoleService.set_role_permissions(db, role_id, permission_ids)

@router.get("/{role_id}/permissions")
def get_role_permissions(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get role's permissions"""
    if not current_user.has_permission("view_roles"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    role = RoleService.get_role_by_id(db, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    return {
        "role_id": role_id, 
        "role_name": role.name,
        "permissions": role.permissions,
        "permissions_count": len(role.permissions)
    }

@router.get("/{role_id}/available-permissions")
def get_available_permissions_for_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get permissions that can be added to this role (not already assigned)"""
    if not current_user.has_permission("view_roles"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    role = RoleService.get_role_by_id(db, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    from src.models.permission import Permission
    all_permissions = db.query(Permission).all()
    role_permission_ids = [perm.id for perm in role.permissions]
    
    available_permissions = [
        perm for perm in all_permissions 
        if perm.id not in role_permission_ids
    ]
    
    return {
        "role_id": role_id,
        "role_name": role.name,
        "available_permissions": available_permissions,
        "available_count": len(available_permissions)
    }