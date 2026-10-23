import uuid
from datetime import datetime, date, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.db.models.core.user import User
from backend.db.models.core.farmer_profile import FarmerProfile
from backend.db.models.core.farm import Farm
from backend.db.models.core.crop_block import CropBlock
from backend.db.models.agronomy.disease_detection import DiseaseDetection
from backend.db.models.agronomy.farm_activity import ActivityType
from backend.db.models.logs.advisory import Advisory, AdvisoryPriority, AdvisorySource
from backend.auth.jwt_handler import get_current_user
from backend.core.router import _verify_crop_block_ownership
from backend.core.activity_service import get_last_activity_of_type
from backend.schemas.advisory import (
    AdvisoryGenerateRequest,
    AdvisoryGenerateResponse,
    AdvisoryResponse,
)
from backend.agents.weather.api_client import fetch_live_weather, DEFAULT_LAT, DEFAULT_LON
from backend.agents.weather.risk_score import calculate_disease_risk_score
from backend.agents.market.data_gov_client import fetch_live_market_prices
from backend.agents.advisory.cache import get_cached_advisory
from backend.agents.advisory.gemini_client import generate_gemini_advisory

from backend.agents.notifying.notifications import dispatch_advisory_notifications

router = APIRouter(prefix="/agents/advisory", tags=["Advisory Agent"])


