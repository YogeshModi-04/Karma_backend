import urllib.request

from fastapi import APIRouter

from core.config import settings
from core.exceptions import OllamaUnavailableError

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/", summary="Liveness check")
async def liveness() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ollama", summary="Check Ollama connectivity")
async def ollama_health() -> dict[str, str]:
    """Verify the Ollama server is reachable and the model is available."""
    try:
        url = f"{settings.ollama_api_base}/api/tags"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=5):  # noqa: S310
            pass
    except Exception as exc:
        raise OllamaUnavailableError() from exc
    return {"status": "ok", "ollama_url": settings.ollama_api_base, "model": settings.ollama_model}
