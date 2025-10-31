# model.py
import torch.nn as nn
from torchvision import models


class AnimalCNN(nn.Module):
    def __init__(self, num_classes):
        super(AnimalCNN, self).__init__()
        self.base_model = models.resnet18(
            weights=models.ResNet18_Weights.DEFAULT)

        # 🔓 Unfreeze only layer4 for Grad-CAM to access gradients
        for name, param in self.base_model.named_parameters():
            param.requires_grad = "layer4" in name

        # 🔁 Replace the classification head
        self.base_model.fc = nn.Sequential(
            nn.Linear(self.base_model.fc.in_features, 256),
            nn.ReLU(),
            nn.Dropout(0.4),
            nn.Linear(256, num_classes)
        )

    def forward(self, x):
        return self.base_model(x)
