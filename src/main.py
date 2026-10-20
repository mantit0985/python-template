from typing import Any, cast

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from .core.config import settings
from .core.logging import setup_logging
from .core.middleware import (
    PrometheusTimingMiddleware,
    RequestCorrelationMiddleware,
    SecureHeadersMiddleware,
)
from .features.example.router import router as example_router
from .features.health.router import router as health_router
from .features.metrics.router import router as metrics_router

# Initialize logging
setup_logging()

# Initialize Rate Limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title=settings.APP_NAME, version=settings.API_VERSION)

# Register Rate Limit handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, cast(Any, _rate_limit_exceeded_handler))

# Middleware - Order matters
app.add_middleware(PrometheusTimingMiddleware)
app.add_middleware(RequestCorrelationMiddleware)
app.add_middleware(SecureHeadersMiddleware)
# Register CORS
if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Accept", "Authorization", "Content-Type", "X-Request-ID"],
    )

app.include_router(health_router)
app.include_router(metrics_router)
app.include_router(example_router)


@app.get("/")
@limiter.limit(settings.RATE_LIMIT_DEFAULT)  # type: ignore
async def root(request: Request):
    return {"message": f"Welcome to {settings.APP_NAME}"}
