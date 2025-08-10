from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.config.database import Base

class Module(Base):
    __tablename__ = "modules"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    label = Column(String(100), nullable=False)
    icon = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    route = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    routes = relationship("Route", back_populates="module", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Module(id={self.id}, name='{self.name}', label='{self.label}')>"
    
    class Config:
        from_attributes = True