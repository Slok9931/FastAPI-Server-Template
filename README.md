# 🚀 FastAPI Dynamic RBAC System

A comprehensive, production-ready backend application built with **FastAPI**, **PostgreSQL**, and **SQLAlchemy** implementing a dynamic Role-Based Access Control (RBAC) system. This template provides secure authentication, flexible permission management, comprehensive user administration, and modular route management.

## ⭐ **Why Choose This Template?**

- 🏗️ **Production-Ready Architecture** - Clean, scalable, and maintainable code structure
- 🔐 **Advanced Security** - JWT authentication, password hashing, rate limiting, security headers
- 🛡️ **Dynamic RBAC** - Create roles and permissions on-demand without hardcoding
- 📊 **Comprehensive API** - Full CRUD operations for all entities with pagination
- 🐳 **Docker-First** - Containerized with optimized builds and development workflow
- 📝 **Auto-Documentation** - Interactive API docs with Swagger UI and ReDoc
- 🔧 **Highly Configurable** - Environment-based configuration for all aspects
- 🧪 **Test-Ready** - Structured for easy testing with pytest integration

---

## ✨ **Complete Feature Set**

### 🔐 **Authentication & Security**
- **JWT Authentication** with access and refresh tokens
- **Secure Password Hashing** using bcrypt with salt rounds
- **Password Complexity Validation** (length, uppercase, lowercase, numbers, special chars)
- **Rate Limiting** per endpoint with configurable limits
- **Security Headers Middleware** (HSTS, CSP, X-Frame-Options, etc.)
- **CORS Configuration** with customizable origins and methods
- **Token Refresh Mechanism** for seamless user experience
- **Session Management** with token blacklisting
- **Account Lockout Protection** after failed login attempts

### 👥 **Advanced User Management**
- **User Registration** with email validation
- **User Authentication** with username/email login
- **Profile Management** with comprehensive user data
- **Account Activation/Deactivation** for user lifecycle management
- **Password Change** with old password verification
- **User Role Assignment** with multiple roles per user
- **User Search & Filtering** with pagination support
- **User Activity Tracking** with login/logout logs
- **Bulk User Operations** for administrative tasks

### 🛡️ **Dynamic Role-Based Access Control (RBAC)**
- **Dynamic Role Creation** - Create roles on-demand via API
- **Granular Permissions** - Fine-grained access control (resource:action format)
- **Permission Inheritance** - Roles can inherit permissions from other roles
- **Role Hierarchies** - Support for role-based hierarchies
- **Permission Categories** - Organize permissions by resources (user, role, permission, module, route)
- **Built-in Role Templates** - Predefined roles (SuperAdmin, Admin, User, Guest)
- **Role Assignment API** - Add/remove roles from users dynamically
- **Permission Checking Decorators** - Easy-to-use permission validation
- **Contextual Permissions** - Check permissions based on resource ownership

### 🗺️ **Module & Route Management System**
- **Dynamic Module Creation** - Organize features into logical modules
- **Hierarchical Route Structure** - Parent-child route relationships
- **Sidebar Menu Management** - Control navigation visibility
- **Route Permissions** - Granular access control per route
- **Module-based Organization** - Group related routes by modules
- **Route Status Management** - Enable/disable routes dynamically
- **Navigation Tree Generation** - Automatic menu structure creation
- **Route Metadata** - Icons, labels, and descriptions for UI integration

### 📊 **Comprehensive API Features**
- **RESTful API Design** following industry best practices
- **Interactive Documentation** with Swagger UI at `/docs`
- **Alternative Documentation** with ReDoc at `/redoc`
- **Comprehensive Error Handling** with detailed error responses
- **Request/Response Validation** using Pydantic v2
- **Pagination Support** with configurable limits and offsets
- **Search & Filtering** across all major entities
- **Bulk Operations** for administrative efficiency
- **API Versioning** support with prefix configuration
- **Response Caching** for improved performance

### 🗄️ **Advanced Database Features**
- **PostgreSQL Integration** with SQLAlchemy ORM
- **Database Migrations** with Alembic support
- **Connection Pooling** for optimal performance
- **Transaction Management** with rollback support
- **Database Seeding** with initial data setup
- **Soft Delete Support** for data preservation
- **Audit Trails** for tracking changes
- **Database Health Checks** with monitoring endpoints
- **Backup Integration** ready for production

