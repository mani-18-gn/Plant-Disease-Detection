import logging
import json
import httpx
from backend.config import settings
from backend.agents.advisory.prompts import ADVISORY_SYSTEM_PROMPT, build_advisory_prompt
from backend.agents.advisory.rule_based_fallback import generate_rule_based_advisory

logger = logging.getLogger(__name__)

GEMINI_MODEL = "gemini-flash-latest"
GEMINI_BASE_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"


def generate_gemini_advisory(context_dict: dict) -> dict:
    """
    Calls Google Gemini API with structured JSON output configuration.
    If API key is missing, network fails, or response is malformed,
    gracefully falls back to the deterministic rule_based_fallback model.
    """
    api_key = settings.GEMINI_API_KEY.strip()

    if api_key:
        prompt_text = build_advisory_prompt(context_dict)
        url = f"{GEMINI_BASE_URL}?key={api_key}"

        payload = {
            "system_instruction": {
                "parts": [{"text": ADVISORY_SYSTEM_PROMPT}]
            },
            "contents": [
                {"parts": [{"text": prompt_text}]}
            ],
            "generationConfig": {
                "response_mime_type": "application/json",
                "temperature": 0.2,
            }
        }
        headers = {"Content-Type": "application/json"}

        try:
            with httpx.Client(timeout=8.0) as client:
                resp = client.post(url, json=payload, headers=headers)
                if resp.status_code == 200:
                    res_json = resp.json()
                    candidates = res_json.get("candidates", [])
                    if candidates:
                        raw_text = candidates[0]["content"]["parts"][0]["text"]
                        try:
                            parsed = json.loads(raw_text)
                            priority = parsed.get("priority", "medium").lower()
                            message = parsed.get("message", "")
                            actions = parsed.get("recommended_actions", [])

                            if priority in ["urgent", "high", "medium", "low"] and message and isinstance(actions, list):
                                disclaimer = parsed.get(
                                    "disclaimer",
                                    "Chemical and dosage recommendations follow standard ICAR-CPCRI guidelines. "
                                    "Farmers are advised to consult their local Agricultural Extension Officer (RSK / KVK) before applying any chemical treatment."
                                )
                                return {
                                    "priority": priority,
                                    "message": message,
                                    "recommended_actions": actions,
                                    "reasoning_summary": parsed.get("reasoning_summary", ""),
                                    "disclaimer": disclaimer,
                                    "generated_by": "gemini",
                                }
                            else:
                                logger.warning("Gemini JSON response missing required fields. Falling back to rules.")
                        except json.JSONDecodeError as jde:
                            logger.warning(f"Failed to decode Gemini JSON response: {jde}. Raw: {raw_text[:200]}")
                else:
                    logger.warning(f"Gemini API returned status {resp.status_code}: {resp.text[:200]}")
        except Exception as e:
            logger.warning(f"Gemini API connection error: {e}")

    # Fallback to deterministic rule-based priority matrix
    logger.info("Executing rule_based_fallback for Advisory generation.")
    fallback_result = generate_rule_based_advisory(context_dict)
    fallback_result["generated_by"] = "rule_fallback"
    return fallback_result
