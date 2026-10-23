import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class FarmerProfileCreate(BaseModel):
    full_name: str
    village: str | None = None
    taluk: str | None = None
    district: str | None = None
    state: str | None = None
    pincode: str | None = None
    preferred_language: str = "kn"
    preferred_mandi: str | None = None


class FarmerProfileUpdate(BaseModel):
    full_name: str | None = None
    village: str | None = None
    taluk: str | None = None
    district: str | None = None
    state: str | None = None
    pincode: str | None = None
    preferred_language: str | None = None
    preferred_mandi: str | None = None


class FarmerProfileResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    full_name: str
    village: str | None = None
    taluk: str | None = None
    district: str | None = None
    state: str | None = None
    pincode: str | None = None
    preferred_language: str | None = None
    preferred_mandi: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
