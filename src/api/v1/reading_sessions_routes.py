from fastapi import APIRouter, HTTPException, status
from opentelemetry import trace

from api.deps import ReadingSessionServiceDep
from schemas.reading_session import ReadingSessionCreate

tracer = trace.get_tracer(__name__)

router = APIRouter(
    prefix="/reading-sessions",
    tags=["Reading Sessions"],
)


# ---------------------------------------------------------------------
# GET ALL SESSIONS
# ---------------------------------------------------------------------
@router.get("/", response_model=list[dict])
def get_sessions(service: ReadingSessionServiceDep):
    with tracer.start_as_current_span("api.reading_sessions.list"):
        return service.list_sessions()


# ---------------------------------------------------------------------
# GET SESSION BY ID
# ---------------------------------------------------------------------
@router.get("/{session_id}", response_model=dict)
def get_session(session_id: int, service: ReadingSessionServiceDep):
    with tracer.start_as_current_span("api.reading_sessions.get") as span:
        span.set_attribute("reading_session.id", session_id)
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
    with tracer.start_as_current_span("api.reading_sessions.by_book") as span:
        span.set_attribute("book.id", book_id)
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
    with tracer.start_as_current_span("api.reading_sessions.by_date_range") as span:
        span.set_attribute("start_date", start_date)
        span.set_attribute("end_date", end_date)
        return service.get_sessions_by_date_range(start_date, end_date)


# ---------------------------------------------------------------------
# CREATE SESSION
# ---------------------------------------------------------------------
@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_session(
    payload: ReadingSessionCreate,
    service: ReadingSessionServiceDep,
):
    with tracer.start_as_current_span("api.reading_sessions.create"):
        return service.create_session(payload.model_dump())


# ---------------------------------------------------------------------
# DELETE SESSION
# ---------------------------------------------------------------------
@router.delete("/{session_id}", response_model=dict)
def delete_session(session_id: int, service: ReadingSessionServiceDep):
    with tracer.start_as_current_span("api.reading_sessions.delete") as span:
        span.set_attribute("reading_session.id", session_id)
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
    with tracer.start_as_current_span("api.reading_sessions.total_minutes") as span:
        span.set_attribute("book.id", book_id)
        return service.get_total_minutes(book_id=book_id)
