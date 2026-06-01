from fastapi import APIRouter, HTTPException

from schemas.anime.watch_entry import (
    WatchEntryCreate,
    WatchEntryProgressUpdate,
    WatchEntryResponse,
    WatchEntryStatusUpdate,
)

from .deps import WatchEntryServiceDep

router = APIRouter(prefix="/watch-entries", tags=["Watch Entries"])


@router.get("", response_model=list[WatchEntryResponse])
def get_watch_entries(service: WatchEntryServiceDep):
    return service.get_all()


@router.post("", response_model=WatchEntryResponse, status_code=201)
def create_watch_entry(payload: WatchEntryCreate, service: WatchEntryServiceDep):
    return service.create(payload.model_dump())


@router.patch("/{entry_id}/progress", response_model=WatchEntryResponse)
def update_progress(entry_id: int, payload: WatchEntryProgressUpdate, service: WatchEntryServiceDep):
    entry = service.update_progress(entry_id, payload.current_episode)

    if not entry:
        raise HTTPException(
            status_code=404,
            detail="Entry not found",
        )

    return entry


@router.patch("/{entry_id}/status", response_model=WatchEntryResponse)
def update_status(entry_id: int, payload: WatchEntryStatusUpdate, service: WatchEntryServiceDep):

    entry = service.update_status(entry_id, payload.watch_status)

    if not entry:
        raise HTTPException(
            status_code=404,
            detail="Entry not found",
        )

    return entry


@router.delete("/{entry_id}", status_code=204)
def delete_entry(entry_id: int, service: WatchEntryServiceDep):

    deleted = service.delete(entry_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Entry not found",
        )

    return deleted
