import os
import sys
import argparse
import hashlib
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from PIL import Image, UnidentifiedImageError

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, precision_recall_fscore_support, confusion_matrix

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Add root project path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from backend.agents.vision.model import (
    ArecanutCNN,
    CLASS_NAMES as ARECA_CLASS_NAMES,
    FOLDER_TO_CLASS as ARECA_FOLDER_TO_CLASS,
    LOW_VOLUME_CLASSES,
)

# Export aliases for compatibility with Arecanut tests
CLASS_NAMES = ARECA_CLASS_NAMES
FOLDER_TO_CLASS = ARECA_FOLDER_TO_CLASS

from backend.agents.vision.preprocess import eval_transform, get_train_transform

DATASET_ROOT_ARECANUT = Path(__file__).resolve().parents[3] / "data" / "Arecanut_dataset"
DATASET_ROOT_PLANTVILLAGE = Path(__file__).resolve().parents[3] / "plantvillage_repo" / "raw" / "color"
DATASET_ROOT_PLANTDOC = Path(__file__).resolve().parents[3] / "backend" / "data" / "plantdoc"
WEIGHTS_DIR = Path(__file__).resolve().parent / "weights"


def compute_file_sha256(file_path: Path) -> str:
    """Compute SHA-256 hash of a file for exact duplicate detection."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def resolve_dataset_root(data_dir_arg: Optional[str] = None) -> Path:
    """
    Locate the dataset train directory with robust fallback resolution.
    Checks user argument, relative workspace path, and standard downloads path.
    """
    candidates = []
    if data_dir_arg:
        p = Path(data_dir_arg).resolve()
        candidates.extend([p, p / "train", p / "dataset" / "train"])

    project_root = Path(__file__).resolve().parents[3]
    candidates.extend([
        project_root / "data" / "Arecanut_dataset" / "dataset" / "train",
        project_root / "data" / "Arecanut_dataset" / "dataset",
        project_root / "data" / "Arecanut_dataset" / "train",
        project_root / "data" / "Arecanut_dataset",
        Path(r"C:\Users\admin\Downloads\Areca-Agent-main\data\Arecanut_dataset\dataset\train"),
        Path(r"C:\Users\admin\Downloads\Areca-Agent-main\data\Arecanut_dataset\dataset"),
    ])

    for cand in candidates:
        if cand.exists() and cand.is_dir():
            subdirs = [d.name for d in cand.iterdir() if d.is_dir()]
            if any(name in subdirs for name in ["0", "bud borer", "bud_borer"]):
                logger.info(f"Resolved dataset training path: {cand}")
                return cand
            elif "train" in subdirs and (cand / "train").is_dir():
                resolved = cand / "train"
                logger.info(f"Resolved dataset training path: {resolved}")
                return resolved

    raise FileNotFoundError(
        f"Could not locate Arecanut training dataset in candidate locations: {candidates}. "
        "Please provide --data-dir pointing to 'data/Arecanut_dataset/dataset/train'."
    )


def load_and_deduplicate_dataset(
    train_dir: Path,
    min_samples_per_class: int = 5,
) -> Tuple[List[Tuple[Path, int, bool]], Dict[str, Any]]:
    """
    Scan dataset directory, map numeric folders (0-8) and named folders to CLASS_NAMES,
    verify image readability with PIL, compute SHA-256 hashes, detect duplicate conflicts,
    and filter out exact duplicate images while keeping class labels consistent.
    """
    class_to_idx = {name: i for i, name in enumerate(CLASS_NAMES)}

    total_files_scanned = 0
    unreadable_files: List[Tuple[Path, str]] = []
    seen_hashes: Dict[str, Tuple[Path, int]] = {}
    duplicate_same_class: List[Dict[str, Any]] = []
    duplicate_conflicts: List[Dict[str, Any]] = []
    unique_samples: List[Tuple[Path, int, bool]] = []

    print("\n" + "=" * 70)
    print(f"AUDITING & LOADING ARECANUT DATASET: {train_dir}")
    print("=" * 70)

    for folder_name in sorted(os.listdir(train_dir)):
        folder_path = train_dir / folder_name
        if not folder_path.is_dir():
            continue

        if folder_name.isdigit():
            idx = int(folder_name)
            if 0 <= idx < len(CLASS_NAMES):
                normalized_class = CLASS_NAMES[idx]
            else:
                logger.warning(f"Numeric folder '{folder_name}' out of bounds (0-{len(CLASS_NAMES)-1}), skipping.")
                continue
        else:
            normalized_class = FOLDER_TO_CLASS.get(folder_name)
            if not normalized_class:
                if folder_name in class_to_idx:
                    normalized_class = folder_name
                else:
                    logger.warning(f"Unrecognized folder '{folder_name}', skipping.")
                    continue

        label_idx = class_to_idx[normalized_class]
        is_low_volume = normalized_class in LOW_VOLUME_CLASSES

        folder_files = [f for f in folder_path.glob("*") if f.is_file() and f.suffix.lower() in [".jpg", ".jpeg", ".png"]]

        for img_file in folder_files:
            total_files_scanned += 1

            try:
                with Image.open(img_file) as img:
                    img.verify()
            except Exception as e:
                unreadable_files.append((img_file, str(e)))
                logger.warning(f"Corrupt or unreadable image skipped: {img_file.name} ({e})")
                continue

            img_hash = compute_file_sha256(img_file)

            if img_hash in seen_hashes:
                first_path, first_label_idx = seen_hashes[img_hash]
                if first_label_idx != label_idx:
                    conflict_record = {
                        "hash": img_hash,
                        "file_a": str(first_path),
                        "class_a": CLASS_NAMES[first_label_idx],
                        "file_b": str(img_file),
                        "class_b": CLASS_NAMES[label_idx],
                    }
                    duplicate_conflicts.append(conflict_record)
                    logger.error(
                        f"[DUPLICATE CONFLICT] Identical image assigned to different classes!\n"
                        f"  File A: {first_path} -> {CLASS_NAMES[first_label_idx]}\n"
                        f"  File B: {img_file} -> {CLASS_NAMES[label_idx]}"
                    )
                else:
                    duplicate_same_class.append({
                        "hash": img_hash,
                        "kept_file": str(first_path),
                        "excluded_file": str(img_file),
                        "class": CLASS_NAMES[label_idx],
                    })
                continue
            else:
                seen_hashes[img_hash] = (img_file, label_idx)
                unique_samples.append((img_file, label_idx, is_low_volume))

    class_counts = [0] * len(CLASS_NAMES)
    for _, l_idx, _ in unique_samples:
        class_counts[l_idx] += 1

    missing_classes = [CLASS_NAMES[i] for i, c in enumerate(class_counts) if c == 0]
    if missing_classes:
        raise ValueError(
            f"Dataset validation failed: missing classes {missing_classes}. All 9 classes are required."
        )

    insufficient_classes = [CLASS_NAMES[i] for i, c in enumerate(class_counts) if c < min_samples_per_class]
    if insufficient_classes:
        raise ValueError(
            f"Dataset validation failed: classes with insufficient samples (<{min_samples_per_class}): {insufficient_classes}."
        )

    audit_summary = {
        "train_dir": str(train_dir),
        "total_files_scanned": total_files_scanned,
        "unreadable_files_count": len(unreadable_files),
        "duplicate_same_class_count": len(duplicate_same_class),
        "duplicate_conflicts_count": len(duplicate_conflicts),
        "unique_samples_count": len(unique_samples),
        "per_class_counts": {CLASS_NAMES[i]: class_counts[i] for i in range(len(CLASS_NAMES))},
        "duplicate_conflicts": duplicate_conflicts,
    }

    print("\n--- DATASET INTEGRITY & DEDUPLICATION REPORT ---")
    print(f"  Total Image Files Scanned: {total_files_scanned}")
    print(f"  Unreadable / Corrupted Files: {len(unreadable_files)}")
    print(f"  Duplicate Conflicts (Diff Classes): {len(duplicate_conflicts)}")
    print(f"  Internal Duplicates Excluded (Same Class): {len(duplicate_same_class)}")
    print(f"  Total Clean Unique Samples: {len(unique_samples)}")
    print("\n--- CLEAN UNIQUE SAMPLES PER CLASS ---")
    for i, name in enumerate(CLASS_NAMES):
        print(f"  [{i}] {name:<22} : {class_counts[i]} unique images")
    print("=" * 70 + "\n")

    return unique_samples, audit_summary


def create_stratified_split(
    unique_samples: List[Tuple[Path, int, bool]],
    val_fraction: float = 0.20,
    random_seed: int = 42,
) -> Tuple[List[Tuple[Path, int, bool]], List[Tuple[Path, int, bool]]]:
    """
    Create deterministic, stratified train and validation splits from unique samples.
    Ensures zero duplicate leakage between train and validation sets.
    """
    labels = [s[1] for s in unique_samples]
    train_samples, val_samples = train_test_split(
        unique_samples,
        test_size=val_fraction,
        random_state=random_seed,
        stratify=labels,
    )

    train_counts = [0] * len(CLASS_NAMES)
    val_counts = [0] * len(CLASS_NAMES)
    for _, l_idx, _ in train_samples:
        train_counts[l_idx] += 1
    for _, l_idx, _ in val_samples:
        val_counts[l_idx] += 1

    print("--- STRATIFIED DATASET SPLIT (SEED: {}) ---".format(random_seed))
    print(f"  Train Set Samples:      {len(train_samples)} (80%)")
    print(f"  Validation Set Samples: {len(val_samples)} (20%)")
    print("  Zero overlap guaranteed: validation samples excluded from training.")
    print("\n  Per-Class Stratification Breakdown:")
    for i, name in enumerate(CLASS_NAMES):
        print(f"    [{i}] {name:<22} | Train: {train_counts[i]:<3} | Val: {val_counts[i]:<3}")
    print("-" * 70 + "\n")

    return train_samples, val_samples


# Mapping from PlantDoc in-field folder names to PlantVillage folder/label naming conventions
PLANTDOC_TO_PV_FOLDER = {
    "Apple Scab Leaf": "Apple___Apple_scab",
    "Apple leaf": "Apple___healthy",
    "Apple rust leaf": "Apple___Cedar_apple_rust",
    "Bell_pepper leaf spot": "Pepper,_bell___Bacterial_spot",
    "Bell_pepper leaf": "Pepper,_bell___healthy",
    "Blueberry leaf": "Blueberry___healthy",
    "Cherry leaf": "Cherry_(including_sour)___healthy",
    "Corn Gray leaf spot": "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot",
    "Corn leaf blight": "Corn_(maize)___Northern_Leaf_Blight",
    "Corn rust leaf": "Corn_(maize)___Common_rust_",
    "grape leaf": "Grape___healthy",
    "grape leaf black rot": "Grape___Black_rot",
    "Peach leaf": "Peach___healthy",
    "Potato leaf early blight": "Potato___Early_blight",
    "Potato leaf late blight": "Potato___Late_blight",
    "Raspberry leaf": "Raspberry___healthy",
    "Soyabean leaf": "Soybean___healthy",
    "Squash Powdery mildew leaf": "Squash___Powdery_mildew",
    "Strawberry leaf": "Strawberry___healthy",
    "Tomato Early blight leaf": "Tomato___Early_blight",
    "Tomato leaf": "Tomato___healthy",
    "Tomato leaf bacterial spot": "Tomato___Bacterial_spot",
    "Tomato leaf late blight": "Tomato___Late_blight",
    "Tomato leaf mosaic virus": "Tomato___Tomato_mosaic_virus",
    "Tomato leaf yellow virus": "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
    "Tomato mold leaf": "Tomato___Leaf_Mold",
    "Tomato Septoria leaf spot": "Tomato___Septoria_leaf_spot",
    "Tomato two spotted spider mites leaf": "Tomato___Spider_mites Two-spotted_spider_mite",
}

PLANTDOC_TO_PV_LABEL = {
    "Apple Scab Leaf": "Apple Apple scab",
    "Apple leaf": "Apple healthy",
    "Apple rust leaf": "Apple Cedar apple rust",
    "Bell_pepper leaf spot": "Pepper, bell Bacterial spot",
    "Bell_pepper leaf": "Pepper, bell healthy",
    "Blueberry leaf": "Blueberry healthy",
    "Cherry leaf": "Cherry (including sour) healthy",
    "Corn Gray leaf spot": "Corn (maize) Cercospora leaf spot Gray leaf spot",
    "Corn leaf blight": "Corn (maize) Northern Leaf Blight",
    "Corn rust leaf": "Corn (maize) Common rust ",
    "grape leaf": "Grape healthy",
    "grape leaf black rot": "Grape Black rot",
    "Peach leaf": "Peach healthy",
    "Potato leaf early blight": "Potato Early blight",
    "Potato leaf late blight": "Potato Late blight",
    "Raspberry leaf": "Raspberry healthy",
    "Soyabean leaf": "Soybean healthy",
    "Squash Powdery mildew leaf": "Squash Powdery mildew",
    "Strawberry leaf": "Strawberry healthy",
    "Tomato Early blight leaf": "Tomato Early blight",
    "Tomato leaf": "Tomato healthy",
    "Tomato leaf bacterial spot": "Tomato Bacterial spot",
    "Tomato leaf late blight": "Tomato Late blight",
    "Tomato leaf mosaic virus": "Tomato Tomato mosaic virus",
    "Tomato leaf yellow virus": "Tomato Tomato Yellow Leaf Curl Virus",
    "Tomato mold leaf": "Tomato Leaf Mold",
    "Tomato Septoria leaf spot": "Tomato Septoria leaf spot",
    "Tomato two spotted spider mites leaf": "Tomato Spider mites Two-spotted spider mite",
}


class ArecanutDataset(Dataset):
    """
    PyTorch Dataset for Arecanut images.
    Can be initialized either from a list of pre-filtered samples
    or from a directory path (with automatic numeric/named folder resolution).
    """

    def __init__(
        self,
        samples_or_dir: Union[Path, str, List[Tuple[Path, int, bool]]],
        is_train: bool = True,
        max_samples_per_class: Optional[int] = None,
    ):
        self.is_train = is_train

        if isinstance(samples_or_dir, list):
            self.samples = samples_or_dir
        else:
            root_path = Path(samples_or_dir).resolve()
            unique_samples, _ = load_and_deduplicate_dataset(root_path)
            self.samples = unique_samples

        if max_samples_per_class is not None:
            capped_samples = []
            class_counters: Dict[int, int] = {}
            for item in self.samples:
                l_idx = item[1]
                count = class_counters.get(l_idx, 0)
                if count < max_samples_per_class:
                    capped_samples.append(item)
                    class_counters[l_idx] = count + 1
            self.samples = capped_samples

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        img_path, label_idx, is_low_volume = self.samples[idx]
        image = Image.open(img_path).convert("RGB")

        if self.is_train:
            transform = get_train_transform(is_low_volume=is_low_volume)
        else:
            transform = eval_transform

        tensor = transform(image)
        return tensor, label_idx


class PlantVillageDataset(Dataset):
    """
    Custom PyTorch Dataset for PlantVillage crop pathology dataset.
    Automatically discovers crop disease classes and partitions reproducible train/val splits.
    """

    def __init__(
        self,
        root_dir: Path,
        is_train: bool = True,
        train_ratio: float = 0.8,
        max_samples_per_class: Optional[int] = None,
        seed: int = 42,
    ):
        self.root_dir = root_dir
        self.is_train = is_train
        self.samples = []

        if not root_dir.exists():
            print(f"[!] Warning: PlantVillage directory not found at {root_dir}")
            self.classes = []
            self.class_to_idx = {}
            return

        self.classes = sorted([d.name for d in root_dir.iterdir() if d.is_dir()])
        self.class_to_idx = {name: i for i, name in enumerate(self.classes)}

        import random
        rng = random.Random(seed)

        for class_name in self.classes:
            class_folder = root_dir / class_name
            label_idx = self.class_to_idx[class_name]

            all_images = sorted([
                f for f in class_folder.glob("*")
                if f.is_file() and f.suffix.lower() in [".jpg", ".jpeg", ".png"]
            ])

            if max_samples_per_class:
                all_images = all_images[:max_samples_per_class * 2]

            rng.shuffle(all_images)
            split_point = int(len(all_images) * train_ratio)

            if is_train:
                selected = all_images[:split_point]
            else:
                selected = all_images[split_point:]

            if max_samples_per_class:
                selected = selected[:max_samples_per_class]

            for img_path in selected:
                self.samples.append((img_path, label_idx))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        img_path, label_idx = self.samples[idx]
        image = Image.open(img_path).convert("RGB")

        if self.is_train:
            transform = get_train_transform(is_low_volume=False)
        else:
            transform = eval_transform

        tensor = transform(image)
        return tensor, label_idx


class PlantVillageHuggingFaceDataset(Dataset):
    """
    Custom PyTorch Dataset utilizing Hugging Face `datasets` library.
    Seamlessly loads `mohanty/PlantVillage` or cached local imagefolder format,
    preventing repeated downloads and preparing reproducible train/val splits.
    """

    def __init__(
        self,
        is_train: bool = True,
        train_ratio: float = 0.8,
        max_samples_per_class: Optional[int] = None,
        seed: int = 42,
    ):
        self.is_train = is_train
        from datasets import load_dataset
        import random

        print("[...] Initializing PlantVillage dataset via Hugging Face `datasets`...")
        if DATASET_ROOT_PLANTVILLAGE.exists():
            hf_ds = load_dataset("imagefolder", data_dir=str(DATASET_ROOT_PLANTVILLAGE))
        else:
            hf_ds = load_dataset("mohanty/PlantVillage", "color")

        raw_data = hf_ds["train"]
        class_label = raw_data.features["label"]
        self.classes = list(class_label.names)
        self.class_to_idx = {name: i for i, name in enumerate(self.classes)}

        indices_by_class = {i: [] for i in range(len(self.classes))}
        for idx, lbl in enumerate(raw_data["label"]):
            indices_by_class[lbl].append(idx)

        rng = random.Random(seed)
        selected_indices = []
        for lbl, idxs in indices_by_class.items():
            rng.shuffle(idxs)
            split_point = int(len(idxs) * train_ratio)
            chosen = idxs[:split_point] if is_train else idxs[split_point:]
            if max_samples_per_class:
                chosen = chosen[:max_samples_per_class]
            selected_indices.extend(chosen)

        self.dataset = raw_data.select(selected_indices)
        self.samples = [(None, self.dataset[i]["label"]) for i in range(len(self.dataset))]

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, idx):
        item = self.dataset[idx]
        image = item["image"].convert("RGB")
        label = item["label"]
        transform = get_train_transform(is_low_volume=False) if self.is_train else eval_transform
        return transform(image), label


class PlantDocDataset(Dataset):
    """
    Custom PyTorch Dataset for PlantDoc in-field crop pathology dataset.
    Loads real farm photos with complex field backgrounds and maps them to standard 38 classes.
    """

    def __init__(
        self,
        root_dir: Path,
        split: str = "train",
        is_train: bool = True,
        class_names: Optional[list] = None,
        max_samples_per_class: Optional[int] = None,
        seed: int = 42,
    ):
        self.root_dir = root_dir / split if (root_dir / split).exists() else root_dir
        self.is_train = is_train
        self.samples = []

        if not self.root_dir.exists():
            print(f"[!] Warning: PlantDoc directory not found at {self.root_dir}")
            self.classes = class_names or []
            self.class_to_idx = {name: i for i, name in enumerate(self.classes)}
            return

        if class_names:
            self.classes = list(class_names)
        else:
            self.classes = sorted([d.name for d in self.root_dir.iterdir() if d.is_dir()])

        self.class_to_idx = {name: i for i, name in enumerate(self.classes)}

        for folder_name in sorted(os.listdir(self.root_dir)):
            folder_path = self.root_dir / folder_name
            if not folder_path.is_dir():
                continue

            mapped = (
                PLANTDOC_TO_PV_LABEL.get(folder_name)
                or PLANTDOC_TO_PV_FOLDER.get(folder_name)
                or folder_name
            )

            if mapped not in self.class_to_idx:
                for c_name, c_idx in self.class_to_idx.items():
                    if mapped.lower() in c_name.lower() or c_name.lower() in mapped.lower():
                        mapped = c_name
                        break

            if mapped not in self.class_to_idx:
                continue

            label_idx = self.class_to_idx[mapped]
            class_count = 0
            for img_file in sorted(folder_path.glob("*")):
                if img_file.is_file() and img_file.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp"]:
                    self.samples.append((img_file, label_idx))
                    class_count += 1
                    if max_samples_per_class and class_count >= max_samples_per_class:
                        break

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        img_path, label_idx = self.samples[idx]
        image = Image.open(img_path).convert("RGB")
        transform = get_train_transform(is_field=True) if self.is_train else eval_transform
        return transform(image), label_idx


class CombinedPlantDataset(Dataset):
    """
    Combined Dataset joining PlantVillage (controlled lab conditions) and PlantDoc (real farm conditions).
    Enhances generalization and in-field diagnostic accuracy across 38 classes.
    """

    def __init__(self, pv_dataset: Dataset, pd_dataset: Dataset):
        self.pv_dataset = pv_dataset
        self.pd_dataset = pd_dataset
        self.classes = getattr(pv_dataset, "classes", getattr(pd_dataset, "classes", []))
        self.class_to_idx = {name: i for i, name in enumerate(self.classes)}
        self.samples = list(pv_dataset.samples) + list(pd_dataset.samples)

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        if idx < len(self.pv_dataset):
            return self.pv_dataset[idx]
        return self.pd_dataset[idx - len(self.pv_dataset)]


def compute_class_weights(dataset: Dataset, num_classes: Optional[int] = None) -> torch.Tensor:
    """
    Compute inverse-frequency class weights across all classes
    to prevent majority classes from dominating loss.
    """
    if num_classes is None:
        num_classes = len(getattr(dataset, "classes", CLASS_NAMES))
    counts = [0] * num_classes
    for item in dataset.samples:
        label_idx = item[1]
        if label_idx < num_classes:
            counts[label_idx] += 1

    total = len(dataset)
    weights = [total / (num_classes * max(c, 1)) for c in counts]
    return torch.tensor(weights, dtype=torch.float32)


def format_confusion_matrix(cm, class_names: List[str]) -> str:
    """Format confusion matrix as an aligned readable ASCII grid."""
    col_title = "True \\ Pred"
    header = f"{col_title:<22} | " + " | ".join(f"{name[:6]:>6}" for name in class_names)
    separator = "-" * len(header)
    lines = [header, separator]
    for i, name in enumerate(class_names):
        row = f"{name:<22} | " + " | ".join(f"{cm[i][j]:>6}" for j in range(len(class_names)))
        lines.append(row)
    return "\n".join(lines)


def evaluate(
    model: nn.Module,
    data_loader: DataLoader,
    device: torch.device,
    num_classes: Optional[int] = None,
    class_names: Optional[List[str]] = None,
    criterion: Optional[nn.Module] = None,
    smoke_test: bool = False,
) -> Tuple[List[int], List[int], float, float, Any]:
    """Run validation pass and return per-class predictions, macro F1 score, validation loss, and confusion matrix."""
    if num_classes is None:
        num_classes = len(class_names) if class_names else len(CLASS_NAMES)
    if class_names is None:
        class_names = [f"Class_{i}" for i in range(num_classes)]

    model.eval()
    all_preds = []
    all_targets = []
    running_val_loss = 0.0
    total_samples = 0

    with torch.no_grad():
        for batch_idx, (images, labels) in enumerate(data_loader):
            if smoke_test and batch_idx >= 5:
                break
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            if criterion is not None:
                loss = criterion(outputs, labels)
                running_val_loss += loss.item() * images.size(0)
            total_samples += labels.size(0)

            _, preds = torch.max(outputs, 1)
            all_preds.extend(preds.cpu().numpy())
            all_targets.extend(labels.cpu().numpy())

    val_loss = (running_val_loss / max(total_samples, 1)) if criterion is not None else 0.0

    if len(all_targets) == 0:
        return [], [], 0.0, 0.0, None

    _, _, macro_f1, _ = precision_recall_fscore_support(
        all_targets,
        all_preds,
        labels=list(range(num_classes)),
        average="macro",
        zero_division=0,
    )

    cm = confusion_matrix(all_targets, all_preds, labels=list(range(num_classes)))

    return all_targets, all_preds, round(float(macro_f1), 4), round(float(val_loss), 4), cm


def run_training(
    dataset_type: str = "arecanut",
    data_dir: Optional[str] = None,
    smoke_test: bool = False,
    epochs: int = 30,
    patience: int = 5,
    batch_size: int = 32,
    lr: float = 1e-4,
    val_split: float = 0.20,
    random_seed: int = 42,
    freeze_backbone: bool = True,
    unfreeze_at_epoch: Optional[int] = 5,
):
    """
    End-to-end vision model training pipeline supporting:
    - 'arecanut': 9-class specialized plantation model with deduplication audit and stratified split.
    - 'plantvillage': Multicrop pathology (14 crops, 26+ conditions).
    - 'plantdoc': PlantDoc in-field benchmark dataset.
    - 'combined': Joint PlantVillage + PlantDoc dataset for robust field generalization.
    - 'plantvillage-hf': Hugging Face streaming/cached loader.
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"\n[...] Starting Vision Model Training")
    print(f"    Dataset Type: {dataset_type}")
    print(f"    Device: {device}, Smoke Test: {smoke_test}")
    print(f"    Config: Max Epochs={epochs}, Early Stopping Patience={patience}, Freeze Backbone={freeze_backbone}")

    sample_cap = 15 if smoke_test else None
    WEIGHTS_DIR.mkdir(parents=True, exist_ok=True)
    audit_summary = {}

    if dataset_type.lower() == "arecanut":
        train_dir = resolve_dataset_root(data_dir)
        unique_samples, audit_summary = load_and_deduplicate_dataset(train_dir)

        train_samples, val_samples = create_stratified_split(
            unique_samples,
            val_fraction=val_split,
            random_seed=random_seed,
        )

        if smoke_test:
            train_samples = train_samples[:30]
            val_samples = val_samples[:10]
            batch_size = min(batch_size, 8)
            total_epochs = 1
        else:
            total_epochs = epochs

        train_dataset = ArecanutDataset(train_samples, is_train=True)
        val_dataset = ArecanutDataset(val_samples, is_train=False)
        class_names = CLASS_NAMES
        save_name = "smoke_test_arecanut_cnn.pt" if smoke_test else "arecanut_cnn.pt"

    elif dataset_type.lower() in ["plantvillage-hf", "hf-plantvillage", "huggingface"]:
        train_dataset = PlantVillageHuggingFaceDataset(is_train=True, max_samples_per_class=sample_cap)
        val_dataset = PlantVillageHuggingFaceDataset(is_train=False, max_samples_per_class=sample_cap)
        class_names = train_dataset.classes
        save_name = "smoke_test_plantvillage_cnn.pt" if smoke_test else "plantvillage_cnn.pt"
        total_epochs = 1 if smoke_test else epochs

    elif dataset_type.lower() in ["plantdoc", "plant-doc", "field"]:
        train_dataset = PlantDocDataset(DATASET_ROOT_PLANTDOC, split="train", is_train=True, max_samples_per_class=sample_cap)
        val_dataset = PlantDocDataset(DATASET_ROOT_PLANTDOC, split="test", is_train=False, class_names=train_dataset.classes, max_samples_per_class=sample_cap)
        class_names = train_dataset.classes
        save_name = "smoke_test_plantdoc_cnn.pt" if smoke_test else "plantdoc_cnn.pt"
        total_epochs = 1 if smoke_test else epochs

    elif dataset_type.lower() in ["combined", "plantvillage+plantdoc", "joint"]:
        root_dir = DATASET_ROOT_PLANTVILLAGE
        pv_train = PlantVillageDataset(root_dir, is_train=True, max_samples_per_class=sample_cap)
        pv_test = PlantVillageDataset(root_dir, is_train=False, max_samples_per_class=sample_cap)
        pd_train = PlantDocDataset(DATASET_ROOT_PLANTDOC, split="train", is_train=True, class_names=pv_train.classes, max_samples_per_class=sample_cap)
        pd_test = PlantDocDataset(DATASET_ROOT_PLANTDOC, split="test", is_train=False, class_names=pv_train.classes, max_samples_per_class=sample_cap)
        train_dataset = CombinedPlantDataset(pv_train, pd_train)
        val_dataset = CombinedPlantDataset(pv_test, pd_test)
        class_names = train_dataset.classes
        save_name = "smoke_test_combined_cnn.pt" if smoke_test else "combined_plantvillage_plantdoc_cnn.pt"
        total_epochs = 1 if smoke_test else epochs

    else:
        root_dir = DATASET_ROOT_PLANTVILLAGE
        train_dataset = PlantVillageDataset(root_dir, is_train=True, max_samples_per_class=sample_cap)
        val_dataset = PlantVillageDataset(root_dir, is_train=False, max_samples_per_class=sample_cap)
        class_names = train_dataset.classes
        save_name = "smoke_test_plantvillage_cnn.pt" if smoke_test else "plantvillage_cnn.pt"
        total_epochs = 1 if smoke_test else epochs

    num_classes = len(class_names)
    print(f"[+] Loaded {len(train_dataset)} training samples, {len(val_dataset)} validation samples across {num_classes} classes:")
    for i, name in enumerate(class_names):
        print(f"    [{i:02d}] {name}")

    if len(train_dataset) == 0:
        print("[!] Error: No training samples available. Aborting.")
        return {"status": "error", "message": "No training samples found."}

    class_weights = compute_class_weights(train_dataset, num_classes).to(device)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=0)

    # Initialize model
    model = ArecanutCNN(num_classes=num_classes, pretrained=True, freeze_backbone=freeze_backbone).to(device)
    criterion = nn.CrossEntropyLoss(weight=class_weights)
    optimizer = torch.optim.AdamW(filter(lambda p: p.requires_grad, model.parameters()), lr=lr, weight_decay=1e-2)

    save_path = WEIGHTS_DIR / save_name
    if smoke_test:
        print(f"\n[SAFETY NOTE] Smoke test checkpoint will be saved to: {save_path.name}")
        print("  Production models and weights will NOT be modified or overwritten.")
    else:
        print(f"\n[TARGET WEIGHTS] Production weights will be saved to: {save_path}")

    best_macro_f1 = -1.0
    best_val_loss = 999.0
    best_epoch = 0
    patience_counter = 0
    best_report = ""
    best_cm = None

    for epoch in range(1, total_epochs + 1):
        if not smoke_test and unfreeze_at_epoch and epoch == unfreeze_at_epoch and freeze_backbone:
            print(f"\n[INFO] Unfreezing backbone for fine-tuning at lower learning rate (lr={lr * 0.1})...")
            model.unfreeze_backbone()
            optimizer = torch.optim.AdamW(model.parameters(), lr=lr * 0.1, weight_decay=1e-2)

        model.train()
        running_loss = 0.0
        correct = 0
        total = 0

        print(f"\n--- Epoch {epoch}/{total_epochs} ---")
        for batch_idx, (images, labels) in enumerate(train_loader):
            if smoke_test and batch_idx >= 5:
                print("  [Smoke Test] Pipeline verified: reached batch limit (5 batches). Stopping epoch.")
                break

            images, labels = images.to(device), labels.to(device)

            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * images.size(0)
            _, preds = torch.max(outputs, 1)
            correct += torch.sum(preds == labels.data).item()
            total += labels.size(0)

            if (batch_idx + 1) % 10 == 0:
                print(f"  Batch {batch_idx + 1}/{len(train_loader)} | Loss: {loss.item():.4f}")

        epoch_loss = running_loss / max(total, 1)
        epoch_acc = correct / max(total, 1)

        # Validation evaluation
        targets, preds, val_macro_f1, val_loss, cm = evaluate(
            model,
            val_loader,
            device,
            num_classes=num_classes,
            class_names=class_names,
            criterion=criterion,
            smoke_test=smoke_test,
        )
        print(f"Epoch {epoch} Results | Train Loss: {epoch_loss:.4f} | Train Acc: {epoch_acc:.4f} | Val Loss: {val_loss:.4f} | Val Macro F1: {val_macro_f1:.4f}")

        # Checkpoint saving
        if val_macro_f1 > best_macro_f1 or smoke_test:
            best_macro_f1 = val_macro_f1
            best_val_loss = val_loss
            best_cm = cm
            best_epoch = epoch
            patience_counter = 0
            torch.save(model.state_dict(), save_path)

            best_report = classification_report(
                targets,
                preds,
                labels=list(range(num_classes)),
                target_names=class_names,
                digits=4,
                zero_division=0,
            )
            print(f"  [+] CHECKPOINT SAVED (Val Macro F1: {best_macro_f1:.4f}, Val Loss: {val_loss:.4f}) -> {save_path.name}")
        else:
            patience_counter += 1
            print(f"  [-] No improvement in Val Macro F1. Early stopping counter: {patience_counter}/{patience}")

        if not smoke_test and patience_counter >= patience:
            print(f"\n[EARLY STOPPING] Validation Macro F1 did not improve for {patience} epochs. Stopping at Epoch {epoch}.")
            break

    print("\n" + "=" * 60)
    if smoke_test:
        print("=== SMOKE TEST PIPELINE CHECK COMPLETE ===")
        print(f"   Status: Successfully executed 1 epoch pipeline test.")
        print(f"   Temporary Checkpoint: {save_path.resolve()}")
        print("   Production model was NOT touched.")
    else:
        print("=== TRAINING COMPLETE - BEST CHECKPOINT SUMMARY ===")
        print(f"   Best Checkpoint Epoch: Epoch {best_epoch}")
        print(f"   Best Validation Macro F1: {best_macro_f1:.4f}")
        print(f"   Best Validation Loss: {best_val_loss:.4f}")
        print(f"   Saved Checkpoint File: {save_path.resolve()}")
    print("=" * 60)

    if not smoke_test and best_report:
        print("\n=== PER-CLASS EVALUATION REPORT (BEST MODEL) ===")
        print(best_report)

    if not smoke_test and best_cm is not None:
        print("\n=== CONFUSION MATRIX (BEST MODEL) ===")
        print(format_confusion_matrix(best_cm, class_names))

    return {
        "status": "success",
        "smoke_test": smoke_test,
        "checkpoint_path": str(save_path),
        "audit_summary": audit_summary,
        "best_epoch": best_epoch,
        "best_macro_f1": best_macro_f1,
        "best_val_loss": best_val_loss,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Plant Disease Detection Vision Models")
    parser.add_argument(
        "--dataset",
        type=str,
        choices=["plantvillage", "plantvillage-hf", "plantdoc", "combined", "arecanut"],
        default="arecanut",
        help="Dataset to train on (plantvillage, plantvillage-hf, plantdoc, combined, or arecanut)",
    )
    parser.add_argument("--data-dir", type=str, default=None, help="Path to dataset directory (for arecanut)")
    parser.add_argument("--smoke-test", action="store_true", help="Run 1-epoch pipeline check without overwriting production model")
    parser.add_argument("--epochs", type=int, default=30, help="Max training epochs")
    parser.add_argument("--patience", type=int, default=5, help="Early stopping patience")
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size")
    parser.add_argument("--lr", type=float, default=1e-4, help="Learning rate")
    args = parser.parse_args()

    run_training(
        dataset_type=args.dataset,
        data_dir=args.data_dir,
        smoke_test=args.smoke_test,
        epochs=args.epochs,
        patience=args.patience,
        batch_size=args.batch_size,
        lr=args.lr,
    )
