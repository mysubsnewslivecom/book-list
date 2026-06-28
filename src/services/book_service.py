from opentelemetry import trace

from db.models.books import Book
from repositories.book_repository import BookRepository
from schemas.books import BookCreate, BookUpdate

tracer = trace.get_tracer(__name__)


class BookService:
    def __init__(self, repo: BookRepository):
        self.repo = repo

    def list_books(self):
        with tracer.start_as_current_span("book_service.list_books"):
            return self.repo.get_all()

    def get_book(self, book_id: int):
        with tracer.start_as_current_span("book_service.get_book") as span:
            span.set_attribute("book.id", book_id)
            return self.repo.get_by_id(book_id)

    def create_book(self, data: BookCreate):
        with tracer.start_as_current_span("book_service.create_book") as span:
            book = Book(**data.model_dump())
            span.set_attribute("book.title", book.title)
            return self.repo.create(book)

    def delete_book(self, book_id: int):
        with tracer.start_as_current_span("book_service.delete_book") as span:
            span.set_attribute("book.id", book_id)
            book = self.repo.get_by_id(book_id)
        if not book:
            return False
        self.repo.delete(book)
        return True

    def update_book(self, book_id: int, data: BookUpdate):
        with tracer.start_as_current_span("book_service.update_book") as span:
            span.set_attribute("book.id", book_id)
            book = self.repo.get_by_id(book_id)

        if not book:
            return None

        update_data = data.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(book, key, value)

        self.repo.db.commit()
        self.repo.db.refresh(book)

        return book

    def get_book_by_status(self, status: str):
        with tracer.start_as_current_span("book_service.get_book_by_status") as span:
            span.set_attribute("book.status", status)
            return self.repo.get_by_status(status=status)

    def get_selected(self):
        with tracer.start_as_current_span("book_service.get_selected"):
            return self.repo.get_selected()
