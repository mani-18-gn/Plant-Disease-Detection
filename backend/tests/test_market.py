import io
import sys
import os
from datetime import date, timedelta
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.main import app
from backend.db.session import SessionLocal
from backend.db.models.market.market_price import MarketPrice
from backend.agents.market.fallback_model import generate_fallback_price_forecast
from backend.agents.market.lstm_model import generate_lstm_forecast

client = TestClient(app)


def test_fallback_model_triggering():
    """Test that < 67 historical price records generates linear trend regression fallback."""
    few_prices = [450.0, 452.5, 455.0]  # Only 3 records < 67
    forecast = generate_fallback_price_forecast(
        historical_prices=few_prices,
        current_price=455.0,
        start_date=date(2026, 8, 1),
        periods=7,
    )
    assert len(forecast) == 7, "Expected 7-day price forecast"
    for item in forecast:
        assert item["forecast_model"] == "linear_trend_regression"
        assert item["lower_bound"] <= item["predicted_price_per_kg"] <= item["upper_bound"]
        assert item["predicted_price_per_kg"] > 0.0


def test_forecast_format_consistency_lstm_vs_fallback():
    """Verify that both LSTM and fallback paths produce identical dictionary structures."""
    sample_window = [450.0 + (i * 0.3) for i in range(60)]
    fallback_res = generate_fallback_price_forecast(sample_window, periods=7)
    lstm_res = generate_lstm_forecast(sample_window, periods=7)

    assert len(fallback_res) == 7
    assert len(lstm_res) == 7

    required_keys = {"forecast_date", "predicted_price_per_kg", "lower_bound", "upper_bound", "forecast_model"}
    for f_item, l_item in zip(fallback_res, lstm_res):
        assert set(f_item.keys()) == required_keys
        assert set(l_item.keys()) == required_keys
        assert f_item["forecast_model"] == "linear_trend_regression"
        assert l_item["forecast_model"] == "lstm"


def test_market_router_endpoint():
    """Test GET /api/v1/agents/market/prices endpoint functionality."""
    # 1. Default query
    res = client.get("/api/v1/agents/market/prices")
    assert res.status_code == 200, res.text
    data = res.json()
    assert "mandi_name" in data
    assert "current_price_per_kg" in data
    assert data["current_price_per_kg"] > 0.0
    assert len(data["forecast"]) == 7
    assert data["forecast"][0]["forecast_model"] in ["linear_trend_regression", "lstm"]

    # 2. Explicit mandi query
    res_sagar = client.get("/api/v1/agents/market/prices?mandi=Sagar%20APMC")
    assert res_sagar.status_code == 200, res_sagar.text
    data_sagar = res_sagar.json()
    assert "Sagar" in data_sagar["mandi_name"]
    assert len(data_sagar["forecast"]) == 7


if __name__ == "__main__":
    pytest.main(["-v", __file__])
