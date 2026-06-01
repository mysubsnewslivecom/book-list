from db.models.anime import Anime
from repositories.anime.anime_repository import AnimeRepository
from schemas.anime.anime import AnimeUpdate


class AnimeService:
    def __init__(self, repo: AnimeRepository):
        self.repo = repo

    def get_all(self):
        return self.repo.get_all()

    def get_by_id(self, anime_id: int):
        return self.repo.get_by_id(anime_id=anime_id)

    def create(self, anime: Anime):
        return self.repo.create(anime=anime)

    def update(self, anime_id: int, anime: AnimeUpdate):
        anime = self.get_by_id(anime_id)
        if not anime:
            return anime

        for key, value in anime.model_dump(exclude_unset=True).items():
            setattr(anime, key, value)

        return self.repo.update(anime=anime)

    def delete(self, anime_id: int):
        anime = self.get_by_id(anime_id)
        if not anime:
            return anime
        return self.repo.delete(anime=anime)
