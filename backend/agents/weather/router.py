import uuid
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.db.models.core.user import User
from backend.db.models.core.farm import Farm
from backend.db.models.env.weather_reading import WeatherReading, WeatherSource
from backend.auth.jwt_handler import get_current_user
from backend.core.router import _verify_farm_ownership
from backend.schemas.weather import (
    WeatherAgentResponse,
    LocationSource,
)
from backend.agents.weather.api_client import (
    fetch_live_weather,
    get_grid_region_key,
    DEFAULT_LAT,
    DEFAULT_LON,
)
from backend.agents.weather.risk_score import calculate_disease_risk_score
from backend.agents.weather.arima_model import generate_weather_forecast

router = APIRouter(prefix="/agents/weather", tags=["Weather Agent"])


@router.get("/current/{farm_id}", response_model=WeatherAgentResponse)
def get_current_weather(
    farm_id: uuid.UUID,
    force_refresh: bool = Query(False, description="Force fresh OpenWeatherMap API call bypassing 6-hour cache"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Weather Agent Endpoint:
    1. Verifies authenticated user owns specified farm_id (raises 403 Forbidden if not).
    2. Computes grid-cell region_key (1.1 km resolution) and location_source.
    3. Checks region-level 6-hour DB cache: if recent reading exists for region_key, uses it to avoid redundant API costs.
    4. If cache missed or force_refresh=true, calls OpenWeatherMap API and persists new reading to env.weather_readings.
    5. Computes 0-100 Disease Risk Score and Risk Level (low/medium/high/urgent).
    6. Runs time-series forecast (ARIMA if historical readings >= 14, otherwise moving-average fallback).
    """
    str_farm_id = str(farm_id)

    # 1. Farm ownership verification
    _verify_farm_ownership(db, str_farm_id, str(current_user.id))

    farm = db.query(Farm).filter(Farm.id == str_farm_id).first()
    if not farm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farm not found")

    # 2. Determine coordinates, region_key, and location_source
    if farm.latitude is not None and farm.longitude is not None:
        lat, lon = float(farm.latitude), float(farm.longitude)
        location_source = LocationSource.FARM_COORDINATES
    else:
        lat, lon = DEFAULT_LAT, DEFAULT_LON
        location_source = LocationSource.DEFAULT_FALLBACK

    region_key = get_grid_region_key(lat, lon)

    # 3. Region-Level 6-Hour Cache Check
    six_hours_ago = datetime.now(timezone.utc) - timedelta(hours=6)
    cached_reading = None

    if not force_refresh:
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
        reading_id = uuid.UUID(cached_reading.id)
        temp = float(cached_reading.temperature) if cached_reading.temperature is not None else 28.0
        hum = float(cached_reading.humidity) if cached_reading.humidity is not None else 75.0
        rain = float(cached_reading.rainfall_mm) if cached_reading.rainfall_mm is not None else 0.0
        source = cached_reading.source
        recorded_at = cached_reading.recorded_at
        is_synthetic = (source == WeatherSource.SYNTHETIC_FALLBACK)
        # Fetch fresh hourly & daily forecast
        live_forecast_data = fetch_live_weather(
            lat if location_source == LocationSource.FARM_COORDINATES else None,
            lon if location_source == LocationSource.FARM_COORDINATES else None,
        )
        hourly_forecast = live_forecast_data.get("hourly_forecast", [])
        weekly_forecast = live_forecast_data.get("weekly_forecast", [])
    else:
        # Cache miss or forced refresh: fetch live or synthetic weather
        live_data = fetch_live_weather(
            lat if location_source == LocationSource.FARM_COORDINATES else None,
            lon if location_source == LocationSource.FARM_COORDINATES else None,
        )

        new_reading = WeatherReading(
            farm_id=str_farm_id,
            region_key=region_key,
            temperature=live_data["temperature"],
            humidity=live_data["humidity"],
            rainfall_mm=live_data["rainfall_mm"],
            source=live_data["weather_source"],
        )
        db.add(new_reading)
        db.commit()
        db.refresh(new_reading)

        reading_id = uuid.UUID(new_reading.id)
        temp = float(new_reading.temperature) if new_reading.temperature is not None else 28.0
        hum = float(new_reading.humidity) if new_reading.humidity is not None else 75.0
        rain = float(new_reading.rainfall_mm) if new_reading.rainfall_mm is not None else 0.0
        source = new_reading.source
        recorded_at = new_reading.recorded_at
        is_synthetic = live_data["is_synthetic"]
        hourly_forecast = live_data.get("hourly_forecast", [])
        weekly_forecast = live_data.get("weekly_forecast", [])

    # 4. Compute Disease Risk Score & Level (with synthetic flag)
    disease_risk = calculate_disease_risk_score(
        humidity=hum,
        temperature=temp,
        rainfall_mm=rain,
        is_synthetic=is_synthetic,
    )

    # 5. Fetch historical readings for forecast computation
    historical_readings = (
        db.query(WeatherReading)
        .filter(WeatherReading.region_key == region_key)
        .order_by(WeatherReading.recorded_at.asc())
        .all()
    )

    forecast_items = generate_weather_forecast(
        historical_readings=historical_readings,
        current_temp=temp,
        current_humidity=hum,
        current_rainfall=rain,
        periods=3
    )

    return WeatherAgentResponse(
        id=reading_id,
        farm_id=farm_id,
        region_key=region_key,
        location_source=location_source,
        temperature=temp,
        humidity=hum,
        rainfall_mm=rain,
        source=source,
        recorded_at=recorded_at,
        disease_risk=disease_risk,
        forecast=forecast_items,
        hourly_forecast=hourly_forecast,
        weekly_forecast=weekly_forecast,
    )
