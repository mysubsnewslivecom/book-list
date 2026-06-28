from functools import lru_cache

from pydantic import HttpUrl, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class CustomSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


class Openweather(CustomSettings):
    db_schema: str = "openweather"
    openweather_api_key: SecretStr
    base_url: HttpUrl = "https://api.openweathermap.org/data/2.5"
    # forcast_api: str = "https://api.openweathermap.org/data/2.5/forecast"
    # current_weather_url: str = "https://api.openweathermap.org/data/2.5/weather"

    @property
    def current_weather_url(self) -> HttpUrl:
        return f"{self.base_url}/weather"

    @property
    def forecast_api(self) -> HttpUrl:
        return f"{self.base_url}/forecast"


class BooksSettings(CustomSettings):
    db_schema: str = "books"


class AnimeSettings(CustomSettings):
    db_schema: str = "anime"


class Settings(CustomSettings):
    openweather: Openweather = Openweather()
    books: BooksSettings = BooksSettings()
    anime: AnimeSettings = AnimeSettings()

    is_sqlite: bool = False
    sqlite_path: str = "sqlite:///data/database.db"
    database_url: str | None = None
    database_schema: str = "data"
    otel_service_name: str = "book-list-service"
    otel_exporter_otlp_endpoint: str | None = None
    otel_exporter_otlp_protocol: str = "grpc"

    @property
    def sqlalchemy_database_uri(self) -> str:
        if self.is_sqlite:
            return self.sqlite_path

        if not self.database_url:
            raise ValueError("DATABASE_URL is required when is_sqlite=False")

        return self.database_url


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
