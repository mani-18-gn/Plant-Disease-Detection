import sys
import os
import pytest
from datetime import date, timedelta
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.main import app
from backend.db.session import SessionLocal
from backend.db.models.core.user import User, UserRole
from backend.auth.jwt_handler import hash_password, create_access_token

client = TestClient(app)


@pytest.fixture(scope="module")
def setup_activity_env():
    db = SessionLocal()
    try:
        # Cleanup
        for name in ["test_act_user_1", "test_act_user_2"]:
            u = db.query(User).filter(User.username == name).first()
            if u:
                db.delete(u)
        db.commit()

        # User 1 & 2
        u1 = User(username="test_act_user_1", phone="9111111111", password_hash=hash_password("p1"), role=UserRole.FARMER)
        u2 = User(username="test_act_user_2", phone="9222222222", password_hash=hash_password("p2"), role=UserRole.FARMER)
        db.add_all([u1, u2])
        db.commit()

        token1 = create_access_token({"sub": str(u1.id)})
        token2 = create_access_token({"sub": str(u2.id)})

        h1 = {"Authorization": f"Bearer {token1}"}
        h2 = {"Authorization": f"Bearer {token2}"}

        # Create Profile & Farm & Crop Block for User 1
        client.post("/api/v1/core/profile", json={"full_name": "Activity Tester 1"}, headers=h1)
        res_f = client.post("/api/v1/core/farms", json={"farm_name": "Act Farm 1"}, headers=h1)
        farm_id = res_f.json()["id"]

        res_b = client.post(
            "/api/v1/core/crop-blocks",
            json={
                "farm_id": farm_id,
                "block_name": "Act Block 1",
                "planting_date": "2020-01-01",
            },
            headers=h1,
        )
        block_id = res_b.json()["id"]

        # Create Profile for User 2
        client.post("/api/v1/core/profile", json={"full_name": "Activity Tester 2"}, headers=h2)

        yield {
            "h1": h1,
            "h2": h2,
            "block_id": block_id,
        }
    finally:
        for name in ["test_act_user_1", "test_act_user_2"]:
            u = db.query(User).filter(User.username == name).first()
            if u:
                db.delete(u)
        db.commit()
        db.close()


def test_log_and_filter_activities(setup_activity_env):
    h1 = setup_activity_env["h1"]
    h2 = setup_activity_env["h2"]
    block_id = setup_activity_env["block_id"]

    today = date.today()

    # 1. User 1 logs 3 activities
    res1 = client.post(
        "/api/v1/core/activities",
        json={
            "crop_block_id": block_id,
            "activity_type": "fertilizer",
            "activity_date": str(today - timedelta(days=20)),
            "product_used": "Organic Compost",
            "quantity": 100.0,
            "quantity_unit": "kg",
            "cost": 1500.0,
            "logged_via": "app",
        },
        headers=h1,
    )
    assert res1.status_code == 201, res1.text

    res2 = client.post(
        "/api/v1/core/activities",
        json={
            "crop_block_id": block_id,
            "activity_type": "spraying",
            "activity_date": str(today - timedelta(days=5)),
            "product_used": "Bordeaux Mixture 1%",
            "quantity": 15.0,
            "quantity_unit": "litre",
            "cost": 600.0,
            "logged_via": "app",
        },
        headers=h1,
    )
    assert res2.status_code == 201

    res3 = client.post(
        "/api/v1/core/activities",
        json={
            "crop_block_id": block_id,
            "activity_type": "spraying",
            "activity_date": str(today - timedelta(days=1)),
            "product_used": "Neem Oil 0.5%",
            "quantity": 10.0,
            "quantity_unit": "litre",
            "logged_via": "app",
        },
        headers=h1,
    )
    assert res3.status_code == 201

    # 2. List all activities for block
    res_list = client.get(f"/api/v1/core/crop-blocks/{block_id}/activities", headers=h1)
    assert res_list.status_code == 200
    assert len(res_list.json()) == 3

    # 3. Filter by activity_type=spraying
    res_spray = client.get(
        f"/api/v1/core/crop-blocks/{block_id}/activities?activity_type=spraying",
        headers=h1,
    )
    assert res_spray.status_code == 200
    assert len(res_spray.json()) == 2
    assert res_spray.json()[0]["product_used"] == "Neem Oil 0.5%"

    # 4. Fetch latest activity of type spraying
    res_latest = client.get(
        f"/api/v1/core/crop-blocks/{block_id}/activities/latest?activity_type=spraying",
        headers=h1,
    )
    assert res_latest.status_code == 200
    assert res_latest.json()["product_used"] == "Neem Oil 0.5%"

    # 5. Cross-farmer access rejection (User 2 trying to log activity on User 1's block)
    res_hack = client.post(
        "/api/v1/core/activities",
        json={
            "crop_block_id": block_id,
            "activity_type": "irrigation",
            "activity_date": str(today),
        },
        headers=h2,
    )
    assert res_hack.status_code == 403, "User 2 should be forbidden from logging activity on User 1's block"


if __name__ == "__main__":
    pytest.main(["-v", __file__])
