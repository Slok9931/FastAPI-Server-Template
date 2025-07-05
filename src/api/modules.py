from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from src.config.database import get_db
from src.schemas.module import ModuleResponse, ModuleCreate, ModuleUpdate, ModuleListResponse
from src.schemas.user import MessageResponse
from src.service.module_service import ModuleService
from src.models.user import User
from src.core.permissions import get_current_user, has_permission
from typing import List
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", response_model=List[ModuleListResponse])
async def get_modules(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    include_count: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission("module", "read"))
):
    """Get all modules (Requires module:read permission)"""
    try:
        if include_count:
            modules = ModuleService.get_all_modules_with_count(db, skip=skip, limit=limit)
        else:
            modules = ModuleService.get_all_modules(db, skip=skip, limit=limit)
            modules = [ModuleListResponse(
                id=module.id,
                name=module.name,
                label=module.label,
                icon=module.icon,
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

@router.get("/{module_id}", response_model=ModuleResponse)
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

@router.put("/{module_id}", response_model=ModuleResponse)
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