### 🐳 **DevOps & Deployment Excellence**
- **Docker Containerization** with multi-stage builds
- **Docker Compose** for development and production
- **pgAdmin Integration** for database management
- **Optimized Docker Images** with security best practices
- **Environment-based Configuration** for different deployments
- **Health Check Endpoints** for monitoring
- **Logging Configuration** with rotation and levels
- **Production-ready** configurations and optimizations

---

## 🏗️ **Complete Project Architecture**

```
fastapi-backend/
├── 📁 src/                           # Main application source code
│   ├── 🐍 main.py                    # FastAPI application entry point
│   ├── 🐍 __init__.py                # Package initialization with centralized imports
│   │
│   ├── 📁 config/                    # Configuration management
│   │   ├── 🐍 __init__.py            # Centralized config exports
│   │   ├── 🐍 database.py            # Database connection & session management
│   │   └── 🐍 settings.py            # Environment variables & app settings
│   │
│   ├── 📁 models/                    # SQLAlchemy database models
│   │   ├── 🐍 __init__.py            # Centralized model exports
│   │   ├── 🐍 user.py                # User model with relationships
│   │   ├── 🐍 role.py                # Role model with permissions
│   │   ├── 🐍 permission.py          # Permission model with actions/resources
│   │   ├── 🐍 module.py              # Module model for feature organization
│   │   ├── 🐍 route.py               # Route model with hierarchical structure
│   │   ├── 🐍 user_role.py           # User-Role association table
│   │   └── 🐍 role_permission.py     # Role-Permission association table
│   │
│   ├── 📁 schemas/                   # Pydantic request/response models
│   │   ├── 🐍 __init__.py            # Centralized schema exports
│   │   ├── 🐍 user.py                # User validation schemas
│   │   ├── 🐍 role.py                # Role validation schemas
│   │   ├── 🐍 permission.py          # Permission validation schemas
│   │   ├── 🐍 module.py              # Module validation schemas
│   │   └── 🐍 route.py               # Route validation schemas
│   │
│   ├── 📁 api/                       # FastAPI route handlers
│   │   ├── 🐍 __init__.py            # Centralized router exports
│   │   ├── 🐍 auth.py                # Authentication endpoints (login, register, refresh)
│   │   ├── 🐍 users.py               # User CRUD operations
│   │   ├── 🐍 roles.py               # Role management endpoints
│   │   ├── 🐍 permissions.py         # Permission management endpoints
│   │   ├── 🐍 modules.py             # Module management endpoints
│   │   └── 🐍 routes.py              # Route management endpoints
│   │
│   ├── 📁 service/                   # Business logic layer
│   │   ├── 🐍 __init__.py            # Centralized service exports
│   │   ├── 🐍 auth_service.py        # Authentication business logic
│   │   ├── 🐍 user_service.py        # User management operations
│   │   ├── 🐍 role_service.py        # Role management operations
│   │   ├── 🐍 permission_service.py  # Permission management operations
│   │   ├── 🐍 module_service.py      # Module management operations
│   │   └── 🐍 route_service.py       # Route management operations
│   │
│   ├── 📁 core/                      # Core utilities and security
│   │   ├── 🐍 __init__.py            # Centralized core exports
│   │   ├── 🐍 security.py            # Password hashing, JWT tokens, encryption
│   │   └── 🐍 permissions.py         # Permission checking decorators and utilities
│   │
│   └── 📁 middleware/                # Custom middleware
│       ├── 🐍 __init__.py            # Centralized middleware exports
│       ├── 🐍 auth.py                # Authentication middleware
│       ├── 🐍 rate_limiting.py       # Rate limiting middleware
│       └── 🐍 security_headers.py    # Security headers middleware
│
├── 📁 tests/                         # Test suite (pytest)
│   ├── 🐍 __init__.py
│   ├── 🧪 test_auth.py              # Authentication tests
│   ├── 🧪 test_users.py             # User management tests
│   ├── 🧪 test_roles.py             # Role management tests
│   └── 🧪 conftest.py               # Test configuration and fixtures
│
├── 📁 logs/                          # Application logs
│   └── 📄 security.log               # Security-related logs
│
├── 📁 migrations/                    # Alembic database migrations
│   ├── 📁 versions/                  # Migration version files
│   ├── 🐍 env.py                     # Migration environment
│   └── 📄 alembic.ini                # Alembic configuration
│
├── 🐳 Dockerfile                     # Docker image configuration
├── 🐳 docker-compose.yml             # Docker services orchestration
├── 🐳 docker-compose.yml.example     # Docker template for customization
├── 🚫 .dockerignore                  # Docker build exclusions
├── 📋 requirements.txt               # Python dependencies
├── 🐍 init_db.py                     # Database initialization script
├── 🔧 .env.example                   # Environment variables template
├── 🔧 .env                           # Your environment configuration (gitignored)
├── 🚫 .gitignore                     # Git ignore rules
└── 📚 README.md                      # This comprehensive documentation
```

