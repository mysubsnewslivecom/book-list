from typing import Any

from repositories.anime import AnimeSeasonRepository


class AnimeSeasonService:
    def __init__(self, repo: AnimeSeasonRepository):
        self.repo = repo

    def get_seasons(self, anime_id: int):
        return self.repo.get_by_anime(anime_id=anime_id)

    def create(self, anime_id: int, payload: dict[str, Any]):
        return self.repo.create(anime_id=anime_id, season_data=payload)
