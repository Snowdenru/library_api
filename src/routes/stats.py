from aiohttp import web
from services.search_service import SearchService
from utils.exceptions import handle_errors


@handle_errors
async def get_genre_stats(request: web.Request) -> web.Response:
    search_service = SearchService(request.app["db"])
    stats = await search_service.get_genre_stats()
    return web.json_response(stats)


@handle_errors
async def get_author_stats(request: web.Request) -> web.Response:
    search_service = SearchService(request.app["db"])
    stats = await search_service.get_author_stats()
    return web.json_response(stats)


def setup_routes(app: web.Application):
    app.router.add_get("/api/stats/genres", get_genre_stats)
    app.router.add_get("/api/stats/authors", get_author_stats)