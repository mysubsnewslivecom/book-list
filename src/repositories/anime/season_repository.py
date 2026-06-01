from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models.anime import AnimeSeason


class AnimeSeasonRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_anime(self, anime_id: int) -> list[AnimeSeason]:
        stmt = select(AnimeSeason).where(AnimeSeason.anime_id == anime_id)

        return self.db.scalars(stmt).all()

    def create(self, anime_id: int, season_data: dict) -> AnimeSeason:
        season = AnimeSeason(anime_id=anime_id, **season_data)

        self.db.add(season)
        self.db.commit()
        self.db.refresh(season)

        return season
