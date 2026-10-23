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

from backend.agents.vision.model import ArecanutCNN, CLASS_NAMES, FOLDER_TO_CLASS, LOW_VOLUME_CLASSES
from backend.agents.vision.preprocess import eval_transform, get_train_transform

DATASET_ROOT = Path(__file__).resolve().parents[3] / "data" / "Arecanut_dataset"
WEIGHTS_DIR = Path(__file__).parent / "weights"


class ArecanutDataset(Dataset):
    """
    Custom PyTorch Dataset for Arecanut images.
    Maps raw folder names ('bud borer', 'Stem_bleeding') to normalized class indexes.
    """

    def __init__(self, root_dir: Path, is_train: bool = True, max_samples_per_class: int | None = None):
        self.root_dir = root_dir
        self.is_train = is_train
        self.samples = []

        class_to_idx = {name: i for i, name in enumerate(CLASS_NAMES)}

        for folder_name in sorted(os.listdir(root_dir)):
            folder_path = root_dir / folder_name
            if not folder_path.is_dir():
                continue

            normalized_class = FOLDER_TO_CLASS.get(folder_name)
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


def compute_class_weights(dataset: ArecanutDataset) -> torch.Tensor:
    """
    Compute inverse-frequency class weights across all 9 classes
    to prevent majority classes (Mahali_Koleroga, Healthy_Nut) from dominating loss.
    """
    counts = [0] * len(CLASS_NAMES)
    for _, label_idx, _ in dataset.samples:
        counts[label_idx] += 1

    total = len(dataset)
    num_classes = len(CLASS_NAMES)

    # Inverse frequency formula: total / (num_classes * count)
    weights = [total / (num_classes * max(c, 1)) for c in counts]
    print("\n--- CLASS DISTRIBUTION & COMPUTED WEIGHTS ---")
    for i, name in enumerate(CLASS_NAMES):
        print(f"  {name:<22} | Count: {counts[i]:<5} | Loss Weight: {weights[i]:.4f}")

    return torch.tensor(weights, dtype=torch.float32)


def evaluate(model: nn.Module, test_loader: DataLoader, device: torch.device, smoke_test: bool = False):
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

    _, _, macro_f1, _ = precision_recall_fscore_support(
        all_targets,
        all_preds,
        labels=list(range(len(CLASS_NAMES))),
        average="macro",
        zero_division=0,
    )

    return all_targets, all_preds, round(float(macro_f1), 4)


def run_training(
    smoke_test: bool = False,
    epochs: int = 30,
    patience: int = 3,
    batch_size: int = 32,
    lr: float = 1e-4,
    freeze_backbone: bool = True,
    unfreeze_at_epoch: int | None = 5,
):
    """
    Training pipeline with:
    - Backbone freezing (stage 1) and unfreezing for fine-tuning (stage 2)
    - Inverse-frequency weighted CrossEntropyLoss across all 9 classes
    - Validation Macro F1 evaluation after each epoch
    - Best model checkpoint saving based on Validation Macro F1
    - Early stopping if Validation Macro F1 fails to improve for `patience` epochs
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"\n[...] Starting Vision Agent Training (Device: {device}, Smoke Test: {smoke_test})")
    print(f"    Config: Max Epochs={epochs}, Early Stopping Patience={patience}, Freeze Backbone={freeze_backbone}")

    sample_cap = 20 if smoke_test else None
    train_dataset = ArecanutDataset(DATASET_ROOT / "train", is_train=True, max_samples_per_class=sample_cap)
    test_dataset = ArecanutDataset(DATASET_ROOT / "test", is_train=False, max_samples_per_class=sample_cap)

    class_weights = compute_class_weights(train_dataset).to(device)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=0)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False, num_workers=0)

    # Initialize model with frozen backbone
    model = ArecanutCNN(num_classes=len(CLASS_NAMES), pretrained=True, freeze_backbone=freeze_backbone).to(device)
    criterion = nn.CrossEntropyLoss(weight=class_weights)
    optimizer = torch.optim.AdamW(filter(lambda p: p.requires_grad, model.parameters()), lr=lr, weight_decay=1e-2)

    total_epochs = 1 if smoke_test else epochs

    best_macro_f1 = -1.0
    best_epoch = 0
    patience_counter = 0
    best_report = ""

    WEIGHTS_DIR.mkdir(parents=True, exist_ok=True)
    save_path = WEIGHTS_DIR / "arecanut_cnn.pt"

    for epoch in range(1, total_epochs + 1):
        # Stage 2 Fine-Tuning: Unfreeze backbone if unfreeze_at_epoch reached
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
            if smoke_test and batch_idx >= 30:
                print("  [Smoke Test] Reached batch limit (30 batches). Stopping epoch early.")
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

            if (batch_idx + 1) % 50 == 0:
                print(f"  Batch {batch_idx + 1}/{len(train_loader)} | Loss: {loss.item():.4f}")

        epoch_loss = running_loss / max(total, 1)
        epoch_acc = correct / max(total, 1)

        # Validation at end of epoch
        targets, preds, val_macro_f1 = evaluate(model, test_loader, device, smoke_test=smoke_test)
        print(f"Epoch {epoch} Results | Train Loss: {epoch_loss:.4f} | Train Acc: {epoch_acc:.4f} | Val Macro F1: {val_macro_f1:.4f}")

        # Best Model Checkpointing based on Validation Macro F1
        if val_macro_f1 > best_macro_f1:
            best_macro_f1 = val_macro_f1
            best_epoch = epoch
            patience_counter = 0
            torch.save(model.state_dict(), save_path)

            best_report = classification_report(
                targets,
                preds,
                labels=list(range(len(CLASS_NAMES))),
                target_names=CLASS_NAMES,
                digits=4,
                zero_division=0,
            )
            print(f"  [+] NEW BEST MODEL SAVED (Val Macro F1: {best_macro_f1:.4f}) -> {save_path.name}")
        else:
            patience_counter += 1
            print(f"  [-] No improvement in Val Macro F1. Early stopping counter: {patience_counter}/{patience}")

        if not smoke_test and patience_counter >= patience:
            print(f"\n[EARLY STOPPING] Validation Macro F1 did not improve for {patience} consecutive epochs. Stopping training early at Epoch {epoch}.")
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
    parser = argparse.ArgumentParser(description="Train Vision Agent Arecanut CNN")
    parser.add_argument("--smoke-test", action="store_true", help="Run 1-epoch smoke test on small batch subset")
    parser.add_argument("--epochs", type=int, default=30, help="Max training epochs")
    parser.add_argument("--patience", type=int, default=3, help="Early stopping patience (epochs without Val Macro F1 improvement)")
    args = parser.parse_args()

    run_training(smoke_test=args.smoke_test, epochs=args.epochs, patience=args.patience)
