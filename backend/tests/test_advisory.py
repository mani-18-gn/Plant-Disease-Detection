import io
import sys
import os
import json
import pytest
import httpx
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.main import app
from backend.config import settings
from backend.db.session import SessionLocal
from backend.db.models.core.user import User, UserRole
from backend.db.models.core.farmer_profile import FarmerProfile
from backend.db.models.core.farm import Farm
from backend.db.models.core.crop_block import CropBlock
from backend.db.models.agronomy.disease_detection import DiseaseDetection
from backend.db.models.logs.advisory import Advisory, AdvisoryPriority, AdvisorySource
from backend.auth.jwt_handler import hash_password, create_access_token
from backend.agents.advisory.rule_based_fallback import generate_rule_based_advisory
from backend.agents.advisory.gemini_client import generate_gemini_advisory
from backend.agents.advisory.cache import get_cached_advisory

client = TestClient(app)


def test_rule_based_fallback_pure_logic():
    """Test deterministic rule-based priority matrix across known agronomic scenarios."""
    # 1. Urgent Koleroga Outbreak
    koleroga_ctx = {
        "crop_block": {"block_name": "North Slope"},
        "diagnosis": {"predicted_disease": "mahali_koleroga", "posterior_probability": 0.95, "validated": True},
        "weather": {"disease_risk_score": 85.0, "rainfall_mm": 20.0, "humidity": 92.0},
        "recent_activities": {"days_since_last_spray": 30},
    }
    adv1 = generate_rule_based_advisory(koleroga_ctx)
    assert adv1["priority"] == "urgent"
    assert "Bordeaux" in str(adv1["recommended_actions"])
    assert "Fruit Rot" in adv1["message"]
    assert "Extension Officer" in adv1["disclaimer"]

    # 2. High Yellow Leaf Disease
    yld_ctx = {
        "crop_block": {"block_name": "Valley Block"},
        "diagnosis": {"predicted_disease": "yellow_leaf_disease", "posterior_probability": 0.88, "validated": True},
        "weather": {"disease_risk_score": 45.0},
    }
    adv2 = generate_rule_based_advisory(yld_ctx)
    assert adv2["priority"] == "high"
    assert "Yellow Leaf Disease" in adv2["message"]

    # 3. Medium Rising Market Price + Healthy Crop
    market_ctx = {
        "crop_block": {"block_name": "Plateau Block"},
        "diagnosis": {"predicted_disease": "healthy_leaf", "validated": True},
        "weather": {"disease_risk_score": 25.0},
        "market": {"mandi_name": "Shivamogga APMC", "price_trend": "rising"},
    }
    adv3 = generate_rule_based_advisory(market_ctx)
    assert adv3["priority"] == "medium"
    assert "Delay harvesting" in str(adv3["recommended_actions"])

    # 4. Low Normal Routine
    low_ctx = {
        "crop_block": {"block_name": "Base Block"},
        "diagnosis": {"predicted_disease": "healthy_leaf", "validated": True},
        "weather": {"disease_risk_score": 15.0, "rainfall_mm": 5.0, "humidity": 70.0},
        "market": {"price_trend": "stable"},
    }
    adv4 = generate_rule_based_advisory(low_ctx)
    assert adv4["priority"] == "low"


def test_gemini_client_well_formed_and_malformed_fallback(monkeypatch):
    """Test Gemini client JSON parsing and automatic fallback on malformed response."""
    test_ctx = {
        "crop_block": {"block_name": "Test Block"},
        "diagnosis": {"predicted_disease": "mahali_koleroga", "validated": True},
        "weather": {"disease_risk_score": 80.0},
    }

    # 1. Test Well-Formed Gemini Mock Response
    def mock_gemini_success(self, url, json=None, **kwargs):
        class MockResp:
            status_code = 200
            def json(self):
                return {
                    "candidates": [{
                        "content": {
                            "parts": [{
                                "text": json_dumps({
                                    "priority": "urgent",
                                    "message": "Immediate protective spray required.",
                                    "recommended_actions": ["Apply 1% Bordeaux mixture"],
                                    "reasoning_summary": "High disease risk."
                                })
                            }]
                        }
                    }]
                }
        return MockResp()

    from json import dumps as json_dumps
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "mock-test-key")
    monkeypatch.setattr(httpx.Client, "post", mock_gemini_success)
    res_success = generate_gemini_advisory(test_ctx)
    assert res_success["generated_by"] == "gemini"
    assert res_success["priority"] == "urgent"

    # 2. Test Malformed Response Fallback
    def mock_gemini_malformed(self, url, json=None, **kwargs):
        class MockResp:
            status_code = 200
            def json(self):
                return {
                    "candidates": [{"content": {"parts": [{"text": "THIS IS INVALID NON-JSON"}]}}]
                }
        return MockResp()

    monkeypatch.setattr(httpx.Client, "post", mock_gemini_malformed)
    res_fallback = generate_gemini_advisory(test_ctx)
    assert res_fallback["generated_by"] == "rule_fallback"
    assert res_fallback["priority"] == "urgent"


