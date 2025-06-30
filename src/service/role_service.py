from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional, Dict
from src.models.role import Role
from src.models.permission import Permission
from src.schemas.role import RoleCreate, RoleUpdate
from src.config.settings import settings
from fastapi import HTTPException

class RoleService:
    
    @staticmethod
    def create_role_if_not_exists(db: Session, role_name: str, description: str = None, 
                                 permissions: List[Permission] = None) -> Role:
        """Create a role if it doesn't exist, with MINIMAL default permissions"""
        
        # Check if role already exists
        existing_role = db.query(Role).filter(Role.name == role_name).first()
        if existing_role:
            return existing_role
        
        # Auto-generate description if not provided
        if not description:
            description = f"{role_name.replace('_', ' ').title()} role"
        
        # Determine if it's a system role (only super_admin is truly system role)
        is_system_role = (role_name == settings.super_admin_role)
        
        # Create new role
        new_role = Role(
            name=role_name,
            description=description,
            is_system_role=is_system_role
        )
        
        # Assign permissions based on role type
        if permissions is None:
            if role_name == settings.super_admin_role:
                # Super admin gets ALL permissions
                permissions = db.query(Permission).all()
            else:
                # ALL OTHER ROLES get only basic permissions
                permissions = RoleService._get_minimal_permissions(db)
        
        new_role.permissions = permissions
        
        db.add(new_role)
        db.commit()
        db.refresh(new_role)
        
        return new_role
    
    @staticmethod
    def _get_minimal_permissions(db: Session) -> List[Permission]:
        """Get minimal permissions for new roles - only basic user permissions"""
        
        all_permissions = db.query(Permission).all()
        permissions_dict = {perm.name: perm for perm in all_permissions}
        
        # ONLY basic permissions for ALL new roles
        minimal_perms = [
            "get_user",           # View user details (themselves)
            "update_own_profile", # Update their own profile
            "view_content"        # Basic content viewing
        ]
        
        # Return only the permissions that exist in database
        assigned_permissions = [
            permissions_dict[perm] for perm in minimal_perms 
            if perm in permissions_dict
        ]
        
        return assigned_permissions
    
    @staticmethod
    def create_role(db: Session, role_data: RoleCreate) -> Role:
        """Create a new role with specified permissions (or minimal if none specified)"""
        
        # Check if role already exists
        existing_role = db.query(Role).filter(Role.name == role_data.name).first()
        if existing_role:
            raise HTTPException(status_code=400, detail="Role already exists")
        
        # Prevent creating another super_admin role
        if role_data.name == settings.super_admin_role:
            raise HTTPException(status_code=400, detail="Cannot create another super admin role")
        
        # Get permissions if specified, otherwise use minimal
        permissions = []
        if role_data.permission_ids:
            permissions = db.query(Permission).filter(
                Permission.id.in_(role_data.permission_ids)
            ).all()
            if len(permissions) != len(role_data.permission_ids):
                raise HTTPException(status_code=400, detail="One or more invalid permission IDs")
        else:
            # No permissions specified = minimal permissions
            permissions = RoleService._get_minimal_permissions(db)
        
        return RoleService.create_role_if_not_exists(
            db, role_data.name, role_data.description, permissions
        )
    
    @staticmethod
    def get_or_create_default_role(db: Session) -> Role:
        """Get or create the default user role with minimal permissions"""
        return RoleService.create_role_if_not_exists(
            db, settings.default_user_role, "Default user role"
        )
    
    @staticmethod
    def ensure_super_admin_exists(db: Session) -> Role:
        """Ensure super admin role exists with all permissions"""
        all_permissions = db.query(Permission).all()
        return RoleService.create_role_if_not_exists(
            db, settings.super_admin_role, "Super Administrator with all permissions", all_permissions
        )
    
    @staticmethod
    def add_permission_to_role(db: Session, role_id: int, permission_id: int) -> Role:
        """Add a permission to role"""
        db_role = RoleService.get_role_by_id(db, role_id)
        if not db_role:
            raise HTTPException(status_code=404, detail="Role not found")
        
        permission = db.query(Permission).filter(Permission.id == permission_id).first()
        if not permission:
            raise HTTPException(status_code=404, detail="Permission not found")
        
        if permission not in db_role.permissions:
            db_role.permissions.append(permission)
            db.commit()
            db.refresh(db_role)
        
        return db_role
    
    @staticmethod
    def remove_permission_from_role(db: Session, role_id: int, permission_id: int) -> Role:
        """Remove a permission from role"""
        db_role = RoleService.get_role_by_id(db, role_id)
        if not db_role:
            raise HTTPException(status_code=404, detail="Role not found")
        
        # Prevent removing basic permissions from non-admin roles
        if not db_role.is_system_role or db_role.name != settings.super_admin_role:
            permission = db.query(Permission).filter(Permission.id == permission_id).first()
            if permission and permission.name in ["get_user", "update_own_profile"]:
                raise HTTPException(
                    status_code=400, 
                    detail="Cannot remove basic user permissions from this role"
                )
        
        permission = db.query(Permission).filter(Permission.id == permission_id).first()
        if not permission:
            raise HTTPException(status_code=404, detail="Permission not found")
        
        if permission in db_role.permissions:
            db_role.permissions.remove(permission)
            db.commit()
            db.refresh(db_role)
        
        return db_role
    
    @staticmethod
    def bulk_add_permissions_to_role(db: Session, role_id: int, permission_ids: List[int]) -> Role:
        """Add multiple permissions to a role at once"""
        db_role = RoleService.get_role_by_id(db, role_id)
        if not db_role:
            raise HTTPException(status_code=404, detail="Role not found")
        
        permissions = db.query(Permission).filter(Permission.id.in_(permission_ids)).all()
        if len(permissions) != len(permission_ids):
            raise HTTPException(status_code=400, detail="One or more invalid permission IDs")
        
        # Add only new permissions
        for permission in permissions:
            if permission not in db_role.permissions:
                db_role.permissions.append(permission)
        
        db.commit()
        db.refresh(db_role)
        return db_role
    
    @staticmethod
    def set_role_permissions(db: Session, role_id: int, permission_ids: List[int]) -> Role:
        """Set exact permissions for a role (replaces all existing permissions)"""
        db_role = RoleService.get_role_by_id(db, role_id)
        if not db_role:
            raise HTTPException(status_code=404, detail="Role not found")
        
        # Prevent modifying super admin permissions through this method
        if db_role.name == settings.super_admin_role:
            raise HTTPException(status_code=400, detail="Cannot modify super admin permissions")
        
        permissions = db.query(Permission).filter(Permission.id.in_(permission_ids)).all()
        if len(permissions) != len(permission_ids):
            raise HTTPException(status_code=400, detail="One or more invalid permission IDs")
        
        # Ensure minimal permissions are always included for non-admin roles
        minimal_permissions = RoleService._get_minimal_permissions(db)
        minimal_permission_ids = [perm.id for perm in minimal_permissions]
        
        all_permissions = minimal_permissions.copy()
        for permission in permissions:
            if permission.id not in minimal_permission_ids:
                all_permissions.append(permission)
        
        db_role.permissions = all_permissions
        db.commit()
        db.refresh(db_role)
        return db_role
    
    @staticmethod
    def get_role_by_id(db: Session, role_id: int) -> Role:
        """Get role by ID"""
        return db.query(Role).filter(Role.id == role_id).first()
    
    @staticmethod
    def get_role_by_name(db: Session, role_name: str) -> Role:
        """Get role by name"""
        return db.query(Role).filter(Role.name == role_name).first()
    
    @staticmethod
    def get_all_roles(db: Session, skip: int = 0, limit: int = 100) -> List[Role]:
        """Get all roles with pagination"""
        return db.query(Role).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_role(db: Session, role_id: int, role_update: RoleUpdate) -> Role:
        """Update role information"""
        db_role = RoleService.get_role_by_id(db, role_id)
        if not db_role:
            raise HTTPException(status_code=404, detail="Role not found")
        
        # Check if it's a system role (prevent modification of critical fields)
        if db_role.is_system_role and role_update.name:
            raise HTTPException(status_code=400, detail="Cannot modify system role name")
        
        # Check if new name is already taken (if updating name)
        if role_update.name and role_update.name != db_role.name:
            existing_role = RoleService.get_role_by_name(db, role_update.name)
            if existing_role:
                raise HTTPException(status_code=400, detail="Role name already exists")
        
        # Update permissions if provided
        if role_update.permission_ids is not None:
            permissions = db.query(Permission).filter(Permission.id.in_(role_update.permission_ids)).all()
            if len(permissions) != len(role_update.permission_ids):
                raise HTTPException(status_code=400, detail="One or more invalid permission IDs")
            db_role.permissions = permissions
        
        # Update other role fields
        update_data = role_update.dict(exclude_unset=True, exclude={'permission_ids'})
        for field, value in update_data.items():
            setattr(db_role, field, value)
        
        db.commit()
        db.refresh(db_role)
        return db_role
    
    @staticmethod
    def delete_role(db: Session, role_id: int) -> bool:
        """Delete a role"""
        db_role = RoleService.get_role_by_id(db, role_id)
        if not db_role:
            raise HTTPException(status_code=404, detail="Role not found")
        
        # Prevent deletion of system roles
        if db_role.is_system_role:
            raise HTTPException(status_code=400, detail="Cannot delete system role")
        
        db.delete(db_role)
        db.commit()
        return True
    
    @staticmethod
    def get_users_by_role(db: Session, role_id: int):
        """Get all users with a specific role"""
        role = RoleService.get_role_by_id(db, role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        
        return role.users