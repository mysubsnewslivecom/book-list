from datetime import date

from pydantic import BaseModel


class ReadingSessionCreate(BaseModel):
    book_id: int
    session_date: date
    minutes_read: int
    pages_read: int | None = None
    notes: str | None = None
