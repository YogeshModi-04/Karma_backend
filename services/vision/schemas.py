from pydantic import BaseModel, Field


class DescribeRequest(BaseModel):
    """
    Request body for the image description endpoint.

    Supply exactly one of: `image` (path/URL) or `image_base64`.
    For file uploads use the multipart endpoint POST /vision/describe/upload.
    """

    image: str | None = Field(
        default=None,
        description="Local filesystem path or public HTTP/HTTPS URL of the image.",
        examples=["https://example.com/photo.jpg"],
    )
    image_base64: str | None = Field(
        default=None,
        description=(
            "Base64-encoded image bytes. Optionally prefix with a data URI: "
            "'data:image/jpeg;base64,<data>' or pass raw base64 string."
        ),
    )
    mime_type: str = Field(
        default="image/jpeg",
        description="MIME type of the base64 image (ignored when using `image`).",
        examples=["image/jpeg", "image/png", "image/webp"],
    )


class DescribeResponse(BaseModel):
    """Successful response from the image description endpoint."""

    description: str = Field(..., description="Detailed description of the image.")
    model: str = Field(..., description="Ollama model used to generate the description.")
