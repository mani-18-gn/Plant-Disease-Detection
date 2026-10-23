import uuid
from datetime import date
from pydantic import BaseModel, ConfigDict


class MarketForecastItem(BaseModel):
    forecast_date: date
    predicted_price_per_kg: float
    lower_bound: float
    upper_bound: float
    forecast_model: str  # "lstm" or "linear_trend_regression"


class MarketPriceResponse(BaseModel):
    id: uuid.UUID
    mandi_name: str
    commodity: str
    price_per_kg: float
    price_date: date
    source: str

    model_config = ConfigDict(from_attributes=True)


class VarietyPriceItem(BaseModel):
    variety: str
    price_per_kg: float
    price_date: date
    source: str
    description: str = ""


class MarketAgentResponse(BaseModel):
    mandi_name: str
    commodity: str
    current_price_per_kg: float
    price_date: date
    source: str
    is_synthetic: bool
    variety_prices: list[VarietyPriceItem] = []
    forecast: list[MarketForecastItem] = []
    historical_prices: list[MarketPriceResponse] = []

    model_config = ConfigDict(from_attributes=True)