@pytest.fixture(scope="module")
def setup_advisory_env():
    db = SessionLocal()
    try:
        # Cleanup
        for name in ["test_adv_user_a", "test_adv_user_b"]:
            u = db.query(User).filter(User.username == name).first()
            if u:
                db.delete(u)
        db.commit()

        # Users A & B
        u_a = User(username="test_adv_user_a", phone="9666666661", password_hash=hash_password("p1"), role=UserRole.FARMER)
        u_b = User(username="test_adv_user_b", phone="9666666662", password_hash=hash_password("p2"), role=UserRole.FARMER)
        db.add_all([u_a, u_b])
        db.commit()

        token_a = create_access_token({"sub": str(u_a.id)})
        token_b = create_access_token({"sub": str(u_b.id)})

        h_a = {"Authorization": f"Bearer {token_a}"}
        h_b = {"Authorization": f"Bearer {token_b}"}

        # Create Profile & Farm & Crop Block for User A
        prof_a = FarmerProfile(user_id=u_a.id, full_name="Advisory Tester A", preferred_mandi="Shivamogga APMC")
        db.add(prof_a)
        db.commit()

        farm_a = Farm(farmer_id=prof_a.id, farm_name="Advisory Farm A", latitude=13.9299, longitude=75.5681)
        db.add(farm_a)
        db.commit()

        block_a = CropBlock(farm_id=farm_a.id, block_name="Advisory Block A", variety="Mohitnagar", planting_date="2018-01-01")
        db.add(block_a)
        db.commit()

        # Create Profile for User B
        prof_b = FarmerProfile(user_id=u_b.id, full_name="Advisory Tester B")
        db.add(prof_b)
        db.commit()

        yield {
            "h_a": h_a,
            "h_b": h_b,
            "prof_a_id": str(prof_a.id),
            "block_a_id": str(block_a.id),
        }
    finally:
        for name in ["test_adv_user_a", "test_adv_user_b"]:
            u = db.query(User).filter(User.username == name).first()
            if u:
                db.delete(u)
        db.commit()
        db.close()


def test_advisory_router_endpoints_and_cache(setup_advisory_env):
    h_a = setup_advisory_env["h_a"]
    h_b = setup_advisory_env["h_b"]
    prof_a_id = setup_advisory_env["prof_a_id"]
    block_a_id = setup_advisory_env["block_a_id"]

    # 1. User A generates advisory for Block A
    payload = {"crop_block_id": block_a_id}
    res1 = client.post("/api/v1/agents/advisory/generate", json=payload, headers=h_a)
    assert res1.status_code == 200, res1.text
    data1 = res1.json()
    adv1_id = data1["id"]
    assert "priority" in data1
    assert "message" in data1
    assert len(data1["recommended_actions"]) > 0
    assert data1["generated_by"] in ["gemini", "rule_fallback"]

    # 2. Caching verification: immediate repeat call should return same advisory ID
    res2 = client.post("/api/v1/agents/advisory/generate", json=payload, headers=h_a)
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["id"] == adv1_id, "Cache hit should return identical advisory ID"

    # 3. List farmer advisories
    res_list = client.get(f"/api/v1/agents/advisory/farmer/{prof_a_id}", headers=h_a)
    assert res_list.status_code == 200
    list_data = res_list.json()
    assert len(list_data) >= 1

    # 4. Cross-farmer security rejection (User B trying to generate advisory for User A's crop block)
    res_b = client.post("/api/v1/agents/advisory/generate", json=payload, headers=h_b)
    assert res_b.status_code == 403, "User B should be forbidden from generating advisory for User A's block"


if __name__ == "__main__":
    pytest.main(["-v", __file__])
