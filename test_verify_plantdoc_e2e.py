import httpx
from pathlib import Path
from PIL import Image, ImageDraw
import io

BASE_URL = "http://127.0.0.1:8000/api/v1"

def run_tests():
    client = httpx.Client(timeout=30.0)

    print("=" * 60)
    print("RUNNING END-TO-END VERIFICATION: PLANTVILLAGE + PLANTDOC")
    print("=" * 60)

    # 1. Vision Status
    print("\n1. Testing Vision Status Endpoint...")
    r = client.get(f"{BASE_URL}/agents/vision/status")
    assert r.status_code == 200, f"Status failed: {r.status_code}"
    status_data = r.json()
    print(f"   [PASS] Status: {status_data.get('status')}, Crops: {len(status_data.get('supported_crops', []))}")

    # 2. Sample Images Catalog
    print("\n2. Testing Sample Images Catalog...")
    r = client.get(f"{BASE_URL}/agents/vision/sample-images")
    assert r.status_code == 200, f"Sample images failed: {r.status_code}"
    samples = r.json()
    plantdoc_samples = [s for s in samples if "PlantDoc" in s.get("title", "") or "PlantDoc" in s.get("badge", "")]
    print(f"   [PASS] Total Samples: {len(samples)}, PlantDoc In-Field Samples: {len(plantdoc_samples)}")
    for ps in plantdoc_samples[:3]:
        print(f"          - {ps['title']} ({ps['crop']} - {ps['condition']})")

    # 3. Test PlantDoc In-Field Image (Tomato Early Blight)
    print("\n3. Testing In-Field PlantDoc Diagnosis (Tomato Early Blight)...")
    field_img_path = Path("backend/data/test_labeled_samples/PlantDoc_Tomato_Early_Blight_Field.jpg")
    assert field_img_path.exists(), "PlantDoc field image missing"
    with open(field_img_path, "rb") as f:
        files = {"file": ("field_tomato.jpg", f, "image/jpeg")}
        r = client.post(f"{BASE_URL}/agents/vision/detect", files=files)
    assert r.status_code in [200, 201], f"Detection failed: {r.status_code} {r.text}"
    det = r.json()
    print(f"   [PASS] Result: {det.get('predicted_disease')}")
    print(f"          Crop: {det.get('crop')}, Condition: {det.get('condition')}")
    conf = det.get('cnn_confidence') or det.get('confidence') or 0.0
    print(f"          Confidence: {conf * 100:.1f}%, Is Plant: {det.get('is_plant')}")
    print(f"          Dataset Source: {det.get('dataset_source')}")
    print(f"          Next Steps: {len(det.get('next_steps', []))} items")
    assert det.get("is_plant") is True, "Should be recognized as a plant"
    assert "tomato" in det.get("crop", "").lower(), f"Expected tomato, got {det.get('crop')}"

    # 4. Test PlantDoc In-Field Image (Corn Northern Leaf Blight)
    print("\n4. Testing In-Field PlantDoc Diagnosis (Corn Northern Leaf Blight)...")
    corn_img_path = Path("backend/data/test_labeled_samples/PlantDoc_Corn_Leaf_Blight_Field.jpg")
    with open(corn_img_path, "rb") as f:
        files = {"file": ("field_corn.jpg", f, "image/jpeg")}
        r = client.post(f"{BASE_URL}/agents/vision/detect", files=files)
    assert r.status_code in [200, 201], f"Detection failed: {r.status_code} {r.text}"
    corn_det = r.json()
    corn_conf = corn_det.get('cnn_confidence') or corn_det.get('confidence') or 0.0
    print(f"   [PASS] Result: {corn_det.get('predicted_disease')}")
    print(f"          Crop: {corn_det.get('crop')}, Condition: {corn_det.get('condition')}")
    print(f"          Confidence: {corn_conf * 100:.1f}%, Is Plant: {corn_det.get('is_plant')}")
    assert corn_det.get("is_plant") is True
    assert "corn" in corn_det.get("crop", "").lower()

    # 4b. Test PlantVillage Laboratory Image (Apple Scab)
    print("\n4b. Testing PlantVillage Lab Leaf Diagnosis (Apple Scab)...")
    apple_img_path = Path("backend/data/test_labeled_samples/Apple___Apple_scab___00075aa8-d81a-4184-8541-b692b78d398a___FREC_Scab 3335.JPG")
    with open(apple_img_path, "rb") as f:
        files = {"file": ("lab_apple.jpg", f, "image/jpeg")}
        r = client.post(f"{BASE_URL}/agents/vision/detect", files=files)
    assert r.status_code in [200, 201], f"Detection failed: {r.status_code} {r.text}"
    apple_det = r.json()
    apple_conf = apple_det.get('cnn_confidence') or apple_det.get('confidence') or 0.0
    print(f"   [PASS] Result: {apple_det.get('predicted_disease')}")
    print(f"          Crop: {apple_det.get('crop')}, Condition: {apple_det.get('condition')}")
    print(f"          Confidence: {apple_conf * 100:.1f}%, Is Plant: {apple_det.get('is_plant')}")
    assert apple_det.get("is_plant") is True
    assert "apple" in apple_det.get("crop", "").lower()

    # 5. Test Non-Crop Image Rejection
    print("\n5. Testing Strict Non-Crop Image Rejection...")
    non_crop = Image.new("RGB", (300, 300), color=(180, 180, 190))
    draw = ImageDraw.Draw(non_crop)
    draw.rectangle([50, 50, 250, 250], fill=(70, 70, 90), outline=(20, 20, 30), width=4)
    buf = io.BytesIO()
    non_crop.save(buf, format="JPEG")
    buf.seek(0)
    files = {"file": ("non_crop.jpg", buf, "image/jpeg")}
    r = client.post(f"{BASE_URL}/agents/vision/detect", files=files)
    assert r.status_code in [200, 201], f"Call failed: {r.status_code}"
    rej = r.json()
    print(f"   [PASS] Is Plant: {rej.get('is_plant')}")
    print(f"          Rejection Note: {rej.get('symptoms')}")
    assert rej.get("is_plant") is False, "Non-crop must be rejected"
    assert "does not appear to show a crop" in rej.get("symptoms", "").lower(), "Must include exact rejection message"

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED SUCCESSFULLY! (100% VERIFIED)")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
