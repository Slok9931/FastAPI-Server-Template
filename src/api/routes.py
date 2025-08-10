from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from src.config.database import get_db
from src.schemas import (
    RouteResponse, RouteCreate, RouteUpdate, RouteListResponse, 
    SidebarModuleResponse, MessageResponse
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

@router.get("/sidebar", response_model=List[SidebarModuleResponse])
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

@router.get("/{route_id}", response_model=RouteResponse)
async def get_route_by_id(
    route_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission("route", "read"))
):
    """Get route by ID (Requires route:read permission)"""
    try:
        route = RouteService.get_route_by_id(db, route_id)
        if not route:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Route with ID {route_id} not found"
            )
        return RouteResponse.from_orm(route)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting route by ID: {e}")
        raise HTTPException(status_code=500, detail="Unable to retrieve route")

@router.post("/", response_model=RouteResponse)
async def create_route(
    route_data: RouteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission("route", "create"))
):
    """Create new route (Requires route:create permission)"""
    try:
        logger.info(f"API: Creating route with data: {route_data.dict()}")
        
        new_route = RouteService.create_route(db, route_data)
        
        if new_route is None:
            logger.error("RouteService.create_route returned None")
            raise HTTPException(status_code=500, detail="Route creation failed - service returned None")
        
        logger.info(f"API: Route created with ID: {new_route.id}")
        
        if not hasattr(new_route, 'id') or new_route.id is None:
            logger.error("Created route missing ID")
            raise HTTPException(status_code=500, detail="Route creation failed - missing ID")
        
        try:
            response = RouteResponse.from_orm(new_route)
            logger.info(f"API: Successfully converted to response model")
            return response
        except Exception as conversion_error:
            logger.error(f"API: Error converting to response model: {conversion_error}")
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
                children=[]
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

@router.put("/{route_id}", response_model=RouteResponse)
async def update_route(
    route_id: int,
    route_data: RouteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission("route", "update"))
):
    """Update route (Requires route:update permission)"""
    try:
        logger.info(f"API: Updating route {route_id} with data: {route_data.dict(exclude_unset=True)}")
        
        # Check if route exists
        existing_route = RouteService.get_route_by_id(db, route_id)
        if not existing_route:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Route with ID {route_id} not found"
            )
        
        # Update route
        updated_route = RouteService.update_route(db, route_id, route_data)
        
        if not updated_route:
            raise HTTPException(status_code=500, detail="Route update failed")
        
        logger.info(f"API: Route {route_id} updated successfully")
        
        try:
            response = RouteResponse.from_orm(updated_route)
            return response
        except Exception as conversion_error:
            logger.error(f"API: Error converting updated route to response model: {conversion_error}")
            return RouteResponse(
                id=updated_route.id,
                route=updated_route.route,
                label=updated_route.label,
                icon=updated_route.icon,
                is_active=updated_route.is_active,
                is_sidebar=updated_route.is_sidebar,
                module_id=updated_route.module_id,
                parent_id=updated_route.parent_id,
                created_at=updated_route.created_at,
                updated_at=updated_route.updated_at,
                children=[]
            )
        
    except ValueError as e:
        logger.error(f"API: Validation error updating route: {e}")
        if "already exists" in str(e).lower():
            raise HTTPException(status_code=400, detail="Route path already exists in this module")
        elif "not found" in str(e).lower():
            raise HTTPException(status_code=400, detail="Module or parent route not found")
        elif "same module" in str(e).lower():
            raise HTTPException(status_code=400, detail="Parent route must be in the same module")
        elif "circular" in str(e).lower():
            raise HTTPException(status_code=400, detail="Route cannot be its own parent")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API: Unexpected error updating route: {e}")
        raise HTTPException(status_code=500, detail=f"Unable to update route: {str(e)}")

@router.delete("/{route_id}", response_model=MessageResponse)
async def delete_route(
    route_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission("route", "delete"))
):
    """Delete route (Requires route:delete permission)"""
    try:
        logger.info(f"API: Deleting route {route_id}")
        
        # Check if route exists
        existing_route = RouteService.get_route_by_id(db, route_id)
        if not existing_route:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Route with ID {route_id} not found"
            )
        
        # Delete route
        success = RouteService.delete_route(db, route_id)
        
        if not success:
            raise HTTPException(status_code=500, detail="Route deletion failed")
        
        logger.info(f"API: Route {route_id} deleted successfully")
        return MessageResponse(message=f"Route '{existing_route.route}' deleted successfully")
        
    except ValueError as e:
        logger.error(f"API: Validation error deleting route: {e}")
        if "children" in str(e).lower():
            raise HTTPException(status_code=400, detail="Cannot delete route with child routes")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API: Unexpected error deleting route: {e}")
        raise HTTPException(status_code=500, detail=f"Unable to delete route: {str(e)}")