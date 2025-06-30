from pydantic import BaseModel
from typing import Optional

class PermissionBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = "general"

class PermissionCreate(PermissionBase):
    pass

class PermissionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None

class PermissionResponse(PermissionBase):
    id: int
    
    class Config:
        from_attributes = True