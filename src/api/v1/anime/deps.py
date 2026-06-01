from typing import Annotated

from fastapi import Depends

from api.deps import DBSession
from repositories.anime import AnimeRepository, AnimeSeasonRepository, WatchEntryRepository
from services.anime import AnimeSeasonService, AnimeService, WatchEntryService


def get_anime_repository(db: DBSession) -> AnimeRepository:
    return AnimeRepository(db)


AnimeRepositoryDep = Annotated[AnimeRepository, Depends(get_anime_repository)]


def get_anime_service(repo: AnimeRepositoryDep) -> AnimeService:
    return AnimeService(repo)


AnimeServiceDep = Annotated[AnimeService, Depends(get_anime_service)]

# SEASON


def get_anime_season_repository(db: DBSession) -> AnimeSeasonRepository:
    return AnimeSeasonRepository(db)


AnimeSeasonRepositoryDep = Annotated[AnimeSeasonRepository, Depends(get_anime_season_repository)]


def get_anime_season_service(repo: AnimeSeasonRepositoryDep) -> AnimeSeasonService:
    return AnimeSeasonService(repo)


AnimeSeasonServiceDep = Annotated[AnimeSeasonService, Depends(get_anime_season_service)]

# WATCH ENTRY


def get_watch_entry_repository(db: DBSession) -> WatchEntryRepository:
    return WatchEntryRepository(db)


WatchEntryRepositoryDep = Annotated[WatchEntryRepository, Depends(get_watch_entry_repository)]


def get_watch_entry_service(repo: WatchEntryRepositoryDep) -> WatchEntryService:
    return WatchEntryService(repo)


WatchEntryServiceDep = Annotated[WatchEntryService, Depends(get_watch_entry_service)]
