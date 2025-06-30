from sqlalchemy.orm import Session
from src.config.database import SessionLocal, engine, Base
from src.models.user import User
from src.models.role import Role
from src.models.permission import Permission
from src.core.security import get_password_hash
from src.config.settings import settings

def init_database():
    """Initialize database with tables and default data"""
    print("🚀 Initializing FastAPI Dynamic RBAC Database...")
    
    # Create all tables
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")
    
    db = SessionLocal()
    
    try:
        # Check if database is already initialized
        existing_permissions = db.query(Permission).first()
        if existing_permissions:
            print("⚠️  Database already initialized. Skipping initialization.")
            return
        
        print("Creating default permissions...")
        
        # Create permissions directly without using service layer
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
        
        # Create permission objects
        permission_objects = []
        for perm_data in permissions_data:
            permission = Permission(**perm_data)
            db.add(permission)
            permission_objects.append(permission)
            print(f"  ✅ Created permission: {perm_data['name']}")
        
        # Commit permissions first
        db.commit()
        print(f"✅ Created {len(permissions_data)} permissions")
        
        print("Creating default roles...")
        
        # Get all permissions for super admin
        all_permissions = db.query(Permission).all()
        
        # Create super admin role with all permissions
        super_admin_role = Role(
            name=settings.super_admin_role,
            description="Super administrator with full system access",
            is_system_role=True
        )
        super_admin_role.permissions = all_permissions
        db.add(super_admin_role)
        print(f"  ✅ Created super admin role with {len(all_permissions)} permissions")
        
        # Create default user role with minimal permissions
        minimal_permission_names = ["update_own_profile", "view_content"]
        minimal_permissions = db.query(Permission).filter(
            Permission.name.in_(minimal_permission_names)
        ).all()
        
        default_role = Role(
            name=settings.default_user_role,
            description="Default role for regular users with minimal permissions",
            is_system_role=True
        )
        default_role.permissions = minimal_permissions
        db.add(default_role)
        print(f"  ✅ Created default user role with {len(minimal_permissions)} permissions")
        
        # Commit roles
        db.commit()
        
        print("Creating default users...")
        
        # Create super admin user
        super_admin_user = User(
            username="superadmin",
            email="superadmin@gmail.com",
            hashed_password=get_password_hash("superadmin123"),
            is_active=True
        )
        super_admin_user.roles = [super_admin_role]
        db.add(super_admin_user)
        print(f"  ✅ Created super admin user: {super_admin_user.username}")
        
        # Create test user
        test_user = User(
            username="testuser",
            email="testuser@gmail.com",
            hashed_password=get_password_hash("testuser123"),
            is_active=True
        )
        test_user.roles = [default_role]
        db.add(test_user)
        print(f"  ✅ Created test user: {test_user.username}")
        
        # Final commit
        db.commit()
        
        print("\n🎉 Database initialization completed successfully!")
        print("\n📋 Default Credentials:")
        print("  🔐 Super Admin:")
        print("    Username: superadmin")
        print("    Password: superadmin123")
        print("    Email: superadmin@example.com")
        print("    Permissions: ALL")
        print("\n  👤 Test User:")
        print("    Username: testuser")
        print("    Password: testuser123")
        print("    Email: testuser@example.com")
        print("    Permissions: update_own_profile, view_content")
        
        print("\n🌐 Access URLs:")
        print("  📱 API: http://localhost:8000")
        print("  📚 API Docs: http://localhost:8000/docs")
        print("  🔄 Alternative Docs: http://localhost:8000/redoc")
        print("  💚 Health Check: http://localhost:8000/health")
        
        print("\n🛡️ System Roles:")
        print(f"  📋 Super Admin Role: {settings.super_admin_role}")
        print(f"  👥 Default User Role: {settings.default_user_role}")
        
        print("\n✨ Features:")
        print("  🔹 Dynamic role creation via API")
        print("  🔹 New roles get minimal permissions by default")
        print("  🔹 Use API endpoints to add more permissions")
        print("  🔹 Comprehensive RBAC system ready!")
        
    except Exception as e:
        print(f"❌ Error during database initialization: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def check_database_status():
    """Check if database is properly initialized"""
    print("🔍 Checking database status...")
    
    db = SessionLocal()
    try:
        # Check tables exist and have data
        permission_count = db.query(Permission).count()
        role_count = db.query(Role).count()
        user_count = db.query(User).count()
        
        print(f"📊 Database Status:")
        print(f"  Permissions: {permission_count}")
        print(f"  Roles: {role_count}")
        print(f"  Users: {user_count}")
        
        if permission_count > 0 and role_count > 0 and user_count > 0:
            print("✅ Database is properly initialized!")
            return True
        else:
            print("⚠️  Database appears to be incomplete")
            return False
            
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    try:
        # Initialize database
        init_database()
        
        # Verify initialization
        print("\n" + "="*50)
        check_database_status()
        
        print("\n🚀 FastAPI Dynamic RBAC System is ready!")
        print("You can now start using the API endpoints.")
        
    except Exception as e:
        print(f"\n❌ Database initialization failed: {e}")
        exit(1)