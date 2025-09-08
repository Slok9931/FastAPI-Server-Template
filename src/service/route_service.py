from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import List, Optional
import logging
from src.models import Route, Module, User, Role
from src.schemas import RouteCreate, RouteUpdate, RouteListResponse, SidebarRouteResponse, SidebarModuleResponse, RoleInfo

logger = logging.getLogger(__name__)

class RouteService:
    @staticmethod
    def get_all_routes(db: Session, skip: int = 0, limit: int = 100) -> List[Route]:
        """Get all routes with pagination, sorted by priority"""
        try:
            return db.query(Route).options(
                joinedload(Route.module),
                joinedload(Route.parent),
                joinedload(Route.children),
                joinedload(Route.roles)
            ).order_by(Route.priority).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting routes: {e}")
            return []

    @staticmethod
    def get_all_routes_with_details(db: Session, skip: int = 0, limit: int = 100) -> List[RouteListResponse]:
        """Get all routes with module and parent details, sorted by priority"""
        try:
            routes = db.query(Route).options(
                joinedload(Route.module),
                joinedload(Route.parent),
                joinedload(Route.children),
                joinedload(Route.roles)
            ).order_by(Route.priority).offset(skip).limit(limit).all()
            
            # Convert to response format
            route_list = []
            for route in routes:
                roles = [RoleInfo(id=role.id, name=role.name, description=role.description) for role in route.roles] if route.roles else []
                
                route_list.append(RouteListResponse(
                    id=route.id,
                    route=route.route,
                    label=route.label,
                    icon=route.icon,
                    is_active=route.is_active,
                    is_sidebar=route.is_sidebar,
                    module_id=route.module_id,
                    parent_id=route.parent_id,
                    priority=route.priority,
                    created_at=route.created_at,
                    module_name=route.module.name if route.module else None,
                    parent_route=route.parent.route if route.parent else None,
                    children_count=len(route.children) if route.children else 0,
                    roles=roles
                ))
            
            return route_list
        except Exception as e:
            logger.error(f"Error getting routes with details: {e}")
            return []
    
    @staticmethod
    def get_route_by_id(db: Session, route_id: int) -> Optional[Route]:
        """Get route by ID"""
        try:
            return db.query(Route).options(
                joinedload(Route.module),
                joinedload(Route.parent),
                joinedload(Route.children),
                joinedload(Route.roles)
            ).filter(Route.id == route_id).first()
        except Exception as e:
            logger.error(f"Error getting route by ID: {e}")
            return None
    
    @staticmethod
    def get_routes_by_module(db: Session, module_id: Optional[int] = None) -> List[Route]:
        """Get all routes for a specific module, or all routes if module_id is None, sorted by priority"""
        try:
            query = db.query(Route).options(
                joinedload(Route.module),
                joinedload(Route.parent),
                joinedload(Route.children),
                joinedload(Route.roles)
            )
            if module_id is not None:
                query = query.filter(Route.module_id == module_id)
            return query.order_by(Route.priority).all()
        except Exception as e:
            logger.error(f"Error getting routes by module: {e}")
            return []

    @staticmethod
    def get_routes_by_parent(db: Session, parent_id: int) -> List[Route]:
        """Get all child routes for a specific parent route, sorted by priority"""
        try:
            query = db.query(Route).options(
                joinedload(Route.module),
                joinedload(Route.parent),
                joinedload(Route.children),
                joinedload(Route.roles)
            )
            if parent_id is not None:
                query = query.filter(Route.parent_id == parent_id)
            return query.order_by(Route.priority).all()
        except Exception as e:
            logger.error(f"Error getting routes by parent: {e}")
            return []

    @staticmethod
    def get_sidebar_routes(db: Session, current_user: User) -> List[SidebarModuleResponse]:
        """Get sidebar modules with their routes in tree structure based on user roles, all sorted by priority"""
        try:
            # Get user's role IDs
            user_role_ids = [role.id for role in current_user.roles]
            logger.info(f"User {current_user.username} has role IDs: {user_role_ids}")
            
            if not user_role_ids:
                logger.info("User has no roles, returning empty sidebar")
                return []
            
            # Get all active modules with their roles loaded
            all_modules = db.query(Module).options(
                joinedload(Module.roles)
            ).filter(Module.is_active == True).order_by(Module.priority).all()

            # Filter modules based on user roles
            accessible_modules = []
            for module in all_modules:
                module_role_ids = [role.id for role in module.roles]
                if any(role_id in user_role_ids for role_id in module_role_ids):
                    accessible_modules.append(module)
            
            result = []

            for module in accessible_modules:
                logger.info(f"Processing module: {module.name}")
                
                # Get all routes for this module with their roles loaded
                all_routes = db.query(Route).options(
                    joinedload(Route.children),
                    joinedload(Route.roles)
                ).filter(
                    Route.module_id == module.id,
                    Route.parent_id.is_(None),
                    Route.is_sidebar == True,
                    Route.is_active == True
                ).order_by(Route.priority).all()
                
                # Filter parent routes based on user roles
                accessible_parent_routes = []
                for route in all_routes:
                    route_role_ids = [role.id for role in route.roles]
                    if any(role_id in user_role_ids for role_id in route_role_ids):
                        accessible_parent_routes.append(route)

                def build_route_tree(route):
                    # Get accessible children for this route
                    accessible_children = []
                    for child in route.children:
                        if (child.is_active and child.is_sidebar):
                            child_role_ids = [role.id for role in child.roles]
                            if any(role_id in user_role_ids for role_id in child_role_ids):
                                accessible_children.append(build_route_tree(child))
                    
                    # Sort children by priority
                    accessible_children.sort(key=lambda r: r.priority if hasattr(r, 'priority') else 0)
                    
                    return SidebarRouteResponse(
                        id=route.id,
                        route=route.route,
                        label=route.label,
                        icon=route.icon or "",
                        module_name=module.name,
                        priority=route.priority,
                        children=accessible_children
                    )

                routes_tree = [build_route_tree(route) for route in accessible_parent_routes]
                logger.info(f"Module {module.name} has {len(routes_tree)} accessible routes")
                
                result.append(SidebarModuleResponse(
                    id=module.id,
                    name=module.name,
                    label=module.label,
                    icon=module.icon or "",
                    route=module.route,
                    is_active=module.is_active,
                    priority=module.priority,
                    routes=routes_tree
                ))

            logger.info(f"User {current_user.username} has access to {len(result)} modules in sidebar")
            return result

        except Exception as e:
            logger.error(f"Error getting sidebar routes: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return []
    
    @staticmethod
    def create_route(db: Session, route_data: RouteCreate) -> Route:
        """Create a new route"""
        try:
            logger.info(f"Starting route creation with data: {route_data.dict()}")
            
            # Validate module exists
            module = db.query(Module).filter(Module.id == route_data.module_id).first()
            if not module:
                logger.error(f"Module with ID {route_data.module_id} not found")
                raise ValueError(f"Module with ID {route_data.module_id} not found")
            
            logger.info(f"Module found: {module.name}")
            
            # Validate parent route exists (if specified)
            if route_data.parent_id:
                parent_route = db.query(Route).filter(Route.id == route_data.parent_id).first()
                if not parent_route:
                    logger.error(f"Parent route with ID {route_data.parent_id} not found")
                    raise ValueError(f"Parent route with ID {route_data.parent_id} not found")
                
                # Ensure parent is in the same module
                if parent_route.module_id != route_data.module_id:
                    logger.error("Parent route not in same module")
                    raise ValueError("Parent route must be in the same module")
                
                logger.info(f"Parent route found: {parent_route.route}")
            
            # Validate role IDs if provided
            roles = []
            if route_data.role_ids:
                roles = db.query(Role).filter(Role.id.in_(route_data.role_ids)).all()
                found_role_ids = [role.id for role in roles]
                missing_role_ids = set(route_data.role_ids) - set(found_role_ids)
                if missing_role_ids:
                    raise ValueError(f"Role IDs not found: {sorted(missing_role_ids)}")
                logger.info(f"Found {len(roles)} roles for assignment")
            
            # Check if route path already exists in the same module
            existing_route = db.query(Route).filter(
                Route.route == route_data.route,
                Route.module_id == route_data.module_id
            ).first()
            if existing_route:
                logger.error(f"Route '{route_data.route}' already exists")
                raise ValueError(f"Route '{route_data.route}' already exists in module '{module.name}'")
            
            # Create route
            db_route = Route(
                route=route_data.route,
                label=route_data.label,
                icon=route_data.icon,
                is_active=route_data.is_active,
                is_sidebar=route_data.is_sidebar,
                module_id=route_data.module_id,
                parent_id=route_data.parent_id,
                priority=route_data.priority
            )
            
            # Assign roles
            db_route.roles = roles
            
            logger.info(f"Route object created: {db_route}")
            
            db.add(db_route)
            logger.info("Route added to session")
            
            db.commit()
            logger.info("Database committed")
            
            db.refresh(db_route)
            logger.info(f"Route refreshed with ID: {db_route.id}")
            
            # Load the route with all relationships
            created_route = db.query(Route).options(
                joinedload(Route.module),
                joinedload(Route.parent),
                joinedload(Route.children),
                joinedload(Route.roles)
            ).filter(Route.id == db_route.id).first()
            
            if not created_route:
                logger.error("Failed to retrieve created route")
                raise ValueError("Failed to create route - could not retrieve created object")
            
            logger.info(f"Route created successfully: {created_route.route} (ID: {created_route.id}) in module {module.name} with {len(roles)} roles assigned")
            return created_route
            
        except ValueError as ve:
            db.rollback()
            logger.error(f"Validation error creating route: {ve}")
            raise ve
        except Exception as e:
            db.rollback()
            logger.error(f"Unexpected error creating route: {e}")
            raise ValueError(f"Failed to create route: {str(e)}")
    
    @staticmethod
    def update_route(db: Session, route_id: int, route_update: RouteUpdate) -> Optional[Route]:
        """Update route"""
        try:
            db_route = db.query(Route).options(joinedload(Route.roles)).filter(Route.id == route_id).first()
            if not db_route:
                return None
            
            # Validate module exists (if being updated)
            if route_update.module_id:
                module = db.query(Module).filter(Module.id == route_update.module_id).first()
                if not module:
                    raise ValueError(f"Module with ID {route_update.module_id} not found")
            
            # Validate parent route exists (if being updated)
            if route_update.parent_id:
                parent_route = db.query(Route).filter(Route.id == route_update.parent_id).first()
                if not parent_route:
                    raise ValueError(f"Parent route with ID {route_update.parent_id} not found")
                
                # Prevent circular reference
                if route_update.parent_id == route_id:
                    raise ValueError("Route cannot be its own parent")
                
                # Ensure parent is in the same module
                module_id = route_update.module_id or db_route.module_id
                if parent_route.module_id != module_id:
                    raise ValueError("Parent route must be in the same module")
            
            # Validate and update roles if provided
            if route_update.role_ids is not None:
                if route_update.role_ids:  # If list is not empty
                    roles = db.query(Role).filter(Role.id.in_(route_update.role_ids)).all()
                    found_role_ids = [role.id for role in roles]
                    missing_role_ids = set(route_update.role_ids) - set(found_role_ids)
                    if missing_role_ids:
                        raise ValueError(f"Role IDs not found: {sorted(missing_role_ids)}")
                    db_route.roles = roles
                else:  # Empty list means remove all roles
                    db_route.roles = []
                logger.info(f"Route {db_route.route} roles updated to: {[role.name for role in db_route.roles]}")
            
            # Check if route path already exists (if route is being updated)
            if route_update.route:
                module_id = route_update.module_id or db_route.module_id
                existing_route = db.query(Route).filter(
                    Route.route == route_update.route,
                    Route.module_id == module_id,
                    Route.id != route_id
                ).first()
                if existing_route:
                    raise ValueError(f"Route '{route_update.route}' already exists in this module")
            
            # Update other fields
            update_data = route_update.dict(exclude_unset=True, exclude={'role_ids'})
            for field, value in update_data.items():
                setattr(db_route, field, value)
            
            db.commit()
            db.refresh(db_route)
            
            logger.info(f"Route updated: {db_route.route}")
            return db_route
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating route: {e}")
            raise
    
    @staticmethod
    def delete_route(db: Session, route_id: int) -> bool:
        """Delete route"""
        try:
            db_route = db.query(Route).filter(Route.id == route_id).first()
            if not db_route:
                return False
            
            # Check if route has children
            children_count = db.query(Route).filter(Route.parent_id == route_id).count()
            if children_count > 0:
                raise ValueError(f"Cannot delete route '{db_route.route}' because it has {children_count} child routes")
            
            db.delete(db_route)
            db.commit()
            
            logger.info(f"Route deleted: {db_route.route}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting route: {e}")
            raise
    
    @staticmethod
    def toggle_route_status(db: Session, route_id: int) -> Optional[Route]:
        """Toggle route active status"""
        try:
            db_route = db.query(Route).filter(Route.id == route_id).first()
            if not db_route:
                return None
            
            db_route.is_active = not db_route.is_active
            db.commit()
            db.refresh(db_route)
            
            logger.info(f"Route status toggled: {db_route.route} -> {db_route.is_active}")
            return db_route
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error toggling route status: {e}")
            raise
    
    @staticmethod
    def toggle_sidebar_visibility(db: Session, route_id: int) -> Optional[Route]:
        """Toggle route sidebar visibility"""
        try:
            db_route = db.query(Route).filter(Route.id == route_id).first()
            if not db_route:
                return None
            
            db_route.is_sidebar = not db_route.is_sidebar
            db.commit()
            db.refresh(db_route)
            
            logger.info(f"Route sidebar visibility toggled: {db_route.route} -> {db_route.is_sidebar}")
            return db_route
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error toggling route sidebar visibility: {e}")
            raise