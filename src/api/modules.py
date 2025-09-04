from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
import logging
from src.config.database import get_db
from src.schemas import (
    ModuleResponse, ModuleCreate, ModuleUpdate, 
    ModuleListResponse, MessageResponse
)
from src.models import User, Module
from src.service import ModuleService
from src.core import has_permission

logger = logging.getLogger(__name__)
router = APIRouter()

class BulkDeleteRequest(BaseModel):
    module_ids: list[int]

@router.get("/", response_model=List[ModuleListResponse])
async def get_modules(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: str = Query(None),
    is_active: bool = Query(None),
    include_count: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission("module", "read"))
):
    """Get all modules with optional filters (Requires module:read permission)"""
    try:
        if include_count:
            modules = ModuleService.get_all_modules_with_count(
                db, 
                skip=skip, 
                limit=limit,
                search=search,
                is_active=is_active
            )
        else:
            modules = ModuleService.get_all_modules(
                db, 
                skip=skip, 
                limit=limit,
                search=search,
                is_active=is_active
            )
            modules = [ModuleListResponse(
                id=module.id,
                name=module.name,
                label=module.label,
                icon=module.icon,
                route=module.route,
                priority=module.priority,
                is_active=module.is_active,
                created_at=module.created_at,
                route_count=0
            ) for module in modules]
        return modules
    except Exception as e:
        logger.error(f"Error getting modules: {e}")
        raise HTTPException(status_code=500, detail="Unable to retrieve modules at this time")

@router.get("/active", response_model=List[ModuleResponse])
async def get_active_modules(
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission("module", "read"))
):
    """Get all active modules (Requires module:read permission)"""
    try:
        modules = ModuleService.get_active_modules(db)
        return [ModuleResponse.from_orm(module) for module in modules]
    except Exception as e:
        logger.error(f"Error getting active modules: {e}")
        raise HTTPException(status_code=500, detail="Unable to retrieve active modules")

@router.post("/", response_model=ModuleResponse)
async def create_module(
    module_data: ModuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission("module", "create"))
):
    """Create new module (Requires module:create permission)"""
    try:
        new_module = ModuleService.create_module(db, module_data)
        return ModuleResponse.from_orm(new_module)
    except ValueError as e:
        if "already exists" in str(e).lower():
            raise HTTPException(status_code=400, detail="Module name already exists")
        raise HTTPException(status_code=400, detail="Invalid module information provided")
    except Exception as e:
        logger.error(f"Error creating module: {e}")
        raise HTTPException(status_code=500, detail="Unable to create module")

@router.get("/get-one/{module_id}", response_model=ModuleResponse)
async def get_module(
    module_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission("module", "read"))
):
    """Get module by ID (Requires module:read permission)"""
    try:
        module = ModuleService.get_module_by_id(db, module_id)
        if not module:
            raise HTTPException(status_code=404, detail="Module not found")
        return ModuleResponse.from_orm(module)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting module: {e}")
        raise HTTPException(status_code=500, detail="Unable to retrieve module information")

@router.put("/get-one/{module_id}", response_model=ModuleResponse)
async def update_module(
    module_id: int,
    module_update: ModuleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission("module", "update"))
):
    """Update module (Requires module:update permission)"""
    try:
        updated_module = ModuleService.update_module(db, module_id, module_update)
        if not updated_module:
            raise HTTPException(status_code=404, detail="Module not found")
        return ModuleResponse.from_orm(updated_module)
    except ValueError as e:
        if "already exists" in str(e).lower():
            raise HTTPException(status_code=400, detail="Module name already exists")
        raise HTTPException(status_code=400, detail="Invalid module information provided")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating module: {e}")
        raise HTTPException(status_code=500, detail="Unable to update module")

@router.delete("/{module_id}", response_model=MessageResponse)
async def delete_module(
    module_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission("module", "delete"))
):
    """Delete module (Requires module:delete permission)"""
    try:
        success = ModuleService.delete_module(db, module_id)
        if not success:
            raise HTTPException(status_code=404, detail="Module not found")
        return MessageResponse(
            message="Module deleted successfully",
            success=True
        )
    except ValueError as e:
        if "has" in str(e).lower() and "routes" in str(e).lower():
            raise HTTPException(status_code=400, detail="Cannot delete module that has associated routes")
        raise HTTPException(status_code=400, detail="Module cannot be deleted")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting module: {e}")
        raise HTTPException(status_code=500, detail="Unable to delete module")

@router.post("/bulk-delete", response_model=MessageResponse)
async def bulk_delete_modules(
    request: BulkDeleteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission("module", "delete"))
):
    """Bulk delete modules (Requires module:delete permission)"""
    try:
        logger.info(f"Bulk delete request: {request.module_ids}")

        if not request.module_ids:
            raise HTTPException(status_code=400, detail="No module IDs provided")

        # Check if modules exist before attempting to delete
        existing_modules = db.query(Module).filter(Module.id.in_(request.module_ids)).all()
        existing_ids = [module.id for module in existing_modules]
        logger.info(f"Existing module IDs found: {existing_ids}")

        if not existing_ids:
            raise HTTPException(status_code=404, detail="No modules found with the provided IDs")

        # Perform bulk delete
        deleted_count = ModuleService.bulk_delete_modules(db, existing_ids)
        logger.info(f"Deleted count: {deleted_count}")

        if deleted_count == 0:
            raise HTTPException(status_code=500, detail="Failed to delete modules")

        return MessageResponse(
            message=f"{deleted_count} module(s) deleted successfully",
            success=True
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error bulk deleting modules: {e}")
        raise HTTPException(status_code=500, detail="Unable to bulk delete modules")