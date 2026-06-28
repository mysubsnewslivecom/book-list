"""SQLAlchemy ORM models for weather forecast data."""

from sqlalchemy import BigInteger, Column, Date, DateTime, Float, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from db.database import Base
from utils.config import settings


class City(Base):
    __tablename__ = "cities"
    __table_args__ = {"schema": settings.openweather.db_schema}

    id = Column(Integer, primary_key=True)  # OpenWeather city id
    name = Column(String(100), nullable=False)

    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)

    country = Column(String(10), nullable=False)
    population = Column(Integer)
    timezone = Column(Integer)

    forecasts = relationship(
        "Forecast",
        back_populates="city",
        cascade="all, delete-orphan",
    )
    astronomy = relationship(
        "CityAstronomy",
        back_populates="city",
        cascade="all, delete-orphan",
    )


class Forecast(Base):
    __tablename__ = "forecasts"
    __table_args__ = (
        UniqueConstraint("city_id", "dt", name="uq_forecast_city_dt"),
        {"schema": settings.openweather.db_schema},
    )

    id = Column(Integer, primary_key=True, autoincrement=True)

    city_id = Column(
        Integer,
        ForeignKey(f"{settings.openweather.db_schema}.cities.id", ondelete="CASCADE"),
        nullable=False,
    )

    dt = Column(BigInteger, nullable=False)
    dt_txt = Column(DateTime, nullable=False)

    visibility = Column(Integer)
    pop = Column(Float)

    city = relationship("City", back_populates="forecasts")

    main = relationship(
        "ForecastMain",
        uselist=False,
        back_populates="forecast",
        cascade="all, delete-orphan",
    )

    clouds = relationship(
        "ForecastClouds",
        uselist=False,
        back_populates="forecast",
        cascade="all, delete-orphan",
    )

    wind = relationship(
        "ForecastWind",
        uselist=False,
        back_populates="forecast",
        cascade="all, delete-orphan",
    )

    rain = relationship(
        "ForecastRain",
        uselist=False,
        back_populates="forecast",
        cascade="all, delete-orphan",
    )

    sys = relationship(
        "ForecastSys",
        uselist=False,
        back_populates="forecast",
        cascade="all, delete-orphan",
    )

    weather = relationship(
        "WeatherCondition",
        back_populates="forecast",
        cascade="all, delete-orphan",
    )


class ForecastMain(Base):
    __tablename__ = "forecast_main"
    __table_args__ = {"schema": settings.openweather.db_schema}

    forecast_id = Column(
        Integer,
        ForeignKey(f"{settings.openweather.db_schema}.forecasts.id", ondelete="CASCADE"),
        primary_key=True,
    )

    temp = Column(Float)
    feels_like = Column(Float)
    temp_min = Column(Float)
    temp_max = Column(Float)

    pressure = Column(Integer)
    sea_level = Column(Integer)
    grnd_level = Column(Integer)

    humidity = Column(Integer)

    temp_kf = Column(Float)
    dew_point = Column(Float)

    forecast = relationship("Forecast", back_populates="main")


class ForecastClouds(Base):
    __tablename__ = "forecast_clouds"
    __table_args__ = {"schema": settings.openweather.db_schema}

    forecast_id = Column(
        Integer,
        ForeignKey(f"{settings.openweather.db_schema}.forecasts.id", ondelete="CASCADE"),
        primary_key=True,
    )

    all = Column(Integer)

    forecast = relationship("Forecast", back_populates="clouds")


class ForecastWind(Base):
    __tablename__ = "forecast_wind"
    __table_args__ = {"schema": settings.openweather.db_schema}

    forecast_id = Column(
        Integer,
        ForeignKey(f"{settings.openweather.db_schema}.forecasts.id", ondelete="CASCADE"),
        primary_key=True,
    )

    speed = Column(Float)
    deg = Column(Integer)
    gust = Column(Float)

    forecast = relationship("Forecast", back_populates="wind")


class ForecastRain(Base):
    __tablename__ = "forecast_rain"
    __table_args__ = {"schema": settings.openweather.db_schema}

    forecast_id = Column(
        Integer,
        ForeignKey(f"{settings.openweather.db_schema}.forecasts.id", ondelete="CASCADE"),
        primary_key=True,
    )

    volume_3h = Column(Float)

    forecast = relationship("Forecast", back_populates="rain")


class ForecastSys(Base):
    __tablename__ = "forecast_sys"
    __table_args__ = {"schema": settings.openweather.db_schema}

    forecast_id = Column(
        Integer,
        ForeignKey(f"{settings.openweather.db_schema}.forecasts.id", ondelete="CASCADE"),
        primary_key=True,
    )

    pod = Column(String(1))

    forecast = relationship("Forecast", back_populates="sys")


class WeatherCondition(Base):
    __tablename__ = "weather_conditions"
    __table_args__ = {"schema": settings.openweather.db_schema}

    id = Column(Integer, primary_key=True, autoincrement=True)

    forecast_id = Column(
        Integer,
        ForeignKey(f"{settings.openweather.db_schema}.forecasts.id", ondelete="CASCADE"),
        nullable=False,
    )

    weather_id = Column(Integer)
    main = Column(String(50))
    description = Column(String(255))
    icon = Column(String(10))

    forecast = relationship("Forecast", back_populates="weather")


class CityAstronomy(Base):
    __tablename__ = "city_astronomy"
    __table_args__ = (
        UniqueConstraint("city_id", "date", name="uq_astronomy_city_date"),
        {"schema": settings.openweather.db_schema},
    )

    id = Column(Integer, primary_key=True, autoincrement=True)

    city_id = Column(
        Integer, ForeignKey(f"{settings.openweather.db_schema}.cities.id", ondelete="CASCADE"), nullable=False
    )

    date = Column(Date, nullable=False)

    sunrise = Column(BigInteger, nullable=False)
    sunset = Column(BigInteger, nullable=False)

    city = relationship("City", back_populates="astronomy")


class CurrentWeatherJSON(Base):
    __tablename__ = "current_weather_json"
    __table_args__ = (
        UniqueConstraint("city_id", name="uq_current_weather_json_city"),
        Index("ix_current_weather_json_dt", "dt"),
        {"schema": settings.openweather.db_schema},
    )

    id = Column(Integer, primary_key=True, autoincrement=True)

    # normalized fields for fast filtering
    city_id = Column(Integer, nullable=False)
    city_name = Column(String(100))
    country = Column(String(10))

    lat = Column(Float)
    lon = Column(Float)

    dt = Column(BigInteger, nullable=False)
    timezone = Column(Integer)
    cod = Column(Integer)

    # FULL RAW PAYLOAD
    payload = Column(JSONB, nullable=False)
