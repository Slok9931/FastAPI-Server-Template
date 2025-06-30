from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class PermissionBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, pattern=r'^[a-zA-Z0-9_]+$')
    description: Optional[str] = Field(None, max_length=200)
    category: Optional[str] = Field(None, max_length=50)

class PermissionCreate(PermissionBase):
    pass

class PermissionUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100, pattern=r'^[a-zA-Z0-9_]+$')
    description: Optional[str] = Field(None, max_length=200)
    category: Optional[str] = Field(None, max_length=50)

class PermissionResponse(PermissionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True  # Updated from orm_mode = True for Pydantic v2

class PermissionInRole(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    
    class Config:
        from_attributes = True