import os
import sys
import io
import torch
from PIL import Image
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from torchvision import transforms
import json
from pathlib import Path

# Add parent directory to Python path for imports
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.append(str(parent_dir))

try:
    from utilss.species_fetcher import fetch_species_names
    from utilss.dataset_manager import get_class_names_from_dataset
    from model import AnimalCNN
    from utilss.logger import log_correction
except ImportError as e:
    print(f"Import error: {e}")
    # Define fallback functions for deployment

    def fetch_species_names(predicted_class, top_n=3):
        return [predicted_class.title()]

    def get_class_names_from_dataset():
        return ["Bear", "Bird", "Cat", "Cow", "Deer", "Dog", "Dolphin",
                "Elephant", "Giraffe", "Horse", "Kangaroo", "Lion", "Panda",
                "Tiger", "Zebra"]

    def log_correction(filename, predicted, actual):
        pass

    # Simple model class for deployment
    class AnimalCNN:
        def __init__(self, num_classes):
            pass

# Initialize FastAPI
app = FastAPI(title="Animal Classification API", version="1.0.0")

# Allow frontend access via CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup device (CPU for Vercel)
device = torch.device("cpu")

# Initialize class names
try:
    class_names = get_class_names_from_dataset()
    num_classes = len(class_names)
except:
    # Fallback class names for deployment
    class_names = ["Bear", "Bird", "Cat", "Cow", "Deer", "Dog", "Dolphin",
                   "Elephant", "Giraffe", "Horse", "Kangaroo", "Lion", "Panda",
                   "Tiger", "Zebra"]
    num_classes = len(class_names)

if num_classes == 0:
    class_names = ["Bear", "Bird", "Cat", "Cow", "Deer", "Dog", "Dolphin",
                   "Elephant", "Giraffe", "Horse", "Kangaroo", "Lion", "Panda",
                   "Tiger", "Zebra"]
    num_classes = len(class_names)

# Load model lazily to reduce cold start time
model = None
model_loaded = False


def load_model():
    """Load model on first request to reduce package size"""
    global model, model_loaded
    if model_loaded:
        return model

    try:
        model = AnimalCNN(num_classes=num_classes).to(device)
        model_path = os.path.join(parent_dir, "outputs", "best_model.pth")

        if os.path.exists(model_path):
            model.load_state_dict(torch.load(model_path, map_location=device))
            model.eval()
            model_loaded = True
            print(f"✅ Model loaded with {num_classes} classes")
            return model
        else:
            print("❌ Model file not found")
            return None
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return None  # Image transform


transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
])

# Mount static files
try:
    frontend_path = os.path.join(parent_dir, "frontend")
    if os.path.exists(frontend_path):
        app.mount("/frontend", StaticFiles(directory=frontend_path),
                  name="frontend")
except Exception as e:
    print(f"Warning: Could not mount frontend directory: {e}")


@app.get("/", response_class=HTMLResponse)
async def serve_index():
    """Serve the main HTML page"""
    try:
        html_path = os.path.join(parent_dir, "frontend", "index.html")
        if os.path.exists(html_path):
            with open(html_path, "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read())
        else:
            return HTMLResponse(content="""
            <!DOCTYPE html>
            <html>
            <head><title>Animal Classifier</title></head>
            <body>
                <h1>Animal Classification API</h1>
                <p>API is running. Please upload the frontend files.</p>
                <p>Available endpoints:</p>
                <ul>
                    <li>POST /predict - Upload image for classification</li>
                    <li>GET /classes - Get available animal classes</li>
                    <li>POST /feedback - Submit classification feedback</li>
                </ul>
            </body>
            </html>
            """)
    except Exception as e:
        return HTMLResponse(content=f"<h1>Error loading page: {e}</h1>")


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    """Predict animal class from uploaded image"""
    # Load model on first request
    current_model = load_model()
    if current_model is None:
        return {"error": "Model not available. Please check deployment."}

    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        input_tensor = transform(image).unsqueeze(0).to(device)

        with torch.no_grad():
            output = current_model(input_tensor)
            pred_idx = output.argmax(dim=1).item()

        predicted_class = class_names[pred_idx]
        confidence = torch.softmax(output, dim=1)[0][pred_idx].item()

        def get_base_class(label: str):
            label = label.replace("_", " ")
            for keyword in ["Bear", "Cat", "Dog", "Deer", "Bird", "Cow", "Horse",
                            "Dolphin", "Elephant", "Giraffe", "Kangaroo", "Lion",
                            "Panda", "Tiger", "Zebra"]:
                if keyword in label:
                    return keyword
            return label

        base_class = get_base_class(predicted_class)
        breed_suggestions = fetch_species_names(predicted_class, top_n=3)

        return {
            "prediction": predicted_class,
            "base_class": base_class,
            "confidence": round(confidence, 4),
            "breeds": breed_suggestions
        }
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error processing image: {str(e)}")


@app.post("/feedback")
async def feedback(
    file: UploadFile = File(...),
    predicted: str = Form(...),
    actual: str = Form(...)
):
    """Submit feedback for model improvement"""
    try:
        contents = await file.read()
        filename = file.filename

        # Log the correction (simplified for deployment)
        log_correction(filename, predicted, actual)

        return {"message": "✅ Feedback received and logged."}
    except Exception as e:
        return {"message": f"⚠️ Error processing feedback: {e}"}


@app.get("/classes")
async def get_class_names():
    """Return available animal classes"""
    return {"classes": class_names}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_loaded": model_loaded,
        "num_classes": num_classes,
        "classes": class_names[:10]  # Show first 10 classes only
    }

# For Vercel deployment
app_handler = app
