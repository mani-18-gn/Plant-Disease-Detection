"""
Curated Visual Similarity & Prototype Gallery Service (Stage B & Stage D).

Compares uploaded plant photographs against a curated collection of labeled
plant disease reference specimens using penultimate MobileNetV2 (1280-d) embeddings.

CRITICAL PRINCIPLES:
- Treats visual similarity as supporting evidence, never as uncalibrated certainty.
- Detects out-of-distribution plantation crops (e.g. Arecanut palms, Coconut)
  by comparing query embeddings to reference palm prototypes.
- Prevents cross-species misclassification (such as misdiagnosing palm fronds as strawberry leaf scorch).
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from PIL import Image
import numpy as np
import torch
import torch.nn.functional as F

logger = logging.getLogger(__name__)

SAMPLE_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "test_labeled_samples"

# Curated reference prototypes metadata
REFERENCE_METADATA: Dict[str, Dict[str, Any]] = {
    "Arecanut_Palm_Leaf_Field.webp": {
        "crop": "Arecanut",
        "crop_kn": "ಅಡಿಕೆ",
        "condition": "Arecanut Palm Frond",
        "condition_kn": "ಅಡಿಕೆ ಮರದ ಗರಿ",
        "is_healthy": False,
        "plant_family": "Arecaceae (Palm)",
        "is_monocot": True,
        "title": "Arecanut Palm Leaf (Karnataka Plantation Benchmark)",
    },
    "Tomato___Early_blight___0012b9d2-2130-4a06-a834-b1f3af34f57e___RS_Erly.B 8389.JPG": {
        "crop": "Tomato",
        "crop_kn": "ಟೊಮ್ಯಾಟೊ",
        "condition": "Early Blight",
        "condition_kn": "ಮುಂಗಾರು ಅಂಗಮಾರಿ",
        "is_healthy": False,
        "plant_family": "Solanaceae",
        "is_monocot": False,
        "title": "Tomato Early Blight (Alternaria solani concentric rings)",
    },
    "Tomato___Late_blight___0003faa8-4b27-4c65-bf42-6d9e352ca1a5___RS_Late.B 4946.JPG": {
        "crop": "Tomato",
        "crop_kn": "ಟೊಮ್ಯಾಟೊ",
        "condition": "Late Blight",
        "condition_kn": "ಹಿಂಗಾರು ಅಂಗಮಾರಿ",
        "is_healthy": False,
        "plant_family": "Solanaceae",
        "is_monocot": False,
        "title": "Tomato Late Blight (Phytophthora infestans water-soaked lesion)",
    },
    "Tomato___healthy___000146ff-92a4-4db6-90ad-8fce2ae4fddd___GH_HL Leaf 259.1.JPG": {
        "crop": "Tomato",
        "crop_kn": "ಟೊಮ್ಯಾಟೊ",
        "condition": "Healthy",
        "condition_kn": "ಆರೋಗ್ಯಕರ",
        "is_healthy": True,
        "plant_family": "Solanaceae",
        "is_monocot": False,
        "title": "Tomato Healthy Foliage",
    },
    "Potato___Early_blight___001187a0-57ab-4329-baff-e7246a9edeb0___RS_Early.B 8178.JPG": {
        "crop": "Potato",
        "crop_kn": "ಆಲೂಗಡ್ಡೆ",
        "condition": "Early Blight",
        "condition_kn": "ಮುಂಗಾರು ಅಂಗಮಾರಿ",
        "is_healthy": False,
        "plant_family": "Solanaceae",
        "is_monocot": False,
        "title": "Potato Early Blight",
    },
    "Potato___Late_blight___0051e5e8-d1c4-4a84-bf3a-a426cdad6285___RS_LB 4640.JPG": {
        "crop": "Potato",
        "crop_kn": "ಆಲೂಗಡ್ಡೆ",
        "condition": "Late Blight",
        "condition_kn": "ಹಿಂಗಾರು ಅಂಗಮಾರಿ",
        "is_healthy": False,
        "plant_family": "Solanaceae",
        "is_monocot": False,
        "title": "Potato Late Blight",
    },
    "Potato___healthy___00fc2ee5-729f-4757-8aeb-65c3355874f2___RS_HL 1864.JPG": {
        "crop": "Potato",
        "crop_kn": "ಆಲೂಗಡ್ಡೆ",
        "condition": "Healthy",
        "condition_kn": "ಆರೋಗ್ಯಕರ",
        "is_healthy": True,
        "plant_family": "Solanaceae",
        "is_monocot": False,
        "title": "Potato Healthy Leaf",
    },
    "Corn_Common_Rust.jpg": {
        "crop": "Corn (Maize)",
        "crop_kn": "ಮೆಕ್ಕೆಜೋಳ",
        "condition": "Common Rust",
        "condition_kn": "ಸಾಮಾನ್ಯ ತುಕ್ಕು ರೋಗ",
        "is_healthy": False,
        "plant_family": "Poaceae",
        "is_monocot": True,
        "title": "Corn Common Rust (Puccinia sorghi pustules)",
    },
    "Grape___Black_rot___00090b0f-c140-4e77-8d20-d39f67b75fcc___FAM_B.Rot 0376.JPG": {
        "crop": "Grape",
        "crop_kn": "ದ್ರಾಕ್ಷಿ",
        "condition": "Black Rot",
        "condition_kn": "ಕಪ್ಪು ಕೊಳೆ ರೋಗ",
        "is_healthy": False,
        "plant_family": "Vitaceae",
        "is_monocot": False,
        "title": "Grape Black Rot",
    },
    "Apple___Apple_scab___00075aa8-d81a-4184-8541-b692b78d398a___FREC_Scab 3335.JPG": {
        "crop": "Apple",
        "crop_kn": "ಸೇಬು",
        "condition": "Apple Scab",
        "condition_kn": "ಸ್ಕ್ಯಾಬ್ ರೋಗ",
        "is_healthy": False,
        "plant_family": "Rosaceae",
        "is_monocot": False,
        "title": "Apple Scab (Venturia inaequalis)",
    },
    "Apple___healthy___0055dd26-23a7-4415-ac61-e0b44ebfaf80___RS_HL 5672.JPG": {
        "crop": "Apple",
        "crop_kn": "ಸೇಬು",
        "condition": "Healthy",
        "condition_kn": "ಆರೋಗ್ಯಕರ",
        "is_healthy": True,
        "plant_family": "Rosaceae",
        "is_monocot": False,
        "title": "Apple Healthy Foliage",
    },
}

_PROTOTYPE_CACHE: Dict[str, torch.Tensor] = {}


CACHE_FILE = SAMPLE_DIR / "prototypes_cache.pt"


def extract_image_embedding(model: Any, processor: Any, image: Image.Image) -> torch.Tensor:
    """Extract 1280-d normalized visual feature embedding from MobileNetV2 penultimate layer."""
    inputs = processor(images=image.convert("RGB"), return_tensors="pt")
    with torch.no_grad():
        features = model.mobilenet_v2(**inputs).pooler_output.squeeze()
        normalized = F.normalize(features, dim=0)
    return normalized


def warm_prototype_embeddings(model: Any = None, processor: Any = None) -> None:
    """Precompute and cache reference prototype embeddings for instantaneous similarity lookup."""
    global _PROTOTYPE_CACHE
    if len(_PROTOTYPE_CACHE) >= len(REFERENCE_METADATA):
        return

    # Try loading from persisted disk cache first
    if CACHE_FILE.exists():
        try:
            loaded = torch.load(CACHE_FILE, map_location="cpu", weights_only=True)
            if isinstance(loaded, dict) and len(loaded) > 0:
                _PROTOTYPE_CACHE.update(loaded)
                logger.info(f"Loaded {len(_PROTOTYPE_CACHE)} prototype embeddings from disk cache.")
                return
        except Exception as e:
            logger.warning(f"Could not load prototype cache from disk: {e}")

    # Compute dynamically if model and processor available
    if model is not None and processor is not None:
        for filename, meta in REFERENCE_METADATA.items():
            if filename in _PROTOTYPE_CACHE:
                continue
            file_path = SAMPLE_DIR / filename
            if file_path.exists():
                try:
                    img = Image.open(file_path).convert("RGB")
                    emb = extract_image_embedding(model, processor, img)
                    _PROTOTYPE_CACHE[filename] = emb.cpu()
                except Exception as e:
                    logger.warning(f"Failed to extract prototype embedding for {filename}: {e}")

        # Persist to disk for instantaneous future reloads
        if _PROTOTYPE_CACHE:
            try:
                SAMPLE_DIR.mkdir(parents=True, exist_ok=True)
                torch.save(_PROTOTYPE_CACHE, CACHE_FILE)
                logger.info(f"Persisted {len(_PROTOTYPE_CACHE)} prototype embeddings to {CACHE_FILE}.")
            except Exception as e:
                logger.warning(f"Failed to persist prototype cache: {e}")


def find_similar_reference_samples(
    query_embedding: torch.Tensor,
    top_k: int = 3,
    model: Any = None,
    processor: Any = None,
) -> List[Dict[str, Any]]:
    """
    Stage D: Compare query embedding against curated benchmark prototypes using cosine similarity.
    Returns ranked list of visually similar reference samples.
    """
    if not _PROTOTYPE_CACHE:
        warm_prototype_embeddings(model, processor)

    if not _PROTOTYPE_CACHE:
        return []

    ranked = []
    for filename, ref_emb in _PROTOTYPE_CACHE.items():
        sim = float(torch.dot(query_embedding.cpu(), ref_emb.cpu()).item())
        meta = REFERENCE_METADATA.get(filename, {})
        ranked.append({
            "filename": filename,
            "crop": meta.get("crop", "Unknown"),
            "crop_kn": meta.get("crop_kn"),
            "condition": meta.get("condition", "Unknown"),
            "condition_kn": meta.get("condition_kn"),
            "similarity_score": round(max(0.0, min(1.0, sim)), 4),
            "similarity_pct": round(max(0.0, min(1.0, sim)) * 100, 1),
            "title": meta.get("title", filename),
            "plant_family": meta.get("plant_family"),
            "is_monocot": meta.get("is_monocot", False),
        })

    ranked.sort(key=lambda x: x["similarity_score"], reverse=True)
    return ranked[:top_k]


def analyze_plant_species_and_compatibility(
    query_embedding: torch.Tensor,
    image: Image.Image,
    predicted_38_crop: str,
    block_crop: Optional[str] = None,
    model: Any = None,
    processor: Any = None,
) -> Dict[str, Any]:
    """
    Stage B: Determine likely plant species, detect out-of-distribution monocot/palm specimens,
    and verify crop compatibility BEFORE final diagnosis.
    """
    if not _PROTOTYPE_CACHE:
        warm_prototype_embeddings(model, processor)

    areca_ref_emb = _PROTOTYPE_CACHE.get("Arecanut_Palm_Leaf_Field.webp")
    areca_similarity = 0.0
    if areca_ref_emb is not None:
        areca_similarity = float(torch.dot(query_embedding.cpu(), areca_ref_emb.cpu()).item())

    # Check for palm morphology: elongated parallel venation / striations
    # Monocot palm fronds have parallel linear venation
    is_palm_morphology = False
    try:
        gray = np.array(image.convert("L").resize((128, 128)), dtype=float)
        # Compute horizontal vs vertical Sobel gradient energy
        sobel_x = np.abs(gray[:, 1:] - gray[:, :-1])
        sobel_y = np.abs(gray[1:, :] - gray[:-1, :])
        energy_ratio = float(np.mean(sobel_x) / (np.mean(sobel_y) + 1e-5))
        # High directional bias (> 1.4 or < 0.7) characteristic of parallel frond leaflets
        if (energy_ratio > 1.35 or energy_ratio < 0.72) and areca_similarity > 0.45:
            is_palm_morphology = True
    except Exception:
        pass

    # Check explicit block_crop hint
    is_explicit_areca = False
    if block_crop:
        b_clean = block_crop.lower().strip()
        is_explicit_areca = any(term in b_clean for term in ["areca", "adike", "supari", "ಅಡಿಕೆ", "palm"])

    # High-confidence detection of Arecanut / Palm family
    # Case 1: Explicit arecanut block requested
    # Case 2: Visual similarity to arecanut prototype >= 0.65
    # Case 3: MobileNet predicted "Strawberry" (classic closed-set artifact) but areca_similarity > 0.48 or palm morphology
    is_arecanut_palm = (
        is_explicit_areca
        or areca_similarity >= 0.65
        or (predicted_38_crop == "Strawberry" and (areca_similarity >= 0.48 or is_palm_morphology))
    )

    if is_arecanut_palm:
        return {
            "identified_crop": "Arecanut",
            "identified_crop_kn": "ಅಡಿಕೆ",
            "scientific_name": "Areca catechu L.",
            "plant_family": "Arecaceae (Palm)",
            "is_supported_by_vision_model": False,
            "crop_support_status": "plantation_monograph_supported",
            "is_arecanut_palm": True,
            "areca_similarity": round(areca_similarity, 4),
            "identification_rationale": (
                f"Visual embedding similarity ({round(areca_similarity * 100, 1)}%) and monocot frond morphology "
                "align with Arecanut Palm (Areca catechu L.). Closed-set 38-class PlantVillage model does not contain "
                "palm frond training weights; routed to verified ICAR-CPCRI plantation monograph."
            ),
        }

    # If not arecanut, verify whether the predicted crop belongs to supported 38-class benchmark
    supported_crops = {
        "Apple", "Blueberry", "Cherry", "Corn (maize)", "Corn (Maize)", "Grape",
        "Orange", "Peach", "Pepper, bell", "Potato", "Raspberry", "Soybean", "Squash", "Strawberry", "Tomato"
    }

    is_supported = any(c.lower() in predicted_38_crop.lower() for c in supported_crops)

    return {
        "identified_crop": predicted_38_crop,
        "identified_crop_kn": None,
        "scientific_name": None,
        "plant_family": None,
        "is_supported_by_vision_model": is_supported,
        "crop_support_status": "supported" if is_supported else "unsupported_crop",
        "is_arecanut_palm": False,
        "areca_similarity": round(areca_similarity, 4),
        "identification_rationale": (
            f"Foliage characteristics match {predicted_38_crop} within the supported multi-crop vision library."
            if is_supported else f"Crop '{predicted_38_crop}' is outside the 38-class benchmark library."
        ),
    }
