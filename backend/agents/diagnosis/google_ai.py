"""
Google-Powered Plant Disease Identification & Grounded Diagnosis Service.
Official SDK: google-genai (Google Gen AI SDK v2.x)

Features:
1. Plant Identification (common name, scientific name, identification certainty).
2. Foliage Plausibility (detects non-plant images and rejects them safely).
3. Symptom-level Visual Pathology (lesions, discoloration, chlorosis, wilting, mold, necrosis).
4. Differential Diagnosis (distinguishing fungal, bacterial, viral, nutrient deficiency, pest, stress, or healthy).
5. Grounded Agricultural Verification (Google Search grounding with fallback to ICAR/academic monographs).
6. Qualitative Confidence (Low, Moderate, High) with explicit uncertainty disclaimers.
7. Strict backend security: GOOGLE_API_KEY is read securely on the server and never exposed to the frontend.
"""

import io
import json
import logging
import os
import re
from typing import Any, Dict, List, Optional
from PIL import Image

try:
    from google import genai
    from google.genai import types
    from google.genai.errors import APIError
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    genai = None
    types = None
    APIError = Exception

from backend.config import settings
from backend.agents.vision.web_research import search_agricultural_research

logger = logging.getLogger(__name__)

# Supported models in priority order
PRIMARY_MODEL = "gemini-3.1-flash-lite-preview"
FALLBACK_MODELS = ["gemini-3-flash-preview"]


def get_google_api_key() -> Optional[str]:
    """Retrieve Google API key from backend environment or configuration."""
    key = settings.GOOGLE_API_KEY or os.environ.get("GOOGLE_API_KEY")
    if not key:
        # Fallback to GEMINI_API_KEY if configured
        key = getattr(settings, "GEMINI_API_KEY", "") or os.environ.get("GEMINI_API_KEY")
    return key.strip() if key else None


def is_google_ai_configured() -> bool:
    """Return True if google-genai is installed and an API key is set."""
    return GENAI_AVAILABLE and bool(get_google_api_key())


def get_google_ai_status() -> Dict[str, Any]:
    """Return public health/status dictionary (never leaks the key itself)."""
    api_key = get_google_api_key()
    configured = bool(api_key)
    return {
        "sdk_installed": GENAI_AVAILABLE,
        "api_key_configured": configured,
        "is_configured": configured,
        "status": "ready" if (GENAI_AVAILABLE and configured) else "api_key_missing" if GENAI_AVAILABLE else "sdk_missing",
        "primary_model": PRIMARY_MODEL,
        "grounding": "Google Search Grounding + ICAR/Extension Knowledge Monograph",
        "message": (
            "Google Gen AI Agent ready for multimodal plant pathology."
            if (GENAI_AVAILABLE and configured)
            else "GOOGLE_API_KEY is not configured on the backend server. Add GOOGLE_API_KEY to backend/.env to activate Google-powered AI diagnosis."
        ),
    }


def _clean_json_text(text: str) -> str:
    """Extract raw JSON text from markdown code blocks or unstructured wrappers."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
    # Match the first outer JSON object
    match = re.search(r"(\{.*\})", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()


def _build_diagnostic_prompt(crop_hint: Optional[str] = None, user_symptoms: Optional[str] = None, location: Optional[str] = None) -> str:
    context_hints = []
    if crop_hint and crop_hint.lower() not in ["auto", "none", "unknown"]:
        context_hints.append(f"User identified crop hint: '{crop_hint}'")
    if user_symptoms:
        context_hints.append(f"User noted field symptoms: '{user_symptoms}'")
    if location:
        context_hints.append(f"Geographic location / climate region: '{location}'")

    hint_str = " | ".join(context_hints) if context_hints else "None provided (auto-detection required)"

    return f"""You are a Senior Plant Pathologist and Agricultural Extension Specialist.
Analyze the attached photograph of a plant specimen carefully.

ADDITIONAL CONTEXT FROM FARMER: {hint_str}

DIAGNOSTIC PROTOCOL:
1. PLAUSIBILITY & PLANT CHECK:
   - Determine if the image actually shows a plant, crop, leaf, stem, fruit, or foliage.
   - If the image is NOT a plant (e.g. human, animal, furniture, vehicle, indoor object, or abstract image), set "is_plant": false and describe what is visible.
2. IMAGE QUALITY CHECK:
   - Check if the photograph is clear, focused, and well-lit.
   - If blurry, dark, or insufficient, set "image_quality": "poor_blurry_or_dark" and describe what additional visual view is needed.
3. SPECIES IDENTIFICATION:
   - Identify common name and scientific botanical name.
   - State identification certainty: "High", "Moderate", or "Low".
4. SYMPTOM EXAMINATION:
   - Inspect specific leaf lesions, chlorosis, halos, water-soaked spots, wilting, curling, powdery growth, pustules, or insect chewing.
