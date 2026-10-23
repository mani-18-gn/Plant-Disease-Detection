import sys
import os
import uuid
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.main import app
from backend.db.session import SessionLocal
from backend.db.models.core.user import User, UserRole
from backend.db.models.core.farmer_profile import FarmerProfile
from backend.db.models.core.farm import Farm
from backend.db.models.core.crop_block import CropBlock
from backend.db.models.agronomy.disease_detection import DiseaseDetection
from backend.auth.jwt_handler import hash_password, create_access_token
from backend.agents.coordinator.weights import (
    compute_situation_score,
    compute_diagnosis_severity,
    compute_weather_urgency,
    compute_market_urgency,
    DIAGNOSIS_WEIGHT,
    WEATHER_WEIGHT,
    MARKET_WEIGHT,
    LEARNING_WEIGHT,
)

client = TestClient(app)


def test_coordinator_weights_pure_logic():
    """Test Table 4.6 consensus calculation across known scenarios."""
    # 1. Urgent Fungal Outbreak Case (Koleroga + Severe Monsoon Weather)
    diag1 = {"predicted_disease": "mahali_koleroga", "posterior_probability": 0.95, "validated": True}
    weather1 = {"disease_risk_score": 85.0, "disease_risk_level": "urgent", "humidity": 92.0, "rainfall_mm": 18.0}
    market1 = {"price_trend": "rising", "current_price_per_kg": 478.50}

    score1 = compute_situation_score(diag1, weather1, market1)
    assert score1["composite_score"] >= 75.0
    assert score1["urgency_level"] == "urgent"
    assert "diagnosis" in score1["urgency_drivers"]
    assert "weather" in score1["urgency_drivers"]
    assert score1["learning_component_status"] == "placeholder_neutral_50_pending_learning_agent"
    assert score1["components"]["diagnosis"]["weight"] == 0.35
    assert score1["components"]["weather"]["weight"] == 0.30
    assert score1["components"]["market"]["weight"] == 0.20
    assert score1["components"]["learning"]["weight"] == 0.15

    # 2. Market Selling Urgency Case (Falling price trend on healthy crop)
    diag2 = {"predicted_disease": "healthy_leaf", "posterior_probability": 0.98, "validated": True}
    weather2 = {"disease_risk_score": 20.0, "disease_risk_level": "low"}
    market2 = {"price_trend": "falling", "current_price_per_kg": 420.0}

    score2 = compute_situation_score(diag2, weather2, market2)
    assert score2["urgency_drivers"] == ["market"]
    assert score2["components"]["market"]["raw_score"] == 80.0

    # 3. Low Risk Baseline Case
    diag3 = {"predicted_disease": "healthy_leaf", "posterior_probability": 1.0, "validated": True}
    weather3 = {"disease_risk_score": 15.0, "disease_risk_level": "low"}
    market3 = {"price_trend": "stable", "current_price_per_kg": 475.0}

    score3 = compute_situation_score(diag3, weather3, market3)
    assert score3["composite_score"] < 40.0
    assert score3["urgency_level"] == "low"
    assert score3["urgency_drivers"] == []


