import pytest
from httpx import AsyncClient
from testcontainers.core.container import DockerContainer


@pytest.fixture(scope="module")
def generic_container():
    # Demonstrating Testcontainers pattern
    with DockerContainer("alpine").with_command("sleep 3600") as container:
        yield container


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient, generic_container: DockerContainer):
    # The health endpoint should work regardless of the container,
    # but the container fixture ensures the pattern is implemented.
    response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "details" in data


@pytest.mark.asyncio
async def test_healthz_endpoint(client: AsyncClient):
    response = await client.get("/healthz")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "uptime_seconds" in data
