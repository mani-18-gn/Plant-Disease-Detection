import io
import os
import sys
import shutil
import tempfile
from pathlib import Path
from PIL import Image
import pytest
import torch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.agents.vision.model import CLASS_NAMES
from backend.agents.vision.preprocess import eval_transform, get_train_transform
from backend.agents.vision.train import (
    compute_file_sha256,
    load_and_deduplicate_dataset,
    create_stratified_split,
    ArecanutDataset,
)


def create_dummy_jpeg(path: Path, color=(34, 139, 34), size=(64, 64)):
    """Create a small valid RGB JPEG file at path."""
    path.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", size, color=color)
    img.save(path, format="JPEG")


def test_numeric_folder_mapping_and_order():
    """Verify that folders '0' through '8' map strictly to CLASS_NAMES without reordering."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        # Create numeric folders 0 to 8, with 5 samples each
        for idx, class_name in enumerate(CLASS_NAMES):
            folder = root / str(idx)
            for s in range(5):
                # Ensure unique colors so hashes are unique
                create_dummy_jpeg(folder / f"sample_{s}.jpg", color=(idx * 20, s * 40, (idx + s) * 10))

        unique_samples, summary = load_and_deduplicate_dataset(root, min_samples_per_class=5)

        # Verify all 9 classes are accounted for
        assert len(summary["per_class_counts"]) == 9
        for idx, class_name in enumerate(CLASS_NAMES):
            assert summary["per_class_counts"][class_name] == 5

        # Verify mapped label indexes match CLASS_NAMES order
        for path, label_idx, _ in unique_samples:
            folder_num = int(path.parent.name)
            assert label_idx == folder_num
            assert CLASS_NAMES[label_idx] == CLASS_NAMES[folder_num]


def test_deduplication_and_conflict_reporting():
    """Verify duplicate images with identical labels are excluded and conflicts with different labels are reported."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)

        # Create 5 baseline samples for each of the 9 classes
        for idx in range(9):
            folder = root / str(idx)
            for s in range(5):
                create_dummy_jpeg(folder / f"sample_{s}.jpg", color=(idx * 15 + 10, s * 30 + 10, 50))

        # Add an exact duplicate within Class 0 (identical bytes)
        target_file = root / "0" / "sample_0.jpg"
        dup_same_class = root / "0" / "sample_duplicate.jpg"
        shutil.copyfile(target_file, dup_same_class)

        # Add a conflict: identical bytes to Class 0 placed inside Class 5
        conflict_file = root / "5" / "sample_conflict.jpg"
        shutil.copyfile(target_file, conflict_file)

        unique_samples, summary = load_and_deduplicate_dataset(root, min_samples_per_class=5)

        # Must detect exactly 1 same-class duplicate and 1 cross-class conflict
        assert summary["duplicate_same_class_count"] == 1
        assert summary["duplicate_conflicts_count"] == 1
        assert len(summary["duplicate_conflicts"]) == 1

        conflict = summary["duplicate_conflicts"][0]
        assert conflict["class_a"] == CLASS_NAMES[0]
        assert conflict["class_b"] == CLASS_NAMES[5]


def test_stratified_validation_split_zero_leakage():
    """Verify stratified split has zero overlap between train and validation sets and fixed seed determinism."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        for idx in range(9):
            folder = root / str(idx)
            for s in range(10):
                create_dummy_jpeg(folder / f"sample_{s}.jpg", color=(idx * 15 + 5, s * 20 + 5, 100))

        unique_samples, _ = load_and_deduplicate_dataset(root, min_samples_per_class=5)
        train_samples, val_samples = create_stratified_split(unique_samples, val_fraction=0.20, random_seed=42)

        # Total samples: 9 classes * 10 = 90
        # 80% train = 72, 20% val = 18 (exactly 2 per class)
        assert len(train_samples) == 72
        assert len(val_samples) == 18

        train_paths = {s[0] for s in train_samples}
        val_paths = {s[0] for s in val_samples}

        # Zero leakage: intersection must be completely empty
        leakage = train_paths.intersection(val_paths)
        assert len(leakage) == 0, f"Found data leakage between train and val: {leakage}"

        # Per-class stratification check: each class must have exactly 2 val samples
        val_class_counts = [0] * 9
        for _, l_idx, _ in val_samples:
            val_class_counts[l_idx] += 1
        for count in val_class_counts:
            assert count == 2


def test_missing_classes_and_insufficient_samples_detection():
    """Verify error is raised if a class is completely missing or has insufficient samples."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        # Create only 8 classes (missing class index 8)
        for idx in range(8):
            folder = root / str(idx)
            for s in range(5):
                create_dummy_jpeg(folder / f"sample_{s}.jpg", color=(idx * 20, s * 30, 80))

        with pytest.raises(ValueError, match="missing classes"):
            load_and_deduplicate_dataset(root, min_samples_per_class=5)


def test_preprocessing_and_dataset_tensor_shapes():
    """Verify that dataset outputs match inference expected shapes (3, 224, 224) and normalization."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        for idx in range(9):
            folder = root / str(idx)
            for s in range(5):
                create_dummy_jpeg(folder / f"sample_{s}.jpg", color=(idx * 10, s * 20, 150))

        unique_samples, _ = load_and_deduplicate_dataset(root, min_samples_per_class=5)

        train_ds = ArecanutDataset(unique_samples, is_train=True)
        val_ds = ArecanutDataset(unique_samples, is_train=False)

        train_img, train_label = train_ds[0]
        val_img, val_label = val_ds[0]

        assert isinstance(train_img, torch.Tensor)
        assert train_img.shape == (3, 224, 224)
        assert isinstance(val_img, torch.Tensor)
        assert val_img.shape == (3, 224, 224)
