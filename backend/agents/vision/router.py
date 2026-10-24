import asyncio
import io
import uuid
import logging
from pathlib import Path
from typing import Optional, List
from PIL import Image, UnidentifiedImageError
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Query, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.config import settings
from backend.db.session import get_db
from backend.db.models.core.user import User
from backend.db.models.core.crop_block import CropBlock
from backend.db.models.agronomy.disease_detection import DiseaseDetection
from datetime import datetime, timezone
from backend.auth.jwt_handler import get_current_user, get_current_user_optional
from backend.schemas.disease import DiseaseDetectionResponse
from backend.core.router import _verify_crop_block_ownership
from backend.agents.vision.inference import (
    run_vision_inference,
    ModelNotAvailableError,
    get_multicrop_model,
)
from backend.agents.vision.advisory_db import (
    CLASS_METADATA,
    get_diagnosis_advisory,
    search_knowledge_base,
    get_all_supported_crops,
)
from backend.agents.vision.web_research import search_agricultural_research

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agents/vision", tags=["Vision Agent"])

UPLOADS_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "uploads"
SAMPLE_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "test_labeled_samples"
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp", "image/jpg"}


@router.get("/status")
def vision_status():
    """Returns the operational status, loaded weights, and supported crops of the Vision Agent."""
    model, processor = get_multicrop_model()
    is_ready = model is not None and processor is not None

    crops = set()
    conditions = []
    for meta in CLASS_METADATA.values():
        crops.add(meta["crop"])
        conditions.append({
            "crop": meta["crop"],
            "crop_kn": meta.get("crop_kn"),
            "condition": meta["condition"],
            "condition_kn": meta.get("condition_kn"),
            "is_healthy": meta["is_healthy"],
        })

    return {
        "status": "ready" if is_ready else "weights_missing",
        "backend": settings.VISION_BACKEND,
        "model_architecture": "MobileNetV2 fine-tuned on PlantVillage",
        "total_supported_classes": len(CLASS_METADATA),
        "supported_crops": sorted(list(crops)),
        "conditions": conditions,
    }


@router.get("/knowledge-base")
def get_knowledge_base(
    query: Optional[str] = Query(None, description="Search query across crops, symptoms, pathogens"),
    crop: Optional[str] = Query(None, description="Filter by crop name (English or Kannada)"),
    lang: str = Query("en", description="Language preference ('en' or 'kn')"),
):
    """
    Search and browse the verified agricultural pathology knowledge base.
    Covers all 38 vision classes plus extended Indian plantation/staple crops.
    """
    results = search_knowledge_base(query=query, crop=crop, lang=lang)
    return {
        "total_results": len(results),
        "query": query,
        "crop_filter": crop,
        "results": results,
    }


@router.get("/knowledge-base/crops")
def get_knowledge_base_crops():
    """Returns catalog of all supported crops with disease counts and metadata."""
    return get_all_supported_crops()


@router.get("/knowledge-base/{raw_key}")
def get_knowledge_base_detail(raw_key: str):
    """Retrieve detailed monograph for a specific condition or raw class label."""
    advisory = get_diagnosis_advisory(raw_label=raw_key)
    return advisory


