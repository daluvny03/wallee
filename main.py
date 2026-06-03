
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
import joblib
import tensorflow as tf
from datetime import datetime, timedelta

app = FastAPI()

MODEL = tf.keras.models.load_model("forecast_model.keras")
SCALER_X = joblib.load("scaler_X.save")
SCALER_Y = joblib.load("scaler_y.save")

def recursive_forecast_api(start_features, remaining_days):
    # Simplified version of recursive forecast
    current = start_features.copy()
    daily = []
    for _ in range(remaining_days):
        scaled = SCALER_X.transform(current)
        pred_scaled = MODEL.predict(scaled, verbose=0)
        pred = SCALER_Y.inverse_transform(pred_scaled).flatten()[0]
        if np.isnan(pred) or np.isinf(pred):
            return 0, False
        pred = max(0, pred)
        daily.append(pred)
        # Simple update (simplified for API)
        new = current[0].copy()
        # shift lags (assuming feature order same as training)
        new[0:3] = [pred, new[0], new[1]]  # lag_1, lag_2, lag_3
        current = new.reshape(1, -1)
    return sum(daily), True

class ForecastRequest(BaseModel):
    lag_1: float
    lag_2: float
    lag_3: float
    rolling_mean_7: float
    transaction_count: int
    day_of_week: int = None
    month: int = None
    is_weekend: int = None
    mtd_progress: float = None

class ForecastResponse(BaseModel):
    success: bool
    message: str
    forecast_next_month: float = None
    confidence_lower: float = None
    confidence_upper: float = None

@app.post("/predict", response_model=ForecastResponse)
async def predict_next_month(req: ForecastRequest):
    try:
        now = datetime.now()
        dow = req.day_of_week if req.day_of_week is not None else now.weekday()
        mon = req.month if req.month is not None else now.month
        we = req.is_weekend if req.is_weekend is not None else (1 if dow >= 5 else 0)
        if req.mtd_progress is None:
            dim = (now.replace(day=1, month=mon%12+1) - timedelta(days=1)).day
            mt = (now.day - 1) / (dim - 1) if dim > 1 else 1
        else:
            mt = req.mtd_progress
        features = np.array([[req.lag_1, req.lag_2, req.lag_3, req.rolling_mean_7, 0,
                              dow, mon, we, mt, req.transaction_count]], dtype=np.float32)
        # Ensure correct number of features
        n_feat = SCALER_X.n_features_in_
        if features.shape[1] > n_feat:
            features = features[:, :n_feat]
        days_left = (now.replace(day=1, month=mon%12+1) - now).days
        if days_left <= 0:
            days_left = 30
        total, ok = recursive_forecast_api(features, days_left)
        if not ok:
            return ForecastResponse(success=False, message="Recursive forecast failed")
        # Confidence interval placeholder
        lower = total * 0.95
        upper = total * 1.05
        return ForecastResponse(success=True, message="OK",
                                forecast_next_month=round(total,2),
                                confidence_lower=round(lower,2),
                                confidence_upper=round(upper,2))
    except Exception as e:
        return ForecastResponse(success=False, message=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy"}