5. DIFFERENTIAL DIAGNOSIS:
   - Differentiate fungal, bacterial, viral, pest damage, nutritional deficiency, environmental stress, or healthy foliage.
   - List alternative plausible conditions that look similar and explain key distinguishing signs.
6. EVIDENCE-BASED MANAGEMENT:
   - Immediate cultural sanitation (removing diseased leaves, airflow).
   - Biological management (beneficial bio-agents, Trichoderma, neem extract).
   - Chemical management: evidence-based recommendations ONLY when supported by official extension guidance. Always include safety precautions and label instructions.
7. AUTHORITATIVE SOURCES:
   - Cite authoritative research institutions (e.g., ICAR institutes, State Agricultural Universities, Extension Guides, FAO).
8. UNCERTAINTY:
   - Do NOT invent artificial numerical accuracy.
   - Set confidence to "High", "Moderate", or "Low" with an explanation of uncertainty and advise consulting local agricultural extension officers.

YOU MUST RESPOND ONLY WITH A VALID JSON OBJECT WITH THIS EXACT STRUCTURE:
{{
  "is_plant": true,
  "rejection_reason": null,
  "image_quality": "good",
  "plant_identification": {{
    "common_name": "Tomato",
    "scientific_name": "Solanum lycopersicum",
    "certainty": "High",
    "plant_part": "Leaf"
  }},
  "disease_assessment": {{
    "is_healthy": false,
    "most_likely_disease": "Tomato Early Blight",
    "pathogen_scientific_name": "Alternaria solani",
    "cause": "fungal",
    "confidence": "High",
    "confidence_explanation": "Characteristic concentric dark target-ring lesions with chlorotic yellow halos on lower foliage.",
    "symptoms_observed": [
      "Brown to black circular spots with concentric rings",
      "Yellow chlorotic halos surrounding lesions",
      "Early leaf senescence on lower canopy"
    ],
    "plausibility_explanation": "Visible concentric target spots are hallmark diagnostic criteria of Alternaria leaf blight.",
    "differential_diagnosis": [
      {{
        "disease_name": "Septoria Leaf Spot (Septoria lycopersici)",
        "distinguishing_feature": "Smaller circular spots with distinct gray centers and black fruiting pycnidia, lacking large target rings."
      }},
      {{
        "disease_name": "Bacterial Spot (Xanthomonas perforans)",
        "distinguishing_feature": "Water-soaked small angular spots that do not form concentric circles."
      }}
    ]
  }},
  "disease_information": {{
    "typical_symptoms": "Dark brown concentric target spots starting on older lower leaves, spreading upward under warm humid conditions.",
    "favorable_conditions": "Warm temperatures (24-29°C) combined with high relative humidity, frequent rain, or overhead irrigation."
  }},
  "treatment_and_management": {{
    "immediate_actions": [
      "Prune and safely destroy lower infected leaves to prevent spore splash.",
      "Avoid overhead sprinkler irrigation; irrigate at root zone."
    ],
    "cultural_practices": [
      "Practice 3-year crop rotation away from solanaceous crops.",
      "Ensure adequate plant spacing for canopy ventilation.",
      "Apply organic mulch around plant bases to prevent soil splash onto foliage."
    ],
    "biological_control": [
      "Foliar spray of Trichoderma harzianum or Bacillus subtilis formulations.",
      "Neem seed kernel extract (NSKE 5%) as prophylactic repellent."
    ],
    "chemical_management": [
      "Chlorothalonil (0.2%) or Mancozeb (0.25%) applied at earliest onset.",
      "Copper oxychloride (0.3%) for mixed fungal/bacterial protection."
    ],
    "safety_precautions": "Always wear personal protective equipment (gloves, mask) and strictly observe pre-harvest intervals according to product label.",
    "preventive_measures": [
      "Plant certified disease-free seeds and resistant varieties.",
      "Maintain balanced potassium and nitrogen soil nutrition."
    ]
  }},
  "sources": [
    {{
      "title": "Integrated Pest and Disease Management in Solanaceous Vegetables",
      "organization": "ICAR - Indian Institute of Horticultural Research (IIHR)",
      "url": "https://iihr.res.in/",
      "notes": "Standard extension recommendations for foliar blight prevention."
    }}
  ],
  "uncertainty_disclaimer": "Photographic AI screening is an advisory aid and cannot replace laboratory pathology cultures. If symptoms persist or spread rapidly, consult your local Krishi Vigyan Kendra (KVK) or State Agricultural Extension Specialist."
}}
"""


async def diagnose_plant_with_google_ai(
    image_bytes: bytes,
    crop_hint: Optional[str] = None,
    user_symptoms: Optional[str] = None,
    location: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Executes the Google-Powered Plant Disease Identification & Grounded Diagnosis.
    Returns structured diagnosis dictionary.
    """
    # 1. Image decodability & format inspection
    try:
        with Image.open(io.BytesIO(image_bytes)) as pil_img:
            format_name = pil_img.format or "JPEG"
            mime_type = "image/png" if format_name.upper() == "PNG" else "image/webp" if format_name.upper() == "WEBP" else "image/jpeg"
            width, height = pil_img.width, pil_img.height
    except Exception as e:
        logger.warning(f"Invalid image format passed to Google AI: {e}")
        return {
            "status": "error",
            "is_plant": False,
            "error": "Uploaded image file could not be decoded. Please provide a valid JPEG, PNG, or WebP photograph.",
            "diagnosis": None,
            "sources": [],
        }

    # 2. Check SDK and API key availability
    if not GENAI_AVAILABLE:
        return {
            "status": "sdk_missing",
            "is_plant": None,
            "error": "The official 'google-genai' SDK is not installed on the server.",
            "diagnosis": None,
            "sources": [],
        }

    api_key = get_google_api_key()
    if not api_key:
        return {
            "status": "api_key_missing",
            "is_plant": None,
            "error": (
                "GOOGLE_API_KEY is not configured on the backend server. "
                "Please configure GOOGLE_API_KEY in backend/.env to activate Google-powered AI diagnosis."
            ),
            "diagnosis": None,
            "sources": [],
        }

    client = genai.Client(api_key=api_key)
    prompt_text = _build_diagnostic_prompt(crop_hint=crop_hint, user_symptoms=user_symptoms, location=location)

    image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)

    # 3. Model invocation with Grounding & Fallback
    grounding_sources: List[Dict[str, Any]] = []
    response_text = ""
    last_error: Optional[Exception] = None

    # Models to try: PRIMARY_MODEL followed by FALLBACK_MODELS
    candidate_models = [PRIMARY_MODEL] + [m for m in FALLBACK_MODELS if m != PRIMARY_MODEL]

    try_search = True
    for model_name in candidate_models:
        # First attempt: With Google Search grounding tool (if available)
        if try_search:
            try:
                logger.info(f"[GoogleAI] Requesting diagnosis with model '{model_name}' and Google Search grounding...")
                config_with_search = types.GenerateContentConfig(
                    temperature=0.2,
                    tools=[types.Tool(google_search=types.GoogleSearch())],
                )
                response = client.models.generate_content(
                    model=model_name,
                    contents=[prompt_text, image_part],
                    config=config_with_search,
                )

                response_text = response.text or ""

                # Extract Google Search Grounding Metadata if present
                if hasattr(response, "candidates") and response.candidates:
                    candidate = response.candidates[0]
                    grounding_meta = getattr(candidate, "grounding_metadata", None)
                    if grounding_meta:
                        chunks = getattr(grounding_meta, "grounding_chunks", []) or []
                        for chunk in chunks:
                            web = getattr(chunk, "web", None)
                            if web:
                                title = getattr(web, "title", None) or "Web Reference"
                                uri = getattr(web, "uri", None) or ""
                                if uri and not any(s.get("url") == uri for s in grounding_sources):
                                    grounding_sources.append({
                                        "title": title,
                                        "organization": "Google Search Grounding",
                                        "url": uri,
                                        "notes": "Retrieved via Google Search grounding verification."
                                    })

                if response_text:
                    break
            except Exception as e:
                err_msg = str(e).lower()
                logger.warning(f"[GoogleAI] Model '{model_name}' with Search grounding failed: {e}. Trying without search tool...")
                last_error = e
                if any(term in err_msg for term in ["429", "quota", "resource_exhausted", "not supported", "unsupported"]):
                    try_search = False

        # Attempt direct JSON generation
        try:
            config_direct = types.GenerateContentConfig(
                temperature=0.2,
                response_mime_type="application/json",
            )
            response = client.models.generate_content(
                model=model_name,
                contents=[prompt_text, image_part],
                config=config_direct,
            )
            response_text = response.text or ""
            if response_text:
                logger.info(f"[GoogleAI] Model '{model_name}' direct JSON generation succeeded.")
                break
        except Exception as e2:
            logger.warning(f"[GoogleAI] Model '{model_name}' direct generation failed: {e2}")
            last_error = e2

    if not response_text:
        err_str = str(last_error) if last_error else "Unknown error"
        if "api_key" in err_str.lower() or "400" in err_str or "403" in err_str or "unauthorized" in err_str.lower():
            return {
                "status": "api_key_invalid",
                "is_plant": None,
                "error": "The provided GOOGLE_API_KEY was rejected by Google AI. Please check your API key in backend/.env.",
                "diagnosis": None,
                "sources": [],
            }
        return {
            "status": "error",
            "is_plant": None,
            "error": f"Google AI diagnostic service temporarily unavailable: {err_str}",
            "diagnosis": None,
            "sources": [],
        }

    # 4. Parse JSON Response
    try:
        clean_text = _clean_json_text(response_text)
        data = json.loads(clean_text)
    except json.JSONDecodeError as e:
        logger.warning(f"[GoogleAI] JSON decode failure: {e}. Raw response: {response_text[:300]}")
        return {
            "status": "error",
            "is_plant": True,
            "error": "Failed to parse structured diagnostic report from Google AI.",
            "raw_text": response_text[:1000],
            "diagnosis": None,
            "sources": [],
        }

    # 5. Non-Plant Rejection Handling
    is_plant = data.get("is_plant", True)
    if not is_plant:
        rejection_reason = data.get("rejection_reason") or (
            "The uploaded photograph could not be identified as a plant leaf or crop specimen. "
            "Please upload a clear photograph of a plant or leaf."
        )
        return {
            "status": "not_a_plant",
            "is_plant": False,
            "rejection_reason": rejection_reason,
            "diagnosis": {
                "plant_identification": {
                    "common_name": "Not a Plant",
                    "scientific_name": None,
                    "certainty": "High",
                    "plant_part": "None"
                },
                "disease_assessment": {
                    "is_healthy": False,
                    "most_likely_disease": "Unidentified Subject (Not a Plant)",
                    "pathogen_scientific_name": None,
                    "cause": "unknown",
                    "confidence": "High",
                    "confidence_explanation": rejection_reason,
                    "symptoms_observed": ["Image does not exhibit botanical structure, foliage, or leaf venation."],
                    "plausibility_explanation": rejection_reason,
                    "differential_diagnosis": []
                },
                "disease_information": {
                    "typical_symptoms": "N/A",
                    "favorable_conditions": "N/A"
                },
                "treatment_and_management": {
                    "immediate_actions": ["Upload a clear photograph of a plant leaf or foliage."],
                    "cultural_practices": [],
                    "biological_control": [],
                    "chemical_management": [],
                    "safety_precautions": "N/A",
                    "preventive_measures": []
                },
                "uncertainty_disclaimer": "The system only diagnoses agricultural crops and plants."
            },
            "sources": [],
        }

    # 6. Quality & Insufficient Evidence Handling
    image_quality = data.get("image_quality", "good")
    is_insufficient = image_quality == "poor_blurry_or_dark"

    # Merge model sources with Google Search grounding sources
    model_sources = data.get("sources") or []
    all_sources = list(model_sources)
    for gs in grounding_sources:
        if not any(s.get("url") == gs.get("url") for s in all_sources):
            all_sources.append(gs)

    # 7. Supplement with authoritative institutional academic monographs from web_research
    plant_info = data.get("plant_identification", {})
    disease_info = data.get("disease_assessment", {})
    crop_name = plant_info.get("common_name") or crop_hint or ""
    pathogen = disease_info.get("pathogen_scientific_name") or disease_info.get("most_likely_disease") or ""

    try:
        institutional_research = await search_agricultural_research(crop=crop_name, condition=pathogen)
        for pub in institutional_research:
            if not any(s.get("url") == pub.get("url") for s in all_sources):
                all_sources.append({
                    "title": pub.get("title"),
                    "organization": pub.get("journal") or pub.get("source_type") or "Agricultural Research Repository",
                    "url": pub.get("url") or f"https://doi.org/{pub.get('doi')}",
                    "notes": pub.get("relevance") or "Peer-reviewed agricultural pathology reference."
                })
    except Exception as e:
        logger.debug(f"[GoogleAI] Fallback research query error: {e}")

    # Ensure all sources have required fields
    clean_sources = []
    for s in all_sources:
        if isinstance(s, dict) and s.get("title"):
            clean_sources.append({
                "title": s.get("title"),
                "organization": s.get("organization") or "Agricultural Extension",
                "url": s.get("url") or "https://icar.org.in/",
                "notes": s.get("notes") or s.get("relevance") or "Authoritative crop protection reference."
            })

    # Return structured diagnosis
    return {
        "status": "insufficient_evidence" if is_insufficient else "success",
        "is_plant": True,
        "image_quality": image_quality,
        "diagnosis": {
            "plant_identification": data.get("plant_identification", {}),
            "disease_assessment": data.get("disease_assessment", {}),
            "disease_information": data.get("disease_information", {}),
            "treatment_and_management": data.get("treatment_and_management", {}),
            "uncertainty_disclaimer": data.get(
                "uncertainty_disclaimer",
                "Visual AI diagnosis provides an indicative assessment. For critical crop decisions, contact your local Krishi Vigyan Kendra (KVK) or plant pathology specialist."
            )
        },
        "sources": clean_sources,
        "model_used": model_name,
    }
