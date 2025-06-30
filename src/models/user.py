from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.config.database import Base
from src.models.user_role import user_roles

class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Many-to-many relationship with roles
    roles = relationship("Role", secondary=user_roles, back_populates="users")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"
    
    def has_role(self, role_name: str) -> bool:
        """Check if user has a specific role"""
        return any(role.name == role_name for role in self.roles)
    
    def get_role_names(self) -> list:
        """Get list of role names for this user"""
        return [role.name for role in self.roles]
    
    def has_permission(self, permission_name: str) -> bool:
        """Check if user has a specific permission through their roles"""
        for role in self.roles:
            if role.has_permission(permission_name):
                return True
        return False
    
    def get_all_permissions(self) -> list:
        """Get all unique permissions from all user's roles"""
        permissions = set()
        for role in self.roles:
            permissions.update(role.get_permission_names())
        return list(permissions)