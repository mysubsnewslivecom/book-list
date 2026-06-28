from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from db.database import get_db
from repositories.book_repository import BookRepository
from repositories.openweather.current_weather_repository import CurrentWeatherRepository
from repositories.openweather.forecast_repository import ForecastRepository
from repositories.reading_session_repository import ReadingSessionRepository
from services.book_service import BookService
from services.openweather.current_weather import CurrentWeatherService
from services.openweather.forecast_service import ForecastService
from services.reading_sessions_service import ReadingSessionService

# ---------------------------------------------------------------------
# DB SESSION
# ---------------------------------------------------------------------
DBSession = Annotated[Session, Depends(get_db)]


# ---------------------------------------------------------------------
# BOOKS
# ---------------------------------------------------------------------
def get_book_repository(db: DBSession) -> BookRepository:
    return BookRepository(db)


BookRepositoryDep = Annotated[BookRepository, Depends(get_book_repository)]


def get_book_service(repo: BookRepositoryDep) -> BookService:
    return BookService(repo)


BookServiceDep = Annotated[BookService, Depends(get_book_service)]


# ---------------------------------------------------------------------
# READING SESSIONS
# ---------------------------------------------------------------------
def get_reading_session_repository(db: DBSession) -> ReadingSessionRepository:
    return ReadingSessionRepository(db)


ReadingSessionRepositoryDep = Annotated[ReadingSessionRepository, Depends(get_reading_session_repository)]


def get_reading_session_service(repo: ReadingSessionRepositoryDep) -> ReadingSessionService:
    return ReadingSessionService(repo)


ReadingSessionServiceDep = Annotated[ReadingSessionService, Depends(get_reading_session_service)]


# ---------------------------------------------------------------------
# OPENWEATHER SESSIONS
# ---------------------------------------------------------------------
def get_forecast_repository(db: DBSession) -> ForecastRepository:
    return ForecastRepository(db)


ForecastRepositoryDep = Annotated[ForecastRepository, Depends(get_forecast_repository)]


def get_forecast_service(repo: ForecastRepositoryDep) -> ForecastService:
    return ForecastService(repo)


ForecastServiceDep = Annotated[ForecastService, Depends(get_forecast_service)]

#


def get_current_weather_repository(db: DBSession) -> CurrentWeatherRepository:
    return CurrentWeatherRepository(db)


CurrentWeatherRepositoryDep = Annotated[CurrentWeatherRepository, Depends(get_current_weather_repository)]


def get_current_weather_service(repo: CurrentWeatherRepositoryDep) -> CurrentWeatherService:
    return CurrentWeatherService(repo)


CurrentWeatherServiceDep = Annotated[CurrentWeatherService, Depends(get_current_weather_service)]
