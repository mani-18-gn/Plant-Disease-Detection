import uuid
from datetime import date
from pydantic import BaseModel, ConfigDict
from backend.db.models.core.crop_block import BlockStatus


class CropBlockCreate(BaseModel):
    farm_id: uuid.UUID
    block_name: str
    variety: str | None = None
    planting_date: date
    number_of_trees: int = 0
    spacing_meters: float | None = None
    status: BlockStatus = BlockStatus.ACTIVE
    notes: str | None = None


class CropBlockUpdate(BaseModel):
    block_name: str | None = None
    variety: str | None = None
    planting_date: date | None = None
    number_of_trees: int | None = None
    spacing_meters: float | None = None
    status: BlockStatus | None = None
    notes: str | None = None


class CropBlockStatusUpdate(BaseModel):
    status: BlockStatus


class CropBlockResponse(BaseModel):
    id: uuid.UUID
    farm_id: uuid.UUID
    block_name: str
    variety: str | None = None
    planting_date: date
    age_years: float
    number_of_trees: int
    spacing_meters: float | None = None
    status: BlockStatus
    notes: str | None = None

    model_config = ConfigDict(from_attributes=True)
