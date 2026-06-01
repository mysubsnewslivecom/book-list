from pydantic import BaseModel, ConfigDict, Field


class AnimeSeasonCreate(BaseModel):
    season_number: int = Field(gt=0)
    title: str | None = None
    total_episodes: int | None = Field(
        default=None,
        gt=0,
    )


class AnimeSeasonResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    anime_id: int
    season_number: int
    title: str | None
    total_episodes: int | None