---

## 🚀 **Quick Start Guide**

### **Prerequisites**
- 🐳 **Docker** and **Docker Compose** (recommended)
- 🐍 **Python 3.11+** (for manual setup)
- 🐘 **PostgreSQL 13+** (for manual setup)
- 🌐 **Git** for cloning the repository

### **🎯 Option 1: Docker Setup (Recommended)**

#### **1. Clone and Setup**
```bash
# Clone the repository
git clone <your-repository-url>
cd fastapi-backend

# Copy environment configuration
cp .env.example .env

# Edit configuration (optional - defaults work for development)
nano .env
```

#### **2. Start with Docker**
```bash
# Start all services (FastAPI + PostgreSQL + pgAdmin)
docker-compose up --build

# Or run in background
docker-compose up -d --build

# View logs
docker-compose logs -f fastapi
```

#### **3. Initialize Database**
```bash
# Database is automatically initialized on first run
# Or manually initialize:
docker-compose exec fastapi python init_db.py
```

### **🎯 Option 2: Manual Setup**

#### **1. Environment Setup**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### **2. Database Setup**
```bash
# Install and setup PostgreSQL
sudo apt-get install postgresql postgresql-contrib  # Ubuntu/Debian
# brew install postgresql  # macOS

# Create database
sudo -u postgres createdb fastapi_db

# Update .env with your database URL
echo "DATABASE_URL=postgresql://username:password@localhost:5432/fastapi_db" >> .env
```

