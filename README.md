# FastAPI Dynamic RBAC System

A comprehensive backend application built with FastAPI, PostgreSQL, and SQLAlchemy implementing a dynamic Role-Based Access Control (RBAC) system. This system provides secure authentication, flexible permission management, and comprehensive user administration.

## ✨ Features

### 🔐 **Authentication & Security**
- JWT-based authentication with access and refresh tokens
- Secure password hashing using bcrypt
- Configurable password complexity requirements
- Rate limiting for API endpoints
- Security headers middleware
- CORS configuration

### 👥 **User Management**
- User registration and authentication
- User profile management
- Account activation/deactivation
- Password change functionality
- Email validation with EmailStr

### 🛡️ **Dynamic Role-Based Access Control**
- **Dynamic Role Creation**: Create roles on-demand without hardcoding
- **Flexible Permission System**: Granular permissions for fine-grained access control
- **Super Admin Role**: Built-in super admin with full system access
- **Default User Role**: Configurable default role for new users
- **Role Assignment**: Assign multiple roles to users
- **Permission Management**: Add/remove permissions from roles dynamically

### 📊 **API Features**
- RESTful API design
- Interactive API documentation (Swagger UI)
- Alternative documentation (ReDoc)
- Comprehensive error handling
- Request/response validation with Pydantic v2
- Pagination support

### 🗄️ **Database**
- PostgreSQL with SQLAlchemy ORM
- Database migrations with Alembic
- Connection pooling and optimization
- Automated database initialization

### 🐳 **DevOps & Deployment**
- Docker containerization with optimized builds
- Docker Compose for multi-service setup
- pgAdmin for database management
- Development and production configurations
- Comprehensive .dockerignore for efficient builds

## 🏗️ **Project Structure**

```
fastapi-backend/
├── src/
│   ├── main.py                    # FastAPI application entry point
│   ├── config/
│   │   ├── database.py            # Database configuration
│   │   └── settings.py            # Application settings
│   ├── models/
│   │   ├── user.py                # User database model
│   │   ├── role.py                # Role database model
│   │   └── permission.py          # Permission database model
│   ├── schemas/
│   │   ├── user.py                # User Pydantic schemas
│   │   ├── role.py                # Role Pydantic schemas
│   │   └── permission.py          # Permission Pydantic schemas
│   ├── api/
│   │   ├── auth.py                # Authentication endpoints
│   │   ├── users.py               # User management endpoints
│   │   ├── roles.py               # Role management endpoints
│   │   └── permissions.py         # Permission management endpoints
│   ├── service/
│   │   ├── user_service.py        # User business logic
│   │   ├── role_service.py        # Role business logic
│   │   └── permission_service.py  # Permission business logic
│   ├── core/
│   │   ├── security.py            # Security utilities
│   │   └── permissions.py         # Permission checking logic
│   └── middleware/
│       └── security_headers.py    # Security headers middleware
├── logs/                          # Application logs
├── requirements.txt               # Python dependencies
├── docker-compose.yml             # Docker services configuration
├── docker-compose.yml.example     # Docker configuration template
├── Dockerfile                     # Docker image configuration
├── .dockerignore                  # Docker build exclusions
├── init_db.py                     # Database initialization script
├── .env.example                   # Environment variables template
├── .gitignore                     # Git ignore rules
└── README.md                      # Project documentation
```

## 🚀 **Quick Start**

### **Prerequisites**
- Docker and Docker Compose
- Git

### **1. Clone the Repository**
```bash
git clone <repository-url>
cd fastapi-backend
```

### **2. Environment Setup**
```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file with your configuration
nano .env
```

### **3. Docker Configuration (Optional)**
```bash
# Copy Docker Compose example if you want to customize
cp docker-compose.yml.example docker-compose.yml

# Edit docker-compose.yml with your preferences
nano docker-compose.yml
```

### **4. Start with Docker**
```bash
# Build and start all services
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

### **5. Initialize Database**
```bash
# The database will be automatically initialized on first run
# Or manually run:
docker-compose exec fastapi python init_db.py
```

### **6. Access the Application**
- **API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **pgAdmin**: http://localhost:5050
  - Email: `admin@gmail.com`
  - Password: `admin123`

## 🐳 **Docker Configuration**

### **Optimized Docker Builds**
The project includes a comprehensive `.dockerignore` file that excludes:
- Development files and documentation
- Version control history
- IDE configurations
- Cache and temporary files
- Environment variables (except .env.example)
- Test and coverage reports
- Log files and backups

This results in:
- ⚡ **Faster builds** (smaller build context)
- 🔒 **Enhanced security** (excludes sensitive files)
- 📦 **Smaller images** (only includes necessary files)
- 🎯 **Reproducible builds** (consistent across environments)

### **Docker Compose Templates**
- `docker-compose.yml` - Main configuration
- `docker-compose.yml.example` - Template with placeholders for customization

### **Container Optimization**
```dockerfile
# Multi-stage builds for production
# Optimized layer caching
# Non-root user execution
# Health checks included
```

## 🔧 **Manual Setup (Without Docker)**

### **1. Environment Setup**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### **2. Database Setup**
```bash
# Install PostgreSQL and create database
createdb fastapi_db

# Update .env with your database URL
DATABASE_URL=postgresql://username:password@localhost:5432/fastapi_db
```

### **3. Run Application**
```bash
# Initialize database
python init_db.py

# Start the application
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## 📚 **API Endpoints**

