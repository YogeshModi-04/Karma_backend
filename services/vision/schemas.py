from pydantic import BaseModel, Field


class DescribeRequest(BaseModel):
    """Request body for the image description endpoint."""

    image: str = Field(
        ...,
        description="Local filesystem path or public HTTP/HTTPS URL of the image.",
        examples=["/home/user/photo.jpg", "https://example.com/image.png"],
    )


class DescribeResponse(BaseModel):
    """Successful response from the image description endpoint."""

    description: str = Field(..., description="Detailed description of the image.")
    model: str = Field(..., description="Ollama model used to generate the description.")
