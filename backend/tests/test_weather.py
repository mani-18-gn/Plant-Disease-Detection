import io
import sys
import os
import pytest
import httpx
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.main import app
from backend.db.session import SessionLocal
from backend.db.models.core.user import User, UserRole
from backend.db.models.core.farmer_profile import FarmerProfile
from backend.db.models.core.farm import Farm
from backend.db.models.env.weather_reading import WeatherReading, WeatherSource
from backend.auth.jwt_handler import hash_password, create_access_token
from backend.agents.weather.risk_score import calculate_disease_risk_score
from backend.agents.weather.arima_model import generate_weather_forecast
from backend.agents.weather.fallback_model import generate_fallback_forecast
from backend.agents.weather.api_client import fetch_live_weather
from backend.schemas.weather import DiseaseRiskLevel, LocationSource

client = TestClient(app)


def test_disease_risk_score_calculation():
    """Test pure risk score logic against known baseline inputs and synthetic flags."""
    # 1. Verified API risk condition
    high_risk = calculate_disease_risk_score(humidity=90.0, temperature=25.0, rainfall_mm=15.0, is_synthetic=False)
    assert high_risk.score >= 70.0
    assert high_risk.level in [DiseaseRiskLevel.HIGH, DiseaseRiskLevel.URGENT]
    assert high_risk.confidence_level == "verified_api"
    assert high_risk.is_synthetic is False

    # 2. Synthetic fallback risk condition
    synthetic_risk = calculate_disease_risk_score(humidity=90.0, temperature=25.0, rainfall_mm=15.0, is_synthetic=True)
    assert synthetic_risk.confidence_level == "unverified_synthetic"
    assert synthetic_risk.is_synthetic is True


def test_fallback_model_triggering():
    """Test that < 14 readings automatically triggers fallback model."""
    readings = []  # 0 readings < 14 threshold
    forecast = generate_weather_forecast(
        historical_readings=readings,
        current_temp=26.0,
        current_humidity=85.0,
        current_rainfall=10.0,
        periods=3,
    )
    assert len(forecast) == 3
    assert forecast[0].forecast_model == "exponential_moving_average"


def test_open_meteo_api_client_and_synthetic_fallback(monkeypatch):
    """Test Open-Meteo live API integration and synthetic fallback handling."""
    # 1. Test live Open-Meteo API response parsing
    def mock_open_meteo_get(self, url, *args, **kwargs):
        class MockResponse:
            status_code = 200
            def json(self):
                return {
                    "current": {
                        "temperature_2m": 27.2,
                        "relative_humidity_2m": 86.0,
                        "rain": 5.0,
                    }
                }
        return MockResponse()

    monkeypatch.setattr(httpx.Client, "get", mock_open_meteo_get)

    live_res = fetch_live_weather(lat=13.9299, lon=75.5681)
    assert live_res["temperature"] == 27.2
    assert live_res["humidity"] == 86.0
    assert live_res["rainfall_mm"] == 5.0
    assert live_res["weather_source"] == WeatherSource.API
    assert live_res["is_synthetic"] is False

    # 2. Test synthetic fallback path when Open-Meteo API raises connection error
    def mock_open_meteo_error(url, params=None, **kwargs):
        raise httpx.ConnectError("Network unreachable")

    monkeypatch.setattr(httpx.Client, "get", mock_open_meteo_error)

    fallback_res = fetch_live_weather(lat=13.9299, lon=75.5681)
    assert fallback_res["weather_source"] == WeatherSource.SYNTHETIC_FALLBACK
    assert fallback_res["is_synthetic"] is True


@pytest.fixture(scope="module")
def setup_weather_env():
    db = SessionLocal()
    try:
        # Cleanup
        for name in ["test_weather_user_a", "test_weather_user_b"]:
            u = db.query(User).filter(User.username == name).first()
            if u:
                db.delete(u)
        db.commit()

        # Users A & B
        u_a = User(username="test_weather_user_a", phone="9444444441", password_hash=hash_password("p1"), role=UserRole.FARMER)
        u_b = User(username="test_weather_user_b", phone="9444444442", password_hash=hash_password("p2"), role=UserRole.FARMER)
        db.add_all([u_a, u_b])
        db.commit()

        token_a = create_access_token({"sub": str(u_a.id)})
        token_b = create_access_token({"sub": str(u_b.id)})

        h_a = {"Authorization": f"Bearer {token_a}"}
        h_b = {"Authorization": f"Bearer {token_b}"}

        # Create Profile & Farms for User A
        prof_a = FarmerProfile(user_id=u_a.id, full_name="Weather Tester A")
        db.add(prof_a)
        db.commit()

        # Farm A1 with explicit coordinates
        farm_a1 = Farm(farmer_id=prof_a.id, farm_name="Weather Farm A1", latitude=13.9299, longitude=75.5681)
        # Farm A2 without coordinates (default fallback)
        farm_a2 = Farm(farmer_id=prof_a.id, farm_name="Weather Farm A2", latitude=None, longitude=None)
        db.add_all([farm_a1, farm_a2])
        db.commit()

        # Create Profile for User B
        prof_b = FarmerProfile(user_id=u_b.id, full_name="Weather Tester B")
        db.add(prof_b)
        db.commit()

        yield {
            "h_a": h_a,
            "h_b": h_b,
            "farm_a1_id": str(farm_a1.id),
            "farm_a2_id": str(farm_a2.id),
        }
    finally:
        for name in ["test_weather_user_a", "test_weather_user_b"]:
            u = db.query(User).filter(User.username == name).first()
            if u:
                db.delete(u)
        db.commit()
        db.close()


def test_weather_router_endpoints(setup_weather_env):
    h_a = setup_weather_env["h_a"]
    h_b = setup_weather_env["h_b"]
    farm_a1_id = setup_weather_env["farm_a1_id"]
    farm_a2_id = setup_weather_env["farm_a2_id"]

    # 1. User A fetches weather for Farm A1 (with coordinates)
    res1 = client.get(f"/api/v1/agents/weather/current/{farm_a1_id}", headers=h_a)
    assert res1.status_code == 200, res1.text
    data1 = res1.json()
    assert data1["location_source"] == LocationSource.FARM_COORDINATES.value
    assert data1["region_key"] == "grid_13.93_75.57"
    assert "disease_risk" in data1
    assert "confidence_level" in data1["disease_risk"]
    assert "is_synthetic" in data1["disease_risk"]
    assert data1["source"] in [WeatherSource.API.value, WeatherSource.SYNTHETIC_FALLBACK.value]

    # 2. User A fetches weather for Farm A2 (no coordinates -> default fallback)
    res2 = client.get(f"/api/v1/agents/weather/current/{farm_a2_id}", headers=h_a)
    assert res2.status_code == 200, res2.text
    data2 = res2.json()
    assert data2["location_source"] == LocationSource.DEFAULT_FALLBACK.value
    assert data2["region_key"] == "grid_12.91_74.86"

    # 3. Cross-farmer security rejection (User B trying to access User A's farm weather)
    res_b = client.get(f"/api/v1/agents/weather/current/{farm_a1_id}", headers=h_b)
    assert res_b.status_code == 403, "User B should be forbidden from reading User A's farm weather"


if __name__ == "__main__":
    pytest.main(["-v", __file__])
