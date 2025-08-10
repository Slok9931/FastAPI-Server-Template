from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime

class ModuleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    label: str = Field(..., min_length=1, max_length=100)
    icon: Optional[str] = Field(None, max_length=50)
    route: str = Field(..., min_length=1, max_length=255)
    is_active: bool = True

class ModuleCreate(ModuleBase):
    @validator('name')
    def name_alphanumeric_underscore(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Module name must contain only letters, numbers, hyphens, and underscores')
        return v.lower()

class ModuleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    label: Optional[str] = Field(None, min_length=1, max_length=100)
    icon: Optional[str] = Field(None, max_length=50)
    route: str = Field(..., min_length=1, max_length=255)
    is_active: Optional[bool] = None
    
    @validator('name')
    def name_alphanumeric_underscore(cls, v):
        if v is not None and not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Module name must contain only letters, numbers, hyphens, and underscores')
        return v.lower() if v else v

class ModuleResponse(ModuleBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    routes: List['RouteResponse'] = []

    class Config:
        from_attributes = True

class ModuleListResponse(BaseModel):
    id: int
    name: str
    label: str
    icon: Optional[str]
    route: str
    is_active: bool
    created_at: datetime
    route_count: int = 0

    class Config:
        from_attributes = True

# Import for forward reference
from src.schemas.route import RouteResponse
ModuleResponse.model_rebuild()