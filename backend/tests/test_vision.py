import io
import sys
import os
from pathlib import Path
import pytest
from PIL import Image
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.main import app
from backend.config import settings
from backend.db.session import SessionLocal
from backend.db.models.core.user import User, UserRole
from backend.db.models.core.farmer_profile import FarmerProfile
from backend.db.models.core.farm import Farm
from backend.db.models.core.crop_block import CropBlock
from backend.auth.jwt_handler import hash_password, create_access_token
from backend.agents.vision.inference import (
    run_vision_inference,
    run_multicrop_vision_inference,
    validate_plant_plausibility,
    ModelNotAvailableError,
)
from backend.agents.vision.advisory_db import (
    get_diagnosis_advisory,
    search_knowledge_base,
    get_all_supported_crops,
    CLASS_METADATA,
)

client = TestClient(app)


def create_sample_image_bytes(color=(34, 139, 34), size=(256, 256)) -> bytes:
    """Helper to generate a valid RGB JPEG image in bytes."""
    img = Image.new("RGB", size, color=color)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


@pytest.fixture(scope="module")
def setup_vision_env():
    db = SessionLocal()
    try:
        # Cleanup prior test data
        for name in ["test_vision_user_a", "test_vision_user_b"]:
            u = db.query(User).filter(User.username == name).first()
            if u:
                db.delete(u)
        db.commit()

        # Users A & B
        u_a = User(username="test_vision_user_a", phone="9333333331", password_hash=hash_password("p1"), role=UserRole.FARMER)
        u_b = User(username="test_vision_user_b", phone="9333333332", password_hash=hash_password("p2"), role=UserRole.FARMER)
        db.add_all([u_a, u_b])
        db.commit()

        token_a = create_access_token({"sub": str(u_a.id)})
        token_b = create_access_token({"sub": str(u_b.id)})

        h_a = {"Authorization": f"Bearer {token_a}"}
        h_b = {"Authorization": f"Bearer {token_b}"}

        # Create Profile & Farm & Crop Block for User A
        prof_a = FarmerProfile(user_id=u_a.id, full_name="Vision Tester A")
        db.add(prof_a)
        db.commit()

        farm_a = Farm(farmer_id=prof_a.id, farm_name="Vision Farm A")
        db.add(farm_a)
        db.commit()

        import datetime
        block_a = CropBlock(farm_id=farm_a.id, block_name="Vision Block A", variety="Tomato", planting_date=datetime.date(2020, 1, 1))
        db.add(block_a)
        db.commit()

        # Create Profile for User B
        prof_b = FarmerProfile(user_id=u_b.id, full_name="Vision Tester B")
        db.add(prof_b)
        db.commit()

        yield {
            "h_a": h_a,
            "h_b": h_b,
            "block_a_id": str(block_a.id),
        }
    finally:
        for name in ["test_vision_user_a", "test_vision_user_b"]:
            u = db.query(User).filter(User.username == name).first()
            if u:
                db.delete(u)
        db.commit()
        db.close()


def test_real_multicrop_inference():
    """Verify real inference runs on a valid image without fake stubs."""
    img_bytes = create_sample_image_bytes()
    res = run_vision_inference(img_bytes)

    assert "predicted_disease" in res
    assert "confidence" in res
    assert isinstance(res["confidence"], float)
    assert 0.0 <= res["confidence"] <= 1.0
    assert "inconclusive" in res
    assert "crop" in res
    assert "condition" in res
    assert "top_predictions" in res
    assert len(res["top_predictions"]) >= 1
    assert res.get("backend") == "multicrop"
    assert "differential_diagnosis" in res
    assert "sources" in res


def test_plant_plausibility_filter():
    """Verify plant plausibility check accepts foliage and flags non-plant images."""
    # 1. Green foliage
    leaf_img = Image.new("RGB", (200, 200), color=(40, 160, 40))
    leaf_check = validate_plant_plausibility(leaf_img)
    assert leaf_check["is_plant"] is True
    assert leaf_check["plant_coverage_pct"] > 50.0

    # 2. Solid metallic blue (non-plant)
    non_plant_img = Image.new("RGB", (200, 200), color=(20, 60, 200))
    buf = io.BytesIO()
    non_plant_img.save(buf, format="JPEG")
    res = run_multicrop_vision_inference(buf.getvalue())
    assert res["is_plant"] is False
    assert res["inconclusive"] is True
    assert "Non-Plant" in res["predicted_disease"]
    assert res["confidence"] == 0.0


