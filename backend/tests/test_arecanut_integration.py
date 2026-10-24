"""
Automated Integration Tests for the Trained 9-Class Arecanut CNN Vision Agent.

Covers:
1. All nine Arecanut disease and healthy classes:
   - bud_borer
   - healthy_foot
   - healthy_leaf
   - healthy_nut
   - healthy_trunk
   - mahali_koleroga
   - stem_cracking
   - stem_bleeding
   - yellow_leaf_disease
2. Unsupported crops and non-plant inputs.
3. Low-confidence predictions and blurry input handling.
4. Missing model weights handling (graceful 503 / ModelNotAvailableError).
5. Robust backend error rejection (corrupted files, empty payloads, invalid MIME types).
6. Crop-block consistency and multi-crop preservation.
"""

import io
from pathlib import Path
import pytest
from PIL import Image, ImageFilter
from fastapi.testclient import TestClient

from backend.main import app
from backend.config import settings
from backend.agents.vision.model import CLASS_NAMES
from backend.agents.vision.inference import (
    run_vision_inference,
    run_pytorch_vision_inference,
    get_pytorch_model,
    ModelNotAvailableError,
)
from backend.agents.vision.advisory_db import get_diagnosis_advisory

client = TestClient(app)
SAMPLE_DIR = Path(__file__).resolve().parent.parent / "data" / "test_labeled_samples"
DATASET_TEST_DIR = Path(__file__).resolve().parents[2] / "data" / "Arecanut_dataset" / "dataset" / "test"


def load_sample_bytes_for_class(class_name: str) -> bytes:
    """Helper to locate genuine test image bytes for a class."""
    # Check test_labeled_samples first
    target_sample = SAMPLE_DIR / f"Arecanut___{class_name}___sample.jpg"
    if target_sample.exists():
        with open(target_sample, "rb") as f:
            return f.read()

    # Fallback to dataset test directory
    class_idx = CLASS_NAMES.index(class_name)
    folder = DATASET_TEST_DIR / str(class_idx)
    if folder.exists():
        files = list(folder.glob("*.jpg")) + list(folder.glob("*.png")) + list(folder.glob("*.jpeg"))
        if files:
            with open(files[0], "rb") as f:
                return f.read()

    raise FileNotFoundError(f"Could not locate sample image for Arecanut class: {class_name}")


@pytest.mark.parametrize("class_name", CLASS_NAMES)
def test_all_nine_arecanut_classes_inference(class_name: str):
    """
    Test that every one of the 9 Arecanut classes runs genuine neural inference,
    resolves to the Arecanut crop, returns valid confidence, and retrieves
    verified ICAR-CPCRI / UAS Bangalore bilingual advisory.
    """
    img_bytes = load_sample_bytes_for_class(class_name)
    res = run_pytorch_vision_inference(img_bytes)

    assert res["crop"] == "Arecanut"
    assert res["crop_kn"] == "ಅಡಿಕೆ"
    assert "Areca catechu" in res["scientific_name"]
    assert res["backend"] == "pytorch"
    assert res["is_plant"] is True
    assert isinstance(res["confidence"], float)
    assert 0.0 <= res["confidence"] <= 1.0

    # Top predictions list
    assert len(res["top_predictions"]) >= 1
    top_pred = res["top_predictions"][0]
    assert top_pred["crop"] == "Arecanut"
    assert "condition" in top_pred
    assert "confidence" in top_pred

    # Advisory checks
    assert len(res["symptoms"]) > 0
    assert len(res["symptoms_kn"]) > 0
    assert len(res["differential_diagnosis"]) > 0
    assert len(res["differential_diagnosis_kn"]) > 0
    assert len(res["sources"]) >= 1
    assert any("CPCRI" in s.get("title", "") or "CPCRI" in s.get("institution", "") for s in res["sources"])

    # Raw class must be a valid member of CLASS_NAMES
    assert res["raw_class"] in CLASS_NAMES


@pytest.mark.parametrize("class_name", CLASS_NAMES)
def test_detect_endpoint_arecanut_classes(class_name: str):
    """Test API endpoint POST /api/v1/agents/vision/detect with all 9 classes."""
    img_bytes = load_sample_bytes_for_class(class_name)

    res = client.post(
        "/api/v1/agents/vision/detect",
        data={"crop_type": "Arecanut"},
        files={"file": (f"{class_name}.jpg", img_bytes, "image/jpeg")},
    )
    assert res.status_code == 201
    data = res.json()

    assert data["crop"] == "Arecanut"
    assert data["crop_kn"] == "ಅಡಿಕೆ"
    assert data["cnn_confidence"] > 0.0
    assert len(data["top_predictions"]) >= 1
    assert data["backend"] == "pytorch"
    assert "Strawberry" not in data["predicted_disease"]


