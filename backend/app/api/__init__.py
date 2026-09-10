from .chat import router as chat_router
from .auth import router as auth_router
from .health import router as health_router
from .user import router as user_router
from .sources import router as sources_router

routes = [
    chat_router,
    auth_router,
    health_router,
    user_router,
    sources_router,
]