@router.get("/sample-images")
def get_sample_images():
    """
    Provides real benchmark labeled test images for evaluators to test genuine inference instantly.
    """
    if not SAMPLE_DIR.exists():
        return []

    samples: list[dict[str, object]] = [
        {
            "filename": "Tomato___Early_blight___0012b9d2-2130-4a06-a834-b1f3af34f57e___RS_Erly.B 8389.JPG",
            "title": "Tomato Early Blight",
            "title_kn": "ಟೊಮ್ಯಾಟೊ ಮುಂಗಾರು ಅಂಗಮಾರಿ",
            "crop": "Tomato",
            "condition": "Early Blight",
            "badge": "Fungal Infection",
        },
        {
            "filename": "Tomato___Late_blight___0003faa8-4b27-4c65-bf42-6d9e352ca1a5___RS_Late.B 4946.JPG",
            "title": "Tomato Late Blight",
            "title_kn": "ಟೊಮ್ಯಾಟೊ ಹಿಂಗಾರು ಅಂಗಮಾರಿ",
            "crop": "Tomato",
            "condition": "Late Blight",
            "badge": "Oomycete Rot",
        },
        {
            "filename": "Tomato___healthy___000146ff-92a4-4db6-90ad-8fce2ae4fddd___GH_HL Leaf 259.1.JPG",
            "title": "Tomato Healthy Leaf",
            "title_kn": "ಟೊಮ್ಯಾಟೊ ಆರೋಗ್ಯಕರ ಎಲೆ",
            "crop": "Tomato",
            "condition": "Healthy",
            "badge": "Healthy",
        },
        {
            "filename": "Potato___Early_blight___001187a0-57ab-4329-baff-e7246a9edeb0___RS_Early.B 8178.JPG",
            "title": "Potato Early Blight",
            "title_kn": "ಆಲೂಗಡ್ಡೆ ಮುಂಗಾರು ಅಂಗಮಾರಿ",
            "crop": "Potato",
            "condition": "Early Blight",
            "badge": "Bullseye Rings",
        },
        {
            "filename": "Potato___Late_blight___0051e5e8-d1c4-4a84-bf3a-a426cdad6285___RS_LB 4640.JPG",
            "title": "Potato Late Blight",
            "title_kn": "ಆಲೂಗಡ್ಡೆ ಹಿಂಗಾರು ಅಂಗಮಾರಿ",
            "crop": "Potato",
            "condition": "Late Blight",
            "badge": "Severe Blight",
        },
        {
            "filename": "Potato___healthy___00fc2ee5-729f-4757-8aeb-65c3355874f2___RS_HL 1864.JPG",
            "title": "Potato Healthy",
            "title_kn": "ಆಲೂಗಡ್ಡೆ ಆರೋಗ್ಯಕರ",
            "crop": "Potato",
            "condition": "Healthy",
            "badge": "Healthy",
        },
        {
            "filename": "Corn_Common_Rust.jpg",
            "title": "Corn (Maize) Common Rust",
            "title_kn": "ಮೆಕ್ಕೆಜೋಳ ಸಾಮಾನ್ಯ ತುಕ್ಕು ರೋಗ",
            "crop": "Corn (Maize)",
            "condition": "Common Rust",
            "badge": "Rust Pustules",
        },
        {
            "filename": "Grape___Black_rot___00090b0f-c140-4e77-8d20-d39f67b75fcc___FAM_B.Rot 0376.JPG",
            "title": "Grape Black Rot",
            "title_kn": "ದ್ರಾಕ್ಷಿ ಕಪ್ಪು ಕೊಳೆ ರೋಗ",
            "crop": "Grape",
            "condition": "Black Rot",
            "badge": "Pycnidial Rot",
        },
        {
            "filename": "Apple___Apple_scab___00075aa8-d81a-4184-8541-b692b78d398a___FREC_Scab 3335.JPG",
            "title": "Apple Apple Scab",
            "title_kn": "ಸೇಬು ಸ್ಕ್ಯಾಬ್ ರೋಗ",
            "crop": "Apple",
            "condition": "Apple Scab",
            "badge": "Olive Scab",
        },
        {
            "filename": "Apple___healthy___0055dd26-23a7-4415-ac61-e0b44ebfaf80___RS_HL 5672.JPG",
            "title": "Apple Healthy",
            "title_kn": "ಸೇಬು ಆರೋಗ್ಯಕರ",
            "crop": "Apple",
            "condition": "Healthy",
            "badge": "Healthy",
        },
        {
            "filename": "PlantDoc_Tomato_Early_Blight_Field.jpg",
            "title": "Tomato Early Blight (PlantDoc Real Field)",
            "title_kn": "ಟೊಮ್ಯಾಟೊ ಮುಂಗಾರು ಅಂಗಮಾರಿ (ನೈಜ ಹೊಲದ ಫೋಟೋ)",
            "crop": "Tomato",
            "condition": "Early Blight",
            "badge": "PlantDoc In-Field",
        },
        {
            "filename": "PlantDoc_Corn_Leaf_Blight_Field.jpg",
            "title": "Corn Northern Leaf Blight (PlantDoc Real Field)",
            "title_kn": "ಮೆಕ್ಕೆಜೋಳ ಉತ್ತರ ಎಲೆ ಅಂಗಮಾರಿ (ನೈಜ ಹೊಲದ ಫೋಟೋ)",
            "crop": "Corn (Maize)",
            "condition": "Northern Leaf Blight",
            "badge": "PlantDoc In-Field",
        },
        {
            "filename": "PlantDoc_Apple_Scab_Field.jpg",
            "title": "Apple Scab (PlantDoc Real Field)",
            "title_kn": "ಸೇಬು ಸ್ಕ್ಯಾಬ್ ರೋಗ (ನೈಜ ಹೊಲದ ಫೋಟೋ)",
            "crop": "Apple",
            "condition": "Apple Scab",
            "badge": "PlantDoc In-Field",
        },
        {
            "filename": "PlantDoc_Potato_Early_Blight_Field.jpg",
            "title": "Potato Early Blight (PlantDoc Real Field)",
            "title_kn": "ಆಲೂಗಡ್ಡೆ ಮುಂಗಾರು ಅಂಗಮಾರಿ (ನೈಜ ಹೊಲದ ಫೋಟೋ)",
            "crop": "Potato",
            "condition": "Early Blight",
            "badge": "PlantDoc In-Field",
        },
        {
            "filename": "PlantDoc_Bell_Pepper_Bacterial_Spot_Field.jpg",
            "title": "Pepper Bell Bacterial Spot (PlantDoc Real Field)",
            "title_kn": "ದಪ್ಪ ಮೆಣಸಿನಕಾಯಿ ಬ್ಯಾಕ್ಟೀರಿಯಾ ಚುಕ್ಕೆ ರೋಗ (ನೈಜ ಹೊಲದ ಫೋಟೋ)",
            "crop": "Pepper (Bell)",
            "condition": "Bacterial Spot",
            "badge": "PlantDoc In-Field",
        },
        {
            "filename": "PlantDoc_Grape_Black_Rot_Field.jpg",
            "title": "Grape Black Rot (PlantDoc Real Field)",
            "title_kn": "ದ್ರಾಕ್ಷಿ ಕಪ್ಪು ಕೊಳೆ ರೋಗ (ನೈಜ ಹೊಲದ ಫೋಟೋ)",
            "crop": "Grape",
            "condition": "Black Rot",
            "badge": "PlantDoc In-Field",
        },
        {
            "filename": "Arecanut_Palm_Leaf_Field.webp",
            "title": "Arecanut Palm Leaf (Out-of-Distribution Demo)",
            "title_kn": "ಅಡಿಕೆ ಮರದ ಗರಿ (ಮಾದರಿ ವ್ಯಾಪ್ತಿ ಪರೀಕ್ಷೆ)",
            "crop": "Arecanut",
            "condition": "Out-of-Distribution (ICAR-CPCRI Monograph)",
            "badge": "Arecanut Palm",
        },
    ]

    available = []
    for item in samples:
        filename_str = str(item["filename"])
        fpath = SAMPLE_DIR / filename_str
        if fpath.exists():
            item["download_url"] = f"/agents/vision/sample-image-file/{filename_str}"
            item["size_bytes"] = fpath.stat().st_size
            available.append(item)

    return available


