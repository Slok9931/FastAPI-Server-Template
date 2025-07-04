from sqlalchemy.orm import Session
from sqlalchemy import text
from src.config.database import SessionLocal, engine
from src.models.user import User
from src.models.role import Role
from src.models.permission import Permission
from src.core.security import get_password_hash
import logging

logger = logging.getLogger(__name__)

def create_default_permissions(db: Session):
    """Create only the required standardized permissions"""
    
    # Define only the 3 resources and 4 actions each (12 total)
    resources = ["user", "role", "permission"]
    actions = ["read", "create", "update", "delete"]
    
    # Create standardized permissions for each resource
    for resource in resources:
        for action in actions:
            permission_name = f"{resource}:{action}"
            permission_description = f"{action.title()} {resource} resources"
            
            # Check if permission already exists
            existing_permission = db.query(Permission).filter(Permission.name == permission_name).first()
            if not existing_permission:
                permission = Permission(
                    name=permission_name,
                    description=permission_description,
                    category=resource
                )
                db.add(permission)
                logger.info(f"Created permission: {permission_name}")

def create_default_roles(db: Session):
    """Create default roles"""
    
    # 1. Superadmin role
    superadmin_role = db.query(Role).filter(Role.name == "superadmin").first()
    if not superadmin_role:
        superadmin_role = Role(
            name="superadmin",
            description="Super Administrator with all permissions",
            is_system_role=True
        )
        db.add(superadmin_role)
        logger.info("Created superadmin role")
    
    # 2. Admin role
    admin_role = db.query(Role).filter(Role.name == "admin").first()
    if not admin_role:
        admin_role = Role(
            name="admin",
            description="Administrator with all user permissions",
            is_system_role=True
        )
        db.add(admin_role)
        logger.info("Created admin role")
    
    # 3. User role
    user_role = db.query(Role).filter(Role.name == "user").first()
    if not user_role:
        user_role = Role(
            name="user",
            description="Basic user with read-only access",
            is_system_role=True
        )
        db.add(user_role)
        logger.info("Created user role")

def create_default_users(db: Session):
    """Create default users"""
    
    # Create superadmin user
    superadmin = db.query(User).filter(User.username == "superadmin").first()
    if not superadmin:
        superadmin = User(
            username="superadmin",
            email="superadmin@gmail.com",
            hashed_password=get_password_hash("superadmin123"),
            is_active=True
        )
        db.add(superadmin)
        logger.info("Created superadmin user")
    
    # Create admin user
    admin_user = db.query(User).filter(User.username == "admin").first()
    if not admin_user:
        admin_user = User(
            username="admin",
            email="admin@gmail.com",
            hashed_password=get_password_hash("admin123"),
            is_active=True
        )
        db.add(admin_user)
        logger.info("Created admin user")
    
    # Create basic user
    basic_user = db.query(User).filter(User.username == "user").first()
    if not basic_user:
        basic_user = User(
            username="user",
            email="user@gmail.com",
            hashed_password=get_password_hash("user123"),
            is_active=True
        )
        db.add(basic_user)
        logger.info("Created basic user")

def create_role_permission_associations(db: Session):
    """Create role-permission associations using SQL"""
    
    try:
        # Insert role_permissions for superadmin (all 12 permissions)
        superadmin_query = text("""
            INSERT INTO role_permissions (role_id, permission_id)
            SELECT 
                (SELECT id FROM roles WHERE name = 'superadmin') as role_id,
                p.id as permission_id
            FROM permissions p
            WHERE NOT EXISTS (
                SELECT 1 FROM role_permissions rp 
                WHERE rp.role_id = (SELECT id FROM roles WHERE name = 'superadmin') 
                AND rp.permission_id = p.id
            )
        """)
        db.execute(superadmin_query)
        logger.info("Created role-permission associations for superadmin")
        
        # Insert role_permissions for admin (only user permissions)
        admin_query = text("""
            INSERT INTO role_permissions (role_id, permission_id)
            SELECT 
                (SELECT id FROM roles WHERE name = 'admin') as role_id,
                p.id as permission_id
            FROM permissions p
            WHERE p.name IN ('user:read', 'user:create', 'user:update', 'user:delete')
            AND NOT EXISTS (
                SELECT 1 FROM role_permissions rp 
                WHERE rp.role_id = (SELECT id FROM roles WHERE name = 'admin') 
                AND rp.permission_id = p.id
            )
        """)
        db.execute(admin_query)
        logger.info("Created role-permission associations for admin")
        
        # Insert role_permissions for user (only user:read permission)
        user_query = text("""
            INSERT INTO role_permissions (role_id, permission_id)
            SELECT 
                (SELECT id FROM roles WHERE name = 'user') as role_id,
                p.id as permission_id
            FROM permissions p
            WHERE p.name = 'user:read'
            AND NOT EXISTS (
                SELECT 1 FROM role_permissions rp 
                WHERE rp.role_id = (SELECT id FROM roles WHERE name = 'user') 
                AND rp.permission_id = p.id
            )
        """)
        db.execute(user_query)
        logger.info("Created role-permission associations for user")
        
    except Exception as e:
        logger.error(f"Error creating role-permission associations: {e}")
        raise

