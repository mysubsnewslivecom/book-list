from .v1.anime import anime_router, dashboard_router, seasons_router, watch_entries_router
from .v1.openweather.routes import router as openweather_forecast_router
from .v1.reading_sessions_routes import router as reading_session_router
from .v1.routes import router as books_router

__all__ = [
    "books_router",
    "reading_session_router",
    "anime_router",
    "dashboard_router",
    "seasons_router",
    "watch_entries_router",
    "openweather_forecast_router",
]
