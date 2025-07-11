from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime

class DynamicFieldBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    field_type: str = Field(..., pattern="^(string|integer|boolean|text|datetime|float|json)$")
    is_required: bool = False
    is_unique: bool = False
    default_value: Optional[str] = None
    max_length: Optional[int] = None
    field_order: int = 0
    validation_rules: Optional[Dict[str, Any]] = None

class DynamicFieldCreate(DynamicFieldBase):
    pass

class DynamicFieldUpdate(BaseModel):
    name: Optional[str] = None
    field_type: Optional[str] = None
    is_required: Optional[bool] = None
    is_unique: Optional[bool] = None
    default_value: Optional[str] = None
    max_length: Optional[int] = None
    field_order: Optional[int] = None
    validation_rules: Optional[Dict[str, Any]] = None

class DynamicFieldResponse(DynamicFieldBase):
    id: int
    model_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class DynamicModelBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    table_name: str = Field(..., min_length=1, max_length=100, pattern="^[a-zA-Z_][a-zA-Z0-9_]*$")
    description: Optional[str] = None
    is_active: bool = True

class DynamicModelCreate(DynamicModelBase):
    fields: List[DynamicFieldCreate]
    
    @validator('table_name')
    def validate_table_name(cls, v):
        # Ensure table name doesn't conflict with existing tables
        reserved_names = ['users', 'roles', 'permissions', 'modules', 'routes', 'dynamic_models', 'dynamic_fields']
        if v.lower() in reserved_names:
            raise ValueError(f'Table name "{v}" is reserved')
        return v.lower()

class DynamicModelUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class DynamicModelResponse(DynamicModelBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    fields: List[DynamicFieldResponse] = []
    
    class Config:
        from_attributes = True

class DynamicModelListResponse(BaseModel):
    models: List[DynamicModelResponse]
    total: int

class DynamicDataCreate(BaseModel):
    data: Dict[str, Any]

class DynamicDataUpdate(BaseModel):
    data: Dict[str, Any]

class DynamicDataResponse(BaseModel):
    id: int
    data: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True