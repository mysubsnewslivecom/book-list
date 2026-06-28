from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.database import Base
from utils.config import settings


class AnimeStatus(StrEnum):
    AIRING = "airing"
    COMPLETED = "completed"
    UPCOMING = "upcoming"


class WatchStatus(StrEnum):
    WATCHING = "watching"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"
    DROPPED = "dropped"
    PLAN_TO_WATCH = "plan_to_watch"


anime_status_enum_type = SQLEnum(
    *[c.value for c in AnimeStatus],
    name="anime_status_enum",
    schema=settings.database_schema,
    create_type=True,
)


anime_watch_status_enum_type = SQLEnum(
    *[c.value for c in WatchStatus],
    name="anime_watch_status_enum",
    schema=settings.database_schema,
    create_type=True,
)


class Anime(Base):
    __tablename__ = "anime"
    __table_args__ = {"schema": settings.database_schema}

    id: Mapped[int] = mapped_column(primary_key=True)

    title: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    alternative_title: Mapped[str | None] = mapped_column(String(255), nullable=True)

    studio: Mapped[str | None] = mapped_column(String(255), nullable=True)

    release_year: Mapped[int | None] = mapped_column(Integer, nullable=True)

    status: Mapped[AnimeStatus] = mapped_column(anime_status_enum_type, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    seasons: Mapped[list[AnimeSeason]] = relationship(
        back_populates="anime",
        cascade="all, delete-orphan",
        order_by="AnimeSeason.season_number",
    )


class AnimeSeason(Base):
    __tablename__ = "anime_seasons"

    __table_args__ = (
        UniqueConstraint(
            "anime_id",
            "season_number",
            name="uq_anime_season",
        ),
        CheckConstraint(
            "season_number > 0",
            name="ck_season_number_positive",
        ),
        {"schema": settings.database_schema},
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    anime_id: Mapped[int] = mapped_column(ForeignKey("data.anime.id", ondelete="CASCADE"))

    season_number: Mapped[int] = mapped_column(Integer)

    title: Mapped[str | None] = mapped_column(String(255), nullable=True)

    total_episodes: Mapped[int | None] = mapped_column(Integer, nullable=True)

    anime: Mapped[Anime] = relationship(back_populates="seasons")

    watch_entries: Mapped[list[WatchEntry]] = relationship(back_populates="season", cascade="all, delete-orphan")


class WatchEntry(Base):
    __tablename__ = "watch_entries"

    __table_args__ = (
        CheckConstraint(
            "current_episode >= 0",
            name="ck_current_episode_positive",
        ),
        {"schema": settings.database_schema},
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    season_id: Mapped[int] = mapped_column(ForeignKey("data.anime_seasons.id", ondelete="CASCADE"))

    watch_status: Mapped[WatchStatus] = mapped_column(
        anime_watch_status_enum_type, nullable=False, default=WatchStatus.PLAN_TO_WATCH
    )

    current_episode: Mapped[int] = mapped_column(Integer, default=0)

    rating: Mapped[Decimal | None] = mapped_column(Numeric(3, 1), nullable=True)

    started_at: Mapped[date | None] = mapped_column(Date, nullable=True)

    finished_at: Mapped[date | None] = mapped_column(Date, nullable=True)

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    season: Mapped[AnimeSeason] = relationship(back_populates="watch_entries")
