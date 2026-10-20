from pydantic import BaseModel, Field


class ExampleRequest(BaseModel):
    name: str = Field(..., examples=["World"], description="The name to greet")


class ExampleResponse(BaseModel):
    message: str = Field(
        ..., examples=["Hello, World!"], description="The greeting message"
    )
