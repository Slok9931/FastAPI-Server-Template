from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from src.config.database import Base

class Permission(Base):
    __tablename__ = 'permissions'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)
    category = Column(String, nullable=True)  # e.g., 'user_management', 'role_management'

    # Many-to-many relationship with roles
    roles = relationship("Role", secondary="role_permissions", back_populates="permissions")

    def __repr__(self):
        return f"<Permission(id={self.id}, name={self.name})>"