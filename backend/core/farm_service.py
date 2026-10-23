from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from backend.db.models.core.farm import Farm
from backend.schemas.farm import FarmCreate, FarmUpdate


from backend.db.models.env.weather_reading import WeatherReading
from backend.agents.weather.api_client import (
    get_grid_region_key,
    backfill_historical_weather,
    DEFAULT_LAT,
    DEFAULT_LON,
)


def create_farm(db: Session, farmer_id: str, data: FarmCreate) -> Farm:
    farm = Farm(farmer_id=str(farmer_id), **data.model_dump())
    db.add(farm)
    db.commit()
    db.refresh(farm)

    # Trigger 14-day historical weather backfill at farm creation if region_key has insufficient data
    try:
        lat = float(farm.latitude) if farm.latitude is not None else DEFAULT_LAT
        lon = float(farm.longitude) if farm.longitude is not None else DEFAULT_LON
        region_key = get_grid_region_key(lat, lon)

        existing_count = db.query(WeatherReading).filter(WeatherReading.region_key == region_key).count()
        if existing_count < 14:
            backfill_historical_weather(
                db=db,
                farm_id=str(farm.id),
                region_key=region_key,
                lat=farm.latitude,
                lon=farm.longitude,
                days=14,
            )
    except Exception as e:
        # Non-blocking: failure to backfill should never prevent farm creation
        pass

    return farm


def get_farm(db: Session, farm_id: str) -> Farm:
    farm = db.query(Farm).filter(Farm.id == str(farm_id)).first()
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farm not found",
        )
    return farm


def list_farms_for_farmer(db: Session, farmer_id: str) -> list[Farm]:
    return (
        db.query(Farm)
        .filter(Farm.farmer_id == str(farmer_id))
        .order_by(Farm.created_at.desc())
        .all()
    )


def update_farm(db: Session, farm_id: str, data: FarmUpdate) -> Farm:
    farm = get_farm(db, farm_id)
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(farm, field, value)
    db.commit()
    db.refresh(farm)
    return farm


def delete_farm(db: Session, farm_id: str) -> bool:
    """Hard delete farm -- cascades to crop_blocks, iot_devices, activities via DB FK ON DELETE rules."""
    farm = get_farm(db, farm_id)
    db.delete(farm)
    db.commit()
    return True
