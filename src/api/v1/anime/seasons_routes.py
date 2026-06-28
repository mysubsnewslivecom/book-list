from fastapi import APIRouter
from opentelemetry import trace

from schemas.anime.season import AnimeSeasonCreate, AnimeSeasonResponse

from .deps import AnimeSeasonServiceDep

tracer = trace.get_tracer(__name__)

router = APIRouter(tags=["Seasons"])


@router.get("/anime/{anime_id}/seasons", response_model=list[AnimeSeasonResponse])
def get_seasons(anime_id: int, service: AnimeSeasonServiceDep):
    with tracer.start_as_current_span("api.anime.seasons.get") as span:
        span.set_attribute("anime.id", anime_id)
        return service.get_seasons(anime_id)


@router.post("/anime/{anime_id}/seasons", response_model=AnimeSeasonResponse, status_code=201)
def create_season(anime_id: int, payload: AnimeSeasonCreate, service: AnimeSeasonServiceDep):
    with tracer.start_as_current_span("api.anime.seasons.create") as span:
        span.set_attribute("anime.id", anime_id)
        return service.create(anime_id, payload.model_dump())
