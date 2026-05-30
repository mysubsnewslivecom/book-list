from db.models.books import Book
from repositories.book_repository import BookRepository
from schemas.books import BookCreate, BookUpdate


class BookService:
    def __init__(self, repo: BookRepository):
        self.repo = repo

    def list_books(self):
        return self.repo.get_all()

    def get_book(self, book_id: int):
        return self.repo.get_by_id(book_id)

    def create_book(self, data: BookCreate):
        book = Book(**data.model_dump())
        return self.repo.create(book)

    def delete_book(self, book_id: int):
        book = self.repo.get_by_id(book_id)
        if not book:
            return False
        self.repo.delete(book)
        return True

    def update_book(self, book_id: int, data: BookUpdate):
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
        return self.repo.get_by_status(status=status)

    def get_selected(self):
        return self.repo.get_selected()
