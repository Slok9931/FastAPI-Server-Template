from sqlalchemy.orm import Session
from src.models import User
from src.core import (
    verify_password, 
    create_access_token, 
    create_refresh_token,
    verify_token
)
from src.service.user_service import UserService
from src.schemas import UserCreate
from src.config import settings
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

class AuthService:
    
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> User:
        """Authenticate user with username and password"""
        try:
            user = UserService.get_user_by_username(db, username)
            if not user:
                logger.warning(f"User not found: {username}")
                return None
            
            if not user.is_active:
                logger.warning(f"User not active: {username}")
                return None
                
            if not verify_password(password, user.hashed_password):
                logger.warning(f"Invalid password for user: {username}")
                return None
                
            logger.info(f"User authenticated successfully: {username}")
            return user
        except Exception as e:
            logger.error(f"Authentication error for {username}: {e}")
            return None
    
    @staticmethod
    def register_user(db: Session, user_data: UserCreate) -> User:
        """Register a new user"""
        try:
            # Check if user already exists
            existing_user = UserService.get_user_by_username(db, user_data.username)
            if existing_user:
                raise ValueError("Username already registered")
            
            existing_email = UserService.get_user_by_email(db, user_data.email)
            if existing_email:
                raise ValueError("Email already registered")
            
            # Create new user
            new_user = UserService.create_user(db, user_data)
            logger.info(f"User registered successfully: {new_user.username}")
            return new_user
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Registration error: {e}")
            raise ValueError("Registration failed")
    
    @staticmethod
    def create_tokens(username: str) -> dict:
        """Create access and refresh tokens for user"""
        try:
            logger.info(f"Creating tokens for user: {username}")
            
            # Create access token
            access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
            access_token = create_access_token(
                data={"sub": username, "type": "access"},
                expires_delta=access_token_expires
            )
            logger.debug(f"Access token created for user: {username}")
            
            # Create refresh token (make it optional)
            refresh_token = None
            try:
                refresh_token_expires = timedelta(days=settings.refresh_token_expire_days)
                refresh_token = create_refresh_token(
                    data={"sub": username, "type": "refresh"},
                    expires_delta=refresh_token_expires
                )
                logger.debug(f"Refresh token created for user: {username}")
            except Exception as e:
                logger.warning(f"Refresh token creation failed for {username}: {e}")
                # Continue without refresh token
            
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expires_in": settings.access_token_expire_minutes * 60
            }
        except Exception as e:
            logger.error(f"Token creation error for {username}: {e}")
            raise ValueError(f"Token creation failed: {str(e)}")
    
    @staticmethod
    def refresh_access_token(refresh_token: str) -> dict:
        """Refresh access token using refresh token"""
        try:
            # Verify refresh token and extract username
            token_data = verify_token(refresh_token)
            
            if not token_data or token_data.get("type") != "refresh":
                raise ValueError("Invalid refresh token")
            
            username = token_data.get("sub")
            if not username:
                raise ValueError("Invalid token payload")
            
            # Create new tokens
            return AuthService.create_tokens(username)
            
        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            raise ValueError("Token refresh failed")