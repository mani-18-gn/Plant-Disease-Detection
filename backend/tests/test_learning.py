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
from backend.db.models.logs.advisory import Advisory, AdvisoryPriority, AdvisorySource
from backend.db.models.logs.feedback import Feedback
from backend.auth.jwt_handler import hash_password, create_access_token
from backend.agents.learning.q_learning import (
    normalize_reward,
    extract_state_key,
    extract_action_key,
    compute_cell_q_value,
    get_learning_score,
    MIN_CELL_OBSERVATIONS,
)

client = TestClient(app)


def test_reward_normalization_pure_logic():
    """Verify reward centering and normalization r = (rating - 3)/2."""
    assert normalize_reward(5) == 1.0
    assert normalize_reward(4) == 0.5
    assert normalize_reward(3) == 0.0
    assert normalize_reward(2) == -0.5
    assert normalize_reward(1) == -1.0


def test_state_and_action_key_extraction():
    """Verify state and action discretization keys."""
    snapshot = {
        "diagnosis": {"predicted_disease": "mahali_koleroga"},
        "weather": {"disease_risk_score": 85.0},
        "market": {"price_trend": "rising"},
    }
    state_k = extract_state_key(snapshot)
    assert state_k == "koleroga:urgent:rising"

    action_k = extract_action_key("urgent", ["Spray 1% Bordeaux mixture on nut bunches"])
    assert action_k == "urgent:fungicide_spray"

    action_yld = extract_action_key("high", ["Apply Zinc Sulfate and Magnesium Sulfate foliar spray"])
    assert action_yld == "high:nutrient_amendment"


def test_q_learning_cell_specific_threshold_pure_logic(monkeypatch):
    """Verify cell-specific threshold guardrail and value convergence."""
    from datetime import datetime, timezone

    class MockFeedback:
        def __init__(self, rating):
            self.rating = rating
            self.created_at = datetime.now(timezone.utc)

    # 1. Below cell threshold (2 ratings < 3)
    below_thresh = [(MockFeedback(5), None), (MockFeedback(5), None)]
    q_val, count = compute_cell_q_value(below_thresh)
    assert count == 2
    assert q_val > 0.0

    # 2. Above cell threshold (3 positive ratings of 5 stars)
    pos_feedbacks = [(MockFeedback(5), None), (MockFeedback(5), None), (MockFeedback(5), None)]
    q_pos, count_pos = compute_cell_q_value(pos_feedbacks)
    assert count_pos == 3
    assert q_pos > 0.20  # alpha=0.1 smooth increase toward 1.0

    # 3. Negative feedback (3 ratings of 1 star)
    neg_feedbacks = [(MockFeedback(1), None), (MockFeedback(1), None), (MockFeedback(1), None)]
    q_neg, count_neg = compute_cell_q_value(neg_feedbacks)
    assert count_neg == 3
    assert q_neg < -0.20  # smooth decrease toward -1.0


@pytest.fixture(scope="module")
def setup_learning_env():
    db = SessionLocal()
    try:
        for name in ["test_learn_user_a", "test_learn_user_b"]:
            u = db.query(User).filter(User.username == name).first()
            if u:
                db.delete(u)
        db.commit()

        u_a = User(username="test_learn_user_a", phone="9888888881", password_hash=hash_password("p1"), role=UserRole.FARMER)
        u_b = User(username="test_learn_user_b", phone="9888888882", password_hash=hash_password("p2"), role=UserRole.FARMER)
        db.add_all([u_a, u_b])
        db.commit()

        token_a = create_access_token({"sub": str(u_a.id)})
        token_b = create_access_token({"sub": str(u_b.id)})

        h_a = {"Authorization": f"Bearer {token_a}"}
        h_b = {"Authorization": f"Bearer {token_b}"}

        prof_a = FarmerProfile(user_id=u_a.id, full_name="Learning Tester A")
        db.add(prof_a)
        db.commit()

        farm_a = Farm(farmer_id=prof_a.id, farm_name="Learning Farm A", latitude=13.9299, longitude=75.5681)
        db.add(farm_a)
        db.commit()

        block_a = CropBlock(farm_id=farm_a.id, block_name="Learning Block A", variety="Mohitnagar", planting_date="2018-01-01")
        db.add(block_a)
        db.commit()

        # Create Advisory for User A
        adv_a = Advisory(
            farmer_id=str(prof_a.id),
            crop_block_id=str(block_a.id),
            priority=AdvisoryPriority.URGENT,
            message="Spray 1% Bordeaux mixture immediately.",
            generated_by=AdvisorySource.RULE_FALLBACK,
            input_snapshot={
                "diagnosis": {"predicted_disease": "mahali_koleroga"},
                "weather": {"disease_risk_score": 85.0},
                "market": {"price_trend": "rising"},
                "recommended_actions": ["Spray 1% Bordeaux mixture"],
            },
        )
        db.add(adv_a)
        db.commit()

        prof_b = FarmerProfile(user_id=u_b.id, full_name="Learning Tester B")
        db.add(prof_b)
        db.commit()

        yield {
            "h_a": h_a,
            "h_b": h_b,
            "block_a_id": str(block_a.id),
            "adv_a_id": str(adv_a.id),
        }
    finally:
        for name in ["test_learn_user_a", "test_learn_user_b"]:
            u = db.query(User).filter(User.username == name).first()
            if u:
                db.delete(u)
        db.commit()
        db.close()


def test_learning_router_endpoints_and_feedback_flow(setup_learning_env):
    h_a = setup_learning_env["h_a"]
    h_b = setup_learning_env["h_b"]
    block_a_id = setup_learning_env["block_a_id"]
    adv_a_id = setup_learning_env["adv_a_id"]

    # 1. User A submits 5-star feedback for their advisory
    payload = {
        "advisory_id": adv_a_id,
        "rating": 5,
        "outcome_notes": "Bordeaux mixture applied in time, nut rot controlled effectively.",
    }
    res = client.post("/api/v1/agents/learning/feedback", json=payload, headers=h_a)
    assert res.status_code == 201, res.text
    data = res.json()
    assert data["rating"] == 5
    assert data["normalized_reward"] == 1.0
    assert data["state_key"] == "koleroga:urgent:rising"
    assert data["action_key"] == "urgent:fungicide_spray"
    assert data["cell_observations"] >= 1

    # 2. Get crop block feedback summary
    res_sum = client.get(f"/api/v1/agents/learning/summary/crop_block/{block_a_id}", headers=h_a)
    assert res_sum.status_code == 200
    sum_data = res_sum.json()
    assert sum_data["total_feedback_count"] >= 1
    assert sum_data["average_rating"] == 5.0

    # 3. Query Q-learning score endpoint
    res_score = client.get("/api/v1/agents/learning/score?state_key=koleroga:urgent:rising&action_key=urgent:fungicide_spray")
    assert res_score.status_code == 200
    score_data = res_score.json()
    assert "q_value" in score_data
    assert "learning_score" in score_data
    assert score_data["required_observations"] == 3

    # 4. Cross-farmer security rejection (User B trying to submit feedback for User A's advisory)
    res_b = client.post("/api/v1/agents/learning/feedback", json=payload, headers=h_b)
    assert res_b.status_code == 403, "User B should be forbidden from submitting feedback for User A's advisory"


if __name__ == "__main__":
    pytest.main(["-v", __file__])
