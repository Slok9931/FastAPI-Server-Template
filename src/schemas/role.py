from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from src.schemas.permission import PermissionResponse
from src.schemas.user import UserResponseSimple

class RoleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, pattern=r'^[a-zA-Z0-9_]+$')
    description: Optional[str] = Field(None, max_length=200)

class RoleCreate(RoleBase):
    permission_ids: Optional[List[int]] = None

class RoleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50, pattern=r'^[a-zA-Z0-9_]+$')
    description: Optional[str] = Field(None, max_length=200)
    permission_ids: Optional[List[int]] = None

class RoleResponseSimple(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    is_system_role: bool
    created_at: datetime

    class Config:
        from_attributes = True

class RoleResponse(RoleResponseSimple):
    permissions: List[PermissionResponse] = []
    users: List[UserResponseSimple] = []

    class Config:
        from_attributes = True

# Import here to avoid circular imports
RoleResponse.model_rebuild()