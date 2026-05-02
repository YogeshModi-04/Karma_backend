from fastapi import APIRouter

from services.vision.dependencies import RunnerDep, SessionServiceDep
from services.vision.schemas import DescribeRequest, DescribeResponse
from services.vision.service import describe_image, get_model_name

router = APIRouter(prefix="/vision", tags=["Vision"])


@router.post(
    "/describe",
    response_model=DescribeResponse,
    summary="Generate a description for an image",
    description=(
        "Accepts a local file path or a public image URL and returns a detailed "
        "natural-language description produced by Gemma 4 E4B running on Ollama."
    ),
)
async def describe(
    body: DescribeRequest,
    runner: RunnerDep,
    session_service: SessionServiceDep,
) -> DescribeResponse:
    description = await describe_image(body.image, runner, session_service)
    return DescribeResponse(description=description, model=get_model_name())
