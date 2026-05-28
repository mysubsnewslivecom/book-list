from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, Integer, String

from db.database import Base


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(
        String,
        nullable=False,
        unique=True,
        index=True,
    )

    author = Column(
        String,
        nullable=False,
        index=True,
    )

    description = Column(
        String,
        nullable=True,
    )

    status = Column(
        String,
        nullable=False,
        default="available",
        index=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        index=True,
    )

    def __repr__(self) -> str:
        return f"<Book(id={self.id}, title='{self.title}', author='{self.author}', status='{self.status}')>"
