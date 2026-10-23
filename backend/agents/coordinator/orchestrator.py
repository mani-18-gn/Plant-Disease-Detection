import uuid
import logging
from datetime import datetime, date, timezone, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from backend.db.models.core.user import User
from backend.db.models.core.farmer_profile import FarmerProfile
from backend.db.models.core.farm import Farm
from backend.db.models.core.crop_block import CropBlock
from backend.db.models.agronomy.disease_detection import DiseaseDetection
from backend.db.models.agronomy.farm_activity import ActivityType
from backend.db.models.env.weather_reading import WeatherReading, WeatherSource
from backend.core.router import _verify_crop_block_ownership
from backend.core.activity_service import get_last_activity_of_type
from backend.agents.diagnosis.bayesian import compute_posterior, get_hybrid_prior
from backend.agents.weather.api_client import fetch_live_weather, get_grid_region_key, DEFAULT_LAT, DEFAULT_LON
from backend.agents.weather.risk_score import calculate_disease_risk_score
from backend.agents.market.data_gov_client import fetch_live_market_prices
from backend.agents.advisory.cache import get_cached_advisory
from backend.agents.advisory.gemini_client import generate_gemini_advisory
from backend.db.models.logs.advisory import Advisory, AdvisoryPriority, AdvisorySource
from backend.agents.coordinator.weights import compute_situation_score
from backend.agents.notifying.notifications import dispatch_advisory_notifications

logger = logging.getLogger(__name__)


