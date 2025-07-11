# Import all API routers for centralized access
from src.api.auth import router as auth_router
from src.api.users import router as users_router
from src.api.roles import router as roles_router
from src.api.permissions import router as permissions_router
from src.api.modules import router as modules_router
from src.api.routes import router as routes_router
from src.api.dynamic_models import router as dynamic_model_router

# Export all routers
__all__ = [
    "auth_router",
    "users_router",
    "roles_router", 
    "permissions_router",
    "modules_router",
    "routes_router",
    "dynamic_model_router"
]