from sqlalchemy.orm import Session
from src.config.database import SessionLocal, engine, Base
from src.models.user import User
from src.models.role import Role
from src.models.permission import Permission
from src.core.security import get_password_hash
from src.config.settings import settings
from src.service.role_service import RoleService

def init_database():
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Check if permissions already exist
        existing_permissions = db.query(Permission).first()
        if existing_permissions:
            print("Database already initialized")
            return
        
        # Create permissions
        permissions_data = [
            # User Management
            {"name": "create_user", "description": "Create new users", "category": "user_management"},
            {"name": "get_users", "description": "View all users", "category": "user_management"},
            {"name": "get_user", "description": "View user details", "category": "user_management"},
            {"name": "update_user", "description": "Update user information", "category": "user_management"},
            {"name": "delete_user", "description": "Delete users", "category": "user_management"},
            {"name": "update_own_profile", "description": "Update own profile", "category": "user_management"},
            
            # Role Management
            {"name": "manage_roles", "description": "Create, update, delete roles", "category": "role_management"},
            {"name": "view_roles", "description": "View roles", "category": "role_management"},
            
            # Permission Management
            {"name": "manage_permissions", "description": "Create, update, delete permissions", "category": "permission_management"},
            {"name": "view_permissions", "description": "View permissions", "category": "permission_management"},
            
            # Content Management
            {"name": "moderate_content", "description": "Moderate user content", "category": "content_management"},
            {"name": "view_content", "description": "View content", "category": "content_management"},
            {"name": "create_content", "description": "Create content", "category": "content_management"},
            {"name": "edit_content", "description": "Edit content", "category": "content_management"},
            {"name": "delete_content", "description": "Delete content", "category": "content_management"},
            
            # System Administration
            {"name": "system_admin", "description": "Full system administration", "category": "system"},
            {"name": "view_analytics", "description": "View system analytics", "category": "system"},
            {"name": "manage_settings", "description": "Manage system settings", "category": "system"},
        ]
        
        # Create permissions
        for perm_data in permissions_data:
            permission = Permission(**perm_data)
            db.add(permission)
        
        db.commit()
        
        # Create ONLY the super_admin role with all permissions
        super_admin_role = RoleService.ensure_super_admin_exists(db)
        
        # Create default user role with minimal permissions
        default_role = RoleService.get_or_create_default_role(db)
        
        # Create super admin user
        super_admin_user = User(
            username="superadmin",
            email="superadmin@gmail.com",
            hashed_password=get_password_hash("superadmin123")
        )
        super_admin_user.roles = [super_admin_role]
        db.add(super_admin_user)
        
        # Create a default user
        default_user = User(
            username="testuser",
            email="testuser@gmail.com",
            hashed_password=get_password_hash("testuser123")
        )
        default_user.roles = [default_role]
        db.add(default_user)
        
        db.commit()
        
        print("Database initialized with minimal permission system!")
        print(f"Super admin role: {settings.super_admin_role} (all permissions)")
        print(f"Default user role: {settings.default_user_role} (minimal permissions)")
        print("\nCreated users:")
        print(f"  superadmin / superadmin123 (role: {settings.super_admin_role})")
        print(f"  testuser / testuser123 (role: {settings.default_user_role})")
        print("\nAll new roles will be created with minimal permissions!")
        print("Use the API to add additional permissions to roles.")
        
        # Display minimal permissions
        minimal_perms = RoleService._get_minimal_permissions(db)
        print(f"\nMinimal permissions for new roles:")
        for perm in minimal_perms:
            print(f"  - {perm.name}: {perm.description}")
        
    finally:
        db.close()

if __name__ == "__main__":
    init_database()