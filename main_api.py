import os
import io
import sys
import shutil
import torch
from PIL import Image
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from torchvision import transforms

from utilss.species_fetcher import fetch_species_names
from utilss.dataset_manager import get_class_names_from_dataset
from model import AnimalCNN
from utilss.logger import log_correction

# Initialize FastAPI
app = FastAPI()

# Allow frontend access via CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve HTML UI
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")


@app.get("/", response_class=HTMLResponse)
async def serve_index():
    with open("frontend/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

# 🔍 Setup device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 🚀 Initialize class names once at startup
print("🔍 Scanning dataset folder for class names...")
class_names = get_class_names_from_dataset()
num_classes = len(class_names)
print(f"✅ Found {num_classes} animal classes")

if num_classes == 0:
    print("❌ No classes found in dataset folder")
    print("➡️ Please ensure the dataset folder contains subfolders for each animal class")
    class_names = ["Unknown"]
    num_classes = 1

# 🧠 Load model
model = AnimalCNN(num_classes=num_classes).to(device)
model_path = "outputs/best_model.pth"

try:
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()
    print(f"✅ Model loaded with {num_classes} classes")
except RuntimeError as e:
    print(f"❌ Error loading model: {e}")
    print("➡️ Please retrain using: python train.py with correct class count.")
    model = None  # Avoid using an invalid model

# 🖼️ Image transform
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
])


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    if model is None:
        return {"error": "Model not available. Please retrain first."}

    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert("RGB")
    input_tensor = transform(image).unsqueeze(0).to(device)

    with torch.no_grad():
        output = model(input_tensor)
        pred_idx = output.argmax(dim=1).item()

    predicted_class = class_names[pred_idx]
    confidence = torch.softmax(output, dim=1)[0][pred_idx].item()

    def get_base_class(label: str):
        label = label.replace("_", " ")
        for keyword in ["Bear", "Cat", "Dog", "Deer", "Bird", "Cow", "Horse", "Dolphin", "Elephant", "Giraffe", "Kangaroo", "Lion", "Panda", "Polar", "Sloth", "Sun", "Tiger", "Zebra"]:
            if keyword in label:
                return keyword
        return label

    base_class = get_base_class(predicted_class)
    breed_suggestions = fetch_species_names(predicted_class, top_n=3)

    print(
        f"Predicted: {predicted_class} | Base: {base_class} | Confidence: {round(confidence, 4)}")

    return {
        "prediction": predicted_class,
        "base_class": base_class,
        "confidence": round(confidence, 4),
        "breeds": breed_suggestions
    }


@app.post("/feedback")
async def feedback(
    file: UploadFile = File(...),
    predicted: str = Form(...),
    actual: str = Form(...)
):
    contents = await file.read()
    filename = file.filename
    save_path = os.path.join("dataset", actual)
    os.makedirs(save_path, exist_ok=True)

    with open(os.path.join(save_path, filename), "wb") as f:
        f.write(contents)

    log_correction(filename, predicted, actual)

    try:
        import subprocess
        subprocess.run([sys.executable, "feedback_trainer.py"], check=True)
        return {"message": "✅ Feedback received and model updated."}
    except Exception as e:
        return {"message": f"⚠️ Feedback saved, but model update failed: {e}"}


@app.get("/classes")
async def get_class_names():
    """Return the pre-loaded class names (no scanning required)"""
    return {"classes": class_names}
