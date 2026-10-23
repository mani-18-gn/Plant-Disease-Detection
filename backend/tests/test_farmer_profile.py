import sys
import os
import pytest
from datetime import date
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.main import app
from backend.db.session import SessionLocal
from backend.db.models.core.user import User, UserRole
from backend.auth.jwt_handler import hash_password, create_access_token

client = TestClient(app)


@pytest.fixture(scope="module")
def setup_users():
    db = SessionLocal()
    try:
        # Cleanup any existing test users
        for name in ["test_farmer_alpha", "test_farmer_beta"]:
            u = db.query(User).filter(User.username == name).first()
            if u:
                db.delete(u)
        db.commit()

        # Create Farmer Alpha
        user_a = User(
            username="test_farmer_alpha",
            phone="9000000001",
            password_hash=hash_password("pass123"),
            role=UserRole.FARMER,
        )
        # Create Farmer Beta
        user_b = User(
            username="test_farmer_beta",
            phone="9000000002",
            password_hash=hash_password("pass123"),
            role=UserRole.FARMER,
        )
        db.add_all([user_a, user_b])
        db.commit()
        db.refresh(user_a)
        db.refresh(user_b)

        token_a = create_access_token({"sub": str(user_a.id)})
        token_b = create_access_token({"sub": str(user_b.id)})

        headers_a = {"Authorization": f"Bearer {token_a}"}
        headers_b = {"Authorization": f"Bearer {token_b}"}

        yield {
            "user_a": user_a,
            "user_b": user_b,
            "headers_a": headers_a,
            "headers_b": headers_b,
        }
    finally:
        # Teardown test users
        for name in ["test_farmer_alpha", "test_farmer_beta"]:
            u = db.query(User).filter(User.username == name).first()
            if u:
                db.delete(u)
        db.commit()
        db.close()


def test_create_and_read_farmer_profile(setup_users):
    headers = setup_users["headers_a"]

    # 1. Create Profile
    res = client.post(
        "/api/v1/core/profile",
        json={
            "full_name": "Alpha Gowda",
            "village": "Sagar",
            "taluk": "Sagar",
            "district": "Shivamogga",
            "state": "Karnataka",
            "pincode": "577401",
            "preferred_language": "kn",
            "preferred_mandi": "Sagar APMC",
        },
        headers=headers,
    )
    assert res.status_code == 201, res.text
    profile_data = res.json()
    assert profile_data["full_name"] == "Alpha Gowda"
    assert profile_data["district"] == "Shivamogga"

    # 2. Read Profile
    res_get = client.get("/api/v1/core/profile", headers=headers)
    assert res_get.status_code == 200
    assert res_get.json()["id"] == profile_data["id"]

    # 3. Update Profile
    res_put = client.put(
        "/api/v1/core/profile",
        json={"full_name": "Alpha Gowda Updated", "preferred_mandi": "Shivamogga APMC"},
        headers=headers,
    )
    assert res_put.status_code == 200
    assert res_put.json()["full_name"] == "Alpha Gowda Updated"


def test_farm_and_crop_block_crud(setup_users):
    headers_a = setup_users["headers_a"]
    headers_b = setup_users["headers_b"]

    # Create profile for Beta so 403 authorization checks work properly
    client.post(
        "/api/v1/core/profile",
        json={"full_name": "Beta Gowda"},
        headers=headers_b,
    )

    # 1. Farmer Alpha creates a Farm
    res_farm = client.post(
        "/api/v1/core/farms",
        json={
            "farm_name": "Alpha North Farm",
            "latitude": 14.1667,
            "longitude": 75.0333,
            "total_area_acres": 3.0,
            "soil_type": "Red Soil",
            "irrigation_type": "drip",
        },
        headers=headers_a,
    )
    assert res_farm.status_code == 201, res_farm.text
    farm_a = res_farm.json()
    farm_a_id = farm_a["id"]

    # 2. Farmer Alpha creates a Crop Block under Farm A
    res_block = client.post(
        "/api/v1/core/crop-blocks",
        json={
            "farm_id": farm_a_id,
            "block_name": "Block 1",
            "variety": "Mangala",
            "planting_date": "2018-05-15",
            "number_of_trees": 250,
            "spacing_meters": 2.7,
            "status": "active",
        },
        headers=headers_a,
    )
    assert res_block.status_code == 201, res_block.text
    block_a = res_block.json()
    assert block_a["age_years"] > 5.0

    # 3. Cross-farmer Access Rejection (Farmer B trying to access Farmer A's Farm / Crop Block)
    res_b_farm = client.get(f"/api/v1/core/farms/{farm_a_id}", headers=headers_b)
    assert res_b_farm.status_code == 403, "Farmer B should be forbidden from accessing Farmer A's farm"

    res_b_block = client.get(f"/api/v1/core/crop-blocks/{block_a['id']}", headers=headers_b)
    assert res_b_block.status_code == 403, "Farmer B should be forbidden from accessing Farmer A's crop block"

    # 4. Status Update by Farmer A
    res_status = client.patch(
        f"/api/v1/core/crop-blocks/{block_a['id']}/status",
        json={"status": "replanted"},
        headers=headers_a,
    )
    assert res_status.status_code == 200
    assert res_status.json()["status"] == "replanted"


if __name__ == "__main__":
    pytest.main(["-v", __file__])
