from fastapi import APIRouter, HTTPException
from opentelemetry import trace

from db.models.anime import Anime
from schemas.anime.anime import AnimeCreate, AnimeResponse, AnimeUpdate

from .deps import AnimeServiceDep

tracer = trace.get_tracer(__name__)

router = APIRouter(prefix="/anime", tags=["Anime"])


@router.get("", response_model=list[AnimeResponse])
def get_anime(service: AnimeServiceDep):
    with tracer.start_as_current_span("api.anime.list"):
        return service.get_all()


@router.get("/{anime_id}", response_model=AnimeResponse)
def get_anime_by_id(anime_id: int, service: AnimeServiceDep):
    with tracer.start_as_current_span("api.anime.get") as span:
        span.set_attribute("anime.id", anime_id)
        anime = service.get_by_id(anime_id)

    if not anime:
        raise HTTPException(
            status_code=404,
            detail="Anime not found",
        )

    return anime


@router.post("", response_model=AnimeResponse, status_code=201)
def create_anime(payload: AnimeCreate, service: AnimeServiceDep):
    with tracer.start_as_current_span("api.anime.create") as span:
        anime = Anime(**payload.model_dump())
        span.set_attribute("anime.title", getattr(anime, "title", None))
        return service.create(anime)


@router.put("/{anime_id}", response_model=AnimeResponse)
def update_anime(anime_id: int, payload: AnimeUpdate, service: AnimeServiceDep):
    with tracer.start_as_current_span("api.anime.update") as span:
        span.set_attribute("anime.id", anime_id)
        anime = service.update(anime_id=anime_id, anime=payload)

    if not anime:
        raise HTTPException(status_code=404, detail="Anime not found")

    return anime


@router.delete("/{anime_id}", status_code=204)
def delete_anime(anime_id: int, service: AnimeServiceDep):
    with tracer.start_as_current_span("api.anime.delete") as span:
        span.set_attribute("anime.id", anime_id)
        anime = service.delete(anime_id)

    if not anime:
        raise HTTPException(status_code=404, detail="Anime not found")
    return anime
