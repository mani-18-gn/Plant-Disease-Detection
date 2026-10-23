"""
Coordinator Agent Weighting Engine (Major_Final_!.md Table 4.6 & §4.4.7 / §4.5.3.7)

Table 4.6 Agent Consensus Weights:
- Diagnosis Agent: 35% (Disease detection critical)
- Weather Agent:   30% (Risk amplification factor)
- Market Agent:    20% (Economic optimization / price volatility)
- Learning Agent:  15% (System reinforcement / continuous improvement)

Note on Urgency Drivers:
The `urgency_drivers` list identifies primary actionable risk dimensions (Diagnosis, Weather, Market)
with raw sub-scores >= 60.0. The Learning Agent is a secondary system confidence modifier (Q-learning)
and is intentionally excluded from `urgency_drivers` to ensure clear agricultural/economic attribution.
"""

DIAGNOSIS_WEIGHT = 0.35
WEATHER_WEIGHT = 0.30
MARKET_WEIGHT = 0.20
LEARNING_WEIGHT = 0.15

LEARNING_PLACEHOLDER_STATUS = "placeholder_neutral_50_pending_learning_agent"


def compute_diagnosis_severity(diagnosis_dict: dict) -> tuple[float, str, str]:
    """
    Computes a 0-100 severity score from Diagnosis Agent output.
    Returns: (raw_score, status, summary)
    """
    if not diagnosis_dict:
        return 0.0, "ok", "No disease detection recorded (assumed healthy)"

    disease = diagnosis_dict.get("predicted_disease", "healthy_leaf")
    posterior = float(diagnosis_dict.get("posterior_probability", 0.0) or diagnosis_dict.get("cnn_confidence", 0.0) or 0.0)
    is_validated = diagnosis_dict.get("validated", False)
    status = diagnosis_dict.get("status", "ok")

    if disease.startswith("healthy_"):
        raw_score = round(max(0.0, 10.0 * (1.0 - posterior)), 2)
        summary = f"Healthy palm canopy ({disease}) - Low disease pressure"
        return raw_score, status, summary

    # Base severities for arecanut pathologies based on yield loss potential (Ref [7], [14])
    base_severity_map = {
        "mahali_koleroga": 100.0,     # Fruit Rot: up to 100% crop loss in monsoon (Ref [7])
        "yellow_leaf_disease": 85.0,  # Progressive systemic chlorosis (Ref [14])
        "bud_borer": 85.0,            # Apical meristem destruction (Ref [19])
        "stem_bleeding": 75.0,        # Vascular trunk rot (Ref [3], [14])
        "stem_cracking": 75.0,        # Structural trunk lesion
    }
    base = base_severity_map.get(disease, 80.0)
    val_multiplier = 1.0 if is_validated else 0.70
    raw_score = round(min(100.0, max(0.0, base * posterior * val_multiplier)), 2)
    summary = f"Detected {disease} (Posterior: {posterior*100:.1f}%, Validated: {is_validated})"
    return raw_score, status, summary


def compute_weather_urgency(weather_dict: dict) -> tuple[float, str, str]:
    """
    Extracts 0-100 environmental risk score from Weather Agent output.
    Returns: (raw_score, status, summary)
    """
    if not weather_dict:
        return 20.0, "partial_fallback", "Weather data unavailable; using baseline risk 20.0"

    risk_score = float(weather_dict.get("disease_risk_score", 20.0) or 20.0)
    level = weather_dict.get("disease_risk_level", "low")
    humidity = weather_dict.get("humidity", 70.0)
    rainfall = weather_dict.get("rainfall_mm", 0.0)
    status = weather_dict.get("status", "ok")

    raw_score = round(min(100.0, max(0.0, risk_score)), 2)
    summary = f"Weather disease risk: {level.upper()} ({raw_score:.1f}/100, Humidity: {humidity}%, Rain: {rainfall}mm)"
    return raw_score, status, summary


