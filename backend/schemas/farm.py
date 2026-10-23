import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from backend.db.models.core.farm import IrrigationType


class FarmCreate(BaseModel):
    farm_name: str
    latitude: float | None = None
    longitude: float | None = None
    total_area_acres: float | None = None
    soil_type: str | None = None
    irrigation_type: IrrigationType | None = IrrigationType.DRIP


class FarmUpdate(BaseModel):
    farm_name: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    total_area_acres: float | None = None
    soil_type: str | None = None
    irrigation_type: IrrigationType | None = None


class FarmResponse(BaseModel):
    id: uuid.UUID
    farmer_id: uuid.UUID
    farm_name: str
    latitude: float | None = None
    longitude: float | None = None
    total_area_acres: float | None = None
    soil_type: str | None = None
    irrigation_type: IrrigationType | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
