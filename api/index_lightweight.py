import os
import sys
import io
import torch
from PIL import Image
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
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

# Initialize class names with fallback
try:
    class_names = get_class_names_from_dataset()
    num_classes = len(class_names)
except:
    class_names = ["Bear", "Bird", "Cat", "Cow", "Deer", "Dog", "Dolphin",
                   "Elephant", "Giraffe", "Horse", "Kangaroo", "Lion", "Panda",
                   "Tiger", "Zebra"]
    num_classes = len(class_names)

if num_classes == 0:
    class_names = ["Bear", "Bird", "Cat", "Cow", "Deer", "Dog", "Dolphin",
                   "Elephant", "Giraffe", "Horse", "Kangaroo", "Lion", "Panda",
                   "Tiger", "Zebra"]
    num_classes = len(class_names)

# Image transform
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
])

# Demo mode - return simulated results when model is not available
DEMO_MODE = True


def get_demo_prediction(image_name):
    """Return demo predictions based on common image names"""
    image_name = image_name.lower()

    if any(keyword in image_name for keyword in ['dog', 'puppy', 'canine']):
        return "Dog", "Dog", 0.92, ["Golden Retriever", "Labrador", "German Shepherd"]
    elif any(keyword in image_name for keyword in ['cat', 'kitten', 'feline']):
        return "Cat", "Cat", 0.89, ["Persian Cat", "Siamese Cat", "Maine Coon"]
    elif any(keyword in image_name for keyword in ['bird', 'eagle', 'parrot']):
        return "Bird", "Bird", 0.85, ["Eagle", "Parrot", "Owl"]
    elif any(keyword in image_name for keyword in ['lion', 'tiger', 'big cat']):
        return "Lion", "Lion", 0.94, ["African Lion", "Asiatic Lion"]
    else:
        return "Dog", "Dog", 0.75, ["Mixed Breed", "Unknown Breed"]


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
            <head>
                <title>Animal Classifier - Demo Mode</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; }
                    .demo-banner { background: #fff3cd; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
                </style>
            </head>
            <body>
                <div class="demo-banner">
                    ⚠️ <strong>Demo Mode:</strong> Full model not loaded. API will return simulated results.
                </div>
                <h1>🐾 Animal Classification API</h1>
                <p>Upload an animal image to get classification results.</p>
                <p><strong>Available endpoints:</strong></p>
                <ul>
                    <li>POST /predict - Upload image for classification</li>
                    <li>GET /classes - Get available animal classes</li>
                    <li>POST /feedback - Submit classification feedback</li>
                    <li>GET /health - API health check</li>
                </ul>
            </body>
            </html>
            """)
    except Exception as e:
        return HTMLResponse(content=f"<h1>Error loading page: {e}</h1>")


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    """Predict animal class from uploaded image"""
    try:
        contents = await file.read()
        filename = file.filename or "unknown.jpg"

        if DEMO_MODE:
            # Return demo prediction
            predicted_class, base_class, confidence, breeds = get_demo_prediction(
                filename)
            return {
                "prediction": predicted_class,
                "base_class": base_class,
                "confidence": confidence,
                "breeds": breeds,
                "demo_mode": True,
                "message": "Demo mode - simulated results"
            }

        # If model was available, real prediction would go here
        return {"error": "Model not available in this deployment"}

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

        return {"message": "✅ Feedback received and logged (demo mode)."}
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
        "demo_mode": DEMO_MODE,
        "model_loaded": False,
        "num_classes": num_classes,
        "classes": class_names[:10]
    }

# For Vercel deployment
app_handler = app