#### **3. Run Application**
```bash
# Initialize database
python init_db.py

# Start the application
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 🌐 **Access Your Application**

After successful startup, access these URLs:

| **Service** | **URL** | **Description** |
|-------------|---------|-----------------|
| 🚀 **API** | http://localhost:8000 | Main application API |
| 📚 **Swagger UI** | http://localhost:8000/docs | Interactive API documentation |
| 📖 **ReDoc** | http://localhost:8000/redoc | Alternative API documentation |
| 💾 **pgAdmin** | http://localhost:5050 | Database management interface |
| ❤️ **Health Check** | http://localhost:8000/health | Application health status |

### **🗃️ pgAdmin Access**
- **Email**: `admin@gmail.com`
- **Password**: `admin123`

---

## 🔐 **Default System Accounts**

The system creates these accounts during initialization:

### **🦸 Super Admin**
- **Username**: `superadmin`
- **Email**: `superadmin@gmail.com`
- **Password**: `superadmin123`
- **Permissions**: All system permissions

### **👤 Test User**
- **Username**: `testuser`
- **Email**: `testuser@gmail.com`
- **Password**: `testuser123`
- **Permissions**: Basic user permissions

> ⚠️ **Security Note**: Change these passwords immediately in production!

---

## 📚 **Complete API Reference**

### **🔐 Authentication Endpoints**
| **Method** | **Endpoint** | **Description** | **Auth Required** |
|------------|--------------|-----------------|-------------------|
| `POST` | `/api/v1/auth/register` | Register new user | ❌ |
| `POST` | `/api/v1/auth/login` | User login | ❌ |
| `POST` | `/api/v1/auth/refresh` | Refresh access token | ❌ |
| `POST` | `/api/v1/auth/logout` | User logout | ✅ |
| `POST` | `/api/v1/auth/change-password` | Change user password | ✅ |

### **👥 User Management Endpoints**
| **Method** | **Endpoint** | **Description** | **Permission Required** |
|------------|--------------|-----------------|-------------------------|
| `GET` | `/api/v1/users/` | List users (paginated) | `user:read` |
| `GET` | `/api/v1/users/{user_id}` | Get user details | `user:read` |
| `GET` | `/api/v1/users/me` | Get current user profile | Authentication |
| `POST` | `/api/v1/users/` | Create new user | `user:create` |
| `PUT` | `/api/v1/users/{user_id}` | Update user | `user:update` |
| `DELETE` | `/api/v1/users/{user_id}` | Delete user | `user:delete` |
| `POST` | `/api/v1/users/{user_id}/roles/{role_id}` | Add role to user | `user:update` |
| `DELETE` | `/api/v1/users/{user_id}/roles/{role_id}` | Remove role from user | `user:update` |
| `PATCH` | `/api/v1/users/{user_id}/toggle-status` | Toggle user active status | `user:update` |

### **🛡️ Role Management Endpoints**
| **Method** | **Endpoint** | **Description** | **Permission Required** |
|------------|--------------|-----------------|-------------------------|
| `GET` | `/api/v1/roles/` | List all roles | `role:read` |
| `GET` | `/api/v1/roles/{role_id}` | Get role details | `role:read` |
| `POST` | `/api/v1/roles/` | Create role with permissions | `role:create` |
| `POST` | `/api/v1/roles/create-minimal` | Create role with minimal permissions | `role:create` |
| `PUT` | `/api/v1/roles/{role_id}` | Update role | `role:update` |
| `DELETE` | `/api/v1/roles/{role_id}` | Delete role | `role:delete` |
| `POST` | `/api/v1/roles/{role_id}/permissions/{permission_id}` | Add permission to role | `role:update` |
| `DELETE` | `/api/v1/roles/{role_id}/permissions/{permission_id}` | Remove permission from role | `role:update` |
| `PATCH` | `/api/v1/roles/{role_id}/toggle-status` | Toggle role active status | `role:update` |

### **🔑 Permission Management Endpoints**
| **Method** | **Endpoint** | **Description** | **Permission Required** |
|------------|--------------|-----------------|-------------------------|
| `GET` | `/api/v1/permissions/` | List all permissions | `permission:read` |
| `GET` | `/api/v1/permissions/{permission_id}` | Get permission details | `permission:read` |
| `POST` | `/api/v1/permissions/` | Create new permission | `permission:create` |
| `PUT` | `/api/v1/permissions/{permission_id}` | Update permission | `permission:update` |
| `DELETE` | `/api/v1/permissions/{permission_id}` | Delete permission | `permission:delete` |
| `GET` | `/api/v1/permissions/by-resource/{resource}` | Get permissions by resource | `permission:read` |
| `PATCH` | `/api/v1/permissions/{permission_id}/toggle-status` | Toggle permission status | `permission:update` |

### **📦 Module Management Endpoints**
| **Method** | **Endpoint** | **Description** | **Permission Required** |
|------------|--------------|-----------------|-------------------------|
| `GET` | `/api/v1/modules/` | List all modules | `module:read` |
| `GET` | `/api/v1/modules/{module_id}` | Get module details | `module:read` |
| `POST` | `/api/v1/modules/` | Create new module | `module:create` |
| `PUT` | `/api/v1/modules/{module_id}` | Update module | `module:update` |
| `DELETE` | `/api/v1/modules/{module_id}` | Delete module | `module:delete` |
| `PATCH` | `/api/v1/modules/{module_id}/toggle-status` | Toggle module status | `module:update` |
| `GET` | `/api/v1/modules/{module_id}/routes` | Get routes for module | `module:read` |

### **🗺️ Route Management Endpoints**
| **Method** | **Endpoint** | **Description** | **Permission Required** |
|------------|--------------|-----------------|-------------------------|
| `GET` | `/api/v1/routes/` | List routes (with filtering) | `route:read` |
| `GET` | `/api/v1/routes/{route_id}` | Get route details | `route:read` |
| `GET` | `/api/v1/routes/sidebar` | Get sidebar menu routes | Authentication |
| `POST` | `/api/v1/routes/` | Create new route | `route:create` |
| `PUT` | `/api/v1/routes/{route_id}` | Update route | `route:update` |
| `DELETE` | `/api/v1/routes/{route_id}` | Delete route | `route:delete` |
| `PATCH` | `/api/v1/routes/{route_id}/toggle-status` | Toggle route status | `route:update` |
| `PATCH` | `/api/v1/routes/{route_id}/toggle-sidebar` | Toggle sidebar visibility | `route:update` |
| `GET` | `/api/v1/routes/module/{module_id}` | Get routes by module | `route:read` |
| `GET` | `/api/v1/routes/parent/{parent_id}/children` | Get child routes | `route:read` |
| `GET` | `/api/v1/routes/top-level` | Get top-level routes | `route:read` |

---

## 🛠️ **Configuration Guide**

### **📋 Environment Variables (.env)**

```bash
# 🗄️ Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/fastapi_db
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# 🔐 Security Configuration
SECRET_KEY=your-super-secret-key-here-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# 🚀 Application Settings
APP_NAME=FastAPI Dynamic RBAC System
APP_DESCRIPTION=A comprehensive FastAPI backend with dynamic RBAC
APP_VERSION=1.0.0
ENVIRONMENT=development
DEBUG=true
API_PREFIX=/api/v1

