# Vision Agent Model Training Handoff Guide

This document contains step-by-step instructions for training the 9-class Arecanut CNN disease classification model (`ArecanutCNN`) using PyTorch.

---

## 1. Dataset Placement

Ensure the dataset is located at `data/Arecanut_dataset/` relative to the workspace root:

```text
Areca-Agent/
└── data/
    └── Arecanut_dataset/
        ├── train/
        │   ├── bud borer/          (144 images)
        │   ├── healthy_foot/       (50 images)
        │   ├── Healthy_Leaf/       (604 images)
        │   ├── Healthy_Nut/        (1,886 images)
        │   ├── Healthy_Trunk/      (1,432 images)
        │   ├── Mahali_Koleroga/    (2,563 images)
        │   ├── stem cracking/      (540 images)
        │   ├── Stem_bleeding/      (151 images)
        │   └── yellow leaf disease/ (1,477 images)
        └── test/
            └── [same 9 class subfolders] (2,216 total test images)
```

> **Note on Folder Names:** Folder names are mapped automatically inside `train.py` to internal normalized labels (`bud_borer`, `healthy_foot`, `healthy_leaf`, `healthy_nut`, `healthy_trunk`, `mahali_koleroga`, `stem_cracking`, `stem_bleeding`, `yellow_leaf_disease`).

---

## 2. Environment Setup

1. Install Python dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
2. **GPU Acceleration (Recommended):**
   If training on a machine with an NVIDIA GPU, override the CPU PyTorch build with the CUDA-enabled build matching your CUDA driver:
   ```bash
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
   ```

---

## 3. Training Command & Parameters

Execute full training from the repository root:

```bash
python -m backend.agents.vision.train --epochs 30 --patience 3
```

### Key Training Mechanisms Built Into `train.py`:
- **Backbone Freezing:** MobileNetV2 pretrained backbone is frozen for initial epochs to train the classification head, then unfrozen for fine-tuning.
- **Class Imbalance Handling:** Uses inverse-frequency `nn.CrossEntropyLoss(weight=class_weights)` across all 9 classes, plus specialized heavy data augmentation (`RandomVerticalFlip`, `RandomRotation(30)`, `RandomAffine`, `ColorJitter`) for the low-volume classes.
- **Validation Macro F1 Checkpointing:** Evaluates validation Macro F1 score after every epoch and saves the checkpoint to `backend/agents/vision/weights/arecanut_cnn.pt` **only** when validation Macro F1 reaches an all-time high.
- **Early Stopping:** Stops training automatically if validation Macro F1 does not improve for 3 consecutive epochs (`patience=3`).

---

## 4. Expected Performance & Runtime

- **CPU Runtime:** ~22 minutes total for 30 epochs (~45s per epoch).
- **GPU Runtime:** ~2–4 minutes total.

---

## 5. Required Handoff Deliverables

When training finishes, please report back:
1. **Checkpoint File:** Send back the generated weight file [`backend/agents/vision/weights/arecanut_cnn.pt`](file:///E:/Areca-Agent/backend/agents/vision/weights/arecanut_cnn.pt).
2. **Console Output Log:** Send back the complete console output, which includes:
   - Best checkpoint epoch number.
   - Best Validation Macro F1 score achieved.
   - Full per-class Precision / Recall / F1-score / Support report table.

---

## 6. Class Imbalance Awareness Notice

The dataset has severe class imbalance:
- `healthy_foot`: 63 images total (50 train / 13 test)
- `bud_borer`: 180 images total (144 train / 36 test)
- `stem_bleeding`: 189 images total (151 train / 38 test)
- `Mahali_Koleroga`: 3,204 images total (2,563 train / 641 test)

Lower precision/recall scores on `healthy_foot`, `bud_borer`, and `stem_bleeding` are **expected** due to raw sample scarcity and should be reported honestly in the final metrics table.
