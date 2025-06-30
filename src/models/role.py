from sqlalchemy import Column, Integer, String, Boolean, Text
from sqlalchemy.orm import relationship
from src.config.database import Base
from src.models.associations import user_roles, role_permissions

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(Text)
    is_system_role = Column(Boolean, default=False)

    # Relationships
    users = relationship("User", secondary=user_roles, back_populates="roles")
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles", lazy="selectin")
    
    def __repr__(self):
        return f"<Role(id={self.id}, name='{self.name}', system={self.is_system_role})>"
    
    def has_permission(self, permission_name: str) -> bool:
        """Check if role has a specific permission"""
        return any(perm.name == permission_name for perm in self.permissions)
    
    def add_permission(self, permission):
        """Add a permission to this role"""
        if permission not in self.permissions:
            self.permissions.append(permission)
    
    def remove_permission(self, permission):
        """Remove a permission from this role"""
        if permission in self.permissions:
            self.permissions.remove(permission)