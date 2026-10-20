import time
import uuid
from collections.abc import Awaitable, Callable

import structlog
from fastapi import Request
from prometheus_client import Counter, Histogram
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = structlog.get_logger()

# Metrics
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP Requests",
    ["method", "route", "http_status"],
)
REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "route"],
)


class RequestCorrelationMiddleware(BaseHTTPMiddleware):
    """
    Middleware to ensure every request has a unique request ID.
    The ID is added to the response headers and the structured logging context.
    """

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ):
        # 1. Extract or generate request ID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

        # 2. Bind request ID to structlog context for the duration of this request
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        # 3. Process the request
        response: Response = await call_next(request)

        # 4. Add request ID to response headers
        response.headers["X-Request-ID"] = request_id

        return response


class SecureHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add standard security headers to all responses.
    """

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
        return response


class PrometheusTimingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to track request duration using Prometheus histograms.
    """

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ):
        start_time = time.time()

        response = await call_next(request)

        duration = time.time() - start_time

        # Get the route template (e.g., /users/{user_id}) instead of the actual URL
        route = request.scope.get("route")
        route_path = route.path if route else "not_found"

        REQUEST_COUNT.labels(
            method=request.method, route=route_path, http_status=response.status_code
        ).inc()
        REQUEST_DURATION.labels(method=request.method, route=route_path).observe(
            duration
        )

        return response
