from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
import logging

from src.config.database import get_db
from src.models.user import User
from src.core.permissions import has_permission
from src.service import DynamicModelService, DynamicDataService
from src.schemas import (
    DynamicModelCreate, DynamicModelUpdate, DynamicModelResponse, 
    DynamicModelListResponse, DynamicDataCreate, DynamicDataUpdate, MessageResponse
)

router = APIRouter()
logger = logging.getLogger(__name__)

# Dynamic Model Management Endpoints

@router.post("/models", response_model=DynamicModelResponse)
async def create_dynamic_model(
    model_data: DynamicModelCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission("dynamic_model", "create"))
):
    """Create new dynamic model (Requires dynamic_model:create permission)"""
    try:
        new_model = DynamicModelService.create_dynamic_model(db, model_data)
        return DynamicModelResponse.from_orm(new_model)
    except ValueError as e:
        if "already exists" in str(e).lower():
            raise HTTPException(status_code=400, detail="Model name or table name already exists")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating dynamic model: {e}")
        raise HTTPException(status_code=500, detail="Unable to create dynamic model")

@router.get("/models", response_model=DynamicModelListResponse)
async def get_dynamic_models(
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission("dynamic_model", "read"))
):
    """Get all dynamic models (Requires dynamic_model:read permission)"""
    try:
        models = DynamicModelService.get_all_dynamic_models(db)
        return DynamicModelListResponse(
            models=[DynamicModelResponse.from_orm(model) for model in models],
            total=len(models)
        )
    except Exception as e:
        logger.error(f"Error getting dynamic models: {e}")
        raise HTTPException(status_code=500, detail="Unable to retrieve dynamic models")

@router.get("/models/{model_id}", response_model=DynamicModelResponse)
async def get_dynamic_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission("dynamic_model", "read"))
):
    """Get dynamic model by ID (Requires dynamic_model:read permission)"""
    model = DynamicModelService.get_dynamic_model_by_id(db, model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Dynamic model not found")
    return DynamicModelResponse.from_orm(model)

@router.put("/models/{model_id}", response_model=DynamicModelResponse)
async def update_dynamic_model(
    model_id: int,
    model_update: DynamicModelUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission("dynamic_model", "update"))
):
    """Update dynamic model (Requires dynamic_model:update permission)"""
    try:
        updated_model = DynamicModelService.update_dynamic_model(db, model_id, model_update)
        if not updated_model:
            raise HTTPException(status_code=404, detail="Dynamic model not found")
        return DynamicModelResponse.from_orm(updated_model)
    except Exception as e:
        logger.error(f"Error updating dynamic model: {e}")
        raise HTTPException(status_code=500, detail="Unable to update dynamic model")

@router.delete("/models/{model_id}", response_model=MessageResponse)
async def delete_dynamic_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission("dynamic_model", "delete"))
):
    """Delete dynamic model (Requires dynamic_model:delete permission)"""
    try:
        deleted = DynamicModelService.delete_dynamic_model(db, model_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Dynamic model not found")
        return MessageResponse(message="Dynamic model deleted successfully")
    except Exception as e:
        logger.error(f"Error deleting dynamic model: {e}")
        raise HTTPException(status_code=500, detail="Unable to delete dynamic model")

# Dynamic Data Management Endpoints

@router.post("/models/{model_id}/data")
async def create_dynamic_data(
    model_id: int,
    data: DynamicDataCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission("dynamic_data", "create"))
):
    """Create new record in dynamic model (Requires dynamic_data:create permission)"""
    try:
        new_record = DynamicDataService.create_record(db, model_id, data)
        return new_record
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating dynamic data: {e}")
        raise HTTPException(status_code=500, detail="Unable to create record")

@router.get("/models/{model_id}/data")
async def get_dynamic_data(
    model_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission("dynamic_data", "read"))
):
    """Get all records from dynamic model (Requires dynamic_data:read permission)"""
    try:
        records = DynamicDataService.get_all_records(db, model_id, skip, limit)
        return {"records": records, "total": len(records)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting dynamic data: {e}")
        raise HTTPException(status_code=500, detail="Unable to retrieve records")

@router.get("/models/{model_id}/data/{record_id}")
async def get_dynamic_record(
    model_id: int,
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission("dynamic_data", "read"))
):
    """Get single record from dynamic model (Requires dynamic_data:read permission)"""
    try:
        record = DynamicDataService.get_record(db, model_id, record_id)
        if not record:
            raise HTTPException(status_code=404, detail="Record not found")
        return record
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting dynamic record: {e}")
        raise HTTPException(status_code=500, detail="Unable to retrieve record")

@router.put("/models/{model_id}/data/{record_id}")
async def update_dynamic_record(
    model_id: int,
    record_id: int,
    data: DynamicDataUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission("dynamic_data", "update"))
):
    """Update record in dynamic model (Requires dynamic_data:update permission)"""
    try:
        updated_record = DynamicDataService.update_record(db, model_id, record_id, data)
        if not updated_record:
            raise HTTPException(status_code=404, detail="Record not found")
        return updated_record
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating dynamic record: {e}")
        raise HTTPException(status_code=500, detail="Unable to update record")

@router.delete("/models/{model_id}/data/{record_id}", response_model=MessageResponse)
async def delete_dynamic_record(
    model_id: int,
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission("dynamic_data", "delete"))
):
    """Delete record from dynamic model (Requires dynamic_data:delete permission)"""
    try:
        deleted = DynamicDataService.delete_record(db, model_id, record_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Record not found")
        return MessageResponse(message="Record deleted successfully")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting dynamic record: {e}")
        raise HTTPException(status_code=500, detail="Unable to delete record")