from sqlalchemy.orm import Session
from src.models.role import Role
from src.models.permission import Permission
from src.schemas.role import RoleCreate, RoleUpdate
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class RoleService:
    
    @staticmethod
    def get_all_roles(db: Session) -> List[Role]:
        """Get all roles"""
        try:
            return db.query(Role).all()
        except Exception as e:
            logger.error(f"Error getting roles: {e}")
            return []
    
    @staticmethod
    def get_role_by_id(db: Session, role_id: int) -> Optional[Role]:
        """Get role by ID"""
        try:
            return db.query(Role).filter(Role.id == role_id).first()
        except Exception as e:
            logger.error(f"Error getting role by ID: {e}")
            return None
    
    @staticmethod
    def get_role_by_name(db: Session, role_name: str) -> Optional[Role]:
        """Get role by name"""
        try:
            return db.query(Role).filter(Role.name == role_name).first()
        except Exception as e:
            logger.error(f"Error getting role by name: {e}")
            return None
    
    @staticmethod
    def create_role(db: Session, role_data: RoleCreate) -> Role:
        """Create a new role"""
        try:
            # Check if role already exists
            existing_role = db.query(Role).filter(Role.name == role_data.name).first()
            if existing_role:
                raise ValueError(f"Role with name '{role_data.name}' already exists")
            
            # Create role
            db_role = Role(
                name=role_data.name,
                description=role_data.description,
                is_system_role=False
            )
            
            # Assign permissions
            if role_data.permission_ids:
                permissions = db.query(Permission).filter(Permission.id.in_(role_data.permission_ids)).all()
                db_role.permissions = permissions
            
            db.add(db_role)
            db.commit()
            db.refresh(db_role)
            
            logger.info(f"Role created: {db_role.name}")
            return db_role
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating role: {e}")
            raise
    
    @staticmethod
    def update_role(db: Session, role_id: int, role_update: RoleUpdate) -> Optional[Role]:
        """Update role"""
        try:
            db_role = db.query(Role).filter(Role.id == role_id).first()
            if not db_role:
                return None
            
            # Don't allow updating system roles
            if db_role.is_system_role:
                raise ValueError("Cannot update system roles")
            
            # Update fields
            if role_update.name is not None:
                # Check if new name already exists
                existing_role = db.query(Role).filter(
                    Role.name == role_update.name,
                    Role.id != role_id
                ).first()
                if existing_role:
                    raise ValueError(f"Role with name '{role_update.name}' already exists")
                db_role.name = role_update.name
            
            if role_update.description is not None:
                db_role.description = role_update.description
            
            # Update permissions
            if role_update.permission_ids is not None:
                permissions = db.query(Permission).filter(Permission.id.in_(role_update.permission_ids)).all()
                db_role.permissions = permissions
            
            db.commit()
            db.refresh(db_role)
            
            logger.info(f"Role updated: {db_role.name}")
            return db_role
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating role: {e}")
            raise
    
    @staticmethod
    def delete_role(db: Session, role_id: int) -> bool:
        """Delete role"""
        try:
            db_role = db.query(Role).filter(Role.id == role_id).first()
            if not db_role:
                return False
            
            # Don't allow deleting system roles
            if db_role.is_system_role:
                raise ValueError("Cannot delete system roles")
            
            # Check if role is assigned to any users
            if db_role.users:
                raise ValueError("Cannot delete role that is assigned to users")
            
            db.delete(db_role)
            db.commit()
            
            logger.info(f"Role deleted: {db_role.name}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting role: {e}")
            raise
    
    @staticmethod
    def add_permission_to_role(db: Session, role_id: int, permission_id: int) -> bool:
        """Add permission to role"""
        try:
            role = db.query(Role).filter(Role.id == role_id).first()
            permission = db.query(Permission).filter(Permission.id == permission_id).first()
            
            if not role or not permission:
                return False
            
            if permission not in role.permissions:
                role.permissions.append(permission)
                db.commit()
            
            logger.info(f"Permission '{permission.name}' added to role '{role.name}'")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error adding permission to role: {e}")
            return False
    
    @staticmethod
    def remove_permission_from_role(db: Session, role_id: int, permission_id: int) -> bool:
        """Remove permission from role"""
        try:
            role = db.query(Role).filter(Role.id == role_id).first()
            permission = db.query(Permission).filter(Permission.id == permission_id).first()
            
            if not role or not permission:
                return False
            
            if permission in role.permissions:
                role.permissions.remove(permission)
                db.commit()
            
            logger.info(f"Permission '{permission.name}' removed from role '{role.name}'")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error removing permission from role: {e}")
            return False
    
    @staticmethod
    def get_or_create_default_role(db: Session) -> Role:
        """Get or create default user role"""
        try:
            default_role = db.query(Role).filter(Role.name == "user").first()
            if not default_role:
                default_role = Role(
                    name="user",
                    description="Default user role",
                    is_system_role=True
                )
                db.add(default_role)
                db.commit()
                db.refresh(default_role)
                logger.info("Created default user role")
            
            return default_role
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error getting/creating default role: {e}")
            raise