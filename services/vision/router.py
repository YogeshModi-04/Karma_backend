import base64

from fastapi import APIRouter, File

from services.vision.schemas import DescribeRequest, DescribeResponse
from services.vision.service import describe_image, get_model_name

router = APIRouter(prefix="/vision", tags=["Vision"])


def _detect_mime(data: bytes) -> str:
    """Detect image MIME type from magic bytes."""
    if data[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    if data[:6] in (b"GIF87a", b"GIF89a"):
        return "image/gif"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    return "image/jpeg"


@router.post(
    "/describe",
    response_model=DescribeResponse,
    summary="Describe an image via URL or base64",
    description=(
        "Accepts either a public image URL/local path (`image`) "
        "or a base64-encoded image string (`image_base64`). "
        "Supply exactly one of the two fields."
    ),
)
async def describe(body: DescribeRequest) -> DescribeResponse:
    description = await describe_image(body)
    return DescribeResponse(description=description, model=get_model_name())


@router.post(
    "/describe/upload",
    response_model=DescribeResponse,
    summary="Describe an image via multipart file upload",
    description=(
        "Upload an image file as raw bytes (multipart/form-data). "
        "The bytes are converted to a base64 data URI before processing, "
        "so the same pipeline is used as the JSON endpoint."
    ),
)
async def describe_upload(
    file: bytes = File(..., description="Raw image bytes to describe"),
) -> DescribeResponse:
    mime_type = _detect_mime(file)
    data_uri = f"data:{mime_type};base64,{base64.b64encode(file).decode()}"
    request = DescribeRequest(image_base64=data_uri, mime_type=mime_type)
    description = await describe_image(request)
    return DescribeResponse(description=description, model=get_model_name())

