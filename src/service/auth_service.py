from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import timedelta
from src.service.user_service import UserService
from src.schemas.user import UserCreate, UserLogin
from src.core.security import create_access_token, verify_password
from src.models.user import User

class AuthService:
    
    @staticmethod
    def register_user(db: Session, user: UserCreate) -> User:
        """Register a new user"""
        return UserService.create_user(db, user)
    
    @staticmethod
    def authenticate_and_create_token(db: Session, credentials: UserLogin) -> dict:
        """Authenticate user and create access token"""
        # Authenticate user
        user = UserService.authenticate_user(db, credentials.username, credentials.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Inactive user account",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token
        access_token = create_access_token(
            data={"sub": user.username}
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    
    @staticmethod
    def refresh_token(db: Session, current_user: User) -> dict:
        """Create a new access token for user"""
        if not current_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Inactive user account"
            )
        
        access_token = create_access_token(
            data={"sub": current_user.username}
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "roles": current_user.get_role_names()
        }
    
    @staticmethod
    def change_password(db: Session, user_id: int, old_password: str, new_password: str) -> bool:
        """Change user password"""
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Verify old password
        if not verify_password(old_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect current password"
            )
        
        # Update password
        from src.core.security import get_password_hash
        user.hashed_password = get_password_hash(new_password)
        db.commit()
        
        return True