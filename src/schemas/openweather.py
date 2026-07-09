from typing import Any

from pydantic import BaseModel, ConfigDict, Field


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


class Main(BaseModel):
    temp: float
    feels_like: float
    temp_min: float
    temp_max: float
    pressure: int
    sea_level: int
    grnd_level: int
    humidity: int
    temp_kf: float


class Weather(BaseModel):
    id: int
    main: str
    description: str
    icon: str


class Clouds(BaseModel):
    all: int


class Wind(BaseModel):
    speed: float
    deg: int
    gust: float | None = None


class Rain(BaseModel):
    three_h: float = Field(alias="3h")

    model_config = ConfigDict(populate_by_name=True)


class Sys(BaseModel):
    pod: str


class ForecastItem(BaseModel):
    dt: int
    main: Main
    weather: list[Weather]
    clouds: Clouds
    wind: Wind
    visibility: int
    pop: float
    sys: Sys
    dt_txt: str
    rain: Rain | None = None


class Coord(BaseModel):
    lat: float
    lon: float


class City(BaseModel):
    id: int
    name: str
    coord: Coord
    country: str
    population: int
    timezone: int
    sunrise: int
    sunset: int


class ForecastResponse(BaseModel):
    cod: str
    message: int
    cnt: int
    list: list[ForecastItem]
    city: City
