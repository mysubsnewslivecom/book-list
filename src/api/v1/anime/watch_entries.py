from fastapi import APIRouter, HTTPException
from opentelemetry import trace

from schemas.anime.watch_entry import (
    WatchEntryCreate,
    WatchEntryProgressUpdate,
    WatchEntryResponse,
    WatchEntryStatusUpdate,
)

from .deps import WatchEntryServiceDep

tracer = trace.get_tracer(__name__)

router = APIRouter(prefix="/watch-entries", tags=["Watch Entries"])


@router.get("", response_model=list[WatchEntryResponse])
def get_watch_entries(service: WatchEntryServiceDep):
    with tracer.start_as_current_span("api.anime.watch_entries.list"):
        return service.get_all()


@router.post("", response_model=WatchEntryResponse, status_code=201)
def create_watch_entry(payload: WatchEntryCreate, service: WatchEntryServiceDep):
    with tracer.start_as_current_span("api.anime.watch_entries.create") as span:
        span.set_attribute("entry", payload.model_dump())
        return service.create(payload.model_dump())


@router.patch("/{entry_id}/progress", response_model=WatchEntryResponse)
def update_progress(entry_id: int, payload: WatchEntryProgressUpdate, service: WatchEntryServiceDep):
    with tracer.start_as_current_span("api.anime.watch_entries.update_progress") as span:
        span.set_attribute("watch_entry.id", entry_id)
        span.set_attribute("watch_entry.episode", payload.current_episode)
        entry = service.update_progress(entry_id, payload.current_episode)

    if not entry:
        raise HTTPException(
            status_code=404,
            detail="Entry not found",
        )

    return entry


@router.patch("/{entry_id}/status", response_model=WatchEntryResponse)
def update_status(entry_id: int, payload: WatchEntryStatusUpdate, service: WatchEntryServiceDep):
    with tracer.start_as_current_span("api.anime.watch_entries.update_status") as span:
        span.set_attribute("watch_entry.id", entry_id)
        span.set_attribute("watch_entry.status", payload.watch_status)
        entry = service.update_status(entry_id, payload.watch_status)

    if not entry:
        raise HTTPException(
            status_code=404,
            detail="Entry not found",
        )

    return entry


@router.delete("/{entry_id}", status_code=204)
def delete_entry(entry_id: int, service: WatchEntryServiceDep):
    with tracer.start_as_current_span("api.anime.watch_entries.delete") as span:
        span.set_attribute("watch_entry.id", entry_id)
        deleted = service.delete(entry_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Entry not found",
        )

    return deleted
