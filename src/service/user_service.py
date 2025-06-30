from sqlalchemy.orm import Session
from src.models.user import User
from src.models.role import Role
from src.schemas.user import UserCreate, UserUpdate
from src.core.security import get_password_hash, verify_password  # Add verify_password import
from src.service.role_service import RoleService
from fastapi import HTTPException
from typing import Optional, List

class UserService:
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """Get user by username"""
        return db.query(User).filter(User.username == username).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_all_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination"""
        return db.query(User).offset(skip).limit(limit).all()
    
    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """Create a new user with roles that have minimal permissions"""
        
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.username == user_data.username) | (User.email == user_data.email)
        ).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")
        
        # Create user
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password
        )
        
        # Handle role assignment
        user_roles = []
        
        if hasattr(user_data, 'role_names') and user_data.role_names:
            # If role names are provided, create them with minimal permissions
            for role_name in user_data.role_names:
                role = RoleService.create_role_if_not_exists(db, role_name)
                user_roles.append(role)
        elif hasattr(user_data, 'role_ids') and user_data.role_ids:
            # If role IDs are provided, use existing roles
            user_roles = db.query(Role).filter(Role.id.in_(user_data.role_ids)).all()
        else:
            # Default role (will be created with minimal permissions if doesn't exist)
            default_role = RoleService.get_or_create_default_role(db)
            user_roles = [default_role]
        
        new_user.roles = user_roles
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return new_user
    
    @staticmethod
    def update_user(db: Session, user_id: int, user_update: UserUpdate) -> User:
        """Update user information"""
        db_user = UserService.get_user_by_id(db, user_id)
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if new username is already taken (if updating username)
        if user_update.username and user_update.username != db_user.username:
            existing_user = UserService.get_user_by_username(db, user_update.username)
            if existing_user:
                raise HTTPException(status_code=400, detail="Username already taken")
        
        # Check if new email is already taken (if updating email)
        if user_update.email and user_update.email != db_user.email:
            existing_email = UserService.get_user_by_email(db, user_update.email)
            if existing_email:
                raise HTTPException(status_code=400, detail="Email already taken")
        
        # Update roles if provided
        if user_update.role_ids is not None:
            roles = db.query(Role).filter(Role.id.in_(user_update.role_ids)).all()
            if len(roles) != len(user_update.role_ids):
                raise HTTPException(status_code=400, detail="One or more invalid role IDs")
            db_user.roles = roles
        
        # Update password if provided
        if user_update.password:
            db_user.hashed_password = get_password_hash(user_update.password)
        
        # Update other user fields
        update_data = user_update.dict(exclude_unset=True, exclude={'role_ids', 'password'})
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def add_role_to_user(db: Session, user_id: int, role_id: int) -> User:
        """Add a role to user"""
        db_user = UserService.get_user_by_id(db, user_id)
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        role = db.query(Role).filter(Role.id == role_id).first()
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        
        if role not in db_user.roles:
            db_user.roles.append(role)
            db.commit()
            db.refresh(db_user)
        
        return db_user
    
    @staticmethod
    def remove_role_from_user(db: Session, user_id: int, role_id: int) -> User:
        """Remove a role from user"""
        db_user = UserService.get_user_by_id(db, user_id)
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        role = db.query(Role).filter(Role.id == role_id).first()
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        
        if role in db_user.roles:
            db_user.roles.remove(role)
            db.commit()
            db.refresh(db_user)
        
        return db_user
    
    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """Delete a user"""
        db_user = UserService.get_user_by_id(db, user_id)
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        db.delete(db_user)
        db.commit()
        return True
    
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
        """Authenticate user credentials"""
        user = UserService.get_user_by_username(db, username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
    
    @staticmethod
    def deactivate_user(db: Session, user_id: int) -> User:
        """Deactivate a user account"""
        db_user = UserService.get_user_by_id(db, user_id)
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        db_user.is_active = False
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def activate_user(db: Session, user_id: int) -> User:
        """Activate a user account"""
        db_user = UserService.get_user_by_id(db, user_id)
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        db_user.is_active = True
        db.commit()
        db.refresh(db_user)
        return db_user