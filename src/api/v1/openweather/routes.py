from fastapi import APIRouter
from opentelemetry import trace

from api.deps import CurrentWeatherServiceDep, ForecastServiceDep
from schemas.openweather import CurrentWeatherResponse, ForecastResponse

tracer = trace.get_tracer(__name__)

router = APIRouter(prefix="/openweather", tags=["openweather"])


@router.get("/forecast/{city}", response_model=int)
async def get_sessions(city: str, service: ForecastServiceDep):
    with tracer.start_as_current_span("api.openweather.forecast") as span:
        span.set_attribute("weather.city", city)
        return await service.save(city)


@router.get("/current/{city}", response_model=CurrentWeatherResponse)
async def get_current(city: str, service: CurrentWeatherServiceDep):
    with tracer.start_as_current_span("api.openweather.current") as span:
        span.set_attribute("weather.city", city)
        return await service.fetch(city)


@router.get("/weather/{city}", response_model=ForecastResponse, response_model_by_alias=True)
async def get_weather(city: str, service: ForecastServiceDep):
    with tracer.start_as_current_span("api.openweather.weather") as span:
        span.set_attribute("weather.forecast", "forecast")
        return await service.get(city=city)