def compute_market_urgency(market_dict: dict) -> tuple[float, str, str]:
    """
    Evaluates 0-100 economic urgency / opportunity score from Market Agent output.
    - Falling trend: High urgency to sell before price drops (75-85)
    - Rising trend: Actionable holding/harvest opportunity (50-65)
    - Stable trend: Low urgency (25)
    Returns: (raw_score, status, summary)
    """
    if not market_dict:
        return 30.0, "partial_fallback", "Market price data unavailable; using baseline urgency 30.0"

    trend = market_dict.get("price_trend", "stable").lower()
    price = market_dict.get("current_price_per_kg", 475.0)
    mandi = market_dict.get("mandi_name", "APMC")
    status = market_dict.get("status", "ok")

    if trend == "falling":
        raw_score = 80.0
        summary = f"Falling price trend at {mandi} (₹{price:.2f}/kg) - Selling urgency elevated"
    elif trend == "rising":
        raw_score = 55.0
        summary = f"Rising price trend at {mandi} (₹{price:.2f}/kg) - Favorable market timing window"
    else:
        raw_score = 25.0
        summary = f"Stable prices at {mandi} (₹{price:.2f}/kg) - Normal economic pressure"

    return raw_score, status, summary


def compute_learning_confidence(learning_dict: dict | None = None) -> tuple[float, str, str]:
    """
    Learning Agent Sub-Score: 15% consensus weight.
    Pending Learning Agent implementation in Week 7, returns neutral 50.0 baseline.
    Returns: (raw_score, status, summary)
    """
    raw_score = 50.0
    status = "placeholder"
    summary = "Neutral 50% baseline prior to Q-learning feedback loop accumulation"
    return raw_score, status, summary


def compute_situation_score(
    diagnosis_dict: dict,
    weather_dict: dict,
    market_dict: dict,
    learning_dict: dict | None = None,
) -> dict:
    """
    Computes the Table 4.6 weighted consensus situation urgency score (0-100)
    and resolves active urgency drivers.
    """
    d_raw, d_status, d_summary = compute_diagnosis_severity(diagnosis_dict)
    w_raw, w_status, w_summary = compute_weather_urgency(weather_dict)
    m_raw, m_status, m_summary = compute_market_urgency(market_dict)
    l_raw, l_status, l_summary = compute_learning_confidence(learning_dict)

    d_weighted = round(d_raw * DIAGNOSIS_WEIGHT, 2)
    w_weighted = round(w_raw * WEATHER_WEIGHT, 2)
    m_weighted = round(m_raw * MARKET_WEIGHT, 2)
    l_weighted = round(l_raw * LEARNING_WEIGHT, 2)

    composite = round(d_weighted + w_weighted + m_weighted + l_weighted, 2)

    # Urgency Band Classification
    if composite >= 75.0:
        urgency_level = "urgent"
    elif composite >= 60.0:
        urgency_level = "high"
    elif composite >= 40.0:
        urgency_level = "moderate"
    else:
        urgency_level = "low"

    # Identify Primary Urgency Drivers (raw_score >= 60.0 across primary dimensions)
    urgency_drivers = []
    if d_raw >= 60.0:
        urgency_drivers.append("diagnosis")
    if w_raw >= 60.0:
        urgency_drivers.append("weather")
    if m_raw >= 60.0:
        urgency_drivers.append("market")

    return {
        "composite_score": composite,
        "urgency_level": urgency_level,
        "urgency_drivers": urgency_drivers,
        "learning_component_status": LEARNING_PLACEHOLDER_STATUS,
        "components": {
            "diagnosis": {
                "weight": DIAGNOSIS_WEIGHT,
                "raw_score": d_raw,
                "weighted_score": d_weighted,
                "status": d_status,
                "summary": d_summary,
            },
            "weather": {
                "weight": WEATHER_WEIGHT,
                "raw_score": w_raw,
                "weighted_score": w_weighted,
                "status": w_status,
                "summary": w_summary,
            },
            "market": {
                "weight": MARKET_WEIGHT,
                "raw_score": m_raw,
                "weighted_score": m_weighted,
                "status": m_status,
                "summary": m_summary,
            },
            "learning": {
                "weight": LEARNING_WEIGHT,
                "raw_score": l_raw,
                "weighted_score": l_weighted,
                "status": l_status,
                "summary": l_summary,
            },
        },
    }
