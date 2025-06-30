from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
from src.config.settings import settings

class UserBase(BaseModel):
    username: str = Field(..., min_length=settings.username_min_length, max_length=settings.username_max_length)
    # Use EmailStr for better email validation (requires email-validator package)
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=settings.password_min_length)
    role_names: Optional[List[str]] = None
    role_ids: Optional[List[int]] = None

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=settings.username_min_length, max_length=settings.username_max_length)  # Fixed typo here
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=settings.password_min_length)
    is_active: Optional[bool] = None
    role_ids: Optional[List[int]] = None

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    roles: List['RoleResponseSimple'] = []

    class Config:
        from_attributes = True

class UserResponseSimple(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseModel):
    username: Optional[str] = None

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=settings.password_min_length)

# Import here to avoid circular imports
from src.schemas.role import RoleResponseSimple
UserResponse.model_rebuild()