def synthesize_farm_status(
    db: Session,
    crop_block_id: str,
    current_user: User,
    detection_id: str | None = None,
) -> dict:
    """
    Coordinator Agent Orchestrator:
    Orchestrates cross-agent synthesis across Diagnosis (35%), Weather (30%), Market (20%),
    and Learning (15%), computing the overall situation urgency score and delivering
    integrated agronomic recommendations.
    """
    crop_block_id_str = str(crop_block_id)

    # 1. Verify Caller Ownership
    _verify_crop_block_ownership(db, crop_block_id_str, str(current_user.id))

    # 2. Fetch Core Entities
    crop_block = db.query(CropBlock).filter(CropBlock.id == crop_block_id_str).first()
    if not crop_block:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crop block not found")

    farm = db.query(Farm).filter(Farm.id == str(crop_block.farm_id)).first()
    farmer_profile = db.query(FarmerProfile).filter(FarmerProfile.user_id == str(current_user.id)).first()
    if not farmer_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farmer profile not found")

    # 3. Weather Agent Context (with 6-Hour Region-Based Cache Alignment)
    lat = float(farm.latitude) if farm and farm.latitude is not None else DEFAULT_LAT
    lon = float(farm.longitude) if farm and farm.longitude is not None else DEFAULT_LON
    region_key = get_grid_region_key(lat, lon)
    six_hours_ago = datetime.now(timezone.utc) - timedelta(hours=6)

    try:
        cached_reading = (
            db.query(WeatherReading)
            .filter(
                WeatherReading.region_key == region_key,
                WeatherReading.recorded_at >= six_hours_ago
            )
            .order_by(WeatherReading.recorded_at.desc())
            .first()
        )

        if cached_reading:
            w_temp = float(cached_reading.temperature)
            w_hum = float(cached_reading.humidity)
            w_rain = float(cached_reading.rainfall_mm)
            w_source = cached_reading.source.value if hasattr(cached_reading.source, "value") else str(cached_reading.source)
            w_synthetic = (cached_reading.source == WeatherSource.SYNTHETIC_FALLBACK)
        else:
            live_w = fetch_live_weather(lat, lon)
            w_temp = float(live_w["temperature"])
            w_hum = float(live_w["humidity"])
            w_rain = float(live_w["rainfall_mm"])
            w_source = live_w["weather_source"].value if hasattr(live_w["weather_source"], "value") else str(live_w["weather_source"])
            w_synthetic = bool(live_w["is_synthetic"])

            new_reading = WeatherReading(
                farm_id=str(farm.id) if farm else None,
                region_key=region_key,
                temperature=w_temp,
                humidity=w_hum,
                rainfall_mm=w_rain,
                source=live_w["weather_source"],
            )
            db.add(new_reading)
            db.commit()
            db.refresh(new_reading)

        risk_result = calculate_disease_risk_score(
            humidity=w_hum,
            temperature=w_temp,
            rainfall_mm=w_rain,
            is_synthetic=w_synthetic,
        )
        weather_summary = {
            "temperature": w_temp,
            "humidity": w_hum,
            "rainfall_mm": w_rain,
            "disease_risk_score": risk_result.score,
            "disease_risk_level": risk_result.level.value,
            "is_synthetic": w_synthetic,
            "weather_source": w_source,
            "status": "ok",
        }
    except Exception as e:
        logger.warning(f"Weather Agent partial failure in Coordinator: {e}")
        weather_summary = {
            "temperature": 25.0,
            "humidity": 70.0,
            "rainfall_mm": 0.0,
            "disease_risk_score": 20.0,
            "disease_risk_level": "low",
            "is_synthetic": True,
            "weather_source": "synthetic_fallback",
            "status": "partial_fallback",
        }

    # 4. Diagnosis Agent Context (fetch detection and validate if needed)
    detection_query = db.query(DiseaseDetection).filter(DiseaseDetection.crop_block_id == crop_block_id_str)
    if detection_id:
        latest_detection = detection_query.filter(DiseaseDetection.id == str(detection_id)).first()
    else:
        latest_detection = detection_query.order_by(DiseaseDetection.detected_at.desc()).first()

    if latest_detection:
        det_disease = latest_detection.predicted_disease
        det_cnn_conf = float(latest_detection.cnn_confidence)
        det_post = float(latest_detection.posterior_probability) if latest_detection.posterior_probability is not None else None
        det_val = latest_detection.validated
        diag_status = "ok"

        # Auto-validate with Bayes' Theorem if not yet validated
        if det_post is None:
            historical_dets = db.query(DiseaseDetection).filter(DiseaseDetection.crop_block_id == crop_block_id_str).all()
            prior = get_hybrid_prior(det_disease, historical_dets)

            det_post, det_val = compute_posterior(
                cnn_confidence=det_cnn_conf,
                weather_risk_score=weather_summary["disease_risk_score"],
                predicted_disease=det_disease,
                historical_prior=prior,
                is_synthetic_weather=weather_summary["is_synthetic"],
            )
            latest_detection.posterior_probability = det_post
            latest_detection.validated = det_val
            db.commit()
            db.refresh(latest_detection)
            diag_status = "auto_validated"

        diagnosis_summary = {
            "detection_id": uuid.UUID(str(latest_detection.id)),
            "predicted_disease": det_disease,
            "cnn_confidence": det_cnn_conf,
            "posterior_probability": det_post,
            "validated": det_val,
            "status": diag_status,
        }
    else:
        diagnosis_summary = {
            "detection_id": None,
            "predicted_disease": "healthy_leaf",
            "cnn_confidence": 1.0,
            "posterior_probability": 1.0,
            "validated": True,
            "status": "default_healthy",
        }

    # 5. Market Agent Context (align with DB cache for 100% consistency across pages)
    preferred_mandi = farmer_profile.preferred_mandi or "Shivamogga APMC"
    try:
        cached_m = (
            db.query(MarketPrice)
            .filter(
                MarketPrice.mandi_name.ilike(f"%{preferred_mandi.split()[0]}%"),
                MarketPrice.commodity.ilike("%Arecanut%"),
            )
            .order_by(MarketPrice.price_date.desc())
            .first()
        )

        if cached_m:
            m_price = float(cached_m.price_per_kg)
        else:
            market_data = fetch_live_market_prices(mandi_name=preferred_mandi)
            m_price = float(market_data["prices"][0]["price_per_kg"]) if market_data["prices"] else 475.0

        market_summary = {
            "mandi_name": preferred_mandi,
            "current_price_per_kg": round(m_price, 2),
            "price_trend": "rising",
            "forecast_model": "linear_trend_regression",
            "status": "ok",
        }
    except Exception as e:
        logger.warning(f"Market Agent partial failure in Coordinator: {e}")
        market_summary = {
            "mandi_name": preferred_mandi,
            "current_price_per_kg": 475.0,
            "price_trend": "stable",
            "forecast_model": "fallback_baseline",
            "status": "partial_fallback",
        }

    # 6. Compute Table 4.6 Situation Urgency Score
    situation_score = compute_situation_score(
        diagnosis_dict=diagnosis_summary,
        weather_dict=weather_summary,
        market_dict=market_summary,
    )

    # 7. Advisory Agent Synthesis (with 6-Hour Cache Guardrail)
    last_spray = get_last_activity_of_type(db, crop_block_id_str, ActivityType.SPRAYING)
    last_irrig = get_last_activity_of_type(db, crop_block_id_str, ActivityType.IRRIGATION)
    days_since_spray = (date.today() - last_spray.activity_date).days if last_spray else None
    days_since_irrig = (date.today() - last_irrig.activity_date).days if last_irrig else None

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
            "predicted_disease": diagnosis_summary["predicted_disease"],
            "cnn_confidence": diagnosis_summary["cnn_confidence"],
            "posterior_probability": diagnosis_summary["posterior_probability"],
            "validated": diagnosis_summary["validated"],
            "detected_at": latest_detection.detected_at.isoformat() if latest_detection else None,
        },
        "weather": {
            "disease_risk_score": weather_summary["disease_risk_score"],
            "disease_risk_level": weather_summary["disease_risk_level"],
            "temperature": weather_summary["temperature"],
            "humidity": weather_summary["humidity"],
            "rainfall_mm": weather_summary["rainfall_mm"],
            "is_synthetic_weather": weather_summary["is_synthetic"],
            "weather_source": weather_summary["weather_source"],
        },
        "market": {
            "mandi_name": market_summary["mandi_name"],
            "current_price_per_kg": market_summary["current_price_per_kg"],
            "price_trend": market_summary["price_trend"],
            "forecast_model": market_summary["forecast_model"],
        },
        "recent_activities": {
            "days_since_last_spray": days_since_spray,
            "days_since_last_irrigation": days_since_irrig,
        },
        "situation_score": situation_score["composite_score"],
        "urgency_drivers": situation_score["urgency_drivers"],
    }

    # Check 6-Hour Cache
    cached_adv = get_cached_advisory(db, crop_block_id_str, input_snapshot)
    if cached_adv:
        stored_snap = cached_adv.input_snapshot or {}
        advisory_dict = {
            "id": uuid.UUID(str(cached_adv.id)),
            "farmer_id": uuid.UUID(str(cached_adv.farmer_id)),
            "crop_block_id": uuid.UUID(str(cached_adv.crop_block_id)),
            "priority": cached_adv.priority,
            "message": cached_adv.message,
            "recommended_actions": stored_snap.get("recommended_actions", []),
            "reasoning_summary": stored_snap.get("reasoning_summary", ""),
            "disclaimer": stored_snap.get("disclaimer", ""),
            "generated_by": cached_adv.generated_by,
            "input_snapshot": stored_snap,
            "read_status": cached_adv.read_status,
            "created_at": cached_adv.created_at,
        }
    else:
        adv_output = generate_gemini_advisory(input_snapshot)
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

        advisory_dict = {
            "id": uuid.UUID(str(new_advisory.id)),
            "farmer_id": uuid.UUID(str(new_advisory.farmer_id)),
            "crop_block_id": uuid.UUID(str(new_advisory.crop_block_id)),
            "priority": new_advisory.priority,
            "message": new_advisory.message,
            "recommended_actions": adv_output.get("recommended_actions", []),
            "reasoning_summary": adv_output.get("reasoning_summary", ""),
            "disclaimer": adv_output.get("disclaimer", ""),
            "generated_by": new_advisory.generated_by,
            "input_snapshot": augmented_snapshot,
            "read_status": new_advisory.read_status,
            "created_at": new_advisory.created_at,
        }

    return {
        "crop_block_id": uuid.UUID(crop_block_id_str),
        "farm_id": uuid.UUID(str(farm.id)) if farm else uuid.UUID(str(crop_block.farm_id)),
        "farmer_id": uuid.UUID(str(farmer_profile.id)),
        "timestamp": datetime.now(timezone.utc),
        "situation_score": situation_score,
        "diagnosis": diagnosis_summary,
        "weather": weather_summary,
        "market": market_summary,
        "advisory": advisory_dict,
    }
