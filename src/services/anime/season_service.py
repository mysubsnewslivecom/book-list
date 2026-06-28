from typing import Any

from opentelemetry import trace

from repositories.anime import AnimeSeasonRepository

tracer = trace.get_tracer(__name__)


class AnimeSeasonService:
    def __init__(self, repo: AnimeSeasonRepository):
        self.repo = repo

    def get_seasons(self, anime_id: int):
        with tracer.start_as_current_span("anime_season_service.get_seasons") as span:
            span.set_attribute("anime.id", anime_id)
            return self.repo.get_by_anime(anime_id=anime_id)

    def create(self, anime_id: int, payload: dict[str, Any]):
        with tracer.start_as_current_span("anime_season_service.create") as span:
            span.set_attribute("anime.id", anime_id)
            return self.repo.create(anime_id=anime_id, season_data=payload)
