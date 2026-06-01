from fastapi import APIRouter

from schemas.anime.season import AnimeSeasonCreate, AnimeSeasonResponse

from .deps import AnimeSeasonServiceDep

router = APIRouter(tags=["Seasons"])


@router.get("/anime/{anime_id}/seasons", response_model=list[AnimeSeasonResponse])
def get_seasons(anime_id: int, service: AnimeSeasonServiceDep):
    return service.get_seasons(anime_id)


@router.post("/anime/{anime_id}/seasons", response_model=AnimeSeasonResponse, status_code=201)
def create_season(anime_id: int, payload: AnimeSeasonCreate, service: AnimeSeasonServiceDep):
    return service.create(anime_id, payload.model_dump())
