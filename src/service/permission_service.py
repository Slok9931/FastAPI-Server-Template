from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List, Optional
from src.models.permission import Permission
from src.schemas.permission import PermissionCreate, PermissionUpdate

class PermissionService:
    
    @staticmethod
    def get_permission_by_id(db: Session, permission_id: int) -> Optional[Permission]:
        """Get permission by ID"""
        return db.query(Permission).filter(Permission.id == permission_id).first()
    
    @staticmethod
    def get_permission_by_name(db: Session, name: str) -> Optional[Permission]:
        """Get permission by name"""
        return db.query(Permission).filter(Permission.name == name).first()
    
    @staticmethod
    def get_all_permissions(db: Session, skip: int = 0, limit: int = 100, category: Optional[str] = None) -> List[Permission]:
        """Get all permissions with pagination and optional category filter"""
        query = db.query(Permission)
        
        if category:
            query = query.filter(Permission.category == category)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def create_permission(db: Session, permission: PermissionCreate) -> Permission:
        """Create a new permission"""
        # Check if permission name already exists
        existing_permission = PermissionService.get_permission_by_name(db, permission.name)
        if existing_permission:
            raise HTTPException(status_code=400, detail="Permission name already exists")
        
        db_permission = Permission(
            name=permission.name,
            description=permission.description,
            category=permission.category
        )
        
        db.add(db_permission)
        db.commit()
        db.refresh(db_permission)
        return db_permission
    
    @staticmethod
    def update_permission(db: Session, permission_id: int, permission_update: PermissionUpdate) -> Permission:
        """Update permission information"""
        db_permission = PermissionService.get_permission_by_id(db, permission_id)
        if not db_permission:
            raise HTTPException(status_code=404, detail="Permission not found")
        
        # Check if new name is already taken (if updating name)
        if permission_update.name and permission_update.name != db_permission.name:
            existing_permission = PermissionService.get_permission_by_name(db, permission_update.name)
            if existing_permission:
                raise HTTPException(status_code=400, detail="Permission name already exists")
        
        # Update permission fields
        update_data = permission_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_permission, field, value)
        
        db.commit()
        db.refresh(db_permission)
        return db_permission
    
    @staticmethod
    def delete_permission(db: Session, permission_id: int) -> bool:
        """Delete a permission"""
        db_permission = PermissionService.get_permission_by_id(db, permission_id)
        if not db_permission:
            raise HTTPException(status_code=404, detail="Permission not found")
        
        # Check if permission is being used by any roles
        if db_permission.roles:
            raise HTTPException(
                status_code=400, 
                detail="Cannot delete permission that is assigned to roles"
            )
        
        db.delete(db_permission)
        db.commit()
        return True
    
    @staticmethod
    def get_permission_categories(db: Session) -> List[str]:
        """Get all unique permission categories"""
        categories = db.query(Permission.category).distinct().filter(Permission.category.isnot(None)).all()
        return [cat[0] for cat in categories if cat[0]]