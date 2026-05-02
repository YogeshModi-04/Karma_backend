"""
Tests for POST /verification/verify and the helper endpoints.

Two layers:
  - Unit tests (mock_litellm fixture) — fast, no Ollama needed.
  - Live integration test (marked `live`) — requires `ollama` running with gemma4:e4b.
    Run with:  pytest -m live tests/services/test_verification.py -s
"""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from gateway.main import create_app

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

MOCK_DESCRIPTION = (
    "A young neem tree sapling in a small plastic bag filled with dark soil. "
    "The sapling is about 30 cm tall with four fresh green leaves. "
    "It is placed on bare earth near a park boundary wall in an urban setting."
)


@pytest.fixture()
def mock_litellm(mocker):
    """Patch litellm.acompletion so no real Ollama call is made."""

    def _make_response(content: str):
        choice = MagicMock()
        choice.message.content = content
        response = MagicMock()
        response.choices = [choice]
        return response

    patcher = mocker.patch(
        "services.verification.service.litellm.acompletion",
        new_callable=AsyncMock,
    )
    # Default: model returns a clean Approved verdict
    patcher.return_value = _make_response(
        json.dumps({"verdict": "Approved", "comment": "Image clearly shows a sapling being planted."})
    )
    return patcher


@pytest.fixture()
def verify_client(mock_litellm):
    """TestClient with litellm mocked — no Ollama required."""
    app = create_app()
    with TestClient(app) as c:
        yield c


# ---------------------------------------------------------------------------
# Helper: valid request body
# ---------------------------------------------------------------------------

BASE_BODY = {
    "image_description": MOCK_DESCRIPTION,
    "action_id": "ENV-P01",
    "title": "Planted neem sapling at community park",
    "description": "I planted a neem sapling near the boundary wall of Vastrapur lake garden.",
    "location": {"area": "Vastrapur", "city": "Ahmedabad"},
}


# ---------------------------------------------------------------------------
# Unit tests — mocked LLM
# ---------------------------------------------------------------------------


def test_verify_approved(verify_client):
    """Happy path — model says Approved."""
    resp = verify_client.post("/verification/verify", json=BASE_BODY)
    assert resp.status_code == 200
    data = resp.json()

    assert data["verdict"] == "Approved"
    assert data["action_id"] == "ENV-P01"
    assert data["action_name"] == "Plant a tree (sapling)"
    assert data["category_name"] == "Environment & Green Cover"
    assert data["points"] == 50
    assert len(data["comment"]) > 0


def test_verify_rejected(verify_client, mock_litellm):
    """Model returns Rejected — fields still populated correctly."""
    mock_litellm.return_value = MagicMock(
        choices=[
            MagicMock(
                message=MagicMock(
                    content=json.dumps({
                        "verdict": "Rejected",
                        "comment": "Image shows a concrete wall, no sapling visible.",
                    })
                )
            )
        ]
    )
    resp = verify_client.post("/verification/verify", json=BASE_BODY)
    assert resp.status_code == 200
    assert resp.json()["verdict"] == "Rejected"
    assert "concrete wall" in resp.json()["comment"]


def test_verify_human_review(verify_client, mock_litellm):
    """Model returns Human Review when evidence is ambiguous."""
    mock_litellm.return_value = MagicMock(
        choices=[
            MagicMock(
                message=MagicMock(
                    content=json.dumps({
                        "verdict": "Human Review",
                        "comment": "Cannot confirm sapling species from image.",
                    })
                )
            )
        ]
    )
    resp = verify_client.post("/verification/verify", json=BASE_BODY)
    assert resp.status_code == 200
    assert resp.json()["verdict"] == "Human Review"


def test_verify_garbled_llm_output_falls_back_to_human_review(verify_client, mock_litellm):
    """If the model returns non-JSON gibberish, parse_verdict must fall back gracefully."""
    mock_litellm.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content="Sorry, I cannot help with that."))]
    )
    resp = verify_client.post("/verification/verify", json=BASE_BODY)
    assert resp.status_code == 200
    assert resp.json()["verdict"] == "Human Review"


