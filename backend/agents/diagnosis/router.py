import uuid
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.db.models.core.user import User
from backend.db.models.core.crop_block import CropBlock
from backend.db.models.core.farm import Farm
from backend.db.models.agronomy.disease_detection import DiseaseDetection
from backend.db.models.env.weather_reading import WeatherReading, WeatherSource
from backend.auth.jwt_handler import get_current_user
from backend.core.router import _verify_crop_block_ownership
from backend.schemas.disease import DiseaseDetectionResponse
from backend.agents.weather.api_client import (
    fetch_live_weather,
    get_grid_region_key,
    DEFAULT_LAT,
    DEFAULT_LON,
)
from backend.agents.weather.risk_score import calculate_disease_risk_score
from backend.agents.diagnosis.bayesian import get_hybrid_prior, compute_posterior

router = APIRouter(prefix="/agents/diagnosis", tags=["Diagnosis Agent"])


@router.post("/validate/{detection_id}", response_model=DiseaseDetectionResponse)
def validate_diagnosis(
    detection_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Diagnosis Agent Endpoint:
    1. Fetches disease_detections record by detection_id.
    2. Verifies authenticated user owns the associated crop_block (403 Forbidden if not).
    3. Reuses Weather Agent logic to obtain environmental disease risk score for the crop block's farm.
    4. Computes historical empirical prior P(Disease) across regional detection history.
    5. Runs Bayesian update P(Disease | Image, Weather, History) to compute posterior_probability.
    6. Sets validated=true if posterior_probability > 0.75 and persists updates to agronomy schema.
    """
    str_detection_id = str(detection_id)

    # 1. Fetch detection record
    detection = db.query(DiseaseDetection).filter(DiseaseDetection.id == str_detection_id).first()
    if not detection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Disease detection record not found")

    # 2. Ownership verification
    _verify_crop_block_ownership(db, str(detection.crop_block_id), str(current_user.id))

    # 3. Retrieve farm coordinates and weather risk
    crop_block = db.query(CropBlock).filter(CropBlock.id == str(detection.crop_block_id)).first()
    farm = db.query(Farm).filter(Farm.id == str(crop_block.farm_id)).first() if crop_block else None

    if farm and farm.latitude is not None and farm.longitude is not None:
        lat, lon = float(farm.latitude), float(farm.longitude)
    else:
        lat, lon = DEFAULT_LAT, DEFAULT_LON

    region_key = get_grid_region_key(lat, lon)

    # Check 6-hour cache in weather_readings
    six_hours_ago = datetime.now(timezone.utc) - timedelta(hours=6)
    cached_reading = (
        db.query(WeatherReading)
        .filter(WeatherReading.region_key == region_key, WeatherReading.recorded_at >= six_hours_ago)
        .order_by(WeatherReading.recorded_at.desc())
        .first()
    )

    if cached_reading:
        temp = float(cached_reading.temperature)
        hum = float(cached_reading.humidity)
        rain = float(cached_reading.rainfall_mm)
        is_synthetic = (cached_reading.source == WeatherSource.SYNTHETIC_FALLBACK)
    else:
        live_data = fetch_live_weather(lat, lon)
        temp = live_data["temperature"]
        hum = live_data["humidity"]
        rain = live_data["rainfall_mm"]
        is_synthetic = live_data["is_synthetic"]

    weather_risk = calculate_disease_risk_score(humidity=hum, temperature=temp, rainfall_mm=rain, is_synthetic=is_synthetic)

    # 4. Hybrid Historical Prior calculation
    historical_detections = (
        db.query(DiseaseDetection)
        .join(CropBlock, DiseaseDetection.crop_block_id == CropBlock.id)
        .filter(CropBlock.farm_id == str(farm.id) if farm else True)
        .all()
    )

    prior = get_hybrid_prior(
        predicted_disease=detection.predicted_disease,
        historical_detections=historical_detections,
    )

    # 5. Bayesian Inference
    posterior, is_validated = compute_posterior(
        cnn_confidence=float(detection.cnn_confidence),
        weather_risk_score=weather_risk.score,
        predicted_disease=detection.predicted_disease,
        historical_prior=prior,
        is_synthetic_weather=is_synthetic,
    )

    # 6. Update and persist record
    detection.posterior_probability = posterior
    detection.validated = is_validated
    db.commit()
    db.refresh(detection)

    return detection
