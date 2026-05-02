import pytest


def test_describe_with_url(client, tmp_path):
    """POST /vision/describe with a URL-like path returns a description."""
    response = client.post("/vision/describe", json={"image": "http://example.com/img.jpg"})
    assert response.status_code == 200
    data = response.json()
    assert "description" in data
    assert "model" in data
    assert len(data["description"]) > 0


def test_describe_with_local_file(client, tmp_path):
    """POST /vision/describe with a real local PNG file returns a description."""
    img_file = tmp_path / "test.png"
    # Minimal 1×1 white PNG
    img_file.write_bytes(
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
        b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00"
        b"\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18"
        b"\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    response = client.post("/vision/describe", json={"image": str(img_file)})
    assert response.status_code == 200
    assert response.json()["description"] == "A beautiful sunset over the mountains."


def test_describe_missing_image_field(client):
    """POST /vision/describe without body returns 422."""
    response = client.post("/vision/describe", json={})
    assert response.status_code == 422


def test_describe_nonexistent_file(client):
    """POST /vision/describe with a non-existent file path returns 400."""
    response = client.post("/vision/describe", json={"image": "/nonexistent/path.jpg"})
    assert response.status_code == 400
