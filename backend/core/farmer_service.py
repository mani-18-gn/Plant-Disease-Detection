from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from backend.db.models.core.farmer_profile import FarmerProfile
from backend.schemas.farmer import FarmerProfileCreate, FarmerProfileUpdate


def create_farmer_profile(db: Session, user_id: str, data: FarmerProfileCreate) -> FarmerProfile:
    existing = db.query(FarmerProfile).filter(FarmerProfile.user_id == str(user_id)).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Farmer profile already exists for this user",
        )
    profile = FarmerProfile(user_id=str(user_id), **data.model_dump())
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def get_farmer_profile(db: Session, farmer_id: str) -> FarmerProfile:
    profile = db.query(FarmerProfile).filter(FarmerProfile.id == str(farmer_id)).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farmer profile not found",
        )
    return profile


def get_farmer_profile_by_user_id(db: Session, user_id: str) -> FarmerProfile:
    profile = db.query(FarmerProfile).filter(FarmerProfile.user_id == str(user_id)).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farmer profile not found for user",
        )
    return profile


def update_farmer_profile(db: Session, farmer_id: str, data: FarmerProfileUpdate) -> FarmerProfile:
    profile = get_farmer_profile(db, farmer_id)
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)
    db.commit()
    db.refresh(profile)
    return profile
