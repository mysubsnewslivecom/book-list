from datetime import date

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from db.models.books import ReadingSession


class ReadingSessionRepository:
    def __init__(self, db: Session):
        self.db = db

    # ---------------------------------------------------------------------
    # READ: all sessions (with book relationship)
    # ---------------------------------------------------------------------
    def get_all(self) -> list[ReadingSession]:
        return self.db.query(ReadingSession).options(joinedload(ReadingSession.book)).all()

    # ---------------------------------------------------------------------
    # READ: by ID
    # ---------------------------------------------------------------------
    def get_by_id(self, session_id: int) -> ReadingSession | None:
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
        session = ReadingSession(**data)
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    # ---------------------------------------------------------------------
    # DELETE
    # ---------------------------------------------------------------------
    def delete(self, session_id: int) -> ReadingSession | None:
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
        return (
            self.db.query(func.sum(ReadingSession.minutes_read)).filter(ReadingSession.book_id == book_id).scalar() or 0
        )
