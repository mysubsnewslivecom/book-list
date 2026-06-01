from .anime_routes import router as anime_router
from .dashboard_routes import router as dashboard_router
from .seasons_routes import router as seasons_router
from .watch_entries import router as watch_entries_router

__all__ = ["anime_router", "seasons_router", "watch_entries_router", "dashboard_router"]
