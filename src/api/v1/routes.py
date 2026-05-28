from fastapi import APIRouter, HTTPException

from api.deps import BookServiceDep
from schemas.books import BookCreate, BookUpdate, BookOut

router = APIRouter(prefix="/books", tags=["Books"])


@router.get("/", response_model=list[BookOut])
def get_books(service: BookServiceDep):
    return service.list_books()


@router.get("/{book_id}", response_model=BookOut)
def get_book(book_id: int, service: BookServiceDep):
    book = service.get_book(book_id)

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    return book


@router.post("/", response_model=BookOut)
def create_book(payload: BookCreate, service: BookServiceDep):
    return service.create_book(payload)


@router.patch("/{book_id}", response_model=BookOut)
def update_book(book_id: int, payload: BookUpdate, service: BookServiceDep):
    book = service.update_book(book_id, payload)

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    return book


@router.delete("/{book_id}")
def delete_book(book_id: int, service: BookServiceDep):
    deleted = service.delete_book(book_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Book not found")

    return {"deleted": True}
