from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class CustomSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore", case_sensitive=False)


class Settings(CustomSettings):
    is_sqlite: bool
    sqlite_path: str = "sqlite:///data/database.db"

    @property
    def sqlalchemy_database_uri(self) -> str:
        if self.is_sqlite:
            return self.sqlite_path
        return "postgresql://user:password@localhost/dbname"


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore


settings = get_settings()
