import logging
from datetime import UTC, datetime, timedelta
from typing import Any

from httpx import AsyncClient, HTTPStatusError, QueryParams, RequestError
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from sqlalchemy.orm import Session

from db.models.openweather import CurrentWeatherJSON
from utils.config import settings

from .forecast_repository import OpenWeatherError

logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")
tracer = trace.get_tracer(__name__)


class CurrentWeatherRepository:
    """
    Repository responsible for:

    - Fetching current weather from OpenWeather
    - Caching results for one hour
    - Persisting JSON payloads
    """

    CACHE_HOURS = 1

    def __init__(self, db: Session):
        self.db = db

    def get(self, city_name: str) -> CurrentWeatherJSON | None:
        return self.db.query(CurrentWeatherJSON).filter(CurrentWeatherJSON.city_name == city_name).one_or_none()

    def _is_stale(self, record: CurrentWeatherJSON | None) -> bool:
        if record is None:
            return True

        last_update = datetime.fromtimestamp(record.dt, tz=UTC)
        return datetime.now(UTC) - last_update > timedelta(hours=self.CACHE_HOURS)

    def should_fetch(self, city_name: int) -> bool:
        return self._is_stale(self.get(city_name))

    def save(self, payload: dict[str, Any]) -> CurrentWeatherJSON:
        city_name = payload["name"]

        obj = self.get(city_name)

        if obj is None:
            logger.debug("Creating weather record city_name=%s", city_name)
            obj = CurrentWeatherJSON(city_id=payload["id"])
            self.db.add(obj)
        else:
            logger.debug("Updating weather record city_name=%s", city_name)

        coord = payload.get("coord", {})
        sys = payload.get("sys", {})

        obj.city_name = payload.get("name")
        obj.country = sys.get("country")

        obj.lat = coord.get("lat")
        obj.lon = coord.get("lon")

        obj.dt = payload.get("dt")
        obj.timezone = payload.get("timezone")
        obj.cod = payload.get("cod")

        obj.payload = payload

        self.db.commit()
        self.db.refresh(obj)

        logger.info(
            "Saved current weather city=%s city_name=%s timestamp=%s",
            obj.city_name,
            obj.city_name,
            obj.dt,
        )

        return obj

    async def _fetch_from_api(self, city_name: str) -> dict[str, Any]:
        """
        Fetch current weather from OpenWeather API.
        """

        params = QueryParams(
            {
                "q": city_name,
                "appid": settings.openweather.openweather_api_key.get_secret_value(),
                "units": "metric",
            }
        )

        with tracer.start_as_current_span("openweather.current.fetch") as span:
            span.set_attribute("weather.city_name", city_name)

            try:
                logger.info("Fetching current weather from OpenWeather city_name=%s", city_name)

                async with AsyncClient(timeout=30) as client:
                    response = await client.get(url=settings.openweather.current_weather_url, params=params)

                response.raise_for_status()

                payload = response.json()

                span.set_attribute("http.status_code", response.status_code)
                span.set_attribute("weather.city_name", payload.get("name"))
                span.set_attribute("weather.timestamp", payload.get("dt"))

                logger.info(
                    "Successfully fetched weather city=%s city_name=%s",
                    payload.get("name"),
                    city_name,
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
                    "OpenWeather returned HTTP %s for city_name=%s",
                    exc.response.status_code,
                    city_name,
                )

                raise OpenWeatherError(f"OpenWeather API returned HTTP {exc.response.status_code}") from exc

            except RequestError as exc:
                span.record_exception(exc)
                span.set_status(
                    Status(
                        StatusCode.ERROR,
                        "Connection failed",
                    )
                )

                logger.exception(
                    "Connection error calling OpenWeather city_name=%s",
                    city_name,
                )

                raise OpenWeatherError("Unable to connect to OpenWeather API") from exc

            except ValueError as exc:
                span.record_exception(exc)
                span.set_status(
                    Status(
                        StatusCode.ERROR,
                        "Invalid JSON",
                    )
                )

                logger.exception(
                    "Invalid JSON received from OpenWeather city_name=%s",
                    city_name,
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
                    "Unexpected error fetching weather city_name=%s",
                    city_name,
                )

                raise OpenWeatherError("Unexpected error while fetching weather") from exc

    async def fetch_if_needed(self, city_name: str | None = None) -> CurrentWeatherJSON:
        """
        Return cached weather if younger than CACHE_HOURS,
        otherwise fetch fresh data from OpenWeather.
        """

        if city_name is None:
            city_name = "Krakow,PL"
        with tracer.start_as_current_span("openweather.current.fetch_if_needed") as span:
            span.set_attribute("city_name", city_name)
            cached = self.get(city_name)

            if not self._is_stale(cached):
                logger.info("Current weather cache hit city_name=%s", city_name)
                return cached

            logger.info("Current weather cache miss city_name=%s", city_name)

            payload = await self._fetch_from_api(city_name)

            logger.info("Current weather cache miss payload=%s", payload)
            return self.save(payload)
