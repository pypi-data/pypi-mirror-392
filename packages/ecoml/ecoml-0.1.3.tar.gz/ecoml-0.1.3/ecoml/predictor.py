import os
from datetime import datetime

import joblib
import pandas as pd
import torch

# =========================================================
# PATHS
# =========================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_PATH = os.path.join(os.path.dirname(BASE_DIR), "data", "emissions_log.csv")

# ✅ Models live in ecoml/model/
SCALER_PATH = os.path.join(BASE_DIR, "model", "scaler.pkl")
RECOMMENDER_PATH = os.path.join(BASE_DIR, "model", "hardware_recommender_model.pkl")

LOG_PATH = os.path.join(os.path.dirname(BASE_DIR), "data", "recommendations_log.csv")

# =========================================================
# ✨ MANUAL CLASS LABEL MAP
# =========================================================
LABEL_MAP = {
    0: "CPU Efficient — No GPU Needed",
    1: "GPU Efficient — Continue GPU Usage",
    2: "Upgrade Recommended — Mid-range GPU",
    3: "High-End GPU Required for heavy workloads",
}

# =========================================================
# LOAD MODELS
# =========================================================
if not os.path.exists(SCALER_PATH) or not os.path.exists(RECOMMENDER_PATH):
    raise FileNotFoundError(
        f"Scaler or recommender model not found in {os.path.join(BASE_DIR, 'model')}"
    )

scaler = joblib.load(SCALER_PATH)
recommender = joblib.load(RECOMMENDER_PATH)

# =========================================================
# GPU CHECK
# =========================================================
GPU_AVAILABLE = torch.cuda.is_available()

print("\n=============================")
print("🟢 GPU Available" if GPU_AVAILABLE else "⚠ No GPU detected → CPU only")
print("=============================\n")

# =========================================================
# GET CLEAN LIVE INPUT
# =========================================================
def get_live_data():
    df = pd.read_csv(DATA_PATH)

    latest = df.tail(1).copy()

    # keep numeric only
    numeric = latest.select_dtypes(include=["number"])
    latest = numeric.copy()

    needed = scaler.feature_names_in_
    latest = latest.reindex(columns=needed, fill_value=0)

    scaled = scaler.transform(latest)
    return scaled, latest


# =========================================================
# LOGGING
# =========================================================
def save_log(rec: str):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "recommendation": rec,
    }
    df = pd.DataFrame([entry])

    if not os.path.exists(LOG_PATH):
        df.to_csv(LOG_PATH, index=False)
    else:
        df.to_csv(LOG_PATH, mode="a", header=False, index=False)


# =========================================================
# PREDICT
# =========================================================
def run_prediction():
    X_scaled, raw = get_live_data()

    pred_int = int(recommender.predict(X_scaled)[0])
    rec = LABEL_MAP.get(pred_int, f"Unknown Class {pred_int}")

    print("🔍 INPUT:", raw.to_dict("records")[0])
    print("⚡ RECOMMENDATION:", rec, "\n")

    save_log(rec)


# =========================================================
# AUTO EXECUTE WHEN RUN AS SCRIPT
# =========================================================
if __name__ == "__main__":
    run_prediction()
