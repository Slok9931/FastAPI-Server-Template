from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime

class RouteBase(BaseModel):
    route: str = Field(..., min_length=1, max_length=255)
    label: str = Field(..., min_length=1, max_length=100)
    icon: Optional[str] = Field(None, max_length=50)
    is_active: bool = True
    is_sidebar: bool = True
    module_id: int = Field(..., gt=0)
    parent_id: Optional[int] = Field(None)
    priority: int = Field(0)

    @validator('parent_id')
    def validate_parent_id(cls, v):
        """Validate parent_id - allow None or positive integers"""
        if v is not None and v <= 0:
            raise ValueError('parent_id must be a positive integer or null')
        return v

class RouteCreate(RouteBase):
    role_ids: Optional[List[int]] = Field(default=[], description="List of role IDs to assign to this route")
    
    @validator('route')
    def route_format(cls, v):
        """Ensure route starts with /"""
        if not v.startswith('/'):
            v = '/' + v
        # Remove any double slashes
        v = v.replace('//', '/')
        return v
    
    @validator('label')
    def validate_label(cls, v):
        """Validate label is not empty after stripping"""
        if not v or not v.strip():
            raise ValueError('Label cannot be empty')
        return v.strip()
    
    @validator('icon')
    def validate_icon(cls, v):
        """Validate icon if provided"""
        if v is not None:
            v = v.strip()
            if not v:
                return None
        return v
    
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

class RouteUpdate(BaseModel):
    route: Optional[str] = Field(None, min_length=1, max_length=255)
    label: Optional[str] = Field(None, min_length=1, max_length=100)
    icon: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None
    is_sidebar: Optional[bool] = None
    module_id: Optional[int] = Field(None, gt=0)
    parent_id: Optional[int] = Field(None)
    priority: Optional[int] = Field(None, ge=0)
    role_ids: Optional[List[int]] = Field(None, description="List of role IDs to assign to this route")

    @validator('parent_id')
    def validate_parent_id(cls, v):
        """Validate parent_id - allow None or positive integers"""
        if v is not None and v <= 0:
            raise ValueError('parent_id must be a positive integer or null')
        return v
    
    @validator('route')
    def route_format(cls, v):
        """Ensure route starts with / if provided"""
        if v is not None:
            if not v.startswith('/'):
                v = '/' + v
            # Remove any double slashes
            v = v.replace('//', '/')
        return v
    
    @validator('label')
    def validate_label(cls, v):
        """Validate label if provided"""
        if v is not None:
            if not v or not v.strip():
                raise ValueError('Label cannot be empty')
            v = v.strip()
        return v
    
    @validator('icon')
    def validate_icon(cls, v):
        """Validate icon if provided"""
        if v is not None:
            v = v.strip()
            if not v:
                return None
        return v
    
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

class RouteResponse(RouteBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    module: Optional['ModuleResponse'] = None
    parent: Optional['RouteResponse'] = None
    children: List['RouteResponse'] = []
    roles: List[RoleInfo] = []

    class Config:
        from_attributes = True

class RouteListResponse(BaseModel):
    id: int
    route: str
    label: str
    icon: Optional[str]
    is_active: bool
    is_sidebar: bool
    module_id: int
    parent_id: Optional[int]
    created_at: datetime
    module_name: Optional[str]
    parent_route: Optional[str]
    children_count: int = 0
    priority: int = 0
    roles: List[RoleInfo] = []

    class Config:
        from_attributes = True

class SidebarRouteResponse(BaseModel):
    id: int
    route: str
    label: str
    icon: str
    module_name: str
    priority: int
    children: List['SidebarRouteResponse'] = []

    class Config:
        orm_mode = True

SidebarRouteResponse.update_forward_refs()

class SidebarModuleResponse(BaseModel):
    id: int
    name: str
    label: str
    icon: str
    route: str
    priority: int
    is_active: bool
    routes: List[SidebarRouteResponse] = []

    class Config:
        orm_mode = True

class RouteCreateResponse(BaseModel):
    """Simple response for route creation"""
    id: int
    route: str
    label: str
    icon: Optional[str]
    is_active: bool
    is_sidebar: bool
    module_id: int
    parent_id: Optional[int]
    priority: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Import for forward reference
from src.schemas.module import ModuleResponse
RouteResponse.model_rebuild()
SidebarModuleResponse.model_rebuild()