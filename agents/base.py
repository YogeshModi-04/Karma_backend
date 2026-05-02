import os
import re
import warnings

import litellm
from google.adk.models.lite_llm import LiteLlm

from core.config import settings

# Suppress harmless Pydantic serialization mismatch warnings that fire when
# Ollama's response shape doesn't perfectly match LiteLLM's internal models.
warnings.filterwarnings(
    "ignore",
    message="Pydantic serializer warnings",
    category=UserWarning,
    module="pydantic",
)
litellm.suppress_debug_info = True

# Matches Gemma 4 thinking blocks: <|channel>thought\n...<channel|>
_THINKING_BLOCK_RE = re.compile(
    r"<\|channel>thought\n.*?<channel\|>",
    re.DOTALL,
)


def get_ollama_model() -> LiteLlm:
    """
    Return a LiteLlm instance configured for the local Ollama server
    with thinking mode disabled.
    """
    os.environ.setdefault("OLLAMA_API_BASE", settings.ollama_api_base)
    return LiteLlm(
        model=f"ollama_chat/{settings.ollama_model}",
        # Disable Gemma 4 chain-of-thought thinking mode.
        # Ollama 0.7+ honours `think: false` in the options payload.
        extra_body={"options": {"think": False}},
    )


def strip_thinking_tokens(text: str) -> str:
    """Remove any Gemma 4 thinking-block markup that leaked into the output."""
    return _THINKING_BLOCK_RE.sub("", text).strip()
