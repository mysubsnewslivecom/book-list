from fastapi import APIRouter

from api.deps import CurrentWeatherServiceDep, ForecastServiceDep
from schemas.anime.openweather import CurrentWeatherResponse

router = APIRouter(prefix="/openweather", tags=["openweather"])


@router.get("/forecast/{city}", response_model=int)
async def get_sessions(city: str, service: ForecastServiceDep):
    return await service.save(city)


@router.get("/current/{city}", response_model=CurrentWeatherResponse)
async def get_current(service: CurrentWeatherServiceDep, city: str = "Krakow,PL"):
    return await service.fetch(city)
