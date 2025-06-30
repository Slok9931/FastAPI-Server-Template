from sqlalchemy.orm import Session
from src.config.database import SessionLocal, engine
from src.models.user import User
from src.models.role import Role
from src.models.permission import Permission
from src.core.security import get_password_hash
from src.config.settings import settings
import logging

logger = logging.getLogger(__name__)

async def init_database():
    """Initialize database with default data"""
    try:
        # Create database tables
        from src.config.database import Base
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
        # Create default data
        db = SessionLocal()
        try:
            await create_default_permissions(db)
            await create_default_roles(db)
            await create_default_users(db)
            db.commit()
            logger.info("Default data created successfully")
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating default data: {e}")
            raise
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

async def create_default_permissions(db: Session):
    """Create default permissions"""
    default_permissions = [
        # User management
        {"name": "user:read", "description": "Read user information", "category": "user"},
        {"name": "user:create", "description": "Create new users", "category": "user"},
        {"name": "user:update", "description": "Update user information", "category": "user"},
        {"name": "user:delete", "description": "Delete users", "category": "user"},
        
        # Role management
        {"name": "role:read", "description": "Read role information", "category": "role"},
        {"name": "role:create", "description": "Create new roles", "category": "role"},
        {"name": "role:update", "description": "Update role information", "category": "role"},
        {"name": "role:delete", "description": "Delete roles", "category": "role"},
        
        # Permission management
        {"name": "permission:read", "description": "Read permission information", "category": "permission"},
        {"name": "permission:create", "description": "Create new permissions", "category": "permission"},
        {"name": "permission:update", "description": "Update permission information", "category": "permission"},
        {"name": "permission:delete", "description": "Delete permissions", "category": "permission"},
        
        # System administration
        {"name": "system:admin", "description": "Full system administration access", "category": "system"},
        {"name": "system:settings", "description": "Manage system settings", "category": "system"},
        {"name": "system:logs", "description": "View system logs", "category": "system"},
        
        # API access
        {"name": "api:read", "description": "Read access to API", "category": "api"},
        {"name": "api:write", "description": "Write access to API", "category": "api"},
    ]
    
    for perm_data in default_permissions:
        # Check if permission already exists
        existing_permission = db.query(Permission).filter(Permission.name == perm_data["name"]).first()
        if not existing_permission:
            permission = Permission(**perm_data)
            db.add(permission)
            logger.info(f"Created permission: {perm_data['name']}")

async def create_default_roles(db: Session):
    """Create default roles"""
    # Get all permissions for super admin
    all_permissions = db.query(Permission).all()
    
    # Super Admin role
    super_admin_role = db.query(Role).filter(Role.name == "super_admin").first()
    if not super_admin_role:
        super_admin_role = Role(
            name="super_admin",
            description="Super Administrator with full system access",
            is_system_role=True
        )
        super_admin_role.permissions = all_permissions
        db.add(super_admin_role)
        logger.info("Created super_admin role")
    
    # Admin role
    admin_role = db.query(Role).filter(Role.name == "admin").first()
    if not admin_role:
        admin_permissions = db.query(Permission).filter(
            Permission.category.in_(["user", "role", "api"])
        ).all()
        admin_role = Role(
            name="admin",
            description="Administrator with user and role management access",
            is_system_role=True
        )
        admin_role.permissions = admin_permissions
        db.add(admin_role)
        logger.info("Created admin role")
    
    # User role
    user_role = db.query(Role).filter(Role.name == "user").first()
    if not user_role:
        user_permissions = db.query(Permission).filter(
            Permission.name.in_(["user:read", "api:read"])
        ).all()
        user_role = Role(
            name="user",
            description="Default user role with basic permissions",
            is_system_role=True
        )
        user_role.permissions = user_permissions
        db.add(user_role)
        logger.info("Created user role")

async def create_default_users(db: Session):
    """Create default users"""
    # Get roles
    super_admin_role = db.query(Role).filter(Role.name == "super_admin").first()
    admin_role = db.query(Role).filter(Role.name == "admin").first()
    user_role = db.query(Role).filter(Role.name == "user").first()
    
    # Create super admin user
    super_admin = db.query(User).filter(User.username == "superadmin").first()
    if not super_admin:
        super_admin = User(
            username="superadmin",
            email="superadmin@example.com",
            hashed_password=get_password_hash("superadmin123"),
            is_active=True
        )
        if super_admin_role:
            super_admin.roles = [super_admin_role]
        db.add(super_admin)
        logger.info("Created superadmin user")
    
    # Create admin user
    admin_user = db.query(User).filter(User.username == "admin").first()
    if not admin_user:
        admin_user = User(
            username="admin",
            email="admin@example.com",
            hashed_password=get_password_hash("admin123"),
            is_active=True
        )
        if admin_role:
            admin_user.roles = [admin_role]
        db.add(admin_user)
        logger.info("Created admin user")
    
    # Create test user
    test_user = db.query(User).filter(User.username == "testuser").first()
    if not test_user:
        test_user = User(
            username="testuser",
            email="testuser@example.com",
            hashed_password=get_password_hash("testuser123"),
            is_active=True
        )
        if user_role:
            test_user.roles = [user_role]
        db.add(test_user)
        logger.info("Created testuser user")

def init_db_sync():
    """Synchronous version for direct calls"""
    try:
        # Create database tables
        from src.config.database import Base
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
        # Create default data
        db = SessionLocal()
        try:
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            loop.run_until_complete(create_default_permissions(db))
            loop.run_until_complete(create_default_roles(db))
            loop.run_until_complete(create_default_users(db))
            
            db.commit()
            logger.info("Default data created successfully")
            
            loop.close()
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating default data: {e}")
            raise
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise