from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from app.core.logging import logger

class AccessLoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        method = request.method
        url_path = request.url.path

        logger.info(f"Access Log: IP={client_ip}, Method={method}, Path={url_path}")

        response = await call_next(request)
        return response
