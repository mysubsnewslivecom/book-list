from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class CustomSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


class Settings(CustomSettings):
    is_sqlite: bool = False
    sqlite_path: str = "sqlite:///data/database.db"
    database_url: str | None = None

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
