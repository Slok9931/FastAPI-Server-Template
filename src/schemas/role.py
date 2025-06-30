from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None

class RoleCreate(RoleBase):
    permission_ids: Optional[List[int]] = None

class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    permission_ids: Optional[List[int]] = None

class RoleSimple(BaseModel):
    """Simplified role response without permissions"""
    id: int
    name: str
    description: Optional[str] = None
    is_system_role: bool
    
    class Config:
        from_attributes = True

class RoleResponse(RoleBase):
    id: int
    is_system_role: bool
    permissions: List["PermissionResponse"] = []
    
    class Config:
        from_attributes = True

# Import PermissionResponse to avoid circular imports
try:
    from src.schemas.permission import PermissionResponse
    RoleResponse.model_rebuild()
except ImportError:
    # Handle circular import gracefully
    pass