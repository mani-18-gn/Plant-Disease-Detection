"""
Learning Agent - Contextual Bandit Value-Updating Engine
(Refinement of Major_Final_!.md §4.4.6 / §4.5.3.6)

========================================================================================
DEVIATION FROM PHASE 1 REPORT SPECIFICATION & MATHEMATICAL JUSTIFICATION:
========================================================================================
1. Phase 1 Report Spec:
   Stated full Bellman temporal difference Q-learning:
       Q(s,a) <- Q(s,a) + alpha * [r + gamma * max_a' Q(s',a') - Q(s,a)]   (alpha=0.1, gamma=0.9)

2. Domain Reality & Architectural Justification:
   In precision agriculture advisory systems, agronomic advisory actions (e.g. "Apply 1% Bordeaux
   mixture" or "Delay harvest 3 days") do NOT cause subsequent environmental weather transitions
   or APMC market price fluctuations. Future states s' transition via exogenous natural and economic
   processes (Southwest monsoon frontal movements, regional commodity supply dynamics).

   Consequently, there is no causal state-transition probability P(s' | s, a), making the discounted
   future return term gamma * max_a' Q(s', a') non-causal and ungrounded in this domain.

3. Contextual Bandit Formulation:
   The problem is rigorously formulated as a Contextual Bandit reinforcement learning system:
       Q(s,a) <- Q(s,a) + alpha * [r - Q(s,a)]   (alpha=0.1)

   where Q(s,a) directly estimates the expected agronomic outcome E[r | s, a] for recommending
   action a under environmental/crop context state s.

4. Cell-Specific Observation Threshold Guardrail:
   - MIN_CELL_OBSERVATIONS = 3: Requires >= 3 feedback ratings for that specific (s,a) cell
     before activating learned confidence adjustment.
   - Below threshold: Returns neutral 50.0 baseline ("insufficient_data_using_baseline").
   - At/Above threshold: Returns 50.0 + 50.0 * tanh(Q(s,a)) in [0.0, 100.0] ("learned_active").
========================================================================================
"""

import math
import logging
from sqlalchemy.orm import Session

from backend.db.models.logs.feedback import Feedback
from backend.db.models.logs.advisory import Advisory

logger = logging.getLogger(__name__)

LEARNING_RATE_ALPHA = 0.1
MIN_CELL_OBSERVATIONS = 3  # Cell-specific observation threshold


def normalize_reward(rating: int) -> float:
    """Normalizes a 1-5 star rating to centered reward r in [-1.0, +1.0]."""
    clamped_rating = max(1, min(5, int(rating)))
    return round((clamped_rating - 3.0) / 2.0, 3)


def extract_state_key(input_snapshot: dict | None) -> str:
    """
    Extracts a discrete state key s = 'disease:weather_band:market_trend' from advisory input snapshot.
    """
    if not input_snapshot or not isinstance(input_snapshot, dict):
        return "healthy:low:stable"

    # 1. Disease category
    diag = input_snapshot.get("diagnosis", {})
    disease = diag.get("predicted_disease", "healthy_leaf")
    if "koleroga" in disease or "fruit_rot" in disease:
        disease_cat = "koleroga"
    elif "yellow" in disease:
        disease_cat = "yellow_leaf"
    elif "bleeding" in disease:
        disease_cat = "stem_bleeding"
    elif "cracking" in disease:
        disease_cat = "stem_cracking"
    elif "borer" in disease:
        disease_cat = "bud_borer"
    elif disease.startswith("healthy_") or disease == "healthy":
        disease_cat = "healthy"
    else:
        disease_cat = "other_disease"

    # 2. Weather risk band
    weather = input_snapshot.get("weather", {})
    risk_score = float(weather.get("disease_risk_score", 20.0) or 20.0)
    if risk_score >= 75.0:
        weather_band = "urgent"
    elif risk_score >= 60.0:
        weather_band = "high"
    elif risk_score >= 40.0:
        weather_band = "medium"
    else:
        weather_band = "low"

    # 3. Market trend
    market = input_snapshot.get("market", {})
    market_trend = market.get("price_trend", "stable").lower()
    if market_trend not in ["rising", "falling", "stable"]:
        market_trend = "stable"

    return f"{disease_cat}:{weather_band}:{market_trend}"


