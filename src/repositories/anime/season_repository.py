from opentelemetry import trace
from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models.anime import AnimeSeason

tracer = trace.get_tracer(__name__)


class AnimeSeasonRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_anime(self, anime_id: int) -> list[AnimeSeason]:
        with tracer.start_as_current_span("anime_season_repository.get_by_anime") as span:
            span.set_attribute("anime.id", anime_id)
            stmt = select(AnimeSeason).where(AnimeSeason.anime_id == anime_id)

            return self.db.scalars(stmt).all()

    def create(self, anime_id: int, season_data: dict) -> AnimeSeason:
        with tracer.start_as_current_span("anime_season_repository.create") as span:
            span.set_attribute("anime.id", anime_id)
            season = AnimeSeason(anime_id=anime_id, **season_data)

            self.db.add(season)
            self.db.commit()
            self.db.refresh(season)

            return season
