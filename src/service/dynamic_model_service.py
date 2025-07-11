from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float, JSON
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from src.models import DynamicModel, DynamicField
from src.schemas import DynamicModelCreate, DynamicModelUpdate, DynamicFieldCreate
from src.config.database import Base, engine

logger = logging.getLogger(__name__)

class DynamicModelService:
    
    @staticmethod
    def create_dynamic_model(db: Session, model_data: DynamicModelCreate) -> DynamicModel:
        """Create a new dynamic model and its database table"""
        try:
            # Create the model record
            db_model = DynamicModel(
                name=model_data.name,
                table_name=model_data.table_name,
                description=model_data.description,
                is_active=model_data.is_active
            )
            
            db.add(db_model)
            db.flush()  # Get the ID without committing
            
            # Create field records
            for field_data in model_data.fields:
                db_field = DynamicField(
                    name=field_data.name,
                    field_type=field_data.field_type,
                    is_required=field_data.is_required,
                    is_unique=field_data.is_unique,
                    default_value=field_data.default_value,
                    max_length=field_data.max_length,
                    field_order=field_data.field_order,
                    validation_rules=field_data.validation_rules,
                    model_id=db_model.id
                )
                db.add(db_field)
            
            db.commit()
            
            # Create the actual database table
            DynamicModelService._create_database_table(db_model, model_data.fields)
            
            # Refresh to get all relationships
            db.refresh(db_model)
            
            logger.info(f"Dynamic model created: {db_model.name}")
            return db_model
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating dynamic model: {e}")
            raise ValueError(f"Failed to create dynamic model: {str(e)}")
    
    @staticmethod
    def _create_database_table(model: DynamicModel, fields: List[DynamicFieldCreate]):
        """Create the actual database table for the dynamic model"""
        try:
            # Create table definition
            table_name = f"dynamic_{model.table_name}"
            
            # Start with base columns
            columns = [
                Column('id', Integer, primary_key=True, index=True),
                Column('created_at', DateTime(timezone=True), server_default=func.now()),
                Column('updated_at', DateTime(timezone=True), onupdate=func.now())
            ]
            
            # Add dynamic fields
            for field in fields:
                col_type = DynamicModelService._get_sqlalchemy_type(field.field_type, field.max_length)
                column = Column(
                    field.name,
                    col_type,
                    nullable=not field.is_required,
                    unique=field.is_unique,
                    default=field.default_value if field.default_value else None
                )
                columns.append(column)
            
            # Create table class dynamically
            table_class = type(
                f"Dynamic{model.name}",
                (Base,),
                {
                    '__tablename__': table_name,
                    **{col.name: col for col in columns}
                }
            )
            
            # Create table in database
            table_class.__table__.create(engine, checkfirst=True)
            
            logger.info(f"Database table created: {table_name}")
            
        except Exception as e:
            logger.error(f"Error creating database table: {e}")
            raise
    
    @staticmethod
    def _get_sqlalchemy_type(field_type: str, max_length: Optional[int] = None):
        """Convert field type string to SQLAlchemy type"""
        type_mapping = {
            'string': String(max_length or 255),
            'text': Text,
            'integer': Integer,
            'float': Float,
            'boolean': Boolean,
            'datetime': DateTime(timezone=True),
            'json': JSON
        }
        
        return type_mapping.get(field_type, String(255))
    
    @staticmethod
    def get_all_dynamic_models(db: Session) -> List[DynamicModel]:
        """Get all dynamic models"""
        return db.query(DynamicModel).filter(DynamicModel.is_active == True).all()
    
    @staticmethod
    def get_dynamic_model_by_id(db: Session, model_id: int) -> Optional[DynamicModel]:
        """Get dynamic model by ID"""
        return db.query(DynamicModel).filter(DynamicModel.id == model_id).first()
    
    @staticmethod
    def get_dynamic_model_by_name(db: Session, name: str) -> Optional[DynamicModel]:
        """Get dynamic model by name"""
        return db.query(DynamicModel).filter(DynamicModel.name == name).first()
    
    @staticmethod
    def update_dynamic_model(db: Session, model_id: int, update_data: DynamicModelUpdate) -> Optional[DynamicModel]:
        """Update dynamic model"""
        db_model = db.query(DynamicModel).filter(DynamicModel.id == model_id).first()
        if not db_model:
            return None
        
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(db_model, field, value)
        
        db.commit()
        db.refresh(db_model)
        return db_model
    
    @staticmethod
    def delete_dynamic_model(db: Session, model_id: int) -> bool:
        """Delete dynamic model and its table"""
        db_model = db.query(DynamicModel).filter(DynamicModel.id == model_id).first()
        if not db_model:
            return False
        
        try:
            # Drop the database table
            table_name = f"dynamic_{db_model.table_name}"
            with engine.connect() as conn:
                conn.execute(f"DROP TABLE IF EXISTS {table_name}")
                conn.commit()
            
            # Delete the model record
            db.delete(db_model)
            db.commit()
            
            logger.info(f"Dynamic model deleted: {db_model.name}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting dynamic model: {e}")
            return False