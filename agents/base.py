import os

from google.adk.models.lite_llm import LiteLlm

from core.config import settings


def get_ollama_model() -> LiteLlm:
    """
    Return a LiteLlm instance configured for the local Ollama server.

    Uses ollama_chat provider (required for proper context handling).
    The OLLAMA_API_BASE env var is consumed directly by LiteLLM internally.
    """
    os.environ.setdefault("OLLAMA_API_BASE", settings.ollama_api_base)
    return LiteLlm(model=f"ollama_chat/{settings.ollama_model}")