def test_advisory_database_lookup():
    """Verify advisory knowledge base returns verified symptoms and management."""
    adv_tomato = get_diagnosis_advisory(class_index=29)  # Tomato Early blight
    assert adv_tomato["crop"] == "Tomato"
    assert "Early Blight" in adv_tomato["condition"]
    assert "Alternaria solani" in adv_tomato["causal_agent"]
    assert len(adv_tomato["symptoms"]) > 10
    assert len(adv_tomato["differential_diagnosis"]) > 10
    assert len(adv_tomato["chemical_management"]) > 10
    assert "sources" in adv_tomato
    assert len(adv_tomato["sources"]) >= 1
    assert adv_tomato["crop_kn"] == "ಟೊಮ್ಯಾಟೊ"


def test_bilingual_kannada_translations():
    """Verify Kannada language translations exist across key crop conditions."""
    for idx in [7, 20, 28, 29, 30]:  # Corn Rust, Potato Blight, Tomato Spot, Tomato Blight
        adv = get_diagnosis_advisory(class_index=idx)
        assert adv["crop_kn"] is not None and len(adv["crop_kn"]) > 0
        assert adv["condition_kn"] is not None and len(adv["condition_kn"]) > 0
        assert adv["symptoms_kn"] is not None and len(adv["symptoms_kn"]) > 0
        assert adv["differential_diagnosis_kn"] is not None and len(adv["differential_diagnosis_kn"]) > 0


def test_knowledge_base_search_endpoints():
    """Verify knowledge base API endpoints for search and supported crops."""
    # 1. Search endpoint
    res = client.get("/api/v1/agents/vision/knowledge-base?crop=Tomato")
    assert res.status_code == 200
    data = res.json()
    assert data["total_results"] >= 9
    assert any("Early Blight" in r["condition"] for r in data["results"])

    # 2. Crops catalog endpoint
    res_crops = client.get("/api/v1/agents/vision/knowledge-base/crops")
    assert res_crops.status_code == 200
    crops = res_crops.json()
    crop_names = [c["crop"] for c in crops]
    assert "Tomato" in crop_names
    assert "Potato" in crop_names
    assert "Arecanut" in crop_names
    assert "Rice (Paddy)" in crop_names


def test_sample_images_endpoint():
    """Verify sample benchmark images are served for 1-click evaluation."""
    res = client.get("/api/v1/agents/vision/sample-images")
    assert res.status_code == 200
    samples = res.json()
    assert len(samples) >= 8
    sample_names = [s["condition"] for s in samples]
    assert "Early Blight" in sample_names
    assert "Common Rust" in sample_names

    # Test downloading one sample image file
    first_file = samples[0]["filename"]
    res_img = client.get(f"/api/v1/agents/vision/sample-image-file/{first_file}")
    assert res_img.status_code == 200
    assert len(res_img.content) > 1000


def test_missing_weights_raises_unavailable(monkeypatch):
    """Verify that when weights are missing, no fake prediction is fabricated and 503 is returned."""
    import backend.agents.vision.inference as inf_mod

    orig_model = inf_mod._multicrop_model
    orig_proc = inf_mod._multicrop_processor
    try:
        inf_mod._multicrop_model = None
        inf_mod._multicrop_processor = None
        monkeypatch.setattr(inf_mod, "MULTICROP_WEIGHTS_DIR", inf_mod.Path("non_existent_weights_dir"))

        with pytest.raises(ModelNotAvailableError):
            inf_mod.run_multicrop_vision_inference(create_sample_image_bytes())
    finally:
        inf_mod._multicrop_model = orig_model
        inf_mod._multicrop_processor = orig_proc