# 🌐 CORS Configuration
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:8080"]
ALLOW_CREDENTIALS=true
ALLOWED_METHODS=["GET", "POST", "PUT", "DELETE", "PATCH"]
ALLOWED_HEADERS=["*"]

# 📊 Feature Flags
DOCS_ENABLED=true
USER_REGISTRATION_ENABLED=true
EMAIL_VALIDATION_ENABLED=true
RATE_LIMIT_ENABLED=true
SECURITY_HEADERS_ENABLED=true

# 🔒 Security Settings
PASSWORD_MIN_LENGTH=8
PASSWORD_REQUIRE_UPPERCASE=true
PASSWORD_REQUIRE_LOWERCASE=true
PASSWORD_REQUIRE_NUMBERS=true
PASSWORD_REQUIRE_SPECIAL=true

# 📈 Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# 📝 Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/security.log
LOG_ROTATION=7 days
LOG_MAX_SIZE=10MB

# 📧 Email Configuration (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=noreply@yourapp.com
```

### **🐳 Docker Configuration**

#### **Production docker-compose.yml**
```yaml
version: '3.8'

services:
  fastapi:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - DEBUG=false
      - DOCS_ENABLED=false
    volumes:
      - ./logs:/app/logs
    depends_on:
      - postgres
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: fastapi_db
      POSTGRES_USER: fastapi_user
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U fastapi_user -d fastapi_db"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  postgres_data:
```

---

## 🎯 **How to Use This Template**

### **🚀 For New Projects**

#### **1. Template Setup**
```bash
# Clone the template
git clone <template-repository-url> my-new-project
cd my-new-project

# Remove git history and start fresh
rm -rf .git
git init
git add .
git commit -m "Initial commit from FastAPI RBAC template"

# Add your remote repository
git remote add origin <your-repository-url>
git push -u origin main
```

#### **2. Customize for Your Project**
```bash
# Update configuration
cp .env.example .env
# Edit .env with your specific values

# Update application metadata
# Edit src/config/settings.py
# Update docker-compose.yml
# Modify README.md
```

#### **3. Add Your Business Logic**
```bash
# Create new models
touch src/models/your_model.py

# Create corresponding schemas
touch src/schemas/your_model.py

# Create service layer
touch src/service/your_service.py

# Create API endpoints
touch src/api/your_endpoints.py

# Register new router in src/main.py
```

### **🏭 For Enterprise Applications**

#### **1. Multi-Environment Setup**
```bash
# Create environment-specific configs
cp .env.example .env.development
cp .env.example .env.staging
cp .env.example .env.production

# Create docker-compose files for each environment
cp docker-compose.yml docker-compose.staging.yml
cp docker-compose.yml docker-compose.production.yml
```

#### **2. Add Custom Modules**
```python
# Example: Adding a Customer Management Module

# 1. Create the model
# src/models/customer.py
class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True)
    # ... other fields

