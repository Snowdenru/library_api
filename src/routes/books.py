from aiohttp import web
from models.book import BookCreate, BookUpdate, BookSearchParams
from services.book_service import BookService
from services.search_service import SearchService
from utils.exceptions import handle_errors


@handle_errors
async def create_book(request: web.Request) -> web.Response:
    data = await request.json()
    book_data = BookCreate(**data)
    book_service = BookService(request.app["db"])
    book = await book_service.create_book(book_data)
    return web.json_response(book.dict(), status=201)


@handle_errors
async def get_book(request: web.Request) -> web.Response:
    book_id = int(request.match_info["id"])
    book_service = BookService(request.app["db"])
    book = await book_service.get_book_by_id(book_id)
    return web.json_response(book.dict())


@handle_errors
async def list_books(request: web.Request) -> web.Response:
    page = int(request.query.get("page", 1))
    per_page = int(request.query.get("per_page", 10))
    book_service = BookService(request.app["db"])
    books = await book_service.list_books(page, per_page)
    return web.json_response([book.dict() for book in books])


@handle_errors
async def update_book(request: web.Request) -> web.Response:
    book_id = int(request.match_info["id"])
    data = await request.json()
    book_data = BookUpdate(**data)
    book_service = BookService(request.app["db"])
    book = await book_service.update_book(book_id, book_data)
    return web.json_response(book.dict())


@handle_errors
async def delete_book(request: web.Request) -> web.Response:
    book_id = int(request.match_info["id"])
    soft_delete = request.query.get("soft", "true").lower() == "true"
    book_service = BookService(request.app["db"])
    await book_service.delete_book(book_id, soft_delete)
    return web.json_response({"status": "deleted"}, status=204)


@handle_errors
async def search_books(request: web.Request) -> web.Response:
    params = BookSearchParams(**request.query)
    search_service = SearchService(request.app["db"])
    result = await search_service.search_books(params)
    return web.json_response(result)


def setup_routes(app: web.Application):
    app.router.add_post("/api/books", create_book)
    app.router.add_get("/api/books", list_books)
    app.router.add_get("/api/books/{id}", get_book)
    app.router.add_put("/api/books/{id}", update_book)
    app.router.add_delete("/api/books/{id}", delete_book)
    app.router.add_get("/api/books/search", search_books)