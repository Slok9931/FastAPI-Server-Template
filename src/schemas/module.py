from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime

class ModuleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    label: str = Field(..., min_length=1, max_length=100)
    icon: Optional[str] = Field(None, max_length=50)
    route: str = Field(..., min_length=1, max_length=255)
    priority: int = Field(0)
    is_active: bool = True

class ModuleCreate(ModuleBase):
    role_ids: Optional[List[int]] = Field(default=[], description="List of role IDs to assign to this module")
    
    @validator('name')
    def name_alphanumeric_underscore(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Module name must contain only letters, numbers, hyphens, and underscores')
        return v.lower()
    
    @validator('role_ids')
    def validate_role_ids(cls, v):
        if v is None:
            return []
        if not isinstance(v, list):
            raise ValueError('role_ids must be a list of integers')
        for role_id in v:
            if not isinstance(role_id, int) or role_id <= 0:
                raise ValueError('All role IDs must be positive integers')
        return v

class ModuleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    label: Optional[str] = Field(None, min_length=1, max_length=100)
    icon: Optional[str] = Field(None, max_length=50)
    route: Optional[str] = Field(None, min_length=1, max_length=255)
    priority: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None
    role_ids: Optional[List[int]] = Field(None, description="List of role IDs to assign to this module")
    
    @validator('name')
    def name_alphanumeric_underscore(cls, v):
        if v is not None and not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Module name must contain only letters, numbers, hyphens, and underscores')
        return v.lower() if v else v
    
    @validator('role_ids')
    def validate_role_ids(cls, v):
        if v is None:
            return None
        if not isinstance(v, list):
            raise ValueError('role_ids must be a list of integers')
        for role_id in v:
            if not isinstance(role_id, int) or role_id <= 0:
                raise ValueError('All role IDs must be positive integers')
        return v

class RoleInfo(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

class ModuleResponse(ModuleBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    routes: List['RouteResponse'] = []
    roles: List[RoleInfo] = []

    class Config:
        from_attributes = True

class ModuleListResponse(BaseModel):
    id: int
    name: str
    label: str
    icon: Optional[str]
    route: str
    priority: int
    is_active: bool
    created_at: datetime
    route_count: int = 0
    roles: List[RoleInfo] = []

    class Config:
        from_attributes = True

# Import for forward reference
from src.schemas.route import RouteResponse
ModuleResponse.model_rebuild()