### **Authentication**
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/logout` - User logout

### **User Management**
- `GET /api/v1/users/` - List users (with pagination)
- `GET /api/v1/users/{user_id}` - Get user details
- `PUT /api/v1/users/{user_id}` - Update user
- `DELETE /api/v1/users/{user_id}` - Delete user
- `POST /api/v1/users/{user_id}/roles/{role_id}` - Add role to user
- `DELETE /api/v1/users/{user_id}/roles/{role_id}` - Remove role from user

### **Role Management**
- `GET /api/v1/roles/` - List roles
- `POST /api/v1/roles/` - Create role with specific permissions
- `POST /api/v1/roles/create-minimal` - Create role with minimal permissions
- `GET /api/v1/roles/{role_id}` - Get role details
- `PUT /api/v1/roles/{role_id}` - Update role
- `DELETE /api/v1/roles/{role_id}` - Delete role
- `POST /api/v1/roles/{role_id}/permissions/{permission_id}` - Add permission to role

### **Permission Management**
- `GET /api/v1/permissions/` - List permissions
- `POST /api/v1/permissions/` - Create permission
- `GET /api/v1/permissions/{permission_id}` - Get permission details
- `PUT /api/v1/permissions/{permission_id}` - Update permission
- `DELETE /api/v1/permissions/{permission_id}` - Delete permission

## 🔐 **Default Credentials**

After initialization, the system creates:

**Super Admin User:**
- Username: `superadmin`
- Email: `superadmin@gmail.com`
- Password: `superadmin123`

**Test User:**
- Username: `testuser`
- Email: `testuser@gmail.com`
- Password: `testuser123`

## 🛠️ **Configuration Files**

### **Environment Configuration**
- `.env.example` - Complete template with all configuration options
- `.env` - Your actual configuration (not tracked by Git)

### **Docker Configuration**
- `docker-compose.yml.example` - Template for custom Docker setup
- `docker-compose.yml` - Your Docker configuration
- `.dockerignore` - Optimizes Docker builds and enhances security

### **Key Configuration Options**
```bash
# Database
DATABASE_URL=postgresql://user:pass@host:port/db

# Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application
ENVIRONMENT=development
DEBUG=true
API_PREFIX=/api/v1

# Features
DOCS_ENABLED=true
USER_REGISTRATION_ENABLED=true
EMAIL_VALIDATION_ENABLED=true
```

See `.env.example` for complete configuration options.

## 🏛️ **Architecture**

### **Permission System**
The system uses a flexible permission-based architecture:

1. **Permissions**: Granular actions (e.g., `read_users`, `manage_roles`)
2. **Roles**: Collections of permissions (e.g., `admin`, `moderator`)
3. **Users**: Can have multiple roles

### **Dynamic Role Creation**
- Roles can be created dynamically via API
- Two creation methods:
  - **Minimal**: Creates role with safe default permissions
  - **Full**: Creates role with specified permissions

### **Security Features**
- Password complexity validation
- Rate limiting per endpoint
- JWT token management
- CORS configuration
- Security headers

## 🧪 **Testing**

```bash
# Run tests
docker-compose exec fastapi pytest

# Run with coverage
docker-compose exec fastapi pytest --cov=src

# Run specific test
docker-compose exec fastapi pytest tests/test_auth.py
```

## 📊 **Monitoring & Logging**

- Application logs in `logs/security.log`
- Configurable log levels and rotation
- Health check endpoint: `/health`
- Performance monitoring ready

## 🔄 **Database Migrations**

```bash
# Generate migration
docker-compose exec fastapi alembic revision --autogenerate -m "description"

# Apply migrations
docker-compose exec fastapi alembic upgrade head

# Migration history
docker-compose exec fastapi alembic history
```

## 📈 **Scaling & Production**

### **Production Checklist**
- [ ] Change default passwords
- [ ] Set strong `SECRET_KEY`
- [ ] Configure production database
- [ ] Enable security headers
- [ ] Set up SSL/TLS
- [ ] Configure rate limiting
- [ ] Set up monitoring
- [ ] Configure backup strategy
- [ ] Optimize Docker images for production

### **Environment Settings**
```bash
ENVIRONMENT=production
DEBUG=false
SECURITY_HEADERS_ENABLED=true
DOCS_ENABLED=false  # Disable in production
```

### **Docker Production Optimizations**
- Multi-stage builds for smaller images
- Non-root user execution
- Health checks and restart policies
- Resource limits and constraints
- Secrets management

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 **License**

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 **Troubleshooting**

### **Common Issues**

**Docker Build Issues:**
```bash
# Clean Docker environment
docker-compose down -v
docker system prune -af
docker-compose up --build
```

**Database Connection:**
```bash
# Check database logs
docker-compose logs postgres

# Test connection
docker-compose exec fastapi python -c "from src.config.database import test_database_connection; test_database_connection()"
```

**Permission Errors:**
- Ensure you're using a user with appropriate permissions
- Check JWT token validity
- Verify role assignments

### **Docker Optimization**
- Use `.dockerignore` to exclude unnecessary files
- Leverage Docker layer caching
- Use multi-stage builds for production
- Monitor image sizes with `docker images`

### **Support**
- Check the API documentation at `/docs`
- Review application logs in `logs/`
- Create an issue on GitHub

---

## 🎯 **Use Cases**

This template is perfect for:
- **Multi-tenant Applications**: Different roles for different organizations
- **Content Management Systems**: Fine-grained content permissions
- **E-commerce Platforms**: Customer, vendor, and admin roles
- **Enterprise Applications**: Department-based access control
- **API Services**: Service-to-service authentication

## 🔮 **Roadmap**

- [ ] OAuth2 integration (Google, GitHub)
- [ ] Multi-factor authentication
- [ ] Audit logging
- [ ] Real-time notifications
- [ ] API rate limiting per user
- [ ] Advanced permission inheritance
- [ ] Role templates
- [ ] Permission bundles
- [ ] Kubernetes deployment manifests
- [ ] CI/CD pipeline templates

---

**Built with ❤️ using FastAPI, PostgreSQL, Docker, and modern Python practices.**