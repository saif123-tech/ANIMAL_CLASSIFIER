import os
import json
import random
import torch
from model import AnimalCNN
from data.dataloader import AnimalDataset
from torchvision import transforms
from torch.utils.data import DataLoader, Subset
from torch import nn, optim
from utilss.logger import LOG_PATH

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 🔧 Transform (same as original training)
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
])

# 🐾 Load full dataset
dataset = AnimalDataset("dataset", transform=transform)
class_names = list(dataset.class_map.keys())

# 📥 Load recent corrections from the log
if not os.path.exists(LOG_PATH):
    print("⚠ No correction log found.")
    exit()

with open(LOG_PATH, "r") as f:
    logs = json.load(f)

if not logs:
    print("⚠ Correction log is empty.")
    exit()

# 🧠 Take last 5 corrections
corrected_paths = [entry["image"] for entry in logs[-5:]]

# 🔍 Find dataset indices for corrected samples
corrected_indices = []
for idx, (img_path, _) in enumerate(dataset.samples):
    if any(os.path.basename(img_path) in path for path in corrected_paths):
        corrected_indices.append(idx)

if not corrected_indices:
    print("⚠ No corrected samples found in dataset.")
    exit()

# 🔁 Add 30 random replay samples (excluding corrected)
all_indices = list(range(len(dataset)))
replay_pool = [i for i in all_indices if i not in corrected_indices]
replay_indices = random.sample(replay_pool, k=min(30, len(replay_pool)))

# 📊 Combine
final_indices = corrected_indices + replay_indices
train_subset = Subset(dataset, final_indices)

# 🧠 Load existing trained model
model = AnimalCNN(num_classes=len(class_names)).to(device)
model.load_state_dict(torch.load("outputs/best_model.pth"))
model.train()

# 🧮 Loss and Optimizer
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=1e-4)

# 🔁 Fine-tune for a few epochs
loader = DataLoader(train_subset, batch_size=16, shuffle=True)
for epoch in range(3):
    total_loss, correct, total = 0, 0, 0
    for imgs, labels in loader:
        imgs, labels = imgs.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(imgs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        total_loss += loss.item() * imgs.size(0)
        correct += (outputs.argmax(1) == labels).sum().item()
        total += imgs.size(0)
    print(
        f"📘 Epoch {epoch+1} | Loss: {total_loss/total:.4f} | Accuracy: {correct/total:.4f}")

# 💾 Overwrite existing model
save_path = "outputs/best_model.pth"
torch.save(model.state_dict(), save_path)

print(f"✅ Model updated and saved to {save_path}")
