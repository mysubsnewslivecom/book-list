from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from db.models.anime import AnimeStatus


class AnimeCreate(BaseModel):
    title: str = Field(max_length=255)
    alternative_title: str | None = None
    studio: str | None = None
    release_year: int | None = None
    status: AnimeStatus


class AnimeUpdate(BaseModel):
    title: str | None = None
    alternative_title: str | None = None
    studio: str | None = None
    release_year: int | None = None
    status: AnimeStatus | None = None


class AnimeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    alternative_title: str | None
    studio: str | None
    release_year: int | None
    status: AnimeStatus
    created_at: datetime
