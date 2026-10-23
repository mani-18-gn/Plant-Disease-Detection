from backend.schemas.weather import DiseaseRiskScore, DiseaseRiskLevel, DiseaseRiskFactorBreakdown


def calculate_disease_risk_score(
    humidity: float,
    temperature: float,
    rainfall_mm: float,
    is_synthetic: bool = False,
) -> DiseaseRiskScore:
    """
    Computes a weighted Disease Risk Score (0.0 - 100.0) and Risk Level for Arecanut diseases
    (specifically Koleroga / Fruit Rot and Yellow Leaf Disease) based on §4.4.5 & §4.5.3.3 rules.

    Risk Factors & Weight Breakdown:
    1. Relative Humidity (Max 40 Points):
       - > 85% RH is optimal for fungal spore germination.
       - Linear scaling between 70% (0 pts) and 95%+ (40 pts).
    2. Temperature Range (Max 35 Points):
       - Optimal fungal proliferation occurs between 22°C and 28°C.
       - Peak 35 pts at 25°C; tapers to 0 pts below 18°C or above 32°C.
    3. Imminent Rainfall (Max 25 Points):
       - Rain splash spreads spores across the canopy.
       - Linear scaling between 0 mm (0 pts) and 25+ mm (25 pts).

    Risk Levels:
       - 0.0  - 29.9 -> LOW
       - 30.0 - 59.9 -> MEDIUM
       - 60.0 - 79.9 -> HIGH
       - 80.0 - 100.0 -> URGENT

    Confidence Level:
       - Real API Data -> "verified_api" (is_synthetic=False)
       - Synthetic Fallback Data -> "unverified_synthetic" (is_synthetic=True)
    """
    # 1. Humidity Points (0.0 to 40.0)
    if humidity <= 70.0:
        humidity_points = 0.0
    elif humidity >= 95.0:
        humidity_points = 40.0
    else:
        humidity_points = ((humidity - 70.0) / 25.0) * 40.0

    # 2. Temperature Points (0.0 to 35.0)
    if 22.0 <= temperature <= 28.0:
        # Ideal range for Phytophthora meadii (Fruit Rot)
        temp_diff = abs(temperature - 25.0)
        temperature_points = 35.0 - (temp_diff * 2.0)
    elif 18.0 <= temperature < 22.0:
        temperature_points = ((temperature - 18.0) / 4.0) * 20.0
    elif 28.0 < temperature <= 32.0:
        temperature_points = ((32.0 - temperature) / 4.0) * 20.0
    else:
        temperature_points = 0.0

    # 3. Rainfall Points (0.0 to 25.0)
    if rainfall_mm <= 0.0:
        rainfall_points = 0.0
    elif rainfall_mm >= 25.0:
        rainfall_points = 25.0
    else:
        rainfall_points = (rainfall_mm / 25.0) * 25.0

    # Total score calculation clamped between 0.0 and 100.0
    total_score = round(min(100.0, max(0.0, humidity_points + temperature_points + rainfall_points)), 2)

    # Determine Risk Level
    if total_score >= 80.0:
        level = DiseaseRiskLevel.URGENT
    elif total_score >= 60.0:
        level = DiseaseRiskLevel.HIGH
    elif total_score >= 30.0:
        level = DiseaseRiskLevel.MEDIUM
    else:
        level = DiseaseRiskLevel.LOW

    confidence_level = "unverified_synthetic" if is_synthetic else "verified_api"

    return DiseaseRiskScore(
        score=total_score,
        level=level,
        confidence_level=confidence_level,
        is_synthetic=is_synthetic,
        factors=DiseaseRiskFactorBreakdown(
            humidity_points=round(humidity_points, 2),
            temperature_points=round(temperature_points, 2),
            rainfall_points=round(rainfall_points, 2),
        ),
    )
