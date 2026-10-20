import pytest

from src.features.health.service import HealthService


@pytest.mark.asyncio
async def test_check_health_returns_ok():
    service = HealthService()
    response = await service.check_health()

    assert response.status == "ok"
    assert response.version is not None
    assert "environment" in response.details
