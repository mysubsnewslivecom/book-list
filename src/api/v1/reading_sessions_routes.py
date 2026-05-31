from fastapi import APIRouter, HTTPException, status

from api.deps import ReadingSessionServiceDep
from schemas.reading_session import ReadingSessionCreate

router = APIRouter(
    prefix="/reading-sessions",
    tags=["Reading Sessions"],
)


# ---------------------------------------------------------------------
# GET ALL SESSIONS
# ---------------------------------------------------------------------
@router.get("/", response_model=list[dict])
def get_sessions(service: ReadingSessionServiceDep):
    return service.list_sessions()


# ---------------------------------------------------------------------
# GET SESSION BY ID
# ---------------------------------------------------------------------
@router.get("/{session_id}", response_model=dict)
def get_session(session_id: int, service: ReadingSessionServiceDep):
    session = service.get_session(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    return session


# ---------------------------------------------------------------------
# GET BY BOOK ID
# ---------------------------------------------------------------------
@router.get("/book/{book_id}", response_model=list[dict])
def get_sessions_by_book(book_id: int, service: ReadingSessionServiceDep):
    return service.get_sessions_by_book(book_id)


# ---------------------------------------------------------------------
# GET BY DATE RANGE
# ---------------------------------------------------------------------
@router.get("/range", response_model=list[dict])
def get_sessions_by_date_range(
    start_date: str,
    end_date: str,
    service: ReadingSessionServiceDep,
):
    return service.get_sessions_by_date_range(start_date, end_date)


# ---------------------------------------------------------------------
# CREATE SESSION
# ---------------------------------------------------------------------
@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_session(
    payload: ReadingSessionCreate,
    service: ReadingSessionServiceDep,
):
    return service.create_session(payload.model_dump())


# ---------------------------------------------------------------------
# DELETE SESSION
# ---------------------------------------------------------------------
@router.delete("/{session_id}", response_model=dict)
def delete_session(session_id: int, service: ReadingSessionServiceDep):
    result = service.delete_session(session_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    return result


# ---------------------------------------------------------------------
# ANALYTICS: TOTAL MINUTES PER BOOK
# ---------------------------------------------------------------------
@router.get("/analytics/{book_id}", response_model=dict)
def get_total_minutes(book_id: int, service: ReadingSessionServiceDep):
    return service.get_total_minutes(book_id=book_id)
