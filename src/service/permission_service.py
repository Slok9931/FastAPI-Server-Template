from sqlalchemy.orm import Session
from src.models import Permission
from src.schemas import PermissionCreate, PermissionUpdate
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class PermissionService:
    
    @staticmethod
    def get_all_permissions(db: Session) -> List[Permission]:
        """Get all permissions"""
        try:
            return db.query(Permission).all()
        except Exception as e:
            logger.error(f"Error getting permissions: {e}")
            return []
    
    @staticmethod
    def get_permission_by_id(db: Session, permission_id: int) -> Optional[Permission]:
        """Get permission by ID"""
        try:
            return db.query(Permission).filter(Permission.id == permission_id).first()
        except Exception as e:
            logger.error(f"Error getting permission by ID: {e}")
            return None
    
    @staticmethod
    def get_permission_by_name(db: Session, permission_name: str) -> Optional[Permission]:
        """Get permission by name"""
        try:
            return db.query(Permission).filter(Permission.name == permission_name).first()
        except Exception as e:
            logger.error(f"Error getting permission by name: {e}")
            return None
    
    @staticmethod
    def get_permissions_by_category(db: Session, category: str) -> List[Permission]:
        """Get permissions by category"""
        try:
            return db.query(Permission).filter(Permission.category == category).all()
        except Exception as e:
            logger.error(f"Error getting permissions by category: {e}")
            return []
    
    @staticmethod
    def create_permission(db: Session, permission_data: PermissionCreate) -> Permission:
        """Create a new permission"""
        try:
            # Check if permission already exists
            existing_permission = db.query(Permission).filter(Permission.name == permission_data.name).first()
            if existing_permission:
                raise ValueError(f"Permission with name '{permission_data.name}' already exists")
            
            # Create permission
            db_permission = Permission(
                name=permission_data.name,
                description=permission_data.description,
                category=permission_data.category
            )
            
            db.add(db_permission)
            db.commit()
            db.refresh(db_permission)
            
            logger.info(f"Permission created: {db_permission.name}")
            return db_permission
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating permission: {e}")
            raise
    
    @staticmethod
    def update_permission(db: Session, permission_id: int, permission_update: PermissionUpdate) -> Optional[Permission]:
        """Update permission"""
        try:
            db_permission = db.query(Permission).filter(Permission.id == permission_id).first()
            if not db_permission:
                return None
            
            # Update fields
            if permission_update.name is not None:
                # Check if new name already exists
                existing_permission = db.query(Permission).filter(
                    Permission.name == permission_update.name,
                    Permission.id != permission_id
                ).first()
                if existing_permission:
                    raise ValueError(f"Permission with name '{permission_update.name}' already exists")
                db_permission.name = permission_update.name
            
            if permission_update.description is not None:
                db_permission.description = permission_update.description
            
            if permission_update.category is not None:
                db_permission.category = permission_update.category
            
            db.commit()
            db.refresh(db_permission)
            
            logger.info(f"Permission updated: {db_permission.name}")
            return db_permission
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating permission: {e}")
            raise
    
    @staticmethod
    def delete_permission(db: Session, permission_id: int) -> bool:
        """Delete permission"""
        try:
            db_permission = db.query(Permission).filter(Permission.id == permission_id).first()
            if not db_permission:
                return False
            
            # Check if permission is assigned to any roles
            if db_permission.roles:
                raise ValueError("Cannot delete permission that is assigned to roles")
            
            db.delete(db_permission)
            db.commit()
            
            logger.info(f"Permission deleted: {db_permission.name}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting permission: {e}")
            raise