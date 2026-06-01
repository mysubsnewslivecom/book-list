from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models.anime import Anime


class AnimeRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[Anime]:
        return self.db.scalars(select(Anime)).all()

    def get_by_id(self, anime_id: int) -> Anime | None:
        return self.db.get(Anime, anime_id)

    def get_by_title(self, title: str) -> Anime | None:
        stmt = select(Anime).where(Anime.title == title)
        return self.db.scalar(stmt)

    def create(self, anime: Anime) -> Anime:
        self.db.add(anime)
        self.db.commit()
        self.db.refresh(anime)
        return anime

    def update(self, anime: Anime) -> Anime:
        self.db.commit()
        self.db.refresh(anime)
        return anime

    def delete(self, anime: Anime) -> None:
        self.db.delete(anime)
        self.db.commit()
        return anime