def test_unsupported_crop_non_plant_rejection():
    """Verify that synthetic non-plant subjects are not forced into Arecanut categories."""
    img = Image.new("RGB", (256, 256), color=(20, 40, 220))  # Solid blue
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    blue_bytes = buf.getvalue()

    res = run_pytorch_vision_inference(blue_bytes)
    assert res["inconclusive"] is True
    assert res["is_plant"] is False
    assert "Non-Plant" in res["predicted_disease"]
    assert res["confidence"] == 0.0


def test_non_arecanut_crop_preservation():
    """Verify supported crops (e.g., Tomato) preserve their 38-class classification and do not collide with Arecanut."""
    sample_tomato = SAMPLE_DIR / "Tomato___Early_blight___0012b9d2-2130-4a06-a834-b1f3af34f57e___RS_Erly.B 8389.JPG"
    assert sample_tomato.exists()

    with open(sample_tomato, "rb") as f:
        img_bytes = f.read()

    res = run_vision_inference(img_bytes)
    assert res["crop"] == "Tomato"
    assert res["condition"] == "Early Blight"
    assert res["confidence"] >= 0.70
    assert "Strawberry" not in res["predicted_disease"]
    assert "Arecanut" not in res["predicted_disease"]


def test_blurry_image_returns_inconclusive():
    """Verify that severely blurry photographs return an inconclusive result (Requirement 6)."""
    # Create an image and apply extreme Gaussian blur
    img_bytes = load_sample_bytes_for_class("mahali_koleroga")
    img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    blurred = img.filter(ImageFilter.GaussianBlur(radius=25))

    buf = io.BytesIO()
    blurred.save(buf, format="JPEG")
    blurry_bytes = buf.getvalue()

    res = run_pytorch_vision_inference(blurry_bytes)
    assert res["inconclusive"] is True
    assert "Blurry" in res["predicted_disease"] or res["confidence"] < 0.40


def test_low_confidence_yields_inconclusive():
    """Verify that ambiguous/featureless inputs return Inconclusive instead of inventing a disease."""
    # Flat neutral gray image
    img = Image.new("RGB", (224, 224), color=(80, 100, 60))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")

    res = run_pytorch_vision_inference(buf.getvalue())
    assert res["inconclusive"] is True
    assert res["predicted_disease"] == "Inconclusive" or "Inconclusive" in res["predicted_disease"]


def test_missing_model_file_handling(monkeypatch):
    """Verify that when weights file is missing, ModelNotAvailableError is raised and 503 is returned."""
    import backend.agents.vision.inference as inf_mod

    orig_cache = inf_mod._pytorch_model_cache
    try:
        inf_mod._pytorch_model_cache = None
        # Mock get_pytorch_model to return None
        monkeypatch.setattr(inf_mod, "get_pytorch_model", lambda: None)

        with pytest.raises(ModelNotAvailableError):
            inf_mod.run_pytorch_vision_inference(create_sample_bytes())

        # Calling endpoint should return 503
        res = client.post(
            "/api/v1/agents/vision/detect",
            data={"crop_type": "Arecanut"},
            files={"file": ("leaf.jpg", create_sample_bytes(), "image/jpeg")},
        )
        assert res.status_code == 503
        assert "missing" in res.json()["detail"].lower() or "unavailable" in res.json()["detail"].lower()
    finally:
        inf_mod._pytorch_model_cache = orig_cache


def test_corrupted_image_rejection():
    """Verify corrupted bytes return 400 Bad Request."""
    res = client.post(
        "/api/v1/agents/vision/detect",
        data={"crop_type": "Arecanut"},
        files={"file": ("broken.jpg", b"NOT_A_VALID_JPEG_HEADER_RANDOM_GARBAGE", "image/jpeg")},
    )
    assert res.status_code == 400
    assert "corrupted" in res.json()["detail"].lower() or "unreadable" in res.json()["detail"].lower()


def test_empty_file_rejection():
    """Verify empty files return 400 Bad Request."""
    res = client.post(
        "/api/v1/agents/vision/detect",
        data={"crop_type": "Arecanut"},
        files={"file": ("empty.jpg", b"", "image/jpeg")},
    )
    assert res.status_code == 400
    assert "empty" in res.json()["detail"].lower()


def test_invalid_mime_type_rejection():
    """Verify non-image MIME types return 400 Bad Request."""
    res = client.post(
        "/api/v1/agents/vision/detect",
        data={"crop_type": "Arecanut"},
        files={"file": ("document.pdf", b"%PDF-1.4...", "application/pdf")},
    )
    assert res.status_code == 400
    assert "unsupported" in res.json()["detail"].lower()


def create_sample_bytes() -> bytes:
    """Helper to create small valid JPEG bytes."""
    img = Image.new("RGB", (224, 224), color=(34, 139, 34))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()