def create_user_role_associations(db: Session):
    """Create user-role associations using SQL"""
    
    try:
        # Assign superadmin role to superadmin user
        superadmin_user_query = text("""
            INSERT INTO user_roles (user_id, role_id)
            SELECT 
                (SELECT id FROM users WHERE username = 'superadmin') as user_id,
                (SELECT id FROM roles WHERE name = 'superadmin') as role_id
            WHERE NOT EXISTS (
                SELECT 1 FROM user_roles ur 
                WHERE ur.user_id = (SELECT id FROM users WHERE username = 'superadmin') 
                AND ur.role_id = (SELECT id FROM roles WHERE name = 'superadmin')
            )
        """)
        db.execute(superadmin_user_query)
        logger.info("Assigned superadmin role to superadmin user")
        
        # Assign admin role to admin user
        admin_user_query = text("""
            INSERT INTO user_roles (user_id, role_id)
            SELECT 
                (SELECT id FROM users WHERE username = 'admin') as user_id,
                (SELECT id FROM roles WHERE name = 'admin') as role_id
            WHERE NOT EXISTS (
                SELECT 1 FROM user_roles ur 
                WHERE ur.user_id = (SELECT id FROM users WHERE username = 'admin') 
                AND ur.role_id = (SELECT id FROM roles WHERE name = 'admin')
            )
        """)
        db.execute(admin_user_query)
        logger.info("Assigned admin role to admin user")
        
        # Assign user role to basic user
        basic_user_query = text("""
            INSERT INTO user_roles (user_id, role_id)
            SELECT 
                (SELECT id FROM users WHERE username = 'user') as user_id,
                (SELECT id FROM roles WHERE name = 'user') as role_id
            WHERE NOT EXISTS (
                SELECT 1 FROM user_roles ur 
                WHERE ur.user_id = (SELECT id FROM users WHERE username = 'user') 
                AND ur.role_id = (SELECT id FROM roles WHERE name = 'user')
            )
        """)
        db.execute(basic_user_query)
        logger.info("Assigned user role to basic user")
        
    except Exception as e:
        logger.error(f"Error creating user-role associations: {e}")
        raise

def init_database():
    """Initialize database with default data"""
    try:
        # Create database tables
        from src.config.database import Base
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
        # Create default data
        db = SessionLocal()
        try:
            # Step 1: Create permissions
            create_default_permissions(db)
            db.commit()
            logger.info("Permissions created successfully")
            
            # Step 2: Create roles
            create_default_roles(db)
            db.commit()
            logger.info("Roles created successfully")
            
            # Step 3: Create users
            create_default_users(db)
            db.commit()
            logger.info("Users created successfully")
            
            # Step 4: Create role-permission associations
            create_role_permission_associations(db)
            db.commit()
            logger.info("Role-permission associations created successfully")
            
            # Step 5: Create user-role associations
            create_user_role_associations(db)
            db.commit()
            logger.info("User-role associations created successfully")
            
            # Verify the data was created correctly
            verify_database_data(db)
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating default data: {e}")
            raise
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

def verify_database_data(db: Session):
    """Verify that the database was initialized correctly"""
    
    # Check permissions
    permissions_count = db.query(Permission).count()
    logger.info(f"Total permissions created: {permissions_count}")
    
    # Check roles
    roles_count = db.query(Role).count()
    logger.info(f"Total roles created: {roles_count}")
    
    # Check users
    users_count = db.query(User).count()
    logger.info(f"Total users created: {users_count}")
    
    # Check role-permission associations
    role_perm_query = text("""
        SELECT r.name, COUNT(rp.permission_id) as permission_count 
        FROM roles r 
        LEFT JOIN role_permissions rp ON r.id = rp.role_id 
        GROUP BY r.name
    """)
    role_perm_results = db.execute(role_perm_query).fetchall()
    for result in role_perm_results:
        logger.info(f"Role '{result[0]}' has {result[1]} permissions")
    
    # Check user-role associations
    user_role_query = text("""
        SELECT u.username, COUNT(ur.role_id) as role_count 
        FROM users u 
        LEFT JOIN user_roles ur ON u.id = ur.user_id 
        GROUP BY u.username
    """)
    user_role_results = db.execute(user_role_query).fetchall()
    for result in user_role_results:
        logger.info(f"User '{result[0]}' has {result[1]} roles")

# For direct execution
if __name__ == "__main__":
    init_database()
    print("Database initialized successfully!")