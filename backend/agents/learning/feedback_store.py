import logging
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status

from backend.db.models.logs.feedback import Feedback
from backend.db.models.logs.advisory import Advisory

logger = logging.getLogger(__name__)


def record_feedback(
    db: Session,
    advisory_id: str,
    farmer_id: str,
    rating: int,
    outcome_notes: str | None = None,
) -> Feedback:
    """
    Persists farmer feedback for a specific advisory.
    Automatically links crop_block_id from the parent advisory.
    """
    advisory = db.query(Advisory).filter(Advisory.id == str(advisory_id)).first()
    if not advisory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Advisory {advisory_id} not found",
        )

    if str(advisory.farmer_id) != str(farmer_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot submit feedback for an advisory issued to another farmer",
        )

    feedback = Feedback(
        advisory_id=str(advisory.id),
        farmer_id=str(farmer_id),
        crop_block_id=str(advisory.crop_block_id) if advisory.crop_block_id else None,
        rating=int(rating),
        outcome_notes=outcome_notes,
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)

    logger.info(
        f"Recorded feedback {feedback.id} for advisory {advisory_id} (Rating: {rating}/5)"
    )
    return feedback


def get_feedback_summary(
    db: Session,
    crop_block_id: str | None = None,
    farmer_id: str | None = None,
) -> dict:
    """
    Computes summary statistics (count, average rating, rating distribution)
    optionally scoped to a crop_block or farmer.
    """
    query = db.query(Feedback)
    if crop_block_id:
        query = query.filter(Feedback.crop_block_id == str(crop_block_id))
    if farmer_id:
        query = query.filter(Feedback.farmer_id == str(farmer_id))

    all_feedbacks = query.all()
    total_count = len(all_feedbacks)

    if total_count == 0:
        return {
            "crop_block_id": crop_block_id,
            "total_feedback_count": 0,
            "average_rating": 0.0,
            "rating_distribution": {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0},
        }

    avg_rating = round(sum(f.rating for f in all_feedbacks) / total_count, 2)
    dist = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0}
    for f in all_feedbacks:
        k = str(f.rating)
        if k in dist:
            dist[k] += 1

    return {
        "crop_block_id": crop_block_id,
        "total_feedback_count": total_count,
        "average_rating": avg_rating,
        "rating_distribution": dist,
    }


def list_feedback_for_advisory(db: Session, advisory_id: str) -> list[Feedback]:
    """Retrieves all feedback submitted for a particular advisory."""
    return (
        db.query(Feedback)
        .filter(Feedback.advisory_id == str(advisory_id))
        .order_by(Feedback.created_at.desc())
        .all()
    )


def list_feedback_for_farmer(db: Session, farmer_id: str) -> list[Feedback]:
    """Retrieves all historical feedback submitted by a farmer."""
    return (
        db.query(Feedback)
        .filter(Feedback.farmer_id == str(farmer_id))
        .order_by(Feedback.created_at.desc())
        .all()
    )
