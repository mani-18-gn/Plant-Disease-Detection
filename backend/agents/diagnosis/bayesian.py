import logging

logger = logging.getLogger(__name__)

# Exact 9-class normalized literature baseline priors (Sum = 1.00)
LITERATURE_PRIORS = {
    "mahali_koleroga": 0.30,
    "yellow_leaf_disease": 0.20,
    "stem_bleeding": 0.08,
    "stem_cracking": 0.08,
    "bud_borer": 0.08,
    "healthy_nut": 0.08,
    "healthy_leaf": 0.08,
    "healthy_trunk": 0.06,
    "healthy_foot": 0.04,
}

# Regional epidemiological prevalence baselines for multi-crop species
MULTI_CROP_PRIORS = {
    # Tomato
    "tomato_early_blight": 0.25,
    "tomato_late_blight": 0.25,
    "tomato_leaf_mold": 0.18,
    "tomato_septoria_leaf_spot": 0.20,
    "tomato_spider_mites": 0.15,
    "tomato_target_spot": 0.15,
    "tomato_bacterial_spot": 0.20,
    "tomato_yellow_leaf_curl": 0.15,
    "tomato_mosaic_virus": 0.10,
    "tomato_healthy": 0.45,
    # Potato
    "potato_early_blight": 0.25,
    "potato_late_blight": 0.30,
    "potato_healthy": 0.45,
    # Chilli / Pepper
    "pepper_bacterial_spot": 0.22,
    "pepper_healthy": 0.45,
    # Corn
    "corn_common_rust": 0.25,
    "corn_northern_leaf_blight": 0.25,
    "corn_gray_leaf_spot": 0.20,
    "corn_healthy": 0.45,
    # Grape
    "grape_black_rot": 0.25,
    "grape_esca": 0.15,
    "grape_leaf_blight": 0.20,
    "grape_healthy": 0.45,
    # Apple
    "apple_apple_scab": 0.25,
    "apple_black_rot": 0.20,
    "apple_cedar_apple_rust": 0.20,
    "apple_healthy": 0.45,
    # Citrus
    "citrus_greening": 0.20,
}

VALIDATION_THRESHOLD = 0.75  # Threshold > 0.75 per Major_Final_!.md §4.4.2


def get_hybrid_prior(predicted_disease: str, historical_detections: list, pseudo_count: float = 5.0) -> float:
    """
    Computes hybrid prior P(Disease):
    - When regional detections count N < 10, uses the literature / baseline epidemiological prior P0.
    - When N >= 10, uses Laplace/m-estimate smoothed empirical frequency: (count + m*P0) / (N + m).
    """
    if predicted_disease in LITERATURE_PRIORS:
        p0 = LITERATURE_PRIORS[predicted_disease]
    else:
        import re
        normalized = re.sub(r"[^a-z0-9]+", "_", predicted_disease.lower()).strip("_")
        matched = None
        for key, val in MULTI_CROP_PRIORS.items():
            if key in normalized or normalized in key:
                matched = val
                break
        if matched is not None:
            p0 = matched
        elif "healthy" in normalized:
            p0 = 0.40
        elif "late_blight" in normalized or "early_blight" in normalized:
            p0 = 0.25
        elif "rust" in normalized or "scab" in normalized or "rot" in normalized:
            p0 = 0.22
        elif "spot" in normalized or "mold" in normalized:
            p0 = 0.20
        else:
            p0 = 0.18

    total_n = len(historical_detections)

    if total_n < 10:
        return p0

    disease_matches = sum(1 for d in historical_detections if d.predicted_disease == predicted_disease)
    smoothed_prior = (disease_matches + pseudo_count * p0) / (total_n + pseudo_count)
    return round(float(smoothed_prior), 4)


def compute_posterior(
    cnn_confidence: float,
    weather_risk_score: float,
    predicted_disease: str,
    historical_prior: float,
    is_synthetic_weather: bool = False,
) -> tuple[float, bool]:
    """
    Computes Bayesian Posterior Probability P(Disease | Image, Weather, History)
    P(D | Evidence) = [P(Image|D) * P(Weather|D) * P(D)] / P(Evidence)

    Where P(Evidence) is normalized across binary hypothesis states:
    P(Evidence) = P(Image|D)*P(Weather|D)*P(D) + P(Image|¬D)*P(Weather|¬D)*P(¬D)

    Returns:
        tuple (posterior_probability: float, validated: bool)
    """
    # 1. Image Likelihoods
    p_image_given_d = max(0.01, min(0.99, float(cnn_confidence)))
    p_image_given_not_d = 1.0 - p_image_given_d

    # 2. Weather Likelihoods (scaled from 0-100 risk score)
    norm_score = max(0.0, min(100.0, float(weather_risk_score))) / 100.0
    is_healthy = "healthy" in predicted_disease.lower()

    if is_healthy:
        # Dry/unfavorable disease conditions favor healthy palm observations
        p_weather_given_d = 0.95 - (norm_score * 0.75)
        p_weather_given_not_d = 0.20 + (norm_score * 0.75)
    else:
        # High humidity & rainfall heavily favor fungal disease occurrence
        p_weather_given_d = 0.20 + (norm_score * 0.75)
        p_weather_given_not_d = 0.95 - (norm_score * 0.75)

    # 3. Synthetic Weather Dampening (shrink toward uninformative neutral likelihood 0.50)
    if is_synthetic_weather:
        p_weather_given_d = 0.50 + 0.50 * (p_weather_given_d - 0.50)
        p_weather_given_not_d = 0.50 + 0.50 * (p_weather_given_not_d - 0.50)

    # 4. Prior Probabilities
    p_d = max(0.01, min(0.99, float(historical_prior)))
    p_not_d = 1.0 - p_d

    # 5. Marginal Evidence Normalization
    joint_d = p_image_given_d * p_weather_given_d * p_d
    joint_not_d = p_image_given_not_d * p_weather_given_not_d * p_not_d

    marginal_evidence = joint_d + joint_not_d
    if marginal_evidence <= 0:
        posterior = p_image_given_d
    else:
        posterior = joint_d / marginal_evidence

    posterior = round(float(min(0.9999, max(0.0001, posterior))), 4)
    validated = bool(posterior > VALIDATION_THRESHOLD)

    return posterior, validated
