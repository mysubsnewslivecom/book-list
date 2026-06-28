from fastapi import APIRouter
from opentelemetry import trace

from api.deps import CurrentWeatherServiceDep, ForecastServiceDep
from schemas.openweather import CurrentWeatherResponse

tracer = trace.get_tracer(__name__)

router = APIRouter(prefix="/openweather", tags=["openweather"])


@router.get("/forecast/{city}", response_model=int)
async def get_sessions(city: str, service: ForecastServiceDep):
    with tracer.start_as_current_span("api.openweather.forecast") as span:
        span.set_attribute("weather.city", city)
        return await service.save(city)


@router.get("/current/{city}", response_model=CurrentWeatherResponse)
async def get_current(service: CurrentWeatherServiceDep, city: str = "Krakow,PL"):
    with tracer.start_as_current_span("api.openweather.current") as span:
        span.set_attribute("weather.city", city)
        return await service.fetch(city)
