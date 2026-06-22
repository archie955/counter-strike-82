import logging
import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        method = request.method
        url = request.url.path
        client_ip = request.client.host if request.client else "NO HOST"

        logger.info(
            "%s %s from %s",
            method,
            url,
            client_ip,
        )

        start = time.perf_counter()

        response = await call_next(request)

        duration = time.perf_counter() - start

        logger.info("%s %s -> %s (%.3fs)", method, url, response.status_code, duration)

        return response
