import logging

logger = logging.getLogger(__name__)


STANDARD_AGROCHEMICAL_DISCLAIMER = (
    "Chemical and dosage recommendations follow standard agricultural extension practices (ICAR-CPCRI / State Agricultural Universities). "
    "Farmers are advised to consult their local Agricultural Extension Officer (RSK / KVK) before applying any chemical treatment."
)


def generate_rule_based_advisory(context_dict: dict) -> dict:
    """
    Deterministic Rule-Based Advisory Engine.
    Directly grounded in:
    - Major_Final_!.md §4.4.5 & Table 4.5 (Advisory Priority Matrix & IF-THEN Rules)
    - Ref [7]  Patil Balanagouda et al. (2019) - Phytophthora Fruit Rot epidemiology & Bordeaux mixture control
    - Ref [14] Vinod Upadhyay & Elangbam Premabati Devi (2015) - Diseases of Arecanut and their Management
    - Ref [10] Ravi Bhat & S. Sujatha (2003) - Integrated nutrient management & organic recycling
    - Ref [16] K. Rajashree et al. (2021) - Weather-based Fruit Rot prediction & spray timing
    - Ref [19] Sneha C. Siddalingadevaru et al. (2025) - Disease Diagnosis & Sustainable Prevention
    - Ref [3]  Pallavi Shetty et al. (2023) - ArecaShield multi-agent advisory system
    """
    crop_block = context_dict.get("crop_block", {})
    block_name = crop_block.get("block_name", "your crop block")

    diagnosis = context_dict.get("diagnosis", {})
    predicted_disease = diagnosis.get("predicted_disease", "healthy_leaf")
    posterior = float(diagnosis.get("posterior_probability", 0.0) or 0.0)
    is_validated = diagnosis.get("validated", False)

    weather = context_dict.get("weather", {})
    risk_score = float(weather.get("disease_risk_score", 20.0) or 20.0)
    rainfall_mm = float(weather.get("rainfall_mm", 0.0) or 0.0)
    humidity = float(weather.get("humidity", 70.0) or 70.0)

    market = context_dict.get("market", {})
    mandi_name = market.get("mandi_name", "APMC")
    price_trend = market.get("price_trend", "stable")

    activities = context_dict.get("recent_activities", {})
    days_since_spray = activities.get("days_since_last_spray")
    days_since_irrigation = activities.get("days_since_last_irrigation")

    # RULE 1: URGENT - Validated Koleroga / Fruit Rot under high disease risk weather
    if (predicted_disease == "mahali_koleroga" and (is_validated or posterior >= 0.70)) or (risk_score >= 75.0 and days_since_spray is not None and days_since_spray >= 28):
        return {
            "priority": "urgent",
            "message": f"Critical Fruit Rot (Mahali/Koleroga) risk in {block_name}. Immediate bunch protection is required before continuous rainfall spreads fungal spores.",
            "recommended_actions": [
                "Spray 1% Bordeaux mixture (1kg copper sulfate + 1kg quicklime in 100L water) thoroughly on all developing nut bunches within 24-48 hours.",
                "Collect and burn or bury all fallen, rotting nuts to eliminate local inoculum sources.",
                "Fasten polythene covers over mature bunches in high-rainfall pockets to prevent rain-splash infection.",
                "Open field drainage channels to prevent stagnant water accumulation around palm roots."
            ],
            "reasoning_summary": f"Severe Koleroga threat identified (Posterior: {posterior*100:.1f}%, Weather Risk: {risk_score:.1f}). Preventive spraying must occur before heavy rain.",
            "disclaimer": STANDARD_AGROCHEMICAL_DISCLAIMER,
            "generated_by": "rule_fallback",
        }

    # RULE 2: HIGH - Validated Yellow Leaf Disease (YLD)
    if predicted_disease == "yellow_leaf_disease" and (is_validated or posterior >= 0.65):
        return {
            "priority": "high",
            "message": f"Yellow Leaf Disease symptoms confirmed in {block_name}. Implement restorative nutrient and root health management.",
            "recommended_actions": [
                "Apply micro-nutrient foliar spray: Zinc Sulfate (0.5%) + Magnesium Sulfate (1.0%) to improve chlorophyll retention.",
                "Incorporate 25kg farmyard manure (FYM) + 2kg neem cake per palm into the root basin.",
                "Aerate the root zone with light shallow hoeing and improve drainage to reduce root water-logging.",
                "Spray systemic insecticide (Dimethoate 30 EC @ 1.5ml/L) if leaf-hopper vectors are observed."
            ],
            "reasoning_summary": f"Validated Yellow Leaf Disease ({posterior*100:.1f}% confidence). Focus on foliar micronutrients and soil organic amendment.",
            "disclaimer": STANDARD_AGROCHEMICAL_DISCLAIMER,
            "generated_by": "rule_fallback",
        }

    # RULE 3: HIGH - Validated Stem Bleeding / Stem Cracking
    if predicted_disease in ["stem_bleeding", "stem_cracking"] and (is_validated or posterior >= 0.65):
        return {
            "priority": "high",
            "message": f"Stem lesion / bleeding infection detected on trunk tissues in {block_name}.",
            "recommended_actions": [
                "Chisel out infected, discolored bark tissues using a sharp chisel until healthy tissue is exposed.",
                "Dress the wound with 10% Bordeaux paste or Coal Tar to seal the exposed trunk.",
                "Apply Trichoderma reesei enriched organic compost (5kg/palm) around the base.",
                "Avoid mechanical injuries to the lower trunk during inter-cultivation."
            ],
            "reasoning_summary": f"Trunk pathology detected ({predicted_disease}). Localized wound dressing and root zone bio-agent application advised.",
            "disclaimer": STANDARD_AGROCHEMICAL_DISCLAIMER,
            "generated_by": "rule_fallback",
        }

    # RULE 4: HIGH - Validated Bud Borer Infestation
    if predicted_disease == "bud_borer" and (is_validated or posterior >= 0.65):
        return {
            "priority": "high",
            "message": f"Bud borer insect damage identified in {block_name}.",
            "recommended_actions": [
                "Clean the palm crown and remove all dried spathes and decayed floral parts.",
                "Apply Chlorpyrifos 20 EC (@ 2ml/L) or Neem oil (0.5%) directly into the top leaf axils.",
                "Place pheromone / kairomone traps around the plantation border to monitor adult weevil populations."
            ],
            "reasoning_summary": f"Bud borer activity confirmed ({posterior*100:.1f}% confidence). Crown sanitation and targeted axil drenching required.",
            "disclaimer": STANDARD_AGROCHEMICAL_DISCLAIMER,
            "generated_by": "rule_fallback",
        }

    # RULE 5: MEDIUM - High Market Price Trend + Healthy Crop (Optimal Harvest Timing)
    if price_trend == "rising" and predicted_disease.startswith("healthy_"):
        return {
            "priority": "medium",
            "message": f"Market prices at {mandi_name} are trending upward while {block_name} remains healthy. Consider timing harvest to maximize returns.",
            "recommended_actions": [
                "Delay harvesting fully mature green nuts by 3-5 days if weather permits to benefit from rising mandi prices.",
                "Prepare drying yards and processing machinery for upcoming harvest arrivals.",
                "Inspect boundary palms for any early symptom onset during the holding period."
            ],
            "reasoning_summary": f"Healthy crop block coupled with rising {mandi_name} price trend presents favorable market timing opportunity.",
            "disclaimer": STANDARD_AGROCHEMICAL_DISCLAIMER,
            "generated_by": "rule_fallback",
        }

    # RULE 6: MEDIUM - Moisture Stress / Irrigation Needed
    if rainfall_mm == 0.0 and humidity < 60.0 and (days_since_irrigation is None or days_since_irrigation >= 6):
        return {
            "priority": "medium",
            "message": f"Low soil moisture conditions detected in {block_name}. Schedule irrigation cycle to prevent nut dropping.",
            "recommended_actions": [
                "Provide drip irrigation at 15-20 liters per palm per day during morning hours.",
                "Apply organic green leaf mulching or arecanut leaf sheaths in 1.5m radius around palm basins to conserve soil moisture.",
                "Inspect micro-irrigation drippers for clogging or pressure loss."
            ],
            "reasoning_summary": "Dry weather (low humidity, zero rain) and prolonged interval since last irrigation requires supplemental moisture.",
            "disclaimer": STANDARD_AGROCHEMICAL_DISCLAIMER,
            "generated_by": "rule_fallback",
        }

    # RULE 7: LOW - Normal Routine Cultural Maintenance
    return {
        "priority": "low",
        "message": f"{block_name} is in good health with normal environmental and market indicators. Maintain standard cultural practices.",
        "recommended_actions": [
            "Maintain routine basin weeding and ring trench cleanout.",
            "Apply green leaf mulch around palm bases to support soil microflora.",
            "Conduct weekly visual scouting for any early leaf or nut discoloration."
        ],
        "reasoning_summary": "Crop is healthy with no elevated meteorological disease risk or acute market disruptions.",
        "disclaimer": STANDARD_AGROCHEMICAL_DISCLAIMER,
        "generated_by": "rule_fallback",
    }
