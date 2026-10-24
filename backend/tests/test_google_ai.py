import io
import pytest
from PIL import Image
from fastapi.testclient import TestClient
from backend.main import app
from backend.agents.diagnosis.google_ai import (
    get_google_ai_status,
    is_google_ai_configured,
    diagnose_plant_with_google_ai,
)

client = TestClient(app)


def test_google_ai_status_endpoint():
    response = client.get("/api/diagnose/status")
    assert response.status_code == 200
    data = response.json()
    assert "sdk_installed" in data
    assert data["sdk_installed"] is True
    assert "primary_model" in data
    assert "gemini" in data["primary_model"].lower()


def test_google_ai_status_v1_endpoint():
    response = client.get("/api/v1/agents/diagnosis/google-ai/status")
    assert response.status_code == 200
    data = response.json()
    assert "sdk_installed" in data


def test_diagnose_endpoint_empty_file():
    files = {"file": ("empty.jpg", b"", "image/jpeg")}
    response = client.post("/api/diagnose", files=files)
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_diagnose_endpoint_unsupported_mimetype():
    files = {"file": ("test.pdf", b"%PDF-1.4 dummy content", "application/pdf")}
    response = client.post("/api/diagnose", files=files)
    assert response.status_code == 400
    assert "unsupported file format" in response.json()["detail"].lower()


def test_diagnose_endpoint_valid_image_structure():
    img = Image.new("RGB", (100, 100), color=(0, 128, 0))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)

    files = {"file": ("leaf.jpg", buf, "image/jpeg")}
    response = client.post("/api/diagnose", files=files, data={"crop_name": "Tomato"})
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "local_model_comparison" in data
    assert data["status"] in ["api_key_missing", "api_key_invalid", "success", "not_a_plant", "insufficient_evidence"]


@pytest.mark.asyncio
async def test_diagnose_corrupted_image_handling():
    corrupted_bytes = b"NOT_AN_IMAGE_DATA_CORRUPT"
    result = await diagnose_plant_with_google_ai(image_bytes=corrupted_bytes)
    assert result["status"] == "error"
    assert "decode" in result["error"].lower() or "corrupt" in result["error"].lower()
