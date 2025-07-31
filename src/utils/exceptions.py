import traceback
from aiohttp import web
from functools import wraps
from typing import Callable, Any


class NotFoundError(Exception):
    pass


def handle_errors(handler: Callable) -> Callable:
    @wraps(handler)
    async def wrapper(request: web.Request) -> web.Response:
        try:
            return await handler(request)
        except NotFoundError as e:
            request.app['logger'].warning(f"Not found: {str(e)}")
            return web.json_response(
                {"error": str(e)}, status=404
            )
        except ValueError as e:
            request.app['logger'].warning(f"Validation error: {str(e)}")
            return web.json_response(
                {"error": str(e)}, status=400
            )
        except Exception as e:
            request.app['logger'].error(
                f"Internal server error: {str(e)}\n"
                f"Traceback: {traceback.format_exc()}"
            )
            return web.json_response(
                {"error": "Internal server error"}, status=500
            )
    return wrapper