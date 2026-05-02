import base64

import litellm

from core.config import settings
from core.exceptions import AgentError, ImageLoadError
from core.image_loader import load_image, load_image_base64
from agents.base import strip_thinking_tokens
from agents.image_agent import IMAGE_AGENT_INSTRUCTION
from services.vision.schemas import DescribeRequest


def _resolve_image(request: DescribeRequest) -> tuple[bytes, str]:
    """Extract image bytes and MIME type from whichever field the client supplied."""
    if request.image_base64:
        return load_image_base64(request.image_base64, request.mime_type)
    if request.image:
        return load_image(request.image)
    raise ImageLoadError("Provide either 'image' (path/URL) or 'image_base64'.")


async def _call_model(image_bytes: bytes, mime_type: str) -> str:
    """
    Send the image directly to Ollama via LiteLLM using the OpenAI vision format.

    ADK's inline_data → LiteLLM content conversion drops the image in some
    versions, so we bypass the ADK runner here and call LiteLLM directly to
    guarantee the image arrives at the model.
    """
    b64 = base64.b64encode(image_bytes).decode()
    data_uri = f"data:{mime_type};base64,{b64}"

    response = await litellm.acompletion(
        model=f"ollama_chat/{settings.ollama_model}",
        messages=[
            {"role": "system", "content": IMAGE_AGENT_INSTRUCTION},
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": data_uri}},
                    {"type": "text", "text": "Describe this image."},
                ],
            },
        ],
        api_base=settings.ollama_api_base,
        extra_body={"options": {"think": False}},
    )

    content: str = response.choices[0].message.content or ""
    if not content.strip():
        raise AgentError("The model returned an empty response.")

    return strip_thinking_tokens(content)


async def describe_image(request: DescribeRequest) -> str:
    """
    Resolve image from request and return model description.

    Args:
        request: Validated DescribeRequest (path/URL or base64).

    Returns:
        Plain-text structured description.

    Raises:
        ImageLoadError: If the image cannot be loaded.
        AgentError:     If the model returns no content.
    """
    image_bytes, mime_type = _resolve_image(request)
    return await _call_model(image_bytes, mime_type)


def get_model_name() -> str:
    return settings.ollama_model

