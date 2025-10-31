import torch
from torch.utils.data import DataLoader, random_split
from torchvision import transforms
from data.dataloader import AnimalDataset
from model import AnimalCNN
from train import train
from evaluate import evaluate
from collections import Counter
from torch.optim.lr_scheduler import ReduceLROnPlateau

# 🧠 Use CUDA if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"\n🖥️  Using device: {device}\n")

# 🧪 Transform with augmentation and normalization
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(15),
    transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])

# 📦 Load dataset
dataset = AnimalDataset("dataset", transform)
class_names = list(dataset.class_map.keys())
print(f"📦 Loaded {len(dataset)} images across {len(class_names)} classes.")

# 🔀 Split dataset: 70% train, 15% val, 15% test
train_size = int(0.7 * len(dataset))
val_size = int(0.15 * len(dataset))
test_size = len(dataset) - train_size - val_size
train_set, val_set, test_set = random_split(
    dataset, [train_size, val_size, test_size])

# 📤 DataLoaders
train_loader = DataLoader(train_set, batch_size=64, shuffle=True)
val_loader = DataLoader(val_set, batch_size=64, shuffle=False)
test_loader = DataLoader(test_set, batch_size=64, shuffle=False)

# 🧮 Compute safe class weights
targets = [label for _, label in dataset.samples]
label_counts = Counter(targets)
num_classes = len(class_names)

weights = torch.ones(num_classes)

# Assign inverse frequency weights
for class_idx in range(num_classes):
    count = label_counts.get(class_idx, 0)
    weights[class_idx] = 1.0 / count if count > 0 else 0.0

# Replace 0 weights (for empty classes) with mean
non_zero_weights = weights[weights != 0]
mean_weight = non_zero_weights.mean() if len(non_zero_weights) > 0 else 1.0
weights[weights == 0] = mean_weight

# Normalize
weights = weights / weights.sum()
weights = weights.to(device)

# 🧠 Initialize model, loss, optimizer, scheduler
model = AnimalCNN(num_classes=num_classes).to(device)
loss_fn = torch.nn.CrossEntropyLoss(weight=weights)
optimizer = torch.optim.Adam(model.parameters(), lr=0.0001)
scheduler = ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=3)

# 🚀 Train
print("\n🚀 Starting training...\n")
train(model, train_loader, val_loader, loss_fn, optimizer, scheduler, device)

# 📊 Final evaluation on test set
print("\n📊 Evaluating model...\n")
evaluate(model, test_loader, class_names)