def test_vision_status_endpoint():
    """Verify the vision status endpoint returns model status and supported crops."""
    res = client.get("/api/v1/agents/vision/status")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] in ["ready", "weights_missing"]
    assert "Tomato" in data["supported_crops"]
    assert "Potato" in data["supported_crops"]
    assert "Arecanut" in data["supported_crops"]
    assert data["total_supported_classes"] == 47


def test_vision_detect_endpoint_success(setup_vision_env):
    """User A posts a valid plant leaf image to their crop block."""
    h_a = setup_vision_env["h_a"]
    block_a_id = setup_vision_env["block_a_id"]
    img_bytes = create_sample_image_bytes()

    res = client.post(
        "/api/v1/agents/vision/detect",
        data={"crop_block_id": block_a_id},
        files={"file": ("leaf.jpg", img_bytes, "image/jpeg")},
        headers=h_a,
    )
    assert res.status_code == 201, res.text
    data = res.json()
    assert data["crop_block_id"] == block_a_id
    assert "predicted_disease" in data
    assert "cnn_confidence" in data
    assert data["cnn_confidence"] >= 0.0
    assert "crop" in data
    assert "condition" in data
    assert "top_predictions" in data
    assert "differential_diagnosis" in data
    assert "favorable_conditions" in data
    assert "sources" in data
    assert "is_plant" in data


def test_empty_file_rejected(setup_vision_env):
    """Reject empty uploaded files with 400 Bad Request."""
    h_a = setup_vision_env["h_a"]
    block_a_id = setup_vision_env["block_a_id"]

    res = client.post(
        "/api/v1/agents/vision/detect",
        data={"crop_block_id": block_a_id},
        files={"file": ("empty.jpg", b"", "image/jpeg")},
        headers=h_a,
    )
    assert res.status_code == 400
    assert "empty" in res.json()["detail"].lower()


def test_corrupted_image_rejected(setup_vision_env):
    """Reject corrupted/unreadable non-image bytes with 400 Bad Request."""
    h_a = setup_vision_env["h_a"]
    block_a_id = setup_vision_env["block_a_id"]

    corrupted_bytes = b"NOT_A_REAL_IMAGE_RANDOM_CORRUPT_BYTES_XYZ"
    res = client.post(
        "/api/v1/agents/vision/detect",
        data={"crop_block_id": block_a_id},
        files={"file": ("corrupt.jpg", corrupted_bytes, "image/jpeg")},
        headers=h_a,
    )
    assert res.status_code == 400
    assert "corrupted" in res.json()["detail"].lower() or "unreadable" in res.json()["detail"].lower()


def test_invalid_mime_type_rejected(setup_vision_env):
    """Reject unsupported file types (e.g. text/plain) with 400 Bad Request."""
    h_a = setup_vision_env["h_a"]
    block_a_id = setup_vision_env["block_a_id"]

    res = client.post(
        "/api/v1/agents/vision/detect",
        data={"crop_block_id": block_a_id},
        files={"file": ("document.txt", b"some plain text content", "text/plain")},
        headers=h_a,
    )
    assert res.status_code == 400
    assert "unsupported" in res.json()["detail"].lower()


def test_cross_farmer_access_rejected(setup_vision_env):
    """User B trying to detect on User A's crop block must receive 403 Forbidden."""
    h_b = setup_vision_env["h_b"]
    block_a_id = setup_vision_env["block_a_id"]
    img_bytes = create_sample_image_bytes()

    res_b = client.post(
        "/api/v1/agents/vision/detect",
        data={"crop_block_id": block_a_id},
        files={"file": ("leaf.jpg", img_bytes, "image/jpeg")},
        headers=h_b,
    )
    assert res_b.status_code == 403


def test_unauthenticated_request_rejected(setup_vision_env):
    """Requests with a specific crop_block_id but without Bearer token must receive 401 Unauthorized."""
    block_a_id = setup_vision_env["block_a_id"]
    img_bytes = create_sample_image_bytes()

    res = client.post(
        "/api/v1/agents/vision/detect",
        data={"crop_block_id": block_a_id},
        files={"file": ("leaf.jpg", img_bytes, "image/jpeg")},
    )
    assert res.status_code == 401


