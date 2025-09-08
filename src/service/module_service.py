from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_
from src.models import Module, Route, Role
from src.schemas import ModuleCreate, ModuleUpdate, ModuleListResponse, RoleInfo
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class ModuleService:
    
    @staticmethod
    def get_all_modules(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        search: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> List[Module]:
        """Get all modules with pagination and filters, sorted by priority"""
        try:
            query = db.query(Module).options(joinedload(Module.roles))
            
            # Apply search filter
            if search:
                search_term = f"%{search}%"
                query = query.filter(
                    or_(
                        Module.name.ilike(search_term),
                        Module.label.ilike(search_term),
                        Module.route.ilike(search_term)
                    )
                )
            
            # Apply active filter
            if is_active is not None:
                query = query.filter(Module.is_active == is_active)
            
            return query.order_by(Module.priority).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting modules: {e}")
            return []
    
    @staticmethod
    def get_all_modules_with_count(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        search: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> List[ModuleListResponse]:
        """Get all modules with route count and filters, sorted by priority"""
        try:
            query = db.query(
                Module.id,
                Module.name,
                Module.label,
                Module.icon,
                Module.route,
                Module.is_active,
                Module.priority,
                Module.created_at,
                func.count(Route.id).label('route_count')
            ).outerjoin(Route).group_by(Module.id)
            
            # Apply search filter
            if search:
                search_term = f"%{search}%"
                query = query.filter(
                    or_(
                        Module.name.ilike(search_term),
                        Module.label.ilike(search_term),
                        Module.route.ilike(search_term)
                    )
                )
            
            # Apply active filter
            if is_active is not None:
                query = query.filter(Module.is_active == is_active)
            
            modules = query.order_by(Module.priority).offset(skip).limit(limit).all()
            
            # Get roles for each module
            result = []
            for module in modules:
                # Get roles for this module
                module_obj = db.query(Module).options(joinedload(Module.roles)).filter(Module.id == module.id).first()
                roles = [RoleInfo(id=role.id, name=role.name, description=role.description).model_dump() for role in module_obj.roles] if module_obj and module_obj.roles else []
                
                result.append(ModuleListResponse(
                    id=module.id,
                    name=module.name,
                    label=module.label,
                    icon=module.icon,
                    route=module.route,
                    priority=module.priority,
                    is_active=module.is_active,
                    created_at=module.created_at,
                    route_count=module.route_count or 0,
                    roles=roles
                ))
            
            return result
        except Exception as e:
            logger.error(f"Error getting modules with count: {e}")
            return []
    
    @staticmethod
    def get_module_count(
        db: Session,
        search: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> int:
        """Get total count of modules with optional filters"""
        try:
            query = db.query(Module)
            if search:
                search_term = f"%{search}%"
                query = query.filter(
                    or_(
                        Module.name.ilike(search_term),
                        Module.label.ilike(search_term),
                        Module.route.ilike(search_term)
                    )
                )
            if is_active is not None:
                query = query.filter(Module.is_active == is_active)
            return query.count()
        except Exception as e:
            logger.error(f"Error getting module count: {e}")
            return 0
    
    @staticmethod
    def get_module_by_id(db: Session, module_id: int) -> Optional[Module]:
        """Get module by ID"""
        try:
            return db.query(Module).filter(Module.id == module_id).first()
        except Exception as e:
            logger.error(f"Error getting module by ID: {e}")
            return None
    
    @staticmethod
    def get_module_by_name(db: Session, name: str) -> Optional[Module]:
        """Get module by name"""
        try:
            return db.query(Module).filter(Module.name == name).first()
        except Exception as e:
            logger.error(f"Error getting module by name: {e}")
            return None
    
    @staticmethod
    def get_active_modules(db: Session) -> List[Module]:
        """Get all active modules"""
        try:
            return db.query(Module).filter(Module.is_active == True).order_by(Module.priority).all()
        except Exception as e:
            logger.error(f"Error getting active modules: {e}")
            return []
    
    @staticmethod
    def create_module(db: Session, module_data: ModuleCreate) -> Module:
        """Create a new module"""
        try:
            logger.info(f"Starting module creation with data: {module_data.dict()}")
            
            # Check if module name already exists
            existing_module = db.query(Module).filter(Module.name == module_data.name).first()
            if existing_module:
                logger.error(f"Module name '{module_data.name}' already exists")
                raise ValueError(f"Module name '{module_data.name}' already exists")
            
            # Create module first without roles
            db_module = Module(
                name=module_data.name,
                label=module_data.label,
                icon=module_data.icon,
                route=module_data.route,
                priority=module_data.priority,
                is_active=module_data.is_active
            )
            
            db.add(db_module)
            db.flush()  # This will assign an ID to the module without committing
            logger.info(f"Module created with ID: {db_module.id}")
            
            # Now handle role assignments if provided
            if module_data.role_ids:
                logger.info(f"Validating role IDs: {module_data.role_ids}")
                roles = db.query(Role).filter(Role.id.in_(module_data.role_ids)).all()
                found_role_ids = [role.id for role in roles]
                missing_role_ids = set(module_data.role_ids) - set(found_role_ids)
                
                if missing_role_ids:
                    logger.error(f"Role IDs not found: {sorted(missing_role_ids)}")
                    raise ValueError(f"Role IDs not found: {sorted(missing_role_ids)}")
                
                # Assign roles to the module
                db_module.roles = roles
                logger.info(f"Assigned {len(roles)} roles to module: {[role.name for role in roles]}")
            
            db.commit()
            logger.info("Database committed successfully")
            
            db.refresh(db_module)
            logger.info(f"Module refreshed with final data")
            
            # Load the module with all relationships for return
            created_module = db.query(Module).options(
                joinedload(Module.roles)
            ).filter(Module.id == db_module.id).first()
            
            if not created_module:
                logger.error("Failed to retrieve created module")
                raise ValueError("Failed to create module - could not retrieve created object")
            
            logger.info(f"Module created successfully: {created_module.name} (ID: {created_module.id}) with {len(created_module.roles)} roles assigned")
            return created_module
            
        except ValueError as ve:
            db.rollback()
            logger.error(f"Validation error creating module: {ve}")
            raise ve
        except Exception as e:
            db.rollback()
            logger.error(f"Unexpected error creating module: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise ValueError(f"Failed to create module: {str(e)}")
    
    @staticmethod
    def update_module(db: Session, module_id: int, module_update: ModuleUpdate) -> Optional[Module]:
        """Update module"""
        try:
            logger.info(f"Starting module update for ID: {module_id}")
            
            db_module = db.query(Module).options(joinedload(Module.roles)).filter(Module.id == module_id).first()
            if not db_module:
                logger.error(f"Module with ID {module_id} not found")
                return None
            
            # Check if new name already exists (if name is being updated)
            if module_update.name and module_update.name != db_module.name:
                existing_module = db.query(Module).filter(
                    Module.name == module_update.name,
                    Module.id != module_id
                ).first()
                if existing_module:
                    logger.error(f"Module name '{module_update.name}' already exists")
                    raise ValueError(f"Module name '{module_update.name}' already exists")
            
            # Update basic fields first
            update_data = module_update.dict(exclude_unset=True, exclude={'role_ids'})
            for field, value in update_data.items():
                if hasattr(db_module, field):
                    setattr(db_module, field, value)
                    logger.info(f"Updated field {field} to {value}")
            
            # Handle role assignments if provided
            if module_update.role_ids is not None:
                if module_update.role_ids:  # If list is not empty
                    logger.info(f"Validating role IDs: {module_update.role_ids}")
                    roles = db.query(Role).filter(Role.id.in_(module_update.role_ids)).all()
                    found_role_ids = [role.id for role in roles]
                    missing_role_ids = set(module_update.role_ids) - set(found_role_ids)
                    
                    if missing_role_ids:
                        logger.error(f"Role IDs not found: {sorted(missing_role_ids)}")
                        raise ValueError(f"Role IDs not found: {sorted(missing_role_ids)}")
                    
                    db_module.roles = roles
                    logger.info(f"Updated module roles to: {[role.name for role in roles]}")
                else:  # Empty list means remove all roles
                    db_module.roles = []
                    logger.info("Removed all roles from module")
            
            db.commit()
            logger.info("Module update committed successfully")
            
            db.refresh(db_module)
            logger.info(f"Module updated successfully: {db_module.name}")
            
            return db_module
            
        except ValueError as ve:
            db.rollback()
            logger.error(f"Validation error updating module: {ve}")
            raise ve
        except Exception as e:
            db.rollback()
            logger.error(f"Unexpected error updating module: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise ValueError(f"Failed to update module: {str(e)}")
    
    @staticmethod
    def delete_module(db: Session, module_id: int) -> bool:
        """Delete module"""
        try:
            db_module = db.query(Module).filter(Module.id == module_id).first()
            if not db_module:
                return False
            
            # Check if module has routes
            route_count = db.query(Route).filter(Route.module_id == module_id).count()
            if route_count > 0:
                raise ValueError(f"Cannot delete module '{db_module.name}' because it has {route_count} associated routes")
            
            db.delete(db_module)
            db.commit()
            
            logger.info(f"Module deleted: {db_module.name}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting module: {e}")
            raise
    
    @staticmethod
    def bulk_delete_modules(db: Session, module_ids: list[int]) -> int:
        """Bulk delete modules by IDs. Returns number of deleted modules."""
        if not module_ids:
            logger.warning("No module IDs provided for bulk delete")
            return 0

        try:
            logger.info(f"Starting bulk delete for module IDs: {module_ids}")
            deleted_count = 0

            for module_id in module_ids:
                try:
                    module = db.query(Module).filter(Module.id == module_id).first()
                    if module:
                        # Check if module has routes
                        route_count = db.query(Route).filter(Route.module_id == module_id).count()
                        if route_count > 0:
                            logger.warning(f"Cannot delete module ID {module_id} - has {route_count} associated routes")
                            continue
                        
                        # Delete the module
                        db.delete(module)
                        deleted_count += 1
                        logger.info(f"Deleted module ID: {module_id}")
                    else:
                        logger.warning(f"Module ID {module_id} not found")
                        
                except Exception as e:
                    logger.error(f"Error deleting module ID {module_id}: {e}")
                    continue

            db.commit()
            logger.info(f"Bulk delete completed successfully: {deleted_count} modules deleted")
            return deleted_count

        except Exception as e:
            db.rollback()
            logger.error(f"Error bulk deleting modules: {e}")
            return 0
    
    @staticmethod
    def toggle_module_status(db: Session, module_id: int) -> Optional[Module]:
        """Toggle module active status"""
        try:
            db_module = db.query(Module).filter(Module.id == module_id).first()
            if not db_module:
                return None
            
            db_module.is_active = not db_module.is_active
            db.commit()
            db.refresh(db_module)
            
            logger.info(f"Module status toggled: {db_module.name} -> {db_module.is_active}")
            return db_module
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error toggling module status: {e}")
            raise