# 2. Create schemas
# src/schemas/customer.py
class CustomerCreate(BaseModel):
    name: str
    email: EmailStr
    # ... other fields

# 3. Create service
# src/service/customer_service.py
class CustomerService:
    @staticmethod
    def create_customer(db: Session, customer_data: CustomerCreate):
        # Implementation
        pass

# 4. Create API endpoints
# src/api/customers.py
@router.post("/", response_model=CustomerResponse)
async def create_customer(
    customer_data: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission("customer", "create"))
):
    # Implementation
    pass

# 5. Register in main.py
from src.api.customers import router as customers_router
app.include_router(customers_router, prefix="/api/v1/customers", tags=["Customers"])
```

### **🔧 For Existing Projects**

#### **1. Integration Steps**
```bash
# Copy authentication system
cp -r src/core/ your-project/src/
cp -r src/models/user.py your-project/src/models/
cp -r src/models/role.py your-project/src/models/
cp -r src/models/permission.py your-project/src/models/

# Copy API endpoints
cp -r src/api/auth.py your-project/src/api/
cp -r src/api/users.py your-project/src/api/
cp -r src/api/roles.py your-project/src/api/

# Copy services
cp -r src/service/ your-project/src/

# Update your main.py to include the routers
```

#### **2. Database Migration**
```bash
# Generate migration for new tables
alembic revision --autogenerate -m "Add RBAC tables"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# Migration history
alembic history

# Current version
alembic current
```

---

## 🧪 **Testing Guide**

### **🚀 Running Tests**
```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov httpx

# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_auth.py

# Run specific test
pytest tests/test_auth.py::test_login_success

# Run tests with verbose output
pytest -v

# Run tests in parallel
pytest -n auto
```

### **📝 Writing Tests**
```python
# tests/test_your_feature.py
import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.config.database import get_db

client = TestClient(app)

def test_your_endpoint():
    # Login to get token
    login_data = {"username": "testuser", "password": "testuser123"}
    response = client.post("/api/v1/auth/login", json=login_data)
    token = response.json()["access_token"]
    
    # Test your endpoint
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/your-endpoint", headers=headers)
    
    assert response.status_code == 200
    assert "expected_field" in response.json()
```

---

## 📊 **Production Deployment**

### **🛡️ Security Checklist**
- [ ] 🔑 Change all default passwords
- [ ] 🎯 Set strong `SECRET_KEY` (32+ characters)
- [ ] 🗄️ Configure production database with SSL
- [ ] 🔒 Enable HTTPS/TLS with valid certificates
- [ ] 🚫 Disable debug mode (`DEBUG=false`)
- [ ] 📚 Disable API docs in production (`DOCS_ENABLED=false`)
- [ ] 🛡️ Enable security headers
- [ ] 🚦 Configure rate limiting
- [ ] 📝 Set up log monitoring and rotation
- [ ] 🔄 Configure database backups
- [ ] 🚨 Set up error monitoring (Sentry, etc.)

### **🐳 Production Docker Setup**
```bash
# Build production image
docker build -t my-fastapi-app:latest .

# Run with production compose
docker-compose -f docker-compose.production.yml up -d

# Monitor logs
docker-compose logs -f fastapi

# Health check
curl -f http://localhost:8000/health
```

### **☸️ Kubernetes Deployment**
```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fastapi-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: fastapi-app
  template:
    metadata:
      labels:
        app: fastapi-app
    spec:
      containers:
      - name: fastapi
        image: my-fastapi-app:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: app-secret
              key: secret-key
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

---

## 🔄 **Database Management**

### **📊 Migrations**
```bash
# Initialize Alembic (if not already done)
alembic init migrations

# Generate migration
alembic revision --autogenerate -m "Add new table"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# Migration history
alembic history

# Current version
alembic current
```

### **💾 Backup & Restore**
```bash
# Backup database
docker-compose exec postgres pg_dump -U fastapi_user fastapi_db > backup.sql

# Restore database
docker-compose exec -T postgres psql -U fastapi_user fastapi_db < backup.sql

# Automated backup script
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec postgres pg_dump -U fastapi_user fastapi_db > "$BACKUP_DIR/backup_$DATE.sql"
find $BACKUP_DIR -name "backup_*.sql" -mtime +7 -delete
```

