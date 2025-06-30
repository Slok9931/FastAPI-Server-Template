from pydantic import BaseModel, EmailStr, validator
from typing import List, Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str
    role_ids: Optional[List[int]] = None
    role_names: Optional[List[str]] = None
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    role_ids: Optional[List[int]] = None
    
    @validator('password')
    def validate_password(cls, v):
        if v is not None and len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponseSimple(UserBase):
    """Simple user response without roles"""
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Define RoleSimple here to avoid circular imports
class RoleSimpleInUser(BaseModel):
    """Role schema for user responses"""
    id: int
    name: str
    description: Optional[str] = None
    is_system_role: bool
    
    class Config:
        from_attributes = True

class UserResponse(UserBase):
    """Full user response with roles"""
    id: int
    is_active: bool
    created_at: datetime
    roles: List[RoleSimpleInUser] = []
    
    class Config:
        from_attributes = True

class UserInDB(UserBase):
    id: int
    hashed_password: str
    is_active: bool
    created_at: datetime

class Token(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseModel):
    username: Optional[str] = None

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('New password must be at least 8 characters long')
        return v

class MessageResponse(BaseModel):
    message: str
    success: bool = True