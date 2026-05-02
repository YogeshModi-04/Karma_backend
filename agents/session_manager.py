from contextlib import asynccontextmanager
from typing import AsyncIterator

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from agents.image_agent import create_image_agent

APP_NAME = "karma_backend"

_session_service: InMemorySessionService | None = None
_runner: Runner | None = None


@asynccontextmanager
async def lifespan() -> AsyncIterator[None]:
    """Initialise the ADK runner on startup; clean up on shutdown."""
    global _session_service, _runner
    _session_service = InMemorySessionService()
    _runner = Runner(
        agent=create_image_agent(),
        app_name=APP_NAME,
        session_service=_session_service,
    )
    yield
    _session_service = None
    _runner = None


def get_runner() -> Runner:
    if _runner is None:
        raise RuntimeError("ADK Runner has not been initialised.")
    return _runner


def get_session_service() -> InMemorySessionService:
    if _session_service is None:
        raise RuntimeError("SessionService has not been initialised.")
    return _session_service
