import time

from ...core.config import settings
from .schemas import HealthResponse

START_TIME = time.time()


class HealthService:
    async def check_health(self) -> HealthResponse:
        return HealthResponse(
            status="ok",
            version=settings.API_VERSION,
            uptime_seconds=time.time() - START_TIME,
            details={"environment": settings.ENVIRONMENT},
        )


health_service = HealthService()
