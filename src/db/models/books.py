import enum
from datetime import UTC, date, datetime

from sqlalchemy import Column, Date, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.database import Base
from utils.config import settings


class Status(enum.StrEnum):
    READ = "read"
    PENDING = "pending"
    READING = "reading"


books_enum_type = Enum(
    *[c.value for c in Status],
    name="books_status_enum",
    schema=settings.database_schema,
    create_type=True,
)


class Book(Base):
    __tablename__ = "books"
    __table_args__ = {"schema": settings.database_schema}

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String, nullable=False, unique=True, index=True)

    author = Column(String, nullable=False, index=True)

    description = Column(String, nullable=True)

    status: Mapped[Status] = mapped_column(books_enum_type, nullable=False, default=Status.PENDING, index=True)

    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC), index=True)

    reading_sessions: Mapped[list[ReadingSession]] = relationship(back_populates="book", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Book(id={self.id}, title='{self.title}', author='{self.author}', status='{self.status}')>"


class ReadingSession(Base):
    __tablename__ = "reading_sessions"
    __table_args__ = {"schema": settings.database_schema}

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    book_id: Mapped[int] = mapped_column(ForeignKey("data.books.id"), nullable=False)

    session_date: Mapped[date] = mapped_column(Date, nullable=False)

    minutes_read: Mapped[int] = mapped_column(Integer, nullable=False)

    pages_read: Mapped[int | None] = mapped_column(Integer, nullable=True)

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    book = relationship("Book", back_populates="reading_sessions")

    def __repr__(self) -> str:
        return (
            f"ReadingSession("
            f"id={self.id!r}, "
            f"book_id={self.book_id!r}, "
            f"session_date={self.session_date!r}, "
            f"minutes_read={self.minutes_read!r}, "
            f"pages_read={self.pages_read!r}"
            f")"
        )
