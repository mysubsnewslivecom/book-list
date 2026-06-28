from opentelemetry import trace
from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models.books import Book

tracer = trace.get_tracer(__name__)


class BookRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self):
        with tracer.start_as_current_span("book_repository.get_all"):
            return self.db.query(Book).all()

    def get_by_id(self, book_id: int):
        with tracer.start_as_current_span("book_repository.get_by_id") as span:
            span.set_attribute("book.id", book_id)
            return self.db.query(Book).filter(Book.id == book_id).first()

    def get_by_title(self, title: str):
        with tracer.start_as_current_span("book_repository.get_by_title") as span:
            span.set_attribute("book.title", title)
            return self.db.query(Book).filter(Book.title == title).first()

    def create(self, book: Book):
        with tracer.start_as_current_span("book_repository.create") as span:
            span.set_attribute("book.title", getattr(book, "title", None))
            self.db.add(book)
            self.db.commit()
            self.db.refresh(book)
            return book

    def delete(self, book: Book):
        with tracer.start_as_current_span("book_repository.delete") as span:
            span.set_attribute("book.id", getattr(book, "id", None))
            self.db.delete(book)
            self.db.commit()

    def update(self, book: Book):
        with tracer.start_as_current_span("book_repository.update"):
            self.db.commit()
            self.db.refresh(book)
            return book

    def get_by_status(self, status: str):
        with tracer.start_as_current_span("book_repository.get_by_status") as span:
            span.set_attribute("book.status", status)
            return self.db.query(Book).filter(Book.status == status).all()

    def get_selected(self):
        with tracer.start_as_current_span("book_repository.get_selected"):
            stmt = select(Book.title, Book.author, Book.status)
            return self.db.execute(stmt).all()
