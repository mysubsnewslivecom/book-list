from datetime import date

from opentelemetry import trace

from repositories.reading_session_repository import ReadingSessionRepository

tracer = trace.get_tracer(__name__)


class ReadingSessionService:
    def __init__(self, repo: ReadingSessionRepository):
        self.repo = repo

    # ---------------------------------------------------------------------
    # LIST ALL SESSIONS (formatted for API)
    # ---------------------------------------------------------------------
    def list_sessions(self) -> list[dict]:
        with tracer.start_as_current_span("reading_sessions_service.list_sessions"):
            sessions = self.repo.get_all()

            return [
                {
                    "id": s.id,
                    "minutes_read": s.minutes_read,
                    "pages_read": s.pages_read,
                    "notes": s.notes,
                    "session_date": s.session_date,
                    "book": {
                        "title": s.book.title,
                        "author": s.book.author,
                    }
                    if s.book
                    else None,
                }
                for s in sessions
            ]

    # ---------------------------------------------------------------------
    # GET ONE SESSION
    # ---------------------------------------------------------------------
    def get_session(self, session_id: int) -> dict | None:
        with tracer.start_as_current_span("reading_sessions_service.get_session") as span:
            span.set_attribute("reading_session.id", session_id)
            s = self.repo.get_by_id(session_id)

        if not s:
            return None

        return {
            "id": s.id,
            "minutes_read": s.minutes_read,
            "pages_read": s.pages_read,
            "notes": s.notes,
            "session_date": s.session_date,
            "book": {
                "title": s.book.title,
                "author": s.book.author,
            }
            if s.book
            else None,
        }

    # ---------------------------------------------------------------------
    # GET SESSIONS BY BOOK
    # ---------------------------------------------------------------------
    def get_sessions_by_book(self, book_id: int) -> list[dict]:
        with tracer.start_as_current_span("reading_sessions_service.get_sessions_by_book") as span:
            span.set_attribute("book.id", book_id)
            sessions = self.repo.get_by_book_id(book_id)

            return [
                {
                    "id": s.id,
                    "minutes_read": s.minutes_read,
                    "pages_read": s.pages_read,
                    "notes": s.notes,
                    "session_date": s.session_date,
                }
                for s in sessions
            ]

    # ---------------------------------------------------------------------
    # GET SESSIONS BY DATE RANGE
    # ---------------------------------------------------------------------
    def get_sessions_by_date_range(
        self,
        start_date: date,
        end_date: date,
    ) -> list[dict]:
        with tracer.start_as_current_span("reading_sessions_service.get_sessions_by_date_range") as span:
            span.set_attribute("start_date", str(start_date))
            span.set_attribute("end_date", str(end_date))
            sessions = self.repo.get_by_date_range(start_date, end_date)

            return [
                {
                    "id": s.id,
                    "minutes_read": s.minutes_read,
                    "pages_read": s.pages_read,
                    "notes": s.notes,
                    "session_date": s.session_date,
                    "book": {
                        "title": s.book.title,
                        "author": s.book.author,
                    }
                    if s.book
                    else None,
                }
                for s in sessions
            ]

    # ---------------------------------------------------------------------
    # CREATE SESSION
    # ---------------------------------------------------------------------
    def create_session(self, data: dict) -> dict:
        with tracer.start_as_current_span("reading_sessions_service.create_session"):
            s = self.repo.create(data)

            return {
                "id": s.id,
                "minutes_read": s.minutes_read,
                "pages_read": s.pages_read,
                "notes": s.notes,
                "session_date": s.session_date,
                "book_id": s.book_id,
            }

    # ---------------------------------------------------------------------
    # DELETE SESSION
    # ---------------------------------------------------------------------
    def delete_session(self, session_id: int) -> dict | None:
        with tracer.start_as_current_span("reading_sessions_service.delete_session") as span:
            span.set_attribute("reading_session.id", session_id)
            s = self.repo.delete(session_id)

            if not s:
                return None

            return {
                "id": s.id,
                "message": "Session deleted successfully",
            }

    # ---------------------------------------------------------------------
    # ANALYTICS: total minutes per book
    # ---------------------------------------------------------------------
    def get_total_minutes(self, book_id: int) -> dict:
        with tracer.start_as_current_span("reading_sessions_service.get_total_minutes") as span:
            span.set_attribute("book.id", book_id)
            total = self.repo.get_total_minutes_by_book(book_id)

            return {
                "book_id": book_id,
                "total_minutes_read": total,
            }
