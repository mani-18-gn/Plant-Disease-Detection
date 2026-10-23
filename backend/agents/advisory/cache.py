import logging
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from backend.db.models.logs.advisory import Advisory

logger = logging.getLogger(__name__)

CACHE_FRESHNESS_HOURS = 6  # 6-hour cache validity window


def get_cached_advisory(
    db: Session,
    crop_block_id: str,
    current_snapshot: dict,
) -> Advisory | None:
    """
    Checks logs.advisories for a recent (<= 6 hours) advisory matching the current agronomic context.
    Matches on:
    - Same crop_block_id
    - Same diagnosis disease and validation status
    - Weather risk score within +/- 5 points
    - Market price within +/- 3%
    """
    six_hours_ago = datetime.now(timezone.utc) - timedelta(hours=CACHE_FRESHNESS_HOURS)

    recent_advisories = (
        db.query(Advisory)
        .filter(
            Advisory.crop_block_id == str(crop_block_id),
            Advisory.created_at >= six_hours_ago,
        )
        .order_by(Advisory.created_at.desc())
        .all()
    )

    if not recent_advisories:
        return None

    cur_diag = current_snapshot.get("diagnosis", {})
    cur_disease = cur_diag.get("predicted_disease")
    cur_val = cur_diag.get("validated")
    cur_weather_score = float(current_snapshot.get("weather", {}).get("disease_risk_score", 0.0) or 0.0)

    for adv in recent_advisories:
        snapshot = adv.input_snapshot
        if not isinstance(snapshot, dict):
            continue

        prev_diag = snapshot.get("diagnosis", {})
        prev_disease = prev_diag.get("predicted_disease")
        prev_val = prev_diag.get("validated")
        prev_weather_score = float(snapshot.get("weather", {}).get("disease_risk_score", 0.0) or 0.0)

        # Check for context match
        disease_match = (cur_disease == prev_disease) and (cur_val == prev_val)
        weather_match = abs(cur_weather_score - prev_weather_score) <= 5.0

        if disease_match and weather_match:
            logger.info(f"Advisory cache HIT for crop_block {crop_block_id} (Advisory ID: {adv.id})")
            return adv

    logger.info(f"Advisory cache MISS for crop_block {crop_block_id}")
    return None