@router.get("/sample-image-file/{filename}")
def get_sample_image_file(filename: str):
    """Serves raw bytes of benchmark sample images for previewing."""
    clean_filename = Path(filename).name
    fpath = SAMPLE_DIR / clean_filename
    if not fpath.exists():
        raise HTTPException(status_code=404, detail="Sample image not found.")
    return FileResponse(str(fpath), media_type="image/jpeg")


@router.get("/history/{crop_block_id}", response_model=List[DiseaseDetectionResponse])
def get_diagnosis_history(
    crop_block_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Fetch past diagnosis history for an authenticated farmer's crop block."""
    _verify_crop_block_ownership(db, str(crop_block_id), str(current_user.id))

    records = (
        db.query(DiseaseDetection)
        .filter(DiseaseDetection.crop_block_id == str(crop_block_id))
        .order_by(DiseaseDetection.detected_at.desc())
        .limit(25)
        .all()
    )

    results = []
    for r in records:
        advisory = get_diagnosis_advisory(raw_label=r.predicted_disease)
        results.append(
            DiseaseDetectionResponse(
                id=uuid.UUID(str(r.id)),
                crop_block_id=uuid.UUID(str(r.crop_block_id)),
                image_path=r.image_path,
                predicted_disease=r.predicted_disease,
                cnn_confidence=float(r.cnn_confidence),
                posterior_probability=float(r.posterior_probability) if r.posterior_probability is not None else None,
                validated=r.validated,
                detected_at=r.detected_at,
                crop=advisory.get("crop"),
                crop_kn=advisory.get("crop_kn"),
                scientific_name=advisory.get("scientific_name"),
                condition=advisory.get("condition"),
                condition_kn=advisory.get("condition_kn"),
                affected_parts=advisory.get("affected_parts"),
                is_healthy=advisory.get("is_healthy", False),
                is_inconclusive=r.predicted_disease == "Inconclusive" or "inconclusive" in r.predicted_disease.lower(),
                causal_agent=advisory.get("causal_agent"),
                symptoms=advisory.get("symptoms"),
                symptoms_kn=advisory.get("symptoms_kn"),
                differential_diagnosis=advisory.get("differential_diagnosis"),
                differential_diagnosis_kn=advisory.get("differential_diagnosis_kn"),
                favorable_conditions=advisory.get("favorable_conditions"),
                favorable_conditions_kn=advisory.get("favorable_conditions_kn"),
                preventive_practices=advisory.get("preventive_practices"),
                preventive_practices_kn=advisory.get("preventive_practices_kn"),
                cultural_biological_management=advisory.get("cultural_biological_management"),
                cultural_biological_management_kn=advisory.get("cultural_biological_management_kn"),
                chemical_management=advisory.get("chemical_management"),
                chemical_management_kn=advisory.get("chemical_management_kn"),
                expert_warning=advisory.get("expert_warning"),
                expert_warning_kn=advisory.get("expert_warning_kn"),
                management=advisory.get("chemical_management") or advisory.get("cultural_biological_management") or advisory.get("preventive_practices"),
                management_kn=advisory.get("chemical_management_kn") or advisory.get("cultural_biological_management_kn") or advisory.get("preventive_practices_kn"),
                sources=advisory.get("sources", []),
            )
        )
    return results


@router.post("/detect", response_model=DiseaseDetectionResponse, status_code=status.HTTP_201_CREATED)
async def detect_disease(
    file: UploadFile = File(...),
    crop_block_id: Optional[uuid.UUID] = Form(None),
    crop_type: Optional[str] = Form(None),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """
    PlantGuard Universal Plant Disease Vision Agent Endpoint:
    1. If crop_block_id is provided: verifies farmer ownership and loads block context.
    2. If no crop_block_id is provided: executes in Preview / Demo Mode without DB mutation.
    3. Validates image payload (type, size, uncorrupted pixels).
    4. Executes the 8-stage safe diagnosis pipeline (foliage plausibility, species consistency,
       MobileNetV2 inference, uncertainty thresholding, verified agronomic retrieval).
    5. Persists diagnosis history only when linked to an authorized crop block.
    6. Returns enriched bilingual diagnosis, differential diagnosis, and IPM management.
    """
    block_crop = crop_type

    # 1. Ownership verification (when linking to a specific crop block)
    if crop_block_id is not None:
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required to link diagnosis with an authorized crop block.",
            )
        _verify_crop_block_ownership(db, str(crop_block_id), str(current_user.id))

        block = db.query(CropBlock).filter(CropBlock.id == str(crop_block_id)).first()
        if block:
            block_crop = block.block_name
            if block.variety:
                block_crop = f"{block.block_name} ({block.variety})"

    # 2. File validation
    if file.content_type and file.content_type.lower() not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported image type '{file.content_type}'. Please upload JPEG, PNG, or WebP format.",
        )

    image_bytes = await file.read()
    if not image_bytes or len(image_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    max_size = getattr(settings, "MAX_UPLOAD_IMAGE_SIZE_BYTES", 15 * 1024 * 1024)
    if len(image_bytes) > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Uploaded file exceeds maximum limit of {max_size // (1024 * 1024)} MB.",
        )

    # 3. Verify image decodability
    try:
        with Image.open(io.BytesIO(image_bytes)) as img:
            img.verify()
    except (UnidentifiedImageError, Exception) as e:
        logger.warning(f"Corrupted or invalid image upload rejected: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Corrupted or unreadable image file. Please upload a valid photograph.",
        )

    # 4. Run real inference in async worker thread
    try:
        inference_result = await asyncio.to_thread(
            run_vision_inference,
            image_bytes,
            block_crop=block_crop
        )
    except ModelNotAvailableError as e:
        logger.error(f"Vision model unavailable: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Inference error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image inference error: {str(e)}",
        )

    # Corroborate with live backend-only peer-reviewed research (CrossRef / OpenAlex / ICAR)
    if inference_result.get("is_plant"):
        try:
            target_crop = inference_result.get("crop") or block_crop
            target_condition = inference_result.get("condition") or "disease management"
            if target_crop and "unrecognized" in target_crop.lower() and block_crop:
                target_crop = block_crop
            if not target_crop or "unrecognized" in target_crop.lower():
                top_preds = inference_result.get("top_predictions", [])
                if top_preds and top_preds[0].get("crop"):
                    target_crop = top_preds[0]["crop"]
                    target_condition = top_preds[0].get("condition", "disease management")

            if target_crop and "unrecognized" not in target_crop.lower():
                live_research = await search_agricultural_research(
                    crop=target_crop,
                    condition=target_condition,
                    scientific_name=inference_result.get("scientific_name"),
                    causal_agent=inference_result.get("causal_agent"),
                )
                if live_research:
                    inference_result["online_research"] = live_research
        except Exception as e:
            logger.warning(f"Online agricultural research fetch error: {e}")

    # 5. Save uploaded image to persistent directory
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    extension = Path(file.filename or "image.jpg").suffix or ".jpg"
    unique_filename = f"{uuid.uuid4()}{extension}"
    saved_path = UPLOADS_DIR / unique_filename

    try:
        with open(saved_path, "wb") as f:
            f.write(image_bytes)
    except Exception as e:
        logger.warning(f"Failed to write image to disk: {e}")

    rel_image_path = f"uploads/{unique_filename}"

    # 6. Insert record into database only if crop_block_id is provided
    detection_id = uuid.uuid4()
    detected_at = datetime.now(timezone.utc)
    if crop_block_id is not None:
        detection = DiseaseDetection(
            id=str(detection_id),
            crop_block_id=str(crop_block_id),
            image_path=rel_image_path,
            predicted_disease=inference_result["predicted_disease"],
            cnn_confidence=inference_result["confidence"] or 0.0,
            posterior_probability=None,
            validated=False,
        )
        db.add(detection)
        db.commit()
        db.refresh(detection)
        detection_id = uuid.UUID(str(detection.id))
        detected_at = detection.detected_at

    # 7. Construct complete response
    return DiseaseDetectionResponse(
        id=detection_id,
        crop_block_id=crop_block_id,
        image_path=rel_image_path,
        predicted_disease=inference_result["predicted_disease"],
        cnn_confidence=float(inference_result.get("confidence") or 0.0),
        posterior_probability=None,
        validated=False,
        detected_at=detected_at,
        crop=inference_result.get("crop"),
        crop_kn=inference_result.get("crop_kn"),
        scientific_name=inference_result.get("scientific_name"),
        condition=inference_result.get("condition"),
        condition_kn=inference_result.get("condition_kn"),
        affected_parts=inference_result.get("affected_parts"),
        is_healthy=inference_result.get("is_healthy", False),
        is_inconclusive=inference_result.get("inconclusive", False),
        causal_agent=inference_result.get("causal_agent"),
        symptoms=inference_result.get("symptoms"),
        symptoms_kn=inference_result.get("symptoms_kn"),
        differential_diagnosis=inference_result.get("differential_diagnosis"),
        differential_diagnosis_kn=inference_result.get("differential_diagnosis_kn"),
        favorable_conditions=inference_result.get("favorable_conditions"),
        favorable_conditions_kn=inference_result.get("favorable_conditions_kn"),
        preventive_practices=inference_result.get("preventive_practices"),
        preventive_practices_kn=inference_result.get("preventive_practices_kn"),
        cultural_biological_management=inference_result.get("cultural_biological_management"),
        cultural_biological_management_kn=inference_result.get("cultural_biological_management_kn"),
        chemical_management=inference_result.get("chemical_management"),
        chemical_management_kn=inference_result.get("chemical_management_kn"),
        expert_warning=inference_result.get("expert_warning"),
        expert_warning_kn=inference_result.get("expert_warning_kn"),
        management=inference_result.get("management"),
        management_kn=inference_result.get("management_kn"),
        sources=inference_result.get("sources"),
        top_predictions=inference_result.get("top_predictions"),
        backend=inference_result.get("backend"),
        is_plant=inference_result.get("is_plant", True),
        plant_coverage_pct=inference_result.get("plant_coverage_pct"),
        plausibility_note=inference_result.get("plausibility_note"),
        rejection_reason=inference_result.get("rejection_reason"),
        detected_objects=inference_result.get("detected_objects"),
        image_quality=inference_result.get("image_quality"),
        crop_match=inference_result.get("crop_match"),
        crop_mismatch_warning=inference_result.get("crop_mismatch_warning"),
        crop_support_status=inference_result.get("crop_support_status"),
        identification_rationale=inference_result.get("identification_rationale"),
        online_research=inference_result.get("online_research"),
        visual_similarity=inference_result.get("visual_similarity"),
        dataset_source=inference_result.get("dataset_source", "Hugging Face mohanty/PlantVillage (38 Classes, CC-BY-SA 3.0)"),
        diagnostic_disclaimer=inference_result.get("diagnostic_disclaimer"),
        next_steps=inference_result.get("next_steps"),
    )
