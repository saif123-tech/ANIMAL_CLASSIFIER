import json
import os
from datetime import datetime

LOG_PATH = "outputs/correction_log.json"
os.makedirs("outputs", exist_ok=True)


def log_correction(image_path, predicted, actual):
    log = []
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, "r") as f:
            log = json.load(f)
    log.append({
        "image": image_path,
        "predicted": predicted,
        "actual": actual,
        "timestamp": str(datetime.now())
    })
    with open(LOG_PATH, "w") as f:
        json.dump(log, f, indent=2)
