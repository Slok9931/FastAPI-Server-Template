from sqlalchemy.orm import Session
from sqlalchemy import or_
from src.models import User, Role
from src.schemas import UserCreate, UserUpdate
from src.core import get_password_hash
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class UserService:
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """Get user by username"""
        try:
            return db.query(User).filter(User.username == username).first()
        except Exception as e:
            logger.error(f"Error getting user by username: {e}")
            return None
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        try:
            return db.query(User).filter(User.email == email).first()
        except Exception as e:
            logger.error(f"Error getting user by email: {e}")
            return None
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        try:
            return db.query(User).filter(User.id == user_id).first()
        except Exception as e:
            logger.error(f"Error getting user by ID: {e}")
            return None
    
    @staticmethod
    def get_all_users(
        db: Session, 
        skip: int = 0, 
        limit: int = 100, 
        is_active: Optional[bool] = None, 
        role: Optional[str] = None,
        search: Optional[str] = None  # <-- Add this
    ) -> List[User]:
        """Get all users with optional filters and pagination"""
        try:
            query = db.query(User)
            if is_active is not None:
                query = query.filter(User.is_active == is_active)
            if role:
                query = query.join(User.roles).filter(Role.name == role)
            if search:
                search_term = f"%{search}%"
                query = query.filter(
                    or_(
                        User.username.ilike(search_term),
                        User.email.ilike(search_term)
                    )
                )
            return query.offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting users: {e}")
            return []
    
    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """Create a new user (for admin/authenticated registration)"""
        try:
            # Check if username already exists
            existing_user = db.query(User).filter(User.username == user_data.username).first()
            if existing_user:
                raise ValueError(f"Username '{user_data.username}' already exists")
            
            # Check if email already exists  
            existing_email = db.query(User).filter(User.email == user_data.email).first()
            if existing_email:
                raise ValueError(f"Email '{user_data.email}' already exists")
            
            # Hash password
            hashed_password = get_password_hash(user_data.password)
            
            # Create user
            db_user = User(
                username=user_data.username,
                email=user_data.email,
                hashed_password=hashed_password,
                is_active=True
            )
            
            db.add(db_user)
            db.flush()
            
            # Assign roles
            if user_data.role_ids:
                roles = db.query(Role).filter(Role.id.in_(user_data.role_ids)).all()
                db_user.roles = roles
            elif user_data.role_names:
                roles = db.query(Role).filter(Role.name.in_(user_data.role_names)).all()
                db_user.roles = roles
            else:
                # Assign default user role
                default_role = db.query(Role).filter(Role.name == "user").first()
                if default_role:
                    db_user.roles = [default_role]
            
            db.commit()
            db.refresh(db_user)
            
            logger.info(f"User created: {db_user.username} with {len(db_user.roles)} roles")
            return db_user
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating user: {e}")
            raise
    
    @staticmethod
    def create_public_user(db: Session, user_data: UserCreate) -> User:
        """Create a new user via public registration (always gets 'user' role)"""
        try:
            # Check if username already exists
            existing_user = db.query(User).filter(User.username == user_data.username).first()
            if existing_user:
                raise ValueError(f"Username '{user_data.username}' already exists")
            
            # Check if email already exists  
            existing_email = db.query(User).filter(User.email == user_data.email).first()
            if existing_email:
                raise ValueError(f"Email '{user_data.email}' already exists")
            
            # Hash password
            hashed_password = get_password_hash(user_data.password)
            
            # Create user
            db_user = User(
                username=user_data.username,
                email=user_data.email,
                hashed_password=hashed_password,
                is_active=True
            )
            
            db.add(db_user)
            db.flush()
            
            # Always assign default "user" role for public registration
            default_role = db.query(Role).filter(Role.name == "user").first()
            if default_role:
                db_user.roles = [default_role]
            else:
                # If somehow the user role doesn't exist, create it
                logger.warning("Default 'user' role not found, creating it")
                default_role = Role(
                    name="user",
                    description="Basic user with read-only access",
                    is_system_role=True
                )
                db.add(default_role)
                db.flush()
                db_user.roles = [default_role]
            
            db.commit()
            db.refresh(db_user)
            
            logger.info(f"Public user created: {db_user.username} with 'user' role")
            return db_user
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating public user: {e}")
            raise
    
    @staticmethod
    def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
        """Update user"""
        try:
            db_user = db.query(User).filter(User.id == user_id).first()
            if not db_user:
                return None
            
            # Update fields
            if user_update.username is not None:
                db_user.username = user_update.username
            
            if user_update.email is not None:
                db_user.email = user_update.email
            
            if user_update.password is not None:
                db_user.hashed_password = get_password_hash(user_update.password)
            
            if user_update.is_active is not None:
                db_user.is_active = user_update.is_active
            
            # Update roles
            if user_update.role_ids is not None:
                roles = db.query(Role).filter(Role.id.in_(user_update.role_ids)).all()
                db_user.roles = roles
            
            db.commit()
            db.refresh(db_user)
            
            logger.info(f"User updated: {db_user.username}")
            return db_user
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating user: {e}")
            return None
    
    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """Delete user"""
        try:
            db_user = db.query(User).filter(User.id == user_id).first()
            if not db_user:
                return False
            
            db.delete(db_user)
            db.commit()
            
            logger.info(f"User deleted: {db_user.username}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting user: {e}")
            return False
    
    @staticmethod
    def assign_role_to_user(db: Session, user_id: int, role_id: int) -> bool:
        """Assign role to user"""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            role = db.query(Role).filter(Role.id == role_id).first()
            
            if not user or not role:
                return False
            
            if role not in user.roles:
                user.roles.append(role)
                db.commit()
            
            logger.info(f"Role '{role.name}' assigned to user '{user.username}'")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error assigning role to user: {e}")
            return False
    
    @staticmethod
    def remove_role_from_user(db: Session, user_id: int, role_id: int) -> bool:
        """Remove role from user"""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            role = db.query(Role).filter(Role.id == role_id).first()
            
            if not user or not role:
                return False
            
            if role in user.roles:
                user.roles.remove(role)
                db.commit()
            
            logger.info(f"Role '{role.name}' removed from user '{user.username}'")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error removing role from user: {e}")
            return False
    
    @staticmethod
    def bulk_delete_users(db: Session, user_ids: list[int]) -> int:
        """Bulk delete users by IDs. Returns number of deleted users."""
        if not user_ids:
            logger.warning("No user IDs provided for bulk delete")
            return 0
        
        try:
            logger.info(f"Starting bulk delete for user IDs: {user_ids}")
            deleted_count = 0
            
            for user_id in user_ids:
                try:
                    # Get the user
                    user = db.query(User).filter(User.id == user_id).first()
                    if user:
                        # Clear roles first (this handles the relationship)
                        user.roles.clear()
                        db.flush()
                        
                        # Delete the user
                        db.delete(user)
                        deleted_count += 1
                        logger.info(f"Deleted user ID: {user_id}")
                    else:
                        logger.warning(f"User ID {user_id} not found")
                        
                except Exception as e:
                    logger.error(f"Error deleting user ID {user_id}: {e}")
                    continue
            
            db.commit()
            logger.info(f"Bulk delete completed successfully: {deleted_count} users deleted")
            return deleted_count
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error bulk deleting users: {e}")
            return 0