from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from backend.db.session import get_db
from backend.db.models.core.user import User
from backend.db.models.core.farm import Farm
from backend.db.models.core.crop_block import CropBlock, BlockStatus
from backend.auth.jwt_handler import get_current_user

from backend.schemas.farmer import (
    FarmerProfileCreate,
    FarmerProfileUpdate,
    FarmerProfileResponse,
)
from backend.schemas.farm import FarmCreate, FarmUpdate, FarmResponse
from backend.schemas.crop_block import (
    CropBlockCreate,
    CropBlockUpdate,
    CropBlockStatusUpdate,
    CropBlockResponse,
)
from backend.schemas.activity import ActivityCreate, ActivityResponse
from backend.db.models.agronomy.farm_activity import ActivityType

import backend.core.farmer_service as farmer_service
import backend.core.farm_service as farm_service
import backend.core.crop_block_service as crop_block_service
import backend.core.activity_service as activity_service

router = APIRouter(prefix="/core", tags=["Core Farmer & Land Management"])


# ── Ownership Helpers ─────────────────────────────────────────────────────────

def _get_farmer_profile_for_user(db: Session, user_id: str):
    """Helper: Retrieve farmer profile for current user or raise 404."""
    return farmer_service.get_farmer_profile_by_user_id(db, str(user_id))


def _verify_farm_ownership(db: Session, farm_id: str, user_id: str) -> Farm:
    """Helper: Verify farm exists and is owned by current user."""
    profile = _get_farmer_profile_for_user(db, user_id)
    farm = farm_service.get_farm(db, str(farm_id))
    if str(farm.farmer_id) != str(profile.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You do not own this farm",
        )
    return farm


def _verify_crop_block_ownership(db: Session, crop_block_id: str, user_id: str) -> CropBlock:
    """Helper: Verify crop block exists and belongs to a farm owned by current user."""
    profile = _get_farmer_profile_for_user(db, user_id)
    block = crop_block_service.get_crop_block(db, str(crop_block_id))
    farm = farm_service.get_farm(db, str(block.farm_id))
    if str(farm.farmer_id) != str(profile.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You do not own this crop block",
        )
    return block


# ── Farmer Profile Endpoints ──────────────────────────────────────────────────

@router.post("/profile", response_model=FarmerProfileResponse, status_code=status.HTTP_201_CREATED)
def create_profile(
    payload: FarmerProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return farmer_service.create_farmer_profile(db, str(current_user.id), payload)


@router.get("/profile", response_model=FarmerProfileResponse)
def read_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return _get_farmer_profile_for_user(db, str(current_user.id))


@router.put("/profile", response_model=FarmerProfileResponse)
def update_profile(
    payload: FarmerProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = _get_farmer_profile_for_user(db, str(current_user.id))
    return farmer_service.update_farmer_profile(db, str(profile.id), payload)


# ── Farm Endpoints ────────────────────────────────────────────────────────────

@router.post("/farms", response_model=FarmResponse, status_code=status.HTTP_201_CREATED)
def add_farm(
    payload: FarmCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = _get_farmer_profile_for_user(db, str(current_user.id))
    return farm_service.create_farm(db, str(profile.id), payload)


@router.get("/farms", response_model=list[FarmResponse])
def get_user_farms(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = _get_farmer_profile_for_user(db, str(current_user.id))
    return farm_service.list_farms_for_farmer(db, str(profile.id))


@router.get("/farms/{farm_id}", response_model=FarmResponse)
def get_single_farm(
    farm_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return _verify_farm_ownership(db, farm_id, str(current_user.id))


@router.put("/farms/{farm_id}", response_model=FarmResponse)
def edit_farm(
    farm_id: str,
    payload: FarmUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _verify_farm_ownership(db, farm_id, str(current_user.id))
    return farm_service.update_farm(db, farm_id, payload)


@router.delete("/farms/{farm_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_farm(
    farm_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _verify_farm_ownership(db, farm_id, str(current_user.id))
    farm_service.delete_farm(db, farm_id)
    return None


@router.post("/crop-blocks", response_model=CropBlockResponse, status_code=status.HTTP_201_CREATED)
def add_crop_block(
    payload: CropBlockCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _verify_farm_ownership(db, str(payload.farm_id), str(current_user.id))
    return crop_block_service.create_crop_block(db, str(payload.farm_id), payload)


@router.post("/farms/{farm_id}/crop-blocks", response_model=CropBlockResponse, status_code=status.HTTP_201_CREATED)
def add_crop_block_nested(
    farm_id: str,
    payload: CropBlockCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _verify_farm_ownership(db, farm_id, str(current_user.id))
    return crop_block_service.create_crop_block(db, farm_id, payload)


@router.get("/farms/{farm_id}/crop-blocks", response_model=list[CropBlockResponse])
def get_farm_crop_blocks(
    farm_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _verify_farm_ownership(db, farm_id, str(current_user.id))
    return crop_block_service.list_crop_blocks_for_farm(db, farm_id)


@router.get("/crop-blocks/{block_id}", response_model=CropBlockResponse)
def get_single_crop_block(
    block_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return _verify_crop_block_ownership(db, block_id, str(current_user.id))


@router.put("/crop-blocks/{block_id}", response_model=CropBlockResponse)
def edit_crop_block(
    block_id: str,
    payload: CropBlockUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _verify_crop_block_ownership(db, block_id, str(current_user.id))
    return crop_block_service.update_crop_block(db, block_id, payload)


@router.patch("/crop-blocks/{block_id}/status", response_model=CropBlockResponse)
def edit_crop_block_status(
    block_id: str,
    payload: CropBlockStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _verify_crop_block_ownership(db, block_id, str(current_user.id))
    return crop_block_service.update_crop_block_status(db, block_id, payload.status)


# ── Farm Activity Endpoints ───────────────────────────────────────────────────

@router.post("/activities", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED)
def record_activity(
    payload: ActivityCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _verify_crop_block_ownership(db, str(payload.crop_block_id), str(current_user.id))
    return activity_service.log_activity(db, str(payload.crop_block_id), payload)


@router.get("/crop-blocks/{block_id}/activities", response_model=list[ActivityResponse])
def get_activities_by_block(
    block_id: str,
    activity_type: ActivityType | None = Query(None),
    since_date: date | None = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _verify_crop_block_ownership(db, block_id, str(current_user.id))
    return activity_service.list_activities_for_block(db, block_id, activity_type, since_date)


@router.get("/crop-blocks/{block_id}/activities/latest", response_model=ActivityResponse | None)
def get_latest_activity(
    block_id: str,
    activity_type: ActivityType = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _verify_crop_block_ownership(db, block_id, str(current_user.id))
    activity = activity_service.get_last_activity_of_type(db, block_id, activity_type)
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No activity of type {activity_type.value} found for block",
        )
    return activity
