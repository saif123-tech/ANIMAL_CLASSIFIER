import os
import torch
import shutil
import subprocess
from torchvision import transforms
from PIL import Image
from model import AnimalCNN
from data.dataloader import AnimalDataset
from torch.nn.functional import softmax
from utilss.logger import log_correction

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load model
model = AnimalCNN(num_classes=15).to(device)
model.load_state_dict(torch.load("outputs/best_model.pth"))
model.eval()

# Load class names
dataset = AnimalDataset("dataset", transform=None)
class_names = list(dataset.class_map.keys())

# Load and preprocess image
image_path = input("📷 Enter path to test image: ").strip()
assert os.path.exists(image_path), f"File not found: {image_path}"

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])
image = Image.open(image_path).convert("RGB")
input_tensor = transform(image).unsqueeze(0).to(device)

# Predict
with torch.no_grad():
    output = model(input_tensor)
    probs = softmax(output, dim=1)
    top_probs, top_idxs = torch.topk(probs, 3)

# Display top predictions
print("\n🔍 Top Predictions:")
for i in range(3):
    print(f"{i+1}. {class_names[top_idxs[0][i]]} ({top_probs[0][i]*100:.2f}%)")

predicted_class = class_names[top_idxs[0][0]]
print(f"\n✅ Final Prediction: {predicted_class}")

# Ask for correction
true_class = input(f"🙋 Enter correct class or 'skip': ").strip()
if true_class.lower() != "skip":
    if true_class not in class_names:
        print("❌ Invalid class. Aborting.")
        exit()

    # Save image to correct class folder
    corrected_path = os.path.join("dataset", true_class)
    os.makedirs(corrected_path, exist_ok=True)
    shutil.copy(image_path, os.path.join(
        corrected_path, os.path.basename(image_path)))

    # Log correction
    log_correction(image_path, predicted_class, true_class)

    print("📥 Image saved and correction logged.")

    # ✅ Automatically run feedback trainer
    print("🔁 Updating model with feedback...")
    subprocess.Popen(["python", "feedback_trainer.py"])

else:
    print("⏭️ Skipped correction. No model update.")
