import logging
from dataclasses import dataclass

from sqlalchemy import text
from sqlalchemy.orm import Session

from db.database import session_local
from db.models.books import Book
from schemas.books import BookCreate
from utils.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:     %(message)s",
)
logger = logging.getLogger(__name__)


@dataclass
class BookList:
    book: list[BookCreate]


SEED_DATA = [
    {
        "title": "Nuclear Wars - A scenario",
        "author": "Annie Jacobsen",
        "description": "",
        "status": "reading",
    },
]


def save():
    logger.info("Starting book seed process.")

    book_list = BookList(book=[BookCreate(**item) for item in SEED_DATA])
    session: Session = session_local()

    try:
        logger.info("Preparing %d book records.", len(book_list.book))

        db_book = [Book(**book.model_dump()) for book in book_list.book]

        logger.info(
            "Truncating table %s.book.",
            settings.books.db_schema,
        )
        session.execute(text(f"TRUNCATE TABLE {settings.books.db_schema}.books RESTART IDENTITY CASCADE;"))

        logger.info("Inserting book records.")
        session.add_all(db_book)

        logger.info("Committing transaction.")
        session.commit()

        logger.info("Refreshing inserted records.")
        for book in db_book:
            session.refresh(book)

        logger.info(
            "Successfully seeded %d book records.",
            len(db_book),
        )

        return db_book

    except Exception:
        logger.exception("Failed to seed book data. Rolling back transaction.")
        session.rollback()
        raise

    finally:
        logger.info("Closing database session.")
        session.close()


if __name__ == "__main__":
    save()
