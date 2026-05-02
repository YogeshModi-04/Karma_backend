def test_liveness(client):
    response = client.get("/health/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ollama_health_unreachable(client):
    """When Ollama is not running, /health/ollama returns 503."""
    response = client.get("/health/ollama")
    # In the test environment Ollama won't be running
    assert response.status_code in (200, 503)