def test_verify_json_embedded_in_prose(verify_client, mock_litellm):
    """parse_verdict should extract JSON even when the model wraps it in prose."""
    prose = (
        'After careful analysis I have reached this conclusion:\n'
        '{"verdict": "Approved", "comment": "Sapling clearly visible."}\n'
        'Thank you for your submission.'
    )
    mock_litellm.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content=prose))]
    )
    resp = verify_client.post("/verification/verify", json=BASE_BODY)
    assert resp.status_code == 200
    assert resp.json()["verdict"] == "Approved"


def test_verify_unknown_action_id(verify_client):
    """Unknown action_id must return 400 without calling the LLM."""
    body = {**BASE_BODY, "action_id": "FAKE-X99"}
    resp = verify_client.post("/verification/verify", json=body)
    assert resp.status_code == 400


def test_verify_missing_fields(verify_client):
    """Incomplete request body must return 422 (Pydantic validation)."""
    resp = verify_client.post("/verification/verify", json={"action_id": "ENV-P01"})
    assert resp.status_code == 422


def test_verify_negative_action(verify_client, mock_litellm):
    """Negative karma actions (e.g. ENV-N01) should also be verifiable."""
    mock_litellm.return_value = MagicMock(
        choices=[
            MagicMock(
                message=MagicMock(
                    content=json.dumps({
                        "verdict": "Approved",
                        "comment": "Image confirms illegal tree felling activity.",
                    })
                )
            )
        ]
    )
    body = {
        **BASE_BODY,
        "action_id": "ENV-N01",
        "title": "Illegal tree cutting spotted",
        "description": "Witnessed unauthorized felling of trees near the railway track.",
    }
    resp = verify_client.post("/verification/verify", json=body)
    assert resp.status_code == 200
    data = resp.json()
    assert data["action_id"] == "ENV-N01"
    assert data["points"] < 0  # negative action → negative points


# ---------------------------------------------------------------------------
# Helper endpoint tests
# ---------------------------------------------------------------------------


def test_list_actions(verify_client):
    """/verification/actions returns all 22 categories."""
    resp = verify_client.get("/verification/actions")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 22
    assert "ENV" in data
    assert "positive" in data["ENV"]
    assert "negative" in data["ENV"]
    assert "ENV-P01" in data["ENV"]["positive"]


def test_get_action_detail(verify_client):
    """/verification/actions/{id} returns full action detail."""
    resp = verify_client.get("/verification/actions/ENV-P01")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == "ENV-P01"
    assert data["points"] == 50


def test_get_action_detail_not_found(verify_client):
    """/verification/actions/{id} returns 404 for unknown IDs."""
    resp = verify_client.get("/verification/actions/NOPE-X00")
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Live integration test — requires Ollama running with gemma4:e4b
# ---------------------------------------------------------------------------


@pytest.mark.live
@pytest.mark.asyncio
async def test_live_verify_real_model():
    """
    End-to-end call against the real Ollama model.
    Run: pytest -m live tests/services/test_verification.py::test_live_verify_real_model -s
    """
    from services.verification.schemas import VerifyRequest
    from services.verification.service import verify_action

    request = VerifyRequest(
        image_description=MOCK_DESCRIPTION,
        action_id="ENV-P01",
        title="Planted neem sapling at community park",
        description="I planted a neem sapling near the boundary wall of Vastrapur lake garden.",
        location={"area": "Vastrapur", "city": "Ahmedabad"},
    )

    result = await verify_action(request)

    print("\n--- Live verification result ---")
    print(f"Action   : {result.action_name} ({result.action_id})")
    print(f"Category : {result.category_name}")
    print(f"Points   : {result.points}")
    print(f"Verdict  : {result.verdict}")
    print(f"Comment  : {result.comment}")
    print("--------------------------------")

    assert result.verdict in {"Approved", "Rejected", "Human Review"}
    assert len(result.comment) > 10
    assert result.action_id == "ENV-P01"
    assert result.points == 50
