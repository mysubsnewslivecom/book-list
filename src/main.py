import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from api import books_router
from db.database import Base, engine

# Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(levelname)s:     %(message)s",
# )

# logger = logging.getLogger(__name__)

logger = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(app: FastAPI):
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
app.include_router(books_router)


@app.get("/", tags=["Home"])
async def root():
    """
    Redirect to Swagger docs.
    """
    return RedirectResponse(url="/docs")


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
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )


if __name__ == "__main__":
    run()
