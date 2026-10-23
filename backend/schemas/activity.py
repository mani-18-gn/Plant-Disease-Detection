import uuid
from datetime import date, datetime
from pydantic import BaseModel, ConfigDict
from backend.db.models.agronomy.farm_activity import ActivityType, LoggedVia


class ActivityCreate(BaseModel):
    crop_block_id: uuid.UUID
    activity_type: ActivityType
    activity_date: date
    product_used: str | None = None
    quantity: float | None = None
    quantity_unit: str | None = None
    cost: float | None = None
    performed_by: str | None = None
    details: dict | None = None
    logged_via: LoggedVia = LoggedVia.APP


class ActivityUpdate(BaseModel):
    activity_type: ActivityType | None = None
    activity_date: date | None = None
    product_used: str | None = None
    quantity: float | None = None
    quantity_unit: str | None = None
    cost: float | None = None
    performed_by: str | None = None
    details: dict | None = None
    logged_via: LoggedVia | None = None


class ActivityResponse(BaseModel):
    id: uuid.UUID
    crop_block_id: uuid.UUID
    activity_type: ActivityType
    activity_date: date
    product_used: str | None = None
    quantity: float | None = None
    quantity_unit: str | None = None
    cost: float | None = None
    performed_by: str | None = None
    details: dict | None = None
    logged_via: LoggedVia
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
