import io
import sys
import os
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
from backend.agents.diagnosis.bayesian import compute_posterior, get_hybrid_prior, LITERATURE_PRIORS

client = TestClient(app)


def test_bayesian_posterior_pure_logic():
    """Test pure Bayesian posterior calculation and validation threshold (>0.75)."""
    # 1. High confidence detection + High humidity/weather favorability (Koleroga outbreak)
    post1, val1 = compute_posterior(
        cnn_confidence=0.92,
        weather_risk_score=85.0,
        predicted_disease="mahali_koleroga",
        historical_prior=0.30,
        is_synthetic_weather=False,
    )
    assert post1 > 0.75, f"Expected posterior > 0.75, got {post1}"
    assert val1 is True, "Expected validated=True for high-confidence outbreak"

    # 2. Low confidence detection + Dry weather
    post2, val2 = compute_posterior(
        cnn_confidence=0.45,
        weather_risk_score=15.0,
        predicted_disease="mahali_koleroga",
        historical_prior=0.30,
        is_synthetic_weather=False,
    )
    assert post2 < 0.75, f"Expected posterior < 0.75, got {post2}"
    assert val2 is False, "Expected validated=False for low-confidence dry conditions"

    # 3. Synthetic weather dampening test: synthetic weather shrinks weather likelihood toward 0.5
    post_real, _ = compute_posterior(cnn_confidence=0.80, weather_risk_score=95.0, predicted_disease="yellow_leaf_disease", historical_prior=0.20, is_synthetic_weather=False)
    post_synth, _ = compute_posterior(cnn_confidence=0.80, weather_risk_score=95.0, predicted_disease="yellow_leaf_disease", historical_prior=0.20, is_synthetic_weather=True)
    # Synthetic weather does not boost posterior as extremely as verified real weather
    assert post_synth < post_real


def test_literature_priors_normalization():
    """Confirm all 9 literature priors sum to exactly 1.00."""
    total_prior = sum(LITERATURE_PRIORS.values())
    assert round(total_prior, 4) == 1.0000, f"Priors must sum to 1.0, got {total_prior}"


@pytest.fixture(scope="module")
def setup_diagnosis_env():
    db = SessionLocal()
    try:
        # Cleanup
        for name in ["test_diag_user_a", "test_diag_user_b"]:
            u = db.query(User).filter(User.username == name).first()
            if u:
                db.delete(u)
        db.commit()

        # Users A & B
        u_a = User(username="test_diag_user_a", phone="9555555551", password_hash=hash_password("p1"), role=UserRole.FARMER)
        u_b = User(username="test_diag_user_b", phone="9555555552", password_hash=hash_password("p2"), role=UserRole.FARMER)
        db.add_all([u_a, u_b])
        db.commit()

        token_a = create_access_token({"sub": str(u_a.id)})
        token_b = create_access_token({"sub": str(u_b.id)})

        h_a = {"Authorization": f"Bearer {token_a}"}
        h_b = {"Authorization": f"Bearer {token_b}"}

        # Create Profile & Farm & Crop Block for User A
        prof_a = FarmerProfile(user_id=u_a.id, full_name="Diagnosis Tester A")
        db.add(prof_a)
        db.commit()

        farm_a = Farm(farmer_id=prof_a.id, farm_name="Diagnosis Farm A", latitude=13.9299, longitude=75.5681)
        db.add(farm_a)
        db.commit()

        block_a = CropBlock(farm_id=farm_a.id, block_name="Diagnosis Block A", planting_date="2020-01-01")
        db.add(block_a)
        db.commit()

        # Create unvalidated detection record for User A
        det_a = DiseaseDetection(
            crop_block_id=str(block_a.id),
            image_path="uploads/test_diagnosis_leaf.jpg",
            predicted_disease="mahali_koleroga",
            cnn_confidence=0.95,
            posterior_probability=None,
            validated=False,
        )
        db.add(det_a)
        db.commit()
        db.refresh(det_a)

        # Create Profile for User B
        prof_b = FarmerProfile(user_id=u_b.id, full_name="Diagnosis Tester B")
        db.add(prof_b)
        db.commit()

        yield {
            "h_a": h_a,
            "h_b": h_b,
            "det_a_id": str(det_a.id),
        }
    finally:
        for name in ["test_diag_user_a", "test_diag_user_b"]:
            u = db.query(User).filter(User.username == name).first()
            if u:
                db.delete(u)
        db.commit()
        db.close()


def test_diagnosis_router_validate_endpoint(setup_diagnosis_env):
    h_a = setup_diagnosis_env["h_a"]
    h_b = setup_diagnosis_env["h_b"]
    det_a_id = setup_diagnosis_env["det_a_id"]

    # 1. User A validates their detection record
    res1 = client.post(f"/api/v1/agents/diagnosis/validate/{det_a_id}", headers=h_a)
    assert res1.status_code == 200, res1.text
    data1 = res1.json()
    assert data1["id"] == det_a_id
    assert data1["posterior_probability"] is not None
    assert data1["posterior_probability"] > 0.70
    assert data1["validated"] is True

    # 2. Cross-farmer security rejection (User B trying to validate User A's detection)
    res_b = client.post(f"/api/v1/agents/diagnosis/validate/{det_a_id}", headers=h_b)
    assert res_b.status_code == 403, "User B should be forbidden from validating User A's disease detection"


if __name__ == "__main__":
    pytest.main(["-v", __file__])
