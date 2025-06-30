from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from src.config.database import Base
from src.models.user_role import user_roles
from src.models.role_permission import role_permissions

class Role(Base):
    __tablename__ = 'roles'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)
    is_system_role = Column(Boolean, default=False)  # Prevent deletion of system roles

    # Many-to-many relationship with users
    users = relationship("User", secondary=user_roles, back_populates="roles")
    
    # Many-to-many relationship with permissions
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")

    def __repr__(self):
        return f"<Role(id={self.id}, name={self.name})>"
    
    def has_permission(self, permission_name: str) -> bool:
        """Check if role has a specific permission"""
        return any(perm.name == permission_name for perm in self.permissions)
    
    def get_permission_names(self) -> list:
        """Get list of permission names for this role"""
        return [perm.name for perm in self.permissions]