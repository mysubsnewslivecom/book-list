from sqlalchemy.orm import Session

from db.models.books import Book


class BookRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self):
        return self.db.query(Book).all()

    def get_by_id(self, book_id: int):
        return self.db.query(Book).filter(Book.id == book_id).first()

    def get_by_title(self, title: str):
        return self.db.query(Book).filter(Book.title == title).first()

    def create(self, book: Book):
        self.db.add(book)
        self.db.commit()
        self.db.refresh(book)
        return book

    def delete(self, book: Book):
        self.db.delete(book)
        self.db.commit()

    def update(self, book: Book):
        self.db.commit()
        self.db.refresh(book)
        return book
