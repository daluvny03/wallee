from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
import joblib
import tensorflow as tf
import json

app = FastAPI(title="Finance Forecast API")

# Load Model & Scalers
# Ensure these paths are correct relative to the main.py location
MODEL = tf.keras.models.load_model('models/forecast_model.keras')
SCALER_X = joblib.load('models/scaler_X.save')
SCALER_Y = joblib.load('models/scaler_y.save')

# Load pre-calculated ensemble forecast results
try:
    with open('models/ensemble_forecast_results.json', 'r') as f:
        ENSEMBLE_FORECAST_RESULTS = json.load(f)
except FileNotFoundError:
    raise RuntimeError("ensemble_forecast_results.json not found. Run the notebook to generate it.")

class PredictRequest(BaseModel):
    lag_1: float
    lag_2: float
    lag_3: float
    rolling_mean_7: float
    rolling_mean_30: float
    day_of_week: int
    month: int
    is_weekend: int
    mtd_progress: float
    transaction_count: int

@app.get("/")
def home():
    return {"message": "Finance Forecast API is running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/predict")
def predict(data: PredictRequest):
    """
    This endpoint returns the pre-calculated monthly ensemble forecast and its confidence interval.
    The input daily features are validated but not used to recompute the monthly forecast for this version.
    """
    try:
        # Although daily features are provided and validated via Pydantic,
        # for this specific request (monthly forecast + CI), we return the pre-calculated ensemble result.
        # If a daily prediction based on these inputs were needed, a different logic would apply here.
        return {
            "success": True,
            "message": "OK",
            "forecast_next_month": ENSEMBLE_FORECAST_RESULTS["forecast_next_month"],
            "confidence_lower": ENSEMBLE_FORECAST_RESULTS["confidence_lower"],
            "confidence_upper": ENSEMBLE_FORECAST_RESULTS["confidence_upper"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