@pytest.fixture(scope="module")
def setup_coordinator_env():
    db = SessionLocal()
    try:
        for name in ["test_coord_user_a", "test_coord_user_b"]:
            u = db.query(User).filter(User.username == name).first()
            if u:
                db.delete(u)
        db.commit()

        u_a = User(username="test_coord_user_a", phone="9777777771", password_hash=hash_password("p1"), role=UserRole.FARMER)
        u_b = User(username="test_coord_user_b", phone="9777777772", password_hash=hash_password("p2"), role=UserRole.FARMER)
        db.add_all([u_a, u_b])
        db.commit()

        token_a = create_access_token({"sub": str(u_a.id)})
        token_b = create_access_token({"sub": str(u_b.id)})

        h_a = {"Authorization": f"Bearer {token_a}"}
        h_b = {"Authorization": f"Bearer {token_b}"}

        prof_a = FarmerProfile(user_id=u_a.id, full_name="Coordinator Tester A", preferred_mandi="Shivamogga APMC")
        db.add(prof_a)
        db.commit()

        farm_a = Farm(farmer_id=prof_a.id, farm_name="Coordinator Farm A", latitude=13.9299, longitude=75.5681)
        db.add(farm_a)
        db.commit()

        block_a = CropBlock(farm_id=farm_a.id, block_name="Coordinator Block A", variety="Mohitnagar", planting_date="2018-01-01")
        db.add(block_a)
        db.commit()

        # Seed detection for User A
        det_a = DiseaseDetection(
            crop_block_id=str(block_a.id),
            image_path="uploads/test_coord_leaf.jpg",
            predicted_disease="mahali_koleroga",
            cnn_confidence=0.94,
            posterior_probability=0.92,
            validated=True,
        )
        db.add(det_a)
        db.commit()

        prof_b = FarmerProfile(user_id=u_b.id, full_name="Coordinator Tester B")
        db.add(prof_b)
        db.commit()

        yield {
            "h_a": h_a,
            "h_b": h_b,
            "block_a_id": str(block_a.id),
            "det_a_id": str(det_a.id),
        }
    finally:
        for name in ["test_coord_user_a", "test_coord_user_b"]:
            u = db.query(User).filter(User.username == name).first()
            if u:
                db.delete(u)
        db.commit()
        db.close()


def test_coordinator_synthesize_endpoint_end_to_end(setup_coordinator_env):
    h_a = setup_coordinator_env["h_a"]
    h_b = setup_coordinator_env["h_b"]
    block_a_id = setup_coordinator_env["block_a_id"]
    det_a_id = setup_coordinator_env["det_a_id"]

    # 1. User A requests synthesis for Block A
    payload = {"crop_block_id": block_a_id, "detection_id": det_a_id}
    res = client.post("/api/v1/agents/coordinator/synthesize", json=payload, headers=h_a)
    assert res.status_code == 200, res.text
    data = res.json()

    # Verify root fields
    assert data["crop_block_id"] == block_a_id
    assert "situation_score" in data
    assert "diagnosis" in data
    assert "weather" in data
    assert "market" in data
    assert "advisory" in data

    # Verify situation score structure
    sit = data["situation_score"]
    assert 0.0 <= sit["composite_score"] <= 100.0
    assert sit["urgency_level"] in ["urgent", "high", "moderate", "low"]
    assert sit["learning_component_status"] == "placeholder_neutral_50_pending_learning_agent"
    assert "diagnosis" in sit["components"]
    assert "weather" in sit["components"]
    assert "market" in sit["components"]
    assert "learning" in sit["components"]

    # Verify advisory structure
    adv = data["advisory"]
    assert adv["priority"] in ["urgent", "high", "medium", "low"]
    assert len(adv["recommended_actions"]) > 0

    # 2. Cross-farmer security rejection (User B trying to access User A's crop block)
    res_b = client.post("/api/v1/agents/coordinator/synthesize", json=payload, headers=h_b)
    assert res_b.status_code == 403, "User B should receive 403 Forbidden for User A's crop block"


def test_coordinator_partial_failure_resilience(setup_coordinator_env, monkeypatch):
    """Test Coordinator returns gracefully when Weather Agent fails."""
    h_a = setup_coordinator_env["h_a"]
    block_a_id = setup_coordinator_env["block_a_id"]

    # Mock weather failure and cache miss
    def mock_weather_fail(*args, **kwargs):
        raise ConnectionError("Weather API Down")

    from backend.agents.coordinator import orchestrator
    monkeypatch.setattr(orchestrator, "fetch_live_weather", mock_weather_fail)
    monkeypatch.setattr(orchestrator, "get_grid_region_key", lambda lat, lon: f"uncached_test_region_{uuid.uuid4().hex[:6]}")

    payload = {"crop_block_id": block_a_id}
    res = client.post("/api/v1/agents/coordinator/synthesize", json=payload, headers=h_a)
    assert res.status_code == 200, "Coordinator should handle partial failure gracefully"
    data = res.json()
    assert data["weather"]["status"] == "partial_fallback"
    assert data["situation_score"]["components"]["weather"]["status"] == "partial_fallback"
    assert data["situation_score"]["composite_score"] > 0.0


if __name__ == "__main__":
    pytest.main(["-v", __file__])
