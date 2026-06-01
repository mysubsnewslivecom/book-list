from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from db.models.anime import WatchStatus


class WatchEntryCreate(BaseModel):
    season_id: int

    watch_status: WatchStatus = WatchStatus.PLAN_TO_WATCH

    current_episode: int = Field(
        default=0,
        ge=0,
    )

    rating: Decimal | None = None

    started_at: date | None = None
    finished_at: date | None = None
    notes: str | None = None


class WatchEntryProgressUpdate(BaseModel):
    current_episode: int = Field(
        ge=0,
    )


class WatchEntryStatusUpdate(BaseModel):
    watch_status: WatchStatus


class WatchEntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    season_id: int
    watch_status: WatchStatus
    current_episode: int
    rating: Decimal | None
    started_at: date | None
    finished_at: date | None
    notes: str | None
