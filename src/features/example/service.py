from .schemas import ExampleRequest, ExampleResponse


class ExampleService:
    def greet(self, request: ExampleRequest) -> ExampleResponse:
        return ExampleResponse(
            message=(
                f"Hello, {request.name}! "
                "This is a demonstration of the service pattern."
            )
        )


example_service = ExampleService()