---

## 📈 **Monitoring & Observability**

### **📊 Health Checks**
The application provides comprehensive health check endpoints:

```bash
# Basic health check
curl http://localhost:8000/health

# Detailed health with database status
curl http://localhost:8000/health/detailed

# Metrics endpoint (if enabled)
curl http://localhost:8000/metrics
```

### **📝 Logging**
```python
# Custom logging in your code
import logging

logger = logging.getLogger(__name__)

def your_function():
    logger.info("Function called")
    logger.error("Error occurred", exc_info=True)
    logger.warning("Warning message")
```

### **🚨 Error Monitoring**
```python
# Add Sentry integration (optional)
# pip install sentry-sdk[fastapi]

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FastApiIntegration()],
    traces_sample_rate=1.0,
)
```

---

## 🤝 **Contributing**

### **🔄 Development Workflow**
1. 🍴 Fork the repository
2. 🌿 Create a feature branch (`git checkout -b feature/amazing-feature`)
3. 💾 Commit your changes (`git commit -m 'Add amazing feature'`)
4. 📤 Push to the branch (`git push origin feature/amazing-feature`)
5. 🔀 Open a Pull Request

### **📋 Code Standards**
- 🐍 Follow PEP 8 style guidelines
- 📝 Add docstrings to all functions and classes
- 🧪 Write tests for new features
- 📊 Maintain test coverage above 80%
- 🔍 Use type hints throughout the codebase

### **🧪 Testing Requirements**
```bash
# Run full test suite before submitting PR
pytest --cov=src --cov-report=term-missing

# Check code style
flake8 src/
black --check src/
isort --check-only src/

# Type checking
mypy src/
```

---

## 🆘 **Troubleshooting**

### **🐳 Docker Issues**
```bash
# Clean Docker environment
docker-compose down -v
docker system prune -af
docker volume prune -f

# Rebuild without cache
docker-compose build --no-cache

# Check container logs
docker-compose logs fastapi
docker-compose logs postgres
```

### **🗄️ Database Issues**
```bash
# Test database connection
docker-compose exec fastapi python -c "
from src.config.database import test_database_connection
result = test_database_connection()
print('✅ Connection successful' if result else '❌ Connection failed')
"

# Reset database
docker-compose down -v
docker-compose up -d postgres
sleep 10
docker-compose exec fastapi python init_db.py
```

### **🔐 Authentication Issues**
```bash
# Check JWT token
python -c "
import jwt
token = 'your-jwt-token-here'
secret = 'your-secret-key'
try:
    payload = jwt.decode(token, secret, algorithms=['HS256'])
    print('✅ Token valid:', payload)
except jwt.ExpiredSignatureError:
    print('❌ Token expired')
except jwt.InvalidTokenError:
    print('❌ Token invalid')
"

# Reset user password
docker-compose exec fastapi python -c "
from src.config.database import SessionLocal
from src.service.user_service import UserService
from src.core.security import get_password_hash

db = SessionLocal()
user = UserService.get_user_by_username(db, 'username')
user.hashed_password = get_password_hash('new_password')
db.commit()
print('✅ Password reset successful')
"
```

### **🚀 Performance Issues**
```bash
# Monitor resource usage
docker stats

# Check slow queries
docker-compose exec postgres psql -U fastapi_user -d fastapi_db -c "
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;
"

# Enable query logging
# Add to docker-compose.yml postgres environment:
# POSTGRES_INITDB_ARGS: "-c log_statement=all"
```

---

## 🔮 **Future Roadmap**

### **🎯 Upcoming Features**
- [ ] 🔐 **OAuth2 Integration** (Google, GitHub, Microsoft)
- [ ] 📱 **Multi-Factor Authentication** (TOTP, SMS)
- [ ] 📋 **Audit Logging** with comprehensive activity tracking
- [ ] 🔔 **Real-time Notifications** via WebSocket
- [ ] 👥 **Team Management** with hierarchical organizations
- [ ] 🎨 **UI Components Library** for frontend integration
- [ ] 📊 **Analytics Dashboard** with user activity metrics
- [ ] 🌐 **Multi-language Support** (i18n)
- [ ] 📧 **Email Templates** with customizable notifications
- [ ] 🔄 **Workflow Engine** for business process automation

