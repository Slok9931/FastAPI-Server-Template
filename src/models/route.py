from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.config.database import Base

class Route(Base):
    __tablename__ = "routes"
    
    id = Column(Integer, primary_key=True, index=True)
    route = Column(String(255), nullable=False)
    label = Column(String(100), nullable=False)
    icon = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_sidebar = Column(Boolean, default=True, nullable=False)
    module_id = Column(Integer, ForeignKey("modules.id", ondelete="CASCADE"), nullable=False)
    parent_id = Column(Integer, ForeignKey("routes.id", ondelete="CASCADE"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    module = relationship("Module", back_populates="routes")
    parent = relationship("Route", remote_side=[id], back_populates="children")
    children = relationship("Route", back_populates="parent", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Route(id={self.id}, route='{self.route}', label='{self.label}')>"
    
    class Config:
        from_attributes = True