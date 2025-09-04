from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from src.models import Module, Route
from src.schemas import ModuleCreate, ModuleUpdate, ModuleListResponse
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
            query = db.query(Module)
            
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
            
            return [
                ModuleListResponse(
                    id=module.id,
                    name=module.name,
                    label=module.label,
                    icon=module.icon,
                    route=module.route,
                    priority=module.priority,
                    is_active=module.is_active,
                    created_at=module.created_at,
                    route_count=module.route_count or 0
                )
                for module in modules
            ]
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
            # Check if module name already exists
            existing_module = db.query(Module).filter(Module.name == module_data.name).first()
            if existing_module:
                raise ValueError(f"Module name '{module_data.name}' already exists")
            
            # Create module
            db_module = Module(
                name=module_data.name,
                label=module_data.label,
                icon=module_data.icon,
                route=module_data.route,
                priority=module_data.priority,
                is_active=module_data.is_active
            )
            
            db.add(db_module)
            db.commit()
            db.refresh(db_module)
            
            logger.info(f"Module created: {db_module.name}")
            return db_module
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating module: {e}")
            raise
    
    @staticmethod
    def update_module(db: Session, module_id: int, module_update: ModuleUpdate) -> Optional[Module]:
        """Update module"""
        try:
            db_module = db.query(Module).filter(Module.id == module_id).first()
            if not db_module:
                return None
            
            # Check if new name already exists (if name is being updated)
            if module_update.name and module_update.name != db_module.name:
                existing_module = db.query(Module).filter(
                    Module.name == module_update.name,
                    Module.id != module_id
                ).first()
                if existing_module:
                    raise ValueError(f"Module name '{module_update.name}' already exists")
            
            # Update fields only if they are provided
            update_data = module_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                if hasattr(db_module, field):
                    setattr(db_module, field, value)
            
            db.commit()
            db.refresh(db_module)
            
            logger.info(f"Module updated: {db_module.name}")
            return db_module
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating module: {e}")
            raise
    
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