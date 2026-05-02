import pytest
from fastapi.testclient import TestClient

from agents import session_manager
from gateway.main import create_app


@pytest.fixture()
def mock_runner(mocker):
    """Return a lightweight mock Runner that yields a final description event."""
    mock = mocker.AsyncMock()

    async def _fake_run_async(**_kwargs):
        event = mocker.MagicMock()
        event.is_final_response.return_value = True
        part = mocker.MagicMock()
        part.text = "A beautiful sunset over the mountains."
        event.content.parts = [part]
        yield event

    mock.run_async.side_effect = _fake_run_async
    return mock


@pytest.fixture()
def mock_session_service(mocker):
    svc = mocker.AsyncMock()
    session = mocker.MagicMock()
    session.id = "test-session-id"
    svc.create_session.return_value = session
    return svc


@pytest.fixture()
def client(mock_runner, mock_session_service):
    app = create_app()
    app.dependency_overrides[session_manager.get_runner] = lambda: mock_runner
    app.dependency_overrides[session_manager.get_session_service] = (
        lambda: mock_session_service
    )
    with TestClient(app) as c:
        yield c
