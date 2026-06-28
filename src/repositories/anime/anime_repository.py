from opentelemetry import trace
from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models.anime import Anime

tracer = trace.get_tracer(__name__)


class AnimeRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[Anime]:
        with tracer.start_as_current_span("anime_repository.get_all"):
            return self.db.scalars(select(Anime)).all()

    def get_by_id(self, anime_id: int) -> Anime | None:
        with tracer.start_as_current_span("anime_repository.get_by_id") as span:
            span.set_attribute("anime.id", anime_id)
            return self.db.get(Anime, anime_id)

    def get_by_title(self, title: str) -> Anime | None:
        with tracer.start_as_current_span("anime_repository.get_by_title") as span:
            span.set_attribute("anime.title", title)
            stmt = select(Anime).where(Anime.title == title)
            return self.db.scalar(stmt)

    def create(self, anime: Anime) -> Anime:
        with tracer.start_as_current_span("anime_repository.create") as span:
            span.set_attribute("anime.title", getattr(anime, "title", None))
            self.db.add(anime)
            self.db.commit()
            self.db.refresh(anime)
            return anime

    def update(self, anime: Anime) -> Anime:
        with tracer.start_as_current_span("anime_repository.update"):
            self.db.commit()
            self.db.refresh(anime)
            return anime

    def delete(self, anime: Anime) -> None:
        with tracer.start_as_current_span("anime_repository.delete") as span:
            span.set_attribute("anime.id", getattr(anime, "id", None))
            self.db.delete(anime)
            self.db.commit()
            return anime
