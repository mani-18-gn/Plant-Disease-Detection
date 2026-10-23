import torch
import torch.nn as nn
from torchvision import models

# Exact 9 normalized class names matching the dataset folders
CLASS_NAMES = [
    "bud_borer",
    "healthy_foot",
    "healthy_leaf",
    "healthy_nut",
    "healthy_trunk",
    "mahali_koleroga",
    "stem_cracking",
    "stem_bleeding",
    "yellow_leaf_disease",
]

# Raw dataset folder name to normalized internal class name mapping
FOLDER_TO_CLASS = {
    "bud borer": "bud_borer",
    "healthy_foot": "healthy_foot",
    "Healthy_Leaf": "healthy_leaf",
    "Healthy_Nut": "healthy_nut",
    "Healthy_Trunk": "healthy_trunk",
    "Mahali_Koleroga": "mahali_koleroga",
    "stem cracking": "stem_cracking",
    "Stem_bleeding": "stem_bleeding",
    "yellow leaf disease": "yellow_leaf_disease",
}

# Low-volume classes that require heavier data augmentation
LOW_VOLUME_CLASSES = ["healthy_foot", "bud_borer", "stem_bleeding"]


class ArecanutCNN(nn.Module):
    """
    CNN Architecture for 9-class Arecanut disease classification.
    Uses MobileNetV2 pretrained backbone with custom FC classification head
    (256 hidden units, BatchNorm, 0.5 Dropout, Softmax over 9 classes).
    Supports explicit backbone freezing for initial head training and unfreezing for fine-tuning.
    """

    def __init__(self, num_classes: int = len(CLASS_NAMES), pretrained: bool = True, freeze_backbone: bool = True):
        super().__init__()
        # Load MobileNetV2 backbone
        weights = models.MobileNet_V2_Weights.DEFAULT if pretrained else None
        self.backbone = models.mobilenet_v2(weights=weights)

        # Replace classification head
        in_features = self.backbone.classifier[1].in_features
        self.backbone.classifier = nn.Sequential(
            nn.Linear(in_features, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(256, num_classes),
        )

        # Freeze entire backbone if requested (transfer learning stage 1)
        if pretrained and freeze_backbone:
            self.freeze_backbone()

    def freeze_backbone(self):
        """Freeze ALL parameters in the feature extraction backbone."""
        for param in self.backbone.features.parameters():
            param.requires_grad = False

    def unfreeze_backbone(self, unfreeze_last_n_layers: int | None = None):
        """
        Unfreeze backbone parameters for fine-tuning.
        If unfreeze_last_n_layers is specified, unfreezes only the last N feature blocks.
        """
        if unfreeze_last_n_layers is not None:
            for param in self.backbone.features[-unfreeze_last_n_layers:].parameters():
                param.requires_grad = True
        else:
            for param in self.backbone.features.parameters():
                param.requires_grad = True

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.backbone(x)
