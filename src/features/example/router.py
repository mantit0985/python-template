from fastapi import APIRouter

from .schemas import ExampleRequest, ExampleResponse
from .service import example_service

router = APIRouter(prefix="/example", tags=["Example"])

# In a real app, you might inject the limiter here or use it via the app state
# Since the template uses a global limiter in main.py, we rely on that or a dependency


@router.post(
    "/greet",
    response_model=ExampleResponse,
    summary="Example Greet Endpoint",
    description="Demonstrates the request -> service -> response pattern",
)
async def greet(request: ExampleRequest):
    return example_service.greet(request)
