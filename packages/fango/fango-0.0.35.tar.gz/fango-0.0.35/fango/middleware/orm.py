from asgiref.sync import sync_to_async
from django.db import close_old_connections
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class CloseOldConnectionsMiddleware(BaseHTTPMiddleware):
    """
    Middleware for correctly close django orm connection in main thread

    """

    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        finally:
            await sync_to_async(close_old_connections)()
