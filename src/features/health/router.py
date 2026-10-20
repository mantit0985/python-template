from typing import Annotated

from fastapi import APIRouter, Depends

from ...core.config import settings
from .schemas import HealthResponse
from .service import HealthService, health_service

router = APIRouter(tags=["Health"])


def get_health_service() -> HealthService:
    return health_service


@router.get("/health", response_model=HealthResponse)
@router.get("/healthz", response_model=HealthResponse)
async def get_health(service: Annotated[HealthService, Depends(get_health_service)]):
    return await service.check_health()


@router.get("/readyz")
async def get_ready():
    return {"status": "ok"}


@router.get("/version")
async def get_version():
    return {"version": settings.API_VERSION}