def extract_action_key(priority_str: str, recommended_actions: list | None = None) -> str:
    """
    Extracts a discrete action key a = 'priority:action_type' from advisory priority and actions.
    """
    p = str(priority_str).lower().strip()
    if p not in ["urgent", "high", "medium", "low"]:
        p = "medium"

    actions_text = " ".join(str(act) for act in (recommended_actions or [])).lower()
    if "bordeaux" in actions_text or "fungicide" in actions_text:
        action_type = "fungicide_spray"
    elif "zinc" in actions_text or "magnesium" in actions_text or "fertilizer" in actions_text or "manure" in actions_text:
        action_type = "nutrient_amendment"
    elif "chisel" in actions_text or "paste" in actions_text or "wound" in actions_text:
        action_type = "wound_dressing"
    elif "borer" in actions_text or "crown" in actions_text or "chlorpyrifos" in actions_text:
        action_type = "crown_sanitation"
    elif "delay" in actions_text or "harvest" in actions_text:
        action_type = "delay_harvest"
    elif "irrigation" in actions_text or "drip" in actions_text or "water" in actions_text:
        action_type = "irrigation"
    else:
        action_type = "routine_maintenance"

    return f"{p}:{action_type}"


def compute_cell_q_value(feedbacks_with_advisories: list) -> tuple[float, int]:
    """
    Computes Q(s,a) for a collection of historical feedback records sharing state s and action a.
    Applies chronological temporal exponential smoothing with alpha = 0.1:
    Q_t = Q_{t-1} + alpha * (r_t - Q_{t-1})
    """
    if not feedbacks_with_advisories:
        return 0.0, 0

    q_val = 0.0  # Initial uninformative prior Q0 = 0.0
    count = 0

    # Sort chronologically
    sorted_records = sorted(feedbacks_with_advisories, key=lambda pair: pair[0].created_at)

    for fb, _ in sorted_records:
        r = normalize_reward(fb.rating)
        q_val = q_val + LEARNING_RATE_ALPHA * (r - q_val)
        count += 1

    return round(q_val, 4), count


def get_learning_score(
    db: Session,
    state_key: str,
    action_key: str,
) -> dict:
    """
    Queries historical feedback for the given (s, a) cell, computes Q(s,a),
    and applies the cell-specific threshold guardrail.
    """
    # Fetch all feedback joined with parent advisories
    results = (
        db.query(Feedback, Advisory)
        .join(Advisory, Feedback.advisory_id == Advisory.id)
        .all()
    )

    cell_matches = []
    for fb, adv in results:
        s = extract_state_key(adv.input_snapshot)
        snap = adv.input_snapshot or {}
        a = extract_action_key(adv.priority.value if hasattr(adv.priority, "value") else str(adv.priority), snap.get("recommended_actions", []))
        if s == state_key and a == action_key:
            cell_matches.append((fb, adv))

    obs_count = len(cell_matches)

    if obs_count < MIN_CELL_OBSERVATIONS:
        return {
            "state_key": state_key,
            "action_key": action_key,
            "q_value": 0.0,
            "learning_score": 50.0,
            "observations": obs_count,
            "required_observations": MIN_CELL_OBSERVATIONS,
            "status": "insufficient_data_using_baseline",
        }

    q_value, _ = compute_cell_q_value(cell_matches)

    # Mapped learning score: 50.0 + 50.0 * tanh(q_value) in [0.0, 100.0]
    learned_score = round(50.0 + 50.0 * math.tanh(q_value), 2)

    return {
        "state_key": state_key,
        "action_key": action_key,
        "q_value": q_value,
        "learning_score": learned_score,
        "observations": obs_count,
        "required_observations": MIN_CELL_OBSERVATIONS,
        "status": "learned_active",
    }
