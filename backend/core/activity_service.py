from datetime import date
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from backend.db.models.agronomy.farm_activity import FarmActivity, ActivityType
from backend.schemas.activity import ActivityCreate, ActivityUpdate


def log_activity(db: Session, crop_block_id: str, data: ActivityCreate) -> FarmActivity:
    payload_dict = data.model_dump()
    payload_dict["crop_block_id"] = str(crop_block_id)
    activity = FarmActivity(**payload_dict)
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity


def list_activities_for_block(
    db: Session,
    crop_block_id: str,
    activity_type: ActivityType | None = None,
    since_date: date | None = None,
) -> list[FarmActivity]:
    query = db.query(FarmActivity).filter(FarmActivity.crop_block_id == str(crop_block_id))
    if activity_type:
        query = query.filter(FarmActivity.activity_type == activity_type)
    if since_date:
        query = query.filter(FarmActivity.activity_date >= since_date)
    return query.order_by(FarmActivity.activity_date.desc()).all()


def get_last_activity_of_type(
    db: Session,
    crop_block_id: str,
    activity_type: ActivityType,
) -> FarmActivity | None:
    return (
        db.query(FarmActivity)
        .filter(
            FarmActivity.crop_block_id == str(crop_block_id),
            FarmActivity.activity_type == activity_type,
        )
        .order_by(FarmActivity.activity_date.desc())
        .first()
    )
