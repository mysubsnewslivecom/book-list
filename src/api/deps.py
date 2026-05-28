from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from db.database import get_db
from repositories.book_repository import BookRepository
from services.book_service import BookService

DBSession = Annotated[Session, Depends(get_db)]


def get_book_repository(db: DBSession) -> BookRepository:
    return BookRepository(db)


BookRepositoryDep = Annotated[
    BookRepository,
    Depends(get_book_repository),
]


def get_book_service(repo: BookRepositoryDep) -> BookService:
    return BookService(repo)


BookServiceDep = Annotated[
    BookService,
    Depends(get_book_service),
]
