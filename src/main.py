import logging
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from api import books_router, reading_session_router
from db.database import Base, engine

# Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(levelname)s:     %(message)s",
# )

# logger = logging.getLogger(__name__)

logger = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """
    Application startup/shutdown lifecycle.
    """

    logger.info("Starting application...")

    # Initialize database
    Base.metadata.create_all(bind=engine)

    logger.info("Database initialized.")

    yield

    logger.info("Shutting down application...")


# FastAPI application
app = FastAPI(
    title="Book Library API",
    description="A simple API for managing a book library",
    version="1.0.0",
    lifespan=lifespan,
)

# Register routers
app.include_router(books_router, prefix="/api/v1")
app.include_router(reading_session_router, prefix="/api/v1")

# Serve static files
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


# Root route - serve the HTML dashboard
@app.get("/", include_in_schema=False)
async def root():
    """Serve the API documentation dashboard"""
    html_file = Path(__file__).parent / "static" / "index.html"
    if html_file.exists():
        return FileResponse(html_file)
    return {"message": "Welcome to Book Library API"}


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    """
    return {
        "status": "ok",
        "service": "book-library-api",
    }


def run():
    """
    Run development server.
    """

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )


if __name__ == "__main__":
    run()