def test_preview_diagnosis_without_crop_block():
    """Unauthenticated or block-less evaluators can run safe preview diagnosis without persistence."""
    img_bytes = create_sample_image_bytes()

    res = client.post(
        "/api/v1/agents/vision/detect",
        files={"file": ("preview_leaf.jpg", img_bytes, "image/jpeg")},
    )
    assert res.status_code == 201
    data = res.json()
    assert data["crop_block_id"] is None
    assert "predicted_disease" in data
    assert "crop" in data
    assert "condition" in data
    assert "sources" in data


def test_arecanut_out_of_distribution_handling():
    """Targeting Arecanut with featureless input must return inconclusive with ICAR-CPCRI advisory, never Strawberry."""
    img_bytes = create_sample_image_bytes()

    res = client.post(
        "/api/v1/agents/vision/detect",
        data={"crop_type": "Arecanut"},
        files={"file": ("areca_leaf.jpg", img_bytes, "image/jpeg")},
    )
    assert res.status_code == 201
    data = res.json()
    assert data["is_inconclusive"] is True
    assert data["crop"] == "Arecanut"
    assert "Strawberry" not in data["predicted_disease"]
    assert len(data["sources"]) >= 1


def test_arbitrary_upload_arecanut_misclassification_prevented():
    """
    Arbitrary upload of an Arecanut Palm image (without specifying crop block/type)
    MUST NOT be misdiagnosed as Strawberry Leaf Scorch.
    """
    from pathlib import Path
    sample_areca = Path(__file__).resolve().parent.parent / "data" / "test_labeled_samples" / "Arecanut_Palm_Leaf_Field.webp"
    assert sample_areca.exists()

    with open(sample_areca, "rb") as f:
        img_bytes = f.read()

    # Upload with NO crop_type or crop_block_id (arbitrary web upload)
    res = client.post(
        "/api/v1/agents/vision/detect",
        files={"file": ("arecanut_unknown.webp", img_bytes, "image/webp")},
    )
    assert res.status_code == 201
    data = res.json()

    assert data["crop"] == "Arecanut"
    assert "Strawberry" not in data["predicted_disease"]
    assert data["crop_support_status"] == "supported"
    assert data["visual_similarity"] is not None
    assert len(data["visual_similarity"]) > 0
    assert data["visual_similarity"][0]["crop"] == "Arecanut"
    assert data["online_research"] is not None
    assert len(data["online_research"]) > 0


def test_supported_tomato_early_blight_benchmark():
    """
    Uploading genuine benchmark Tomato Early Blight image must return
    accurate Tomato Early Blight prediction with high confidence and corroborating research.
    """
    from pathlib import Path
    sample_tomato = Path(__file__).resolve().parent.parent / "data" / "test_labeled_samples" / "Tomato___Early_blight___0012b9d2-2130-4a06-a834-b1f3af34f57e___RS_Erly.B 8389.JPG"
    assert sample_tomato.exists()

    with open(sample_tomato, "rb") as f:
        img_bytes = f.read()

    res = client.post(
        "/api/v1/agents/vision/detect",
        files={"file": ("tomato_test.jpg", img_bytes, "image/jpeg")},
    )
    assert res.status_code == 201
    data = res.json()

    assert data["crop"] == "Tomato"
    assert data["condition"] == "Early Blight"
    assert data["cnn_confidence"] >= 0.70
    assert data["crop_support_status"] == "supported"
    assert data["visual_similarity"] is not None
    assert data["visual_similarity"][0]["crop"] == "Tomato"
    assert data["online_research"] is not None


@pytest.mark.asyncio
async def test_online_agricultural_research_service():
    """Verify backend-only research service returns valid peer-reviewed/institutional citations."""
    from backend.agents.vision.web_research import search_agricultural_research

    research = await search_agricultural_research(
        crop="Arecanut",
        condition="Fruit Rot Koleroga",
        causal_agent="Phytophthora meadii",
    )
    assert len(research) >= 1
    assert "title" in research[0]
    assert "journal" in research[0]
    assert "url" in research[0]


