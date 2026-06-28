from opentelemetry import trace

from db.models.anime import Anime
from repositories.anime.anime_repository import AnimeRepository
from schemas.anime.anime import AnimeUpdate

tracer = trace.get_tracer(__name__)


class AnimeService:
    def __init__(self, repo: AnimeRepository):
        self.repo = repo

    def get_all(self):
        with tracer.start_as_current_span("anime_service.get_all"):
            return self.repo.get_all()

    def get_by_id(self, anime_id: int):
        with tracer.start_as_current_span("anime_service.get_by_id") as span:
            span.set_attribute("anime.id", anime_id)
            return self.repo.get_by_id(anime_id=anime_id)

    def create(self, anime: Anime):
        with tracer.start_as_current_span("anime_service.create") as span:
            span.set_attribute("anime.title", getattr(anime, "title", None))
            return self.repo.create(anime=anime)

    def update(self, anime_id: int, anime: AnimeUpdate):
        with tracer.start_as_current_span("anime_service.update") as span:
            span.set_attribute("anime.id", anime_id)
            anime = self.get_by_id(anime_id)
        if not anime:
            return anime

        for key, value in anime.model_dump(exclude_unset=True).items():
            setattr(anime, key, value)

        return self.repo.update(anime=anime)

    def delete(self, anime_id: int):
        with tracer.start_as_current_span("anime_service.delete") as span:
            span.set_attribute("anime.id", anime_id)
            anime = self.get_by_id(anime_id)
            if not anime:
                return anime
            return self.repo.delete(anime=anime)
