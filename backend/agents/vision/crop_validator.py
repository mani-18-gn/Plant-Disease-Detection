"""
Crop and Plant Validator Module for PlantGuard Vision Agent.

Ensures the uploaded image specifically depicts agricultural crops or plant foliage,
rejecting human faces, persons, animals, vehicles, electronics, furniture, or generic non-crop objects.

Validation Rules:
1. Rejects if a human face is detected (OpenCV Haar Cascade & YOLO person detector).
2. Rejects if prominent non-crop objects are detected (YOLOv8 COCO detector).
3. Rejects if vegetative foliage / chlorophyll / necrotic plant pigment coverage is insufficient.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

DETECTION_DIR = Path(__file__).resolve().parent / "weights" / "detection"
HAAR_CASCADE_PATH = DETECTION_DIR / "haarcascade_frontalface_default.xml"
YOLO_MODEL_PATH = DETECTION_DIR / "yolov8n.pt"

_face_cascade = None
_yolo_model = None

# COCO classes that unambiguously signify non-crop / unrelated objects
NON_CROP_COCO_CLASSES = {
    "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck", "boat",
    "traffic light", "fire hydrant", "stop sign", "parking meter", "bench",
    "cat", "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe",
    "backpack", "umbrella", "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard",
    "sports ball", "kite", "baseball bat", "baseball glove", "skateboard", "surfboard",
    "tennis racket", "bottle", "wine glass", "cup", "fork", "knife", "spoon", "bowl",
    "chair", "couch", "bed", "dining table", "toilet", "tv", "laptop", "mouse",
    "remote", "keyboard", "cell phone", "microwave", "oven", "toaster", "sink",
    "refrigerator", "book", "clock", "scissors", "teddy bear", "hair drier", "toothbrush"
}


def get_face_cascade():
    """Lazy load Haar Cascade for fast human face detection."""
    global _face_cascade
    if _face_cascade is not None:
        return _face_cascade
    if HAAR_CASCADE_PATH.exists():
        try:
            import cv2
            cascade = cv2.CascadeClassifier(str(HAAR_CASCADE_PATH))
            if not cascade.empty():
                _face_cascade = cascade
                logger.info("Haar Face Cascade loaded successfully.")
                return _face_cascade
            else:
                logger.warning(f"Haar cascade at {HAAR_CASCADE_PATH} is empty.")
        except Exception as e:
            logger.warning(f"Failed to load Haar Cascade: {e}")
    return None


def get_yolo_detector():
    """Lazy load YOLOv8n object detector for non-crop object & person detection."""
    global _yolo_model
    if _yolo_model is not None:
        return _yolo_model
    if YOLO_MODEL_PATH.exists():
        try:
            from ultralytics import YOLO
            model = YOLO(str(YOLO_MODEL_PATH))
            _yolo_model = model
            logger.info("YOLOv8 object detector loaded successfully.")
            return _yolo_model
        except Exception as e:
            logger.warning(f"Failed to load YOLOv8 detector: {e}")
    return None


def detect_human_face(image: Image.Image) -> bool:
    """
    Detect if the image contains one or more human faces using OpenCV Haar Cascade.
    """
    cascade = get_face_cascade()
    if cascade is None:
        return False
    try:
        import cv2
        img_rgb = image.convert("RGB")
        img_rgb.thumbnail((800, 800))
        arr = np.array(img_rgb)
        gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
        
        # Test candidate face detections
        candidates = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(48, 48))
        if len(candidates) == 0:
            candidates = cascade.detectMultiScale(cv2.equalizeHist(gray), scaleFactor=1.1, minNeighbors=6, minSize=(48, 48))

        # Confirm candidate contains human skin pigmentation to avoid false positives on leaf veins/textures
        for (x, y, w, h) in candidates:
            face_crop = arr[y:y+h, x:x+w].astype(float) / 255.0
            r, g, b = face_crop[..., 0], face_crop[..., 1], face_crop[..., 2]
            skin_mask = (r > 0.35) & (g > 0.20) & (r - g > 0.08) & (r - b > 0.12)
            if np.mean(skin_mask) >= 0.08:
                return True
        return False
    except Exception as e:
        logger.debug(f"Face detection exception: {e}")
        return False


def detect_unrelated_objects(image: Image.Image) -> List[Dict[str, Any]]:
    """
    Detect non-crop objects (vehicles, electronics, furniture, animals, persons) using YOLOv8.
    Returns list of detected non-crop object info.
    """
    detector = get_yolo_detector()
    if detector is None:
        return []
    try:
        results = detector(image, verbose=False, conf=0.40)
        detected = []
        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0].item())
                cls_name = r.names.get(cls_id, "").lower()
                conf = float(box.conf[0].item())
                if cls_name in NON_CROP_COCO_CLASSES:
                    detected.append({
                        "name": cls_name,
                        "confidence": round(conf, 3),
                    })
        return detected
    except Exception as e:
        logger.debug(f"YOLO object detection exception: {e}")
        return []


def calculate_foliage_coverage(image: Image.Image) -> float:
    """
    Calculate organic plant foliage percentage using Excess Green (ExG)
    and chlorotic/necrotic pigment detection.
    """
    img_rgb = image.convert("RGB")
    thumb = img_rgb.resize((128, 128))
    arr = np.array(thumb, dtype=float) / 255.0

    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]

    # Excess Green Index (ExG = 2G - R - B)
    exg = 2 * g - r - b
    green_mask = (exg > 0.03) | ((g > r * 0.92) & (g > b * 1.08) & (g > 0.12))

    # Chlorotic yellow / necrotic leaf spot mask
    yellow_brown_mask = (r > 0.25) & (g > 0.20) & (b < 0.35) & (r > b * 1.25)

    foliage_mask = green_mask | yellow_brown_mask
    return float(np.mean(foliage_mask) * 100.0)


def validate_crop_image(image: Image.Image) -> Dict[str, Any]:
    """
    Comprehensive validation to ensure image depicts crops or plants only.

    Returns:
        dict with keys:
            - is_crop: bool
            - reason: Optional[str] ('face_detected', 'unrelated_object', 'no_foliage')
            - message: str (Farmer-facing message in English)
            - message_kn: str (Farmer-facing message in Kannada)
            - plant_coverage_pct: float
            - detected_objects: List[str]
    """
    # 1. Human Face Check (Haar Cascade)
    if detect_human_face(image):
        return {
            "is_crop": False,
            "reason": "face_detected",
            "message": "This image does not appear to show a crop. A human face was detected. Please upload a clear photo of crop leaves or plants only.",
            "message_kn": "ಈ ಚಿತ್ರವು ಕೃಷಿ ಬೆಳೆಯನ್ನು ತೋರಿಸುತ್ತಿಲ್ಲ. ಚಿತ್ರದಲ್ಲಿ ಮಾನವ ಮುಖ ಕಂಡುಬಂದಿದೆ. ದಯವಿಟ್ಟು ಕೃಷಿ ಬೆಳೆಯ ಅಥವಾ ಗಿಡದ ಎಲೆಯ ಸ್ಪಷ್ಟ ಫೋಟೋವನ್ನು ಮಾತ್ರ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ.",
            "plant_coverage_pct": 0.0,
            "detected_objects": ["human face"],
        }

    # 2. Non-Crop Unrelated Object Check (YOLOv8)
    unrelated_objs = detect_unrelated_objects(image)
    if unrelated_objs:
        primary_obj = unrelated_objs[0]["name"]
        obj_names = ", ".join(list({o["name"] for o in unrelated_objs}))
        if primary_obj == "person":
            msg = "This image does not appear to show a crop. A person was detected in the photograph. Please upload a photo of crop leaves or plants only."
            msg_kn = "ಈ ಚಿತ್ರವು ಕೃಷಿ ಬೆಳೆಯನ್ನು ತೋರಿಸುತ್ತಿಲ್ಲ. ಚಿತ್ರದಲ್ಲಿ ವ್ಯಕ್ತಿ ಕಂಡುಬಂದಿದ್ದಾರೆ. ದಯವಿಟ್ಟು ಕೃಷಿ ಬೆಳೆಯ ಎಲೆಯ ಸ್ಪಷ್ಟ ಫೋಟೋವನ್ನು ಮಾತ್ರ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ."
        else:
            msg = f"This image does not appear to show a crop. An unrelated object ({obj_names}) was detected. Please upload a photo of crop leaves or plants only."
            msg_kn = f"ಈ ಚಿತ್ರವು ಕೃಷಿ ಬೆಳೆಯನ್ನು ತೋರಿಸುತ್ತಿಲ್ಲ. ಸಂಬಂಧವಿಲ್ಲದ ವಸ್ತು ({obj_names}) ಕಂಡುಬಂದಿದೆ. ದಯವಿಟ್ಟು ಕೃಷಿ ಬೆಳೆಯ ಅಥವಾ ಗಿಡದ ಎಲೆಯ ಸ್ಪಷ್ಟ ಫೋಟೋವನ್ನು ಮಾತ್ರ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ."

        return {
            "is_crop": False,
            "reason": "unrelated_object",
            "message": msg,
            "message_kn": msg_kn,
            "plant_coverage_pct": 0.0,
            "detected_objects": [o["name"] for o in unrelated_objs],
        }

    # 3. Organic Plant Pigment / Foliage Plausibility Check
    try:
        coverage_pct = calculate_foliage_coverage(image)
    except Exception as e:
        logger.warning(f"Foliage coverage error: {e}")
        coverage_pct = 50.0

    if coverage_pct < 7.5:
        return {
            "is_crop": False,
            "reason": "no_foliage",
            "message": "This image does not appear to show a crop. No crop or plant foliage was recognized in the photo. Please upload a clear photo of crop leaves or plants only.",
            "message_kn": "ಈ ಚಿತ್ರವು ಕೃಷಿ ಬೆಳೆಯನ್ನು ತೋರಿಸುತ್ತಿಲ್ಲ. ಚಿತ್ರದಲ್ಲಿ ಯಾವುದೇ ಕೃಷಿ ಬೆಳೆ ಅಥವಾ ಸಸ್ಯದ ಅಂಗಾಂಶಗಳು ಕಂಡುಬಂದಿಲ್ಲ. ದಯವಿಟ್ಟು ಕೃಷಿ ಬೆಳೆಯ ಎಲೆಯ ಸ್ಪಷ್ಟ ಫೋಟೋವನ್ನು ಅಪ್‌ಲೋಡ್ ಮಾಡಿ.",
            "plant_coverage_pct": round(coverage_pct, 1),
            "detected_objects": [],
        }

    # Valid crop image
    return {
        "is_crop": True,
        "reason": None,
        "message": f"Plausible crop foliage confirmed ({coverage_pct:.1f}% vegetative surface area).",
        "message_kn": f"ಕೃಷಿ ಬೆಳೆಯ ಎಲೆ ದೃಢೀಕರಿಸಲಾಗಿದೆ ({coverage_pct:.1f}% ಸಸ್ಯ ಪ್ರದೇಶ).",
        "plant_coverage_pct": round(coverage_pct, 1),
        "detected_objects": [],
    }
