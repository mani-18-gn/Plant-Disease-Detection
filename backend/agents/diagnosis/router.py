import asyncio
import logging
from typing import Any, Dict, Optional
import uuid
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status, File, Form, UploadFile
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
from backend.schemas.diagnosis import DiagnoseAPIResponse
from backend.agents.weather.api_client import (
    fetch_live_weather,
    get_grid_region_key,
    DEFAULT_LAT,
    DEFAULT_LON,
)
from backend.agents.weather.risk_score import calculate_disease_risk_score
from backend.agents.diagnosis.bayesian import get_hybrid_prior, compute_posterior
from backend.agents.diagnosis.google_ai import (
    diagnose_plant_with_google_ai,
    get_google_ai_status,
    is_google_ai_configured,
)
from backend.agents.vision.inference import run_vision_inference

logger = logging.getLogger(__name__)

ALLOWED_MIME_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp"}
MAX_UPLOAD_SIZE = 15 * 1024 * 1024

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


@router.get("/google-ai/status")
def google_ai_status():
    """Check availability and configuration of the Google Gen AI Plant Pathology Agent."""
    return get_google_ai_status()


@router.post("/diagnose", response_model=DiagnoseAPIResponse)
async def diagnose_plant(
    file: UploadFile = File(..., description="Photograph of a plant, crop leaf, or specimen"),
    crop_name: Optional[str] = Form(None, description="Optional common or crop name"),
    symptoms: Optional[str] = Form(None, description="Optional user-observed field symptoms"),
    location: Optional[str] = Form(None, description="Optional geographic region or climate zone"),
    crop_block_id: Optional[uuid.UUID] = Form(None, description="Optional crop block ID to link"),
):
    """
    Google-Powered Plant Disease Identification & Grounded Diagnosis Endpoint:
    1. Validates uploaded file type (JPEG, PNG, WebP) and 15MB size limit.
    2. Runs local edge neural network (MobileNetV2 / Arecanut CNN) for independent baseline comparison.
    3. Runs Google Gen AI multimodal pathology analysis (plant check, leaf symptoms, differential diagnosis, IPM recommendations).
    4. Retrieves grounded agricultural sources (Google Search Grounding / ICAR & University monographs).
    5. Returns structured diagnosis without leaking API keys or internal stack traces.
    """
    if file.content_type and file.content_type.lower() not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{file.content_type}'. Please upload a JPEG, PNG, or WebP photograph.",
        )

    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty.")

    if len(image_bytes) > MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds maximum allowed limit (15 MB).",
        )

    # 1. Run local edge neural network for baseline comparison
    local_comparison = None
    try:
        local_result = await asyncio.to_thread(
            run_vision_inference,
            image_bytes,
            block_crop=crop_name
        )
        local_comparison = {
            "predicted_disease": local_result.get("predicted_disease"),
            "crop": local_result.get("crop"),
            "condition": local_result.get("condition"),
            "confidence": float(local_result.get("cnn_confidence", 0.0)),
            "is_healthy": local_result.get("is_healthy", False),
            "backend": local_result.get("backend", "local_edge_cnn"),
        }
    except Exception as e:
        logger.warning(f"Local model comparison failed during diagnose: {e}")
        local_comparison = {"status": "unavailable", "note": str(e)}

    # 2. Run Google AI Multimodal Diagnosis
    google_ai_result = await diagnose_plant_with_google_ai(
        image_bytes=image_bytes,
        crop_hint=crop_name,
        user_symptoms=symptoms,
        location=location,
    )

    # Determine alignment if both are available
    if local_comparison and google_ai_result.get("diagnosis"):
        local_cond = (local_comparison.get("condition") or "").lower()
        gai_disease = (google_ai_result["diagnosis"].get("disease_assessment", {}).get("most_likely_disease") or "").lower()
        alignment = "aligned" if (local_cond and local_cond in gai_disease or gai_disease in local_cond) else "divergent_or_differential"
        local_comparison["alignment"] = alignment

    return {
        "status": google_ai_result.get("status", "error"),
        "is_plant": google_ai_result.get("is_plant"),
        "image_quality": google_ai_result.get("image_quality", "good"),
        "rejection_reason": google_ai_result.get("rejection_reason"),
        "error": google_ai_result.get("error"),
        "diagnosis": google_ai_result.get("diagnosis"),
        "sources": google_ai_result.get("sources", []),
        "model_used": google_ai_result.get("model_used"),
        "local_model_comparison": local_comparison,
    }

