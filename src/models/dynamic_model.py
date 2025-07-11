from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.config.database import Base

class DynamicModel(Base):
    __tablename__ = "dynamic_models"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    table_name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    fields = relationship("DynamicField", back_populates="model", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<DynamicModel(id={self.id}, name='{self.name}', table_name='{self.table_name}')>"
    
    class Config:
        from_attributes = True


class DynamicField(Base):
    __tablename__ = "dynamic_fields"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    field_type = Column(String(50), nullable=False)  # string, integer, boolean, text, datetime, etc.
    is_required = Column(Boolean, default=False, nullable=False)
    is_unique = Column(Boolean, default=False, nullable=False)
    default_value = Column(Text, nullable=True)
    max_length = Column(Integer, nullable=True)
    field_order = Column(Integer, default=0, nullable=False)
    validation_rules = Column(JSON, nullable=True)  # Store validation rules as JSON
    model_id = Column(Integer, ForeignKey("dynamic_models.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    model = relationship("DynamicModel", back_populates="fields")
    
    def __repr__(self):
        return f"<DynamicField(id={self.id}, name='{self.name}', type='{self.field_type}')>"
    
    class Config:
        from_attributes = True