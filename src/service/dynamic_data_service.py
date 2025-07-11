from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import logging
import json
from datetime import datetime

from src.models import DynamicModel
from src.schemas import DynamicDataCreate, DynamicDataUpdate
from src.config.database import engine

logger = logging.getLogger(__name__)

class DynamicDataService:
    
    @staticmethod
    def create_record(db: Session, model_id: int, data: DynamicDataCreate) -> Dict[str, Any]:
        """Create a new record in dynamic table"""
        try:
            # Get model definition
            model = db.query(DynamicModel).filter(DynamicModel.id == model_id).first()
            if not model:
                raise ValueError("Dynamic model not found")
            
            table_name = f"dynamic_{model.table_name}"
            
            # Validate and prepare data
            validated_data = DynamicDataService._validate_data(db, model, data.data)
            
            # Build INSERT query
            columns = list(validated_data.keys())
            placeholders = [f":{col}" for col in columns]
            
            query = f"""
                INSERT INTO {table_name} ({', '.join(columns)})
                VALUES ({', '.join(placeholders)})
            """
            
            # Execute query
            with engine.connect() as conn:
                result = conn.execute(text(query), validated_data)
                record_id = result.lastrowid
                conn.commit()
            
            # Return created record
            return DynamicDataService.get_record(db, model_id, record_id)
            
        except Exception as e:
            logger.error(f"Error creating dynamic record: {e}")
            raise ValueError(f"Failed to create record: {str(e)}")
    
    @staticmethod
    def get_all_records(db: Session, model_id: int, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all records from dynamic table"""
        try:
            model = db.query(DynamicModel).filter(DynamicModel.id == model_id).first()
            if not model:
                raise ValueError("Dynamic model not found")
            
            table_name = f"dynamic_{model.table_name}"
            
            query = f"SELECT * FROM {table_name} ORDER BY id DESC LIMIT {limit} OFFSET {skip}"
            
            with engine.connect() as conn:
                result = conn.execute(text(query))
                records = []
                for row in result:
                    record = dict(row._mapping)
                    records.append(record)
                
                return records
                
        except Exception as e:
            logger.error(f"Error getting dynamic records: {e}")
            raise ValueError(f"Failed to get records: {str(e)}")
    
    @staticmethod
    def get_record(db: Session, model_id: int, record_id: int) -> Optional[Dict[str, Any]]:
        """Get single record from dynamic table"""
        try:
            model = db.query(DynamicModel).filter(DynamicModel.id == model_id).first()
            if not model:
                raise ValueError("Dynamic model not found")
            
            table_name = f"dynamic_{model.table_name}"
            
            query = f"SELECT * FROM {table_name} WHERE id = :id"
            
            with engine.connect() as conn:
                result = conn.execute(text(query), {"id": record_id})
                row = result.fetchone()
                if row:
                    return dict(row._mapping)
                return None
                
        except Exception as e:
            logger.error(f"Error getting dynamic record: {e}")
            raise ValueError(f"Failed to get record: {str(e)}")
    
    @staticmethod
    def update_record(db: Session, model_id: int, record_id: int, data: DynamicDataUpdate) -> Optional[Dict[str, Any]]:
        """Update record in dynamic table"""
        try:
            model = db.query(DynamicModel).filter(DynamicModel.id == model_id).first()
            if not model:
                raise ValueError("Dynamic model not found")
            
            table_name = f"dynamic_{model.table_name}"
            
            # Validate and prepare data
            validated_data = DynamicDataService._validate_data(db, model, data.data, is_update=True)
            
            # Build UPDATE query
            set_clauses = [f"{col} = :{col}" for col in validated_data.keys()]
            query = f"""
                UPDATE {table_name}
                SET {', '.join(set_clauses)}, updated_at = :updated_at
                WHERE id = :id
            """
            
            validated_data['updated_at'] = datetime.utcnow()
            validated_data['id'] = record_id
            
            with engine.connect() as conn:
                result = conn.execute(text(query), validated_data)
                if result.rowcount == 0:
                    return None
                conn.commit()
            
            return DynamicDataService.get_record(db, model_id, record_id)
            
        except Exception as e:
            logger.error(f"Error updating dynamic record: {e}")
            raise ValueError(f"Failed to update record: {str(e)}")
    
    @staticmethod
    def delete_record(db: Session, model_id: int, record_id: int) -> bool:
        """Delete record from dynamic table"""
        try:
            model = db.query(DynamicModel).filter(DynamicModel.id == model_id).first()
            if not model:
                raise ValueError("Dynamic model not found")
            
            table_name = f"dynamic_{model.table_name}"
            
            query = f"DELETE FROM {table_name} WHERE id = :id"
            
            with engine.connect() as conn:
                result = conn.execute(text(query), {"id": record_id})
                conn.commit()
                return result.rowcount > 0
                
        except Exception as e:
            logger.error(f"Error deleting dynamic record: {e}")
            raise ValueError(f"Failed to delete record: {str(e)}")
    
    @staticmethod
    def _validate_data(db: Session, model: DynamicModel, data: Dict[str, Any], is_update: bool = False) -> Dict[str, Any]:
        """Validate data against model fields"""
        validated_data = {}
        
        for field in model.fields:
            value = data.get(field.name)
            
            # Check required fields
            if field.is_required and value is None and not is_update:
                raise ValueError(f"Field '{field.name}' is required")
            
            # Skip None values for updates
            if value is None and is_update:
                continue
            
            # Type validation and conversion
            if value is not None:
                validated_value = DynamicDataService._convert_value(value, field.field_type)
                validated_data[field.name] = validated_value
        
        return validated_data
    
    @staticmethod
    def _convert_value(value: Any, field_type: str) -> Any:
        """Convert value to appropriate type"""
        try:
            if field_type == 'integer':
                return int(value)
            elif field_type == 'float':
                return float(value)
            elif field_type == 'boolean':
                if isinstance(value, str):
                    return value.lower() in ('true', '1', 'yes', 'on')
                return bool(value)
            elif field_type == 'json':
                if isinstance(value, str):
                    return json.loads(value)
                return value
            else:  # string, text, datetime
                return str(value)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid value for field type {field_type}: {value}")