@router.post("/generate", response_model=AdvisoryGenerateResponse)
def generate_advisory(
    payload: AdvisoryGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Advisory Agent: Synthesizes Vision/Diagnosis, Weather, Market, and Activity context
    into farmer-facing advisory guidance using Gemini (with rule-based fallback).
    """
    crop_block_id_str = str(payload.crop_block_id)

    # 1. Verify caller owns the crop_block
    _verify_crop_block_ownership(db, crop_block_id_str, str(current_user.id))

    # 2. Fetch Farm, Block, and Farmer Profile
    crop_block = db.query(CropBlock).filter(CropBlock.id == crop_block_id_str).first()
    farm = db.query(Farm).filter(Farm.id == str(crop_block.farm_id)).first() if crop_block else None
    farmer_profile = db.query(FarmerProfile).filter(FarmerProfile.user_id == str(current_user.id)).first()

    if not crop_block or not farmer_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crop block or farmer profile not found")

    # 3. Retrieve Latest Validated Diagnosis
    latest_detection = (
        db.query(DiseaseDetection)
        .filter(DiseaseDetection.crop_block_id == crop_block_id_str)
        .order_by(DiseaseDetection.detected_at.desc())
        .first()
    )

    # 4. Retrieve Live/Cached Weather Context
    lat = float(farm.latitude) if farm and farm.latitude is not None else DEFAULT_LAT
    lon = float(farm.longitude) if farm and farm.longitude is not None else DEFAULT_LON
    weather_data = fetch_live_weather(lat, lon)
    risk_score = calculate_disease_risk_score(
        humidity=weather_data["humidity"],
        temperature=weather_data["temperature"],
        rainfall_mm=weather_data["rainfall_mm"],
        is_synthetic=weather_data["is_synthetic"],
    )

    # 5. Retrieve Live Market Context
    mandi_name = farmer_profile.preferred_mandi or "Shivamogga APMC"
    market_data = fetch_live_market_prices(mandi_name=mandi_name)
    current_m_price = market_data["prices"][0]["price_per_kg"] if market_data["prices"] else 475.0

    # 6. Retrieve Recent Activities
    last_spray = get_last_activity_of_type(db, crop_block_id_str, ActivityType.SPRAYING)
    last_irrig = get_last_activity_of_type(db, crop_block_id_str, ActivityType.IRRIGATION)

    days_since_spray = (date.today() - last_spray.activity_date).days if last_spray else None
    days_since_irrig = (date.today() - last_irrig.activity_date).days if last_irrig else None

    # 7. Construct Input Snapshot
    input_snapshot = {
        "farmer_id": str(farmer_profile.id),
        "crop_block": {
            "crop_block_id": str(crop_block.id),
            "block_name": crop_block.block_name,
            "palm_variety": crop_block.variety,
            "palm_age_years": crop_block.age_years,
            "soil_type": farm.soil_type if farm else None,
            "irrigation_type": farm.irrigation_type if farm else None,
        },
        "diagnosis": {
            "predicted_disease": latest_detection.predicted_disease if latest_detection else "healthy_leaf",
            "cnn_confidence": float(latest_detection.cnn_confidence) if latest_detection else 0.90,
            "posterior_probability": float(latest_detection.posterior_probability) if latest_detection and latest_detection.posterior_probability else 0.85,
            "validated": latest_detection.validated if latest_detection else True,
            "detected_at": latest_detection.detected_at.isoformat() if latest_detection else None,
        },
        "weather": {
            "disease_risk_score": risk_score.score,
            "disease_risk_level": risk_score.level.value,
            "temperature": weather_data["temperature"],
            "humidity": weather_data["humidity"],
            "rainfall_mm": weather_data["rainfall_mm"],
            "is_synthetic_weather": weather_data["is_synthetic"],
            "weather_source": weather_data["weather_source"].value,
        },
        "market": {
            "mandi_name": mandi_name,
            "current_price_per_kg": current_m_price,
            "price_trend": "rising",
            "source": market_data["source"],
        },
        "recent_activities": {
            "days_since_last_spray": days_since_spray,
            "last_spray_date": last_spray.activity_date.isoformat() if last_spray else None,
            "days_since_last_irrigation": days_since_irrig,
        },
    }

    # 8. Check Cache
    cached_adv = get_cached_advisory(db, crop_block_id_str, input_snapshot)
    if cached_adv:
        stored_snapshot = cached_adv.input_snapshot or {}
        return AdvisoryGenerateResponse(
            id=uuid.UUID(str(cached_adv.id)),
            farmer_id=uuid.UUID(str(cached_adv.farmer_id)),
            crop_block_id=uuid.UUID(str(cached_adv.crop_block_id)),
            priority=cached_adv.priority,
            message=cached_adv.message,
            recommended_actions=stored_snapshot.get("recommended_actions", []),
            reasoning_summary=stored_snapshot.get("reasoning_summary", ""),
            disclaimer=stored_snapshot.get("disclaimer", "Chemical recommendations follow ICAR-CPCRI guidelines. Consult local extension officers before application."),
            generated_by=cached_adv.generated_by,
            input_snapshot=stored_snapshot,
            read_status=cached_adv.read_status,
            created_at=cached_adv.created_at,
        )

    # 9. Generate Advisory via Gemini or Rule-Based Fallback
    adv_output = generate_gemini_advisory(input_snapshot)

    # Store recommended actions, reasoning, and disclaimer inside input_snapshot for persistence
    augmented_snapshot = dict(input_snapshot)
    augmented_snapshot["recommended_actions"] = adv_output.get("recommended_actions", [])
    augmented_snapshot["reasoning_summary"] = adv_output.get("reasoning_summary", "")
    augmented_snapshot["disclaimer"] = adv_output.get("disclaimer", "")

    new_advisory = Advisory(
        farmer_id=str(farmer_profile.id),
        crop_block_id=crop_block_id_str,
        priority=AdvisoryPriority(adv_output["priority"]),
        message=adv_output["message"],
        generated_by=AdvisorySource(adv_output["generated_by"]),
        input_snapshot=augmented_snapshot,
    )
    db.add(new_advisory)
    db.commit()
    db.refresh(new_advisory)

    # Automatically dispatch notifications according to Table 4.5 Priority Matrix
    dispatch_advisory_notifications(db, new_advisory)

    return AdvisoryGenerateResponse(
        id=uuid.UUID(str(new_advisory.id)),
        farmer_id=uuid.UUID(str(new_advisory.farmer_id)),
        crop_block_id=uuid.UUID(str(new_advisory.crop_block_id)),
        priority=new_advisory.priority,
        message=new_advisory.message,
        recommended_actions=adv_output.get("recommended_actions", []),
        reasoning_summary=adv_output.get("reasoning_summary", ""),
        disclaimer=adv_output.get("disclaimer", ""),
        generated_by=new_advisory.generated_by,
        input_snapshot=augmented_snapshot,
        read_status=new_advisory.read_status,
        created_at=new_advisory.created_at,
    )


@router.get("/farmer/{farmer_id}", response_model=list[AdvisoryResponse])
def list_farmer_advisories(
    farmer_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lists historical advisories for a farmer profile."""
    profile = db.query(FarmerProfile).filter(FarmerProfile.id == str(farmer_id)).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farmer profile not found")

    if str(profile.user_id) != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to farmer advisories")

    advisories = (
        db.query(Advisory)
        .filter(Advisory.farmer_id == str(farmer_id))
        .order_by(Advisory.created_at.desc())
        .all()
    )

    return advisories
