import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from backend.schemas.advisory import AdvisoryGenerateResponse


class SynthesizeRequest(BaseModel):
    crop_block_id: uuid.UUID
    detection_id: uuid.UUID | None = None


class ComponentScoreDetail(BaseModel):
    weight: float
    raw_score: float  # 0.0 to 100.0
    weighted_score: float
    status: str  # "ok" | "partial_fallback" | "placeholder"
    summary: str


class SituationScoreBreakdown(BaseModel):
    composite_score: float  # 0.0 to 100.0
    urgency_level: str  # "urgent" | "high" | "moderate" | "low"
    urgency_drivers: list[str]  # e.g. ["diagnosis", "weather"] | ["market"] | []
    learning_component_status: str  # "placeholder_neutral_50_pending_learning_agent"
    components: dict[str, ComponentScoreDetail]


class DiagnosisSummary(BaseModel):
    detection_id: uuid.UUID | None = None
    predicted_disease: str
    cnn_confidence: float
    posterior_probability: float | None = None
    validated: bool
    status: str  # "ok" | "auto_validated" | "default_healthy"


class WeatherSummary(BaseModel):
    temperature: float
    humidity: float
    rainfall_mm: float
    disease_risk_score: float
    disease_risk_level: str
    is_synthetic: bool
    weather_source: str
    status: str  # "ok" | "partial_fallback"


class MarketSummary(BaseModel):
    mandi_name: str
    current_price_per_kg: float
    price_trend: str
    forecast_model: str
    status: str  # "ok" | "partial_fallback"


class CoordinatorSynthesizeResponse(BaseModel):
    crop_block_id: uuid.UUID
    farm_id: uuid.UUID
    farmer_id: uuid.UUID
    timestamp: datetime
    situation_score: SituationScoreBreakdown
    diagnosis: DiagnosisSummary
    weather: WeatherSummary
    market: MarketSummary
    advisory: AdvisoryGenerateResponse

    model_config = ConfigDict(from_attributes=True)
