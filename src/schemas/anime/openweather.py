from typing import Any

from pydantic import BaseModel, ConfigDict


class CurrentWeatherResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    city_id: int
    city_name: str | None
    country: str | None
    lat: float | None
    lon: float | None
    dt: int
    timezone: int | None
    cod: int | None
    payload: dict[str, Any]
