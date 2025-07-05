from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from src.config.database import get_db
from src.schemas import (
    RouteResponse, RouteCreate, RouteListResponse, 
    SidebarResponse
)
from src.models import User
from src.service import RouteService
from src.core import get_current_user, has_permission
from typing import List
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", response_model=List[RouteListResponse])
async def get_routes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    module_id: int = Query(None, description="Filter by module ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission("route", "read"))
):
    """Get all routes (Requires route:read permission)"""
    try:
        if module_id:
            routes = RouteService.get_routes_by_module(db, module_id)
            routes = [RouteListResponse(
                id=route.id,
                route=route.route,
                label=route.label,
                icon=route.icon,
                is_active=route.is_active,
                is_sidebar=route.is_sidebar,
                module_id=route.module_id,
                parent_id=route.parent_id,
                created_at=route.created_at,
                module_name=route.module.name,
                parent_route=route.parent.route if route.parent else None,
                children_count=len(route.children)
            ) for route in routes]
        else:
            routes = RouteService.get_all_routes_with_details(db, skip=skip, limit=limit)
        return routes
    except Exception as e:
        logger.error(f"Error getting routes: {e}")
        raise HTTPException(status_code=500, detail="Unable to retrieve routes at this time")

@router.get("/sidebar", response_model=List[SidebarResponse])
async def get_sidebar_routes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get sidebar menu routes (Requires authentication only)"""
    try:
        sidebar_routes = RouteService.get_sidebar_routes(db)
        return sidebar_routes
    except Exception as e:
        logger.error(f"Error getting sidebar routes: {e}")
        raise HTTPException(status_code=500, detail="Unable to retrieve sidebar routes")

@router.post("/", response_model=RouteResponse)
async def create_route(
    route_data: RouteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission("route", "create"))  # ✅ Fix permission
):
    """Create new route (Requires user:create permission)"""
    try:
        logger.info(f"API: Creating route with data: {route_data.dict()}")
        
        # ✅ Call service and check for None return
        new_route = RouteService.create_route(db, route_data)
        
        if new_route is None:
            logger.error("RouteService.create_route returned None")
            raise HTTPException(status_code=500, detail="Route creation failed - service returned None")
        
        logger.info(f"API: Route created with ID: {new_route.id}")
        
        # ✅ Verify all required fields are present
        if not hasattr(new_route, 'id') or new_route.id is None:
            logger.error("Created route missing ID")
            raise HTTPException(status_code=500, detail="Route creation failed - missing ID")
        
        # ✅ Convert to response model safely
        try:
            response = RouteResponse.from_orm(new_route)
            logger.info(f"API: Successfully converted to response model")
            return response
        except Exception as conversion_error:
            logger.error(f"API: Error converting to response model: {conversion_error}")
            # ✅ Return a manual response if from_orm fails
            return RouteResponse(
                id=new_route.id,
                route=new_route.route,
                label=new_route.label,
                icon=new_route.icon,
                is_active=new_route.is_active,
                is_sidebar=new_route.is_sidebar,
                module_id=new_route.module_id,
                parent_id=new_route.parent_id,
                created_at=new_route.created_at,
                updated_at=new_route.updated_at,
                module=None,  # Simplified to avoid circular reference
                parent=None,  # Simplified to avoid circular reference
                children=[]   # Empty for new route
            )
        
    except ValueError as e:
        logger.error(f"API: Validation error: {e}")
        if "already exists" in str(e).lower():
            raise HTTPException(status_code=400, detail="Route already exists in this module")
        elif "not found" in str(e).lower():
            raise HTTPException(status_code=400, detail="Module or parent route not found")
        elif "same module" in str(e).lower():
            raise HTTPException(status_code=400, detail="Parent route must be in the same module")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API: Unexpected error creating route: {e}")
        raise HTTPException(status_code=500, detail=f"Unable to create route: {str(e)}")

# ✅ Add a simple test endpoint
@router.post("/test", response_model=dict)
async def create_route_test(
    route_data: RouteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission("route", "create"))
):
    """Test route creation endpoint"""
    try:
        logger.info(f"TEST: Creating route with data: {route_data.dict()}")
        
        new_route = RouteService.create_route(db, route_data)
        
        if new_route is None:
            return {"error": "Service returned None", "success": False}
        
        return {
            "success": True,
            "route_id": new_route.id,
            "route_path": new_route.route,
            "label": new_route.label,
            "module_id": new_route.module_id,
            "created_at": str(new_route.created_at)
        }
        
    except Exception as e:
        logger.error(f"TEST: Error: {e}")
        return {"error": str(e), "success": False}