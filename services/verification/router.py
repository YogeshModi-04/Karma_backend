from fastapi import APIRouter

from core.karma_registry import karma_registry
from services.verification.schemas import VerifyRequest, VerifyResponse
from services.verification.service import verify_action

router = APIRouter(prefix="/verification", tags=["Verification"])


@router.post(
    "/verify",
    response_model=VerifyResponse,
    summary="Verify a karma action submission",
    description=(
        "Pass the AI-generated image description, the claimed action ID, "
        "the user's title + description, and their location. "
        "Returns a verdict of **Approved**, **Rejected**, or **Human Review** "
        "with a plain-English comment explaining the decision."
    ),
)
async def verify(body: VerifyRequest) -> VerifyResponse:
    return await verify_action(body)


@router.get(
    "/actions",
    summary="List all valid action IDs",
    description="Returns every action ID in the karma rule book, grouped by category.",
)
def list_actions() -> dict:
    result = {}
    for cat in karma_registry.categories:
        result[cat["id"]] = {
            "name": cat["name"],
            "positive": [a["id"] for a in cat["positive"]],
            "negative": [a["id"] for a in cat["negative"]],
        }
    return result


@router.get(
    "/actions/{action_id}",
    summary="Get full details of a single action",
)
def get_action(action_id: str) -> dict:
    from fastapi import HTTPException

    action = karma_registry.get_action(action_id)
    if action is None:
        raise HTTPException(status_code=404, detail=f"Action '{action_id}' not found.")
    return action
