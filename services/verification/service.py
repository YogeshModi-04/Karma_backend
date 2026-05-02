import litellm

from agents.verification_agent import build_verification_messages, parse_verdict
from agents.base import strip_thinking_tokens
from core.config import settings
from core.exceptions import AgentError
from core.karma_registry import karma_registry
from services.verification.schemas import VerifyRequest, VerifyResponse


async def verify_action(request: VerifyRequest) -> VerifyResponse:
    """
    Core verification logic:

    1. Look up the claimed action in the karma registry.
    2. Build an LLM prompt combining action rules + image description + user context.
    3. Call the model and parse the structured verdict.
    4. Return a VerifyResponse with verdict + comment + action metadata.
    """
    action = karma_registry.get_action(request.action_id)
    if action is None:
        from core.exceptions import ImageLoadError  # reuse 400-level exception
        raise ImageLoadError(
            f"Unknown action_id '{request.action_id}'. "
            "Check /verification/actions for valid IDs."
        )

    messages = build_verification_messages(
        action=action,
        image_description=request.image_description,
        title=request.title,
        user_description=request.description,
        area=request.location.area,
        city=request.location.city,
    )

    response = await litellm.acompletion(
        model=f"ollama_chat/{settings.ollama_model}",
        messages=messages,
        api_base=settings.ollama_api_base,
        extra_body={"options": {"think": False}},
    )

    raw: str = response.choices[0].message.content or ""
    if not raw.strip():
        raise AgentError("The verification model returned an empty response.")

    raw = strip_thinking_tokens(raw)
    verdict_data = parse_verdict(raw)

    return VerifyResponse(
        action_id=action["id"],
        action_name=action["action"],
        category_id=action["category_id"],
        category_name=action["category_name"],
        points=action.get("points", 0),
        verdict=verdict_data["verdict"],
        comment=verdict_data["comment"],
    )
