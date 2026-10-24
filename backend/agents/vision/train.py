import os
import sys
import argparse
from pathlib import Path
from PIL import Image

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.metrics import classification_report, precision_recall_fscore_support

# Add root project path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from backend.agents.vision.model import ArecanutCNN, CLASS_NAMES as ARECA_CLASS_NAMES, FOLDER_TO_CLASS as ARECA_FOLDER_TO_CLASS, LOW_VOLUME_CLASSES
from backend.agents.vision.preprocess import eval_transform, get_train_transform

DATASET_ROOT_ARECANUT = Path(__file__).resolve().parents[3] / "data" / "Arecanut_dataset"
DATASET_ROOT_PLANTVILLAGE = Path(__file__).resolve().parents[3] / "plantvillage_repo" / "raw" / "color"
DATASET_ROOT_PLANTDOC = Path(__file__).resolve().parents[3] / "backend" / "data" / "plantdoc"
WEIGHTS_DIR = Path(__file__).parent / "weights"

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
    Custom PyTorch Dataset for Arecanut images.
    Maps raw folder names ('bud borer', 'Stem_bleeding') to normalized class indexes.
    """

    def __init__(self, root_dir: Path, is_train: bool = True, max_samples_per_class: int | None = None):
        self.root_dir = root_dir
        self.is_train = is_train
        self.samples = []

        class_to_idx = {name: i for i, name in enumerate(ARECA_CLASS_NAMES)}

        if root_dir.exists():
            for folder_name in sorted(os.listdir(root_dir)):
                folder_path = root_dir / folder_name
                if not folder_path.is_dir():
                    continue

                normalized_class = ARECA_FOLDER_TO_CLASS.get(folder_name)
                if not normalized_class or normalized_class not in class_to_idx:
                    continue

                label_idx = class_to_idx[normalized_class]
                is_low_volume = normalized_class in LOW_VOLUME_CLASSES

                class_count = 0
                for img_file in folder_path.glob("*"):
                    if img_file.is_file() and img_file.suffix.lower() in [".jpg", ".jpeg", ".png"]:
                        self.samples.append((img_file, label_idx, is_low_volume))
                        class_count += 1
                        if max_samples_per_class and class_count >= max_samples_per_class:
                            break

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
        max_samples_per_class: int | None = None,
        seed: int = 42
    ):
        self.root_dir = root_dir
        self.is_train = is_train
        self.samples = []

        if not root_dir.exists():
            print(f"[!] Warning: PlantVillage directory not found at {root_dir}")
            self.classes = []
            self.class_to_idx = {}
            return

        # Discover all subfolders as crop disease classes
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
    preventing repeated 2GB full downloads and preparing reproducible train/val splits.
    """

    def __init__(
        self,
        is_train: bool = True,
        train_ratio: float = 0.8,
        max_samples_per_class: int | None = None,
        seed: int = 42
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

        # Stratified split by class
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
        class_names: list | None = None,
        max_samples_per_class: int | None = None,
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

            # Resolve mapped class
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


def compute_class_weights(dataset: Dataset, num_classes: int) -> torch.Tensor:
    """
    Compute inverse-frequency class weights to balance representation across classes.
    """
    counts = [0] * num_classes
    for item in dataset.samples:
        label_idx = item[1]
        counts[label_idx] += 1

    total = len(dataset)
    weights = [total / (num_classes * max(c, 1)) for c in counts]
    return torch.tensor(weights, dtype=torch.float32)


def evaluate(model: nn.Module, test_loader: DataLoader, device: torch.device, num_classes: int, class_names: list, smoke_test: bool = False):
    """Run validation pass on test set and return per-class predictions and macro F1 score."""
    model.eval()
    all_preds = []
    all_targets = []

    with torch.no_grad():
        for batch_idx, (images, labels) in enumerate(test_loader):
            if smoke_test and batch_idx >= 15:
                break
            images = images.to(device)
            outputs = model(images)
            _, preds = torch.max(outputs, 1)
            all_preds.extend(preds.cpu().numpy())
            all_targets.extend(labels.numpy())

    if len(all_targets) == 0:
        return [], [], 0.0

    _, _, macro_f1, _ = precision_recall_fscore_support(
        all_targets,
        all_preds,
        labels=list(range(num_classes)),
        average="macro",
        zero_division=0,
    )

    return all_targets, all_preds, round(float(macro_f1), 4)


def run_training(
    dataset_type: str = "plantvillage",
    smoke_test: bool = False,
    epochs: int = 10,
    patience: int = 3,
    batch_size: int = 32,
    lr: float = 1e-4,
    freeze_backbone: bool = True,
    unfreeze_at_epoch: int | None = 3,
):
    """
    Unified training pipeline supporting:
    - 'plantvillage': Multicrop pathology (14 crops, 26+ conditions)
    - 'arecanut': Arecanut 9-class specialized plantation model
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"\n[...] Starting Vision Model Training")
    print(f"    Dataset Type: {dataset_type}")
    print(f"    Device: {device}, Smoke Test: {smoke_test}")
    print(f"    Config: Max Epochs={epochs}, Early Stopping Patience={patience}, Freeze Backbone={freeze_backbone}")

    sample_cap = 15 if smoke_test else None

    if dataset_type.lower() in ["plantvillage-hf", "hf-plantvillage", "huggingface"]:
        train_dataset = PlantVillageHuggingFaceDataset(is_train=True, max_samples_per_class=sample_cap)
        test_dataset = PlantVillageHuggingFaceDataset(is_train=False, max_samples_per_class=sample_cap)
        class_names = train_dataset.classes
        save_name = "plantvillage_cnn.pt"
    elif dataset_type.lower() in ["plantdoc", "plant-doc", "field"]:
        train_dataset = PlantDocDataset(DATASET_ROOT_PLANTDOC, split="train", is_train=True, max_samples_per_class=sample_cap)
        test_dataset = PlantDocDataset(DATASET_ROOT_PLANTDOC, split="test", is_train=False, class_names=train_dataset.classes, max_samples_per_class=sample_cap)
        class_names = train_dataset.classes
        save_name = "plantdoc_cnn.pt"
    elif dataset_type.lower() in ["combined", "plantvillage+plantdoc", "joint"]:
        root_dir = DATASET_ROOT_PLANTVILLAGE
        pv_train = PlantVillageDataset(root_dir, is_train=True, max_samples_per_class=sample_cap)
        pv_test = PlantVillageDataset(root_dir, is_train=False, max_samples_per_class=sample_cap)
        pd_train = PlantDocDataset(DATASET_ROOT_PLANTDOC, split="train", is_train=True, class_names=pv_train.classes, max_samples_per_class=sample_cap)
        pd_test = PlantDocDataset(DATASET_ROOT_PLANTDOC, split="test", is_train=False, class_names=pv_train.classes, max_samples_per_class=sample_cap)
        train_dataset = CombinedPlantDataset(pv_train, pd_train)
        test_dataset = CombinedPlantDataset(pv_test, pd_test)
        class_names = train_dataset.classes
        save_name = "combined_plantvillage_plantdoc_cnn.pt"
    elif dataset_type.lower() == "plantvillage":
        root_dir = DATASET_ROOT_PLANTVILLAGE
        train_dataset = PlantVillageDataset(root_dir, is_train=True, max_samples_per_class=sample_cap)
        test_dataset = PlantVillageDataset(root_dir, is_train=False, max_samples_per_class=sample_cap)
        class_names = train_dataset.classes
        save_name = "plantvillage_cnn.pt"
    else:
        train_dataset = ArecanutDataset(DATASET_ROOT_ARECANUT / "train", is_train=True, max_samples_per_class=sample_cap)
        test_dataset = ArecanutDataset(DATASET_ROOT_ARECANUT / "test", is_train=False, max_samples_per_class=sample_cap)
        class_names = ARECA_CLASS_NAMES
        save_name = "arecanut_cnn.pt"

    num_classes = len(class_names)
    print(f"[+] Loaded {len(train_dataset)} training samples, {len(test_dataset)} test samples across {num_classes} classes:")
    for i, name in enumerate(class_names):
        print(f"    [{i:02d}] {name}")

    if len(train_dataset) == 0:
        print("[!] Error: No training samples available. Aborting.")
        return

    class_weights = compute_class_weights(train_dataset, num_classes).to(device)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=0)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False, num_workers=0)

    # Initialize MobileNetV2 architecture
    model = ArecanutCNN(num_classes=num_classes, pretrained=True, freeze_backbone=freeze_backbone).to(device)
    criterion = nn.CrossEntropyLoss(weight=class_weights)
    optimizer = torch.optim.AdamW(filter(lambda p: p.requires_grad, model.parameters()), lr=lr, weight_decay=1e-2)

    total_epochs = 1 if smoke_test else epochs
    best_macro_f1 = -1.0
    best_epoch = 0
    patience_counter = 0
    best_report = ""

    WEIGHTS_DIR.mkdir(parents=True, exist_ok=True)
    save_path = WEIGHTS_DIR / save_name

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
            if smoke_test and batch_idx >= 15:
                print("  [Smoke Test] Reached batch limit. Finishing epoch.")
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

        targets, preds, val_macro_f1 = evaluate(model, test_loader, device, num_classes, class_names, smoke_test=smoke_test)
        print(f"Epoch {epoch} Results | Train Loss: {epoch_loss:.4f} | Train Acc: {epoch_acc:.4f} | Val Macro F1: {val_macro_f1:.4f}")

        if val_macro_f1 > best_macro_f1:
            best_macro_f1 = val_macro_f1
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
            print(f"  [+] NEW BEST MODEL SAVED (Val Macro F1: {best_macro_f1:.4f}) -> {save_path.name}")
        else:
            patience_counter += 1
            print(f"  [-] No improvement in Val Macro F1. Early stopping counter: {patience_counter}/{patience}")

        if not smoke_test and patience_counter >= patience:
            print(f"\n[EARLY STOPPING] Validation Macro F1 did not improve for {patience} consecutive epochs. Stopping at Epoch {epoch}.")
            break

    print("\n" + "=" * 60)
    print("=== TRAINING COMPLETE - BEST CHECKPOINT SUMMARY ===")
    print(f"   Best Checkpoint Epoch: Epoch {best_epoch}")
    print(f"   Best Validation Macro F1: {best_macro_f1:.4f}")
    print(f"   Saved Checkpoint File: {save_path.resolve()}")
    print("=" * 60)

    print("\n=== PER-CLASS EVALUATION REPORT (BEST MODEL) ===")
    print(best_report)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Plant Disease Detection Vision Models")
    parser.add_argument(
        "--dataset",
        type=str,
        choices=["plantvillage", "plantvillage-hf", "plantdoc", "combined", "arecanut"],
        default="combined",
        help="Dataset to train on (plantvillage, plantvillage-hf, plantdoc, combined, or arecanut)"
    )
    parser.add_argument("--smoke-test", action="store_true", help="Run 1-epoch smoke test on small batch subset")
    parser.add_argument("--epochs", type=int, default=10, help="Max training epochs")
    parser.add_argument("--patience", type=int, default=3, help="Early stopping patience")
    args = parser.parse_args()

    run_training(dataset_type=args.dataset, smoke_test=args.smoke_test, epochs=args.epochs, patience=args.patience)
