from datetime import date

from opentelemetry import trace
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from db.models.books import ReadingSession

tracer = trace.get_tracer(__name__)


class ReadingSessionRepository:
    def __init__(self, db: Session):
        self.db = db

    # ---------------------------------------------------------------------
    # READ: all sessions (with book relationship)
    # ---------------------------------------------------------------------
    def get_all(self) -> list[ReadingSession]:
        with tracer.start_as_current_span("reading_session_repository.get_all"):
            return self.db.query(ReadingSession).options(joinedload(ReadingSession.book)).all()

    # ---------------------------------------------------------------------
    # READ: by ID
    # ---------------------------------------------------------------------
    def get_by_id(self, session_id: int) -> ReadingSession | None:
        with tracer.start_as_current_span("reading_session_repository.get_by_id") as span:
            span.set_attribute("reading_session.id", session_id)
            return (
                self.db.query(ReadingSession)
                .options(joinedload(ReadingSession.book))
                .filter(ReadingSession.id == session_id)
                .first()
            )

    # ---------------------------------------------------------------------
    # READ: by book_id
    # ---------------------------------------------------------------------
    def get_by_book_id(self, book_id: int) -> list[ReadingSession]:
        with tracer.start_as_current_span("reading_session_repository.get_by_book_id") as span:
            span.set_attribute("book.id", book_id)
            return (
                self.db.query(ReadingSession)
                .options(joinedload(ReadingSession.book))
                .filter(ReadingSession.book_id == book_id)
                .all()
            )

    # ---------------------------------------------------------------------
    # READ: by date range
    # ---------------------------------------------------------------------
    def get_by_date_range(
        self,
        start_date: date,
        end_date: date,
    ) -> list[ReadingSession]:
        with tracer.start_as_current_span("reading_session_repository.get_by_date_range") as span:
            span.set_attribute("start_date", str(start_date))
            span.set_attribute("end_date", str(end_date))
            return (
                self.db.query(ReadingSession)
                .options(joinedload(ReadingSession.book))
                .filter(
                    ReadingSession.session_date >= start_date,
                    ReadingSession.session_date <= end_date,
                )
                .all()
            )

    # ---------------------------------------------------------------------
    # CREATE
    # ---------------------------------------------------------------------
    def create(self, data: dict) -> ReadingSession:
        with tracer.start_as_current_span("reading_session_repository.create"):
            session = ReadingSession(**data)
            self.db.add(session)
            self.db.commit()
            self.db.refresh(session)
            return session

    # ---------------------------------------------------------------------
    # DELETE
    # ---------------------------------------------------------------------
    def delete(self, session_id: int) -> ReadingSession | None:
        with tracer.start_as_current_span("reading_session_repository.delete") as span:
            span.set_attribute("reading_session.id", session_id)
            session = self.get_by_id(session_id)

            if not session:
                return None

            self.db.delete(session)
            self.db.commit()
            return session

    # ---------------------------------------------------------------------
    # AGGREGATION: total minutes per book
    # ---------------------------------------------------------------------
    def get_total_minutes_by_book(self, book_id: int) -> int:
        with tracer.start_as_current_span("reading_session_repository.get_total_minutes_by_book") as span:
            span.set_attribute("book.id", book_id)
            return (
                self.db.query(func.sum(ReadingSession.minutes_read)).filter(ReadingSession.book_id == book_id).scalar()
                or 0
            )
