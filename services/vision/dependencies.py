from typing import Annotated

from fastapi import Depends
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from agents.session_manager import get_runner, get_session_service

RunnerDep = Annotated[Runner, Depends(get_runner)]
SessionServiceDep = Annotated[InMemorySessionService, Depends(get_session_service)]