### **🏗️ Architecture Improvements**
- [ ] 📦 **Microservices** architecture with API Gateway
- [ ] 🚀 **GraphQL** API alongside REST
- [ ] 💾 **Redis** integration for caching and sessions
- [ ] 📨 **Message Queue** (Celery + Redis/RabbitMQ)
- [ ] 🔍 **Full-text Search** with Elasticsearch
- [ ] 📱 **Mobile App** authentication support
- [ ] ☸️ **Kubernetes** deployment manifests
- [ ] 🔄 **CI/CD** pipeline templates
- [ ] 📊 **Prometheus** metrics integration
- [ ] 🚨 **Grafana** dashboard templates

---

## 🏆 **Use Cases & Examples**

### **🏢 Enterprise Applications**
```python
# Multi-tenant SaaS application
class TenantMiddleware:
    async def __call__(self, request: Request, call_next):
        tenant_id = request.headers.get("X-Tenant-ID")
        # Tenant-specific database routing
        request.state.tenant_id = tenant_id
        return await call_next(request)
```

### **🛒 E-commerce Platform**
```python
# Product management with role-based access
@router.post("/products/")
async def create_product(
    product: ProductCreate,
    current_user: User = Depends(has_permission("product", "create"))
):
    # Only users with product:create permission can add products
    pass
```

### **📚 Content Management System**
```python
# Content approval workflow
@router.patch("/articles/{article_id}/approve")
async def approve_article(
    article_id: int,
    current_user: User = Depends(has_permission("article", "approve"))
):
    # Only editors can approve articles
    pass
```

### **🏥 Healthcare Management**
```python
# Patient data access with strict permissions
@router.get("/patients/{patient_id}")
async def get_patient(
    patient_id: int,
    current_user: User = Depends(has_permission("patient", "read"))
):
    # HIPAA compliant access control
    if not current_user.can_access_patient(patient_id):
        raise HTTPException(403, "Access denied")
    pass
```

---

## 📄 **License**

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

### **🤝 MIT License Summary**
- ✅ **Commercial use** allowed
- ✅ **Modification** allowed
- ✅ **Distribution** allowed
- ✅ **Private use** allowed
- ❌ **Liability** - No warranty provided
- ❌ **Warranty** - Software provided "as is"

---

## 🙏 **Acknowledgments**

This template is built with amazing open-source technologies:

- 🚀 **[FastAPI](https://fastapi.tiangolo.com/)** - Modern, fast web framework for building APIs
- 🐘 **[PostgreSQL](https://www.postgresql.org/)** - Advanced open source relational database
- 🗂️ **[SQLAlchemy](https://www.sqlalchemy.org/)** - Python SQL toolkit and ORM
- 🔒 **[Pydantic](https://pydantic-docs.helpmanual.io/)** - Data validation using Python type annotations
- 🐳 **[Docker](https://www.docker.com/)** - Containerization platform
- 🧪 **[pytest](https://pytest.org/)** - Testing framework for Python
- 🔐 **[bcrypt](https://github.com/pyca/bcrypt/)** - Password hashing library
- 🎫 **[PyJWT](https://pyjwt.readthedocs.io/)** - JSON Web Token implementation

---

## 📞 **Support**

### **🆘 Getting Help**
- 📚 **Documentation**: Check this README and `/docs` endpoint
- 🐛 **Issues**: Create an issue on GitHub
- 💬 **Discussions**: Use GitHub Discussions for questions
- 📧 **Email**: [your-email@domain.com](mailto:your-email@domain.com)

### **🔍 Debugging Steps**
1. ✅ Check application logs in `logs/security.log`
2. 🔍 Review Docker container logs
3. 🗄️ Verify database connectivity
4. 🔐 Validate JWT tokens and permissions
5. 📊 Check API documentation at `/docs`

---

**🎉 Built with ❤️ using FastAPI, PostgreSQL, Docker, and modern Python practices.**

**⭐ If this template helped you, please consider giving it a star on GitHub!**

---

*Last updated: December 2024*
*Template version: 2.0.0*