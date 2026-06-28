import logging
from collections import defaultdict

from fastapi import APIRouter, HTTPException, Query, status
from opentelemetry import trace
from pydantic import BaseModel

from api.deps import BookServiceDep
from schemas.books import BookCreate, BookOut, BookUpdate

tracer = trace.get_tracer(__name__)

# ---------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)

logger = logging.getLogger("uvicorn.error")

# ---------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------
router = APIRouter(
    prefix="/books",
    tags=["Books"],
)


def group_books_by_status(books):
    grouped = defaultdict(list)

    for book in books:
        grouped[book.status].append({"title": book.title, "author": book.author})

    return dict(grouped)


# ---------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------


@router.get(
    "/",
    response_model=list[BookOut],
    summary="List books",
    description="Retrieve all books. Optionally filter by status.",
    operation_id="listBooks",
)
async def get_books(
    service: BookServiceDep,
    book_status: str | None = Query(
        default=None,
        description="Filter books by status (e.g. reading, finished, planned)",
    ),
):
    with tracer.start_as_current_span("api.books.list") as span:
        if book_status:
            span.set_attribute("book.status", book_status)
            return service.get_book_by_status(book_status)
        return service.list_books()


@router.get(
    "/{book_id}",
    response_model=BookOut,
    summary="Get book by ID",
    description="Retrieve a single book by its unique ID.",
    operation_id="getBookById",
    responses={
        404: {"description": "Book not found"},
    },
)
async def get_book(
    book_id: int,
    service: BookServiceDep,
):
    with tracer.start_as_current_span("api.books.get") as span:
        span.set_attribute("book.id", book_id)
        book = service.get_book(book_id)

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )

    return book


@router.post(
    "/",
    response_model=BookOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create book",
    description="Create a new book entry.",
    operation_id="createBook",
)
async def create_book(
    payload: BookCreate,
    service: BookServiceDep,
):
    with tracer.start_as_current_span("api.books.create") as span:
        span.set_attribute("book.title", payload.title)
        return service.create_book(payload)


@router.patch(
    "/{book_id}",
    response_model=BookOut,
    summary="Update book",
    description="Partially update a book by ID.",
    operation_id="updateBook",
    responses={
        404: {"description": "Book not found"},
    },
)
async def update_book(
    book_id: int,
    payload: BookUpdate,
    service: BookServiceDep,
):
    with tracer.start_as_current_span("api.books.update") as span:
        span.set_attribute("book.id", book_id)
        book = service.update_book(book_id, payload)

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )

    return book


@router.delete(
    "/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete book",
    description="Delete a book by ID.",
    operation_id="deleteBook",
    responses={
        404: {"description": "Book not found"},
    },
)
async def delete_book(
    book_id: int,
    service: BookServiceDep,
):
    with tracer.start_as_current_span("api.books.delete") as span:
        span.set_attribute("book.id", book_id)
        deleted = service.delete_book(book_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )

    return None


# ---------------------------------------------------------------------
# Optional: explicit status endpoint (if you prefer path filtering)
# ---------------------------------------------------------------------


class StatusResponse(BaseModel):
    title: str
    author: str


class ByStatus(BaseModel):
    status: list[StatusResponse]


@router.get(
    "/status/all",
    summary="Get books by status",
    description="Retrieve books filtered by reading status.",
    operation_id="getBooksByStatus",
)
async def get_books_by_status(service: BookServiceDep):
    with tracer.start_as_current_span("api.books.by_status"):
        books = service.list_books()

    if not books:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No books found",
        )

    rows = service.get_selected()
    logger.info(group_books_by_status(rows))

    return group_books_by_status(books=books)
