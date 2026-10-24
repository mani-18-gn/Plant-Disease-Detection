"""
Script to fetch, sanitize, and structure the PlantDoc In-Field Dataset
from https://github.com/pratikkayal/PlantDoc-Dataset.git

Handles Windows filename safety (stripping illegal chars like '?', ':', '%')
and structures data into backend/data/plantdoc/ for training and validation.
"""

import os
import re
import sys
import time
from pathlib import Path
import httpx

BASE_DIR = Path(__file__).resolve().parents[1]
PLANTDOC_DIR = BASE_DIR / "data" / "plantdoc"
SAMPLES_DIR = BASE_DIR / "data" / "test_labeled_samples"

GITHUB_API_BASE = "https://api.github.com/repos/pratikkayal/PlantDoc-Dataset/contents"
RAW_BASE = "https://raw.githubusercontent.com/pratikkayal/PlantDoc-Dataset/master"

HEADERS = {"User-Agent": "PlantDiseaseDetection-DataSync/1.0"}


def sanitize_filename(name: str) -> str:
    """Remove Windows-illegal characters from scraped filenames."""
    # Split query params if any
    clean = name.split("?")[0]
    # Remove characters illegal on Windows: < > : " / \ | ? * %
    clean = re.sub(r'[<>:"/\\|?*%]', '_', clean)
    if not clean.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
        clean += ".jpg"
    return clean


def download_folder_images(split: str, class_name: str, max_images: int = 10, client: httpx.Client = None):
    out_dir = PLANTDOC_DIR / split / class_name
    out_dir.mkdir(parents=True, exist_ok=True)

    url = f"{GITHUB_API_BASE}/{split}/{class_name}"
    try:
        resp = client.get(url, headers=HEADERS, timeout=15.0)
        if resp.status_code != 200:
            print(f"[!] Warning: Could not list {url} (status {resp.status_code})")
            return []
        items = resp.json()
    except Exception as e:
        print(f"[!] Error fetching {url}: {e}")
        return []

    downloaded = []
    count = 0
    for item in items:
        if count >= max_images:
            break
        raw_name = item.get("name", "")
        clean_name = sanitize_filename(raw_name)
        target_path = out_dir / clean_name

        if target_path.exists() and target_path.stat().st_size > 1000:
            downloaded.append(target_path)
            count += 1
            continue

        raw_url = item.get("download_url") or f"{RAW_BASE}/{split}/{class_name}/{raw_name}"
        try:
            img_resp = client.get(raw_url, headers=HEADERS, timeout=20.0)
            if img_resp.status_code == 200 and len(img_resp.content) > 1000:
                with open(target_path, "wb") as f:
                    f.write(img_resp.content)
                downloaded.append(target_path)
                count += 1
        except Exception as e:
            pass

    return downloaded


def sync_plantdoc(max_per_class: int = 8):
    print("=" * 60)
    print("Starting PlantDoc Dataset Ingestion")
    print(f"Target Directory: {PLANTDOC_DIR}")
    print("=" * 60)

    client = httpx.Client()
    total_images = 0

    # 1. Fetch class list for test
    for split, cap in [("test", max_per_class), ("train", max_per_class)]:
        split_url = f"{GITHUB_API_BASE}/{split}"
        try:
            r = client.get(split_url, headers=HEADERS, timeout=15.0)
            if r.status_code != 200:
                print(f"[!] Error listing {split}: {r.status_code}")
                continue
            folders = [d["name"] for d in r.json() if d.get("type") == "dir"]
        except Exception as e:
            print(f"[!] Exception: {e}")
            continue

        print(f"\n[+] Processing '{split}' split ({len(folders)} classes)...")
        for idx, c_name in enumerate(folders):
            files = download_folder_images(split, c_name, max_images=cap, client=client)
            print(f"    [{idx+1}/{len(folders)}] {c_name}: {len(files)} field images")
            total_images += len(files)

    print(f"\n[OK] Successfully ingested {total_images} PlantDoc in-field images into {PLANTDOC_DIR}")


if __name__ == "__main__":
    cap = 6 if len(sys.argv) < 2 else int(sys.argv[1])
    sync_plantdoc(max_per_class=cap)
