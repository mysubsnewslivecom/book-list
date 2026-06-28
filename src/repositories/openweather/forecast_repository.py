"""Persistence logic for saving OpenWeatherMap forecast payloads."""

import json
import logging
from datetime import datetime
from typing import Any

from httpx import AsyncClient, HTTPStatusError, QueryParams, RequestError
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from sqlalchemy.orm import Session

from db.models.openweather import (
    City,
    Forecast,
    ForecastClouds,
    ForecastMain,
    ForecastRain,
    ForecastSys,
    ForecastWind,
    WeatherCondition,
)
from utils.config import settings

tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)

# Explicit allow-list of fields we accept from the API's "main" block.
_MAIN_FIELDS = (
    "temp",
    "feels_like",
    "temp_min",
    "temp_max",
    "pressure",
    "sea_level",
    "grnd_level",
    "humidity",
    "temp_kf",
    "dew_point",
)


class OpenWeatherError(Exception):
    """Raised when the OpenWeather API request fails."""


class ForecastRepository:
    """Repository for persisting OpenWeatherMap forecast data."""

    def __init__(self, db: Session):
        self.db = db

    def _get_or_create_city(self, city_data: dict[str, Any]) -> City:
        """Retrieve an existing city or create a new one."""
        city = self.db.get(City, city_data["id"])
        if city:
            return city

        city = City(
            id=city_data["id"],
            name=city_data["name"],
            lat=city_data["coord"]["lat"],
            lon=city_data["coord"]["lon"],
            country=city_data["country"],
            population=city_data.get("population"),
            timezone=city_data.get("timezone"),
        )

        self.db.add(city)
        return city

    def _existing_forecast_timestamps(self, city_id: int) -> set[int]:
        """Fetch all existing forecast timestamps for a city."""
        rows = self.db.query(Forecast.dt).filter_by(city_id=city_id).all()
        return {row.dt for row in rows}

    def _build_forecast(self, city_id: int, forecast_data: dict[str, Any]) -> Forecast:
        """Build a Forecast model from API data."""
        return Forecast(
            city_id=city_id,
            dt=forecast_data["dt"],
            dt_txt=datetime.strptime(
                forecast_data["dt_txt"],
                "%Y-%m-%d %H:%M:%S",
            ),
            visibility=forecast_data.get("visibility"),
            pop=forecast_data.get("pop"),
        )

    def save_forecast(self, payload: dict[str, Any]) -> int:
        """
        Persist an OpenWeatherMap forecast payload.

        Existing forecast entries (same city + timestamp) are skipped.

        Returns:
            Number of newly inserted forecast records.
        """
        with tracer.start_as_current_span("openweather.persist_forecast") as span:
            city_data = payload["city"]

            span.set_attribute("city.id", city_data["id"])
            span.set_attribute("city.name", city_data["name"])
            span.set_attribute(
                "forecast.records_received",
                len(payload["list"]),
            )

            city = self._get_or_create_city(
                city_data,
            )

            known_timestamps = self._existing_forecast_timestamps(
                city.id,
            )

            inserted = 0

            for forecast_data in payload["list"]:
                if forecast_data["dt"] in known_timestamps:
                    continue

                forecast = self._build_forecast(
                    city.id,
                    forecast_data,
                )

                self.db.add(forecast)
                self.db.flush()

                main = forecast_data.get("main", {})

                main_fields = {field: main[field] for field in _MAIN_FIELDS if field in main}

                self.db.add(
                    ForecastMain(
                        forecast_id=forecast.id,
                        **main_fields,
                    )
                )

                if "clouds" in forecast_data:
                    self.db.add(
                        ForecastClouds(
                            forecast_id=forecast.id,
                            all=forecast_data["clouds"]["all"],
                        )
                    )

                if "wind" in forecast_data:
                    wind = forecast_data["wind"]

                    self.db.add(
                        ForecastWind(
                            forecast_id=forecast.id,
                            speed=wind.get("speed"),
                            deg=wind.get("deg"),
                            gust=wind.get("gust"),
                        )
                    )

                if "rain" in forecast_data:
                    self.db.add(
                        ForecastRain(
                            forecast_id=forecast.id,
                            volume_3h=forecast_data["rain"].get("3h"),
                        )
                    )

                if "sys" in forecast_data:
                    self.db.add(
                        ForecastSys(
                            forecast_id=forecast.id,
                            pod=forecast_data["sys"].get("pod"),
                        )
                    )

                for weather in forecast_data.get("weather", []):
                    self.db.add(
                        WeatherCondition(
                            forecast_id=forecast.id,
                            weather_id=weather["id"],
                            main=weather["main"],
                            description=weather["description"],
                            icon=weather["icon"],
                        )
                    )

                known_timestamps.add(forecast_data["dt"])

                inserted += 1
                self.db.commit()

            skipped = len(payload["list"]) - inserted

            span.set_attribute(
                "forecast.inserted",
                inserted,
            )

            span.set_attribute(
                "forecast.skipped",
                skipped,
            )

            logger.info(
                "Saved forecast for city=%s: %d new records, %d already present",
                city.name,
                inserted,
                skipped,
            )

            return inserted

    async def get(self, city: str) -> dict[str, Any]:
        """Fetch the latest forecast from OpenWeather."""

        params = QueryParams(
            {
                "units": "metric",
                "cnt": 12,
                "q": city,
                "appid": settings.openweather.openweather_api_key.get_secret_value(),
            }
        )

        with tracer.start_as_current_span("openweather.fetch_forecast") as span:
            span.set_attribute(
                "weather.location",
                params["q"],
            )

            span.set_attribute(
                "forecast.request_count",
                params["cnt"],
            )

            try:
                async with AsyncClient(timeout=10.0) as client:
                    response = await client.get(
                        settings.openweather.forecast_api,
                        params=params,
                    )

                span.set_attribute(
                    "http.status_code",
                    response.status_code,
                )

                response.raise_for_status()

                payload = response.json()

                span.set_attribute(
                    "forecast.records_returned",
                    len(payload.get("list", [])),
                )

                logger.info(
                    "Successfully fetched forecast for %s",
                    params["q"],
                )

                return payload

            except HTTPStatusError as exc:
                span.record_exception(exc)
                span.set_status(
                    Status(
                        StatusCode.ERROR,
                        f"HTTP {exc.response.status_code}",
                    )
                )

                logger.exception(
                    "OpenWeather API returned %s for %s. Response: %s",
                    exc.response.status_code,
                    params["q"],
                    exc.response.text,
                )

                raise OpenWeatherError(f"OpenWeather API returned {exc.response.status_code}") from exc

            except RequestError as exc:
                span.record_exception(exc)

                span.set_status(
                    Status(
                        StatusCode.ERROR,
                        "connection failed",
                    )
                )

                logger.exception(
                    "Failed to connect to OpenWeather API for %s",
                    params["q"],
                )

                raise OpenWeatherError("Unable to connect to OpenWeather API") from exc

            except ValueError as exc:
                span.record_exception(exc)

                span.set_status(
                    Status(
                        StatusCode.ERROR,
                        "invalid json",
                    )
                )

                logger.exception(
                    "OpenWeather API returned invalid JSON for %s",
                    params["q"],
                )

                raise OpenWeatherError("Invalid response from OpenWeather API") from exc

            except Exception as exc:
                span.record_exception(exc)

                span.set_status(
                    Status(
                        StatusCode.ERROR,
                        str(exc),
                    )
                )

                logger.exception(
                    "Unexpected error while fetching forecast for %s",
                    params["q"],
                )

                raise OpenWeatherError("Unexpected error while fetching forecast") from exc

    def _validate_city(self, city: str):
        return len(city.split(",")) == 2

    async def run(self, city) -> int:
        """Fetch and persist the latest forecast."""

        with tracer.start_as_current_span("openweather.import") as span:
            try:
                if not self._validate_city(city):
                    logger.exception("city input should in 'city,country_code' format")
                    span.set_status(
                        Status(
                            StatusCode.ERROR,
                            "city input should in 'city,country_code' format",
                        )
                    )
                    raise OpenWeatherError("city input should be in 'city,country_code' format")

                payload = await self.get(city)
                span.set_attribute("payload", json.dumps(payload))

                inserted = self.save_forecast(
                    payload,
                )

                span.set_attribute(
                    "forecast.inserted",
                    inserted,
                )

                logger.info(
                    "Forecast import completed successfully (%d records inserted)",
                    inserted,
                )

                return inserted

            except OpenWeatherError as exc:
                span.record_exception(exc)

                span.set_status(
                    Status(
                        StatusCode.ERROR,
                        str(exc),
                    )
                )

                logger.exception("Forecast import failed")

                raise

            except Exception as exc:
                span.record_exception(exc)

                span.set_status(
                    Status(
                        StatusCode.ERROR,
                        str(exc),
                    )
                )

                logger.exception("Unexpected error during forecast import")

                raise
